"""Shared slash-command handling for interactive sessions (chat, code)."""
from pathlib import Path
from nice.cli._spinner import console

CHAT_HELP = """\
[bold]Available commands:[/bold]
  [cyan]exit[/cyan]               — end the session
  [cyan]clear[/cyan]              — reset conversation history
  [cyan]/model <name>[/cyan]      — switch model mid-session
  [cyan]/context <file>[/cyan]    — load a file as extra context
  [cyan]/usage[/cyan]             — show token usage from last request
  [cyan]/help[/cyan]              — show this help
"""

CODE_HELP = """\
[bold]Available commands:[/bold]
  [cyan]exit[/cyan]               — end the session
  [cyan]clear[/cyan]              — reset history
  [cyan]/model <name>[/cyan]      — switch model mid-session
  [cyan]/context <file>[/cyan]    — load a file as extra context
  [cyan]/usage[/cyan]             — show token usage from last request
  [cyan]/help[/cyan]              — show this help
"""


def show_usage(provider) -> None:
    usage = getattr(provider, "_last_usage", {})
    if not usage:
        console.print("[dim]No usage data yet. Make a request first.[/dim]")
        return
    pt = usage.get("prompt_tokens", "?")
    ct = usage.get("completion_tokens", "?")
    tt = usage.get("total_tokens", "?")
    console.print(f"[dim]tokens — in: {pt}  out: {ct}  total: {tt}[/dim]")


def print_usage_inline(provider) -> None:
    """Print usage on one line after a response (only when show_usage=true)."""
    usage = getattr(provider, "_last_usage", {})
    if not usage:
        return
    pt = usage.get("prompt_tokens", "?")
    ct = usage.get("completion_tokens", "?")
    tt = usage.get("total_tokens", "?")
    console.print(f"[dim]  ↳ {pt} in + {ct} out = {tt} tokens[/dim]")


def load_context_file(path_str: str) -> tuple[str, str | None]:
    """Read a file for /context. Returns (content, error_message)."""
    try:
        content = Path(path_str).read_text(encoding="utf-8")
        return content, None
    except FileNotFoundError:
        return "", f"File not found: {path_str}"
    except Exception as e:
        return "", str(e)
