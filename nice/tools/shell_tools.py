import os
import subprocess

# These are always blocked, regardless of user config.
_ALWAYS_BLOCKED = [
    "rm -rf /",
    "rm -rf ~",
    "rm -rf *",
    "mkfs",
    "dd if=",
    ":(){:|:&};:",     # fork bomb
    "chmod -R 777 /",
    "DROP TABLE",
    "> /dev/sda",
]


def _is_blocked(command: str, extra: list[str]) -> str | None:
    """Return the matched pattern if the command is blocked, else None."""
    for pattern in _ALWAYS_BLOCKED + extra:
        if pattern.lower() in command.lower():
            return pattern
    return None


def run_command(command: str, timeout: int = None) -> str:
    """Execute a shell command and return its output."""
    from nice.config.settings import load_config
    config = load_config()

    if timeout is None:
        timeout = config.command_timeout

    # Security: check blocklist
    matched = _is_blocked(command, config.blocked_commands)
    if matched:
        return f"Error: Command blocked — matched pattern '{matched}'."

    # Security: confirm before running (if enabled)
    if config.confirm_commands:
        print(f"\n{'─' * 50}")
        print(f"  Command: {command}")
        print(f"{'─' * 50}")
        try:
            choice = input("Execute? [y/n]: ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            return "Command execution cancelled."
        if choice != "y":
            return "Command execution cancelled by user."

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            stdin=subprocess.DEVNULL,
            env={**os.environ, "CI": "true", "NO_COLOR": "1"},
        )
        output = result.stdout
        if result.stderr:
            output += f"\nSTDERR: {result.stderr}"
        return output.strip() or "(no output)"
    except subprocess.TimeoutExpired:
        return f"Error: Command timed out after {timeout}s."
    except Exception as e:
        return f"Error: {e}"
