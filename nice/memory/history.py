import json
from pathlib import Path

HISTORY_FILE = Path.home() / ".nice" / "history.json"

class ConversationHistory:
    """Menyimpan dan mengelola riwayat percakapan."""

    def __init__(self):
        self.messages: list[dict] = []
        self._load()

    def _load(self):
        """Load history dari file kalau ada."""
        if HISTORY_FILE.exists():
            with open(HISTORY_FILE) as f:
                self.messages = json.load(f)

    def save(self):
        """Simpan history ke file."""
        HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(HISTORY_FILE, "w") as f:
            json.dump(self.messages, f, indent=2)
    
    def add(self, role: str, content: str):
        """Tambah pesan baru ke history."""
        if not content:
            return
        self.messages.append({"role": role, "content": content})
        self.save()

    def clear(self):
        """Hapus semua history."""
        self.messages = []
        self.save()
    
    def get_messages(self, system_propmt: str) -> list[dict]:
        """Ambil semua messages dengan system prompt di depan."""
        return [{"role": "system", "content": system_propmt}] + self.messages
    
    def is_empty(self) -> bool:
        """Cek apakah history kosong."""
        return len(self.messages) == 0

    
   