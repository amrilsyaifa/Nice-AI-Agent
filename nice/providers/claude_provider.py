import json
import os
from collections.abc import Iterator

import httpx

from nice.config.settings import load_config
from nice.providers.base import BaseProvider


def _to_claude_tools(openai_tools: list) -> list:
    """Convert OpenAI-format tool definitions to Anthropic format."""
    result = []
    for t in openai_tools or []:
        fn = t.get("function", {})
        result.append(
            {
                "name": fn["name"],
                "description": fn.get("description", ""),
                "input_schema": fn.get("parameters", {"type": "object", "properties": {}}),
            }
        )
    return result


def _split_system(messages: list[dict]) -> tuple[str, list[dict]]:
    """Extract system message; return (system_text, remaining_messages)."""
    system = ""
    rest = []
    for m in messages:
        if m["role"] == "system":
            system = m["content"]
        else:
            rest.append(m)
    return system, rest


class ClaudeProvider(BaseProvider):
    ANTHROPIC_VERSION = "2023-06-01"
    BASE_URL = "https://api.anthropic.com/v1"

    def name(self) -> str:
        return "claude"

    async def chat(self, messages: list[dict]) -> str:
        return self.chat_sync(messages)

    def chat_sync(self, messages: list[dict], tools: list = None) -> str:
        config, api_key = self._load_credentials()
        system, msgs = _split_system(messages)

        payload: dict = {
            "model": config.model,
            "max_tokens": 8096,
            "messages": msgs,
        }
        if system:
            payload["system"] = system
        if tools:
            payload["tools"] = _to_claude_tools(tools)

        try:
            with httpx.Client() as client:
                response = client.post(
                    f"{self.BASE_URL}/messages",
                    headers=self._headers(api_key),
                    json=payload,
                    timeout=120.0,
                )
        except httpx.ConnectError:
            raise RuntimeError("Cannot connect to Anthropic. Check your internet connection.")
        except httpx.TimeoutException:
            raise RuntimeError("Anthropic took too long to respond. Please try again.")

        self._raise_for_status(response.status_code, response.text)
        data = response.json()

        # Check for tool use
        tool_uses = [b for b in data.get("content", []) if b.get("type") == "tool_use"]
        if tool_uses:
            return self._handle_tool_calls(data["content"], msgs, tools, payload.get("system", ""))

        text_blocks = [b["text"] for b in data.get("content", []) if b.get("type") == "text"]
        return "".join(text_blocks)

    def chat_stream(self, messages: list[dict], tools: list = None) -> Iterator[str]:
        config, api_key = self._load_credentials()
        system, msgs = _split_system(messages)

        payload: dict = {
            "model": config.model,
            "max_tokens": 8096,
            "messages": msgs,
            "stream": True,
        }
        if system:
            payload["system"] = system
        if tools:
            payload["tools"] = _to_claude_tools(tools)

        # Accumulate blocks indexed by position
        blocks: dict[int, dict] = {}
        full_text = ""

        try:
            with httpx.Client() as client:
                with client.stream(
                    "POST",
                    f"{self.BASE_URL}/messages",
                    headers=self._headers(api_key),
                    json=payload,
                    timeout=120.0,
                ) as response:
                    self._raise_for_status(response.status_code)

                    for line in response.iter_lines():
                        if not line.startswith("data:"):
                            continue
                        data_str = line[5:].strip()
                        if not data_str:
                            continue

                        try:
                            event = json.loads(data_str)
                        except json.JSONDecodeError:
                            continue

                        etype = event.get("type")

                        if etype == "content_block_start":
                            idx = event["index"]
                            blocks[idx] = dict(event["content_block"])

                        elif etype == "content_block_delta":
                            idx = event["index"]
                            delta = event["delta"]
                            if delta["type"] == "text_delta":
                                text = delta["text"]
                                full_text += text
                                yield text
                            elif delta["type"] == "input_json_delta":
                                if idx in blocks:
                                    blocks[idx].setdefault("_args_raw", "")
                                    blocks[idx]["_args_raw"] += delta.get("partial_json", "")

                        elif etype == "message_stop":
                            break

        except httpx.ConnectError:
            raise RuntimeError("Cannot connect to Anthropic. Check your internet connection.")
        except httpx.TimeoutException:
            raise RuntimeError("Anthropic took too long to respond. Please try again.")

        # Execute any tool use blocks
        tool_blocks = [b for b in blocks.values() if b.get("type") == "tool_use"]
        if tool_blocks:
            from nice.tools.registry import execute_tool

            # Reconstruct assistant content list
            assistant_content = []
            if full_text:
                assistant_content.append({"type": "text", "text": full_text})
            for b in tool_blocks:
                try:
                    args = json.loads(b.get("_args_raw", "{}"))
                except json.JSONDecodeError:
                    args = {}
                assistant_content.append(
                    {
                        "type": "tool_use",
                        "id": b["id"],
                        "name": b["name"],
                        "input": args,
                    }
                )

            updated = msgs + [{"role": "assistant", "content": assistant_content}]

            # Execute tools and append results
            tool_results = []
            for b in tool_blocks:
                try:
                    args = json.loads(b.get("_args_raw", "{}"))
                except json.JSONDecodeError:
                    args = {}
                print(f"\n🔧 Running tool: {b['name']}({args})")
                result = execute_tool(b["name"], args)
                print(f"✅ Result: {result[:100]}...")
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": b["id"],
                        "content": result,
                    }
                )

            updated.append({"role": "user", "content": tool_results})

            # Rebuild full message list with system
            full_messages = messages[:1] + [
                {"role": m["role"], "content": m["content"]} for m in updated
            ]
            yield from self.chat_stream(full_messages, tools)

    # ------------------------------------------------------------------ #

    def _load_credentials(self):
        config = load_config()
        api_key = config.api_key or os.getenv("ANTHROPIC_API_KEY", "")
        if not api_key:
            raise ValueError(
                "api_key is not set. Run: nice config set api_key <YOUR_ANTHROPIC_KEY>"
            )
        return config, api_key

    def _headers(self, api_key: str) -> dict:
        return {
            "x-api-key": api_key,
            "anthropic-version": self.ANTHROPIC_VERSION,
            "Content-Type": "application/json",
        }

    def _raise_for_status(self, status_code: int, body: str = ""):
        if status_code == 401:
            raise RuntimeError(
                "Invalid Anthropic API key. Update with: nice config set api_key <KEY>"
            )
        if status_code == 429:
            raise RuntimeError("Anthropic rate limit reached. Wait a moment and try again.")
        if status_code == 402:
            raise RuntimeError("Insufficient Anthropic credits. Please top up your balance.")
        if status_code >= 500:
            raise RuntimeError("Anthropic server error. Please try again later.")
        if status_code >= 400:
            raise RuntimeError(f"Anthropic request rejected (code {status_code}).")

    def _handle_tool_calls(
        self,
        assistant_content: list,
        messages: list,
        tools: list,
        system: str,
    ) -> str:
        from nice.tools.registry import execute_tool

        tool_uses = [b for b in assistant_content if b.get("type") == "tool_use"]
        updated = messages + [{"role": "assistant", "content": assistant_content}]

        tool_results = []
        for tu in tool_uses:
            args = tu.get("input", {})
            print(f"\n🔧 Running tool: {tu['name']}({args})")
            result = execute_tool(tu["name"], args)
            print(f"✅ Result: {result[:100]}...")
            tool_results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": tu["id"],
                    "content": result,
                }
            )

        updated.append({"role": "user", "content": tool_results})

        config, api_key = self._load_credentials()
        payload: dict = {
            "model": config.model,
            "max_tokens": 8096,
            "messages": updated,
        }
        if system:
            payload["system"] = system
        if tools:
            payload["tools"] = _to_claude_tools(tools)

        with httpx.Client() as client:
            response = client.post(
                f"{self.BASE_URL}/messages",
                headers=self._headers(api_key),
                json=payload,
                timeout=120.0,
            )
        self._raise_for_status(response.status_code, response.text)
        data = response.json()

        # Check for nested tool use
        more_tools = [b for b in data.get("content", []) if b.get("type") == "tool_use"]
        if more_tools:
            return self._handle_tool_calls(data["content"], updated, tools, system)

        return "".join(b["text"] for b in data.get("content", []) if b.get("type") == "text")
