import json
from datetime import datetime
from pathlib import Path

import yaml
from pydantic import BaseModel, Field

from .constants import TODOING_DIR, INDEX_FILE, STATUS_ICONS, TASKS_DIR, TaskStatus


class Task(BaseModel):
    id: int
    title: str
    added_at: datetime = Field(default_factory=datetime.now)
    status: TaskStatus = TaskStatus.TODO
    labels: list[str] = Field(default_factory=list)
    body: str = ""

    @property
    def icon(self) -> str:
        return STATUS_ICONS[self.status]

    @property
    def labels_str(self) -> str:
        return ",".join(self.labels)

    def format_list(self) -> str:
        labels = f"[{','.join(self.labels)}]" if self.labels else "[]"
        return f"(#{self.id}) {labels} {{{self.icon}}} {self.title}"

    def format_see(self) -> str:
        frontmatter = {
            "id": self.id,
            "title": self.title,
            "added_at": self.added_at.isoformat(),
            "status": self.status.value,
            "labels": self.labels,
        }
        yaml_str = yaml.dump(frontmatter, allow_unicode=True, default_flow_style=None).strip()
        body = self.body.strip()
        if body:
            return f"---\n{yaml_str}\n---\n\n{body}\n"
        return f"---\n{yaml_str}\n---\n"


class Store:
    def __init__(self, root: Path | None = None):
        self._root = Path(root) if root else Path.cwd()
        self._todoing = self._root / TODOING_DIR
        self._tasks = self._todoing / TASKS_DIR
        self._index_path = self._todoing / INDEX_FILE

    # ---- ensure ----

    def ensure(self) -> None:
        self._todoing.mkdir(parents=True, exist_ok=True)
        self._tasks.mkdir(parents=True, exist_ok=True)

    # ---- IDs ----

    def next_id(self) -> int:
        if not self._tasks.exists():
            return 1
        ids = [
            int(p.stem) for p in self._tasks.glob("*.md") if p.stem.isdigit()
        ]
        return max(ids, default=0) + 1

    @staticmethod
    def resolve_id(raw: str) -> int:
        raw = raw.strip().lstrip("#")
        if not raw.isdigit():
            raise ValueError(f"Invalid task ID: {raw}")
        return int(raw)

    # ---- task file read/write ----

    def read_task(self, id: int) -> Task | None:
        path = self._tasks / f"{id}.md"
        if not path.exists():
            return None
        return self._parse_task_file(path)

    def write_task(self, task: Task) -> None:
        self.ensure()
        path = self._tasks / f"{task.id}.md"
        path.write_text(task.format_see())

    def delete_task_file(self, id: int) -> bool:
        path = self._tasks / f"{id}.md"
        if not path.exists():
            return False
        path.unlink()
        return True

    # ---- index read/write ----

    def read_index(self) -> list[Task]:
        if not self._index_path.exists():
            return self.rebuild_index()
        try:
            data = json.loads(self._index_path.read_text())
            return [Task(**item) for item in data]
        except (json.JSONDecodeError, KeyError, TypeError):
            return self.rebuild_index()

    def write_index(self, tasks: list[Task]) -> None:
        self.ensure()
        raw = json.dumps(
            [t.model_dump(mode="json") for t in tasks],
            ensure_ascii=False,
            indent=2,
        )
        self._index_path.write_text(raw + "\n")

    def rebuild_index(self) -> list[Task]:
        tasks = []
        for p in sorted(self._tasks.glob("*.md"), key=lambda p: int(p.stem) if p.stem.isdigit() else 0):
            task = self._parse_task_file(p)
            if task:
                tasks.append(task)
        self.write_index(tasks)
        return tasks

    def sync_index_on_mutation(self, task: Task) -> None:
        idx = self.read_index()
        found = False
        for i, t in enumerate(idx):
            if t.id == task.id:
                idx[i] = task
                found = True
                break
        if not found:
            idx.append(task)
        self.write_index(idx)

    def sync_index_on_delete(self, id: int) -> None:
        idx = self.read_index()
        idx = [t for t in idx if t.id != id]
        self.write_index(idx)

    # ---- filter ----

    def filter(
        self,
        status: TaskStatus | None = None,
        labels: list[str] | None = None,
        limit: int = 0,
        q: str | None = None,
    ) -> list[Task]:
        tasks = self.read_index()
        if status:
            tasks = [t for t in tasks if t.status == status]
        if labels:
            labels_lower = {lbl.lower() for lbl in labels}
            tasks = [t for t in tasks if labels_lower <= {l.lower() for l in t.labels}]
        if q:
            ql = q.lower()
            tasks = [
                t for t in tasks
                if ql in t.title.lower()
                or ql in t.body.lower()
                or ql in " ".join(t.labels).lower()
                or ql == t.status.value
            ]
        tasks.sort(key=lambda t: t.id, reverse=True)
        if limit > 0:
            tasks = tasks[:limit]
        return tasks

    # ---- internal ----

    def _parse_task_file(self, path: Path) -> Task | None:
        try:
            text = path.read_text()
        except OSError:
            return None

        if not text.startswith("---"):
            import warnings
            warnings.warn(f"Task file {path} has no frontmatter, skipping")
            return None

        parts = text.split("---", 2)
        if len(parts) < 3:
            return None

        try:
            fm = yaml.safe_load(parts[1])
        except yaml.YAMLError:
            return None

        body = parts[2].strip()
        return Task(
            id=int(fm["id"]),
            title=fm["title"],
            added_at=fm.get("added_at", datetime.now()),
            status=TaskStatus(fm.get("status", "todo")),
            labels=fm.get("labels") or [],
            body=body,
        )
