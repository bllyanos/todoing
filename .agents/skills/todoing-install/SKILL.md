---
name: todoing-install
description: Guide users through installing and setting up `todoing` — the local, git-friendly CLI task manager. Use this when the user asks to install todoing, set up todoing, configure todoing for their project, or wants to start using todoing for task management. Also use this when onboarding AI agents to use todoing — including adding agent instructions to project config files like AGENTS.md or CLAUDE.md.
---

# todoing-install

A guide for installing `todoing` and integrating it into a project so that
AI agents can use it for task tracking.

## Requirements

- Python 3.11+
- `pip`, `pipx`, or `uv` (any Python package manager works)

## Install `uv` (one-time, if not installed)

If you don't have `uv` yet, install it first:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Or via pip: `pip install uv`. Verify with `uv --version`.

## Install methods

### Recommended: `uv tool install todoing`

```bash
uv tool install todoing
```

Pros: isolated environment, fast, works without activating a venv.

### Via pipx

```bash
pipx install todoing
pipx ensurepath              # add pipx-managed tools to PATH
```

Pros: isolated environment, widely available. Requires `pipx`.

### Via pip

```bash
pip install todoing
```

Pros: no extra tools. Cons: pollutes the global Python environment; use a
virtualenv if possible.

## Verify installation

```bash
todoing --help
todoing version
```

You should see usage info and the version number.

## Troubleshooting

| Symptom | Likely fix |
|---------|-----------|
| `todoing: command not found` | The install directory isn't on `PATH`. For `uv tool install` / `pipx`: add `~/.local/bin/` to `PATH` (`export PATH="$HOME/.local/bin:$PATH"` in shell rc), or run `pipx ensurepath`. |
| `Permission denied` | Don't `sudo pip install`. Use `uv tool install` or `pipx` instead — they respect user isolation. |
| `No module named yaml` | Corrupted install. Reinstall: `uv tool install todoing --reinstall` or `pipx reinstall todoing`. |
| `Error: No such command` | You have an old version. Upgrade: `uv tool upgrade todoing` or `pipx upgrade todoing` or `pip install --upgrade todoing`. |

## Setting up the agent skill

For AI agents (opencode, Claude Code) to use `todoing`, they need the skill
installed. The skill lives at `.agents/skills/todoing/SKILL.md`.

### Install the skill

If you're inside the repo that contains `.agents/skills/todoing/`, the skill
is already available — the agent can load it with `skill todoing`.

For other repos, copy the skill directory:

```bash
cp -r /path/to/todoing/.agents/skills/todoing /your/repo/.agents/skills/
```

Or reference it in the agent's config (e.g. opencode's `AGENTS.md`).

## Adding todoing instructions to the project

When onboarding a project to use `todoing`, ask the user:

> "Do you want me to add todoing instructions to your project's `AGENTS.md`
> (or `CLAUDE.md`) so that AI agents automatically know to use `todoing` for
> task management?"

If they say yes, add a section like this to the project's config file:

```markdown
## Task management with todoing

This project uses [todoing](https://github.com/bllyanos/todoing) for task
tracking. Tasks live in `.todoing/tasks/`. Always use the `todoing` CLI — never
read `.todoing/` files directly unless something is broken.

Quick reference:
- `todoing ls -n 5` — see recent tasks
- `todoing status <id> in_progress` — start work on a task
- `todoing status <id> done` — mark complete
- `todoing add "title" -l label` — create a task
- `todoing append <id> "progress note"` — log progress
```

This config should be placed in the project root as `AGENTS.md` (for opencode)
or `CLAUDE.md` (for Claude Code), whichever the user prefers or already has.
