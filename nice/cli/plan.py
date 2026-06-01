import os
import sys
from typing import Optional
import typer
from nice.planner.planner import create_plan
from nice.planner.executor import execute_plan
from nice.cli._spinner import run_with_spinner, console

def plan_command(
    goal: Optional[str] = typer.Argument(None, help="Goal yang ingin dicapai"),
    execute: bool = typer.Option(False, "--execute", "-e", help="Langsung eksekusi tanpa konfirmasi"),
):
    """Buat execution plan dengan feedback loop, lalu eksekusi."""

    if not goal:
        goal = typer.prompt("Goal")

    feedback = None
    previous_steps = None

    while True:
        typer.echo(f"\nGoal: {goal}")

        # Buat plan dengan spinner
        current_goal = goal
        current_feedback = feedback
        current_prev = previous_steps

        plan, err = run_with_spinner(
            lambda: create_plan(current_goal, current_feedback, current_prev)
        )

        if isinstance(err, KeyboardInterrupt):
            console.print("[yellow]Dibatalkan.[/yellow]")
            return
        if err:
            console.print(f"[red]Error:[/red] {err}")
            return

        plan.display()

        if not plan.steps:
            console.print("[red]Tidak bisa membuat plan. Coba lagi.[/red]")
            return

        if execute:
            break

        # Feedback loop
        typer.echo("  [a] Approve    [r] Revisi    [c] Cancel")
        choice = typer.prompt("Pilihan").strip().lower()

        if choice == "a":
            break
        elif choice == "r":
            feedback = typer.prompt("Masukan")
            previous_steps = [s.description for s in plan.steps]
            continue
        else:
            typer.echo("Plan dibatalkan.")
            return

    # Eksekusi plan
    plan = execute_plan(plan)

    # Restore terminal state jika subprocess merusaknya
    if sys.platform != "win32":
        os.system("stty sane 2>/dev/null")

    typer.echo(f"\n{'=' * 50}")
    typer.echo("Summary:")
    plan.display()

    done = sum(1 for s in plan.steps if s.status.value == "done")
    total = len(plan.steps)
    typer.echo(f"{done}/{total} steps berhasil.")

    if plan.is_complete():
        typer.echo("Plan selesai!")
    else:
        typer.echo("Plan belum selesai sepenuhnya.")
