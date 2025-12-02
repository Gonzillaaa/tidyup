"""File discovery for Tidy.

This module handles discovering files to process, with support for
filtering by patterns, hidden files, and recency.
"""

import fnmatch
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterator, Optional

from .models import FileInfo


# Default patterns to always skip
DEFAULT_SKIP_PATTERNS = [
    ".DS_Store",
    "*.tmp",
    "*.temp",
    "*.crdownload",  # Chrome partial downloads
    "*.part",  # Firefox partial downloads
    "*.download",  # Safari partial downloads
    "Thumbs.db",  # Windows thumbnail cache
    "desktop.ini",  # Windows folder settings
    "*.swp",  # Vim swap files
    "*~",  # Backup files
]


def should_skip_pattern(name: str, patterns: list[str]) -> bool:
    """Check if filename matches any skip pattern.

    Args:
        name: Filename to check.
        patterns: List of glob patterns to match against.

    Returns:
        True if the file should be skipped.
    """
    name_lower = name.lower()
    for pattern in patterns:
        if fnmatch.fnmatch(name_lower, pattern.lower()):
            return True
    return False


def should_skip_recent(
    modified: datetime, skip_recent_hours: int
) -> bool:
    """Check if file was modified too recently.

    Args:
        modified: File's modification timestamp.
        skip_recent_hours: Hours threshold (0 to disable).

    Returns:
        True if the file should be skipped due to recency.
    """
    if skip_recent_hours <= 0:
        return False

    cutoff = datetime.now() - timedelta(hours=skip_recent_hours)
    return modified > cutoff


def discover_files(
    source: Path,
    skip_patterns: Optional[list[str]] = None,
    skip_hidden: bool = True,
    skip_recent_hours: int = 0,
    limit: Optional[int] = None,
) -> Iterator[FileInfo]:
    """Discover files to process in source directory.

    Iterates through files in the source directory, applying various
    filters to skip unwanted files.

    Args:
        source: Source directory to scan.
        skip_patterns: Additional glob patterns to skip (combined with defaults).
        skip_hidden: Whether to skip hidden files (starting with .).
        skip_recent_hours: Skip files modified within this many hours (0 to disable).
        limit: Maximum number of files to yield (None for unlimited).

    Yields:
        FileInfo objects for each file that passes all filters.

    Raises:
        ValueError: If source is not a directory.

    Examples:
        >>> for file in discover_files(Path("~/Downloads"), limit=10):
        ...     print(file.name)
    """
    if not source.is_dir():
        raise ValueError(f"Source must be a directory: {source}")

    # Combine default and custom patterns
    all_patterns = DEFAULT_SKIP_PATTERNS.copy()
    if skip_patterns:
        all_patterns.extend(skip_patterns)

    count = 0

    # Use iterdir for non-recursive, shallow scan of source
    for path in sorted(source.iterdir()):
        # Skip directories
        if path.is_dir():
            continue

        # Skip hidden files
        if skip_hidden and path.name.startswith("."):
            continue

        # Skip by pattern
        if should_skip_pattern(path.name, all_patterns):
            continue

        # Create FileInfo to get modification time
        try:
            file_info = FileInfo.from_path(path)
        except (OSError, PermissionError):
            # Skip files we can't access
            continue

        # Skip recent files
        if should_skip_recent(file_info.modified, skip_recent_hours):
            continue

        yield file_info
        count += 1

        # Check limit
        if limit is not None and count >= limit:
            break
