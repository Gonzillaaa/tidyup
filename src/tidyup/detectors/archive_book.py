"""Archive book detector.

Detects archives that contain books (e.g., ZIP files with EPUB/PDF).
"""

import re
import zipfile

from ..models import DetectionResult, FileInfo
from .base import CONFIDENCE_HIGH, CONFIDENCE_MEDIUM, BaseDetector

# Book file extensions to look for inside archives
BOOK_EXTENSIONS = {".epub", ".mobi", ".azw", ".azw3", ".pdf", ".fb2", ".djvu"}

# Archive extensions that can be inspected
ZIP_COMPATIBLE = {"zip", "cbz", "cbr", "epub"}  # EPUB is actually a ZIP

# Archive extensions we can only check by filename
OPAQUE_ARCHIVES = {"rar", "7z", "tar", "gz", "bz2"}

# Book-related keywords in filenames (strong indicators)
STRONG_BOOK_KEYWORDS = [
    r"\bedition\b",           # "3rd Edition"
    r"\bhandbook\b",
    r"\btextbook\b",
    r"\bfor\s+dummies\b",
    r"\bcookbook\b",
    r"\bdefinitive\b",
]

# Moderate indicators (need 2+ to classify)
MODERATE_BOOK_KEYWORDS = [
    r"\bprogramming\b",
    r"\btutorial\b",
    r"\bguide\b",
    r"\bmanual\b",
    r"\blearning\b",
    r"\bmastering\b",
    r"\bbeginning\b",
    r"\badvanced\b",
    r"\bintroducing\b",
    r"\bintroduction\b",
    r"\breference\b",
    r"\bessentials?\b",
    r"\bpractical\b",
    r"\bcomplete\b",
    r"\bcomprehensive\b",
    r"\bstudy\b",
    r"\bcertified\b",
    r"\banalyst\b",
    r"\bdeveloper\b",
    r"\bin\s+action\b",       # "Spring in Action"
    r"\bpro\s+\w+",           # "Pro Git"
    r"\bhead\s+first\b",      # "Head First Java"
]

# Compile patterns
STRONG_PATTERNS = [re.compile(p, re.IGNORECASE) for p in STRONG_BOOK_KEYWORDS]
MODERATE_PATTERNS = [re.compile(p, re.IGNORECASE) for p in MODERATE_BOOK_KEYWORDS]


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

    def detect(self, file: FileInfo) -> DetectionResult | None:
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

    def _inspect_zip(self, file: FileInfo) -> DetectionResult | None:
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

    def _analyze_filename(self, file: FileInfo) -> DetectionResult | None:
        """Analyze filename for book-related keywords."""
        # Get stem without extension
        stem = file.path.stem.lower()

        # Check for strong indicators (single match = high confidence)
        strong_matches = sum(1 for p in STRONG_PATTERNS if p.search(stem))
        if strong_matches >= 1:
            return DetectionResult(
                category="Books",
                confidence=CONFIDENCE_HIGH,
                detector_name=self.name,
                reason="Filename contains strong book indicator",
            )

        # Check moderate indicators (need 2+ matches)
        moderate_matches = sum(1 for p in MODERATE_PATTERNS if p.search(stem))
        if moderate_matches >= 2:
            return DetectionResult(
                category="Books",
                confidence=CONFIDENCE_MEDIUM,
                detector_name=self.name,
                reason=f"Filename suggests book ({moderate_matches} keywords)",
            )

        return None
