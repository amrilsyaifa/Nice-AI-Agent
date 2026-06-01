# nice

Your autonomous CLI AI engineer. Ask questions, run interactive chats, execute coding tasks with file/shell tools, plan and execute multi-step goals, and auto-fix broken commands — all from the terminal.

## Features

- **Streaming output** — responses render token-by-token with full Markdown formatting
- **`ask`** — one-shot question to the AI
- **`chat`** — persistent interactive chat with conversation memory
- **`code`** — AI coding agent with read/write/shell tools and persistent session history
- **`plan`** — break a goal into steps, review/revise the plan, then execute it
- **`fix`** — run a command with automatic error-reflection and retry loop
- **`config`** — manage provider, model, and API settings
- **Context file** — place a `.nice.md` in any project directory for automatic project context
- **Diff preview** — shows a diff and asks for confirmation before the AI writes any file

## Requirements

- Python >= 3.13
- [uv](https://github.com/astral-sh/uv)
- An API key for [OpenRouter](https://openrouter.ai) or any OpenAI-compatible endpoint

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
uv run nice ask "What is recursion?"
```

Or activate the virtualenv:

```bash
source .venv/bin/activate
nice ask "What is recursion?"
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

All config is stored at `~/.nice/config.json`. Set values with:

```bash
nice config set api_key  YOUR_API_KEY
nice config set base_url https://openrouter.ai/api/v1
nice config set model    openai/gpt-4o
nice config set provider openai
```

| Key        | Default                              |
|------------|--------------------------------------|
| `provider` | `openai`                             |
| `model`    | `liquid/lfm-2.5-1.2b-thinking:free`  |
| `api_key`  | *(required)*                         |
| `base_url` | `https://openrouter.ai/api/v1`       |

View current config:

```bash
nice config list
nice config get model
```

## Usage

### Ask a single question

```bash
nice ask "What is a race condition?"
```

### Interactive chat (with persistent memory)

```bash
nice chat
```

Conversation history is saved to `~/.nice/history.json` and resumed on the next run.

| Command | Action |
|---------|--------|
| `exit`  | End the session |
| `clear` | Wipe conversation history |

### Coding agent

One-shot:

```bash
nice code "Create a Python script that fetches weather data from an API"
```

Interactive mode (session history persists across runs):

```bash
nice code
```

```
You: create a file hello.py that prints Hello World
AI: ...
You: add a name argument to the script
AI: ...
```

| Command        | Action |
|----------------|--------|
| `exit`         | End the session |
| `clear`        | Wipe code session history |
| `nice code --clear` | Clear history without entering the session |

The agent can use these tools:

| Tool             | Description                      |
|------------------|----------------------------------|
| `read_file`      | Read a file from disk            |
| `write_file`     | Write or create a file (shows diff preview first) |
| `list_directory` | List the contents of a directory |
| `run_command`    | Execute a shell command          |

### Planning agent

```bash
nice plan "Build a REST API with Flask"
```

Or omit the goal to be prompted:

```bash
nice plan
```

Nice creates a step-by-step execution plan, then enters a feedback loop:

```
  [a] Approve    [r] Revise    [c] Cancel
Choice: r
Feedback: use FastAPI instead of Flask
```

After approval, each step is executed automatically using the coding tools. Pass `--execute` / `-e` to skip the review loop.

### Auto-fix a failing command

```bash
nice fix "python main.py"
nice fix "pytest tests/" --file src/main.py
```

`fix` runs the command, detects errors, asks the AI to patch the file, then retries — up to 3 times automatically. Pass `--file` to give the AI the relevant file as extra context.

### Version

```bash
nice version
```

## Context file

Create a `.nice.md` in your project root to give Nice automatic context about the project:

```markdown
## Stack
- React 18 + Vite + TypeScript
- Tailwind CSS v4

## Conventions
- Components in `src/components/`, one file per component
- Use named exports only
- All API calls go through `src/lib/api.ts`
```

Nice reads `.nice.md` automatically when you run `code`, `chat`, `plan`, or `fix` from that directory. No flags needed.

## Diff preview

Before the AI writes any file, Nice shows a diff and asks for confirmation:

```
Diff preview: src/App.tsx
--- src/App.tsx  (current)
+++ src/App.tsx  (proposed)
@@ -1,4 +1,5 @@
 import React from 'react'
-function App() {
+function App({ name }: { name: string }) {
+  const title = `Hello, ${name}`
Apply? [y/n]:
```

New files show a preview of the first 20 lines before creation.

## Project structure

```
nice/
├── nice/
│   ├── main.py              # CLI entry point
│   ├── cli/
│   │   ├── _spinner.py      # Spinner + stream_markdown helper
│   │   ├── ask.py           # nice ask
│   │   ├── chat.py          # nice chat
│   │   ├── code.py          # nice code
│   │   ├── fix.py           # nice fix
│   │   ├── plan.py          # nice plan
│   │   ├── config_cmd.py    # nice config
│   │   └── version.py       # nice version
│   ├── config/
│   │   ├── settings.py      # Load/save ~/.nice/config.json
│   │   └── context.py       # .nice.md project context loader
│   ├── core/
│   │   └── reflection.py    # Error-reflection retry loop
│   ├── memory/
│   │   └── history.py       # Persistent conversation history
│   ├── planner/
│   │   ├── plan.py          # ExecutionPlan + Step data classes
│   │   ├── planner.py       # LLM-driven plan creation
│   │   └── executor.py      # Step-by-step plan execution
│   ├── providers/
│   │   ├── base.py          # BaseProvider abstract class
│   │   ├── http_provider.py # OpenAI-compatible HTTP provider (streaming)
│   │   └── registry.py      # Provider lookup
│   └── tools/
│       ├── file_tools.py    # read_file, write_file (diff preview), list_directory
│       ├── shell_tools.py   # run_command
│       └── registry.py      # Tool definitions + executor
└── pyproject.toml
```

## How it works

1. **Streaming** — `HttpProvider.chat_stream` calls any OpenAI-compatible endpoint with `stream: true`, yields text tokens, accumulates tool call chunks, executes tools, then streams the follow-up response. Rendered live as Markdown via Rich.
2. **Tool calling** — when the LLM returns `tool_calls`, the provider executes each tool locally, appends results into the message list, and re-queries until it returns plain text.
3. **Diff preview** — `write_file` computes a `difflib.unified_diff` against the current file, displays it with colour, and requires explicit `y` confirmation before writing.
4. **Planning** — `create_plan` sends the goal to the LLM and parses a JSON step list. `execute_plan` runs each step with tools, tracking status (pending / running / done / failed).
5. **Reflection loop** — `nice fix` wraps a command in a retry loop; on failure it hands the error + optional file context to the LLM which patches the file, then retries.
6. **Memory** — `ConversationHistory` serialises the message list to `~/.nice/<name>.json` after every turn. `chat` uses `history.json`, `code` interactive mode uses `code_history.json`.
7. **Context** — `inject_context` reads `.nice.md` from the current directory and appends it to the system prompt before every request.

## License

MIT
