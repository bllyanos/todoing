import json
from datetime import datetime

import pytest

from doing.constants import DOING_DIR, INDEX_FILE, TASKS_DIR, TaskStatus
from doing.task import Store, Task


# ---- ensure -----------------------------------------------------------

class TestEnsure:
    def test_creates_directories(self, tmp_store: Store) -> None:
        tmp_store.ensure()
        assert tmp_store._doing.exists()
        assert tmp_store._tasks.exists()

    def test_idempotent(self, tmp_store: Store) -> None:
        tmp_store.ensure()
        tmp_store.ensure()
        assert tmp_store._doing.is_dir()
        assert tmp_store._tasks.is_dir()


# ---- IDs --------------------------------------------------------------

class TestNextId:
    def test_empty_tasks_dir_returns_1(self, tmp_store: Store) -> None:
        tmp_store.ensure()
        assert tmp_store.next_id() == 1

    def test_no_tasks_dir_returns_1(self, tmp_store: Store) -> None:
        assert tmp_store.next_id() == 1

    def test_gap_does_not_cause_reuse(self, tmp_store: Store) -> None:
        tmp_store.ensure()
        tmp_store.write_task(Task(id=1, title="a"))
        tmp_store.write_task(Task(id=3, title="c"))
        assert tmp_store.next_id() == 4

    def test_sequential_increment(self, store_with_tasks: Store) -> None:
        assert store_with_tasks.next_id() == 4


class TestResolveId:
    def test_bare_number(self) -> None:
        assert Store.resolve_id("1") == 1

    def test_hash_prefix(self) -> None:
        assert Store.resolve_id("#1") == 1

    def test_whitespace(self) -> None:
        assert Store.resolve_id("  #42  ") == 42

    def test_invalid_raises(self) -> None:
        with pytest.raises(ValueError, match="Invalid task ID"):
            Store.resolve_id("abc")

    def test_empty_raises(self) -> None:
        with pytest.raises(ValueError, match="Invalid task ID"):
            Store.resolve_id("")


# ---- task file I/O ----------------------------------------------------

class TestWriteReadTask:
    def test_roundtrip(self, tmp_store: Store) -> None:
        task = Task(
            id=7,
            title="roundtrip test",
            added_at=datetime(2026, 5, 1, 10, 0, 0),
            status=TaskStatus.IN_PROGRESS,
            labels=["a", "b"],
            body="some body\nwith two lines",
        )
        tmp_store.write_task(task)
        result = tmp_store.read_task(7)
        assert result is not None
        assert result.id == task.id
        assert result.title == task.title
        assert result.status == task.status
        assert result.labels == task.labels
        assert result.body == task.body

    def test_read_missing_returns_none(self, tmp_store: Store) -> None:
        assert tmp_store.read_task(999) is None

    def test_no_frontmatter_returns_none(self, tmp_store: Store) -> None:
        tmp_store.ensure()
        path = tmp_store._tasks / "99.md"
        path.write_text("just some text, no frontmatter")
        assert tmp_store.read_task(99) is None

    def test_corrupted_yaml_returns_none(self, tmp_store: Store) -> None:
        tmp_store.ensure()
        path = tmp_store._tasks / "99.md"
        path.write_text("---\nkey: [unclosed\n---\nbody")
        assert tmp_store.read_task(99) is None

    def test_missing_file_returns_none(self, tmp_store: Store) -> None:
        tmp_store.ensure()
        # file never created
        assert tmp_store.read_task(1) is None


class TestDeleteTaskFile:
    def test_deletes_existing(self, store_with_tasks: Store) -> None:
        assert store_with_tasks.delete_task_file(1)
        assert store_with_tasks.read_task(1) is None

    def test_missing_returns_false(self, tmp_store: Store) -> None:
        assert not tmp_store.delete_task_file(999)


# ---- index ------------------------------------------------------------

class TestIndexReadWrite:
    def test_roundtrip(self, tmp_store: Store) -> None:
        tasks = [
            Task(id=1, title="a"),
            Task(id=2, title="b"),
        ]
        tmp_store.write_index(tasks)
        result = tmp_store.read_index()
        assert len(result) == 2
        assert {t.id for t in result} == {1, 2}

    def test_missing_index_triggers_rebuild(self, tmp_store: Store) -> None:
        tmp_store.ensure()
        # create a task file but no index
        task = Task(id=1, title="lonely")
        tmp_store.write_task(task)
        # index doesn't exist, read_index should rebuild from files
        assert not tmp_store._index_path.exists()
        result = tmp_store.read_index()
        assert len(result) == 1
        assert result[0].title == "lonely"
        assert tmp_store._index_path.exists()

    def test_corrupt_json_triggers_rebuild(self, tmp_store: Store) -> None:
        tmp_store.ensure()
        tmp_store._index_path.write_text("not valid json {{{")
        task = Task(id=1, title="recovered")
        tmp_store.write_task(task)
        result = tmp_store.read_index()
        assert len(result) == 1
        assert result[0].title == "recovered"


