"""Content extraction utilities for file type detection.

This module provides utilities for extracting text content from
various file types to enable content-based detection.
"""

import logging
from functools import lru_cache
from pathlib import Path
from typing import Optional

from pypdf import PdfReader
from pypdf.errors import PdfReadError

# Suppress noisy pypdf warnings for malformed PDFs
logging.getLogger("pypdf").setLevel(logging.ERROR)


def extract_pdf_text(
    path: Path,
    max_pages: int = 2,
    max_chars: int = 5000,
) -> Optional[str]:
    """Extract text from the first pages of a PDF.

    Args:
        path: Path to the PDF file.
        max_pages: Maximum number of pages to extract (default 2).
        max_chars: Maximum characters to return (default 5000).

    Returns:
        Extracted text, or None if extraction fails.
    """
    try:
        reader = PdfReader(path)
        text_parts: list[str] = []
        total_chars = 0

        for i, page in enumerate(reader.pages):
            if i >= max_pages:
                break

            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
                total_chars += len(page_text)

                if total_chars >= max_chars:
                    break

        if not text_parts:
            return None

        full_text = "\n".join(text_parts)
        return full_text[:max_chars] if len(full_text) > max_chars else full_text

    except (PdfReadError, Exception):
        # PDF is corrupted, encrypted, or otherwise unreadable
        return None


@lru_cache(maxsize=128)
def extract_pdf_text_cached(
    path: str,
    max_pages: int = 2,
    max_chars: int = 5000,
) -> Optional[str]:
    """Cached version of extract_pdf_text.

    Uses string path for hashability in LRU cache.

    Args:
        path: String path to the PDF file.
        max_pages: Maximum number of pages to extract.
        max_chars: Maximum characters to return.

    Returns:
        Extracted text, or None if extraction fails.
    """
    return extract_pdf_text(Path(path), max_pages, max_chars)
