import typer
from nice.providers.registry import get_active_provider
from nice.config.settings import load_config
from nice.memory.history import ConversationHistory

SYSTEM_PROMPT = "Kamu adalah AI assistant bernama Nice. Jawab selalu dalam Bahasa Indonesia. Kamu mengingat konteks percakapan sebelumnya."

def chat_command():
    """Chat interaktif dengan AI. Ketik 'exit' untuk keluar, 'clear' untuk hapus history."""

    config = load_config()
    provider = get_active_provider()
    history = ConversationHistory()

    typer.echo(f"Nice Chat [{config.provider} / {config.model}]")
    typer.echo("Ketik 'exit' untuk keluar, 'clear' untuk hapus history.")
    typer.echo("-" * 50)

    # Kalau ada history sebelumnya, kasih tahu user
    if not history.is_empty():
        typer.echo(f"(melanjutkan {len(history.messages)} pesan sebelumnya)\n")

    while True:
        # Terima input dari user
        try:
            user_input = typer.prompt("You")
        except (KeyboardInterrupt, EOFError):
            typer.echo("\nSampai jumpa!")
            break

        # Handle command khusus
        if user_input.lower() == "exit":
            typer.echo("Sampai jumpa!")
            break

        elif user_input.lower() == "clear":
            history.clear()
            typer.echo("History dihapus.")
            continue

        if not user_input.strip():
            continue

        # Simpan pesan user ke history
        history.add("user", user_input)

        # Kirim ke AI
        typer.echo("AI: ", nl=False)
        messages = history.get_messages(SYSTEM_PROMPT)
        response = provider.chat_sync(messages)

        # Tampilkan dan simpan response
        typer.echo(response)
        history.add("assistant", response)
        typer.echo("-" * 50)
