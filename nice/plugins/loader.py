"""
Plugin loader — reads Python files from ~/.nice/plugins/ at startup.

Each plugin file can expose:
  TOOL_DEFINITIONS  list[dict]   — OpenAI-format tool schemas
  TOOL_FUNCTIONS    dict[str, callable] — name → function
  COMMANDS          dict[str, callable] — name → typer command function
"""
import importlib.util
from pathlib import Path
from nice.core.logger import get_logger

PLUGINS_DIR = Path.home() / ".nice" / "plugins"
log = get_logger("plugins")


def load_plugins() -> tuple[list, dict, dict]:
    """
    Load all *.py files from ~/.nice/plugins/.
    Returns (extra_tool_defs, extra_tool_funcs, extra_commands).
    """
    extra_defs: list = []
    extra_funcs: dict = {}
    extra_commands: dict = {}

    if not PLUGINS_DIR.exists():
        return extra_defs, extra_funcs, extra_commands

    for plugin_file in sorted(PLUGINS_DIR.glob("*.py")):
        try:
            spec = importlib.util.spec_from_file_location(plugin_file.stem, plugin_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            defs = getattr(module, "TOOL_DEFINITIONS", [])
            funcs = getattr(module, "TOOL_FUNCTIONS", {})
            cmds = getattr(module, "COMMANDS", {})

            extra_defs.extend(defs)
            extra_funcs.update(funcs)
            extra_commands.update(cmds)

            log.info(
                "Loaded plugin %s — %d tool(s), %d command(s)",
                plugin_file.name,
                len(defs),
                len(cmds),
            )

        except Exception as exc:
            log.warning("Failed to load plugin %s: %s", plugin_file.name, exc)
            print(f"[nice] Warning: plugin '{plugin_file.name}' failed to load — {exc}")

    return extra_defs, extra_funcs, extra_commands
