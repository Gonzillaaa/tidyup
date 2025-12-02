"""File operations for Tidy.

This module handles safe file moves, renames, and duplicate detection.
All operations are designed to never lose data.
"""

import shutil
from pathlib import Path
from typing import Optional

from .utils import compute_file_hash, generate_unique_path


def safe_move(src: Path, dest: Path) -> Path:
    """Safely move a file to destination, handling cross-device moves.

    Creates parent directories if they don't exist. If the destination
    already exists, generates a unique name with numeric suffix.

    Args:
        src: Source file path.
        dest: Destination file path.

    Returns:
        The final path where the file was moved.

    Raises:
        FileNotFoundError: If source file doesn't exist.
        IsADirectoryError: If source is a directory.
        PermissionError: If lacking permissions.
    """
    if not src.exists():
        raise FileNotFoundError(f"Source file not found: {src}")

    if src.is_dir():
        raise IsADirectoryError(f"Source must be a file, not directory: {src}")

    # Create destination parent directories
    dest.parent.mkdir(parents=True, exist_ok=True)

    # Generate unique path if destination exists
    final_dest = generate_unique_path(dest)

    # Use shutil.move which handles cross-device moves
    shutil.move(str(src), str(final_dest))

    return final_dest


def safe_rename(path: Path, new_name: str) -> Path:
    """Safely rename a file in the same directory.

    If a file with the new name already exists, generates a unique
    name with numeric suffix.

    Args:
        path: Current file path.
        new_name: New filename (without path).

    Returns:
        The final path after renaming.

    Raises:
        FileNotFoundError: If source file doesn't exist.
        ValueError: If new_name contains path separators.
    """
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    if "/" in new_name or "\\" in new_name:
        raise ValueError(f"new_name must not contain path separators: {new_name}")

    new_path = path.parent / new_name

    # If name unchanged, return original
    if new_path == path:
        return path

    # Generate unique path if destination exists
    final_path = generate_unique_path(new_path)

    path.rename(final_path)

    return final_path


def ensure_dest_structure(dest: Path, folders: list[dict]) -> None:
    """Create the destination folder structure.

    Creates numbered folders based on configuration.

    Args:
        dest: Destination root directory.
        folders: List of folder configs with 'number' and 'name' keys.

    Example:
        >>> folders = [
        ...     {"number": 1, "name": "Documents"},
        ...     {"number": 2, "name": "Images"},
        ... ]
        >>> ensure_dest_structure(Path("/dest"), folders)
        # Creates: /dest/01_Documents/, /dest/02_Images/
    """
    dest.mkdir(parents=True, exist_ok=True)

    for folder in folders:
        number = folder.get("number", 99)
        name = folder.get("name", "Unsorted")
        folder_name = f"{number:02d}_{name}"
        folder_path = dest / folder_name
        folder_path.mkdir(exist_ok=True)


def is_duplicate(file: Path, dest_folder: Path) -> Optional[Path]:
    """Check if file is a duplicate of an existing file in destination.

    Compares file hashes to detect exact duplicates.

    Args:
        file: File to check.
        dest_folder: Destination folder to search for duplicates.

    Returns:
        Path to the existing duplicate if found, None otherwise.
    """
    if not file.exists() or not dest_folder.exists():
        return None

    # Compute hash of source file
    try:
        source_hash = compute_file_hash(file)
    except (OSError, PermissionError):
        return None

    # Check all files in destination folder
    for existing in dest_folder.iterdir():
        if existing.is_dir():
            continue

        try:
            if compute_file_hash(existing) == source_hash:
                return existing
        except (OSError, PermissionError):
            continue

    return None


def move_to_duplicates(file: Path, dest: Path) -> Path:
    """Move a file to the duplicates subfolder.

    Moves the file to 99_Unsorted/_duplicates/ subfolder.

    Args:
        file: File to move.
        dest: Destination root directory.

    Returns:
        The final path where the duplicate was moved.
    """
    duplicates_folder = dest / "99_Unsorted" / "_duplicates"
    duplicates_folder.mkdir(parents=True, exist_ok=True)

    dest_path = duplicates_folder / file.name
    return safe_move(file, dest_path)


# Default folder structure for tidy
DEFAULT_FOLDERS = [
    {"number": 1, "name": "Documents"},
    {"number": 2, "name": "Images"},
    {"number": 3, "name": "Videos"},
    {"number": 4, "name": "Audio"},
    {"number": 5, "name": "Archives"},
    {"number": 6, "name": "Code"},
    {"number": 7, "name": "Books"},
    {"number": 8, "name": "Data"},
    {"number": 99, "name": "Unsorted"},
]
