"""Tests for file operations module."""

import pytest
from pathlib import Path

from tidy.operations import (
    safe_move,
    safe_rename,
    ensure_dest_structure,
    is_duplicate,
    move_to_duplicates,
    DEFAULT_FOLDERS,
)


class TestSafeMove:
    """Tests for safe_move function."""

    def test_moves_file_to_destination(self, tmp_path: Path) -> None:
        """File is moved to destination."""
        src = tmp_path / "source" / "file.txt"
        src.parent.mkdir()
        src.write_text("content")

        dest = tmp_path / "dest" / "file.txt"

        result = safe_move(src, dest)

        assert result == dest
        assert dest.exists()
        assert dest.read_text() == "content"
        assert not src.exists()

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        """Creates parent directories if they don't exist."""
        src = tmp_path / "file.txt"
        src.write_text("content")

        dest = tmp_path / "nested" / "deep" / "folder" / "file.txt"

        result = safe_move(src, dest)

        assert result == dest
        assert dest.exists()

    def test_handles_existing_destination(self, tmp_path: Path) -> None:
        """Generates unique name if destination exists."""
        src = tmp_path / "file.txt"
        src.write_text("new content")

        dest = tmp_path / "dest" / "file.txt"
        dest.parent.mkdir()
        dest.write_text("existing content")

        result = safe_move(src, dest)

        assert result == tmp_path / "dest" / "file (1).txt"
        assert result.exists()
        assert result.read_text() == "new content"
        assert dest.read_text() == "existing content"

    def test_raises_for_nonexistent_source(self, tmp_path: Path) -> None:
        """Raises FileNotFoundError for nonexistent source."""
        src = tmp_path / "nonexistent.txt"
        dest = tmp_path / "dest.txt"

        with pytest.raises(FileNotFoundError):
            safe_move(src, dest)

    def test_raises_for_directory_source(self, tmp_path: Path) -> None:
        """Raises IsADirectoryError for directory source."""
        src = tmp_path / "source_dir"
        src.mkdir()
        dest = tmp_path / "dest"

        with pytest.raises(IsADirectoryError):
            safe_move(src, dest)


class TestSafeRename:
    """Tests for safe_rename function."""

    def test_renames_file(self, tmp_path: Path) -> None:
        """Renames file in same directory."""
        original = tmp_path / "original.txt"
        original.write_text("content")

        result = safe_rename(original, "renamed.txt")

        assert result == tmp_path / "renamed.txt"
        assert result.exists()
        assert not original.exists()

    def test_handles_existing_name(self, tmp_path: Path) -> None:
        """Generates unique name if target exists."""
        original = tmp_path / "original.txt"
        original.write_text("original content")

        existing = tmp_path / "target.txt"
        existing.write_text("existing content")

        result = safe_rename(original, "target.txt")

        assert result == tmp_path / "target (1).txt"
        assert result.exists()
        assert existing.read_text() == "existing content"

    def test_same_name_returns_original(self, tmp_path: Path) -> None:
        """Returns original path if name unchanged."""
        file = tmp_path / "file.txt"
        file.write_text("content")

        result = safe_rename(file, "file.txt")

        assert result == file
        assert file.exists()

    def test_raises_for_nonexistent(self, tmp_path: Path) -> None:
        """Raises FileNotFoundError for nonexistent file."""
        file = tmp_path / "nonexistent.txt"

        with pytest.raises(FileNotFoundError):
            safe_rename(file, "new.txt")

    def test_raises_for_path_in_name(self, tmp_path: Path) -> None:
        """Raises ValueError if new_name contains path."""
        file = tmp_path / "file.txt"
        file.write_text("content")

        with pytest.raises(ValueError, match="path separator"):
            safe_rename(file, "sub/file.txt")


class TestEnsureDestStructure:
    """Tests for ensure_dest_structure function."""

    def test_creates_folders(self, tmp_path: Path) -> None:
        """Creates numbered folders."""
        folders = [
            {"number": 1, "name": "Documents"},
            {"number": 2, "name": "Images"},
        ]

        ensure_dest_structure(tmp_path / "dest", folders)

        assert (tmp_path / "dest" / "01_Documents").is_dir()
        assert (tmp_path / "dest" / "02_Images").is_dir()

    def test_creates_parent_directory(self, tmp_path: Path) -> None:
        """Creates destination root if needed."""
        dest = tmp_path / "nested" / "dest"

        ensure_dest_structure(dest, [{"number": 1, "name": "Test"}])

        assert dest.is_dir()
        assert (dest / "01_Test").is_dir()

    def test_idempotent(self, tmp_path: Path) -> None:
        """Can be called multiple times safely."""
        folders = [{"number": 1, "name": "Documents"}]

        ensure_dest_structure(tmp_path, folders)
        ensure_dest_structure(tmp_path, folders)

        assert (tmp_path / "01_Documents").is_dir()

    def test_default_values(self, tmp_path: Path) -> None:
        """Uses defaults for missing keys."""
        folders = [{}]

        ensure_dest_structure(tmp_path, folders)

        assert (tmp_path / "99_Unsorted").is_dir()


