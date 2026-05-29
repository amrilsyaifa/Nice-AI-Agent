import typer
from nice.providers.registry import get_active_provider
from nice.config.settings import load_config

def ask_command(prompt: str):
    """Tanya sesuatu ke AI."""
    config = load_config()
    typer.echo(f"[{config.provider} / {config.model}]")
    typer.echo("Thinking...\n")

    messages = [
        {
            "role": "system",
            "content": "Kamu adalah AI assistant. Jawab selalu dalam Bahasa Indonesia."
        },
        {
            "role": "user",
            "content": prompt
        }
    ]

    provider = get_active_provider()
    hasil = provider.chat_sync(messages)
    typer.echo(f"AI: {hasil}")