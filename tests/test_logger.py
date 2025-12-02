"""Tests for logging system."""

import json
import pytest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

from tidyup.logger import (
    ensure_log_dir,
    get_tidy_dir,
    ActionLogger,
    load_log,
    list_logs,
    aggregate_logs,
)
from tidyup.models import Action, FileInfo, DetectionResult, RenameResult


class TestEnsureLogDir:
    """Tests for ensure_log_dir function."""

    def test_creates_log_directory(self, tmp_path: Path) -> None:
        """Creates log directory if it doesn't exist."""
        with patch("tidyup.logger.get_tidy_dir", return_value=tmp_path):
            result = ensure_log_dir()

            assert result == tmp_path / "logs"
            assert result.is_dir()

    def test_returns_existing_directory(self, tmp_path: Path) -> None:
        """Returns existing directory without error."""
        log_dir = tmp_path / "logs"
        log_dir.mkdir(parents=True)

        with patch("tidyup.logger.get_tidy_dir", return_value=tmp_path):
            result = ensure_log_dir()

            assert result == log_dir


class TestActionLogger:
    """Tests for ActionLogger class."""

    def test_init_sets_attributes(self, tmp_path: Path) -> None:
        """Initializes with correct attributes."""
        source = tmp_path / "source"
        dest = tmp_path / "dest"
        options = {"move": True, "dry_run": False}

        logger = ActionLogger(source, dest, options)

        assert logger.source == source
        assert logger.destination == dest
        assert logger.options == options
        assert logger.actions == []
        assert isinstance(logger.timestamp, datetime)

    def test_log_action_appends(self, tmp_path: Path, sample_pdf: Path) -> None:
        """log_action appends action to list."""
        logger = ActionLogger(tmp_path, tmp_path, {})

        action = Action(
            file=FileInfo.from_path(sample_pdf),
            detection=DetectionResult("01_Documents", 0.9, "TestDetector"),
            source_path=sample_pdf,
            dest_path=tmp_path / "dest" / "file.pdf",
            status="success",
        )

        logger.log_action(action)

        assert len(logger.actions) == 1
        assert logger.actions[0] == action

    def test_log_action_updates_summary(self, tmp_path: Path, sample_pdf: Path) -> None:
        """log_action updates summary counters."""
        logger = ActionLogger(tmp_path, tmp_path, {})

        # Success action
        action = Action(
            file=FileInfo.from_path(sample_pdf),
            detection=DetectionResult("01_Documents", 0.9, "TestDetector"),
            source_path=sample_pdf,
            dest_path=tmp_path / "dest" / "file.pdf",
            status="success",
            rename=RenameResult("old.pdf", "new.pdf", "TestRenamer"),
        )
        logger.log_action(action)

        assert logger.summary.processed == 1
        assert logger.summary.moved == 1
        assert logger.summary.renamed == 1

    def test_log_action_tracks_errors(self, tmp_path: Path, sample_pdf: Path) -> None:
        """log_action tracks error status."""
        logger = ActionLogger(tmp_path, tmp_path, {})

        action = Action(
            file=FileInfo.from_path(sample_pdf),
            detection=DetectionResult("01_Documents", 0.9, "TestDetector"),
            source_path=sample_pdf,
            dest_path=tmp_path / "dest" / "file.pdf",
            status="error",
            error="Permission denied",
        )
        logger.log_action(action)

        assert logger.summary.errors == 1

    def test_log_action_tracks_unsorted(self, tmp_path: Path, sample_pdf: Path) -> None:
        """log_action tracks unsorted files."""
        logger = ActionLogger(tmp_path, tmp_path, {})

        action = Action(
            file=FileInfo.from_path(sample_pdf),
            detection=DetectionResult("99_Unsorted", 0.3, "TestDetector"),
            source_path=sample_pdf,
            dest_path=tmp_path / "dest" / "file.pdf",
            status="success",
        )
        logger.log_action(action)

        assert logger.summary.unsorted == 1

    def test_log_duplicate_increments_counter(self, tmp_path: Path) -> None:
        """log_duplicate increments duplicates counter."""
        logger = ActionLogger(tmp_path, tmp_path, {})

        logger.log_duplicate()
        logger.log_duplicate()

        assert logger.summary.duplicates == 2

    def test_get_run_result_returns_result(self, tmp_path: Path) -> None:
        """get_run_result creates RunResult."""
        logger = ActionLogger(tmp_path, tmp_path / "dest", {"dry_run": True})

        result = logger.get_run_result()

        assert result.source == tmp_path
        assert result.destination == tmp_path / "dest"
        assert result.options == {"dry_run": True}

    def test_save_creates_json_file(self, tmp_path: Path) -> None:
        """save creates JSON file with correct format."""
        with patch("tidyup.logger.ensure_log_dir", return_value=tmp_path):
            logger = ActionLogger(
                tmp_path / "source",
                tmp_path / "dest",
                {"move": True},
            )
            logger.timestamp = datetime(2024, 1, 15, 14, 30, 45)

            log_path = logger.save()

            assert log_path.exists()
            assert log_path.name == "2024-01-15_143045.json"

            with open(log_path) as f:
                data = json.load(f)

            assert data["source"] == str(tmp_path / "source")
            assert data["destination"] == str(tmp_path / "dest")
            assert data["options"]["move"] is True
            assert "summary" in data


