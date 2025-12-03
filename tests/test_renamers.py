"""Tests for renamer framework and renamers."""

import pytest
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, MagicMock

from tidyup.models import FileInfo, DetectionResult
from tidyup.renamers import (
    BaseRenamer,
    RenamerRegistry,
    get_renamer_registry,
    format_date,
    format_datetime,
)
from tidyup.renamers.generic import GenericRenamer
from tidyup.renamers.screenshot import ScreenshotRenamer, extract_screenshot_datetime
from tidyup.renamers.arxiv import ArxivRenamer
from tidyup.renamers.pdf import PDFRenamer
from tidyup.renamers.invoice import InvoiceRenamer


class TestFormatFunctions:
    """Tests for date formatting functions."""

    def test_format_date(self) -> None:
        """Formats date as YYYY-MM-DD."""
        dt = datetime(2024, 1, 15, 10, 30, 45)
        assert format_date(dt) == "2024-01-15"

    def test_format_datetime(self) -> None:
        """Formats datetime as YYYY-MM-DD_HH-MM-SS."""
        dt = datetime(2024, 1, 15, 10, 30, 45)
        assert format_datetime(dt) == "2024-01-15_10-30-45"


class TestRenamerRegistry:
    """Tests for RenamerRegistry."""

    def test_register_renamer(self) -> None:
        """Can register a renamer."""
        registry = RenamerRegistry()
        renamer = GenericRenamer()

        registry.register("TestDetector", renamer)

        assert "TestDetector" in registry.renamers

    def test_set_default(self) -> None:
        """Can set default renamer."""
        registry = RenamerRegistry()
        renamer = GenericRenamer()

        registry.set_default(renamer)

        assert registry.default_renamer == renamer

    def test_uses_specialized_renamer(self, tmp_path: Path) -> None:
        """Uses specialized renamer when available."""
        registry = RenamerRegistry()
        registry.register("ScreenshotDetector", ScreenshotRenamer())
        registry.set_default(GenericRenamer())

        file_path = tmp_path / "Screenshot 2024-01-15 at 10.30.45.png"
        file_path.write_bytes(b"content")
        file = FileInfo.from_path(file_path)

        detection = DetectionResult(
            category="02_Images",
            confidence=0.9,
            detector_name="ScreenshotDetector",
        )

        result = registry.rename(file, detection)

        assert result is not None
        assert result.renamer_name == "ScreenshotRenamer"

    def test_falls_back_to_default(self, tmp_path: Path) -> None:
        """Falls back to default renamer."""
        registry = RenamerRegistry()
        registry.set_default(GenericRenamer())

        file_path = tmp_path / "1234567890123.txt"
        file_path.write_text("content")
        file = FileInfo.from_path(file_path)

        detection = DetectionResult(
            category="01_Documents",
            confidence=0.7,
            detector_name="UnknownDetector",
        )

        result = registry.rename(file, detection)

        assert result is not None
        assert result.renamer_name == "GenericRenamer"


class TestGenericRenamer:
    """Tests for GenericRenamer."""

    def test_renames_ugly_filename(self, tmp_path: Path) -> None:
        """Renames files with ugly names."""
        renamer = GenericRenamer()
        file_path = tmp_path / "1234567890123.pdf"
        file_path.write_text("content")
        file = FileInfo.from_path(file_path)

        detection = DetectionResult(
            category="01_Documents",
            confidence=0.7,
            detector_name="GenericDetector",
        )

        result = renamer.rename(file, detection)

        assert result is not None
        assert result.new_name.endswith(".pdf")
        assert result.new_name != file.name

    def test_keeps_nice_filename(self, tmp_path: Path) -> None:
        """Keeps files with nice names."""
        renamer = GenericRenamer()
        file_path = tmp_path / "Annual_Report_2024.pdf"
        file_path.write_text("content")
        file = FileInfo.from_path(file_path)

        detection = DetectionResult(
            category="01_Documents",
            confidence=0.7,
            detector_name="GenericDetector",
        )

        result = renamer.rename(file, detection)

        assert result is None


class TestScreenshotRenamer:
    """Tests for ScreenshotRenamer."""

    def test_extracts_macos_datetime(self) -> None:
        """Extracts datetime from macOS screenshot."""
        dt = extract_screenshot_datetime("Screenshot 2024-01-15 at 10.30.45.png")
        assert dt is not None
        assert dt.year == 2024
        assert dt.month == 1
        assert dt.day == 15
        assert dt.hour == 10
        assert dt.minute == 30

    def test_extracts_macos_am_pm(self) -> None:
        """Handles AM/PM in macOS screenshots."""
        dt = extract_screenshot_datetime("Screen Shot 2024-01-15 at 2.30.45 PM.png")
        assert dt is not None
        assert dt.hour == 14

    def test_extracts_cleanshot_datetime(self) -> None:
        """Extracts datetime from CleanShot."""
        dt = extract_screenshot_datetime("CleanShot 2024-01-15 at 10.30.45.png")
        assert dt is not None

    def test_standardizes_screenshot_name(self, tmp_path: Path) -> None:
        """Standardizes screenshot filename."""
        renamer = ScreenshotRenamer()
        file_path = tmp_path / "Screenshot 2024-01-15 at 10.30.45.png"
        file_path.write_bytes(b"content")
        file = FileInfo.from_path(file_path)

        detection = DetectionResult(
            category="02_Images",
            confidence=0.9,
            detector_name="ScreenshotDetector",
        )

        result = renamer.rename(file, detection)

        assert result is not None
        assert result.new_name == "Screenshot_2024-01-15_10-30-45.png"

    def test_ignores_non_screenshots(self, tmp_path: Path) -> None:
        """Ignores files not detected as screenshots."""
        renamer = ScreenshotRenamer()
        file_path = tmp_path / "photo.png"
        file_path.write_bytes(b"content")
        file = FileInfo.from_path(file_path)

        detection = DetectionResult(
            category="02_Images",
            confidence=0.9,
            detector_name="GenericDetector",
        )

        result = renamer.rename(file, detection)

        assert result is None


