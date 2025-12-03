"""Tests for ArchiveBookDetector."""

import pytest
import zipfile
from pathlib import Path

from tidyup.models import FileInfo
from tidyup.detectors.archive_book import ArchiveBookDetector
from tidyup.detectors.base import CONFIDENCE_HIGH, CONFIDENCE_MEDIUM


class TestArchiveBookDetector:
    """Tests for ArchiveBookDetector."""

    def test_ignores_non_archive(self, tmp_path: Path) -> None:
        """Ignores non-archive files."""
        detector = ArchiveBookDetector()
        file_path = tmp_path / "book.txt"
        file_path.write_text("Some text content")
        file = FileInfo.from_path(file_path)

        result = detector.detect(file)

        assert result is None

    def test_detects_zip_with_epub(self, tmp_path: Path) -> None:
        """Detects ZIP containing EPUB file."""
        detector = ArchiveBookDetector()
        zip_path = tmp_path / "books.zip"

        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("book.epub", b"epub content")

        file = FileInfo.from_path(zip_path)
        result = detector.detect(file)

        assert result is not None
        assert result.category == "Books"
        assert result.confidence == CONFIDENCE_HIGH
        assert "epub" in result.reason.lower()

    def test_detects_zip_with_pdf(self, tmp_path: Path) -> None:
        """Detects ZIP containing PDF file."""
        detector = ArchiveBookDetector()
        zip_path = tmp_path / "document.zip"

        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("book.pdf", b"%PDF-1.4")

        file = FileInfo.from_path(zip_path)
        result = detector.detect(file)

        assert result is not None
        assert result.category == "Books"
        assert result.confidence == CONFIDENCE_HIGH

    def test_detects_zip_with_mobi(self, tmp_path: Path) -> None:
        """Detects ZIP containing MOBI file."""
        detector = ArchiveBookDetector()
        zip_path = tmp_path / "ebook.zip"

        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("book.mobi", b"mobi content")

        file = FileInfo.from_path(zip_path)
        result = detector.detect(file)

        assert result is not None
        assert result.category == "Books"

    def test_detects_multiple_book_files(self, tmp_path: Path) -> None:
        """Detects ZIP with multiple book files."""
        detector = ArchiveBookDetector()
        zip_path = tmp_path / "books.zip"

        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("book1.epub", b"epub1")
            zf.writestr("book2.pdf", b"%PDF-1.4")
            zf.writestr("book3.mobi", b"mobi")

        file = FileInfo.from_path(zip_path)
        result = detector.detect(file)

        assert result is not None
        assert result.category == "Books"
        assert "3" in result.reason

    def test_ignores_zip_without_books(self, tmp_path: Path) -> None:
        """Ignores ZIP without book files."""
        detector = ArchiveBookDetector()
        zip_path = tmp_path / "files.zip"

        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("image.jpg", b"jpg data")
            zf.writestr("doc.txt", b"text content")

        file = FileInfo.from_path(zip_path)
        result = detector.detect(file)

        assert result is None

    def test_detects_rar_with_book_keywords(self, tmp_path: Path) -> None:
        """Detects RAR with book keywords in filename."""
        detector = ArchiveBookDetector()

        # Can't inspect RAR content, but filename has "Edition" (strong indicator)
        file_path = tmp_path / "Python Programming Guide 3rd Edition.rar"
        file_path.write_bytes(b"rar content")
        file = FileInfo.from_path(file_path)

        result = detector.detect(file)

        assert result is not None
        assert result.category == "Books"
        assert result.confidence == CONFIDENCE_HIGH  # "Edition" is strong indicator

    def test_detects_7z_with_book_keywords(self, tmp_path: Path) -> None:
        """Detects 7z with book keywords in filename."""
        detector = ArchiveBookDetector()

        file_path = tmp_path / "Complete Introduction to Machine Learning.7z"
        file_path.write_bytes(b"7z content")
        file = FileInfo.from_path(file_path)

        result = detector.detect(file)

        assert result is not None
        assert result.category == "Books"

    def test_ignores_archive_without_book_keywords(self, tmp_path: Path) -> None:
        """Ignores archives without book-related keywords."""
        detector = ArchiveBookDetector()

        file_path = tmp_path / "project_backup_2024.rar"
        file_path.write_bytes(b"rar content")
        file = FileInfo.from_path(file_path)

        result = detector.detect(file)

        assert result is None

    def test_handles_corrupt_zip(self, tmp_path: Path) -> None:
        """Handles corrupt ZIP files gracefully."""
        detector = ArchiveBookDetector()

        # Create an invalid ZIP file
        file_path = tmp_path / "corrupt.zip"
        file_path.write_bytes(b"not a real zip file")
        file = FileInfo.from_path(file_path)

        result = detector.detect(file)

        # Should not crash, may return None or filename-based detection
        assert result is None or result.category == "Books"

    def test_detects_nested_book_in_subdirectory(self, tmp_path: Path) -> None:
        """Detects book files in subdirectories of ZIP."""
        detector = ArchiveBookDetector()
        zip_path = tmp_path / "archive.zip"

        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("folder/subfolder/book.epub", b"epub content")

        file = FileInfo.from_path(zip_path)
        result = detector.detect(file)

        assert result is not None
        assert result.category == "Books"

    def test_priority_is_set(self) -> None:
        """Detector has correct priority."""
        detector = ArchiveBookDetector()
        assert detector.priority == 18

    def test_name_property(self) -> None:
        """Name property returns correct value."""
        detector = ArchiveBookDetector()
        assert detector.name == "ArchiveBookDetector"

    def test_detects_cookbook_keyword(self, tmp_path: Path) -> None:
        """Detects archives with book keywords in filename."""
        detector = ArchiveBookDetector()

        # Need at least 2 book keywords for detection
        file_path = tmp_path / "Python Cookbook Practical Guide.rar"
        file_path.write_bytes(b"rar content")
        file = FileInfo.from_path(file_path)

        result = detector.detect(file)

        assert result is not None

    def test_detects_handbook_keyword(self, tmp_path: Path) -> None:
        """Detects archives with 'handbook' in filename."""
        detector = ArchiveBookDetector()

        file_path = tmp_path / "Developer Handbook 2024 Edition.7z"
        file_path.write_bytes(b"7z content")
        file = FileInfo.from_path(file_path)

        result = detector.detect(file)

        assert result is not None

    def test_detects_study_guide_rar(self, tmp_path: Path) -> None:
        """Detects RAR with 'Study Guide' in filename."""
        detector = ArchiveBookDetector()

        file_path = tmp_path / "Tableau Certified Data Analyst Study Guide.rar"
        file_path.write_bytes(b"rar content")
        file = FileInfo.from_path(file_path)

        result = detector.detect(file)

        assert result is not None
        assert result.category == "Books"
        # "study", "guide", "certified", "analyst" = 4 moderate keywords
        assert result.confidence == CONFIDENCE_MEDIUM

    def test_detects_introducing_edition_rar(self, tmp_path: Path) -> None:
        """Detects RAR with 'Introducing' and 'Edition' in filename."""
        detector = ArchiveBookDetector()

        file_path = tmp_path / "Introducing Python 3rd Edition.rar"
        file_path.write_bytes(b"rar content")
        file = FileInfo.from_path(file_path)

        result = detector.detect(file)

        assert result is not None
        assert result.category == "Books"
        assert result.confidence == CONFIDENCE_HIGH  # "Edition" is strong
