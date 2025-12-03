"""Tests for detector framework and detectors."""

import pytest
from pathlib import Path

from tidyup.models import FileInfo
from tidyup.detectors import (
    BaseDetector,
    DetectorRegistry,
    CONFIDENCE_HIGH,
    CONFIDENCE_MEDIUM,
    CONFIDENCE_LOW,
    get_registry,
)
from tidyup.detectors.base import BaseDetector
from tidyup.detectors.generic import GenericDetector, EXTENSION_MAP
from tidyup.detectors.screenshot import ScreenshotDetector
from tidyup.detectors.arxiv import ArxivDetector


class TestBaseDetector:
    """Tests for BaseDetector constants."""

    def test_confidence_levels_ordered(self) -> None:
        """Confidence levels are properly ordered."""
        assert CONFIDENCE_HIGH > CONFIDENCE_MEDIUM > CONFIDENCE_LOW

    def test_confidence_levels_valid(self) -> None:
        """Confidence levels are between 0 and 1."""
        assert 0.0 <= CONFIDENCE_LOW <= 1.0
        assert 0.0 <= CONFIDENCE_MEDIUM <= 1.0
        assert 0.0 <= CONFIDENCE_HIGH <= 1.0


class TestDetectorRegistry:
    """Tests for DetectorRegistry."""

    def test_register_detector(self) -> None:
        """Can register a detector."""
        registry = DetectorRegistry()
        detector = GenericDetector()

        registry.register(detector)

        assert len(registry.detectors) == 1

    def test_detectors_sorted_by_priority(self) -> None:
        """Detectors are sorted by priority."""
        registry = DetectorRegistry()
        generic = GenericDetector()  # priority=50
        screenshot = ScreenshotDetector()  # priority=10

        registry.register(generic)
        registry.register(screenshot)

        # Screenshot should come first (lower priority number)
        assert registry.detectors[0].priority < registry.detectors[1].priority

    def test_detect_returns_best_result(self, tmp_path: Path) -> None:
        """detect() returns highest confidence result."""
        registry = DetectorRegistry()
        registry.register(GenericDetector())

        file_path = tmp_path / "test.pdf"
        file_path.write_text("content")
        file = FileInfo.from_path(file_path)

        result = registry.detect(file)

        assert result.category == "Documents"
        assert result.confidence == CONFIDENCE_MEDIUM

    def test_detect_returns_unsorted_when_no_match(self, tmp_path: Path) -> None:
        """detect() returns Unsorted when no detector matches."""
        registry = DetectorRegistry()
        # Empty registry - no detectors

        file_path = tmp_path / "test.xyz"
        file_path.write_text("content")
        file = FileInfo.from_path(file_path)

        result = registry.detect(file)

        assert result.category == "Unsorted"
        assert result.confidence == 0.0

    def test_priority_breaks_ties(self, tmp_path: Path) -> None:
        """Lower priority wins when confidence is equal."""
        registry = DetectorRegistry()
        registry.register(ScreenshotDetector())  # priority=10
        registry.register(GenericDetector())  # priority=50

        # Screenshot that also matches as image
        file_path = tmp_path / "Screenshot 2024-01-15 at 10.30.45.png"
        file_path.write_text("content")
        file = FileInfo.from_path(file_path)

        result = registry.detect(file)

        # Screenshot detector should win (same confidence, lower priority)
        assert result.detector_name == "ScreenshotDetector"


