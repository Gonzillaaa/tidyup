"""Data models for Tidy.

This module contains all the dataclasses used throughout the application
for representing files, detection results, actions, and run summaries.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime, date
from pathlib import Path
from typing import Literal, Optional


@dataclass
class FileInfo:
    """Information about a file to be processed.

    Attributes:
        path: Full path to the file.
        name: Filename without path.
        extension: File extension without dot (lowercase).
        size: File size in bytes.
        modified: Last modification timestamp.
        created: Creation timestamp.
    """

    path: Path
    name: str
    extension: str
    size: int
    modified: datetime
    created: datetime

    @classmethod
    def from_path(cls, path: Path) -> "FileInfo":
        """Create a FileInfo from a Path object."""
        stat = path.stat()
        return cls(
            path=path,
            name=path.name,
            extension=path.suffix.lstrip(".").lower() if path.suffix else "",
            size=stat.st_size,
            modified=datetime.fromtimestamp(stat.st_mtime),
            created=datetime.fromtimestamp(stat.st_ctime),
        )

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "path": str(self.path),
            "name": self.name,
            "extension": self.extension,
            "size": self.size,
            "modified": self.modified.isoformat(),
            "created": self.created.isoformat(),
        }


@dataclass
class DetectionResult:
    """Result of file type detection.

    Attributes:
        category: The detected category (e.g., "01_Documents", "02_Images").
        confidence: Confidence score from 0.0 to 1.0.
        detector_name: Name of the detector that made this detection.
        reason: Optional explanation for uncertain detections.
    """

    category: str
    confidence: float
    detector_name: str
    reason: Optional[str] = None

    def is_confident(self, threshold: float = 0.7) -> bool:
        """Check if detection meets confidence threshold."""
        return self.confidence >= threshold

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        result = {
            "category": self.category,
            "confidence": self.confidence,
            "detector_name": self.detector_name,
        }
        if self.reason:
            result["reason"] = self.reason
        return result


@dataclass
class RenameResult:
    """Result of file renaming.

    Attributes:
        original_name: The original filename.
        new_name: The new filename after renaming.
        date_extracted: Date extracted from file metadata, if any.
        title_extracted: Title extracted from file metadata, if any.
        renamer_name: Name of the renamer that generated this name.
    """

    original_name: str
    new_name: str
    renamer_name: str
    date_extracted: Optional[date] = None
    title_extracted: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        result = {
            "original_name": self.original_name,
            "new_name": self.new_name,
            "renamer_name": self.renamer_name,
        }
        if self.date_extracted:
            result["date_extracted"] = self.date_extracted.isoformat()
        if self.title_extracted:
            result["title_extracted"] = self.title_extracted
        return result


ActionStatus = Literal["pending", "success", "error", "skipped"]


@dataclass
class Action:
    """A single file processing action.

    Attributes:
        file: Information about the source file.
        detection: Result of file type detection.
        rename: Result of renaming, if applicable.
        source_path: Original file path.
        dest_path: Destination file path after move.
        status: Current status of the action.
        error: Error message if status is "error".
    """

    file: FileInfo
    detection: DetectionResult
    source_path: Path
    dest_path: Path
    status: ActionStatus = "pending"
    rename: Optional[RenameResult] = None
    error: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        result = {
            "file": self.file.name,
            "from": str(self.source_path),
            "to": str(self.dest_path),
            "category": self.detection.category,
            "confidence": self.detection.confidence,
            "status": self.status,
        }
        if self.rename:
            result["renamed_from"] = self.rename.original_name
            result["renamed_to"] = self.rename.new_name
        if self.detection.reason:
            result["reason"] = self.detection.reason
        if self.error:
            result["error"] = self.error
        return result


@dataclass
class RunSummary:
    """Summary statistics for a run.

    Attributes:
        processed: Total files processed.
        moved: Files successfully moved.
        renamed: Files successfully renamed.
        unsorted: Files moved to Unsorted folder.
        skipped: Files skipped (--skip flag or errors).
        errors: Files with errors.
        duplicates: Duplicate files detected.
    """

    processed: int = 0
    moved: int = 0
    renamed: int = 0
    unsorted: int = 0
    skipped: int = 0
    errors: int = 0
    duplicates: int = 0

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


@dataclass
class RunResult:
    """Complete result of a tidy run.

    Attributes:
        timestamp: When the run started.
        source: Source directory path.
        destination: Destination directory path.
        options: CLI options used for this run.
        actions: List of all actions taken.
        summary: Summary statistics.
    """

    timestamp: datetime
    source: Path
    destination: Path
    options: dict
    actions: list[Action] = field(default_factory=list)
    summary: RunSummary = field(default_factory=RunSummary)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "source": str(self.source),
            "destination": str(self.destination),
            "options": self.options,
            "actions": [a.to_dict() for a in self.actions],
            "summary": self.summary.to_dict(),
        }