class TestRebuildIndex:
    def test_empty_tasks_dir(self, tmp_store: Store) -> None:
        tmp_store.ensure()
        tasks = tmp_store.rebuild_index()
        assert tasks == []
        assert tmp_store._index_path.exists()

    def test_rebuilds_from_files(self, store_with_tasks: Store) -> None:
        # delete the index, then rebuild
        store_with_tasks._index_path.unlink()
        tasks = store_with_tasks.rebuild_index()
        assert len(tasks) == 3
        ids = {t.id for t in tasks}
        assert ids == {1, 2, 3}

    def test_skips_corrupted_files(self, tmp_store: Store) -> None:
        tmp_store.ensure()
        task = Task(id=1, title="good")
        tmp_store.write_task(task)
        (tmp_store._tasks / "2.md").write_text("rubbish content with no ---")
        tasks = tmp_store.rebuild_index()
        assert len(tasks) == 1
        assert tasks[0].id == 1


class TestSyncIndexOnMutation:
    def test_appends_new_task(self, tmp_store: Store) -> None:
        task = Task(id=1, title="new")
        tmp_store.sync_index_on_mutation(task)
        idx = tmp_store.read_index()
        assert len(idx) == 1
        assert idx[0].title == "new"

    def test_updates_existing_task(self, store_with_tasks: Store) -> None:
        task = store_with_tasks.read_task(1)
        assert task is not None
        task.title = "updated first"
        store_with_tasks.sync_index_on_mutation(task)
        idx = store_with_tasks.read_index()
        assert len(idx) == 3  # count unchanged
        titles = {t.title for t in idx}
        assert "updated first" in titles
        assert "first task" not in titles


class TestSyncIndexOnDelete:
    def test_removes_task(self, store_with_tasks: Store) -> None:
        store_with_tasks.sync_index_on_delete(2)
        idx = store_with_tasks.read_index()
        assert len(idx) == 2
        assert {t.id for t in idx} == {1, 3}

    def test_nonexistent_id_noop(self, store_with_tasks: Store) -> None:
        store_with_tasks.sync_index_on_delete(999)
        idx = store_with_tasks.read_index()
        assert len(idx) == 3


# ---- filter -----------------------------------------------------------

class TestFilter:
    def test_returns_all_by_default(self, store_with_tasks: Store) -> None:
        result = store_with_tasks.filter()
        assert len(result) == 3

    def test_filter_by_status(self, store_with_tasks: Store) -> None:
        result = store_with_tasks.filter(status=TaskStatus.TODO)
        assert len(result) == 1
        assert result[0].title == "first task"

    def test_filter_by_single_label(self, store_with_tasks: Store) -> None:
        result = store_with_tasks.filter(labels=["p1"])
        assert len(result) == 2
        assert {t.id for t in result} == {1, 3}

    def test_filter_by_multiple_labels_and(self, store_with_tasks: Store) -> None:
        result = store_with_tasks.filter(labels=["p1", "bug"])
        assert len(result) == 1
        assert result[0].id == 1

    def test_filter_by_labels_case_insensitive(self, store_with_tasks: Store) -> None:
        result = store_with_tasks.filter(labels=["BUG"])
        assert len(result) == 1
        assert result[0].id == 1

    def test_filter_limit(self, store_with_tasks: Store) -> None:
        result = store_with_tasks.filter(limit=2)
        assert len(result) == 2

    def test_filter_limit_zero_returns_all(self, store_with_tasks: Store) -> None:
        result = store_with_tasks.filter(limit=0)
        assert len(result) == 3

    def test_filter_sorted_newest_first(self, store_with_tasks: Store) -> None:
        result = store_with_tasks.filter()
        assert [t.id for t in result] == [3, 2, 1]

    def test_query_in_title(self, store_with_tasks: Store) -> None:
        result = store_with_tasks.filter(q="second")
        assert len(result) == 1
        assert result[0].id == 2

    def test_query_in_body(self, store_with_tasks: Store) -> None:
        result = store_with_tasks.filter(q="more text")
        assert len(result) == 1
        assert result[0].id == 2

    def test_query_in_labels(self, store_with_tasks: Store) -> None:
        result = store_with_tasks.filter(q="feature")
        assert len(result) == 1
        assert result[0].id == 3

    def test_query_in_status_value(self, store_with_tasks: Store) -> None:
        result = store_with_tasks.filter(q="in_progress")
        assert len(result) == 1
        assert result[0].id == 2

    def test_query_case_insensitive(self, store_with_tasks: Store) -> None:
        result = store_with_tasks.filter(q="FIRST")
        assert len(result) == 1
        assert result[0].id == 1

    def test_query_no_match(self, store_with_tasks: Store) -> None:
        result = store_with_tasks.filter(q="zzz_nonexistent_zzz")
        assert result == []

    def test_combined_filters(self, store_with_tasks: Store) -> None:
        # task 3: DONE + p1, task 4 doesn't exist
        result = store_with_tasks.filter(status=TaskStatus.DONE, labels=["p1"])
        assert len(result) == 1
        assert result[0].id == 3
