# nice

Your autonomous CLI AI engineer. Ask questions, run interactive chats, execute coding tasks with file/shell tools, and auto-fix broken commands — all from the terminal.

## Features

- **`ask`** — one-shot question to the AI
- **`chat`** — persistent interactive chat with conversation memory
- **`code`** — AI coding agent with read/write/shell tools
- **`fix`** — run a command with automatic error-reflection and retry loop
- **`config`** — manage provider and model settings

## Requirements

- Python >= 3.13
- [uv](https://github.com/astral-sh/uv)
- An API key for [OpenRouter](https://openrouter.ai) (or any OpenAI-compatible endpoint)

## Installation

Install uv if you haven't:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Clone and sync dependencies:

```bash
git clone <repo-url>
cd nice
uv sync
```

Run without installing globally:

```bash
uv run nice ask "Halo!"
```

Or install the `nice` command into the project's virtualenv and activate it:

```bash
uv sync
source .venv/bin/activate
nice ask "Halo!"
```

Install globally (available everywhere without activating venv):

```bash
uv tool install .
```

Uninstall:

```bash
uv tool uninstall nice
```

## Configuration

Create a `.env` file in the project root (or export variables in your shell):

```env
OPENAI_API_KEY=your_openrouter_api_key
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1   # default, can be omitted
```

Runtime config is stored at `~/.nice/config.json`. Defaults:

| Key        | Default                                  |
|------------|------------------------------------------|
| `provider` | `openai`                                 |
| `model`    | `liquid/lfm-2.5-1.2b-thinking:free`      |

Change them at any time:

```bash
nice config set model openai/gpt-4o
nice config set provider openai
```

## Usage

### Ask a single question

```bash
nice ask "Apa itu recursion?"
```

### Interactive chat (with persistent memory)

```bash
nice chat
```

Conversation history is saved to `~/.nice/history.json` and resumed on the next run.

In-session commands:

| Command | Action                     |
|---------|----------------------------|
| `exit`  | End the session            |
| `clear` | Wipe the conversation history |

### Coding agent with tools

```bash
nice code "Buat file hello.py yang print Hello World"
```

The agent can call these tools:

| Tool             | Description                          |
|------------------|--------------------------------------|
| `read_file`      | Read a file from disk                |
| `write_file`     | Write (or create) a file             |
| `list_directory` | List the contents of a directory     |
| `run_command`    | Execute a shell command              |

### Auto-fix a failing command

```bash
nice fix "python main.py"
nice fix "python main.py" --file main.py
```

`fix` runs the command, detects errors (traceback, stderr, exceptions), asks the AI to analyse and patch the relevant file, then retries — up to 3 times automatically. Pass `--file` to give the AI extra context about which file to inspect.

### Manage config

```bash
nice config list          # show all settings
nice config get model     # get a single value
nice config set model openai/gpt-4o-mini
```

### Show version

```bash
nice version
```

## Project Structure

```
nice/
├── nice/
│   ├── main.py              # CLI entry point (Typer app)
│   ├── cli/
│   │   ├── ask.py           # `nice ask`
│   │   ├── chat.py          # `nice chat`
│   │   ├── code.py          # `nice code`
│   │   ├── fix.py           # `nice fix`
│   │   ├── config_cmd.py    # `nice config`
│   │   └── version.py       # `nice version`
│   ├── config/
│   │   └── settings.py      # Load/save ~/.nice/config.json
│   ├── core/
│   │   └── reflection.py    # Error-reflection retry loop
│   ├── memory/
│   │   └── history.py       # Persistent conversation history
│   ├── providers/
│   │   ├── base.py          # BaseProvider abstract class
│   │   ├── openai_provider_sync.py  # OpenAI-compatible HTTP provider
│   │   └── registry.py      # Provider lookup
│   └── tools/
│       ├── file_tools.py    # read_file, write_file, list_directory
│       ├── shell_tools.py   # run_command
│       └── registry.py      # Tool definitions + executor
└── pyproject.toml
```

## How it works

1. **Provider layer** — `BaseProvider` defines `chat_sync` / `chat`. `OpenAIProvider` calls any OpenAI-compatible REST endpoint (default: OpenRouter) via `httpx`.
2. **Tool calling** — when the LLM returns `tool_calls`, `OpenAIProvider._handle_tool_calls` executes each tool locally, appends results back into the message list, and re-queries the LLM until it returns plain text.
3. **Reflection loop** — `nice fix` wraps a command in a retry loop; on failure it hands the error + optional file context to the LLM which patches the file using `write_file`, then retries the original command.
4. **Memory** — `ConversationHistory` serialises the message list to `~/.nice/history.json` after every turn so `nice chat` resumes seamlessly.

## License

MIT
