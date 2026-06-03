# nice

Your autonomous CLI AI engineer. Ask questions, run interactive chats, execute coding tasks with file and shell tools, plan and execute multi-step goals, review and explain code, generate commit messages, and auto-fix broken commands — all from the terminal.

## Features

- **Streaming output** — responses render token-by-token with full Markdown formatting
- **Multiple providers** — OpenAI-compatible (OpenRouter), Anthropic Claude, Ollama (local)
- **9 built-in tools** — read/write files, run commands, web search, fetch URLs, git operations
- **Context file** — place `.nice.md` in any project for automatic AI context injection
- **Diff preview** — shows a coloured diff before the AI writes any file
- **Persistent history** — `chat` and `code` sessions resume where you left off
- **Plugin system** — drop a `.py` file in `~/.nice/plugins/` to add custom tools or commands
- **Activity log** — everything logged to `~/.nice/nice.log`

## Requirements

- An API key for [OpenRouter](https://openrouter.ai) or any OpenAI-compatible endpoint

## Installation

### Option 1 — Standalone binary (recommended, no Python needed)

**macOS / Linux:**
```bash
curl -fsSL https://raw.githubusercontent.com/amrilsyaifa/Nice-AI-Agent/main/scripts/install.sh | bash
```

**Windows (PowerShell):**
```powershell
iwr https://raw.githubusercontent.com/amrilsyaifa/Nice-AI-Agent/main/scripts/install.ps1 | iex
```

Or download the binary directly from [Releases](https://github.com/amrilsyaifa/Nice-AI-Agent/releases/latest):

| Platform | File |
|----------|------|
| macOS Apple Silicon | `nice-macos-arm64` |
| macOS Intel | `nice-macos-x86_64` |
| Linux x86_64 | `nice-linux-x86_64` |
| Windows x86_64 | `nice-windows-x86_64.exe` |

### Option 2 — pip / uv (requires Python >= 3.13)

```bash
pip install nice-ai
# or
uv tool install nice-ai
# or
pipx install nice-ai
```

### Option 3 — from source

```bash
git clone https://github.com/amrilsyaifa/Nice-AI-Agent.git
cd Nice-AI-Agent
uv sync
uv tool install .
```

## Configuration

All config lives at `~/.nice/config.json`.

```bash
nice config set api_key   YOUR_API_KEY
nice config set base_url  https://openrouter.ai/api/v1
nice config set model     openai/gpt-4o
nice config set provider  openai

nice config list          # show all settings
nice config get model     # get one value
```

| Key | Default | Description |
|-----|---------|-------------|
| `provider` | `openai` | Active provider: `openai`, `claude`, `ollama` |
| `model` | `liquid/lfm-2.5-1.2b-thinking:free` | Model name |
| `api_key` | *(required)* | API key for the active provider |
| `base_url` | `https://openrouter.ai/api/v1` | API base URL |
| `show_usage` | `false` | Print token count after every response |
| `command_timeout` | `60` | Shell command timeout in seconds |
| `confirm_commands` | `false` | Ask before running any shell command |
| `blocked_commands` | *(empty)* | Extra patterns to block (comma-separated) |
| `log_level` | `warning` | Log verbosity: `debug`, `info`, `warning`, `error` |

### Provider setup

**OpenAI / OpenRouter (default)**
```bash
nice config set provider openai
nice config set api_key  YOUR_OPENROUTER_KEY
```

**Anthropic Claude**
```bash
nice config set provider claude
nice config set api_key  YOUR_ANTHROPIC_KEY
nice config set model    claude-sonnet-4-6
```

**Ollama (local, no internet)**
```bash
ollama pull llama3.2
nice config set provider ollama
nice config set model    llama3.2
# base_url defaults to http://localhost:11434/v1 — no api_key needed
```

---

## Commands

### `nice ask`

One-shot question. Streams a Markdown response.

```bash
nice ask "What is a race condition?"
nice ask "List sorting algorithms" --quiet   # plain text, no decoration
```

### `nice chat`

Interactive chat with persistent memory and named sessions.

```bash
nice chat                          # default session
nice chat --session work           # named session
nice chat --list                   # list all sessions
nice chat --delete work            # delete a session
nice chat --session work --export  # export to Markdown
nice chat --session work --export-json
```

In-session commands:

| Command | Action |
|---------|--------|
| `exit` | End the session |
| `clear` | Reset history |
| `/model <name>` | Switch model without restarting |
| `/context <file>` | Load a file as extra context for this session |
| `/usage` | Show token count from last request |
| `/help` | List all commands |

History is saved to `~/.nice/history.json` (default) or `~/.nice/sessions/<name>.json`.
When total conversation length exceeds 40,000 characters, older messages are automatically summarised to keep context manageable.

### `nice code`

AI coding agent with tools. One-shot or interactive.

```bash
nice code "Create a FastAPI hello-world app"   # one-shot
nice code                                       # interactive (history persists)
nice code --clear                               # reset interactive history
nice code "Create config.json" --quiet          # plain output for scripting
```

Interactive mode has the same slash commands as `nice chat`.
History saved to `~/.nice/code_history.json`.

### `nice plan`

Break a goal into steps, review/revise the plan, then execute.

```bash
nice plan "Build a REST API with Flask"
nice plan          # prompts for goal interactively
nice plan -e "..." # skip review, execute immediately
```

At the plan review prompt:

| Choice | Action |
|--------|--------|
| `a` | Approve and execute |
| `r` | Revise — type feedback, get a new plan |
| `c` | Cancel |

### `nice fix`

Run a command and auto-fix errors (up to 3 attempts).

```bash
nice fix "python main.py"
nice fix "pytest tests/" --file src/main.py   # give AI the file for context
```

### `nice review`

Review code for bugs, issues, and improvements. Output uses `[ERROR]`, `[WARNING]`, `[INFO]` tags.

```bash
nice review main.py          # single file
nice review src/             # whole directory (skips node_modules, .git, etc.)
```

### `nice explain`

Explain what a piece of code does.

```bash
nice explain utils.py         # whole file
nice explain utils.py:42      # focus on line 42 (±40 lines shown)
```

### `nice commit`

Generate a commit message from staged changes.

```bash
nice commit          # uses git diff --cached
nice commit --all    # stages all tracked changes first (git add -u)
```

Options at the review prompt: `[a]` accept · `[e]` edit · `[c]` cancel.

### `nice test`

Run a test suite and auto-fix failures (up to 3 attempts).

```bash
nice test "pytest"
nice test "npm test"
```

### `nice version`

```bash
nice version
```

---

## Tools

All tools are available to the AI in `code`, `plan`, `fix`, and `test`.

| Tool | Description |
|------|-------------|
| `read_file` | Read a file from disk |
| `write_file` | Write/create a file (shows diff preview first) |
| `list_directory` | List directory contents |
| `run_command` | Execute a shell command |
| `web_search` | Search with DuckDuckGo (no API key needed) |
| `fetch_url` | Fetch and read a web page as text |
| `git_status` | `git status --short --branch` |
| `git_diff` | Working-tree or staged diff |
| `git_log` | Recent commit history |

---

## Context file

Create `.nice.md` in any project root:

```markdown
## Stack
- React 18 + Vite + TypeScript
- Tailwind CSS v4

## Conventions
- Components in `src/components/`, one file per component
- Named exports only
- API calls go through `src/lib/api.ts`
```

`nice` reads `.nice.md` automatically in `ask`, `chat`, `code`, `plan`, and `fix`. No flags needed.

---

## Diff preview

Before writing any file the AI shows a diff and asks for confirmation:

```
Diff preview: src/App.tsx
--- src/App.tsx  (current)
+++ src/App.tsx  (proposed)
@@ -1,4 +1,5 @@
 import React from 'react'
-function App() {
+function App({ name }: { name: string }) {
Apply? [y/n]:
```

New files show a preview of the first 20 lines before creation.

---

## Security

```bash
# Block specific command patterns
nice config set blocked_commands "sudo rm,git push --force,npm publish"

# Require confirmation before every shell command
nice config set confirm_commands true
```

Certain commands are always blocked regardless of config: `rm -rf /`, `mkfs`, `dd if=`, fork bombs, and similar destructive operations.

---

## Plugin system

Drop a `.py` file in `~/.nice/plugins/` to extend Nice with custom tools or CLI commands:

```python
# ~/.nice/plugins/jira.py

TOOL_DEFINITIONS = [{
    "type": "function",
    "function": {
        "name": "get_jira_ticket",
        "description": "Fetch a Jira ticket",
        "parameters": {
            "type": "object",
            "properties": {"ticket_id": {"type": "string"}},
            "required": ["ticket_id"]
        }
    }
}]

TOOL_FUNCTIONS = {
    "get_jira_ticket": lambda ticket_id: f"Ticket {ticket_id}: ..."
}

# Optional: add a new CLI command
import typer

def command_jira(ticket_id: str):
    """Open a Jira ticket."""
    typer.echo(f"Opening {ticket_id}...")

COMMANDS = {"jira": command_jira}
```

Plugins are loaded at startup. Errors in a plugin print a warning but do not crash the app.

---

## Logging

```bash
nice config set log_level info    # debug | info | warning | error
tail -f ~/.nice/nice.log
```

Logs include: tool calls, API requests, plugin loading, blocked commands, and errors.

---

## Project structure

```
nice/
├── nice/
│   ├── main.py                  # CLI entry point + plugin loader
│   ├── cli/
│   │   ├── _slash.py            # Shared slash-command helpers
│   │   ├── _spinner.py          # stream_markdown, stream_quiet, run_with_spinner
│   │   ├── ask.py               # nice ask
│   │   ├── chat.py              # nice chat
│   │   ├── code.py              # nice code
│   │   ├── commit.py            # nice commit
│   │   ├── explain.py           # nice explain
│   │   ├── fix.py               # nice fix
│   │   ├── plan.py              # nice plan
│   │   ├── review.py            # nice review
│   │   ├── test_cmd.py          # nice test
│   │   ├── version.py           # nice version
│   │   └── config_cmd.py        # nice config
│   ├── config/
│   │   ├── settings.py          # NiceConfig — load/save ~/.nice/config.json
│   │   └── context.py           # .nice.md loader
│   ├── core/
│   │   ├── logger.py            # Logging setup → ~/.nice/nice.log
│   │   └── reflection.py        # Error-reflection retry loop (nice fix)
│   ├── memory/
│   │   └── history.py           # ConversationHistory, sessions, export, compress
│   ├── planner/
│   │   ├── plan.py              # ExecutionPlan + Step data classes
│   │   ├── planner.py           # LLM plan creation with feedback support
│   │   └── executor.py          # Step-by-step plan execution
│   ├── plugins/
│   │   └── loader.py            # Load ~/.nice/plugins/*.py at startup
│   ├── providers/
│   │   ├── base.py              # BaseProvider ABC
│   │   ├── http_provider.py     # OpenAI-compatible (streaming, tool use, usage tracking)
│   │   ├── claude_provider.py   # Anthropic direct API
│   │   ├── ollama_provider.py   # Ollama local models
│   │   └── registry.py          # Provider lookup
│   └── tools/
│       ├── file_tools.py        # read_file, write_file (diff), list_directory
│       ├── shell_tools.py       # run_command (blocklist, confirm, configurable timeout)
│       ├── web_tools.py         # web_search, fetch_url
│       ├── git_tools.py         # git_status, git_diff, git_log
│       └── registry.py          # TOOL_DEFINITIONS, TOOL_FUNCTIONS, execute_tool
└── pyproject.toml
```

## How it works

1. **Startup** — `main.py` callback runs before every command: sets up logging, loads plugins, extends tool registry.
2. **Streaming** — `HttpProvider.chat_stream` sends `stream: true`, yields text tokens, accumulates tool-call chunks, executes tools, then yields the follow-up stream. Rendered live as Markdown via Rich `Live`.
3. **Tool calling** — when the LLM returns `tool_calls`, the provider executes each locally, appends results to the message list, and re-queries until it returns plain text.
4. **Diff preview** — `write_file` computes `difflib.unified_diff`, displays it colour-coded, and requires `y` before writing.
5. **Planning** — `create_plan` parses a JSON step list from the LLM. `execute_plan` runs each step with tools and tracks status.
6. **Reflection loop** — `nice fix` wraps a command in a retry loop; on failure the LLM patches the file with tools, then retries.
7. **Memory** — `ConversationHistory` serialises to `~/.nice/<name>.json` after every turn. Auto-compresses when >40 k chars.
8. **Context** — `inject_context` reads `.nice.md` and appends it to the system prompt before every request.
9. **Security** — `run_command` checks against a hardcoded blocklist plus user-configured patterns. Optional confirm prompt.
10. **Plugins** — `load_plugins` imports `*.py` from `~/.nice/plugins/`, merges `TOOL_DEFINITIONS`, `TOOL_FUNCTIONS`, and `COMMANDS` into the live registry.

## License

MIT
