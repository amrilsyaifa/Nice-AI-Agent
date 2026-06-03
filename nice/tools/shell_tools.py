import os
import subprocess


def run_command(command: str, timeout: int = None) -> str:
    """Execute a shell command and return its output."""
    BLOCKED = ["rm -rf", "DROP TABLE", "mkfs", "dd if=", ":(){:|:&};:"]
    for blocked in BLOCKED:
        if blocked in command:
            return f"Error: Command blocked for safety: '{blocked}'"

    if timeout is None:
        from nice.config.settings import load_config
        timeout = load_config().command_timeout

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
