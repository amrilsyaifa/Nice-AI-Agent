import httpx
import json
import os
from typing import Iterator
from nice.providers.base import BaseProvider
from nice.config.settings import load_config
from nice.core.logger import get_logger

log = get_logger("http_provider")


class HttpProvider(BaseProvider):

    def __init__(self):
        self._last_usage: dict = {}

    def name(self) -> str:
        return "openai"

    async def chat(self, messages: list[dict]) -> str:
        return self._chat_sync(messages)

    def chat_sync(self, messages: list[dict], tools: list = None) -> str:
        return self._chat_sync(messages, tools)

    def chat_stream(self, messages: list[dict], tools: list = None) -> Iterator[str]:
        """Stream response tokens as they arrive. Yields str chunks."""
        config, api_key, base_url = self._load_credentials()

        payload = {
            "model": config.model,
            "messages": messages,
            "stream": True,
            "stream_options": {"include_usage": True},
        }
        if tools:
            payload["tools"] = tools

        tool_calls_acc: dict[int, dict] = {}
        full_content = ""

        try:
            with httpx.Client() as client:
                with client.stream(
                    "POST",
                    f"{base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                    timeout=120.0,
                ) as response:
                    self._raise_for_status(response.status_code)

                    for line in response.iter_lines():
                        if not line.startswith("data: "):
                            continue
                        data = line[6:]
                        if data == "[DONE]":
                            break

                        try:
                            chunk = json.loads(data)
                        except json.JSONDecodeError:
                            continue

                        # Capture usage when provider includes it
                        if chunk.get("usage"):
                            self._last_usage = chunk["usage"]

                        if not chunk.get("choices"):
                            continue
                        delta = chunk["choices"][0].get("delta", {})

                        # Stream text content
                        if delta.get("content"):
                            full_content += delta["content"]
                            yield delta["content"]

                        # Accumulate tool call chunks
                        for tc in delta.get("tool_calls") or []:
                            idx = tc["index"]
                            if idx not in tool_calls_acc:
                                tool_calls_acc[idx] = {
                                    "id": "",
                                    "type": "function",
                                    "function": {"name": "", "arguments": ""},
                                }
                            if tc.get("id"):
                                tool_calls_acc[idx]["id"] = tc["id"]
                            fn = tc.get("function", {})
                            if fn.get("name"):
                                tool_calls_acc[idx]["function"]["name"] += fn["name"]
                            if fn.get("arguments"):
                                tool_calls_acc[idx]["function"]["arguments"] += fn["arguments"]

        except httpx.ConnectError:
            raise RuntimeError("Cannot connect to server. Check your internet connection.")
        except httpx.TimeoutException:
            raise RuntimeError("Server took too long to respond. Please try again.")

        # Execute accumulated tool calls, then stream the follow-up
        if tool_calls_acc:
            from nice.tools.registry import execute_tool

            tool_calls = list(tool_calls_acc.values())
            assistant_msg = {
                "role": "assistant",
                "content": full_content or None,
                "tool_calls": tool_calls,
            }
            updated = messages + [assistant_msg]

            for tc in tool_calls:
                tool_name = tc["function"]["name"]
                tool_args = json.loads(tc["function"]["arguments"])

                print(f"\n🔧 Running tool: {tool_name}({tool_args})")
                result = execute_tool(tool_name, tool_args)
                print(f"✅ Result: {result[:100]}...")

                updated.append({
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "content": result,
                })

            yield from self.chat_stream(updated, tools)

    # ------------------------------------------------------------------ #

    def _load_credentials(self):
        config = load_config()
        api_key = config.api_key or os.getenv("OPENAI_API_KEY", "")
        base_url = config.base_url or os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
        if not api_key:
            raise ValueError("api_key is not set. Run: nice config set api_key <YOUR_KEY>")
        return config, api_key, base_url

    def _raise_for_status(self, status_code: int):
        if status_code == 401:
            raise RuntimeError("Invalid API key. Update with: nice config set api_key <YOUR_KEY>")
        if status_code == 429:
            raise RuntimeError("Too many requests. Wait a moment and try again.")
        if status_code == 402:
            raise RuntimeError("Insufficient API credits. Please top up your balance.")
        if status_code >= 500:
            raise RuntimeError("Server is having issues. Please try again later.")
        if status_code >= 400:
            raise RuntimeError(f"Request rejected by server (code {status_code}).")

    def _chat_sync(self, messages: list[dict], tools: list = None) -> str:
        config, api_key, base_url = self._load_credentials()

        payload = {"model": config.model, "messages": messages}
        if tools:
            payload["tools"] = tools

        try:
            with httpx.Client() as client:
                response = client.post(
                    f"{base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                    timeout=120.0,
                )
        except httpx.ConnectError:
            raise RuntimeError("Cannot connect to server. Check your internet connection.")
        except httpx.TimeoutException:
            raise RuntimeError("Server took too long to respond. Please try again.")

        self._raise_for_status(response.status_code)

        data = response.json()
        if data.get("usage"):
            self._last_usage = data["usage"]
            log.info("chat_sync usage: %s", self._last_usage)
        message = data["choices"][0]["message"]

        if "tool_calls" in message:
            return self._handle_tool_calls(message, messages, tools)

        return message["content"]

    def _handle_tool_calls(self, message: dict, messages: list, tools: list) -> str:
        from nice.tools.registry import execute_tool

        updated = messages + [message]

        for tc in message["tool_calls"]:
            tool_name = tc["function"]["name"]
            tool_args = json.loads(tc["function"]["arguments"])

            log.info("tool_call: %s(%s)", tool_name, tool_args)
            print(f"\n🔧 Running tool: {tool_name}({tool_args})")
            result = execute_tool(tool_name, tool_args)
            log.debug("tool_result: %s", result[:200])
            print(f"✅ Result: {result[:100]}...")

            updated.append({
                "role": "tool",
                "tool_call_id": tc["id"],
                "content": result,
            })

        return self.chat_sync(updated, tools)
