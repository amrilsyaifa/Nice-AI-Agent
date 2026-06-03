import typer

from nice.config.context import inject_context
from nice.providers.registry import get_active_provider
from nice.tools.registry import TOOL_DEFINITIONS, execute_tool

MAX_RETRY = 3

SYSTEM_PROMPT = """You are an AI engineer fixing failing tests.

You have tools: read_file, write_file, run_command, list_directory.

Workflow:
1. Read the test output carefully
2. Identify which test(s) are failing and why
3. Read the relevant source file(s)
4. Fix the code (not the tests, unless the test itself is wrong)
5. Report what you changed

Reply in the same language as the user's input."""


def test_command(
    command: str = typer.Argument(..., help="Test command to run, e.g. 'pytest' or 'npm test'"),
):
    """Run a test suite and auto-fix failures."""
    provider = get_active_provider()
    system = inject_context(SYSTEM_PROMPT)

    for attempt in range(1, MAX_RETRY + 1):
        typer.echo(f"\n{'=' * 50}")
        typer.echo(f"Attempt {attempt}/{MAX_RETRY}: {command}")
        typer.echo("=" * 50)

        output = execute_tool("run_command", {"command": command})
        typer.echo(output)

        is_failure = any(
            kw in output.lower()
            for kw in ("failed", "failure", "error", "traceback", "exception", "stderr")
        )

        if not is_failure:
            typer.echo(f"\nAll tests passed on attempt {attempt}!")
            return

        if attempt == MAX_RETRY:
            break

        typer.echo(
            f"\nTest failures detected. Asking AI to fix (attempt {attempt}/{MAX_RETRY - 1})..."
        )

        messages = [
            {"role": "system", "content": system},
            {
                "role": "user",
                "content": (
                    f"Test command: `{command}`\n\n"
                    f"Output:\n```\n{output}\n```\n\n"
                    "Analyse the failures, fix the source code, and report what you changed."
                ),
            },
        ]

        fix_output = provider.chat_sync(messages, tools=TOOL_DEFINITIONS)
        typer.echo(f"\nAI: {fix_output}")

    typer.echo(f"\nFailed after {MAX_RETRY} attempts. Manual intervention needed.")
    raise typer.Exit(1)
