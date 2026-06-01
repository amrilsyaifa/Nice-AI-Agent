import typer
from nice.providers.registry import get_active_provider
from nice.config.settings import load_config

def ask_command(prompt: str):
    """Ask the AI a question."""
    config = load_config()
    typer.echo(f"[{config.provider} / {config.model}]")
    typer.echo("Thinking...\n")

    messages = [
        {
            "role": "system",
            "content": "You are a helpful AI assistant. Reply in the same language as the user's input."
        },
        {
            "role": "user",
            "content": prompt
        }
    ]

    provider = get_active_provider()
    result = provider.chat_sync(messages)
    typer.echo(f"AI: {result}")
