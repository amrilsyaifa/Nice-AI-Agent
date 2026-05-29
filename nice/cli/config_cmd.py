import typer
from nice.config.settings import load_config, save_config

config_app = typer.Typer(help="Manage Nice configuration.")

@config_app.command("set")
def config_set(key: str, value: str):
    """Set nilai config. Contoh: nice config set provider openai"""
    config = load_config()

    if key == "provider":
        config.provider = value
    elif key == "model":
        config.model = value
    else:
        typer.echo(f"❌ Key '{key}' tidak dikenal. Tersedia: provider, model")
        raise typer.Exit(1)

    save_config(config)
    typer.echo(f"✅ {key} = {value}")

@config_app.command("get")
def config_get(key: str):
    """Lihat nilai config. Contoh: nice config get provider"""
    config = load_config()

    if key == "provider":
        typer.echo(config.provider)
    elif key == "model":
        typer.echo(config.model)
    else:
        typer.echo(f"❌ Key '{key}' tidak dikenal. Tersedia: provider, model")
        raise typer.Exit(1)

@config_app.command("list")
def config_list():
    """Tampilkan semua config."""
    config = load_config()
    typer.echo(f"provider = {config.provider}")
    typer.echo(f"model    = {config.model}")