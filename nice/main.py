import typer
from nice.cli.ask import ask_command
from nice.cli.version import version_command

app = typer.Typer(
    name="nice",
    help="Your autonomous CLI AI engineer",
    no_args_is_help=True,
)

app.command("ask")(ask_command)
app.command("version")(version_command)

if __name__ == "__main__":
    app()