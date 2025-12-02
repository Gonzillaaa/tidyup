"""Core engine for Tidy.

This module contains the main orchestration logic that ties together
file discovery, detection, renaming, moving, and logging.
"""

from pathlib import Path
from typing import Optional

from .discovery import discover_files
from .logger import ActionLogger
from .models import Action, DetectionResult, FileInfo, RenameResult, RunResult
from .operations import (
    DEFAULT_FOLDERS,
    ensure_dest_structure,
    is_duplicate,
    move_to_duplicates,
    safe_move,
    safe_rename,
)
from .utils import format_date, is_ugly_filename, sanitize_filename


# Simple extension-based category mapping (placeholder until detectors are implemented)
EXTENSION_CATEGORIES = {
    # Documents
    "pdf": ("01_Documents", 0.9),
    "doc": ("01_Documents", 0.9),
    "docx": ("01_Documents", 0.9),
    "txt": ("01_Documents", 0.8),
    "rtf": ("01_Documents", 0.8),
    "odt": ("01_Documents", 0.8),
    "xls": ("01_Documents", 0.8),
    "xlsx": ("01_Documents", 0.8),
    "ppt": ("01_Documents", 0.8),
    "pptx": ("01_Documents", 0.8),
    "csv": ("01_Documents", 0.7),
    # Images
    "jpg": ("02_Images", 0.95),
    "jpeg": ("02_Images", 0.95),
    "png": ("02_Images", 0.95),
    "gif": ("02_Images", 0.95),
    "bmp": ("02_Images", 0.9),
    "webp": ("02_Images", 0.9),
    "svg": ("02_Images", 0.85),
    "heic": ("02_Images", 0.95),
    "heif": ("02_Images", 0.95),
    # Videos
    "mp4": ("03_Videos", 0.95),
    "mov": ("03_Videos", 0.95),
    "avi": ("03_Videos", 0.9),
    "mkv": ("03_Videos", 0.9),
    "wmv": ("03_Videos", 0.9),
    "webm": ("03_Videos", 0.9),
    # Audio
    "mp3": ("04_Audio", 0.95),
    "wav": ("04_Audio", 0.9),
    "flac": ("04_Audio", 0.9),
    "aac": ("04_Audio", 0.9),
    "ogg": ("04_Audio", 0.85),
    "m4a": ("04_Audio", 0.9),
    # Archives
    "zip": ("05_Archives", 0.9),
    "rar": ("05_Archives", 0.9),
    "7z": ("05_Archives", 0.9),
    "tar": ("05_Archives", 0.9),
    "gz": ("05_Archives", 0.85),
    "bz2": ("05_Archives", 0.85),
    # Code
    "py": ("06_Code", 0.9),
    "js": ("06_Code", 0.9),
    "ts": ("06_Code", 0.9),
    "java": ("06_Code", 0.9),
    "c": ("06_Code", 0.9),
    "cpp": ("06_Code", 0.9),
    "h": ("06_Code", 0.85),
    "go": ("06_Code", 0.9),
    "rs": ("06_Code", 0.9),
    "rb": ("06_Code", 0.9),
    "html": ("06_Code", 0.8),
    "css": ("06_Code", 0.8),
    "json": ("06_Code", 0.7),
    "yaml": ("06_Code", 0.7),
    "yml": ("06_Code", 0.7),
    # Books
    "epub": ("07_Books", 0.95),
    "mobi": ("07_Books", 0.95),
    "azw": ("07_Books", 0.9),
    "azw3": ("07_Books", 0.9),
    # Data
    "db": ("08_Data", 0.8),
    "sqlite": ("08_Data", 0.85),
    "sql": ("08_Data", 0.8),
}


