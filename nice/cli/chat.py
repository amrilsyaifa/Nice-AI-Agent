import typer
from nice.providers.registry import get_active_provider
from nice.config.settings import load_config
from nice.config.context import inject_context
from nice.memory.history import ConversationHistory
from nice.cli._spinner import stream_markdown, console

SYSTEM_PROMPT = "You are a helpful AI assistant named Nice. Reply in the same language as the user's input. You remember the context of previous messages."

def chat_command():
    """Interactive chat with AI. Type 'exit' to quit, 'clear' to reset history."""

    config = load_config()
    provider = get_active_provider()
    history = ConversationHistory()

    typer.echo(f"Nice Chat [{config.provider} / {config.model}]")
    typer.echo("Type 'exit' to quit, 'clear' to reset history.")
    typer.echo("-" * 50)

    if not history.is_empty():
        typer.echo(f"(continuing from {len(history.messages)} previous messages)\n")

    while True:
        try:
            user_input = typer.prompt("You")
        except (KeyboardInterrupt, EOFError):
            typer.echo("\nGoodbye!")
            break

        if user_input.lower() == "exit":
            typer.echo("Goodbye!")
            break

        if user_input.lower() == "clear":
            history.clear()
            typer.echo("History cleared.")
            continue

        if not user_input.strip():
            continue

        history.add("user", user_input)
        messages = history.get_messages(inject_context(SYSTEM_PROMPT))

        response, err = stream_markdown(provider, messages)

        if isinstance(err, KeyboardInterrupt):
            console.print("[yellow]Cancelled.[/yellow]")
            history.messages.pop()
            continue

        if err:
            console.print(f"[red]Error:[/red] {err}")
            history.messages.pop()
            continue

        history.add("assistant", response)
        typer.echo("-" * 50)
