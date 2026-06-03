import typer
from nice.config.settings import load_config, save_config

config_app = typer.Typer(help="Manage Nice configuration.")

VALID_KEYS = (
    "provider", "model", "api_key", "base_url",
    "show_usage", "command_timeout",
    "blocked_commands", "confirm_commands",
    "log_level",
)

BOOL_KEYS  = ("show_usage", "confirm_commands")
INT_KEYS   = ("command_timeout",)
LIST_KEYS  = ("blocked_commands",)
LEVEL_KEYS = ("log_level",)
VALID_LEVELS = ("debug", "info", "warning", "error")


@config_app.command("set")
def config_set(key: str, value: str):
    """Set a config value. Example: nice config set model gpt-4o

    For blocked_commands pass a comma-separated list:
      nice config set blocked_commands "sudo rm,git push --force"
    """
    if key not in VALID_KEYS:
        typer.echo(f"Unknown key '{key}'. Available: {', '.join(VALID_KEYS)}")
        raise typer.Exit(1)

    config = load_config()

    if key in LEVEL_KEYS:
        if value.lower() not in VALID_LEVELS:
            typer.echo(f"Invalid log level '{value}'. Use: {', '.join(VALID_LEVELS)}")
            raise typer.Exit(1)
        config.log_level = value.lower()
    elif key in BOOL_KEYS:
        setattr(config, key, value.lower() in ("true", "1", "yes"))
    elif key in INT_KEYS:
        try:
            setattr(config, key, int(value))
        except ValueError:
            typer.echo(f"'{key}' must be an integer.")
            raise typer.Exit(1)
    elif key in LIST_KEYS:
        setattr(config, key, [s.strip() for s in value.split(",") if s.strip()])
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
    typer.echo(f"provider          = {config.provider}")
    typer.echo(f"model             = {config.model}")
    typer.echo(f"api_key           = {config.api_key[:8]}..." if config.api_key else "api_key           = (not set)")
    typer.echo(f"base_url          = {config.base_url}")
    typer.echo(f"show_usage        = {config.show_usage}")
    typer.echo(f"command_timeout   = {config.command_timeout}s")
    typer.echo(f"confirm_commands  = {config.confirm_commands}")
    blocked = ", ".join(config.blocked_commands) if config.blocked_commands else "(none)"
    typer.echo(f"blocked_commands  = {blocked}")
    typer.echo(f"log_level         = {config.log_level}")
