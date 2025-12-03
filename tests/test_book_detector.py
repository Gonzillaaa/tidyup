"""Tests for BookDetector."""

import pytest
from pathlib import Path
from unittest.mock import patch

from tidyup.models import FileInfo
from tidyup.detectors.book import BookDetector
from tidyup.detectors.base import CONFIDENCE_HIGH, CONFIDENCE_MEDIUM


class TestBookDetector:
    """Tests for BookDetector."""

    def test_detects_epub(self, tmp_path: Path) -> None:
        """Detects epub files as books."""
        detector = BookDetector()
        file_path = tmp_path / "book.epub"
        file_path.write_bytes(b"epub content")
        file = FileInfo.from_path(file_path)

        result = detector.detect(file)

        assert result is not None
        assert result.category == "Books"
        assert result.confidence == CONFIDENCE_HIGH

    def test_detects_mobi(self, tmp_path: Path) -> None:
        """Detects mobi files as books."""
        detector = BookDetector()
        file_path = tmp_path / "book.mobi"
        file_path.write_bytes(b"mobi content")
        file = FileInfo.from_path(file_path)

        result = detector.detect(file)

        assert result is not None
        assert result.category == "Books"

    def test_detects_azw3(self, tmp_path: Path) -> None:
        """Detects azw3 files as books."""
        detector = BookDetector()
        file_path = tmp_path / "book.azw3"
        file_path.write_bytes(b"kindle content")
        file = FileInfo.from_path(file_path)

        result = detector.detect(file)

        assert result is not None
        assert result.category == "Books"

    def test_ignores_non_book_extensions(self, tmp_path: Path) -> None:
        """Ignores files with non-book extensions."""
        detector = BookDetector()
        file_path = tmp_path / "document.txt"
        file_path.write_text("some text")
        file = FileInfo.from_path(file_path)

        result = detector.detect(file)

        assert result is None

    @patch("tidyup.detectors.book.extract_pdf_text_cached")
    def test_returns_none_when_pdf_has_no_text(
        self, mock_extract: patch, tmp_path: Path
    ) -> None:
        """Returns None when PDF has no extractable text."""
        mock_extract.return_value = None
        detector = BookDetector()

        file_path = tmp_path / "scan.pdf"
        file_path.write_bytes(b"%PDF-1.4")
        file = FileInfo.from_path(file_path)

        result = detector.detect(file)

        assert result is None

    @patch("tidyup.detectors.book.extract_pdf_text_cached")
    def test_detects_isbn_10(self, mock_extract: patch, tmp_path: Path) -> None:
        """Detects books by ISBN-10."""
        mock_extract.return_value = """
        Programming in Python
        ISBN 0-13-110362-8
        First Edition
        """
        detector = BookDetector()

        file_path = tmp_path / "book.pdf"
        file_path.write_bytes(b"%PDF-1.4")
        file = FileInfo.from_path(file_path)

        result = detector.detect(file)

        assert result is not None
        assert result.confidence == CONFIDENCE_HIGH
        assert "ISBN" in result.reason

    @patch("tidyup.detectors.book.extract_pdf_text_cached")
    def test_detects_isbn_13(self, mock_extract: patch, tmp_path: Path) -> None:
        """Detects books by ISBN-13."""
        mock_extract.return_value = """
        Advanced Python Programming
        ISBN 978-0-13-110362-7
        """
        detector = BookDetector()

        file_path = tmp_path / "book.pdf"
        file_path.write_bytes(b"%PDF-1.4")
        file = FileInfo.from_path(file_path)

        result = detector.detect(file)

        assert result is not None
        assert result.confidence == CONFIDENCE_HIGH

    @patch("tidyup.detectors.book.extract_pdf_text_cached")
    def test_detects_multiple_book_keywords(
        self, mock_extract: patch, tmp_path: Path
    ) -> None:
        """Detects books with multiple keywords."""
        mock_extract.return_value = """
        Table of Contents

        Preface
        Chapter 1: Introduction
        Chapter 2: Getting Started
        Appendix A: References
        Bibliography
        """
        detector = BookDetector()

        file_path = tmp_path / "book.pdf"
        file_path.write_bytes(b"%PDF-1.4")
        file = FileInfo.from_path(file_path)

        result = detector.detect(file)

        assert result is not None
        assert result.confidence == CONFIDENCE_HIGH

    @patch("tidyup.detectors.book.extract_pdf_text_cached")
    def test_detects_some_book_keywords_medium_confidence(
        self, mock_extract: patch, tmp_path: Path
    ) -> None:
        """Some keywords give medium confidence."""
        mock_extract.return_value = """
        Chapter 1: Introduction

        This is a preface to the document.
        """
        detector = BookDetector()

        file_path = tmp_path / "book.pdf"
        file_path.write_bytes(b"%PDF-1.4")
        file = FileInfo.from_path(file_path)

        result = detector.detect(file)

        assert result is not None
        assert result.confidence == CONFIDENCE_MEDIUM

    @patch("tidyup.detectors.book.extract_pdf_text_cached")
    def test_detects_copyright_notice(
        self, mock_extract: patch, tmp_path: Path
    ) -> None:
        """Detects books by copyright notice."""
        mock_extract.return_value = """
        Copyright © 2024 Author Name
        All Rights Reserved
        Published by Publisher Inc.
        Chapter 1: Beginning
        """
        detector = BookDetector()

        file_path = tmp_path / "book.pdf"
        file_path.write_bytes(b"%PDF-1.4")
        file = FileInfo.from_path(file_path)

        result = detector.detect(file)

        assert result is not None

    @patch("tidyup.detectors.book.extract_pdf_text_cached")
    def test_detects_edition_keyword(
        self, mock_extract: patch, tmp_path: Path
    ) -> None:
        """Detects books by edition keyword."""
        mock_extract.return_value = """
        Python Programming
        Third Edition
        Preface
        """
        detector = BookDetector()

        file_path = tmp_path / "book.pdf"
        file_path.write_bytes(b"%PDF-1.4")
        file = FileInfo.from_path(file_path)

        result = detector.detect(file)

        assert result is not None

    @patch("tidyup.detectors.book.extract_pdf_text_cached")
    def test_ignores_pdf_without_book_keywords(
        self, mock_extract: patch, tmp_path: Path
    ) -> None:
        """Ignores PDFs that don't have book indicators."""
        mock_extract.return_value = """
        Meeting Notes
        January 15, 2024

        Attendees:
        - Alice
        - Bob

        Action Items:
        1. Review the proposal
        2. Send follow-up email
        """
        detector = BookDetector()

        file_path = tmp_path / "notes.pdf"
        file_path.write_bytes(b"%PDF-1.4")
        file = FileInfo.from_path(file_path)

        result = detector.detect(file)

        assert result is None

    def test_priority_is_set(self) -> None:
        """Detector has correct priority."""
        detector = BookDetector()
        assert detector.priority == 20

    def test_name_property(self) -> None:
        """Name property returns correct value."""
        detector = BookDetector()
        assert detector.name == "BookDetector"
