import os
import sys
from typing import Optional
import typer
from nice.planner.planner import create_plan
from nice.planner.executor import execute_plan
from nice.cli._spinner import run_with_spinner, console

def plan_command(
    goal: Optional[str] = typer.Argument(None, help="Goal to achieve"),
    execute: bool = typer.Option(False, "--execute", "-e", help="Execute immediately without confirmation"),
):
    """Create an execution plan with a feedback loop, then execute it."""

    if not goal:
        goal = typer.prompt("Goal")

    feedback = None
    previous_steps = None

    while True:
        typer.echo(f"\nGoal: {goal}")

        current_goal = goal
        current_feedback = feedback
        current_prev = previous_steps

        plan, err = run_with_spinner(
            lambda: create_plan(current_goal, current_feedback, current_prev)
        )

        if isinstance(err, KeyboardInterrupt):
            console.print("[yellow]Cancelled.[/yellow]")
            return
        if err:
            console.print(f"[red]Error:[/red] {err}")
            return

        plan.display()

        if not plan.steps:
            console.print("[red]Could not create a plan. Please try again.[/red]")
            return

        if execute:
            break

        typer.echo("  [a] Approve    [r] Revise    [c] Cancel")
        choice = typer.prompt("Choice").strip().lower()

        if choice == "a":
            break
        elif choice == "r":
            feedback = typer.prompt("Feedback")
            previous_steps = [s.description for s in plan.steps]
            continue
        else:
            typer.echo("Plan cancelled.")
            return

    # Execute plan
    plan = execute_plan(plan)

    # Restore terminal state in case a subprocess broke it
    if sys.platform != "win32":
        os.system("stty sane 2>/dev/null")

    typer.echo(f"\n{'=' * 50}")
    typer.echo("Summary:")
    plan.display()

    done = sum(1 for s in plan.steps if s.status.value == "done")
    total = len(plan.steps)
    typer.echo(f"{done}/{total} steps completed.")

    if plan.is_complete():
        typer.echo("Plan complete!")
    else:
        typer.echo("Plan did not complete fully.")
