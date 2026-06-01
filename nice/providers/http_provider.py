import httpx
import json
import os
from nice.providers.base import BaseProvider
from nice.config.settings import load_config

class HttpProvider(BaseProvider):

    def name(self) -> str:
        return "openai"

    async def chat(self, messages: list[dict]) -> str:
        return self._chat_sync(messages)

    def chat_sync(self, messages: list[dict], tools: list = None) -> str:
        return self._chat_sync(messages, tools)

    def _chat_sync(self, messages: list[dict], tools: list = None) -> str:
        config = load_config()
        api_key = config.api_key or os.getenv("OPENAI_API_KEY", "")
        base_url = config.base_url or os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

        if not api_key:
            raise ValueError("api_key is not set. Run: nice config set api_key <YOUR_KEY>")

        payload = {
            "model": config.model,
            "messages": messages,
        }

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

        if response.status_code == 401:
            raise RuntimeError("Invalid API key. Update with: nice config set api_key <YOUR_KEY>")
        if response.status_code == 429:
            raise RuntimeError("Too many requests. Wait a moment and try again.")
        if response.status_code == 402:
            raise RuntimeError("Insufficient API credits. Please top up your balance.")
        if response.status_code >= 500:
            raise RuntimeError("Server is having issues. Please try again later.")
        if response.status_code >= 400:
            raise RuntimeError(f"Request rejected by server (code {response.status_code}).")

        data = response.json()
        message = data["choices"][0]["message"]

        if "tool_calls" in message:
            return self._handle_tool_calls(message, messages, tools)

        return message["content"]

    def _handle_tool_calls(self, message: dict, messages: list, tools: list) -> str:
        from nice.tools.registry import execute_tool

        updated_messages = messages + [message]

        for tool_call in message["tool_calls"]:
            tool_name = tool_call["function"]["name"]
            tool_args = json.loads(tool_call["function"]["arguments"])

            print(f"\n🔧 Menjalankan tool: {tool_name}({tool_args})")
            result = execute_tool(tool_name, tool_args)
            print(f"✅ Hasil: {result[:100]}...")

            updated_messages.append({
                "role": "tool",
                "tool_call_id": tool_call["id"],
                "content": result
            })

        return self.chat_sync(updated_messages, tools)
