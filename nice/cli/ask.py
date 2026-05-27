import typer
import asyncio
from nice.providers.openai_provider import chat

def ask_command(prompt: str):
    """Tanya sesuatu ke AI."""
    typer.echo("Thinking...")
    hasil = asyncio.run(chat(prompt))
    typer.echo(f"\nAI: {hasil}")