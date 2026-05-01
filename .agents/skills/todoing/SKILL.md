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
- `-n, --limit <N>` — show only N newest tasks
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

Delete a task. Prompts for confirmation unless `--force`.

```
todoing delete 4 --force
```

### `todoing reindex`

Rebuild `index.json` from all `.md` files. Recovery command; not needed
during normal use.

## AI agent usage

- **No `$EDITOR`**: you can't run `todoing edit <id>`. Use `body`/`append` to
  modify descriptions, `status`/`label` for metadata.
- **Always use `--force`** with `delete` to skip interactive prompts.
- `todoing see <id>` outputs the raw file — you can also read
  `.todoing/tasks/{id}.md` directly with file tools.
- `todoing ls -n 5` is a fast way to get recent context before working.
- When you start working on something, run `todoing status <id> in_progress`.
  When done, `todoing status <id> done`.
- The index is JSON. If `todoing` behaves oddly, run `todoing reindex` to rebuild.
