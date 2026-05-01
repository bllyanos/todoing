<p align="center">
  <h1 align="center">todoing</h1>
  <p align="center">
    Tasks that live in your repo. No servers. No databases. Just git.
  </p>
</p>

<p align="center">
  <a href="https://pypi.org/project/todoing"><img src="https://img.shields.io/pypi/v/todoing?color=blue" alt="PyPI"></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-%3E%3D3.11-blue" alt="Python"></a>
  <a href="https://github.com/anomalyco/todoing/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-green" alt="License"></a>
  <a href="https://github.com/anomalyco/todoing/actions"><img src="https://img.shields.io/badge/tests-108%20passed-brightgreen" alt="Tests"></a>
</p>

---

**todoing** is a local, file-based task manager built for the AI era. It stores every task as a markdown file with YAML frontmatter — fully git-trackable, editor-friendly, and agent-native. No API keys, no cloud, no lock-in.

If your ideas, plans, and to-dos should live next to your code, **todoing** is for you.

## Why todoing?

| | todoing | GitHub Issues | Linear | Notion | Todoist |
|---|---|---|---|---|---|
| Stored in-repo | ✅ | ❌ | ❌ | ❌ | ❌ |
| Git-trackable | ✅ | ❌ | ❌ | ❌ | ❌ |
| Offline-first | ✅ | ❌ | ❌ | ❌ | ❌ |
| AI-agent-friendly CLI | ✅ | ❌ | ❌ | ❌ | ❌ |
| Zero setup | ✅ | ❌ | ❌ | ❌ | ❌ |
| Markdown native | ✅ | ❌ | ❌ | ❌ | ❌ |

## Install

```bash
uv tool install todoing     # recommended: isolated environment
pipx install todoing        # or via pipx
pip install todoing         # or classic pip
```

Requires Python 3.11+.

## Quickstart

```bash
todoing add "Ship the MVP"
todoing add "Write integration tests" -l testing -s in_progress
todoing ls

# (#2) [testing] {🏃} Write integration tests
# (#1) [] {⏳} Ship the MVP
```

That's it. A `.todoing/` directory is created in your repo root. Add it to git. You're done.

## How it works

Each task is a **markdown file** in `.todoing/tasks/`. A **JSON index** makes listing and searching instantaneous. Everything is plain text — your editor, `grep`, and `git diff` all work natively.

```
.todoing/
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
todoing add "Refactor auth module" -l p1 -l backend -s todo -b "Current approach is brittle."
# (#4) Refactor auth module
```

### `ls` — List tasks

```bash
todoing ls                  # all tasks, newest first
todoing ls -n 5             # latest 5
todoing ls -s in_progress   # filter by status
todoing ls -l p0 -l backend # filter by labels (AND)
```

### `see` — View a task

```bash
todoing see 4               # raw markdown to stdout
todoing see "#4"            # # prefix is optional
```

### `status` — Change status

```bash
todoing status 4 in_progress
todoing status 4 done
```

Statuses: `todo` ⏳ , `in_progress` 🏃 , `done` ✅ , `cancelled` ❌

### `label` — Add or remove labels

```bash
todoing label 4 +p0               # add p0
todoing label 4 -- -backend       # remove backend (-- separator needed)
todoing label 4 +bug --clear      # clear all, then add bug
```

### `body` / `append` — Edit descriptions

```bash
todoing body 4 "Full rewrite of the auth flow."     # replace body
todoing append 4 "Also update token refresh logic."  # append to body
```

### `search` — Full-text search

```bash
todoing search "auth"
# (#4) [p0] {🏃} Refactor auth module
```

### `delete` — Remove a task

```bash
todoing delete 4 --force       # skip confirmation
```

### `edit` — Open in `$EDITOR`

```bash
todoing edit 4                 # humans only; AI agents use body/append
```

### `reindex` — Rebuild the index

```bash
todoing reindex                # recovery command; rarely needed
```

## Built for AI agents

**todoing** is designed for AI coding agents to drive via CLI. Commands are single-shot, output is parseable, and the `$EDITOR`-based `edit` command has scriptable alternatives (`body`, `append`, `status`, `label`).

```bash
todoing ls -n 5                     # agent checks current work
todoing status 3 in_progress        # agent starts a task
todoing append 3 "Fixed in a1b2c3d" # agent records progress
todoing status 3 done               # agent completes task
```

No prompts, no TUI, no friction.

## Self-dogfooding

**todoing** tracks its own development. Every feature, fix, and idea for **todoing** itself is a task inside `.todoing/tasks/`. The tool builds the tool.

## Development

```bash
git clone https://github.com/anomalyco/todoing
cd todoing
uv sync
source .venv/bin/activate
python -m pytest
```

## License

MIT © Anomaly Collective
