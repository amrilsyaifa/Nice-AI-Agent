from nice.providers.base import BaseProvider
from nice.providers.openai_provider import OpenAIProvider

PROVIDERS : dict[str, BaseProvider] = {
    "openai": OpenAIProvider(),
}

def get_provider(name: str) -> BaseProvider:
    """Ambil provider berdasarkan nama."""
    if name not in PROVIDERS:
        available = ", ".join(PROVIDERS.keys())
        raise ValueError(f"Provider '{name}' tidak dikenal. Tersedia: {available}")
    return PROVIDERS[name]

def get_default_provider() -> BaseProvider:
    """Ambil provider default (OpenAI)."""
    return get_provider("openai")