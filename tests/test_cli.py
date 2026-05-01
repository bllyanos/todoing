import os

import pytest
from typer.testing import CliRunner

from todoing.main import app
from todoing.task import Store


@pytest.fixture(autouse=True)
def isolated_store(tmp_path, monkeypatch):
    """Replace the module-level store with one rooted in tmp_path."""
    s = Store(root=tmp_path)
    monkeypatch.setattr("todoing.main.store", s)


@pytest.fixture
def runner():
    return CliRunner()


# ---- add --------------------------------------------------------------

class TestAdd:
    def test_basic(self, runner):
        result = runner.invoke(app, ["add", "my first task"])
        assert result.exit_code == 0
        assert "(#1) my first task" in result.stdout

    def test_with_labels(self, runner):
        result = runner.invoke(app, ["add", "labeled task", "-l", "urgent", "-l", "p0"])
        assert result.exit_code == 0
        assert "(#1) labeled task" in result.stdout

    def test_with_status(self, runner):
        result = runner.invoke(app, ["add", "in progress task", "-s", "in_progress"])
        assert result.exit_code == 0

    def test_with_body(self, runner):
        result = runner.invoke(app, ["add", "described task", "-b", "detailed body"])
        assert result.exit_code == 0
        see = runner.invoke(app, ["see", "1"])
        assert "detailed body" in see.stdout

    def test_invalid_status_rejected(self, runner):
        result = runner.invoke(app, ["add", "bad", "-s", "bogus"])
        assert result.exit_code == 1
        assert "Invalid status" in result.stderr

    def test_sequential_ids(self, runner):
        runner.invoke(app, ["add", "first"])
        runner.invoke(app, ["add", "second"])
        result = runner.invoke(app, ["add", "third"])
        assert "(#3) third" in result.stdout


# ---- ls ---------------------------------------------------------------

class TestLs:
    def test_empty(self, runner):
        result = runner.invoke(app, ["ls"])
        assert result.exit_code == 0
        assert "No tasks." in result.stdout

    def test_shows_newest_first(self, runner):
        runner.invoke(app, ["add", "first"])
        runner.invoke(app, ["add", "second"])
        result = runner.invoke(app, ["ls"])
        assert result.exit_code == 0
        lines = [l for l in result.stdout.strip().split("\n") if l]
        assert "second" in lines[0]
        assert "first" in lines[1]

    def test_limit(self, runner):
        runner.invoke(app, ["add", "a"])
        runner.invoke(app, ["add", "b"])
        runner.invoke(app, ["add", "c"])
        result = runner.invoke(app, ["ls", "-n", "2"])
        lines = [l for l in result.stdout.strip().split("\n") if l]
        assert len(lines) == 2

    def test_filter_by_status(self, runner):
        runner.invoke(app, ["add", "todo task"])
        runner.invoke(app, ["add", "done task", "-s", "done"])
        result = runner.invoke(app, ["ls", "-s", "done"])
        lines = [l for l in result.stdout.strip().split("\n") if l]
        assert len(lines) == 1
        assert "done task" in lines[0]

    def test_filter_by_label(self, runner):
        runner.invoke(app, ["add", "buggy", "-l", "bug"])
        runner.invoke(app, ["add", "clean"])
        result = runner.invoke(app, ["ls", "-l", "bug"])
        lines = [l for l in result.stdout.strip().split("\n") if l]
        assert len(lines) == 1
        assert "buggy" in lines[0]

    def test_filter_by_2_labels_and(self, runner):
        runner.invoke(app, ["add", "both", "-l", "a", "-l", "b"])
        runner.invoke(app, ["add", "only_a", "-l", "a"])
        result = runner.invoke(app, ["ls", "-l", "a", "-l", "b"])
        lines = [l for l in result.stdout.strip().split("\n") if l]
        assert len(lines) == 1
        assert "both" in lines[0]


# ---- see --------------------------------------------------------------

