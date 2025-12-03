"""Invoice renamer.

Extracts vendor name and date for invoice filenames.
"""

import re

from ..detectors.content import extract_pdf_text_cached
from ..models import DetectionResult, FileInfo, RenameResult
from ..utils import sanitize_filename
from .base import BaseRenamer, format_date

# Patterns to extract vendor/company names
VENDOR_PATTERNS = [
    # "From: Company Name" or "Invoice from Company"
    re.compile(r"(?:from|by|issued by)[:\s]+([A-Z][A-Za-z0-9\s&.,'-]+)", re.IGNORECASE),
    # "Company Name Inc." or "Company LLC"
    re.compile(r"([A-Z][A-Za-z0-9\s&]+(?:Inc\.?|LLC|Ltd\.?|Corp\.?|GmbH|S\.A\.))", re.IGNORECASE),
    # Email domain as fallback: "@company.com"
    re.compile(r"@([a-z0-9-]+)\.[a-z]{2,}", re.IGNORECASE),
]


def extract_vendor_name(text: str) -> str | None:
    """Extract vendor/company name from invoice text.

    Args:
        text: Invoice text content.

    Returns:
        Vendor name or None.
    """
    for pattern in VENDOR_PATTERNS:
        match = pattern.search(text)
        if match:
            vendor = match.group(1).strip()
            # Clean up and validate
            vendor = re.sub(r"\s+", " ", vendor)
            if 2 <= len(vendor) <= 50:
                return vendor
    return None


class InvoiceRenamer(BaseRenamer):
    """Renamer for invoices.

    Pattern: {date}_Invoice_{vendor}.pdf

    Attempts to extract vendor name from PDF text.
    Falls back to "Invoice" if vendor not found.
    """

    @property
    def name(self) -> str:
        return "InvoiceRenamer"

    def should_rename(self, file: FileInfo) -> bool:
        """Always rename invoices."""
        return True

    def rename(
        self,
        file: FileInfo,
        detection: DetectionResult,
    ) -> RenameResult | None:
        """Generate invoice filename with vendor.

        Args:
            file: FileInfo for the invoice.
            detection: DetectionResult from category detection.

        Returns:
            RenameResult if file should be renamed, None otherwise.
        """
        # Only rename if detector identified as invoice
        if detection.detector_name != "InvoiceDetector":
            return None

        if file.extension.lower() != "pdf":
            return None

        # Try to extract vendor from text
        text = extract_pdf_text_cached(str(file.path))
        vendor = None
        if text:
            vendor = extract_vendor_name(text)

        # Use file date
        date_str = format_date(file.modified)

        # Build new name
        if vendor:
            sanitized_vendor = sanitize_filename(vendor)
            # Truncate if too long
            if len(sanitized_vendor) > 30:
                sanitized_vendor = sanitized_vendor[:30].rsplit("_", 1)[0]
            new_stem = f"{date_str}_Invoice_{sanitized_vendor}"
        else:
            new_stem = f"{date_str}_Invoice"

        new_name = f"{new_stem}.pdf"

        if new_name == file.name:
            return None

        return RenameResult(
            original_name=file.name,
            new_name=new_name,
            renamer_name=self.name,
            date_extracted=file.modified.date(),
            title_extracted=vendor,
        )
