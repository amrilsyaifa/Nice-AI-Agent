from typing import Optional
import typer
from nice.config.settings import load_config
from nice.providers.registry import get_active_provider
from nice.tools.registry import TOOL_DEFINITIONS
from nice.cli._spinner import run_with_spinner, console

SYSTEM_PROMPT = """You are an AI engineer named Nice.
You can read, write, and run commands on the user's computer.
Use the available tools to complete the task.
Remember the context of previous tasks in this session.
Reply in the same language as the user's input."""

def code_command(task: Optional[str] = typer.Argument(None, help="Coding task. Leave empty for interactive mode.")):
    """Execute a coding task with tools. No argument = interactive mode."""
    config = load_config()
    provider = get_active_provider()

    if task:
        # One-shot mode
        typer.echo(f"[{config.provider} / {config.model}]")
        typer.echo(f"Task: {task}\n")

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": task},
        ]

        result, err = run_with_spinner(lambda: provider.chat_sync(messages, tools=TOOL_DEFINITIONS))

        if isinstance(err, KeyboardInterrupt):
            console.print("[yellow]Cancelled.[/yellow]")
            return
        if err:
            console.print(f"[red]Error:[/red] {err}")
            return

        console.print(f"\n[bold]AI:[/bold] {result}")
        return

    # Interactive mode
    console.print(f"[bold]Nice Code[/bold] [{config.provider} / {config.model}]")
    console.print("Interactive mode — type a task, AI executes immediately. 'exit' to quit.")
    console.print("-" * 50)

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    while True:
        try:
            user_input = typer.prompt("You")
        except (KeyboardInterrupt, EOFError):
            typer.echo("\nGoodbye!")
            break

        if user_input.lower() == "exit":
            typer.echo("Goodbye!")
            break

        if not user_input.strip():
            continue

        messages.append({"role": "user", "content": user_input})

        current_messages = list(messages)
        result, err = run_with_spinner(lambda: provider.chat_sync(current_messages, tools=TOOL_DEFINITIONS))

        if isinstance(err, KeyboardInterrupt):
            console.print("\n[yellow]Cancelled.[/yellow]")
            messages.pop()
            continue

        if err:
            console.print(f"[red]Error:[/red] {err}")
            messages.pop()
            continue

        console.print(f"\n[bold]AI:[/bold] {result}")
        messages.append({"role": "assistant", "content": result})
        typer.echo("-" * 50)
