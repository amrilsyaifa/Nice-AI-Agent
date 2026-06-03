from nice.providers.base import BaseProvider
from nice.providers.http_provider import HttpProvider
from nice.providers.claude_provider import ClaudeProvider
from nice.providers.ollama_provider import OllamaProvider

PROVIDERS: dict[str, BaseProvider] = {
    "openai":  HttpProvider(),
    "claude":  ClaudeProvider(),
    "ollama":  OllamaProvider(),
}

def get_provider(name: str) -> BaseProvider:
    if name not in PROVIDERS:
        available = ", ".join(PROVIDERS.keys())
        raise ValueError(f"Unknown provider '{name}'. Available: {available}")
    return PROVIDERS[name]

def get_active_provider() -> BaseProvider:
    from nice.config.settings import load_config
    config = load_config()
    return get_provider(config.provider)
