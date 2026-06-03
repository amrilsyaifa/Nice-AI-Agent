from nice.config.context import inject_context
from nice.providers.registry import get_active_provider
from nice.tools.registry import TOOL_DEFINITIONS, execute_tool

MAX_RETRY = 3

REFLECTION_PROMPT = """You are an AI engineer debugging an error.

You have tools: read_file, write_file, run_command, list_directory.

Your workflow:
1. Read the error that occurred
2. Read the problematic file
3. Analyse the root cause
4. Fix the file
5. Re-run to verify the fix

Reply in the same language as the user's input."""


def run_with_reflection(command: str, context_file: str = None) -> dict:
    """
    Run a command; if it errors, reflect and auto-fix, then retry.
    Returns dict with keys: success, output, attempts
    """
    provider = get_active_provider()
    attempts = []

    for attempt in range(1, MAX_RETRY + 1):
        print(f"\n{'=' * 50}")
        print(f"Attempt {attempt}/{MAX_RETRY}: {command}")
        print("=" * 50)

        result = execute_tool("run_command", {"command": command})
        attempts.append({"attempt": attempt, "output": result})

        is_error = (
            "error" in result.lower()
            or "traceback" in result.lower()
            or "exception" in result.lower()
            or "stderr" in result.lower()
        )

        if not is_error:
            print(f"Success on attempt {attempt}!")
            return {"success": True, "output": result, "attempts": attempts}

        print("Error detected, asking AI to fix...")

        error_context = f"""Command: `{command}`
Output/Error:
{result}"""

        if context_file:
            file_content = execute_tool("read_file", {"path": context_file})
            error_context += f"""

Contents of `{context_file}`:
{file_content}"""

        error_context += (
            "\nAnalyse this error and fix the problematic file, then re-run the command."
        )

        messages = [
            {"role": "system", "content": inject_context(REFLECTION_PROMPT)},
            {"role": "user", "content": error_context},
        ]

        provider.chat_sync(messages, tools=TOOL_DEFINITIONS)

    print(f"\nFailed after {MAX_RETRY} attempts. Manual intervention needed.")
    return {"success": False, "output": attempts[-1]["output"], "attempts": attempts}