class TestLoadLog:
    """Tests for load_log function."""

    def test_loads_valid_log(self, tmp_path: Path) -> None:
        """Loads and parses valid log file."""
        log_data = {
            "timestamp": "2024-01-15T14:30:45",
            "source": "/path/to/source",
            "destination": "/path/to/dest",
            "options": {"dry_run": False},
            "actions": [],
            "summary": {
                "processed": 10,
                "moved": 8,
                "renamed": 7,
                "unsorted": 2,
                "skipped": 1,
                "errors": 1,
                "duplicates": 0,
            },
        }
        log_path = tmp_path / "test.json"
        with open(log_path, "w") as f:
            json.dump(log_data, f)

        result = load_log(log_path)

        assert result.source == Path("/path/to/source")
        assert result.destination == Path("/path/to/dest")
        assert result.summary.processed == 10
        assert result.summary.moved == 8

    def test_raises_for_nonexistent(self, tmp_path: Path) -> None:
        """Raises FileNotFoundError for missing file."""
        with pytest.raises(FileNotFoundError):
            load_log(tmp_path / "nonexistent.json")

    def test_raises_for_invalid_json(self, tmp_path: Path) -> None:
        """Raises JSONDecodeError for invalid JSON."""
        log_path = tmp_path / "invalid.json"
        log_path.write_text("not valid json {{{")

        with pytest.raises(json.JSONDecodeError):
            load_log(log_path)


class TestListLogs:
    """Tests for list_logs function."""

    def test_returns_empty_for_no_dir(self, tmp_path: Path) -> None:
        """Returns empty list if log dir doesn't exist."""
        with patch("tidyup.logger.get_tidy_dir", return_value=tmp_path / "nonexistent"):
            result = list_logs()

            assert result == []

    def test_returns_logs_sorted_descending(self, tmp_path: Path) -> None:
        """Returns logs sorted newest first."""
        log_dir = tmp_path / "logs"
        log_dir.mkdir()

        (log_dir / "2024-01-10_120000.json").write_text("{}")
        (log_dir / "2024-01-15_120000.json").write_text("{}")
        (log_dir / "2024-01-12_120000.json").write_text("{}")

        with patch("tidyup.logger.get_tidy_dir", return_value=tmp_path):
            result = list_logs()

            assert len(result) == 3
            assert result[0].name == "2024-01-15_120000.json"
            assert result[1].name == "2024-01-12_120000.json"
            assert result[2].name == "2024-01-10_120000.json"

    def test_respects_limit(self, tmp_path: Path) -> None:
        """Respects limit parameter."""
        log_dir = tmp_path / "logs"
        log_dir.mkdir()

        for i in range(5):
            (log_dir / f"2024-01-{10+i:02d}_120000.json").write_text("{}")

        with patch("tidyup.logger.get_tidy_dir", return_value=tmp_path):
            result = list_logs(limit=2)

            assert len(result) == 2

    def test_ignores_non_json_files(self, tmp_path: Path) -> None:
        """Ignores non-JSON files."""
        log_dir = tmp_path / "logs"
        log_dir.mkdir()

        (log_dir / "2024-01-15_120000.json").write_text("{}")
        (log_dir / "readme.txt").write_text("text")
        (log_dir / "backup.bak").write_text("backup")

        with patch("tidyup.logger.get_tidy_dir", return_value=tmp_path):
            result = list_logs()

            assert len(result) == 1


class TestAggregateLogs:
    """Tests for aggregate_logs function."""

    def test_returns_zeros_for_no_logs(self, tmp_path: Path) -> None:
        """Returns zero stats when no logs exist."""
        with patch("tidyup.logger.get_tidy_dir", return_value=tmp_path / "nonexistent"):
            result = aggregate_logs()

            assert result["total_runs"] == 0
            assert result["total_processed"] == 0

    def test_aggregates_recent_logs(self, tmp_path: Path) -> None:
        """Aggregates stats from recent logs."""
        log_dir = tmp_path / "logs"
        log_dir.mkdir()

        # Recent log
        today = datetime.now().strftime("%Y-%m-%d")
        recent_log = {
            "timestamp": f"{today}T12:00:00",
            "source": "/source",
            "destination": "/dest",
            "options": {},
            "actions": [],
            "summary": {"processed": 10, "moved": 8, "renamed": 5, "errors": 1, "duplicates": 2, "unsorted": 0, "skipped": 0},
        }
        with open(log_dir / f"{today}_120000.json", "w") as f:
            json.dump(recent_log, f)

        with patch("tidyup.logger.get_tidy_dir", return_value=tmp_path):
            result = aggregate_logs(days=7)

            assert result["total_runs"] == 1
            assert result["total_processed"] == 10
            assert result["total_moved"] == 8
            assert result["total_errors"] == 1

    def test_excludes_old_logs(self, tmp_path: Path) -> None:
        """Excludes logs older than specified days."""
        log_dir = tmp_path / "logs"
        log_dir.mkdir()

        # Old log (30 days ago)
        old_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        old_log = {
            "timestamp": f"{old_date}T12:00:00",
            "source": "/source",
            "destination": "/dest",
            "options": {},
            "actions": [],
            "summary": {"processed": 100, "moved": 0, "renamed": 0, "errors": 0, "duplicates": 0, "unsorted": 0, "skipped": 0},
        }
        with open(log_dir / f"{old_date}_120000.json", "w") as f:
            json.dump(old_log, f)

        with patch("tidyup.logger.get_tidy_dir", return_value=tmp_path):
            result = aggregate_logs(days=7)

            assert result["total_runs"] == 0
            assert result["total_processed"] == 0

    def test_skips_invalid_logs(self, tmp_path: Path) -> None:
        """Skips logs that can't be parsed."""
        log_dir = tmp_path / "logs"
        log_dir.mkdir()

        today = datetime.now().strftime("%Y-%m-%d")
        (log_dir / f"{today}_120000.json").write_text("invalid json {{{")

        with patch("tidyup.logger.get_tidy_dir", return_value=tmp_path):
            # Should not raise, just skip the invalid log
            result = aggregate_logs(days=7)

            assert result["total_runs"] == 0
