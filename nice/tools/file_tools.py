import difflib
import os
from pathlib import Path

from rich.console import Console

console = Console()


def read_file(path: str) -> str:
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: File '{path}' not found."
    except Exception as e:
        return f"Error: {e}"


def write_file(path: str, content: str) -> str:
    file_path = Path(path)

    if file_path.exists():
        current = file_path.read_text(encoding="utf-8")

        if current == content:
            return f"No changes to '{path}'."

        diff = list(
            difflib.unified_diff(
                current.splitlines(keepends=True),
                content.splitlines(keepends=True),
                fromfile=f"{path}  (current)",
                tofile=f"{path}  (proposed)",
            )
        )

        console.print(f"\n[bold]Diff preview:[/bold] [cyan]{path}[/cyan]")
        for line in diff:
            if line.startswith("+++") or line.startswith("---"):
                console.print(f"[dim]{line}[/dim]", end="")
            elif line.startswith("@@"):
                console.print(f"[yellow]{line}[/yellow]", end="")
            elif line.startswith("+"):
                console.print(f"[green]{line}[/green]", end="")
            elif line.startswith("-"):
                console.print(f"[red]{line}[/red]", end="")
            else:
                console.print(line, end="")
        console.print()

    else:
        lines = content.splitlines()
        preview = "\n".join(f"+ {line}" for line in lines[:20])
        if len(lines) > 20:
            preview += f"\n... ({len(lines) - 20} more lines)"

        console.print(f"\n[bold]New file:[/bold] [cyan]{path}[/cyan]")
        console.print(f"[green]{preview}[/green]")
        console.print()

    choice = input("Apply? [y/n]: ").strip().lower()
    if choice != "y":
        return f"Write cancelled: '{path}'"

    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding="utf-8")
    return f"Written '{path}' ({len(content)} chars)."


def list_directory(path: str = ".") -> str:
    try:
        items = os.listdir(path or ".")
        if not items:
            return f"Directory '{path}' is empty."

        result = f"Directory '{path}':\n"
        for item in sorted(items):
            full = os.path.join(path, item)
            icon = "📁" if os.path.isdir(full) else "📄"
            result += f"  {icon} {item}\n"
        return result.strip()
    except FileNotFoundError:
        return f"Error: Directory '{path}' not found."
    except Exception as e:
        return f"Error: {e}"
