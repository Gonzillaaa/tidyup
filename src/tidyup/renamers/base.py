"""Base renamer class and utilities.

This module provides the abstract base class for all renamers.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

from ..models import DetectionResult, FileInfo, RenameResult


def format_date(dt: datetime) -> str:
    """Format datetime as ISO date string.

    Args:
        dt: Datetime to format.

    Returns:
        Date string in YYYY-MM-DD format.
    """
    return dt.strftime("%Y-%m-%d")


def format_datetime(dt: datetime) -> str:
    """Format datetime with time for screenshots.

    Args:
        dt: Datetime to format.

    Returns:
        DateTime string in YYYY-MM-DD_HH-MM-SS format.
    """
    return dt.strftime("%Y-%m-%d_%H-%M-%S")


class BaseRenamer(ABC):
    """Abstract base class for file renamers.

    Renamers generate new filenames based on file content,
    metadata, and detection results.

    Attributes:
        name: Human-readable name of the renamer.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the renamer name."""
        ...

    @abstractmethod
    def rename(
        self,
        file: FileInfo,
        detection: DetectionResult,
    ) -> Optional[RenameResult]:
        """Generate a new filename for a file.

        Args:
            file: FileInfo for the file to rename.
            detection: DetectionResult from category detection.

        Returns:
            RenameResult if file should be renamed, None otherwise.
        """
        ...

    def should_rename(self, file: FileInfo) -> bool:
        """Check if this file should be renamed.

        Default implementation checks for "ugly" filenames.
        Subclasses can override for different logic.

        Args:
            file: FileInfo for the file.

        Returns:
            True if file should be renamed.
        """
        from ..utils import is_ugly_filename
        return is_ugly_filename(file.path.stem)
