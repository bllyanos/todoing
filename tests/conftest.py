from datetime import datetime
from pathlib import Path

import pytest

from todoing.constants import TaskStatus
from todoing.task import Store, Task


@pytest.fixture
def tmp_store(tmp_path: Path) -> Store:
    return Store(root=tmp_path)


@pytest.fixture
def store_with_tasks(tmp_store: Store) -> Store:
    tasks = [
        Task(
            id=1,
            title="first task",
            added_at=datetime(2026, 5, 1, 10, 0, 0),
            status=TaskStatus.TODO,
            labels=["p1", "bug"],
            body="details about first",
        ),
        Task(
            id=2,
            title="second task",
            added_at=datetime(2026, 5, 1, 11, 0, 0),
            status=TaskStatus.IN_PROGRESS,
            labels=["p2"],
            body="more text",
        ),
        Task(
            id=3,
            title="third task",
            added_at=datetime(2026, 5, 1, 12, 0, 0),
            status=TaskStatus.DONE,
            labels=["p1", "feature"],
            body="",
        ),
    ]
    for t in tasks:
        tmp_store.write_task(t)
    tmp_store.write_index(tasks)
    return tmp_store


@pytest.fixture
def sample_task() -> Task:
    return Task(
        id=1,
        title="sample task",
        added_at=datetime(2026, 5, 1, 10, 0, 0),
        status=TaskStatus.TODO,
        labels=["p2", "enhancement"],
        body="a multi-line\nbody for testing",
    )
