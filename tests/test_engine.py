"""Tests for the engine module."""

import pytest
from pathlib import Path
from unittest.mock import patch

from tidyup.engine import Engine, EXTENSION_CATEGORIES
from tidyup.models import FileInfo


class TestEngineInit:
    """Tests for Engine initialization."""

    def test_default_destination(self, tmp_path: Path) -> None:
        """Uses default destination when not specified."""
        engine = Engine(tmp_path)

        assert engine.destination == Path.home() / "Documents" / "Organized"

    def test_custom_destination(self, tmp_path: Path) -> None:
        """Uses custom destination when specified."""
        dest = tmp_path / "custom_dest"
        engine = Engine(tmp_path, destination=dest)

        assert engine.destination == dest

    def test_rename_only_no_destination(self, tmp_path: Path) -> None:
        """Rename-only mode doesn't require destination."""
        engine = Engine(tmp_path, options={"rename": True})

        # Destination should still be None for rename-only
        assert engine.rename_only is True

    def test_extracts_options(self, tmp_path: Path) -> None:
        """Extracts all options correctly."""
        options = {
            "dry_run": True,
            "move": True,
            "rename": False,
            "skip": True,
            "verbose": True,
            "limit": 10,
        }
        engine = Engine(tmp_path, options=options)

        assert engine.dry_run is True
        assert engine.move_only is True
        assert engine.rename_only is False
        assert engine.skip_uncertain is True
        assert engine.verbose is True
        assert engine.limit == 10


class TestDetectCategory:
    """Tests for category detection."""

    def test_detects_pdf_as_documents(self, tmp_path: Path, sample_pdf: Path) -> None:
        """PDFs are detected as Documents."""
        engine = Engine(tmp_path)
        file = FileInfo.from_path(sample_pdf)

        result = engine.detect_category(file)

        assert result.category == "01_Documents"
        assert result.confidence >= 0.7

    def test_detects_image_extensions(self, tmp_path: Path) -> None:
        """Image extensions are detected as Images."""
        engine = Engine(tmp_path)

        for ext in ["jpg", "jpeg", "png", "gif"]:
            file_path = tmp_path / f"test.{ext}"
            file_path.write_bytes(b"content")
            file = FileInfo.from_path(file_path)

            result = engine.detect_category(file)

            assert result.category == "02_Images", f"Failed for .{ext}"

    def test_unknown_extension_is_unsorted(self, tmp_path: Path) -> None:
        """Unknown extensions go to Unsorted."""
        engine = Engine(tmp_path)
        file_path = tmp_path / "unknown.xyz123"
        file_path.write_text("content")
        file = FileInfo.from_path(file_path)

        result = engine.detect_category(file)

        assert result.category == "99_Unsorted"
        assert result.confidence < 0.7
        assert result.reason is not None


class TestGenerateNewName:
    """Tests for filename generation."""

    def test_keeps_readable_names(self, tmp_path: Path) -> None:
        """Readable filenames are not renamed."""
        engine = Engine(tmp_path)
        file_path = tmp_path / "Annual_Report_2024.pdf"
        file_path.write_text("content")
        file = FileInfo.from_path(file_path)
        detection = engine.detect_category(file)

        result = engine.generate_new_name(file, detection)

        assert result is None

    def test_renames_ugly_names(self, tmp_path: Path) -> None:
        """Ugly filenames are renamed."""
        engine = Engine(tmp_path)
        file_path = tmp_path / "1743151465964.pdf"
        file_path.write_text("content")
        file = FileInfo.from_path(file_path)
        detection = engine.detect_category(file)

        result = engine.generate_new_name(file, detection)

        assert result is not None
        assert result.new_name != file.name
        assert result.new_name.endswith(".pdf")


class TestProcessFile:
    """Tests for file processing."""

    def test_processes_file_successfully(self, tmp_path: Path) -> None:
        """Processes file and returns success action."""
        source = tmp_path / "source"
        source.mkdir()
        dest = tmp_path / "dest"

        file_path = source / "document.pdf"
        file_path.write_text("content")

        engine = Engine(source, destination=dest, options={"dry_run": True})
        file = FileInfo.from_path(file_path)

        from tidyup.logger import ActionLogger
        logger = ActionLogger(source, dest, {})

        action = engine.process_file(file, logger)

        assert action is not None
        assert action.status == "success"
        assert action.detection.category == "01_Documents"

    def test_skips_uncertain_with_skip_flag(self, tmp_path: Path) -> None:
        """Skips uncertain files when --skip is set."""
        source = tmp_path / "source"
        source.mkdir()

        file_path = source / "unknown.xyz"
        file_path.write_text("content")

        engine = Engine(source, options={"skip": True, "dry_run": True})
        file = FileInfo.from_path(file_path)

        from tidyup.logger import ActionLogger
        logger = ActionLogger(source, source, {})

        action = engine.process_file(file, logger)

        assert action is not None
        assert action.status == "skipped"

    def test_moves_to_unsorted_without_skip(self, tmp_path: Path) -> None:
        """Moves uncertain files to Unsorted without --skip."""
        source = tmp_path / "source"
        source.mkdir()
        dest = tmp_path / "dest"

        file_path = source / "unknown.xyz"
        file_path.write_text("content")

        engine = Engine(source, destination=dest, options={"dry_run": True})
        file = FileInfo.from_path(file_path)

        from tidyup.logger import ActionLogger
        logger = ActionLogger(source, dest, {})

        action = engine.process_file(file, logger)

        assert action is not None
        assert action.status == "success"
        assert "99_Unsorted" in str(action.dest_path)