class Engine:
    """Main engine for organizing files.

    Orchestrates the full pipeline: discover files → detect category
    → rename → move → log actions.

    Attributes:
        source: Source directory to process.
        destination: Destination directory (None for rename-only mode).
        options: CLI options dictionary.
        dry_run: Whether to preview without making changes.
        move_only: Only move files, don't rename.
        rename_only: Only rename files, don't move.
        skip_uncertain: Skip files with low confidence.
        verbose: Enable verbose output.
        confidence_threshold: Minimum confidence for certain detection.
    """

    def __init__(
        self,
        source: Path,
        destination: Optional[Path] = None,
        options: Optional[dict] = None,
    ) -> None:
        """Initialize the engine.

        Args:
            source: Source directory to process.
            destination: Destination directory (optional for rename-only).
            options: CLI options dictionary.
        """
        self.source = source
        self.destination = destination
        self.options = options or {}

        # Extract options
        self.dry_run = self.options.get("dry_run", False)
        self.move_only = self.options.get("move", False)
        self.rename_only = self.options.get("rename", False)
        self.skip_uncertain = self.options.get("skip", False)
        self.verbose = self.options.get("verbose", False)
        self.limit = self.options.get("limit")

        self.confidence_threshold = 0.7

        # Determine destination
        if self.destination is None and not self.rename_only:
            self.destination = Path.home() / "Documents" / "Organized"

    def detect_category(self, file: FileInfo) -> DetectionResult:
        """Detect the category for a file.

        Uses simple extension-based detection as a placeholder
        until the full detector framework is implemented.

        Args:
            file: FileInfo for the file to detect.

        Returns:
            DetectionResult with category and confidence.
        """
        ext = file.extension.lower()

        if ext in EXTENSION_CATEGORIES:
            category, confidence = EXTENSION_CATEGORIES[ext]
            return DetectionResult(
                category=category,
                confidence=confidence,
                detector_name="ExtensionDetector",
            )

        # Unknown extension
        return DetectionResult(
            category="99_Unsorted",
            confidence=0.3,
            detector_name="ExtensionDetector",
            reason=f"Unknown extension: .{ext}" if ext else "No file extension",
        )

    def generate_new_name(self, file: FileInfo, detection: DetectionResult) -> Optional[RenameResult]:
        """Generate a new filename for a file.

        Args:
            file: FileInfo for the file.
            detection: DetectionResult from category detection.

        Returns:
            RenameResult if file should be renamed, None otherwise.
        """
        stem = file.path.stem
        ext = file.extension

        # Check if filename is "ugly" (auto-generated)
        if not is_ugly_filename(stem):
            # Filename looks fine, don't rename
            return None

        # Generate new name based on date and sanitized name
        date_str = format_date(file.modified)

        # Try to extract something useful from the name
        # For now, just use the date
        new_stem = f"{date_str}_{sanitize_filename(stem)}"

        new_name = f"{new_stem}.{ext}" if ext else new_stem

        if new_name == file.name:
            return None

        return RenameResult(
            original_name=file.name,
            new_name=new_name,
            renamer_name="DefaultRenamer",
            date_extracted=file.modified.date(),
        )

    def process_file(
        self,
        file: FileInfo,
        logger: ActionLogger,
    ) -> Optional[Action]:
        """Process a single file through the pipeline.

        Args:
            file: FileInfo for the file to process.
            logger: ActionLogger to record the action.

        Returns:
            Action taken, or None if file was skipped.
        """
        # Step 1: Detect category
        detection = self.detect_category(file)

        # Step 2: Handle uncertain detections
        if not detection.is_confident(self.confidence_threshold):
            if self.skip_uncertain:
                # Skip uncertain files when --skip is set
                action = Action(
                    file=file,
                    detection=detection,
                    source_path=file.path,
                    dest_path=file.path,  # Not moved
                    status="skipped",
                )
                logger.log_action(action)
                return action

        # Step 3: Determine rename (unless move-only mode)
        rename_result = None
        if not self.move_only:
            rename_result = self.generate_new_name(file, detection)

        # Step 4: Determine final filename
        final_name = rename_result.new_name if rename_result else file.name

        # Step 5: Determine destination path
        if self.rename_only:
            # Rename in place
            dest_path = file.path.parent / final_name
        else:
            # Move to destination
            dest_path = self.destination / detection.category / final_name

        # Step 6: Check for duplicates (only when moving)
        if not self.rename_only and self.destination:
            dest_folder = self.destination / detection.category
            if dest_folder.exists():
                existing = is_duplicate(file.path, dest_folder)
                if existing:
                    logger.log_duplicate()
                    # Move to duplicates folder
                    if not self.dry_run:
                        final_path = move_to_duplicates(file.path, self.destination)
                    else:
                        final_path = self.destination / "99_Unsorted" / "_duplicates" / file.name

                    action = Action(
                        file=file,
                        detection=detection,
                        source_path=file.path,
                        dest_path=final_path,
                        status="success",
                        rename=rename_result,
                    )
                    logger.log_action(action)
                    return action

        # Step 7: Execute the action (unless dry run)
        try:
            if not self.dry_run:
                if self.rename_only:
                    if rename_result:
                        final_path = safe_rename(file.path, final_name)
                    else:
                        final_path = file.path
                else:
                    # Move (and optionally rename)
                    final_path = safe_move(file.path, dest_path)
            else:
                final_path = dest_path

            action = Action(
                file=file,
                detection=detection,
                source_path=file.path,
                dest_path=final_path,
                status="success",
                rename=rename_result,
            )

        except (OSError, PermissionError) as e:
            action = Action(
                file=file,
                detection=detection,
                source_path=file.path,
                dest_path=dest_path,
                status="error",
                rename=rename_result,
                error=str(e),
            )

        logger.log_action(action)
        return action

    def run(self) -> RunResult:
        """Run the engine to process all files.

        Returns:
            RunResult containing all actions and summary.
        """
        # Ensure destination structure exists (unless dry-run or rename-only)
        if not self.rename_only and self.destination and not self.dry_run:
            ensure_dest_structure(self.destination, DEFAULT_FOLDERS)

        # Create logger
        logger = ActionLogger(
            source=self.source,
            destination=self.destination or self.source,
            options=self.options,
        )

        # Discover and process files
        for file in discover_files(self.source, limit=self.limit):
            self.process_file(file, logger)

        # Save log (unless dry-run)
        if not self.dry_run:
            logger.save()

        return logger.get_run_result()
