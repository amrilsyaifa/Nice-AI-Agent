import subprocess


def _git(cmd: str) -> str:
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True,
        timeout=10,
    )
    output = (result.stdout + result.stderr).strip()
    return output or "(no output)"


def git_status() -> str:
    """Show the working tree status (branch + changed files)."""
    return _git("git status --short --branch")


def git_diff(staged: bool = False) -> str:
    """Show changes. Pass staged=true to see staged (cached) diff."""
    flag = "--staged" if staged else ""
    output = _git(f"git diff {flag}")
    if not output or output == "(no output)":
        return "No changes." if not staged else "Nothing staged."
    return output


def git_log(n: int = 10) -> str:
    """Show the last n commit messages (default 10)."""
    return _git(f"git log --oneline -{n}")
