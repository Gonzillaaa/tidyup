"""arXiv paper renamer.

Keeps arXiv ID but adds date prefix.
"""

import re
from typing import Optional

from ..models import DetectionResult, FileInfo, RenameResult
from .base import BaseRenamer, format_date


# arXiv ID pattern: YYMM.NNNNN or YYMM.NNNNNvN
ARXIV_ID_PATTERN = re.compile(r"(\d{4}\.\d{4,5})(v\d+)?")


class ArxivRenamer(BaseRenamer):
    """Renamer for arXiv papers.

    Pattern: {date}_{arxiv_id}.pdf

    Keeps the arXiv ID intact and adds a date prefix.
    """

    @property
    def name(self) -> str:
        return "ArxivRenamer"

    def should_rename(self, file: FileInfo) -> bool:
        """Always rename arXiv papers to add date."""
        return True

    def rename(
        self,
        file: FileInfo,
        detection: DetectionResult,
    ) -> Optional[RenameResult]:
        """Generate arXiv filename with date prefix.

        Args:
            file: FileInfo for the arXiv paper.
            detection: DetectionResult from category detection.

        Returns:
            RenameResult if file should be renamed, None otherwise.
        """
        # Only rename if detector identified as arXiv
        if detection.detector_name != "ArxivDetector":
            return None

        # Extract arXiv ID from filename
        match = ARXIV_ID_PATTERN.search(file.path.stem)
        if not match:
            return None

        arxiv_id = match.group(0)  # Full match including version

        # Use file date
        date_str = format_date(file.modified)

        # Build new name
        new_name = f"{date_str}_{arxiv_id}.pdf"

        if new_name == file.name:
            return None

        return RenameResult(
            original_name=file.name,
            new_name=new_name,
            renamer_name=self.name,
            date_extracted=file.modified.date(),
        )
