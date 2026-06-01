import typer
from nice.providers.registry import get_active_provider
from nice.config.settings import load_config
from nice.cli._spinner import stream_markdown, console

def ask_command(prompt: str):
    """Ask the AI a question."""
    config = load_config()
    typer.echo(f"[{config.provider} / {config.model}]\n")

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
    _, err = stream_markdown(provider, messages)

    if err and not isinstance(err, KeyboardInterrupt):
        console.print(f"[red]Error:[/red] {err}")
