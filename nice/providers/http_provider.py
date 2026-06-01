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
            raise ValueError("api_key belum di-set. Jalankan: nice config set api_key <YOUR_KEY>")

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
            raise RuntimeError("Tidak bisa terhubung ke server. Periksa koneksi internet kamu.")
        except httpx.TimeoutException:
            raise RuntimeError("Server terlalu lama merespons. Coba lagi sebentar.")

        if response.status_code == 401:
            raise RuntimeError("API key tidak valid. Cek dengan: nice config set api_key <YOUR_KEY>")
        if response.status_code == 429:
            raise RuntimeError("Terlalu banyak permintaan. Tunggu sebentar lalu coba lagi.")
        if response.status_code == 402:
            raise RuntimeError("Saldo API habis. Silakan isi ulang.")
        if response.status_code >= 500:
            raise RuntimeError("Server sedang bermasalah. Coba beberapa saat lagi.")
        if response.status_code >= 400:
            raise RuntimeError(f"Permintaan ditolak server (kode {response.status_code}).")

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
