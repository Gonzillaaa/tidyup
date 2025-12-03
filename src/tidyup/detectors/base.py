"""Base detector class and constants.

This module defines the abstract base class for all file detectors
and confidence level constants.
"""

from abc import ABC, abstractmethod

from ..models import DetectionResult, FileInfo

# Confidence level constants
CONFIDENCE_HIGH = 0.9
CONFIDENCE_MEDIUM = 0.7
CONFIDENCE_LOW = 0.5


class BaseDetector(ABC):
    """Abstract base class for file type detectors.

    All detectors must inherit from this class and implement
    the detect() method.

    Attributes:
        name: Human-readable name of the detector.
        priority: Lower numbers = higher priority for tie-breaking.
                  More specific detectors should have lower priority values.
    """

    priority: int = 50  # Default priority (lower = more specific)

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the detector's name."""
        ...

    @abstractmethod
    def detect(self, file: FileInfo) -> DetectionResult | None:
        """Attempt to detect the file type.

        Args:
            file: FileInfo object containing file metadata.

        Returns:
            DetectionResult if the detector can categorize the file,
            None if the detector doesn't recognize the file.
        """
        ...
