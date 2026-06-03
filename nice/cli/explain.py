import typer
from nice.providers.registry import get_active_provider
from nice.config.context import inject_context
from nice.cli._spinner import stream_markdown, console

SYSTEM_PROMPT = """You are a code explainer. Explain the provided code clearly.

Structure your explanation:
1. **What it does** — one-sentence summary
2. **How it works** — key logic, flow, and important decisions
3. **Notable details** — patterns, algorithms, non-obvious behaviour, potential gotchas

Be concise. Avoid restating what is already obvious from the code.
Reply in the same language as the user's input."""


def explain_command(
    target: str = typer.Argument(..., help="File to explain, optionally with line: file.py:42"),
):
    """Explain what a piece of code does."""
    provider = get_active_provider()
    system = inject_context(SYSTEM_PROMPT)

    # Parse optional :line suffix
    focus_line = None
    path_str = target
    if ":" in target:
        parts = target.rsplit(":", 1)
        if parts[1].isdigit():
            path_str, focus_line = parts[0], int(parts[1])

    from pathlib import Path
    file_path = Path(path_str)

    if not file_path.exists():
        console.print(f"[red]Error:[/red] '{path_str}' not found.")
        raise typer.Exit(1)

    try:
        lines = file_path.read_text(encoding="utf-8").splitlines()
    except Exception as e:
        console.print(f"[red]Error reading file:[/red] {e}")
        raise typer.Exit(1)

    if focus_line:
        # Show ±40 lines around the focus line
        start = max(0, focus_line - 41)
        end = min(len(lines), focus_line + 40)
        snippet = "\n".join(
            f"{i + start + 1:4}  {l}" for i, l in enumerate(lines[start:end])
        )
        label = f"{path_str} (lines {start + 1}–{end})"
        user_msg = f"Explain this section of `{label}`:\n\n```\n{snippet}\n```"
    else:
        content = "\n".join(f"{i + 1:4}  {l}" for i, l in enumerate(lines))
        user_msg = f"Explain `{path_str}`:\n\n```\n{content}\n```"

    typer.echo(f"Explaining {target}...\n")
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user_msg},
    ]
    stream_markdown(provider, messages)
