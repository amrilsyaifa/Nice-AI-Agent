import typer
import asyncio
from nice.providers.registry import get_default_provider

def ask_command(prompt: str):
    """Tanya sesuatu ke AI."""
    typer.echo("Thinking...")
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

    provider = get_default_provider()
    hasil = asyncio.run(provider.chat(messages))
    typer.echo(f"\nAI: {hasil}")