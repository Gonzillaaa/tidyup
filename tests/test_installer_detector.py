"""Tests for InstallerDetector."""

import pytest
from pathlib import Path

from tidyup.models import FileInfo
from tidyup.detectors.installer import InstallerDetector, INSTALLER_EXTENSIONS
from tidyup.detectors.base import CONFIDENCE_HIGH


class TestInstallerDetector:
    """Tests for InstallerDetector."""

    def test_detects_dmg(self, tmp_path: Path) -> None:
        """Detects macOS disk images."""
        detector = InstallerDetector()
        file_path = tmp_path / "App.dmg"
        file_path.write_bytes(b"content")
        file = FileInfo.from_path(file_path)

        result = detector.detect(file)

        assert result is not None
        assert result.category == "Installers"
        assert result.confidence == CONFIDENCE_HIGH

    def test_detects_pkg(self, tmp_path: Path) -> None:
        """Detects macOS installer packages."""
        detector = InstallerDetector()
        file_path = tmp_path / "installer.pkg"
        file_path.write_bytes(b"content")
        file = FileInfo.from_path(file_path)

        result = detector.detect(file)

        assert result is not None
        assert result.category == "Installers"

    def test_detects_exe(self, tmp_path: Path) -> None:
        """Detects Windows executables."""
        detector = InstallerDetector()
        file_path = tmp_path / "setup.exe"
        file_path.write_bytes(b"content")
        file = FileInfo.from_path(file_path)

        result = detector.detect(file)

        assert result is not None
        assert result.category == "Installers"

    def test_detects_msi(self, tmp_path: Path) -> None:
        """Detects Windows installer packages."""
        detector = InstallerDetector()
        file_path = tmp_path / "program.msi"
        file_path.write_bytes(b"content")
        file = FileInfo.from_path(file_path)

        result = detector.detect(file)

        assert result is not None
        assert result.category == "Installers"

    def test_detects_deb(self, tmp_path: Path) -> None:
        """Detects Debian packages."""
        detector = InstallerDetector()
        file_path = tmp_path / "package.deb"
        file_path.write_bytes(b"content")
        file = FileInfo.from_path(file_path)

        result = detector.detect(file)

        assert result is not None
        assert result.category == "Installers"

    def test_detects_appimage(self, tmp_path: Path) -> None:
        """Detects Linux AppImages."""
        detector = InstallerDetector()
        file_path = tmp_path / "App.appimage"
        file_path.write_bytes(b"content")
        file = FileInfo.from_path(file_path)

        result = detector.detect(file)

        assert result is not None
        assert result.category == "Installers"

    def test_ignores_non_installer(self, tmp_path: Path) -> None:
        """Ignores non-installer files."""
        detector = InstallerDetector()
        file_path = tmp_path / "document.pdf"
        file_path.write_bytes(b"content")
        file = FileInfo.from_path(file_path)

        result = detector.detect(file)

        assert result is None

    def test_case_insensitive(self, tmp_path: Path) -> None:
        """Extension matching is case-insensitive."""
        detector = InstallerDetector()
        file_path = tmp_path / "App.DMG"
        file_path.write_bytes(b"content")
        file = FileInfo.from_path(file_path)

        result = detector.detect(file)

        assert result is not None
        assert result.category == "Installers"

    def test_priority_is_set(self) -> None:
        """Detector has correct priority."""
        detector = InstallerDetector()
        assert detector.priority == 15

    def test_name_property(self) -> None:
        """Name property returns correct value."""
        detector = InstallerDetector()
        assert detector.name == "InstallerDetector"

    def test_all_extensions_covered(self, tmp_path: Path) -> None:
        """All defined extensions are detected."""
        detector = InstallerDetector()

        for ext in INSTALLER_EXTENSIONS:
            file_path = tmp_path / f"test.{ext}"
            file_path.write_bytes(b"content")
            file = FileInfo.from_path(file_path)

            result = detector.detect(file)

            assert result is not None, f"Failed to detect .{ext}"
            assert result.category == "Installers", f"Wrong category for .{ext}"
