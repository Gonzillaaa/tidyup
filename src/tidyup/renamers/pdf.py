"""PDF renamer with metadata extraction.

Extracts title and date from PDF metadata for smart renaming.
"""

import logging
import re
from datetime import datetime

from pypdf import PdfReader
from pypdf.errors import PdfReadError

from ..models import DetectionResult, FileInfo, RenameResult
from ..utils import sanitize_filename
from .base import BaseRenamer, format_date

# Suppress pypdf warnings
logging.getLogger("pypdf").setLevel(logging.ERROR)


def extract_pdf_metadata(file: FileInfo) -> tuple[str | None, datetime | None]:
    """Extract title and date from PDF metadata.

    Args:
        file: FileInfo for the PDF file.

    Returns:
        Tuple of (title, creation_date), either may be None.
    """
    try:
        reader = PdfReader(file.path)
        metadata = reader.metadata

        if not metadata:
            return None, None

        # Extract title
        title = None
        if metadata.title:
            title = str(metadata.title).strip()
            # Skip if title is just the filename or too short
            if len(title) < 3 or title.lower() == file.path.stem.lower():
                title = None

        # Extract creation date
        creation_date = None
        if metadata.creation_date:
            creation_date = metadata.creation_date

        return title, creation_date

    except (PdfReadError, Exception):
        return None, None


def extract_title_from_text(file: FileInfo) -> str | None:
    """Extract title from PDF text content.

    Looks for the first substantial line of text that could be a title.

    Args:
        file: FileInfo for the PDF file.

    Returns:
        Extracted title or None.
    """
    try:
        reader = PdfReader(file.path)
        if not reader.pages:
            return None

        # Get text from first page
        text = reader.pages[0].extract_text()
        if not text:
            return None

        # Look for title-like lines (first non-empty lines)
        lines = [line.strip() for line in text.split("\n") if line.strip()]

        for line in lines[:5]:  # Check first 5 lines
            # Skip very short or very long lines
            if 5 <= len(line) <= 100:
                # Skip lines that look like metadata
                if not re.match(r"^(page|copyright|©|\d+$)", line, re.IGNORECASE):
                    return line

        return None

    except (PdfReadError, Exception):
        return None


class PDFRenamer(BaseRenamer):
    """Renamer for PDF documents using metadata.

    Pattern: {date}_{title}.pdf

    Attempts to extract title from:
    1. PDF metadata (/Title field)
    2. First heading in document text
    3. Falls back to sanitized original name
    """

    @property
    def name(self) -> str:
        return "PDFRenamer"

    def rename(
        self,
        file: FileInfo,
        detection: DetectionResult,
    ) -> RenameResult | None:
        """Generate a new filename from PDF metadata.

        Args:
            file: FileInfo for the PDF file.
            detection: DetectionResult from category detection.

        Returns:
            RenameResult if file should be renamed, None otherwise.
        """
        if not self.should_rename(file):
            return None

        if file.extension.lower() != "pdf":
            return None

        # Try to extract metadata
        title, creation_date = extract_pdf_metadata(file)

        # If no title in metadata, try text extraction
        if not title:
            title = extract_title_from_text(file)

        # Determine the date to use
        if creation_date:
            date_str = format_date(creation_date)
            date_extracted = creation_date.date()
        else:
            date_str = format_date(file.modified)
            date_extracted = file.modified.date()

        # Build new filename
        if title:
            sanitized_title = sanitize_filename(title)
            # Truncate if too long
            if len(sanitized_title) > 80:
                sanitized_title = sanitized_title[:80].rsplit("_", 1)[0]
            new_stem = f"{date_str}_{sanitized_title}"
            title_extracted = title
        else:
            # Fall back to sanitized original name
            sanitized_name = sanitize_filename(file.path.stem)
            if len(sanitized_name) < 3:
                new_stem = f"{date_str}_document"
            else:
                new_stem = f"{date_str}_{sanitized_name}"
            title_extracted = None

        new_name = f"{new_stem}.pdf"

        if new_name == file.name:
            return None

        return RenameResult(
            original_name=file.name,
            new_name=new_name,
            renamer_name=self.name,
            date_extracted=date_extracted,
            title_extracted=title_extracted,
        )
