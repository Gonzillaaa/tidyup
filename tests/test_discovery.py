"""Tests for file discovery module."""

import pytest
from datetime import datetime, timedelta
from pathlib import Path

from tidy.discovery import (
    discover_files,
    should_skip_pattern,
    should_skip_recent,
    DEFAULT_SKIP_PATTERNS,
)


class TestShouldSkipPattern:
    """Tests for should_skip_pattern function."""

    def test_matches_exact_name(self) -> None:
        """Matches exact filename."""
        assert should_skip_pattern(".DS_Store", [".DS_Store"]) is True

    def test_matches_wildcard_extension(self) -> None:
        """Matches wildcard pattern for extension."""
        assert should_skip_pattern("file.tmp", ["*.tmp"]) is True
        assert should_skip_pattern("download.crdownload", ["*.crdownload"]) is True

    def test_case_insensitive(self) -> None:
        """Pattern matching is case-insensitive."""
        assert should_skip_pattern("FILE.TMP", ["*.tmp"]) is True
        assert should_skip_pattern(".ds_store", [".DS_Store"]) is True

    def test_no_match_returns_false(self) -> None:
        """Returns False when no pattern matches."""
        assert should_skip_pattern("document.pdf", ["*.tmp", "*.part"]) is False

    def test_empty_patterns_returns_false(self) -> None:
        """Empty pattern list returns False."""
        assert should_skip_pattern("anything.txt", []) is False


class TestShouldSkipRecent:
    """Tests for should_skip_recent function."""

    def test_recent_file_skipped(self) -> None:
        """File modified within threshold is skipped."""
        recent = datetime.now() - timedelta(minutes=30)
        assert should_skip_recent(recent, skip_recent_hours=1) is True

    def test_old_file_not_skipped(self) -> None:
        """File modified outside threshold is not skipped."""
        old = datetime.now() - timedelta(hours=2)
        assert should_skip_recent(old, skip_recent_hours=1) is False

    def test_zero_hours_disables_check(self) -> None:
        """Skip recent hours of 0 disables the check."""
        recent = datetime.now()
        assert should_skip_recent(recent, skip_recent_hours=0) is False

    def test_negative_hours_disables_check(self) -> None:
        """Negative hours also disables the check."""
        recent = datetime.now()
        assert should_skip_recent(recent, skip_recent_hours=-1) is False


