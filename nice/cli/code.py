from typing import Optional
import typer
from nice.config.settings import load_config, save_config
from nice.config.context import inject_context
from nice.providers.registry import get_active_provider
from nice.tools.registry import TOOL_DEFINITIONS
from nice.memory.history import ConversationHistory
from nice.cli._spinner import stream_markdown, console

SYSTEM_PROMPT = """You are an AI engineer named Nice.
You can read, write, and run commands on the user's computer.
Use the available tools to complete the task.
Remember the context of previous tasks in this session.
Reply in the same language as the user's input."""

def code_command(
    task: Optional[str] = typer.Argument(None, help="Coding task. Leave empty for interactive mode."),
    clear: bool = typer.Option(False, "--clear", help="Clear code session history."),
):
    """Execute a coding task with tools. No argument = interactive mode."""
    config = load_config()
    provider = get_active_provider()

    if task:
        typer.echo(f"[{config.provider} / {config.model}]")
        typer.echo(f"Task: {task}\n")
        messages = [
            {"role": "system", "content": inject_context(SYSTEM_PROMPT)},
            {"role": "user", "content": task},
        ]
        _, err = stream_markdown(provider, messages, tools=TOOL_DEFINITIONS)
        if err and not isinstance(err, KeyboardInterrupt):
            console.print(f"[red]Error:[/red] {err}")
        return

    # Interactive mode
    history = ConversationHistory("code_history.json")

    if clear:
        history.clear()
        typer.echo("Code history cleared.")
        return

    console.print(f"[bold]Nice Code[/bold] [{config.provider} / {config.model}]")
    console.print("Type 'exit' to quit, 'clear' to reset history, '/model <name>' to switch model.")
    console.print("-" * 50)

    if not history.is_empty():
        typer.echo(f"(continuing from {len(history.messages)} previous messages)\n")

    system_prompt = inject_context(SYSTEM_PROMPT)

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

        if user_input.lower().startswith("/model "):
            new_model = user_input[7:].strip()
            if new_model:
                config = load_config()
                config.model = new_model
                save_config(config)
                console.print(f"[green]Model switched to:[/green] {new_model}")
            else:
                console.print(f"[dim]Current model:[/dim] {config.model}")
            continue

        if not user_input.strip():
            continue

        history.add("user", user_input)
        messages = history.get_messages(system_prompt)

        response, err = stream_markdown(provider, messages, tools=TOOL_DEFINITIONS)

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
