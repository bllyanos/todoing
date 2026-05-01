import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Annotated, List, Optional

import typer

from .constants import TaskStatus
from .task import Store, Task

app = typer.Typer(no_args_is_help=True)
store = Store()


# ---- helpers ----

def _error(msg: str) -> None:
    typer.echo(f"Error: {msg}", err=True)
    raise typer.Exit(1)


def _resolve_status(raw: str) -> TaskStatus:
    try:
        return TaskStatus(raw.lower())
    except ValueError:
        valid = ", ".join(s.value for s in TaskStatus)
        _error(f"Invalid status '{raw}'. Valid: {valid}")


# ---- add ----

@app.command()
def add(
    title: Annotated[str, typer.Argument(help="Task title")],
    labels: Annotated[List[str], typer.Option("-l", "--label", help="Attach a label (repeatable)")] = [],
    status: Annotated[str, typer.Option("-s", "--status", help="Initial status")] = "todo",
    body: Annotated[str, typer.Option("-b", "--body", help="Initial description body")] = "",
) -> None:
    """Create a new task."""
    idx = store.next_id()
    st = _resolve_status(status)
    task = Task(
        id=idx,
        title=title,
        added_at=datetime.now(),
        status=st,
        labels=list(dict.fromkeys(labels)),
        body=body,
    )
    store.write_task(task)
    store.sync_index_on_mutation(task)
    typer.echo(f"(#{task.id}) {task.title}")


# ---- list ----

@app.command(name="ls")
def ls(
    limit: Annotated[int, typer.Option("-n", "--limit", help="Show only N newest tasks (0 = all)")] = 0,
    status: Annotated[Optional[str], typer.Option("-s", "--status", help="Filter by status")] = None,
    labels: Annotated[List[str], typer.Option("-l", "--label", help="Filter by label (repeatable, AND logic)")] = [],
    scan: Annotated[bool, typer.Option("--scan", help="Bypass index, scan .md files directly")] = False,
) -> None:
    """List tasks, newest first."""
    if scan:
        tasks = store.rebuild_index()
    else:
        tasks = store.read_index()

    st = _resolve_status(status) if status else None
    if st:
        tasks = [t for t in tasks if t.status == st]
    if labels:
        labels_lower = {lbl.lower() for lbl in labels}
        tasks = [t for t in tasks if labels_lower <= {l.lower() for l in t.labels}]

    tasks.sort(key=lambda t: t.id, reverse=True)
    if limit > 0:
        tasks = tasks[:limit]

    if not tasks:
        typer.echo("No tasks.")
        return
    for t in tasks:
        typer.echo(t.format_list())


# ---- see ----

@app.command()
def see(
    id: Annotated[str, typer.Argument(help="Task ID, e.g. #1 or 1")],
) -> None:
    """Show a task as markdown with frontmatter."""
    nid = store.resolve_id(id)
    task = store.read_task(nid)
    if not task:
        _error(f"Task #{nid} not found.")
    typer.echo(task.format_see(), nl=False)


# ---- edit ----

@app.command()
def edit(
    id: Annotated[str, typer.Argument(help="Task ID to edit")],
) -> None:
    """Open the task file in $EDITOR."""
    nid = store.resolve_id(id)
    path = store._tasks / f"{nid}.md"
    if not path.exists():
        _error(f"Task #{nid} not found.")
    editor = os.environ.get("EDITOR", "vim")
    ret = subprocess.call([editor, str(path)])
    if ret != 0:
        _error(f"Editor exited with code {ret}")
    store.rebuild_index()


# ---- body ----

@app.command()
def body(
    id: Annotated[str, typer.Argument(help="Task ID")],
    text: Annotated[str, typer.Argument(help="New description body text")],
) -> None:
    """Replace the description body of a task."""
    nid = store.resolve_id(id)
    task = store.read_task(nid)
    if not task:
        _error(f"Task #{nid} not found.")
    task.body = text
    store.write_task(task)
    store.sync_index_on_mutation(task)
    typer.echo(f"(#{task.id}) body updated.")


