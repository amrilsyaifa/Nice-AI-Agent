import httpx
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

    def chat_sync(self, messages: list[dict]) -> str:
        """Sync version — dipakai CLI."""
        return self._chat_sync(messages)

    def _chat_sync(self, messages: list[dict]) -> str:
        api_key = os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
        config = load_config()

        with httpx.Client() as client:
            response = client.post(
                f"{base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": config.model,
                    "messages": messages,
                },
                timeout=30.0,
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]