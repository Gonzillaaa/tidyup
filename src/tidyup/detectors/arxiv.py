"""arXiv paper detector.

Detects arXiv preprints by their distinctive filename pattern.
"""

import re
from typing import Optional

from ..models import DetectionResult, FileInfo
from .base import BaseDetector, CONFIDENCE_HIGH


# arXiv filename pattern: YYMM.NNNNN or YYMM.NNNNNvN
# Examples: 2501.12948.pdf, 2501.12948v1.pdf, 2501.12948v2.pdf
ARXIV_PATTERN = re.compile(r"^\d{4}\.\d{4,5}(v\d+)?$")


class ArxivDetector(BaseDetector):
    """Detector for arXiv preprints.

    Identifies arXiv papers by their standard filename format
    (YYMM.NNNNN.pdf).
    """

    priority = 10  # High priority - very specific pattern

    @property
    def name(self) -> str:
        return "ArxivDetector"

    def detect(self, file: FileInfo) -> Optional[DetectionResult]:
        """Detect if file is an arXiv paper.

        Args:
            file: FileInfo for the file to detect.

        Returns:
            DetectionResult if file matches arXiv pattern,
            None otherwise.
        """
        # Must be a PDF
        if file.extension.lower() != "pdf":
            return None

        # Check filename pattern
        stem = file.path.stem

        if ARXIV_PATTERN.match(stem):
            return DetectionResult(
                category="Papers",
                confidence=CONFIDENCE_HIGH,
                detector_name=self.name,
            )

        return None
