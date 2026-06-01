import json
from pathlib import Path

HISTORY_DIR = Path.home() / ".nice"

class ConversationHistory:

    def __init__(self, filename: str = "history.json"):
        self._file = HISTORY_DIR / filename
        self.messages: list[dict] = []
        self._load()

    def _load(self):
        if self._file.exists():
            with open(self._file) as f:
                self.messages = json.load(f)

    def save(self):
        HISTORY_DIR.mkdir(parents=True, exist_ok=True)
        with open(self._file, "w") as f:
            json.dump(self.messages, f, indent=2)

    def add(self, role: str, content: str):
        if not content:
            return
        self.messages.append({"role": role, "content": content})
        self.save()

    def clear(self):
        self.messages = []
        self.save()

    def get_messages(self, system_prompt: str) -> list[dict]:
        return [{"role": "system", "content": system_prompt}] + self.messages

    def is_empty(self) -> bool:
        return len(self.messages) == 0
