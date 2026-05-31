import typer

from nice.core.reflection import run_with_reflection

def fix_command(
        command: str = typer.Argument(..., help="Command yang ingin dijalankan"),
        file: str = typer.Option(None, "--file", "-f", help="File yang relevan dengan command")
):
    """Jalankan command dengan auto-fix kalau error."""
    typer.echo("🔧 Menjalankan dengan error reflection...")
    result = run_with_reflection(command, context_file=file)

    typer.echo(f"\n{'='*50}")
    if result["success"]:
        typer.echo(f"✅ Berhasil setelah {len(result['attempts'])} attempt")
        typer.echo(f"\nOutput:\n{result['output']}")
    else:
        typer.echo(f"❌ Gagal setelah {len(result['attempts'])} attempt")
        typer.echo(f"\nOutput terakhir:\n{result['output']}")
        typer.echo("\n💡 Coba periksa file secara manual.")