class TestSee:
    def test_existing_task(self, runner):
        runner.invoke(app, ["add", "view me", "-b", "the body"])
        result = runner.invoke(app, ["see", "1"])
        assert result.exit_code == 0
        assert "id: 1" in result.stdout
        assert "title: view me" in result.stdout
        assert "the body" in result.stdout

    def test_hash_prefix(self, runner):
        runner.invoke(app, ["add", "hashed"])
        result = runner.invoke(app, ["see", "#1"])
        assert result.exit_code == 0
        assert "title: hashed" in result.stdout

    def test_missing_task(self, runner):
        result = runner.invoke(app, ["see", "99"])
        assert result.exit_code == 1
        assert "not found" in result.stderr

    def test_invalid_id(self, runner):
        result = runner.invoke(app, ["see", "notanumber"])
        assert result.exit_code == 1
        assert result.exception is not None


# ---- body -------------------------------------------------------------

class TestBody:
    def test_sets_body(self, runner):
        runner.invoke(app, ["add", "write it"])
        result = runner.invoke(app, ["body", "1", "new content"])
        assert result.exit_code == 0
        assert "body updated" in result.stdout
        see = runner.invoke(app, ["see", "1"])
        assert "new content" in see.stdout

    def test_overwrites_existing_body(self, runner):
        runner.invoke(app, ["add", "rewrite", "-b", "old"])
        runner.invoke(app, ["body", "1", "new"])
        see = runner.invoke(app, ["see", "1"])
        assert "old" not in see.stdout
        assert "new" in see.stdout

    def test_missing_task(self, runner):
        result = runner.invoke(app, ["body", "99", "text"])
        assert result.exit_code == 1
        assert "not found" in result.stderr


# ---- append -----------------------------------------------------------

class TestAppend:
    def test_append_to_empty(self, runner):
        runner.invoke(app, ["add", "empty body"])
        result = runner.invoke(app, ["append", "1", "first paragraph"])
        assert result.exit_code == 0
        assert "body appended" in result.stdout
        see = runner.invoke(app, ["see", "1"])
        assert "first paragraph" in see.stdout

    def test_append_to_existing(self, runner):
        runner.invoke(app, ["add", "existing", "-b", "line one"])
        runner.invoke(app, ["append", "1", "line two"])
        see = runner.invoke(app, ["see", "1"])
        assert "line one\n\nline two" in see.stdout

    def test_missing_task(self, runner):
        result = runner.invoke(app, ["append", "99", "text"])
        assert result.exit_code == 1
        assert "not found" in result.stderr


# ---- status -----------------------------------------------------------

class TestStatus:
    def test_change_status(self, runner):
        runner.invoke(app, ["add", "change me"])
        result = runner.invoke(app, ["status", "1", "done"])
        assert result.exit_code == 0
        assert "status ->" in result.stdout
        assert "\u2705" in result.stdout

    def test_all_valid_statuses(self, runner):
        runner.invoke(app, ["add", "status test"])
        for st in ("todo", "in_progress", "done", "cancelled"):
            r = runner.invoke(app, ["status", "1", st])
            assert r.exit_code == 0, f"status '{st}' should be valid"

    def test_invalid_status(self, runner):
        runner.invoke(app, ["add", "test"])
        result = runner.invoke(app, ["status", "1", "unknown"])
        assert result.exit_code == 1
        assert "Invalid status" in result.stderr

    def test_missing_task(self, runner):
        result = runner.invoke(app, ["status", "99", "done"])
        assert result.exit_code == 1
        assert "not found" in result.stderr


# ---- label ------------------------------------------------------------

class TestLabel:
    def test_add_label(self, runner):
        runner.invoke(app, ["add", "label test"])
        result = runner.invoke(app, ["label", "1", "+urgent"])
        assert result.exit_code == 0
        assert "labels -> [urgent]" in result.stdout

    def test_remove_label(self, runner):
        runner.invoke(app, ["add", "rm test", "-l", "bug", "-l", "feature"])
        result = runner.invoke(app, ["label", "1", "--", "-bug"])
        assert result.exit_code == 0
        assert "labels -> [feature]" in result.stdout

    def test_add_and_remove(self, runner):
        runner.invoke(app, ["add", "both ops", "-l", "a", "-l", "b"])
        result = runner.invoke(app, ["label", "1", "+c", "--", "-a"])
        assert result.exit_code == 0
        assert "labels -> [b, c]" in result.stdout

    def test_clear_before_add(self, runner):
        runner.invoke(app, ["add", "clear test", "-l", "old1", "-l", "old2"])
        result = runner.invoke(app, ["label", "1", "+fresh", "--clear"])
        assert result.exit_code == 0
        assert "labels -> [fresh]" in result.stdout

    def test_remove_nonexistent_noop(self, runner):
        runner.invoke(app, ["add", "no label task"])
        result = runner.invoke(app, ["label", "1", "--", "-nonexistent"])
        assert result.exit_code == 0
        assert "labels -> []" in result.stdout

    def test_invalid_operation(self, runner):
        runner.invoke(app, ["add", "op test"])
        result = runner.invoke(app, ["label", "1", "invalid"])
        assert result.exit_code == 1
        assert "Invalid label operation" in result.stderr

    def test_missing_task(self, runner):
        result = runner.invoke(app, ["label", "99", "+tag"])
        assert result.exit_code == 1
        assert "not found" in result.stderr


