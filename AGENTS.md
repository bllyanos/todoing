# AGENTS.md

## Setup

```bash
uv sync
source .venv/bin/activate
```

## Test

```bash
python -m pytest        # all 108 tests
python -m pytest tests/test_store.py::TestNextId  # single class
python -m pytest tests/test_store.py::TestNextId::test_empty_tasks_dir_returns_1  # single test
```

## Conventions

- **Commit messages**: conventional commits (`feat:`, `fix:`, `chore:`, etc.)
- No pre-commit hooks or CI configured yet
- No linter or typechecker configured yet

## Architecture

- `doing` CLI entry: `src/doing/main.py` — typer app
- `Store` in `src/doing/task.py` handles all file I/O (`.doing/tasks/*.md` + `.doing/index.json`)
- `Task` is a Pydantic model; frontmatter is YAML, body is markdown below `---`
- `doing` is self-dogfooding: this project's own tasks live in `.doing/tasks/`
- IDs are sequential integers; `#1` and `1` are equivalent
- Missing or corrupt index auto-rebuilds on next read; `doing reindex` for manual recovery

## AI agent usage of `doing`

- Don't use `doing edit` — it opens `$EDITOR`; use `body`/`append` instead
- Always use `--force` with `doing delete` to skip interactive prompts
- Update status when starting/stopping work: `doing status <id> in_progress` / `done`
- `doing ls -n 5` for quick context before working
- See also `.agents/skills/doing/SKILL.md` for full CLI reference
