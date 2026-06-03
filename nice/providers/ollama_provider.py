import os
from typing import Iterator
from nice.providers.http_provider import HttpProvider
from nice.config.settings import load_config


class OllamaProvider(HttpProvider):
    """OpenAI-compatible provider for local Ollama models."""

    def name(self) -> str:
        return "ollama"

    def _load_credentials(self):
        config = load_config()
        # Ollama doesn't require an API key
        api_key = config.api_key or os.getenv("OLLAMA_API_KEY", "ollama")
        base_url = config.base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
        return config, api_key, base_url