# ---- append ----

@app.command()
def append(
    id: Annotated[str, typer.Argument(help="Task ID")],
    text: Annotated[str, typer.Argument(help="Text to append to the description body")],
) -> None:
    """Append text to the description body of a task."""
    nid = store.resolve_id(id)
    task = store.read_task(nid)
    if not task:
        _error(f"Task #{nid} not found.")
    if task.body:
        task.body += f"\n\n{text}"
    else:
        task.body = text
    store.write_task(task)
    store.sync_index_on_mutation(task)
    typer.echo(f"(#{task.id}) body appended.")


# ---- status ----

@app.command()
def status(
    id: Annotated[str, typer.Argument(help="Task ID")],
    new_status: Annotated[str, typer.Argument(help="New status: todo, in_progress, done, cancelled")],
) -> None:
    """Change a task's status."""
    nid = store.resolve_id(id)
    task = store.read_task(nid)
    if not task:
        _error(f"Task #{nid} not found.")
    st = _resolve_status(new_status)
    task.status = st
    store.write_task(task)
    store.sync_index_on_mutation(task)
    typer.echo(f"(#{task.id}) status -> {{{task.icon}}} {task.status.value}")


# ---- label ----

@app.command()
def label(
    id: Annotated[str, typer.Argument(help="Task ID")],
    ops: Annotated[List[str], typer.Argument(help="Label operations: +label to add, -label to remove")],
    clear: Annotated[bool, typer.Option("--clear/--no-clear", help="Clear all labels before applying operations")] = False,
) -> None:
    """Modify task labels with add/remove operations.

    \b
    Examples:
        doing label 1 +p0 -p2        add p0, remove p2
        doing label 1 +bug --clear   clear all, then add bug
    """
    nid = store.resolve_id(id)
    task = store.read_task(nid)
    if not task:
        _error(f"Task #{nid} not found.")

    current = [] if clear else list(task.labels)
    adds = []
    removes = set()

    for op in ops:
        if op.startswith("+"):
            adds.append(op[1:])
        elif op.startswith("-"):
            removes.add(op[1:])
        else:
            _error(f"Invalid label operation '{op}'. Use +label to add or -label to remove.")

    for r in removes:
        try:
            current.remove(r)
        except ValueError:
            pass
    current.extend(adds)
    task.labels = list(dict.fromkeys(current))
    store.write_task(task)
    store.sync_index_on_mutation(task)
    typer.echo(f"(#{task.id}) labels -> [{', '.join(task.labels)}]")


# ---- search ----

@app.command()
def search(
    query: Annotated[str, typer.Argument(help="Search query (case-insensitive)")],
) -> None:
    """Search tasks by title, labels, status, and body."""
    tasks = store.filter(q=query)
    if not tasks:
        typer.echo("No matches.")
        return
    for t in tasks:
        typer.echo(t.format_list())


# ---- delete ----

@app.command()
def delete(
    id: Annotated[str, typer.Argument(help="Task ID")],
    force: Annotated[bool, typer.Option("-f", "--force", help="Skip confirmation")] = False,
) -> None:
    """Delete a task."""
    nid = store.resolve_id(id)
    task = store.read_task(nid)
    if not task:
        _error(f"Task #{nid} not found.")
    if not force:
        confirm = typer.prompt(f"Delete (#{nid}) {task.title}? [y/N]").lower()
        if confirm not in ("y", "yes"):
            typer.echo("Aborted.")
            return
    store.delete_task_file(nid)
    store.sync_index_on_delete(nid)
    typer.echo(f"(#{nid}) deleted.")


# ---- reindex ----

@app.command()
def reindex() -> None:
    """Rebuild index.json from all task .md files."""
    tasks = store.rebuild_index()
    typer.echo(f"Index rebuilt: {len(tasks)} tasks.")
