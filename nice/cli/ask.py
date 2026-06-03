import typer

from nice.cli._spinner import console, stream_markdown, stream_quiet
from nice.config.settings import load_config
from nice.providers.registry import get_active_provider


def ask_command(
    prompt: str = typer.Argument(..., help="Question to ask the AI."),
    quiet: bool = typer.Option(
        False, "--quiet", "-q", help="Plain output — no markdown, no decorations."
    ),
):
    """Ask the AI a question."""
    config = load_config()
    provider = get_active_provider()

    if not quiet:
        typer.echo(f"[{config.provider} / {config.model}]\n")

    messages = [
        {
            "role": "system",
            "content": "You are a helpful AI assistant. Reply in the same language as the user's input.",
        },
        {"role": "user", "content": prompt},
    ]

    stream_fn = stream_quiet if quiet else stream_markdown
    _, err = stream_fn(provider, messages)

    if err and not isinstance(err, KeyboardInterrupt):
        console.print(f"[red]Error:[/red] {err}")
        raise typer.Exit(1)

    if not quiet and config.show_usage:
        from nice.cli._slash import print_usage_inline

        print_usage_inline(provider)
