import httpx
import os
from dotenv import load_dotenv

load_dotenv()

async def chat(prompt: str) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "liquid/lfm-2.5-1.2b-thinking:free", # Free model for testing
                "messages": [
                    {
                        "role": "system",
                        "content": "Kamu adalah AI assistant. Jawab selalu dalam Bahasa Indonesia."
                    },
                    {"role": "user", "content": prompt}
                ]
            },
            timeout=30.0
        )

        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
    

# this function sends a chat completion request to the OpenRouter API using the specified model. The model "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free" is a free model that can be used for testing purposes. You can replace it with any other available model if needed.
#     curl https://openrouter.ai/api/v1/models \
#   -H "Authorization: Bearer $(grep OPENAI_API_KEY .env | cut -d= -f2)" \
#   | python3 -c "
# import json, sys
# data = json.load(sys.stdin)
# free = [m['id'] for m in data['data'] if ':free' in m['id']]
# for m in free[:10]:
#     print(m)
# "