"""Renamer framework for TidyUp.

This module provides the renamer registry and imports all renamers.
"""

from typing import Optional

from ..models import DetectionResult, FileInfo, RenameResult
from .base import BaseRenamer, format_date, format_datetime


class RenamerRegistry:
    """Registry for file renamers.

    Maps detector names to specialized renamers, with a fallback
    to the generic renamer.

    Attributes:
        renamers: Dict mapping detector names to renamer instances.
        default_renamer: Fallback renamer for unmatched detectors.
    """

    def __init__(self) -> None:
        """Initialize an empty registry."""
        self.renamers: dict[str, BaseRenamer] = {}
        self.default_renamer: Optional[BaseRenamer] = None

    def register(self, detector_name: str, renamer: BaseRenamer) -> None:
        """Register a renamer for a detector.

        Args:
            detector_name: Name of the detector to match.
            renamer: Renamer instance to use.
        """
        self.renamers[detector_name] = renamer

    def set_default(self, renamer: BaseRenamer) -> None:
        """Set the default renamer for unmatched detectors.

        Args:
            renamer: Default renamer instance.
        """
        self.default_renamer = renamer

    def rename(
        self,
        file: FileInfo,
        detection: DetectionResult,
    ) -> Optional[RenameResult]:
        """Rename a file using the appropriate renamer.

        Args:
            file: FileInfo for the file to rename.
            detection: DetectionResult from category detection.

        Returns:
            RenameResult if file should be renamed, None otherwise.
        """
        # Try to find a specialized renamer
        renamer = self.renamers.get(detection.detector_name)

        if renamer:
            result = renamer.rename(file, detection)
            if result:
                return result

        # Fall back to default renamer
        if self.default_renamer:
            return self.default_renamer.rename(file, detection)

        return None


# Global registry instance
_registry: Optional[RenamerRegistry] = None


def get_renamer_registry() -> RenamerRegistry:
    """Get the global renamer registry, creating it if needed."""
    global _registry
    if _registry is None:
        _registry = RenamerRegistry()
        _register_default_renamers(_registry)
    return _registry


def _register_default_renamers(registry: RenamerRegistry) -> None:
    """Register all default renamers."""
    from .generic import GenericRenamer
    from .pdf import PDFRenamer
    from .image import ImageRenamer
    from .screenshot import ScreenshotRenamer
    from .arxiv import ArxivRenamer
    from .invoice import InvoiceRenamer

    # Set default renamer
    registry.set_default(GenericRenamer())

    # Register specialized renamers by detector name
    registry.register("ScreenshotDetector", ScreenshotRenamer())
    registry.register("ArxivDetector", ArxivRenamer())
    registry.register("InvoiceDetector", InvoiceRenamer())

    # PDF renamer for documents detected by GenericDetector
    # (but only if they're PDFs - handled in PDFRenamer)
    registry.register("GenericDetector", PDFRenamer())

    # Image renamer for images
    # Note: Screenshots are handled by ScreenshotRenamer first
    # This is for regular images detected by GenericDetector


__all__ = [
    "BaseRenamer",
    "RenamerRegistry",
    "format_date",
    "format_datetime",
    "get_renamer_registry",
]
