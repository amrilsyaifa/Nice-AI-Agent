from typing import Optional
import typer
from nice.config.settings import load_config
from nice.providers.registry import get_active_provider
from nice.tools.registry import TOOL_DEFINITIONS
from nice.cli._spinner import run_with_spinner, console

SYSTEM_PROMPT = """Kamu adalah AI engineer bernama Nice.
Kamu bisa membaca, menulis, dan menjalankan perintah di komputer user.
Gunakan tools yang tersedia untuk menyelesaikan task.
Ingat konteks task sebelumnya dalam sesi ini.
Selalu jawab dalam Bahasa Indonesia."""

def code_command(task: Optional[str] = typer.Argument(None, help="Task coding. Kosongkan untuk mode interaktif.")):
    """Eksekusi task coding dengan tools. Tanpa argumen = mode interaktif."""
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
            console.print("[yellow]Dibatalkan.[/yellow]")
            return
        if err:
            console.print(f"[red]Error:[/red] {err}")
            return

        console.print(f"\n[bold]AI:[/bold] {result}")
        return

    # Interactive mode
    console.print(f"[bold]Nice Code[/bold] [{config.provider} / {config.model}]")
    console.print("Mode interaktif — ketik task, AI langsung eksekusi. 'exit' untuk keluar.")
    console.print("-" * 50)

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    while True:
        try:
            user_input = typer.prompt("You")
        except (KeyboardInterrupt, EOFError):
            typer.echo("\nSampai jumpa!")
            break

        if user_input.lower() == "exit":
            typer.echo("Sampai jumpa!")
            break

        if not user_input.strip():
            continue

        messages.append({"role": "user", "content": user_input})

        # Snapshot messages untuk lambda (hindari closure issue)
        current_messages = list(messages)
        result, err = run_with_spinner(lambda: provider.chat_sync(current_messages, tools=TOOL_DEFINITIONS))

        if isinstance(err, KeyboardInterrupt):
            console.print("\n[yellow]Dibatalkan.[/yellow]")
            messages.pop()
            continue

        if err:
            console.print(f"[red]Error:[/red] {err}")
            messages.pop()
            continue

        console.print(f"\n[bold]AI:[/bold] {result}")
        messages.append({"role": "assistant", "content": result})
        typer.echo("-" * 50)