class TestIsDuplicate:
    """Tests for is_duplicate function."""

    def test_detects_duplicate(self, tmp_path: Path) -> None:
        """Detects duplicate when file with same hash exists."""
        # Create source
        source = tmp_path / "source.txt"
        source.write_text("identical content")

        # Create dest with same content
        dest_folder = tmp_path / "dest"
        dest_folder.mkdir()
        existing = dest_folder / "existing.txt"
        existing.write_text("identical content")

        result = is_duplicate(source, dest_folder)

        assert result == existing

    def test_returns_none_for_unique(self, tmp_path: Path) -> None:
        """Returns None when no duplicate exists."""
        source = tmp_path / "source.txt"
        source.write_text("unique content")

        dest_folder = tmp_path / "dest"
        dest_folder.mkdir()
        (dest_folder / "other.txt").write_text("different content")

        result = is_duplicate(source, dest_folder)

        assert result is None

    def test_returns_none_for_empty_dest(self, tmp_path: Path) -> None:
        """Returns None when destination is empty."""
        source = tmp_path / "source.txt"
        source.write_text("content")

        dest_folder = tmp_path / "dest"
        dest_folder.mkdir()

        result = is_duplicate(source, dest_folder)

        assert result is None

    def test_returns_none_for_nonexistent_dest(self, tmp_path: Path) -> None:
        """Returns None when destination doesn't exist."""
        source = tmp_path / "source.txt"
        source.write_text("content")

        dest_folder = tmp_path / "nonexistent"

        result = is_duplicate(source, dest_folder)

        assert result is None

    def test_ignores_directories(self, tmp_path: Path) -> None:
        """Directories in dest are ignored."""
        source = tmp_path / "source.txt"
        source.write_text("content")

        dest_folder = tmp_path / "dest"
        dest_folder.mkdir()
        (dest_folder / "subdir").mkdir()

        result = is_duplicate(source, dest_folder)

        assert result is None


class TestMoveToDuplicates:
    """Tests for move_to_duplicates function."""

    def test_moves_to_duplicates_folder(self, tmp_path: Path) -> None:
        """Moves file to _duplicates subfolder."""
        file = tmp_path / "dupe.txt"
        file.write_text("content")

        dest = tmp_path / "organized"

        result = move_to_duplicates(file, dest)

        expected = dest / "99_Unsorted" / "_duplicates" / "dupe.txt"
        assert result == expected
        assert result.exists()
        assert not file.exists()

    def test_creates_duplicates_folder(self, tmp_path: Path) -> None:
        """Creates _duplicates folder if needed."""
        file = tmp_path / "dupe.txt"
        file.write_text("content")

        dest = tmp_path / "organized"

        move_to_duplicates(file, dest)

        assert (dest / "99_Unsorted" / "_duplicates").is_dir()

    def test_handles_name_conflict(self, tmp_path: Path) -> None:
        """Handles name conflict in duplicates folder."""
        file1 = tmp_path / "file.txt"
        file1.write_text("content 1")

        dest = tmp_path / "organized"
        move_to_duplicates(file1, dest)

        file2 = tmp_path / "file.txt"
        file2.write_text("content 2")

        result = move_to_duplicates(file2, dest)

        assert result.name == "file (1).txt"


class TestDefaultFolders:
    """Tests for DEFAULT_FOLDERS constant."""

    def test_has_required_folders(self) -> None:
        """Has all required category folders."""
        names = {f["name"] for f in DEFAULT_FOLDERS}

        assert "Documents" in names
        assert "Images" in names
        assert "Videos" in names
        assert "Archives" in names
        assert "Books" in names
        assert "Unsorted" in names

    def test_unsorted_is_99(self) -> None:
        """Unsorted folder is number 99."""
        unsorted = next(f for f in DEFAULT_FOLDERS if f["name"] == "Unsorted")
        assert unsorted["number"] == 99

    def test_numbers_are_unique(self) -> None:
        """All folder numbers are unique."""
        numbers = [f["number"] for f in DEFAULT_FOLDERS]
        assert len(numbers) == len(set(numbers))
