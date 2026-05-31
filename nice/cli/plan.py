import typer
from nice.planner.planner import create_plan
from nice.planner.executor import execute_plan

def plan_command(
    goal: str = typer.Argument(..., help="Goal yang ingin dicapai"),
    execute: bool = typer.Option(False, "--execute", "-e", help="Langsung eksekusi tanpa konfirmasi")
):
    """Buat execution plan untuk sebuah goal, lalu eksekusi."""
    typer.echo(f"\n🎯 Goal: {goal}")
    typer.echo("⏳ Membuat plan...\n")

    # Buat plan
    plan = create_plan(goal)
    plan.display()

    if not plan.steps:
        typer.echo("❌ Tidak bisa membuat plan. Coba lagi.")
        raise typer.Exit(1)

    # Konfirmasi eksekusi
    if not execute:
        confirm = input("Eksekusi plan ini? (y/n): ").strip().lower()
        if confirm != "y":
            typer.echo("Plan dibatalkan.")
            raise typer.Exit(0)

    # Eksekusi
    plan = execute_plan(plan)

    # Summary
    typer.echo(f"\n{'='*50}")
    typer.echo("📊 Summary:")
    plan.display()

    done = sum(1 for s in plan.steps if s.status.value == "done")
    total = len(plan.steps)
    typer.echo(f"\n{done}/{total} steps berhasil.")

    if plan.is_complete():
        typer.echo("🎉 Plan selesai!")
    else:
        typer.echo("⚠️  Plan belum selesai sepenuhnya.")