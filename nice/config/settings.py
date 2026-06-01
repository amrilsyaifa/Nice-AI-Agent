import json
from pathlib import Path
from pydantic import BaseModel

# ~/.nice/config.json
CONFIG_DIR = Path.home() / ".nice"
CONFIG_FILE = CONFIG_DIR / "config.json"

class NiceConfig(BaseModel):
    """Schema config Nice."""
    provider: str = "openai"
    model: str = "liquid/lfm-2.5-1.2b-thinking:free"
    api_key: str = ""
    base_url: str = "https://openrouter.ai/api/v1"

def load_config() -> NiceConfig:
    """Baca config dari file. Kalau belum ada, return default."""
    if not CONFIG_FILE.exists():
        return NiceConfig()
    
    with open(CONFIG_FILE) as f:
        data = json.load(f)
        return NiceConfig(**data)
    
def save_config(config: NiceConfig):
    """Simpan config ke file."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(config.model_dump(), f, indent=2)
    
    