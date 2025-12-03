"""Book detector.

Detects book files by content analysis (PDFs) and file extensions.
"""

import re
from typing import Optional

from ..models import DetectionResult, FileInfo
from .base import BaseDetector, CONFIDENCE_HIGH, CONFIDENCE_MEDIUM
from .content import extract_pdf_text_cached


# Book file extensions (handled by GenericDetector, but we boost priority for PDFs)
EBOOK_EXTENSIONS = {"epub", "mobi", "azw", "azw3", "fb2"}

# ISBN patterns
ISBN_10_PATTERN = re.compile(r"\bISBN[-:\s]*(\d[-\s]?){9}[\dXx]\b")
ISBN_13_PATTERN = re.compile(r"\bISBN[-:\s]*(\d[-\s]?){13}\b")
ISBN_GENERIC = re.compile(r"\bISBN[-:\s]*[\d\-\sXx]{10,17}\b", re.IGNORECASE)

# Book-specific keywords
BOOK_KEYWORDS = [
    r"\bedition\b",
    r"\bchapter\s+\d+\b",
    r"\bpreface\b",
    r"\bforeword\b",
    r"\bepilogue\b",
    r"\bprologue\b",
    r"\btable\s+of\s+contents\b",
    r"\backnowledgments?\b",
    r"\bbibliography\b",
    r"\bappendix\b",
    r"\bindex\b",
    r"\bcopyright\s+©?\s*\d{4}\b",
    r"\ball\s+rights\s+reserved\b",
    r"\bpublished\s+by\b",
    r"\bprinted\s+in\b",
]

# Compile patterns
BOOK_PATTERNS = [re.compile(p, re.IGNORECASE) for p in BOOK_KEYWORDS]


class BookDetector(BaseDetector):
    """Detector for book files.

    Identifies books by:
    - ISBN patterns in PDF content
    - Book-specific keywords (edition, chapter, preface, etc.)
    - Ebook file extensions
    """

    priority = 20  # Higher than generic (50), but lower than specific detectors

    @property
    def name(self) -> str:
        return "BookDetector"

    def detect(self, file: FileInfo) -> Optional[DetectionResult]:
        """Detect if file is a book.

        Args:
            file: FileInfo for the file to detect.

        Returns:
            DetectionResult if file appears to be a book,
            None otherwise.
        """
        ext = file.extension.lower()

        # Ebook extensions are definitely books
        if ext in EBOOK_EXTENSIONS:
            return DetectionResult(
                category="07_Books",
                confidence=CONFIDENCE_HIGH,
                detector_name=self.name,
                reason=f"Ebook format (.{ext})",
            )

        # For PDFs, analyze content
        if ext != "pdf":
            return None

        text = extract_pdf_text_cached(str(file.path))
        if not text:
            return None

        # ISBN is a strong indicator
        if ISBN_GENERIC.search(text):
            return DetectionResult(
                category="07_Books",
                confidence=CONFIDENCE_HIGH,
                detector_name=self.name,
                reason="Contains ISBN",
            )

        # Count keyword matches
        match_count = sum(1 for p in BOOK_PATTERNS if p.search(text))

        if match_count >= 4:
            # Many book keywords = high confidence
            return DetectionResult(
                category="07_Books",
                confidence=CONFIDENCE_HIGH,
                detector_name=self.name,
                reason=f"Contains {match_count} book keywords",
            )
        elif match_count >= 2:
            # Some keywords = medium confidence
            return DetectionResult(
                category="07_Books",
                confidence=CONFIDENCE_MEDIUM,
                detector_name=self.name,
                reason="Contains book-related keywords",
            )

        return None
