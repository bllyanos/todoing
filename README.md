<p align="center">
  <h1 align="center">doing</h1>
  <p align="center">
    Tasks that live in your repo. No servers. No databases. Just git.
  </p>
</p>

<p align="center">
  <a href="https://pypi.org/project/doing"><img src="https://img.shields.io/pypi/v/doing?color=blue" alt="PyPI"></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-%3E%3D3.11-blue" alt="Python"></a>
  <a href="https://github.com/anomalyco/doing/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-green" alt="License"></a>
  <a href="https://github.com/anomalyco/doing/actions"><img src="https://img.shields.io/badge/tests-108%20passed-brightgreen" alt="Tests"></a>
</p>

---

**doing** is a local, file-based task manager built for the AI era. It stores every task as a markdown file with YAML frontmatter — fully git-trackable, editor-friendly, and agent-native. No API keys, no cloud, no lock-in.

If your ideas, plans, and to-dos should live next to your code, **doing** is for you.

## Why doing?

| | doing | GitHub Issues | Linear | Notion | Todoist |
|---|---|---|---|---|---|
| Stored in-repo | ✅ | ❌ | ❌ | ❌ | ❌ |
| Git-trackable | ✅ | ❌ | ❌ | ❌ | ❌ |
| Offline-first | ✅ | ❌ | ❌ | ❌ | ❌ |
| AI-agent-friendly CLI | ✅ | ❌ | ❌ | ❌ | ❌ |
| Zero setup | ✅ | ❌ | ❌ | ❌ | ❌ |
| Markdown native | ✅ | ❌ | ❌ | ❌ | ❌ |

## Install

```bash
uv tool install doing     # recommended: isolated environment
pipx install doing        # or via pipx
pip install doing         # or classic pip
```

Requires Python 3.11+.

## Quickstart

```bash
doing add "Ship the MVP"
doing add "Write integration tests" -l testing -s in_progress
doing ls

# (#2) [testing] {🏃} Write integration tests
# (#1) [] {⏳} Ship the MVP
```

That's it. A `.doing/` directory is created in your repo root. Add it to git. You're done.

## How it works

Each task is a **markdown file** in `.doing/tasks/`. A **JSON index** makes listing and searching instantaneous. Everything is plain text — your editor, `grep`, and `git diff` all work natively.

```
.doing/
  tasks/
    1.md    # markdown with YAML frontmatter
    2.md
    ...
  index.json    # auto-rebuilt, never committed alone
```

```markdown
---
id: 1
title: Ship the MVP
added_at: 2026-05-01T10:00:00
status: in_progress
labels: [p0, feature]
---

Long-form description here. Supports
multi-paragraph markdown body.
```

## Commands

### `add` — Create a task

```bash
doing add "Refactor auth module" -l p1 -l backend -s todo -b "Current approach is brittle."
# (#4) Refactor auth module
```

### `ls` — List tasks

```bash
doing ls                  # all tasks, newest first
doing ls -n 5             # latest 5
doing ls -s in_progress   # filter by status
doing ls -l p0 -l backend # filter by labels (AND)
```

### `see` — View a task

```bash
doing see 4               # raw markdown to stdout
doing see "#4"            # # prefix is optional
```

### `status` — Change status

```bash
doing status 4 in_progress
doing status 4 done
```

Statuses: `todo` ⏳ , `in_progress` 🏃 , `done` ✅ , `cancelled` ❌

### `label` — Add or remove labels

```bash
doing label 4 +p0               # add p0
doing label 4 -- -backend       # remove backend (-- separator needed)
doing label 4 +bug --clear      # clear all, then add bug
```

### `body` / `append` — Edit descriptions

```bash
doing body 4 "Full rewrite of the auth flow."     # replace body
doing append 4 "Also update token refresh logic."  # append to body
```

### `search` — Full-text search

```bash
doing search "auth"
# (#4) [p0] {🏃} Refactor auth module
```

### `delete` — Remove a task

```bash
doing delete 4 --force       # skip confirmation
```

### `edit` — Open in `$EDITOR`

```bash
doing edit 4                 # humans only; AI agents use body/append
```

### `reindex` — Rebuild the index

```bash
doing reindex                # recovery command; rarely needed
```

## Built for AI agents

**doing** is designed for AI coding agents to drive via CLI. Commands are single-shot, output is parseable, and the `$EDITOR`-based `edit` command has scriptable alternatives (`body`, `append`, `status`, `label`).

```bash
doing ls -n 5                     # agent checks current work
doing status 3 in_progress        # agent starts a task
doing append 3 "Fixed in a1b2c3d" # agent records progress
doing status 3 done               # agent completes task
```

No prompts, no TUI, no friction.

## Self-dogfooding

**doing** tracks its own development. Every feature, fix, and idea for **doing** itself is a task inside `.doing/tasks/`. The tool builds the tool.

## Development

```bash
git clone https://github.com/anomalyco/doing
cd doing
uv sync
source .venv/bin/activate
python -m pytest
```

## License

MIT © Anomaly Collective
