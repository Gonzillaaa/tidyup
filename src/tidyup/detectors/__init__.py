"""Detector framework for TidyUp.

This module provides the detector registry and imports all detectors.
"""

from typing import Optional

from ..models import DetectionResult, FileInfo
from .base import (
    CONFIDENCE_HIGH,
    CONFIDENCE_LOW,
    CONFIDENCE_MEDIUM,
    BaseDetector,
)


class DetectorRegistry:
    """Registry for file type detectors.

    Manages a collection of detectors and runs them in priority order
    to determine the best categorization for a file.

    Attributes:
        detectors: List of registered detector instances.
    """

    def __init__(self) -> None:
        """Initialize an empty registry."""
        self.detectors: list[BaseDetector] = []

    def register(self, detector: BaseDetector) -> None:
        """Register a detector.

        Args:
            detector: Detector instance to register.
        """
        self.detectors.append(detector)
        # Keep sorted by priority (lower = higher priority)
        self.detectors.sort(key=lambda d: d.priority)

    def detect(self, file: FileInfo) -> DetectionResult:
        """Run all detectors and return the best result.

        Detectors are run in priority order. The result with the
        highest confidence wins. In case of ties, the more specific
        detector (lower priority number) wins.

        Args:
            file: FileInfo for the file to detect.

        Returns:
            Best DetectionResult, or a default "Unsorted" result.
        """
        results: list[tuple[int, DetectionResult]] = []

        for detector in self.detectors:
            result = detector.detect(file)
            if result is not None:
                results.append((detector.priority, result))

        if not results:
            # No detector matched
            return DetectionResult(
                category="99_Unsorted",
                confidence=0.0,
                detector_name="None",
                reason="No detector matched this file",
            )

        # Sort by confidence (desc), then by priority (asc) for tie-breaking
        results.sort(key=lambda x: (-x[1].confidence, x[0]))

        return results[0][1]


# Global registry instance
_registry: Optional[DetectorRegistry] = None


def get_registry() -> DetectorRegistry:
    """Get the global detector registry, creating it if needed."""
    global _registry
    if _registry is None:
        _registry = DetectorRegistry()
        _register_default_detectors(_registry)
    return _registry


def _register_default_detectors(registry: DetectorRegistry) -> None:
    """Register all default detectors."""
    # Import here to avoid circular imports
    from .generic import GenericDetector
    from .screenshot import ScreenshotDetector
    from .arxiv import ArxivDetector
    from .invoice import InvoiceDetector
    from .book import BookDetector

    # Register in priority order (more specific first)
    registry.register(ScreenshotDetector())  # priority=10
    registry.register(ArxivDetector())  # priority=10
    registry.register(InvoiceDetector())  # priority=15
    registry.register(BookDetector())  # priority=20
    registry.register(GenericDetector())  # priority=50


__all__ = [
    "BaseDetector",
    "DetectorRegistry",
    "CONFIDENCE_HIGH",
    "CONFIDENCE_MEDIUM",
    "CONFIDENCE_LOW",
    "get_registry",
]
