"""Tests for InvoiceDetector."""

import pytest
from pathlib import Path
from unittest.mock import patch

from tidyup.models import FileInfo
from tidyup.detectors.invoice import InvoiceDetector
from tidyup.detectors.base import CONFIDENCE_HIGH, CONFIDENCE_MEDIUM


class TestInvoiceDetector:
    """Tests for InvoiceDetector."""

    def test_ignores_non_pdf(self, tmp_path: Path) -> None:
        """Ignores non-PDF files."""
        detector = InvoiceDetector()
        file_path = tmp_path / "invoice.txt"
        file_path.write_text("Invoice #123")
        file = FileInfo.from_path(file_path)

        result = detector.detect(file)

        assert result is None

    @patch("tidyup.detectors.invoice.extract_pdf_text_cached")
    def test_returns_none_when_no_text(
        self, mock_extract: patch, tmp_path: Path
    ) -> None:
        """Returns None when PDF has no extractable text."""
        mock_extract.return_value = None
        detector = InvoiceDetector()

        file_path = tmp_path / "scan.pdf"
        file_path.write_bytes(b"%PDF-1.4")
        file = FileInfo.from_path(file_path)

        result = detector.detect(file)

        assert result is None

    @patch("tidyup.detectors.invoice.extract_pdf_text_cached")
    def test_detects_invoice_number(
        self, mock_extract: patch, tmp_path: Path
    ) -> None:
        """Detects invoice by Invoice Number field."""
        mock_extract.return_value = """
        ACME Corp
        Invoice Number: INV-2024-001
        Date: January 15, 2024
        """
        detector = InvoiceDetector()

        file_path = tmp_path / "document.pdf"
        file_path.write_bytes(b"%PDF-1.4")
        file = FileInfo.from_path(file_path)

        result = detector.detect(file)

        assert result is not None
        assert result.confidence == CONFIDENCE_HIGH
        assert result.detector_name == "InvoiceDetector"

    @patch("tidyup.detectors.invoice.extract_pdf_text_cached")
    def test_detects_bill_to(self, mock_extract: patch, tmp_path: Path) -> None:
        """Detects invoice by Bill To field."""
        mock_extract.return_value = """
        Bill To:
        John Smith
        123 Main St
        """
        detector = InvoiceDetector()

        file_path = tmp_path / "document.pdf"
        file_path.write_bytes(b"%PDF-1.4")
        file = FileInfo.from_path(file_path)

        result = detector.detect(file)

        assert result is not None
        assert result.confidence == CONFIDENCE_HIGH

    @patch("tidyup.detectors.invoice.extract_pdf_text_cached")
    def test_detects_multiple_keywords(
        self, mock_extract: patch, tmp_path: Path
    ) -> None:
        """Detects invoice with multiple keywords."""
        mock_extract.return_value = """
        Invoice
        Subtotal: $100.00
        Total Due: $108.00
        """
        detector = InvoiceDetector()

        file_path = tmp_path / "document.pdf"
        file_path.write_bytes(b"%PDF-1.4")
        file = FileInfo.from_path(file_path)

        result = detector.detect(file)

        assert result is not None
        assert result.confidence == CONFIDENCE_HIGH

    @patch("tidyup.detectors.invoice.extract_pdf_text_cached")
    def test_detects_single_keyword_medium_confidence(
        self, mock_extract: patch, tmp_path: Path
    ) -> None:
        """Single keyword gives medium confidence."""
        mock_extract.return_value = """
        Thank you for your purchase!
        Your receipt is below.
        """
        detector = InvoiceDetector()

        file_path = tmp_path / "document.pdf"
        file_path.write_bytes(b"%PDF-1.4")
        file = FileInfo.from_path(file_path)

        result = detector.detect(file)

        assert result is not None
        assert result.confidence == CONFIDENCE_MEDIUM

    @patch("tidyup.detectors.invoice.extract_pdf_text_cached")
    def test_detects_spanish_invoice(
        self, mock_extract: patch, tmp_path: Path
    ) -> None:
        """Detects Spanish invoices."""
        mock_extract.return_value = """
        FACTURA
        Fecha: 15/01/2024
        Total: €100.00
        """
        detector = InvoiceDetector()

        file_path = tmp_path / "document.pdf"
        file_path.write_bytes(b"%PDF-1.4")
        file = FileInfo.from_path(file_path)

        result = detector.detect(file)

        assert result is not None

    @patch("tidyup.detectors.invoice.extract_pdf_text_cached")
    def test_detects_german_invoice(
        self, mock_extract: patch, tmp_path: Path
    ) -> None:
        """Detects German invoices."""
        mock_extract.return_value = """
        RECHNUNG
        Rechnungsnummer: 2024-001
        Datum: 15.01.2024
        """
        detector = InvoiceDetector()

        file_path = tmp_path / "document.pdf"
        file_path.write_bytes(b"%PDF-1.4")
        file = FileInfo.from_path(file_path)

        result = detector.detect(file)

        assert result is not None

    @patch("tidyup.detectors.invoice.extract_pdf_text_cached")
    def test_ignores_unrelated_pdf(
        self, mock_extract: patch, tmp_path: Path
    ) -> None:
        """Ignores PDFs without invoice keywords."""
        mock_extract.return_value = """
        Chapter 1: Introduction

        This book is about Python programming.
        """
        detector = InvoiceDetector()

        file_path = tmp_path / "book.pdf"
        file_path.write_bytes(b"%PDF-1.4")
        file = FileInfo.from_path(file_path)

        result = detector.detect(file)

        assert result is None

    def test_priority_is_set(self) -> None:
        """Detector has correct priority."""
        detector = InvoiceDetector()
        assert detector.priority == 15

    def test_name_property(self) -> None:
        """Name property returns correct value."""
        detector = InvoiceDetector()
        assert detector.name == "InvoiceDetector"