class TestArxivRenamer:
    """Tests for ArxivRenamer."""

    def test_adds_date_to_arxiv(self, tmp_path: Path) -> None:
        """Adds date prefix to arXiv papers."""
        renamer = ArxivRenamer()
        file_path = tmp_path / "2501.12948.pdf"
        file_path.write_text("content")
        file = FileInfo.from_path(file_path)

        detection = DetectionResult(
            category="01_Documents",
            confidence=0.9,
            detector_name="ArxivDetector",
        )

        result = renamer.rename(file, detection)

        assert result is not None
        assert "2501.12948" in result.new_name
        assert result.new_name.startswith("20")  # Date prefix

    def test_keeps_version(self, tmp_path: Path) -> None:
        """Keeps version number in arXiv ID."""
        renamer = ArxivRenamer()
        file_path = tmp_path / "2501.12948v2.pdf"
        file_path.write_text("content")
        file = FileInfo.from_path(file_path)

        detection = DetectionResult(
            category="01_Documents",
            confidence=0.9,
            detector_name="ArxivDetector",
        )

        result = renamer.rename(file, detection)

        assert result is not None
        assert "2501.12948v2" in result.new_name


class TestPDFRenamer:
    """Tests for PDFRenamer."""

    def test_ignores_non_pdf(self, tmp_path: Path) -> None:
        """Ignores non-PDF files."""
        renamer = PDFRenamer()
        file_path = tmp_path / "1234567890.txt"
        file_path.write_text("content")
        file = FileInfo.from_path(file_path)

        detection = DetectionResult(
            category="01_Documents",
            confidence=0.7,
            detector_name="GenericDetector",
        )

        result = renamer.rename(file, detection)

        assert result is None

    @patch("tidyup.renamers.pdf.extract_pdf_metadata")
    def test_uses_metadata_title(self, mock_extract: MagicMock, tmp_path: Path) -> None:
        """Uses title from PDF metadata."""
        mock_extract.return_value = ("My Document Title", None)

        renamer = PDFRenamer()
        file_path = tmp_path / "1234567890.pdf"
        file_path.write_text("content")
        file = FileInfo.from_path(file_path)

        detection = DetectionResult(
            category="01_Documents",
            confidence=0.7,
            detector_name="GenericDetector",
        )

        result = renamer.rename(file, detection)

        assert result is not None
        assert "My Document Title" in result.new_name or "My_Document_Title" in result.new_name


class TestInvoiceRenamer:
    """Tests for InvoiceRenamer."""

    def test_ignores_non_invoices(self, tmp_path: Path) -> None:
        """Ignores files not detected as invoices."""
        renamer = InvoiceRenamer()
        file_path = tmp_path / "document.pdf"
        file_path.write_text("content")
        file = FileInfo.from_path(file_path)

        detection = DetectionResult(
            category="01_Documents",
            confidence=0.7,
            detector_name="GenericDetector",
        )

        result = renamer.rename(file, detection)

        assert result is None

    @patch("tidyup.renamers.invoice.extract_pdf_text_cached")
    def test_extracts_vendor(self, mock_extract: MagicMock, tmp_path: Path) -> None:
        """Extracts vendor name from invoice."""
        mock_extract.return_value = "Invoice from Acme Corp\nTotal: $100"

        renamer = InvoiceRenamer()
        file_path = tmp_path / "invoice123.pdf"
        file_path.write_text("content")
        file = FileInfo.from_path(file_path)

        detection = DetectionResult(
            category="01_Documents",
            confidence=0.9,
            detector_name="InvoiceDetector",
        )

        result = renamer.rename(file, detection)

        assert result is not None
        assert "Invoice" in result.new_name
        assert "Acme" in result.new_name


class TestGlobalRegistry:
    """Tests for global registry."""

    def test_get_registry_returns_registry(self) -> None:
        """get_renamer_registry returns a RenamerRegistry."""
        registry = get_renamer_registry()

        assert isinstance(registry, RenamerRegistry)

    def test_registry_has_default_renamer(self) -> None:
        """Global registry has default renamer."""
        registry = get_renamer_registry()

        assert registry.default_renamer is not None

    def test_registry_has_specialized_renamers(self) -> None:
        """Global registry has specialized renamers registered."""
        registry = get_renamer_registry()

        assert "ScreenshotDetector" in registry.renamers
        assert "ArxivDetector" in registry.renamers
        assert "InvoiceDetector" in registry.renamers