class TestDiscoverFiles:
    """Tests for discover_files function."""

    def test_discovers_regular_files(self, tmp_path: Path) -> None:
        """Discovers regular files in directory."""
        (tmp_path / "file1.txt").write_text("content")
        (tmp_path / "file2.pdf").write_text("content")

        files = list(discover_files(tmp_path))

        assert len(files) == 2
        names = {f.name for f in files}
        assert "file1.txt" in names
        assert "file2.pdf" in names

    def test_skips_directories(self, tmp_path: Path) -> None:
        """Directories are not yielded."""
        (tmp_path / "subdir").mkdir()
        (tmp_path / "file.txt").write_text("content")

        files = list(discover_files(tmp_path))

        assert len(files) == 1
        assert files[0].name == "file.txt"

    def test_skips_hidden_files_by_default(self, tmp_path: Path) -> None:
        """Hidden files (starting with .) are skipped by default."""
        (tmp_path / ".hidden").write_text("content")
        (tmp_path / "visible.txt").write_text("content")

        files = list(discover_files(tmp_path))

        assert len(files) == 1
        assert files[0].name == "visible.txt"

    def test_includes_hidden_when_disabled(self, tmp_path: Path) -> None:
        """Hidden files included when skip_hidden=False."""
        (tmp_path / ".hidden").write_text("content")
        (tmp_path / "visible.txt").write_text("content")

        files = list(discover_files(tmp_path, skip_hidden=False))

        assert len(files) == 2

    def test_skips_default_patterns(self, tmp_path: Path) -> None:
        """Default skip patterns are applied."""
        (tmp_path / ".DS_Store").write_text("content")
        (tmp_path / "download.crdownload").write_text("content")
        (tmp_path / "real_file.pdf").write_text("content")

        files = list(discover_files(tmp_path, skip_hidden=False))

        assert len(files) == 1
        assert files[0].name == "real_file.pdf"

    def test_skips_custom_patterns(self, tmp_path: Path) -> None:
        """Custom skip patterns are applied."""
        (tmp_path / "keep.txt").write_text("content")
        (tmp_path / "skip_me.log").write_text("content")

        files = list(discover_files(tmp_path, skip_patterns=["*.log"]))

        assert len(files) == 1
        assert files[0].name == "keep.txt"

    def test_limit_restricts_count(self, tmp_path: Path) -> None:
        """Limit parameter restricts number of files yielded."""
        for i in range(10):
            (tmp_path / f"file{i:02d}.txt").write_text("content")

        files = list(discover_files(tmp_path, limit=3))

        assert len(files) == 3

    def test_limit_none_returns_all(self, tmp_path: Path) -> None:
        """Limit=None returns all files."""
        for i in range(5):
            (tmp_path / f"file{i}.txt").write_text("content")

        files = list(discover_files(tmp_path, limit=None))

        assert len(files) == 5

    def test_skip_recent_hours(self, tmp_path: Path) -> None:
        """Files modified within skip_recent_hours are skipped."""
        # Create file and immediately check
        (tmp_path / "recent.txt").write_text("content")

        files = list(discover_files(tmp_path, skip_recent_hours=1))

        # File was just created, so should be skipped
        assert len(files) == 0

    def test_skip_recent_hours_zero_includes_all(self, tmp_path: Path) -> None:
        """skip_recent_hours=0 includes all files."""
        (tmp_path / "recent.txt").write_text("content")

        files = list(discover_files(tmp_path, skip_recent_hours=0))

        assert len(files) == 1

    def test_raises_for_non_directory(self, tmp_path: Path) -> None:
        """Raises ValueError if source is not a directory."""
        file_path = tmp_path / "not_a_dir.txt"
        file_path.write_text("content")

        with pytest.raises(ValueError, match="must be a directory"):
            list(discover_files(file_path))

    def test_returns_fileinfo_objects(self, tmp_path: Path) -> None:
        """Yielded objects are FileInfo instances."""
        (tmp_path / "test.txt").write_text("hello world")

        files = list(discover_files(tmp_path))

        assert len(files) == 1
        file = files[0]
        assert file.name == "test.txt"
        assert file.extension == "txt"
        assert file.size == 11
        assert isinstance(file.modified, datetime)

    def test_sorted_output(self, tmp_path: Path) -> None:
        """Files are yielded in sorted order."""
        (tmp_path / "zebra.txt").write_text("content")
        (tmp_path / "alpha.txt").write_text("content")
        (tmp_path / "beta.txt").write_text("content")

        files = list(discover_files(tmp_path))

        names = [f.name for f in files]
        assert names == ["alpha.txt", "beta.txt", "zebra.txt"]

    def test_handles_symlink_to_nonexistent(self, tmp_path: Path) -> None:
        """Broken symlinks are skipped without error."""
        good_file = tmp_path / "good.txt"
        good_file.write_text("content")

        # Create a broken symlink
        broken_link = tmp_path / "broken_link.txt"
        broken_link.symlink_to("/nonexistent/path/that/does/not/exist")

        files = list(discover_files(tmp_path))

        # Should only get the good file, broken symlink silently skipped
        assert len(files) == 1
        assert files[0].name == "good.txt"


class TestDefaultSkipPatterns:
    """Tests for default skip patterns."""

    def test_includes_ds_store(self) -> None:
        """DS_Store is in default patterns."""
        assert ".DS_Store" in DEFAULT_SKIP_PATTERNS

    def test_includes_partial_downloads(self) -> None:
        """Partial download patterns are included."""
        patterns_str = " ".join(DEFAULT_SKIP_PATTERNS)
        assert "crdownload" in patterns_str
        assert "part" in patterns_str

    def test_includes_temp_files(self) -> None:
        """Temp file patterns are included."""
        patterns_str = " ".join(DEFAULT_SKIP_PATTERNS)
        assert "tmp" in patterns_str
