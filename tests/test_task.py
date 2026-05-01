from datetime import datetime

import pytest
from pydantic import ValidationError

from doing.constants import TaskStatus
from doing.task import Task


class TestTaskConstruction:
    def test_defaults(self) -> None:
        task = Task(id=1, title="hello")
        assert task.id == 1
        assert task.title == "hello"
        assert task.status == TaskStatus.TODO
        assert task.labels == []
        assert task.body == ""
        assert isinstance(task.added_at, datetime)

    def test_all_fields(self, sample_task: Task) -> None:
        assert sample_task.id == 1
        assert sample_task.title == "sample task"
        assert sample_task.status == TaskStatus.TODO
        assert sample_task.labels == ["p2", "enhancement"]
        assert sample_task.body == "a multi-line\nbody for testing"

    def test_id_must_be_int(self) -> None:
        with pytest.raises(ValidationError):
            Task(id="one", title="bad")  # type: ignore[arg-type]

    def test_title_must_be_str(self) -> None:
        with pytest.raises(ValidationError):
            Task(id=1, title=None)  # type: ignore[arg-type]

    def test_invalid_status_rejected(self) -> None:
        with pytest.raises(ValidationError):
            Task(id=1, title="x", status="bogus")  # type: ignore[arg-type]


class TestTaskIcon:
    def test_todo_icon(self) -> None:
        task = Task(id=1, title="x", status=TaskStatus.TODO)
        assert task.icon == "\u23f3"

    def test_in_progress_icon(self) -> None:
        task = Task(id=1, title="x", status=TaskStatus.IN_PROGRESS)
        assert task.icon == "\U0001f3c3"

    def test_done_icon(self) -> None:
        task = Task(id=1, title="x", status=TaskStatus.DONE)
        assert task.icon == "\u2705"

    def test_cancelled_icon(self) -> None:
        task = Task(id=1, title="x", status=TaskStatus.CANCELLED)
        assert task.icon == "\u274c"


class TestTaskLabelsStr:
    def test_empty_labels(self) -> None:
        task = Task(id=1, title="x")
        assert task.labels_str == ""

    def test_single_label(self) -> None:
        task = Task(id=1, title="x", labels=["urgent"])
        assert task.labels_str == "urgent"

    def test_multiple_labels(self) -> None:
        task = Task(id=1, title="x", labels=["a", "b", "c"])
        assert task.labels_str == "a,b,c"


class TestTaskFormatList:
    def test_no_labels(self) -> None:
        task = Task(id=5, title="write docs", status=TaskStatus.TODO)
        assert task.format_list() == "(#5) [] {\u23f3} write docs"

    def test_with_labels(self) -> None:
        task = Task(id=5, title="fix bug", status=TaskStatus.IN_PROGRESS, labels=["urgent", "p0"])
        assert task.format_list() == "(#5) [urgent,p0] {\U0001f3c3} fix bug"

    def test_done_task(self) -> None:
        task = Task(id=1, title="deploy", status=TaskStatus.DONE)
        assert task.format_list() == "(#1) [] {\u2705} deploy"

    def test_cancelled_task(self) -> None:
        task = Task(id=1, title="old idea", status=TaskStatus.CANCELLED)
        assert task.format_list() == "(#1) [] {\u274c} old idea"


class TestTaskFormatSee:
    def test_without_body(self, sample_task: Task) -> None:
        sample_task.body = ""
        out = sample_task.format_see()
        assert out.startswith("---\n")
        assert out.endswith("---\n")
        assert "id: 1" in out
        assert "title: sample task" in out
        assert "status: todo" in out
        assert "labels:" in out
        assert "\n\n" not in out  # no spare body block

    def test_with_body(self, sample_task: Task) -> None:
        out = sample_task.format_see()
        assert out.startswith("---\n")
        assert out.endswith("\n")
        assert "---\n\na multi-line\nbody for testing\n" in out

    def test_contains_iso_datetime(self, sample_task: Task) -> None:
        out = sample_task.format_see()
        assert sample_task.added_at.isoformat() in out