class TestGenericDetector:
    """Tests for GenericDetector."""

    def test_detects_pdf_as_documents(self, tmp_path: Path) -> None:
        """PDF files detected as Documents."""
        detector = GenericDetector()
        file_path = tmp_path / "report.pdf"
        file_path.write_text("content")
        file = FileInfo.from_path(file_path)

        result = detector.detect(file)

        assert result.category == "Documents"
        assert result.confidence == CONFIDENCE_MEDIUM

    def test_detects_images(self, tmp_path: Path) -> None:
        """Image files detected as Images."""
        detector = GenericDetector()

        for ext in ["jpg", "png", "gif", "heic"]:
            file_path = tmp_path / f"photo.{ext}"
            file_path.write_bytes(b"content")
            file = FileInfo.from_path(file_path)

            result = detector.detect(file)

            assert result.category == "Images", f"Failed for .{ext}"

    def test_detects_videos(self, tmp_path: Path) -> None:
        """Video files detected as Videos."""
        detector = GenericDetector()

        for ext in ["mp4", "mov", "mkv"]:
            file_path = tmp_path / f"video.{ext}"
            file_path.write_bytes(b"content")
            file = FileInfo.from_path(file_path)

            result = detector.detect(file)

            assert result.category == "Videos", f"Failed for .{ext}"

    def test_detects_audio(self, tmp_path: Path) -> None:
        """Audio files detected as Audio."""
        detector = GenericDetector()

        for ext in ["mp3", "wav", "flac"]:
            file_path = tmp_path / f"audio.{ext}"
            file_path.write_bytes(b"content")
            file = FileInfo.from_path(file_path)

            result = detector.detect(file)

            assert result.category == "Audio", f"Failed for .{ext}"

    def test_detects_archives(self, tmp_path: Path) -> None:
        """Archive files detected as Archives."""
        detector = GenericDetector()

        for ext in ["zip", "rar", "7z", "tar"]:
            file_path = tmp_path / f"archive.{ext}"
            file_path.write_bytes(b"content")
            file = FileInfo.from_path(file_path)

            result = detector.detect(file)

            assert result.category == "Archives", f"Failed for .{ext}"

    def test_detects_code(self, tmp_path: Path) -> None:
        """Code files detected as Code."""
        detector = GenericDetector()

        for ext in ["py", "js", "go", "rs"]:
            file_path = tmp_path / f"code.{ext}"
            file_path.write_text("content")
            file = FileInfo.from_path(file_path)

            result = detector.detect(file)

            assert result.category == "Code", f"Failed for .{ext}"

    def test_detects_books(self, tmp_path: Path) -> None:
        """Book files detected as Books."""
        detector = GenericDetector()

        for ext in ["epub", "mobi", "azw3"]:
            file_path = tmp_path / f"book.{ext}"
            file_path.write_bytes(b"content")
            file = FileInfo.from_path(file_path)

            result = detector.detect(file)

            assert result.category == "Books", f"Failed for .{ext}"

    def test_detects_data(self, tmp_path: Path) -> None:
        """Data files detected as Data."""
        detector = GenericDetector()

        for ext in ["csv", "json", "sql"]:
            file_path = tmp_path / f"data.{ext}"
            file_path.write_text("content")
            file = FileInfo.from_path(file_path)

            result = detector.detect(file)

            assert result.category == "Data", f"Failed for .{ext}"

    def test_unknown_extension_is_unsorted(self, tmp_path: Path) -> None:
        """Unknown extensions go to Unsorted with low confidence."""
        detector = GenericDetector()
        file_path = tmp_path / "unknown.xyz123"
        file_path.write_text("content")
        file = FileInfo.from_path(file_path)

        result = detector.detect(file)

        assert result.category == "Unsorted"
        assert result.confidence < CONFIDENCE_MEDIUM
        assert result.reason is not None

    def test_case_insensitive(self, tmp_path: Path) -> None:
        """Extension matching is case-insensitive."""
        detector = GenericDetector()
        file_path = tmp_path / "photo.PNG"
        file_path.write_bytes(b"content")
        file = FileInfo.from_path(file_path)

        result = detector.detect(file)

        assert result.category == "Images"


