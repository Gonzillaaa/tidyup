"""Invoice/receipt detector.

Detects invoice and receipt documents by content analysis.
"""

import re

from ..models import DetectionResult, FileInfo
from .base import CONFIDENCE_HIGH, CONFIDENCE_MEDIUM, BaseDetector
from .content import extract_pdf_text_cached

# Invoice keywords in multiple languages
INVOICE_KEYWORDS = [
    # English
    r"\binvoice\b",
    r"\breceipt\b",
    r"\bbill\s+to\b",
    r"\bpayment\s+due\b",
    r"\bsubtotal\b",
    r"\btotal\s+due\b",
    r"\bamount\s+due\b",
    r"\border\s+confirmation\b",
    # Spanish
    r"\bfactura\b",
    r"\brecibo\b",
    r"\bcomprobante\b",
    # German
    r"\brechnung\b",
    r"\bquittung\b",
    r"\bbeleg\b",
    # French
    r"\bfacture\b",
    r"\bre[cç]u\b",
    # Portuguese
    r"\bnota\s+fiscal\b",
    r"\brecibo\b",
    # Italian
    r"\bfattura\b",
    r"\bricevuta\b",
]

# Compile patterns for efficiency
INVOICE_PATTERNS = [re.compile(p, re.IGNORECASE) for p in INVOICE_KEYWORDS]

# Strong indicators that almost certainly mean invoice
STRONG_INDICATORS = [
    re.compile(r"\binvoice\s*(number|no\.?|#)\s*:?\s*\w+", re.IGNORECASE),
    re.compile(r"\binvoice\s+date\b", re.IGNORECASE),
    re.compile(r"\bbill\s+to\s*:", re.IGNORECASE),
    re.compile(r"\bpayment\s+terms\b", re.IGNORECASE),
    re.compile(r"\btax\s+id\b", re.IGNORECASE),
    re.compile(r"\bvat\s*(number|no\.?|#)?\s*:?", re.IGNORECASE),
]


class InvoiceDetector(BaseDetector):
    """Detector for invoice and receipt documents.

    Identifies invoices by analyzing PDF content for invoice-related
    keywords in multiple languages.
    """

    priority = 15  # Higher priority than generic, lower than arXiv

    @property
    def name(self) -> str:
        return "InvoiceDetector"

    def detect(self, file: FileInfo) -> DetectionResult | None:
        """Detect if file is an invoice or receipt.

        Args:
            file: FileInfo for the file to detect.

        Returns:
            DetectionResult if file appears to be an invoice,
            None otherwise.
        """
        # Only process PDFs
        if file.extension.lower() != "pdf":
            return None

        # Extract text from PDF
        text = extract_pdf_text_cached(str(file.path))
        if not text:
            return None

        # Check for strong indicators first
        for pattern in STRONG_INDICATORS:
            if pattern.search(text):
                return DetectionResult(
                    category="Documents",
                    confidence=CONFIDENCE_HIGH,
                    detector_name=self.name,
                    reason="Contains invoice-specific fields",
                )

        # Count keyword matches
        match_count = sum(1 for p in INVOICE_PATTERNS if p.search(text))

        if match_count >= 3:
            # Multiple keywords = high confidence
            return DetectionResult(
                category="Documents",
                confidence=CONFIDENCE_HIGH,
                detector_name=self.name,
                reason=f"Contains {match_count} invoice keywords",
            )
        elif match_count >= 1:
            # Single keyword = medium confidence
            return DetectionResult(
                category="Documents",
                confidence=CONFIDENCE_MEDIUM,
                detector_name=self.name,
                reason="Contains invoice-related keywords",
            )

        return None
