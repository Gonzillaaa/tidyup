"""Academic paper detector.

Detects research papers and academic documents by content analysis.
"""

import re

from ..models import DetectionResult, FileInfo
from .base import CONFIDENCE_HIGH, CONFIDENCE_MEDIUM, BaseDetector
from .content import extract_pdf_text_cached

# DOI patterns
DOI_PATTERN = re.compile(r"\b10\.\d{4,}/[^\s]+\b")

# Paper-specific keywords with their patterns
PAPER_KEYWORDS = [
    r"\babstract\b",
    r"\breferences\b",
    r"\bcitations?\b",
    r"\bet\s+al\.?\b",
    r"\bconclusions?\b",
    r"\bmethodology\b",
    r"\bintroduction\b",
    r"\brelated\s+work\b",
    r"\bexperiments?\b",
    r"\bresults?\b",
    r"\bdiscussion\b",
    r"\bfigure\s+\d+\b",
    r"\btable\s+\d+\b",
    r"\bequation\s+\d+\b",
    r"\btheorem\s+\d+\b",
    r"\blemma\s+\d+\b",
    r"\bproof\b",
    r"\backnowledg[e]?ments?\b",
    r"\bfunding\b",
    r"\bconflict\s+of\s+interest\b",
    r"\bpeer[\s-]?review\b",
    r"\bjournal\b",
    r"\bproceedings?\b",
    r"\bconference\b",
    r"\buniversity\b",
    r"\bresearch\s+(institute|center|centre|lab)\b",
    r"\bdepartment\s+of\b",
]

# Compile patterns
PAPER_PATTERNS = [re.compile(p, re.IGNORECASE) for p in PAPER_KEYWORDS]

# Strong academic indicators (just 1-2 of these = high confidence)
STRONG_INDICATORS = [
    re.compile(r"\babstract\b", re.IGNORECASE),
    re.compile(r"\breferences\b", re.IGNORECASE),
    re.compile(r"\bet\s+al\.?\b", re.IGNORECASE),
]


class PaperDetector(BaseDetector):
    """Detector for academic papers and research documents.

    Identifies papers by:
    - DOI patterns
    - Academic keywords (abstract, references, citations, et al.)
    - Paper structure indicators (methodology, results, discussion)
    """

    priority = 12  # Higher priority than BookDetector (20)

    @property
    def name(self) -> str:
        return "PaperDetector"

    def detect(self, file: FileInfo) -> DetectionResult | None:
        """Detect if file is an academic paper.

        Args:
            file: FileInfo for the file to detect.

        Returns:
            DetectionResult if file appears to be an academic paper,
            None otherwise.
        """
        ext = file.extension.lower()

        # Only handle PDFs
        if ext != "pdf":
            return None

        text = extract_pdf_text_cached(str(file.path))
        if not text:
            return None

        # DOI is a strong indicator
        if DOI_PATTERN.search(text):
            return DetectionResult(
                category="Papers",
                confidence=CONFIDENCE_HIGH,
                detector_name=self.name,
                reason="Contains DOI",
            )

        # Count strong indicator matches
        strong_matches = sum(1 for p in STRONG_INDICATORS if p.search(text))

        # Count all keyword matches
        match_count = sum(1 for p in PAPER_PATTERNS if p.search(text))

        # Strong indicators + good keyword count = high confidence
        if strong_matches >= 2 and match_count >= 5:
            return DetectionResult(
                category="Papers",
                confidence=CONFIDENCE_HIGH,
                detector_name=self.name,
                reason=f"Academic paper ({match_count} indicators)",
            )

        # Good keyword count alone = medium confidence
        if match_count >= 5:
            return DetectionResult(
                category="Papers",
                confidence=CONFIDENCE_MEDIUM,
                detector_name=self.name,
                reason=f"Contains {match_count} academic keywords",
            )

        # Strong indicators with fewer keywords = medium confidence
        if strong_matches >= 2 and match_count >= 3:
            return DetectionResult(
                category="Papers",
                confidence=CONFIDENCE_MEDIUM,
                detector_name=self.name,
                reason="Contains academic structure",
            )

        return None
