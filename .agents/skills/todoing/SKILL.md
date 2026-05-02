---
name: todoing
description: Use the `todoing` CLI for local task management. Track, list, search, and update tasks stored as markdown files in `.todoing/tasks/`. Use this whenever the user asks to manage work items, track tasks, list to-dos, or mentions "todoing" in the context of task tracking.
---

# todoing

`todoing` is a local CLI task manager. Tasks live as markdown files in
`.todoing/tasks/{id}.md`, indexed by `.todoing/index.json`. Everything is
git-trackable flat files — no databases, no servers.

Always run `todoing` from the repo root so `.todoing/` is discovered correctly.
The directory is auto-created on first use.

## Statuses

| Key           | Icon | Meaning          |
|---------------|------|------------------|
| `todo`        | ⏳   | Not yet started  |
| `in_progress` | 🏃   | Being worked on  |
| `done`        | ✅   | Completed        |
| `cancelled`   | ❌   | No longer needed |

IDs are sequential integers. `#1` and `1` are equivalent.

## Commands

### `todoing add "title"`

Create a task. Auto-assigns the next ID. Prints the ID.

```
todoing add "set up CI pipeline"
# (#3) set up CI pipeline
```

Options:
- `-l, --label <label>` — attach a label (repeatable, e.g. `-l p0 -l bug`)
- `-s, --status <status>` — initial status (default `todo`)
- `-b, --body "text"` — initial description body

### `todoing ls`

List tasks, newest first.

```
todoing ls
# (#3) [p0,infra] {🏃} set up CI pipeline
# (#2) [p3] {🏃} review onboarding docs
# (#1) [p2,p0] {🏃} initiate projects
```

Options:
- `-n, --limit <N>` — show only N newest tasks (default 0 = all)
- `-s, --status <status>` — filter by status
- `-l, --label <label>` — filter by label (repeatable, AND logic)
- `--scan` — bypass index, scan `.md` files directly

### `todoing see <id>`

Print the raw markdown for a task.

```
todoing see 3
---
id: 3
title: set up CI pipeline
---
```

### `todoing body <id> "text"`

Replace the entire description body (below the frontmatter).

### `todoing append <id> "text"`

Append text to the description body. Adds a blank-line separator if the body
is non-empty.

### `todoing status <id> <status>`

Change task status. Accepts: `todo`, `in_progress`, `done`, `cancelled`.

```
todoing status 1 done
```

### `todoing label <id> <ops...>`

Modify labels. Prefix with `+` to add, `-` to remove. Use `--` separator
before any removal that starts with `-`.

Options:
- `--clear` — clear all existing labels before applying operations

```
todoing label 1 +p0          # add p0
todoing label 1 -- -p2       # remove p2 (note the --)
todoing label 1 +bug --clear # clear all labels, then add bug
```

### `todoing search "query"`

Case-insensitive search across title, labels, status, and body.

```
todoing search CI
# (#3) [p0,infra] {🏃} set up CI pipeline
```

### `todoing delete <id>`

Delete a task. Prompts for confirmation unless `--force` / `-f`.

```
todoing delete 4 -f
```

### `todoing version`

Show the installed todoing version.

```
todoing version
# 1.0.5
```

### `todoing reindex`

Rebuild `index.json` from all `.md` files. Recovery command; not needed
during normal use.

## Common workflows for AI agents

These are copy-paste ready. Run them to drive work naturally.

### Start working on a task

```bash
todoing append 3 "Starting work: investigating the issue."
todoing status 3 in_progress
```

### Log progress during a task

```bash
todoing append 3 "Fixed the race condition in the connection pool."
```

### Complete a task

```bash
todoing append 3 "Done. Final state: all 42 tests pass."
todoing status 3 done
```

### Check what needs attention

```bash
todoing ls -s todo -n 10   # next 10 unfinished tasks
todoing ls -s in_progress   # what's currently being worked on
todoing ls -l p0            # high-priority items
```

### Create a task and assign it to yourself

```bash
todoing add "Refactor auth module" -l enhancement -s in_progress -b "Current approach is brittle."
```

### Search for something before duplicating work

```bash
todoing search "auth"
```

## AI agent usage

- **Never read `.todoing/` files directly.** Always use the CLI (`todoing see`,
  `todoing ls`, etc.). The index is the source of truth. Only read `.md` files
  directly when something is clearly broken (e.g., `todoing` errors out).
- **No `$EDITOR`**: you can't run `todoing edit <id>`. Use `body`/`append` to
  modify descriptions, `status`/`label` for metadata.
- **Always use `-f` / `--force`** with `delete` to skip interactive prompts.
- `todoing see <id>` outputs the raw file.
- `todoing ls -n 5` is a fast way to get recent context before working.
- Filter by status to find relevant tasks:
  `todoing ls -s in_progress` → active tasks
  `todoing ls -s todo` → pending tasks
- When you start working on something, run `todoing status <id> in_progress`.
  When done, run `todoing status <id> done` immediately — never leave a task
  in `in_progress` after completing it.
- The task body is full markdown (not plaintext). Use it for plans, research
  notes, links, logs, or anything else. A task's body is the canonical place
  to document context and progress so other agents can pick up where you left
  off.
- Right after finishing any task, always update its status to `done`. This is
  the single most important habit: completed work without a status update is
  invisible to `todoing ls` and other agents.
- The index is JSON. If `todoing` behaves oddly, run `todoing reindex` to rebuild.

## Self-dogfooding

**todoing** tracks its own development. Every task in `.todoing/tasks/` is a
feature, bug, or idea for todoing itself. When working on this repo, use
`todoing ls -n 5` to see what's next before starting.