# ---- search -----------------------------------------------------------

class TestSearch:
    def test_matches_title(self, runner):
        runner.invoke(app, ["add", "deploy to production"])
        runner.invoke(app, ["add", "fix typo"])
        result = runner.invoke(app, ["search", "deploy"])
        assert result.exit_code == 0
        assert "deploy to production" in result.stdout
        assert "fix typo" not in result.stdout

    def test_matches_body(self, runner):
        runner.invoke(app, ["add", "task 1", "-b", "secret code"])
        runner.invoke(app, ["add", "task 2", "-b", "public doc"])
        result = runner.invoke(app, ["search", "secret"])
        assert "task 1" in result.stdout
        assert "task 2" not in result.stdout

    def test_matches_labels(self, runner):
        runner.invoke(app, ["add", "bug fix", "-l", "critical"])
        runner.invoke(app, ["add", "feature", "-l", "minor"])
        result = runner.invoke(app, ["search", "critical"])
        assert "bug fix" in result.stdout
        assert "feature" not in result.stdout

    def test_case_insensitive(self, runner):
        runner.invoke(app, ["add", "Case Sensitive"])
        result = runner.invoke(app, ["search", "case"])
        assert "Case Sensitive" in result.stdout

    def test_no_matches(self, runner):
        runner.invoke(app, ["add", "only task"])
        result = runner.invoke(app, ["search", "zzz"])
        assert result.exit_code == 0
        assert "No matches." in result.stdout


# ---- delete -----------------------------------------------------------

class TestDelete:
    def test_delete_with_confirmation(self, runner):
        runner.invoke(app, ["add", "delete me"])
        result = runner.invoke(app, ["delete", "1"], input="y\n")
        assert result.exit_code == 0
        assert "deleted" in result.stdout
        ls = runner.invoke(app, ["ls"])
        assert "No tasks." in ls.stdout

    def test_delete_refused(self, runner):
        runner.invoke(app, ["add", "keep me"])
        result = runner.invoke(app, ["delete", "1"], input="n\n")
        assert result.exit_code == 0
        assert "Aborted." in result.stdout
        ls = runner.invoke(app, ["ls"])
        assert "keep me" in ls.stdout

    def test_force_delete(self, runner):
        runner.invoke(app, ["add", "force delete"])
        result = runner.invoke(app, ["delete", "1", "--force"])
        assert result.exit_code == 0
        assert "deleted" in result.stdout

    def test_missing_task(self, runner):
        result = runner.invoke(app, ["delete", "99", "--force"])
        assert result.exit_code == 1
        assert "not found" in result.stderr


# ---- reindex ----------------------------------------------------------

class TestReindex:
    def test_empty(self, runner):
        result = runner.invoke(app, ["reindex"])
        assert result.exit_code == 0
        assert "0 tasks" in result.stdout

    def test_with_tasks(self, runner):
        runner.invoke(app, ["add", "a"])
        runner.invoke(app, ["add", "b"])
        result = runner.invoke(app, ["reindex"])
        assert result.exit_code == 0
        assert "2 tasks" in result.stdout


# ---- edge cases -------------------------------------------------------

class TestEdgeCases:
    def test_special_chars_in_title(self, runner):
        result = runner.invoke(app, ["add", "fix: #42 @home !!!"])
        assert result.exit_code == 0
        see = runner.invoke(app, ["see", "1"])
        assert "fix: #42 @home !!!" in see.stdout

    def test_multiline_body(self, runner):
        result = runner.invoke(app, ["add", "ml", "-b", "line1\nline2\nline3"])
        assert result.exit_code == 0
        see = runner.invoke(app, ["see", "1"])
        assert "line1\nline2\nline3" in see.stdout
