from pathlib import Path
from typing import Optional
import typer
from nice.providers.registry import get_active_provider
from nice.config.context import inject_context
from nice.tools.registry import TOOL_DEFINITIONS
from nice.cli._spinner import stream_markdown, console

SYSTEM_PROMPT = """You are a senior code reviewer. Analyse the provided code and give structured feedback.

For each finding use this format:
- [ERROR] <finding> — critical bugs, security issues, logic errors
- [WARNING] <finding> — potential problems, bad practices, edge cases
- [INFO] <finding> — style, readability, naming, minor suggestions

Rules:
- Reference specific line numbers where relevant
- Be concise and actionable
- Group findings by file if reviewing multiple files
- End with a short overall summary

Reply in the same language as the user's input."""

# Extensions considered as source code
CODE_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".go", ".rs", ".java", ".c", ".cpp",
    ".cs", ".rb", ".php", ".swift", ".kt", ".vue", ".svelte", ".html", ".css",
    ".scss", ".sql", ".sh", ".yaml", ".yml", ".toml", ".json",
}

SKIP_DIRS = {"node_modules", ".git", "__pycache__", ".venv", "dist", "build", ".next"}


def _collect_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    files = []
    for f in sorted(path.rglob("*")):
        if any(part in SKIP_DIRS for part in f.parts):
            continue
        if f.is_file() and f.suffix in CODE_EXTENSIONS:
            files.append(f)
    return files


def review_command(
    path: str = typer.Argument(".", help="File or directory to review"),
):
    """Review code for bugs, issues, and improvements."""
    target = Path(path)

    if not target.exists():
        console.print(f"[red]Error:[/red] '{path}' not found.")
        raise typer.Exit(1)

    provider = get_active_provider()
    system = inject_context(SYSTEM_PROMPT)

    if target.is_file():
        try:
            content = target.read_text(encoding="utf-8")
        except Exception as e:
            console.print(f"[red]Error reading file:[/red] {e}")
            raise typer.Exit(1)

        typer.echo(f"Reviewing {path}...\n")
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": f"Review this file ({path}):\n\n```\n{content}\n```"},
        ]
        stream_markdown(provider, messages)

    else:
        files = _collect_files(target)
        if not files:
            console.print(f"[yellow]No source files found in '{path}'.[/yellow]")
            raise typer.Exit(0)

        typer.echo(f"Reviewing {len(files)} file(s) in {path}...\n")

        # Build combined content (cap at ~8000 chars per file, 20 files max)
        parts = []
        for f in files[:20]:
            try:
                text = f.read_text(encoding="utf-8")[:8000]
                parts.append(f"### {f}\n```\n{text}\n```")
            except Exception:
                pass

        combined = "\n\n".join(parts)
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": f"Review the following files:\n\n{combined}"},
        ]
        stream_markdown(provider, messages)
