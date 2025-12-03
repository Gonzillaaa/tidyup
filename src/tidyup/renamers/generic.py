"""Generic renamer for all file types.

This is the fallback renamer used when no specialized renamer matches.
"""


from ..models import DetectionResult, FileInfo, RenameResult
from ..utils import sanitize_filename
from .base import BaseRenamer, format_date


class GenericRenamer(BaseRenamer):
    """Generic renamer that uses date and sanitized filename.

    Pattern: {date}_{sanitized_name}.{ext}

    This renamer is used as a fallback for files without
    specialized renamers.
    """

    @property
    def name(self) -> str:
        return "GenericRenamer"

    def rename(
        self,
        file: FileInfo,
        detection: DetectionResult,
    ) -> RenameResult | None:
        """Generate a new filename using date and sanitized name.

        Args:
            file: FileInfo for the file to rename.
            detection: DetectionResult from category detection.

        Returns:
            RenameResult if file should be renamed, None otherwise.
        """
        if not self.should_rename(file):
            return None

        stem = file.path.stem
        ext = file.extension

        # Generate new name based on date and sanitized name
        date_str = format_date(file.modified)
        sanitized = sanitize_filename(stem)

        # If sanitized name is too short or empty, use generic name
        if len(sanitized) < 3:
            new_stem = f"{date_str}_file"
        else:
            new_stem = f"{date_str}_{sanitized}"

        new_name = f"{new_stem}.{ext}" if ext else new_stem

        if new_name == file.name:
            return None

        return RenameResult(
            original_name=file.name,
            new_name=new_name,
            renamer_name=self.name,
            date_extracted=file.modified.date(),
        )
