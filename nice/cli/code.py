import typer
from nice.config.settings import load_config
from nice.providers.registry import get_active_provider
from nice.tools.registry import TOOL_DEFINITIONS

SYSTEM_PROMPT = """Kamu adalah AI engineer bernama Nice.
Kamu bisa membaca, menulis, dan melihat file di komputer user.
Gunakan tools yang tersedia untuk menyelesaikan task.
Selalu jawab dalam Bahasa Indonesia."""

def code_command(task: str):
    """Jalankan task coding dengan tools (baca/tulis file)."""
    config = load_config()
    provider = get_active_provider()

    typer.echo(f"[{config.provider} / {config.model}]")
    typer.echo(f"Task: {task}\n")

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": task},
    ]

    hasil = provider.chat_sync(messages, tools=TOOL_DEFINITIONS)
    typer.echo(f"\nAI: {hasil}")