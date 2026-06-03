import typer
from nice.config.settings import load_config, save_config

config_app = typer.Typer(help="Manage Nice configuration.")

VALID_KEYS = ("provider", "model", "api_key", "base_url", "show_usage", "command_timeout")


@config_app.command("set")
def config_set(key: str, value: str):
    """Set a config value. Example: nice config set model gpt-4o"""
    if key not in VALID_KEYS:
        typer.echo(f"Unknown key '{key}'. Available: {', '.join(VALID_KEYS)}")
        raise typer.Exit(1)

    config = load_config()

    if key == "show_usage":
        config.show_usage = value.lower() in ("true", "1", "yes")
    elif key == "command_timeout":
        try:
            config.command_timeout = int(value)
        except ValueError:
            typer.echo("command_timeout must be an integer (seconds).")
            raise typer.Exit(1)
    else:
        setattr(config, key, value)

    save_config(config)
    typer.echo(f"{key} = {getattr(config, key)}")


@config_app.command("get")
def config_get(key: str):
    """Get a config value. Example: nice config get model"""
    if key not in VALID_KEYS:
        typer.echo(f"Unknown key '{key}'. Available: {', '.join(VALID_KEYS)}")
        raise typer.Exit(1)
    config = load_config()
    typer.echo(getattr(config, key))


@config_app.command("list")
def config_list():
    """Show all config values."""
    config = load_config()
    typer.echo(f"provider         = {config.provider}")
    typer.echo(f"model            = {config.model}")
    typer.echo(f"api_key          = {config.api_key[:8]}..." if config.api_key else "api_key          = (not set)")
    typer.echo(f"base_url         = {config.base_url}")
    typer.echo(f"show_usage       = {config.show_usage}")
    typer.echo(f"command_timeout  = {config.command_timeout}s")
