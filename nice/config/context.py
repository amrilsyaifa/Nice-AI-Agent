from pathlib import Path

CONTEXT_FILE = ".nice.md"

def load_project_context() -> str | None:
    """Read .nice.md from the current working directory. Returns content or None."""
    path = Path.cwd() / CONTEXT_FILE
    if path.exists():
        return path.read_text(encoding="utf-8").strip() or None
    return None


def inject_context(system_prompt: str) -> str:
    """Append project context to a system prompt if .nice.md exists."""
    context = load_project_context()
    if context:
        return system_prompt + f"\n\n## Project Context\n\n{context}"
    return system_prompt
