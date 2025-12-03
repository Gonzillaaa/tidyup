"""Core engine for Tidy.

This module contains the main orchestration logic that ties together
file discovery, detection, renaming, moving, and logging.
"""

from pathlib import Path
from typing import Optional

from .detectors import get_registry
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
from .renamers import get_renamer_registry


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

        Uses the detector registry to run all registered detectors
        and return the best result.

        Args:
            file: FileInfo for the file to detect.

        Returns:
            DetectionResult with category and confidence.
        """
        registry = get_registry()
        return registry.detect(file)

    def generate_new_name(self, file: FileInfo, detection: DetectionResult) -> Optional[RenameResult]:
        """Generate a new filename for a file.

        Uses the renamer registry to find the appropriate renamer
        based on the detection result.

        Args:
            file: FileInfo for the file.
            detection: DetectionResult from category detection.

        Returns:
            RenameResult if file should be renamed, None otherwise.
        """
        registry = get_renamer_registry()
        return registry.rename(file, detection)

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
