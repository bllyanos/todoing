from enum import StrEnum


class TaskStatus(StrEnum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CANCELLED = "cancelled"


STATUS_ICONS: dict[TaskStatus, str] = {
    TaskStatus.TODO: "\u23f3",          # ⏳
    TaskStatus.IN_PROGRESS: "\U0001f3c3",  # 🏃
    TaskStatus.DONE: "\u2705",          # ✅
    TaskStatus.CANCELLED: "\u274c",     # ❌
}

DOING_DIR = ".doing"
TASKS_DIR = "tasks"
INDEX_FILE = "index.json"
