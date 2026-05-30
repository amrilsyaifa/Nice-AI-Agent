import httpx
import json
import os
from dotenv import load_dotenv
from nice.providers.base import BaseProvider
from nice.config.settings import load_config

load_dotenv()

class OpenAIProvider(BaseProvider):

    def name(self) -> str:
        return "openai"

    async def chat(self, messages: list[dict]) -> str:
        """Async version — untuk future use."""
        return self._chat_sync(messages)

    def chat_sync(self, messages: list[dict],  tools: list = None) -> str:
        """Sync version — dipakai CLI."""
        return self._chat_sync(messages, tools)

    def _chat_sync(self, messages: list[dict], tools: list = None) -> str:
        api_key = os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
        config = load_config()

        payload = {
            "model": config.model,
            "messages": messages,
        }

        if tools:
            payload["tools"] = tools
           

        with httpx.Client() as client:
            response = client.post(
                f"{base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=30.0,
            )
            response.raise_for_status()
            data = response.json()

            message = data["choices"][0]["message"]
            
            # Cek apakah LLM mau pakai tool
            if "tool_calls" in message:
                return self._handle_tool_calls(message, messages, tools)
            
            return message["content"]
        
    def _handle_tool_calls(self, message: dict, messages:list, tools: list) -> str:
        """Proses tool calls dari LLM."""
        from nice.tools.registry import execute_tool

        # Tambah response LLM ke messages
        updated_messages = messages + [message]

        # Jalankan setiap tool yang diminta LLM
        for tool_call in message["tool_calls"]:
            tool_name = tool_call["function"]["name"]
            tool_args = json.loads(tool_call["function"]["arguments"])

            print(f"\n🔧 Menjalankan tool: {tool_name}({tool_args})")
            result = execute_tool(tool_name, tool_args)
            print(f"✅ Hasil: {result[:100]}...")  # preview 100 karakter

            # Tambah hasil tool ke messages
            updated_messages.append({
                "role": "tool",
                "tool_call_id": tool_call["id"],
                "content": result
            })

        # Kirim balik ke LLM dengan hasil tool
        return self.chat_sync(updated_messages, tools)