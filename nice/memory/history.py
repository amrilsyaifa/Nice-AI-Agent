import json
from datetime import datetime
from pathlib import Path

HISTORY_DIR = Path.home() / ".nice"
SESSIONS_DIR = HISTORY_DIR / "sessions"

# Compress when total chars exceed this threshold
COMPRESS_THRESHOLD = 40_000
# Keep this many recent messages after compression
COMPRESS_KEEP = 8


class ConversationHistory:

    def __init__(self, filename: str = None, session: str = None):
        if session:
            SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
            self._file = SESSIONS_DIR / f"{session}.json"
            self._session_name = session
        elif filename:
            self._file = HISTORY_DIR / filename
            self._session_name = filename.replace(".json", "")
        else:
            self._file = HISTORY_DIR / "history.json"
            self._session_name = "default"

        self.messages: list[dict] = []
        self._load()

    # ------------------------------------------------------------------ #
    # Core

    def _load(self):
        if self._file.exists():
            with open(self._file) as f:
                self.messages = json.load(f)

    def save(self):
        self._file.parent.mkdir(parents=True, exist_ok=True)
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

    # ------------------------------------------------------------------ #
    # Auto-compress

    def total_chars(self) -> int:
        return sum(len(m.get("content") or "") for m in self.messages)

    def should_compress(self) -> bool:
        return self.total_chars() > COMPRESS_THRESHOLD

    def compress(self, provider) -> str:
        """Summarise old messages and replace them with a compact summary pair."""
        if len(self.messages) <= COMPRESS_KEEP:
            return ""

        old = self.messages[:-COMPRESS_KEEP]
        recent = self.messages[-COMPRESS_KEEP:]

        conversation_text = "\n".join(
            f"{m['role'].upper()}: {m.get('content', '')}" for m in old
        )

        summary_messages = [
            {
                "role": "system",
                "content": "You are a conversation summariser. Create a concise summary that preserves all important facts, decisions, and context from the conversation. Be thorough but compact.",
            },
            {
                "role": "user",
                "content": f"Summarise this conversation:\n\n{conversation_text}",
            },
        ]

        summary = provider.chat_sync(summary_messages)

        compressed = [
            {"role": "user", "content": f"[Previous conversation summary]\n{summary}"},
            {"role": "assistant", "content": "Understood, I have the full context."},
        ] + recent

        self.messages = compressed
        self.save()
        return summary

    # ------------------------------------------------------------------ #
    # Sessions management (static helpers)

    @staticmethod
    def list_sessions() -> list[dict]:
        sessions = []

        # Default session
        default = HISTORY_DIR / "history.json"
        if default.exists():
            data = json.loads(default.read_text())
            sessions.append({
                "name": "default",
                "messages": len(data),
                "modified": datetime.fromtimestamp(default.stat().st_mtime),
                "file": default,
            })

        # Named sessions
        if SESSIONS_DIR.exists():
            for f in sorted(SESSIONS_DIR.glob("*.json")):
                try:
                    data = json.loads(f.read_text())
                    sessions.append({
                        "name": f.stem,
                        "messages": len(data),
                        "modified": datetime.fromtimestamp(f.stat().st_mtime),
                        "file": f,
                    })
                except Exception:
                    pass

        return sorted(sessions, key=lambda s: s["modified"], reverse=True)

    @staticmethod
    def delete_session(name: str) -> bool:
        if name == "default":
            f = HISTORY_DIR / "history.json"
        else:
            f = SESSIONS_DIR / f"{name}.json"

        if f.exists():
            f.unlink()
            return True
        return False

    # ------------------------------------------------------------------ #
    # Export

    def export_markdown(self) -> str:
        lines = [
            f"# Chat Session — {self._session_name}",
            f"*Exported: {datetime.now().strftime('%Y-%m-%d %H:%M')}*",
            "",
            "---",
            "",
        ]
        for m in self.messages:
            role = "**You**" if m["role"] == "user" else "**AI**"
            lines.append(f"{role}: {m.get('content', '')}")
            lines.append("")
            lines.append("---")
            lines.append("")
        return "\n".join(lines)

    def export_json(self) -> str:
        return json.dumps(self.messages, indent=2, ensure_ascii=False)
