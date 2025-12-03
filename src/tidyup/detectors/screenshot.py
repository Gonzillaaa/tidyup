"""Screenshot detector.

Detects screenshot files by filename patterns across different
operating systems and languages.
"""

import re
from typing import Optional

from ..models import DetectionResult, FileInfo
from .base import BaseDetector, CONFIDENCE_HIGH


# Screenshot filename patterns
SCREENSHOT_PATTERNS = [
    # macOS: "Screen Shot 2024-01-15 at 10.30.45 AM.png"
    r"^Screen Shot \d{4}-\d{2}-\d{2} at \d{1,2}\.\d{2}\.\d{2}( [AP]M)?",
    # macOS newer: "Screenshot 2024-01-15 at 10.30.45.png"
    r"^Screenshot \d{4}-\d{2}-\d{2} at \d{1,2}\.\d{2}\.\d{2}",
    # Windows Snipping Tool: "Screenshot 2024-01-15 103045.png"
    r"^Screenshot \d{4}-\d{2}-\d{2} \d{6}",
    # Windows: "Screenshot (123).png"
    r"^Screenshot \(\d+\)",
    # Generic: starts with Screenshot or Screen Shot
    r"^Screenshot[_\s-]",
    r"^Screen Shot[_\s-]",
    # Spanish: "Captura de pantalla"
    r"^Captura de pantalla",
    r"^Captura[_\s-]",
    # German: "Bildschirmfoto"
    r"^Bildschirmfoto",
    # French: "Capture d'écran"
    r"^Capture d['\u2019]écran",
    # iOS: "IMG_1234.PNG" (numbered photos could be screenshots)
    # Not included - too generic, would match regular photos
    # CleanShot: "CleanShot 2024-01-15 at 10.30.45.png"
    r"^CleanShot \d{4}-\d{2}-\d{2}",
    # Skitch
    r"^Skitch",
    # Lightshot
    r"^Lightshot",
    # ShareX
    r"^ShareX",
    # Greenshot
    r"^Greenshot",
    # Snagit
    r"^Snagit",
]

# Compile patterns for efficiency
COMPILED_PATTERNS = [re.compile(p, re.IGNORECASE) for p in SCREENSHOT_PATTERNS]

# Image extensions that screenshots typically use
SCREENSHOT_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp", "tiff", "bmp"}


class ScreenshotDetector(BaseDetector):
    """Detector for screenshot files.

    Identifies screenshots by matching filename patterns used by
    various operating systems and screenshot tools.
    """

    priority = 10  # High priority - more specific than generic image

    @property
    def name(self) -> str:
        return "ScreenshotDetector"

    def detect(self, file: FileInfo) -> Optional[DetectionResult]:
        """Detect if file is a screenshot.

        Args:
            file: FileInfo for the file to detect.

        Returns:
            DetectionResult if file appears to be a screenshot,
            None otherwise.
        """
        # Must be an image extension
        if file.extension.lower() not in SCREENSHOT_EXTENSIONS:
            return None

        # Check filename against patterns
        stem = file.path.stem

        for pattern in COMPILED_PATTERNS:
            if pattern.match(stem):
                return DetectionResult(
                    category="02_Images",
                    confidence=CONFIDENCE_HIGH,
                    detector_name=self.name,
                )

        return None
