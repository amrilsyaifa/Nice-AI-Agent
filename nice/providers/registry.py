from nice.providers.base import BaseProvider
from nice.providers.http_provider import HttpProvider

PROVIDERS: dict[str, BaseProvider] = {
    "openai": HttpProvider(),
}

def get_provider(name: str) -> BaseProvider:
    """Ambil provider berdasarkan nama."""
    if name not in PROVIDERS:
        available = ", ".join(PROVIDERS.keys())
        raise ValueError(f"Provider '{name}' tidak dikenal. Tersedia: {available}")
    return PROVIDERS[name]

def get_active_provider() -> BaseProvider:
    """Ambil provider yang aktif berdasarkan config."""
    from nice.config.settings import load_config
    config = load_config()
    return get_provider(config.provider)