"""Tests for data models."""

import pytest
from datetime import datetime, date
from pathlib import Path

from tidy.models import (
    FileInfo,
    DetectionResult,
    RenameResult,
    Action,
    RunSummary,
    RunResult,
)


class TestFileInfo:
    """Tests for FileInfo dataclass."""

    def test_from_path_creates_fileinfo(self, sample_pdf: Path) -> None:
        """FileInfo.from_path creates valid FileInfo from path."""
        info = FileInfo.from_path(sample_pdf)

        assert info.path == sample_pdf
        assert info.name == "sample.pdf"
        assert info.extension == "pdf"
        assert info.size > 0
        assert isinstance(info.modified, datetime)
        assert isinstance(info.created, datetime)

    def test_from_path_handles_no_extension(self, tmp_path: Path) -> None:
        """FileInfo.from_path handles files without extension."""
        no_ext = tmp_path / "noextension"
        no_ext.write_text("content")

        info = FileInfo.from_path(no_ext)

        assert info.extension == ""

    def test_to_dict_serializes_correctly(self, sample_pdf: Path) -> None:
        """FileInfo.to_dict produces valid JSON-serializable dict."""
        info = FileInfo.from_path(sample_pdf)
        d = info.to_dict()

        assert d["path"] == str(sample_pdf)
        assert d["name"] == "sample.pdf"
        assert d["extension"] == "pdf"
        assert isinstance(d["size"], int)
        assert isinstance(d["modified"], str)  # ISO format string
        assert isinstance(d["created"], str)


class TestDetectionResult:
    """Tests for DetectionResult dataclass."""

    def test_is_confident_above_threshold(self) -> None:
        """is_confident returns True when confidence >= threshold."""
        result = DetectionResult(
            category="01_Documents",
            confidence=0.9,
            detector_name="GenericDetector",
        )

        assert result.is_confident(0.7) is True
        assert result.is_confident(0.9) is True

    def test_is_confident_below_threshold(self) -> None:
        """is_confident returns False when confidence < threshold."""
        result = DetectionResult(
            category="01_Documents",
            confidence=0.5,
            detector_name="GenericDetector",
        )

        assert result.is_confident(0.7) is False

    def test_to_dict_includes_reason_when_present(self) -> None:
        """to_dict includes reason field when set."""
        result = DetectionResult(
            category="99_Unsorted",
            confidence=0.3,
            detector_name="GenericDetector",
            reason="Unknown file extension",
        )
        d = result.to_dict()

        assert d["reason"] == "Unknown file extension"

    def test_to_dict_excludes_reason_when_none(self) -> None:
        """to_dict excludes reason field when None."""
        result = DetectionResult(
            category="01_Documents",
            confidence=0.9,
            detector_name="GenericDetector",
        )
        d = result.to_dict()

        assert "reason" not in d


class TestRenameResult:
    """Tests for RenameResult dataclass."""

    def test_to_dict_basic(self) -> None:
        """to_dict produces valid dict with required fields."""
        result = RenameResult(
            original_name="report.pdf",
            new_name="2024-01-15_Annual_Report.pdf",
            renamer_name="PDFRenamer",
        )
        d = result.to_dict()

        assert d["original_name"] == "report.pdf"
        assert d["new_name"] == "2024-01-15_Annual_Report.pdf"
        assert d["renamer_name"] == "PDFRenamer"

    def test_to_dict_with_extracted_data(self) -> None:
        """to_dict includes extracted date and title when present."""
        result = RenameResult(
            original_name="report.pdf",
            new_name="2024-01-15_Annual_Report.pdf",
            renamer_name="PDFRenamer",
            date_extracted=date(2024, 1, 15),
            title_extracted="Annual Report",
        )
        d = result.to_dict()

        assert d["date_extracted"] == "2024-01-15"
        assert d["title_extracted"] == "Annual Report"


class TestAction:
    """Tests for Action dataclass."""

    def test_to_dict_produces_log_format(self, sample_pdf: Path) -> None:
        """to_dict produces format matching log specification."""
        file_info = FileInfo.from_path(sample_pdf)
        detection = DetectionResult(
            category="01_Documents",
            confidence=0.95,
            detector_name="GenericDetector",
        )
        rename = RenameResult(
            original_name="sample.pdf",
            new_name="2024-01-15_Sample.pdf",
            renamer_name="PDFRenamer",
        )
        dest = Path("/dest/01_Documents/2024-01-15_Sample.pdf")

        action = Action(
            file=file_info,
            detection=detection,
            source_path=sample_pdf,
            dest_path=dest,
            status="success",
            rename=rename,
        )
        d = action.to_dict()

        assert d["file"] == "sample.pdf"
        assert d["from"] == str(sample_pdf)
        assert d["to"] == str(dest)
        assert d["category"] == "01_Documents"
        assert d["confidence"] == 0.95
        assert d["status"] == "success"
        assert d["renamed_from"] == "sample.pdf"
        assert d["renamed_to"] == "2024-01-15_Sample.pdf"


class TestRunSummary:
    """Tests for RunSummary dataclass."""

    def test_default_values_are_zero(self) -> None:
        """RunSummary defaults all counters to zero."""
        summary = RunSummary()

        assert summary.processed == 0
        assert summary.moved == 0
        assert summary.renamed == 0
        assert summary.unsorted == 0
        assert summary.skipped == 0
        assert summary.errors == 0
        assert summary.duplicates == 0

    def test_to_dict_includes_all_fields(self) -> None:
        """to_dict includes all counter fields."""
        summary = RunSummary(
            processed=100,
            moved=90,
            renamed=85,
            unsorted=5,
            skipped=3,
            errors=2,
            duplicates=1,
        )
        d = summary.to_dict()

        assert d == {
            "processed": 100,
            "moved": 90,
            "renamed": 85,
            "unsorted": 5,
            "skipped": 3,
            "errors": 2,
            "duplicates": 1,
        }


class TestRunResult:
    """Tests for RunResult dataclass."""

    def test_to_dict_produces_complete_log(self, tmp_path: Path) -> None:
        """to_dict produces format matching log specification."""
        result = RunResult(
            timestamp=datetime(2024, 1, 15, 14, 30, 0),
            source=tmp_path / "source",
            destination=tmp_path / "dest",
            options={"move": True, "rename": True, "dry_run": False},
            summary=RunSummary(processed=10, moved=8, renamed=7),
        )
        d = result.to_dict()

        assert d["timestamp"] == "2024-01-15T14:30:00"
        assert d["source"] == str(tmp_path / "source")
        assert d["destination"] == str(tmp_path / "dest")
        assert d["options"]["move"] is True
        assert d["actions"] == []
        assert d["summary"]["processed"] == 10
