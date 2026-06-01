import typer
from nice.providers.registry import get_active_provider
from nice.config.settings import load_config
from nice.memory.history import ConversationHistory
from nice.cli._spinner import run_with_spinner, console

SYSTEM_PROMPT = "Kamu adalah AI assistant bernama Nice. Jawab selalu dalam Bahasa Indonesia. Kamu mengingat konteks percakapan sebelumnya."

def chat_command():
    """Chat interaktif dengan AI. Ketik 'exit' untuk keluar, 'clear' untuk hapus history."""

    config = load_config()
    provider = get_active_provider()
    history = ConversationHistory()

    typer.echo(f"Nice Chat [{config.provider} / {config.model}]")
    typer.echo("Ketik 'exit' untuk keluar, 'clear' untuk hapus history.")
    typer.echo("-" * 50)

    if not history.is_empty():
        typer.echo(f"(melanjutkan {len(history.messages)} pesan sebelumnya)\n")

    while True:
        try:
            user_input = typer.prompt("You")
        except (KeyboardInterrupt, EOFError):
            typer.echo("\nSampai jumpa!")
            break

        if user_input.lower() == "exit":
            typer.echo("Sampai jumpa!")
            break

        if user_input.lower() == "clear":
            history.clear()
            typer.echo("History dihapus.")
            continue

        if not user_input.strip():
            continue

        history.add("user", user_input)
        messages = history.get_messages(SYSTEM_PROMPT)

        response, err = run_with_spinner(lambda: provider.chat_sync(messages))

        if isinstance(err, KeyboardInterrupt):
            console.print("\n[yellow]Dibatalkan.[/yellow]")
            history.messages.pop()
            continue

        if err:
            console.print(f"[red]Error:[/red] {err}")
            history.messages.pop()
            continue

        console.print(f"[bold]AI:[/bold] {response}")
        history.add("assistant", response)
        typer.echo("-" * 50)
