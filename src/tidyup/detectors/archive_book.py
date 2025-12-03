"""Archive book detector.

Detects archives that contain books (e.g., ZIP files with EPUB/PDF).
"""

import re
import zipfile
from typing import Optional

from ..models import DetectionResult, FileInfo
from .base import BaseDetector, CONFIDENCE_HIGH, CONFIDENCE_MEDIUM


# Book file extensions to look for inside archives
BOOK_EXTENSIONS = {".epub", ".mobi", ".azw", ".azw3", ".pdf", ".fb2", ".djvu"}

# Archive extensions that can be inspected
ZIP_COMPATIBLE = {"zip", "cbz", "cbr", "epub"}  # EPUB is actually a ZIP

# Archive extensions we can only check by filename
OPAQUE_ARCHIVES = {"rar", "7z", "tar", "gz", "bz2"}

# Book-related keywords in filenames
BOOK_KEYWORDS = [
    r"\bedition\b",
    r"\bhandbook\b",
    r"\bprogramming\b",
    r"\btutorial\b",
    r"\bguide\b",
    r"\bmanual\b",
    r"\btextbook\b",
    r"\blearning\b",
    r"\bmastering\b",
    r"\bbeginning\b",
    r"\badvanced\b",
    r"\bintroduction\s+to\b",
    r"\bfor\s+dummies\b",
    r"\bcookbook\b",
    r"\breference\b",
    r"\bdefinitive\b",
    r"\bessential\s",
    r"\bpractical\b",
    r"\bcomplete\b",
    r"\bcomprehensive\b",
]

# Compile patterns
BOOK_PATTERNS = [re.compile(p, re.IGNORECASE) for p in BOOK_KEYWORDS]


class ArchiveBookDetector(BaseDetector):
    """Detector for archives containing books.

    Identifies book archives by:
    - Inspecting ZIP contents for book file extensions
    - Analyzing archive filenames for book-related keywords
    """

    priority = 18  # Higher than BookDetector (20), but lower than more specific

    @property
    def name(self) -> str:
        return "ArchiveBookDetector"

    def detect(self, file: FileInfo) -> Optional[DetectionResult]:
        """Detect if archive contains books.

        Args:
            file: FileInfo for the file to detect.

        Returns:
            DetectionResult if archive appears to contain books,
            None otherwise.
        """
        ext = file.extension.lower()

        # Try to inspect ZIP-compatible archives
        if ext in ZIP_COMPATIBLE:
            result = self._inspect_zip(file)
            if result:
                return result

        # For opaque archives or when ZIP inspection fails, use filename heuristics
        if ext in OPAQUE_ARCHIVES or ext in ZIP_COMPATIBLE:
            result = self._analyze_filename(file)
            if result:
                return result

        return None

    def _inspect_zip(self, file: FileInfo) -> Optional[DetectionResult]:
        """Inspect ZIP archive contents for book files."""
        try:
            with zipfile.ZipFile(file.path, "r") as zf:
                names = zf.namelist()

                # Count book files inside
                book_files = [
                    n for n in names
                    if any(n.lower().endswith(ext) for ext in BOOK_EXTENSIONS)
                ]

                if book_files:
                    # Found book files inside
                    ext_found = set()
                    for name in book_files:
                        for ext in BOOK_EXTENSIONS:
                            if name.lower().endswith(ext):
                                ext_found.add(ext.lstrip("."))
                                break

                    return DetectionResult(
                        category="Books",
                        confidence=CONFIDENCE_HIGH,
                        detector_name=self.name,
                        reason=f"Contains {len(book_files)} book file(s) ({', '.join(ext_found)})",
                    )

        except (zipfile.BadZipFile, OSError, PermissionError):
            # Not a valid ZIP or can't read it
            pass

        return None

    def _analyze_filename(self, file: FileInfo) -> Optional[DetectionResult]:
        """Analyze filename for book-related keywords."""
        # Get stem without extension
        stem = file.path.stem.lower()

        # Count keyword matches
        match_count = sum(1 for p in BOOK_PATTERNS if p.search(stem))

        if match_count >= 2:
            # Multiple book keywords = medium confidence
            return DetectionResult(
                category="Books",
                confidence=CONFIDENCE_MEDIUM,
                detector_name=self.name,
                reason=f"Filename suggests book ({match_count} keywords)",
            )

        return None
