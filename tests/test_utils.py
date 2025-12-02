"""Tests for utility functions."""

import pytest
from pathlib import Path
from datetime import datetime

from tidy.utils import (
    sanitize_filename,
    format_size,
    compute_file_hash,
    get_file_dates,
    generate_unique_path,
    is_ugly_filename,
    format_date,
    format_datetime,
)


class TestSanitizeFilename:
    """Tests for sanitize_filename function."""

    def test_removes_forbidden_characters(self) -> None:
        """Forbidden characters are removed/replaced."""
        result = sanitize_filename('file/with\\bad:chars*?"<>|')
        # Forbidden chars should not be in result
        assert "/" not in result
        assert "\\" not in result
        assert ":" not in result
        assert "*" not in result
        assert "?" not in result
        assert '"' not in result
        assert "<" not in result
        assert ">" not in result
        assert "|" not in result

    def test_collapses_whitespace(self) -> None:
        """Multiple spaces are collapsed to single space."""
        assert sanitize_filename("too   many    spaces") == "too many spaces"

    def test_removes_leading_dots(self) -> None:
        """Leading dots are removed (hidden files)."""
        assert sanitize_filename(".hidden") == "hidden"
        assert sanitize_filename("...dots") == "dots"

    def test_truncates_long_names(self) -> None:
        """Long filenames are truncated."""
        long_name = "a" * 300
        result = sanitize_filename(long_name, max_length=200)
        assert len(result) <= 200

    def test_handles_empty_string(self) -> None:
        """Empty string returns 'unnamed'."""
        assert sanitize_filename("") == "unnamed"

    def test_handles_only_forbidden_chars(self) -> None:
        """String with only forbidden chars returns 'unnamed'."""
        assert sanitize_filename("///") == "unnamed"

    def test_preserves_unicode(self) -> None:
        """Unicode characters are preserved (normalized)."""
        result = sanitize_filename("日本語ファイル")
        assert "日本語" in result


class TestFormatSize:
    """Tests for format_size function."""

    def test_bytes(self) -> None:
        """Small sizes shown in bytes."""
        assert format_size(0) == "0 B"
        assert format_size(512) == "512 B"
        assert format_size(1023) == "1023 B"

    def test_kilobytes(self) -> None:
        """KB range sizes."""
        assert format_size(1024) == "1.0 KB"
        assert format_size(1536) == "1.5 KB"

    def test_megabytes(self) -> None:
        """MB range sizes."""
        assert format_size(1024 * 1024) == "1.0 MB"
        assert format_size(1024 * 1024 * 2.5) == "2.5 MB"

    def test_gigabytes(self) -> None:
        """GB range sizes."""
        assert format_size(1024 * 1024 * 1024) == "1.0 GB"

    def test_negative_returns_zero(self) -> None:
        """Negative values return 0 B."""
        assert format_size(-100) == "0 B"


class TestComputeFileHash:
    """Tests for compute_file_hash function."""

    def test_computes_hash(self, tmp_path: Path) -> None:
        """Computes correct hash for file content."""
        file = tmp_path / "test.txt"
        file.write_text("hello world")

        hash_result = compute_file_hash(file)

        assert len(hash_result) == 64  # SHA-256 hex length
        assert hash_result.isalnum()

    def test_same_content_same_hash(self, tmp_path: Path) -> None:
        """Same content produces same hash."""
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        file1.write_text("identical content")
        file2.write_text("identical content")

        assert compute_file_hash(file1) == compute_file_hash(file2)

    def test_different_content_different_hash(self, tmp_path: Path) -> None:
        """Different content produces different hash."""
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        file1.write_text("content one")
        file2.write_text("content two")

        assert compute_file_hash(file1) != compute_file_hash(file2)

    def test_supports_md5(self, tmp_path: Path) -> None:
        """Supports MD5 algorithm."""
        file = tmp_path / "test.txt"
        file.write_text("test")

        hash_result = compute_file_hash(file, algorithm="md5")

        assert len(hash_result) == 32  # MD5 hex length


class TestGetFileDates:
    """Tests for get_file_dates function."""

    def test_returns_datetime_tuple(self, tmp_path: Path) -> None:
        """Returns tuple of datetime objects."""
        file = tmp_path / "test.txt"
        file.write_text("content")

        created, modified = get_file_dates(file)

        assert isinstance(created, datetime)
        assert isinstance(modified, datetime)


class TestGenerateUniquePath:
    """Tests for generate_unique_path function."""

    def test_returns_same_path_if_not_exists(self, tmp_path: Path) -> None:
        """Returns original path if it doesn't exist."""
        path = tmp_path / "newfile.txt"

        result = generate_unique_path(path)

        assert result == path

    def test_adds_suffix_if_exists(self, tmp_path: Path) -> None:
        """Adds (1) suffix if file exists."""
        path = tmp_path / "existing.txt"
        path.write_text("original")

        result = generate_unique_path(path)

        assert result == tmp_path / "existing (1).txt"

    def test_increments_suffix(self, tmp_path: Path) -> None:
        """Increments suffix if (1) also exists."""
        path = tmp_path / "file.txt"
        path.write_text("original")
        (tmp_path / "file (1).txt").write_text("copy1")
        (tmp_path / "file (2).txt").write_text("copy2")

        result = generate_unique_path(path)

        assert result == tmp_path / "file (3).txt"

    def test_preserves_extension(self, tmp_path: Path) -> None:
        """Preserves file extension in new name."""
        path = tmp_path / "document.pdf"
        path.write_bytes(b"pdf content")

        result = generate_unique_path(path)

        assert result.suffix == ".pdf"


class TestIsUglyFilename:
    """Tests for is_ugly_filename function."""

    def test_detects_timestamp_names(self) -> None:
        """Detects timestamp-based filenames."""
        assert is_ugly_filename("1743151465964") is True
        assert is_ugly_filename("20240115143052") is True

    def test_detects_uuid_names(self) -> None:
        """Detects UUID filenames."""
        assert is_ugly_filename("07-05711b687f-fa1b-4a37-bbb6-cf4383aa64de") is True
        assert is_ugly_filename("a1b2c3d4-e5f6-7890-abcd-ef1234567890") is True

    def test_detects_hex_strings(self) -> None:
        """Detects long hex string filenames."""
        assert is_ugly_filename("a1b2c3d4e5f6789012345678") is True

    def test_accepts_readable_names(self) -> None:
        """Accepts human-readable filenames."""
        assert is_ugly_filename("Annual_Report_2024") is False
        assert is_ugly_filename("meeting-notes") is False
        assert is_ugly_filename("photo from vacation") is False

    def test_empty_string_is_ugly(self) -> None:
        """Empty string is considered ugly."""
        assert is_ugly_filename("") is True


class TestFormatDate:
    """Tests for date formatting functions."""

    def test_format_date_iso(self) -> None:
        """format_date produces ISO format."""
        dt = datetime(2024, 1, 15, 14, 30, 45)
        assert format_date(dt) == "2024-01-15"

    def test_format_datetime_with_time(self) -> None:
        """format_datetime includes time."""
        dt = datetime(2024, 1, 15, 14, 30, 45)
        assert format_datetime(dt) == "2024-01-15_14-30-45"
