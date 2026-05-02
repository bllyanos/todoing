# AGENTS.md

## Setup

```bash
uv sync
source .venv/bin/activate
```

## Test (use `uv run` instead of `python -m pytest`)

```bash
uv run pytest             # all tests
uv run pytest tests/test_store.py::TestNextId  # single class
uv run pytest tests/test_store.py::TestNextId::test_empty_tasks_dir_returns_1  # single test
```

## Conventions

- **Commit messages**: conventional commits (`feat:`, `fix:`, `chore:`, etc.)
- **Never push to remote** — only commit locally
- No pre-commit hooks or CI configured yet
- No linter or typechecker configured yet

## Architecture

- `todoing` CLI entry: `src/todoing/main.py` — typer app
- `Store` in `src/todoing/task.py` handles all file I/O (`.todoing/tasks/*.md` + `.todoing/index.json`)
- `Task` is a Pydantic model; frontmatter is YAML, body is markdown below `---`
- `todoing` is self-dogfooding: this project's own tasks live in `.todoing/tasks/`
- IDs are sequential integers; `#1` and `1` are equivalent
- Missing or corrupt index auto-rebuilds on next read; `todoing reindex` for manual recovery

## AI agent usage of `todoing`

- Don't use `todoing edit` — it opens `$EDITOR`; use `body`/`append` instead
- Always use `--force` with `todoing delete` to skip interactive prompts
- Update status when starting/stopping work: `todoing status <id> in_progress` / `done`
- `todoing ls -n 5` for quick context before working
- See also `.agents/skills/todoing/SKILL.md` for full CLI reference
