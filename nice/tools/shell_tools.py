import subprocess

def run_command(command: str, timeout: int = 30) -> str:
    """Jalankan shell command dan return outputnya."""

    # Blocklist command yang berbahaya
    BLOCKED = ["rm -rf", "DROP TABLE", "mkfs", "dd if=", ":(){:|:&};:"]

    for blocked in BLOCKED:
        if blocked in command:
            return f"❌ Command '{command}' diblokir karena berbahaya"
        
    try:
        result = subprocess.run(
            command, 
            shell=True,
            capture_output = True,
            text = True,
            timeout = timeout,
        )
        output = ""
        if result.stdout:
             output += result.stdout
        if result.stderr:
            output += f"\nSTDERR: {result.stderr}"
        if not output:
            output = "(tidak ada output)"
        return output
    except subprocess.TimeoutExpired:
        return f"❌ Command timeout setelah {timeout} detik"
    except Exception as e:
        return f"❌ Error: {e}"