class TestEngineRun:
    """Tests for engine.run() method."""

    def test_dry_run_doesnt_move_files(self, tmp_path: Path) -> None:
        """Dry run doesn't actually move files."""
        source = tmp_path / "source"
        source.mkdir()
        dest = tmp_path / "dest"

        (source / "file1.pdf").write_text("content1")
        (source / "file2.jpg").write_text("content2")

        engine = Engine(source, destination=dest, options={"dry_run": True})
        result = engine.run()

        # Files should still be in source
        assert (source / "file1.pdf").exists()
        assert (source / "file2.jpg").exists()
        # Destination shouldn't be created
        assert not dest.exists()
        # But result should show what would happen
        assert result.summary.processed == 2

    def test_actually_moves_files(self, tmp_path: Path) -> None:
        """Files are actually moved when not dry run."""
        source = tmp_path / "source"
        source.mkdir()
        dest = tmp_path / "dest"

        (source / "document.pdf").write_text("content")

        with patch("tidyup.engine.ActionLogger.save"):  # Don't save to ~/.tidy
            engine = Engine(source, destination=dest)
            result = engine.run()

        # File should be moved
        assert not (source / "document.pdf").exists()
        assert (dest / "01_Documents" / "document.pdf").exists()
        assert result.summary.moved == 1

    def test_respects_limit(self, tmp_path: Path) -> None:
        """Respects the limit option."""
        source = tmp_path / "source"
        source.mkdir()

        for i in range(10):
            (source / f"file{i:02d}.pdf").write_text(f"content{i}")

        engine = Engine(source, options={"dry_run": True, "limit": 3})
        result = engine.run()

        assert result.summary.processed == 3

    def test_move_only_mode(self, tmp_path: Path) -> None:
        """Move-only mode doesn't rename files."""
        source = tmp_path / "source"
        source.mkdir()
        dest = tmp_path / "dest"

        # Create file with ugly name
        (source / "1234567890123.pdf").write_text("content")

        with patch("tidyup.engine.ActionLogger.save"):
            engine = Engine(source, destination=dest, options={"move": True})
            result = engine.run()

        # File should be moved but not renamed
        assert (dest / "01_Documents" / "1234567890123.pdf").exists()
        assert result.summary.renamed == 0

    def test_rename_only_mode(self, tmp_path: Path) -> None:
        """Rename-only mode doesn't move files."""
        source = tmp_path / "source"
        source.mkdir()

        # Create file with ugly name
        (source / "1234567890123.pdf").write_text("content")

        with patch("tidyup.engine.ActionLogger.save"):
            engine = Engine(source, options={"rename": True})
            result = engine.run()

        # File should stay in source (renamed)
        files = list(source.glob("*.pdf"))
        assert len(files) == 1
        assert files[0].name != "1234567890123.pdf"

    def test_creates_destination_structure(self, tmp_path: Path) -> None:
        """Creates destination folder structure."""
        source = tmp_path / "source"
        source.mkdir()
        dest = tmp_path / "dest"

        (source / "test.pdf").write_text("content")

        with patch("tidyup.engine.ActionLogger.save"):
            engine = Engine(source, destination=dest)
            engine.run()

        # Should have created folder structure
        assert (dest / "01_Documents").is_dir()


class TestExtensionCategories:
    """Tests for the extension category mapping."""

    def test_all_categories_exist(self) -> None:
        """All mapped categories exist in folder structure."""
        from tidyup.operations import DEFAULT_FOLDERS

        folder_names = {f["name"] for f in DEFAULT_FOLDERS}
        folder_numbers = {f["number"] for f in DEFAULT_FOLDERS}

        for ext, (category, _) in EXTENSION_CATEGORIES.items():
            number = int(category.split("_")[0])
            name = category.split("_")[1]

            assert number in folder_numbers, f"Category {category} number not in folders"

    def test_confidence_values_valid(self) -> None:
        """All confidence values are between 0 and 1."""
        for ext, (_, confidence) in EXTENSION_CATEGORIES.items():
            assert 0.0 <= confidence <= 1.0, f"Invalid confidence for .{ext}"
