import typer

from nice.cli._slash import CODE_HELP, load_context_file, print_usage_inline, show_usage
from nice.cli._spinner import console, stream_markdown, stream_quiet
from nice.config.context import inject_context
from nice.config.settings import load_config, save_config
from nice.memory.history import ConversationHistory
from nice.providers.registry import get_active_provider
from nice.tools.registry import TOOL_DEFINITIONS

SYSTEM_PROMPT = """You are an AI engineer named Nice.
You can read, write, and run commands on the user's computer.
Use the available tools to complete the task.
Remember the context of previous tasks in this session.
Reply in the same language as the user's input."""


def code_command(
    task: str | None = typer.Argument(None, help="Coding task. Leave empty for interactive mode."),
    clear: bool = typer.Option(False, "--clear", help="Clear code session history."),
    quiet: bool = typer.Option(
        False, "--quiet", "-q", help="Plain output — no markdown, no decorations."
    ),
):
    """Execute a coding task with tools. No argument = interactive mode."""
    config = load_config()
    provider = get_active_provider()
    stream_fn = stream_quiet if quiet else stream_markdown

    if task:
        if not quiet:
            typer.echo(f"[{config.provider} / {config.model}]")
            typer.echo(f"Task: {task}\n")
        messages = [
            {"role": "system", "content": inject_context(SYSTEM_PROMPT)},
            {"role": "user", "content": task},
        ]
        _, err = stream_fn(provider, messages, tools=TOOL_DEFINITIONS)
        if err and not isinstance(err, KeyboardInterrupt):
            console.print(f"[red]Error:[/red] {err}")
        if not quiet and config.show_usage:
            print_usage_inline(provider)
        return

    # Interactive mode
    history = ConversationHistory("code_history.json")

    if clear:
        history.clear()
        typer.echo("Code history cleared.")
        return

    console.print(f"[bold]Nice Code[/bold] [{config.provider} / {config.model}]")
    console.print("Type /help for available commands.")
    console.print("-" * 50)

    if not history.is_empty():
        typer.echo(f"(continuing from {len(history.messages)} messages)\n")

    system_prompt = inject_context(SYSTEM_PROMPT)

    while True:
        try:
            user_input = typer.prompt("You")
        except (KeyboardInterrupt, EOFError):
            typer.echo("\nGoodbye!")
            break

        cmd = user_input.strip().lower()

        if cmd == "exit":
            typer.echo("Goodbye!")
            break

        if cmd == "clear":
            history.clear()
            typer.echo("History cleared.")
            continue

        if cmd == "/help":
            console.print(CODE_HELP)
            continue

        if cmd == "/usage":
            show_usage(provider)
            continue

        if cmd.startswith("/model"):
            new_model = user_input[6:].strip()
            if new_model:
                config = load_config()
                config.model = new_model
                save_config(config)
                console.print(f"[green]Model switched to:[/green] {new_model}")
            else:
                console.print(f"[dim]Current model:[/dim] {config.model}")
            continue

        if cmd.startswith("/context"):
            path_str = user_input[8:].strip()
            if not path_str:
                console.print("[yellow]Usage: /context <file>[/yellow]")
                continue
            content, err = load_context_file(path_str)
            if err:
                console.print(f"[red]Error:[/red] {err}")
                continue
            history.add("user", f"[Context from {path_str}]\n{content}")
            history.add("assistant", f"Understood, I've loaded the context from `{path_str}`.")
            console.print(f"[green]Context loaded from {path_str}[/green]")
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

        config = load_config()
        if config.show_usage:
            print_usage_inline(provider)

        history.add("assistant", response)
        typer.echo("-" * 50)
