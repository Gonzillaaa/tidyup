"""Installer/application detector.

Detects installer and application files by extension.
"""

from typing import Optional

from ..models import DetectionResult, FileInfo
from .base import BaseDetector, CONFIDENCE_HIGH


# Installer extensions by platform
INSTALLER_EXTENSIONS = {
    # macOS
    "dmg",  # Disk image
    "pkg",  # Installer package
    "app",  # Application bundle (rare as file)
    # Windows
    "exe",  # Executable
    "msi",  # Windows Installer
    "msix",  # Modern Windows package
    # Linux
    "deb",  # Debian package
    "rpm",  # Red Hat package
    "appimage",  # AppImage
    "flatpak",  # Flatpak bundle
    "snap",  # Snap package
}


class InstallerDetector(BaseDetector):
    """Detector for installer and application files.

    Identifies installers by their file extension across
    macOS, Windows, and Linux platforms.
    """

    priority = 15  # Higher than generic, catches before Archives

    @property
    def name(self) -> str:
        return "InstallerDetector"

    def detect(self, file: FileInfo) -> Optional[DetectionResult]:
        """Detect if file is an installer.

        Args:
            file: FileInfo for the file to detect.

        Returns:
            DetectionResult if file is an installer,
            None otherwise.
        """
        ext = file.extension.lower()

        if ext in INSTALLER_EXTENSIONS:
            return DetectionResult(
                category="Installers",
                confidence=CONFIDENCE_HIGH,
                detector_name=self.name,
                reason=f"Installer format (.{ext})",
            )

        return None
