"""Logging system for Tidy.

This module handles logging all file operations to JSON files
for auditing and status reporting.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from .models import Action, RunResult, RunSummary


def get_tidy_dir() -> Path:
    """Get the tidy config/data directory.

    Returns:
        Path to ~/.tidy/ directory.
    """
    return Path.home() / ".tidy"


def ensure_log_dir() -> Path:
    """Ensure the log directory exists.

    Creates ~/.tidy/logs/ if it doesn't exist.

    Returns:
        Path to the logs directory.
    """
    log_dir = get_tidy_dir() / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


class ActionLogger:
    """Logger for tracking file operations during a run.

    Collects all actions taken during a tidy run and saves
    them to a JSON log file.

    Attributes:
        source: Source directory being processed.
        destination: Destination directory.
        options: CLI options for this run.
        actions: List of actions taken.
        summary: Summary statistics.
        timestamp: When the run started.
    """

    def __init__(
        self,
        source: Path,
        destination: Path,
        options: dict,
    ) -> None:
        """Initialize the action logger.

        Args:
            source: Source directory path.
            destination: Destination directory path.
            options: Dictionary of CLI options.
        """
        self.source = source
        self.destination = destination
        self.options = options
        self.actions: list[Action] = []
        self.summary = RunSummary()
        self.timestamp = datetime.now()

    def log_action(self, action: Action) -> None:
        """Log a file operation action.

        Args:
            action: The action to log.
        """
        self.actions.append(action)

        # Update summary counters
        self.summary.processed += 1

        if action.status == "success":
            self.summary.moved += 1
            if action.rename:
                self.summary.renamed += 1
            if "Unsorted" in action.detection.category:
                self.summary.unsorted += 1
        elif action.status == "error":
            self.summary.errors += 1
        elif action.status == "skipped":
            self.summary.skipped += 1

    def log_duplicate(self) -> None:
        """Increment the duplicates counter."""
        self.summary.duplicates += 1

    def get_run_result(self) -> RunResult:
        """Create a RunResult from the current state.

        Returns:
            RunResult containing all logged data.
        """
        return RunResult(
            timestamp=self.timestamp,
            source=self.source,
            destination=self.destination,
            options=self.options,
            actions=self.actions,
            summary=self.summary,
        )

    def save(self) -> Path:
        """Save the log to a JSON file.

        Writes to ~/.tidy/logs/YYYY-MM-DD_HHMMSS.json

        Returns:
            Path to the saved log file.
        """
        log_dir = ensure_log_dir()
        filename = self.timestamp.strftime("%Y-%m-%d_%H%M%S.json")
        log_path = log_dir / filename

        run_result = self.get_run_result()
        log_data = run_result.to_dict()

        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)

        return log_path


def load_log(path: Path) -> RunResult:
    """Load a log file and parse it back to a RunResult.

    Args:
        path: Path to the log file.

    Returns:
        RunResult parsed from the JSON file.

    Raises:
        FileNotFoundError: If log file doesn't exist.
        json.JSONDecodeError: If log file is invalid JSON.
    """
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Parse the summary
    summary_data = data.get("summary", {})
    summary = RunSummary(
        processed=summary_data.get("processed", 0),
        moved=summary_data.get("moved", 0),
        renamed=summary_data.get("renamed", 0),
        unsorted=summary_data.get("unsorted", 0),
        skipped=summary_data.get("skipped", 0),
        errors=summary_data.get("errors", 0),
        duplicates=summary_data.get("duplicates", 0),
    )

    # Note: We don't fully parse actions back to Action objects
    # as that would require reconstructing FileInfo, DetectionResult etc.
    # For now, keep them as dicts in the RunResult

    return RunResult(
        timestamp=datetime.fromisoformat(data["timestamp"]),
        source=Path(data["source"]),
        destination=Path(data["destination"]),
        options=data.get("options", {}),
        actions=[],  # Actions not fully parsed back
        summary=summary,
    )


def list_logs(limit: Optional[int] = None) -> list[Path]:
    """List log files sorted by date descending (newest first).

    Args:
        limit: Maximum number of logs to return (None for all).

    Returns:
        List of paths to log files.
    """
    log_dir = get_tidy_dir() / "logs"

    if not log_dir.exists():
        return []

    # Get all .json files
    logs = sorted(
        log_dir.glob("*.json"),
        key=lambda p: p.name,
        reverse=True,
    )

    if limit is not None:
        logs = logs[:limit]

    return logs


def aggregate_logs(days: int = 7) -> dict:
    """Aggregate statistics from recent log files.

    Args:
        days: Number of days to look back.

    Returns:
        Dictionary with aggregated statistics:
        - total_runs: Number of runs
        - total_processed: Total files processed
        - total_moved: Total files moved
        - total_renamed: Total files renamed
        - total_errors: Total errors
        - total_duplicates: Total duplicates found
    """
    log_dir = get_tidy_dir() / "logs"

    if not log_dir.exists():
        return {
            "total_runs": 0,
            "total_processed": 0,
            "total_moved": 0,
            "total_renamed": 0,
            "total_errors": 0,
            "total_duplicates": 0,
        }

    cutoff = datetime.now() - timedelta(days=days)
    cutoff_str = cutoff.strftime("%Y-%m-%d")

    stats = {
        "total_runs": 0,
        "total_processed": 0,
        "total_moved": 0,
        "total_renamed": 0,
        "total_errors": 0,
        "total_duplicates": 0,
    }

    for log_path in log_dir.glob("*.json"):
        # Check if log is within date range (filename format: YYYY-MM-DD_HHMMSS.json)
        log_date = log_path.stem[:10]  # Extract YYYY-MM-DD
        if log_date < cutoff_str:
            continue

        try:
            run_result = load_log(log_path)
            stats["total_runs"] += 1
            stats["total_processed"] += run_result.summary.processed
            stats["total_moved"] += run_result.summary.moved
            stats["total_renamed"] += run_result.summary.renamed
            stats["total_errors"] += run_result.summary.errors
            stats["total_duplicates"] += run_result.summary.duplicates
        except (json.JSONDecodeError, KeyError, ValueError):
            # Skip invalid log files
            continue

    return stats
