"""Tests for PaperDetector."""

import pytest
from pathlib import Path
from unittest.mock import patch

from tidyup.models import FileInfo
from tidyup.detectors.paper import PaperDetector
from tidyup.detectors.base import CONFIDENCE_HIGH, CONFIDENCE_MEDIUM


class TestPaperDetector:
    """Tests for PaperDetector."""

    def test_ignores_non_pdf(self, tmp_path: Path) -> None:
        """Ignores non-PDF files."""
        detector = PaperDetector()
        file_path = tmp_path / "paper.txt"
        file_path.write_text("abstract references et al.")
        file = FileInfo.from_path(file_path)

        result = detector.detect(file)

        assert result is None

    @patch("tidyup.detectors.paper.extract_pdf_text_cached")
    def test_returns_none_when_no_text(
        self, mock_extract: patch, tmp_path: Path
    ) -> None:
        """Returns None when PDF has no extractable text."""
        mock_extract.return_value = None
        detector = PaperDetector()

        file_path = tmp_path / "scan.pdf"
        file_path.write_bytes(b"%PDF-1.4")
        file = FileInfo.from_path(file_path)

        result = detector.detect(file)

        assert result is None

    @patch("tidyup.detectors.paper.extract_pdf_text_cached")
    def test_detects_doi(self, mock_extract: patch, tmp_path: Path) -> None:
        """Detects papers by DOI."""
        mock_extract.return_value = """
        This paper presents our findings.
        DOI: 10.1038/nature12373
        """
        detector = PaperDetector()

        file_path = tmp_path / "paper.pdf"
        file_path.write_bytes(b"%PDF-1.4")
        file = FileInfo.from_path(file_path)

        result = detector.detect(file)

        assert result is not None
        assert result.category == "Papers"
        assert result.confidence == CONFIDENCE_HIGH
        assert "DOI" in result.reason

    @patch("tidyup.detectors.paper.extract_pdf_text_cached")
    def test_detects_academic_paper_high_confidence(
        self, mock_extract: patch, tmp_path: Path
    ) -> None:
        """Detects academic paper with strong indicators."""
        mock_extract.return_value = """
        Abstract

        This paper presents a novel approach...

        1. Introduction

        The field has seen significant progress...

        2. Related Work

        Smith et al. showed that...
        Jones et al. demonstrated...

        3. Methodology

        We conducted experiments...

        4. Results

        Figure 1 shows the comparison...
        Table 1 presents the metrics...

        5. Discussion

        Our findings suggest...

        6. Conclusions

        We have presented...

        References

        [1] Smith, J. et al. (2023)...
        """
        detector = PaperDetector()

        file_path = tmp_path / "paper.pdf"
        file_path.write_bytes(b"%PDF-1.4")
        file = FileInfo.from_path(file_path)

        result = detector.detect(file)

        assert result is not None
        assert result.category == "Papers"
        assert result.confidence == CONFIDENCE_HIGH

    @patch("tidyup.detectors.paper.extract_pdf_text_cached")
    def test_detects_paper_medium_confidence(
        self, mock_extract: patch, tmp_path: Path
    ) -> None:
        """Detects paper with fewer indicators at medium confidence."""
        mock_extract.return_value = """
        Abstract

        This paper presents...

        Introduction

        The problem of...

        Conclusions

        In this paper, we have shown...

        References
        """
        detector = PaperDetector()

        file_path = tmp_path / "paper.pdf"
        file_path.write_bytes(b"%PDF-1.4")
        file = FileInfo.from_path(file_path)

        result = detector.detect(file)

        assert result is not None
        assert result.category == "Papers"
        assert result.confidence in (CONFIDENCE_MEDIUM, CONFIDENCE_HIGH)

    @patch("tidyup.detectors.paper.extract_pdf_text_cached")
    def test_detects_et_al_pattern(
        self, mock_extract: patch, tmp_path: Path
    ) -> None:
        """Detects papers with et al. citations."""
        mock_extract.return_value = """
        Abstract

        Prior work by Smith et al. (2020) showed...
        This was extended by Jones et al. (2021)...

        References

        Smith et al., Nature, 2020
        Jones et al., Science, 2021
        """
        detector = PaperDetector()

        file_path = tmp_path / "paper.pdf"
        file_path.write_bytes(b"%PDF-1.4")
        file = FileInfo.from_path(file_path)

        result = detector.detect(file)

        assert result is not None
        assert result.category == "Papers"

    @patch("tidyup.detectors.paper.extract_pdf_text_cached")
    def test_ignores_non_academic_pdf(
        self, mock_extract: patch, tmp_path: Path
    ) -> None:
        """Ignores PDFs that don't look like academic papers."""
        mock_extract.return_value = """
        Meeting Notes
        January 15, 2024

        Attendees:
        - Alice
        - Bob

        Action Items:
        1. Review the proposal
        2. Send follow-up email

        Next meeting: January 22, 2024
        """
        detector = PaperDetector()

        file_path = tmp_path / "notes.pdf"
        file_path.write_bytes(b"%PDF-1.4")
        file = FileInfo.from_path(file_path)

        result = detector.detect(file)

        assert result is None

    @patch("tidyup.detectors.paper.extract_pdf_text_cached")
    def test_detects_figure_table_references(
        self, mock_extract: patch, tmp_path: Path
    ) -> None:
        """Detects papers with figure and table references."""
        mock_extract.return_value = """
        Abstract

        We present results of our analysis...

        As shown in Figure 1, the data indicates...
        Table 1 presents the comparison of methods...
        Figure 2 illustrates the architecture...

        See also Equation 1 for the formal definition...

        References
        """
        detector = PaperDetector()

        file_path = tmp_path / "paper.pdf"
        file_path.write_bytes(b"%PDF-1.4")
        file = FileInfo.from_path(file_path)

        result = detector.detect(file)

        assert result is not None
        assert result.category == "Papers"

    def test_priority_is_set(self) -> None:
        """Detector has correct priority."""
        detector = PaperDetector()
        assert detector.priority == 12

    def test_name_property(self) -> None:
        """Name property returns correct value."""
        detector = PaperDetector()
        assert detector.name == "PaperDetector"