class TestScreenshotDetector:
    """Tests for ScreenshotDetector."""

    def test_detects_macos_screenshot(self, tmp_path: Path) -> None:
        """Detects macOS screenshot format."""
        detector = ScreenshotDetector()
        file_path = tmp_path / "Screen Shot 2024-01-15 at 10.30.45 AM.png"
        file_path.write_bytes(b"content")
        file = FileInfo.from_path(file_path)

        result = detector.detect(file)

        assert result is not None
        assert result.category == "Screenshots"
        assert result.confidence == CONFIDENCE_HIGH

    def test_detects_macos_new_screenshot(self, tmp_path: Path) -> None:
        """Detects newer macOS screenshot format."""
        detector = ScreenshotDetector()
        file_path = tmp_path / "Screenshot 2024-01-15 at 10.30.45.png"
        file_path.write_bytes(b"content")
        file = FileInfo.from_path(file_path)

        result = detector.detect(file)

        assert result is not None
        assert result.detector_name == "ScreenshotDetector"

    def test_detects_cleanshot(self, tmp_path: Path) -> None:
        """Detects CleanShot screenshots."""
        detector = ScreenshotDetector()
        file_path = tmp_path / "CleanShot 2024-01-15 at 10.30.45.png"
        file_path.write_bytes(b"content")
        file = FileInfo.from_path(file_path)

        result = detector.detect(file)

        assert result is not None

    def test_detects_spanish_screenshot(self, tmp_path: Path) -> None:
        """Detects Spanish screenshot names."""
        detector = ScreenshotDetector()
        file_path = tmp_path / "Captura de pantalla 2024-01-15.png"
        file_path.write_bytes(b"content")
        file = FileInfo.from_path(file_path)

        result = detector.detect(file)

        assert result is not None

    def test_detects_german_screenshot(self, tmp_path: Path) -> None:
        """Detects German screenshot names."""
        detector = ScreenshotDetector()
        file_path = tmp_path / "Bildschirmfoto 2024-01-15 um 10.30.45.png"
        file_path.write_bytes(b"content")
        file = FileInfo.from_path(file_path)

        result = detector.detect(file)

        assert result is not None

    def test_ignores_non_image(self, tmp_path: Path) -> None:
        """Ignores files with non-image extensions."""
        detector = ScreenshotDetector()
        file_path = tmp_path / "Screenshot 2024-01-15.pdf"
        file_path.write_text("content")
        file = FileInfo.from_path(file_path)

        result = detector.detect(file)

        assert result is None

    def test_ignores_regular_image(self, tmp_path: Path) -> None:
        """Ignores regular images without screenshot pattern."""
        detector = ScreenshotDetector()
        file_path = tmp_path / "vacation_photo.png"
        file_path.write_bytes(b"content")
        file = FileInfo.from_path(file_path)

        result = detector.detect(file)

        assert result is None


class TestArxivDetector:
    """Tests for ArxivDetector."""

    def test_detects_arxiv_pattern(self, tmp_path: Path) -> None:
        """Detects standard arXiv filename."""
        detector = ArxivDetector()
        file_path = tmp_path / "2501.12948.pdf"
        file_path.write_text("content")
        file = FileInfo.from_path(file_path)

        result = detector.detect(file)

        assert result is not None
        assert result.category == "Papers"
        assert result.confidence == CONFIDENCE_HIGH

    def test_detects_arxiv_with_version(self, tmp_path: Path) -> None:
        """Detects arXiv filename with version number."""
        detector = ArxivDetector()
        file_path = tmp_path / "2501.12948v2.pdf"
        file_path.write_text("content")
        file = FileInfo.from_path(file_path)

        result = detector.detect(file)

        assert result is not None

    def test_detects_five_digit_arxiv(self, tmp_path: Path) -> None:
        """Detects arXiv with 5-digit paper number."""
        detector = ArxivDetector()
        file_path = tmp_path / "2312.00001.pdf"
        file_path.write_text("content")
        file = FileInfo.from_path(file_path)

        result = detector.detect(file)

        assert result is not None

    def test_ignores_non_pdf(self, tmp_path: Path) -> None:
        """Ignores non-PDF files."""
        detector = ArxivDetector()
        file_path = tmp_path / "2501.12948.txt"
        file_path.write_text("content")
        file = FileInfo.from_path(file_path)

        result = detector.detect(file)

        assert result is None

    def test_ignores_similar_patterns(self, tmp_path: Path) -> None:
        """Ignores similar but non-arXiv patterns."""
        detector = ArxivDetector()

        # Too few digits
        file_path = tmp_path / "2501.123.pdf"
        file_path.write_text("content")
        file = FileInfo.from_path(file_path)

        assert detector.detect(file) is None

        # Wrong format
        file_path = tmp_path / "12345.67890.pdf"
        file_path.write_text("content")
        file = FileInfo.from_path(file_path)

        assert detector.detect(file) is None


class TestGlobalRegistry:
    """Tests for global registry."""

    def test_get_registry_returns_registry(self) -> None:
        """get_registry returns a DetectorRegistry."""
        registry = get_registry()

        assert isinstance(registry, DetectorRegistry)

    def test_registry_has_default_detectors(self) -> None:
        """Global registry has default detectors registered."""
        registry = get_registry()

        names = {d.name for d in registry.detectors}

        assert "GenericDetector" in names
        assert "ScreenshotDetector" in names
        assert "ArxivDetector" in names
        assert "InvoiceDetector" in names
        assert "BookDetector" in names
        assert "InstallerDetector" in names
        assert "PaperDetector" in names
        assert "ArchiveBookDetector" in names
