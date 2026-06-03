from pathlib import Path
from datetime import datetime
from typing import Optional
import typer
from nice.providers.registry import get_active_provider
from nice.config.settings import load_config, save_config
from nice.config.context import inject_context
from nice.memory.history import ConversationHistory
from nice.cli._spinner import run_with_spinner, stream_markdown, console
from nice.cli._slash import CHAT_HELP, show_usage, print_usage_inline, load_context_file

SYSTEM_PROMPT = "You are a helpful AI assistant named Nice. Reply in the same language as the user's input. You remember the context of previous messages."


def chat_command(
    session: Optional[str] = typer.Option(None, "--session", "-s", help="Named session to use or create."),
    list_sessions: bool = typer.Option(False, "--list", "-l", help="List all sessions."),
    delete: Optional[str] = typer.Option(None, "--delete", help="Delete a session by name."),
    export: bool = typer.Option(False, "--export", "-e", help="Export session to Markdown."),
    export_json: bool = typer.Option(False, "--export-json", help="Export session to JSON."),
):
    """Interactive chat with AI. Type 'exit' to quit, 'clear' to reset history."""

    if list_sessions:
        sessions = ConversationHistory.list_sessions()
        if not sessions:
            typer.echo("No sessions found.")
            return
        typer.echo(f"{'SESSION':<20} {'MESSAGES':>8}  LAST ACTIVE")
        typer.echo("-" * 50)
        for s in sessions:
            ts = s["modified"].strftime("%Y-%m-%d %H:%M")
            typer.echo(f"{s['name']:<20} {s['messages']:>8}  {ts}")
        return

    if delete:
        if typer.confirm(f"Delete session '{delete}'?"):
            ok = ConversationHistory.delete_session(delete)
            typer.echo("Deleted." if ok else f"Session '{delete}' not found.")
        else:
            typer.echo("Cancelled.")
        return

    history = ConversationHistory(session=session)

    if export or export_json:
        if history.is_empty():
            typer.echo("Session is empty, nothing to export.")
            return
        name = session or "default"
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        if export_json:
            content = history.export_json()
            filename = f"nice-chat-{name}-{ts}.json"
        else:
            content = history.export_markdown()
            filename = f"nice-chat-{name}-{ts}.md"
        Path(filename).write_text(content, encoding="utf-8")
        typer.echo(f"Exported to {filename}")
        return

    config = load_config()
    provider = get_active_provider()
    session_label = session or "default"

    typer.echo(f"Nice Chat [{config.provider} / {config.model}]  session: {session_label}")
    typer.echo("Type /help for available commands.")
    typer.echo("-" * 50)

    if not history.is_empty():
        typer.echo(f"(continuing from {len(history.messages)} messages)\n")

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
            console.print(CHAT_HELP)
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

        if history.should_compress():
            console.print("[dim]Compressing conversation history…[/dim]")
            _, err = run_with_spinner(lambda: history.compress(provider))
            if err:
                console.print(f"[yellow]Compression failed:[/yellow] {err}")
            else:
                console.print(f"[dim]Compressed to {len(history.messages)} messages.[/dim]")

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

        config = load_config()
        if config.show_usage:
            print_usage_inline(provider)

        history.add("assistant", response)
        typer.echo("-" * 50)
