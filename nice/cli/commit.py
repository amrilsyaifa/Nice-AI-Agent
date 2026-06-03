import subprocess
import typer
from nice.providers.registry import get_active_provider
from nice.cli._spinner import run_with_spinner, console

SYSTEM_PROMPT = """You are a git commit message writer.

Given a git diff, write a concise, descriptive commit message.

Rules:
- First line: imperative mood, max 72 chars (e.g. "Add user authentication")
- If needed, add a blank line then a short paragraph with more detail
- Focus on WHY, not just what changed
- No bullet points in the subject line
- Output ONLY the commit message — no explanations, no quotes, no markdown"""


def _run(cmd: str) -> tuple[str, int]:
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return (result.stdout + result.stderr).strip(), result.returncode


def commit_command(
    all: bool = typer.Option(False, "--all", "-a", help="Stage all tracked changes before committing"),
):
    """Generate a commit message from staged changes and commit."""

    if all:
        _, code = _run("git add -u")
        if code != 0:
            console.print("[red]Error:[/red] Failed to stage changes.")
            raise typer.Exit(1)

    diff, _ = _run("git diff --cached")

    if not diff.strip():
        console.print("[yellow]Nothing staged. Use `git add` first, or pass --all.[/yellow]")
        raise typer.Exit(0)

    # Also grab recent commits for style reference
    log, _ = _run("git log --oneline -5")

    provider = get_active_provider()

    user_content = f"Git diff (staged):\n\n```diff\n{diff}\n```"
    if log:
        user_content += f"\n\nRecent commits (for style reference):\n{log}"

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]

    proposed, err = run_with_spinner(lambda: provider.chat_sync(messages))

    if err:
        console.print(f"[red]Error:[/red] {err}")
        raise typer.Exit(1)

    proposed = proposed.strip()
    console.print(f"\n[bold]Proposed commit message:[/bold]\n\n[cyan]{proposed}[/cyan]\n")
    typer.echo("  [a] Accept    [e] Edit    [c] Cancel")
    choice = typer.prompt("Choice").strip().lower()

    if choice == "c":
        typer.echo("Cancelled.")
        raise typer.Exit(0)

    if choice == "e":
        proposed = typer.prompt("Commit message", default=proposed)

    _, code = _run(f'git commit -m {_quote(proposed)}')
    if code == 0:
        console.print("[green]Committed.[/green]")
    else:
        console.print("[red]Commit failed.[/red]")
        raise typer.Exit(1)


def _quote(s: str) -> str:
    escaped = s.replace("'", "'\\''")
    return f"'{escaped}'"
