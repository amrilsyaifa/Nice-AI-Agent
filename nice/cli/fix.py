import typer

from nice.core.reflection import run_with_reflection

def fix_command(
        command: str = typer.Argument(..., help="Command to run with auto-fix on error"),
        file: str = typer.Option(None, "--file", "-f", help="Relevant file for context")
):
    """Run a command and auto-fix errors until it succeeds."""
    typer.echo("Running with error reflection...")
    result = run_with_reflection(command, context_file=file)

    typer.echo(f"\n{'='*50}")
    if result["success"]:
        typer.echo(f"Success after {len(result['attempts'])} attempt(s)")
        typer.echo(f"\nOutput:\n{result['output']}")
    else:
        typer.echo(f"Failed after {len(result['attempts'])} attempt(s)")
        typer.echo(f"\nLast output:\n{result['output']}")
        typer.echo("\nTip: check the file manually.")
