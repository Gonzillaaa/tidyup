"""Screenshot renamer.

Standardizes screenshot filenames with consistent date/time format.
"""

import re
from datetime import datetime
from typing import Optional

from ..models import DetectionResult, FileInfo, RenameResult
from .base import BaseRenamer, format_datetime


# Patterns to extract date/time from screenshot filenames
SCREENSHOT_DATE_PATTERNS = [
    # macOS: "Screen Shot 2024-01-15 at 10.30.45 AM.png"
    (
        r"Screen Shot (\d{4})-(\d{2})-(\d{2}) at (\d{1,2})\.(\d{2})\.(\d{2})( [AP]M)?",
        lambda m: _parse_macos_datetime(m),
    ),
    # macOS newer: "Screenshot 2024-01-15 at 10.30.45.png"
    (
        r"Screenshot (\d{4})-(\d{2})-(\d{2}) at (\d{1,2})\.(\d{2})\.(\d{2})",
        lambda m: datetime(
            int(m.group(1)), int(m.group(2)), int(m.group(3)),
            int(m.group(4)), int(m.group(5)), int(m.group(6))
        ),
    ),
    # CleanShot: "CleanShot 2024-01-15 at 10.30.45.png"
    (
        r"CleanShot (\d{4})-(\d{2})-(\d{2}) at (\d{1,2})\.(\d{2})\.(\d{2})",
        lambda m: datetime(
            int(m.group(1)), int(m.group(2)), int(m.group(3)),
            int(m.group(4)), int(m.group(5)), int(m.group(6))
        ),
    ),
    # Windows: "Screenshot 2024-01-15 103045.png"
    (
        r"Screenshot (\d{4})-(\d{2})-(\d{2}) (\d{2})(\d{2})(\d{2})",
        lambda m: datetime(
            int(m.group(1)), int(m.group(2)), int(m.group(3)),
            int(m.group(4)), int(m.group(5)), int(m.group(6))
        ),
    ),
    # German: "Bildschirmfoto 2024-01-15 um 10.30.45.png"
    (
        r"Bildschirmfoto (\d{4})-(\d{2})-(\d{2}) um (\d{1,2})\.(\d{2})\.(\d{2})",
        lambda m: datetime(
            int(m.group(1)), int(m.group(2)), int(m.group(3)),
            int(m.group(4)), int(m.group(5)), int(m.group(6))
        ),
    ),
    # Spanish: "Captura de pantalla 2024-01-15.png" (date only)
    (
        r"Captura de pantalla (\d{4})-(\d{2})-(\d{2})",
        lambda m: datetime(int(m.group(1)), int(m.group(2)), int(m.group(3))),
    ),
]


def _parse_macos_datetime(match: re.Match) -> datetime:
    """Parse macOS screenshot datetime with AM/PM handling."""
    year = int(match.group(1))
    month = int(match.group(2))
    day = int(match.group(3))
    hour = int(match.group(4))
    minute = int(match.group(5))
    second = int(match.group(6))
    ampm = match.group(7)

    if ampm:
        ampm = ampm.strip().upper()
        if ampm == "PM" and hour != 12:
            hour += 12
        elif ampm == "AM" and hour == 12:
            hour = 0

    return datetime(year, month, day, hour, minute, second)


def extract_screenshot_datetime(filename: str) -> Optional[datetime]:
    """Extract datetime from screenshot filename.

    Args:
        filename: Screenshot filename to parse.

    Returns:
        Extracted datetime or None.
    """
    for pattern, parser in SCREENSHOT_DATE_PATTERNS:
        match = re.search(pattern, filename, re.IGNORECASE)
        if match:
            try:
                return parser(match)
            except (ValueError, IndexError):
                continue
    return None


class ScreenshotRenamer(BaseRenamer):
    """Renamer for screenshots.

    Pattern: Screenshot_{date}_{time}.{ext}

    Extracts date/time from original screenshot filename or falls
    back to file modified time.
    """

    @property
    def name(self) -> str:
        return "ScreenshotRenamer"

    def should_rename(self, file: FileInfo) -> bool:
        """Always rename screenshots to standardize format."""
        return True

    def rename(
        self,
        file: FileInfo,
        detection: DetectionResult,
    ) -> Optional[RenameResult]:
        """Generate standardized screenshot filename.

        Args:
            file: FileInfo for the screenshot.
            detection: DetectionResult from category detection.

        Returns:
            RenameResult if file should be renamed, None otherwise.
        """
        # Only rename if detector identified as screenshot
        if detection.detector_name != "ScreenshotDetector":
            return None

        # Try to extract datetime from filename
        dt = extract_screenshot_datetime(file.name)
        if not dt:
            dt = file.modified

        # Build standardized name
        datetime_str = format_datetime(dt)
        new_name = f"Screenshot_{datetime_str}.{file.extension}"

        if new_name == file.name:
            return None

        return RenameResult(
            original_name=file.name,
            new_name=new_name,
            renamer_name=self.name,
            date_extracted=dt.date(),
        )
