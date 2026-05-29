import httpx
import os
from dotenv import load_dotenv
from nice.providers.base import BaseProvider

load_dotenv()

class OpenAIProvider(BaseProvider):
    """Provider untuk OpenAI dan OpenRouter."""

    def name(self) -> str:
        return "openai"
    
    async def chat(self, message: list[dict]) -> str:
        api_key = os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
        model = os.getenv("OPENAI_MODEL", "liquid/lfm-2.5-1.2b-thinking:free")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": model,
                    "messages": message,
                }
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]

    
    

