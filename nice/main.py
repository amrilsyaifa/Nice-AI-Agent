import typer

from nice.cli.ask import ask_command
from nice.cli.chat import chat_command
from nice.cli.code import code_command
from nice.cli.commit import commit_command
from nice.cli.config_cmd import config_app
from nice.cli.explain import explain_command
from nice.cli.fix import fix_command
from nice.cli.plan import plan_command
from nice.cli.review import review_command
from nice.cli.test_cmd import test_command
from nice.cli.version import version_command

app = typer.Typer(
    name="nice",
    help="Your autonomous CLI AI engineer",
    no_args_is_help=True,
)


@app.callback()
def startup() -> None:
    """Initialise logging and load plugins before any command runs."""
    from nice.config.settings import load_config
    from nice.core.logger import setup_logging
    from nice.plugins.loader import load_plugins
    from nice.tools.registry import TOOL_DEFINITIONS, TOOL_FUNCTIONS

    config = load_config()
    setup_logging(config.log_level)

    extra_defs, extra_funcs, extra_commands = load_plugins()
    TOOL_DEFINITIONS.extend(extra_defs)
    TOOL_FUNCTIONS.update(extra_funcs)
    for name, fn in extra_commands.items():
        app.command(name)(fn)


app.command("ask")(ask_command)
app.command("chat")(chat_command)
app.command("code")(code_command)
app.command("commit")(commit_command)
app.command("explain")(explain_command)
app.command("fix")(fix_command)
app.command("plan")(plan_command)
app.command("review")(review_command)
app.command("test")(test_command)
app.command("version")(version_command)
app.add_typer(config_app, name="config")

if __name__ == "__main__":
    app()
