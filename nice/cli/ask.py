import typer

def ask_command(prompt: str):
    """Tanya sesuatu ke AI."""
    typer.echo(f"kamu bertanya: {prompt}")