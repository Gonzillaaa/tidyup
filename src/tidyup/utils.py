"""Utility functions for TidyUp.

This module contains helper functions for file operations, string sanitization,
hashing, and date handling.
"""

import hashlib
import re
import unicodedata
from datetime import datetime
from pathlib import Path


def sanitize_filename(name: str, max_length: int = 200) -> str:
    """Sanitize a string to be safe for use as a filename.

    Args:
        name: The string to sanitize.
        max_length: Maximum allowed length for the filename.

    Returns:
        A sanitized filename safe for all major operating systems.

    Examples:
        >>> sanitize_filename("Report: Q1 2024")
        'Report_ Q1 2024'
        >>> sanitize_filename("file/with\\bad:chars*?")
        'file_with_bad_chars__'
    """
    if not name:
        return "unnamed"

    # Normalize unicode characters
    name = unicodedata.normalize("NFKC", name)

    # Replace characters that are problematic on various OS
    # Windows: \ / : * ? " < > |
    # macOS/Linux: / and null
    forbidden_chars = r'[\\/:*?"<>|\x00]'
    name = re.sub(forbidden_chars, "_", name)

    # Collapse multiple spaces/underscores into single space
    name = re.sub(r"[\s_]+", " ", name)

    # Remove leading/trailing whitespace
    name = name.strip()

    # Remove leading dots (hidden files on Unix)
    name = name.lstrip(".")

    # Truncate if too long (preserve extension if present)
    if len(name) > max_length:
        name = name[:max_length].rstrip()

    # Fallback if nothing left
    if not name:
        return "unnamed"

    return name


def format_size(bytes_: int) -> str:
    """Convert bytes to human-readable size string.

    Args:
        bytes_: Size in bytes.

    Returns:
        Human-readable size string (e.g., "1.5 MB").

    Examples:
        >>> format_size(1024)
        '1.0 KB'
        >>> format_size(1048576)
        '1.0 MB'
    """
    if bytes_ < 0:
        return "0 B"

    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(bytes_)
    unit_index = 0

    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1

    if unit_index == 0:
        return f"{int(size)} B"
    return f"{size:.1f} {units[unit_index]}"


def compute_file_hash(
    path: Path,
    algorithm: str = "sha256",
    chunk_size: int = 8192,
) -> str:
    """Compute hash of a file using streaming to handle large files.

    Args:
        path: Path to the file.
        algorithm: Hash algorithm to use (default: sha256).
        chunk_size: Size of chunks to read at a time.

    Returns:
        Hexadecimal hash string.

    Raises:
        FileNotFoundError: If file doesn't exist.
        PermissionError: If file can't be read.
    """
    hasher = hashlib.new(algorithm)

    with open(path, "rb") as f:
        while chunk := f.read(chunk_size):
            hasher.update(chunk)

    return hasher.hexdigest()


def get_file_dates(path: Path) -> tuple[datetime, datetime]:
    """Get creation and modification dates of a file.

    Args:
        path: Path to the file.

    Returns:
        Tuple of (created, modified) datetime objects.

    Note:
        On some systems, creation time may not be available and
        will fall back to modification time.
    """
    stat = path.stat()

    modified = datetime.fromtimestamp(stat.st_mtime)

    # st_birthtime is macOS-specific, st_ctime is creation on Windows
    # but inode change time on Unix
    try:
        created = datetime.fromtimestamp(stat.st_birthtime)  # type: ignore
    except AttributeError:
        # Fall back to ctime (which is inode change time on Unix)
        created = datetime.fromtimestamp(stat.st_ctime)

    return created, modified


def generate_unique_path(dest: Path) -> Path:
    """Generate a unique path by appending (1), (2), etc. if file exists.

    Args:
        dest: The desired destination path.

    Returns:
        A path that doesn't exist yet, possibly with a numeric suffix.

    Examples:
        If 'file.pdf' exists:
        >>> generate_unique_path(Path('file.pdf'))
        PosixPath('file (1).pdf')
    """
    if not dest.exists():
        return dest

    stem = dest.stem
    suffix = dest.suffix
    parent = dest.parent

    counter = 1
    while True:
        new_name = f"{stem} ({counter}){suffix}"
        new_path = parent / new_name
        if not new_path.exists():
            return new_path
        counter += 1


def is_ugly_filename(name: str) -> bool:
    """Check if a filename appears to be auto-generated or uninformative.

    Args:
        name: The filename to check (without extension).

    Returns:
        True if the filename looks like random/auto-generated content.

    Examples:
        >>> is_ugly_filename("1743151465964")
        True
        >>> is_ugly_filename("07-05711b687f-fa1b-4a37-bbb6-cf4383aa64de")
        True
        >>> is_ugly_filename("Annual_Report_2024")
        False
    """
    if not name:
        return True

    # Remove extension if present
    stem = Path(name).stem

    # Check if mostly digits (timestamps)
    digit_ratio = sum(c.isdigit() for c in stem) / len(stem) if stem else 0
    if digit_ratio > 0.7:
        return True

    # Check for UUID patterns (standard and non-standard with prefix)
    uuid_pattern = r"^[a-f0-9]{8}(-[a-f0-9]{4}){3}-[a-f0-9]{12}$"
    if re.match(uuid_pattern, stem.lower()):
        return True

    # Check for UUID-like patterns (hex groups separated by dashes)
    # This catches various UUID formats and UUID-like hashes
    hex_dash_pattern = r"^[a-f0-9]{2,}(-[a-f0-9]{2,}){3,}$"
    if re.match(hex_dash_pattern, stem.lower()):
        return True

    # Check for hex strings (common in downloads)
    hex_pattern = r"^[a-f0-9]{16,}$"
    if re.match(hex_pattern, stem.lower()):
        return True

    return False


def format_date(dt: datetime) -> str:
    """Format datetime as ISO date string.

    Args:
        dt: The datetime to format.

    Returns:
        Date string in YYYY-MM-DD format.
    """
    return dt.strftime("%Y-%m-%d")


def format_datetime(dt: datetime) -> str:
    """Format datetime with time for screenshot naming.

    Args:
        dt: The datetime to format.

    Returns:
        Datetime string in YYYY-MM-DD_HH-MM-SS format.
    """
    return dt.strftime("%Y-%m-%d_%H-%M-%S")
