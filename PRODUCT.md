# todoing — Task management CLI for AI agents and humans

## Purpose

A local, file-based task manager. Designed for AI agents to drive via CLI
but human-friendly too. Everything is git-trackable flat files — no databases,
no servers, no state outside the repo.

## Architecture

### Storage

```
.todoing/
  tasks/
    1.md         # one markdown file per task
    2.md
    ...
  index.json    # derived, rebuildable index for fast list/search
```

### Task file format

Markdown with YAML frontmatter — the `see` command output *is* the file:

```markdown
---
id: 1
title: initiate projects
added_at: 2026-04-23T20:00:00
status: in_progress
labels: [p2, enhancements]
---

Long description that can span
multiple paragraphs.
```

### Index

`index.json` is a JSON array of frontmatter objects, rebuilt on every mutation.
Reads (`list`, `search`) hit the index; `see` reads the `.md` file directly.

If the index is missing or corrupted, it's auto-rebuilt on the next command.
`todoing reindex` exists as a manual recovery tool.

## Status model

| Key          | Icon | Meaning              |
|-------------|------|----------------------|
| `todo`      | ⏳   | Not yet started      |
| `in_progress` | 🏃   | Being worked on      |
| `done`      | ✅   | Completed            |
| `cancelled` | ❌   | No longer needed     |

## Commands

### `todoing add "title"`
Create a new task. Auto-assigns ID (max existing + 1). Returns the ID and file path.
```
todoing add "set up CI for deploy"
# (#3) set up CI for deploy
```

Options:
- `-l, --label <label>` — attach labels (repeatable)
- `-s, --status <status>` — initial status (default: `todo`)
- `-b, --body "text"` — initial description body

### `todoing ls`
List tasks, newest first.
```
todoing ls
# (#1) [p2, enhancements] {🏃} initiate projects
# (#2) [] {⏳} review onboarding docs
```

Options:
- `-n, --limit <N>` — show only N newest tasks (0 = all)
- `-s, --status <status>` — filter by status
- `-l, --label <label>` — filter by label (repeatable, AND logic)
- `--scan` — bypass index, scan .md files directly

### `todoing see <id>`
Print the raw markdown file to stdout.
```
todoing see #1
---
id: 1
title: initiate projects
...
```

### `todoing edit <id>`
Open `$EDITOR` on the task file. Reindexes on exit.
For humans; AI agents should use `body`/`append`.

### `todoing body <id> "text"`
Replace the entire description body (below frontmatter).

### `todoing append <id> "text"`
Append text to the description body. Adds a blank line separator if the body
is non-empty.

### `todoing status <id> <status>`
Change task status. Accepts: `todo`, `in_progress`, `done`, `cancelled`.
```
todoing status 1 done
```

### `todoing label <id> +<label> -<label> ...`
Modify labels with add/remove semantics. Use `--` before ops that start with `-`:
```
todoing label 1 +p0 -- -p2    # add p0, remove p2
todoing label 1 +bug --clear   # clear all, then add bug
```
todoing label 1 +p0 -p2    # add p0, remove p2
todoing label 1 +bug --clear # clear all, then add bug
```
`+` adds, `-` removes, `--clear` wipes before applying operations.

### `todoing search "query"`
Case-insensitive grep across title, labels, status, and body of all tasks.
Shows matching IDs and titles.

### `todoing delete <id>`
Delete a task file. Confirms unless `--force`.

### `todoing reindex`
Rebuild `index.json` from all `.md` files. Recovery command; not needed
during normal use.

## ID format

IDs are sequential integers (`1`, `2`, `3`, …). Users reference them with
or without the `#` prefix: `#1` and `1` are equivalent.

## Dependencies

- Python >= 3.11
- `typer` — CLI framework
- `pyyaml` — frontmatter parsing

## Edge cases

- Empty task list → `list` prints "No tasks."
- Invalid ID → "Task #N not found."
- Invalid status → rejected with valid choices listed
- Corrupted frontmatter → skipped with warning, doesn't crash
- `.todoing/` doesn't exist → auto-created on first command
- Concurrent writes → last write wins (acceptable for single-user CLI)
