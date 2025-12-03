"""Image renamer with EXIF date extraction.

Extracts date from image EXIF metadata for smart renaming.
"""

from datetime import datetime
from typing import Optional

from PIL import Image
from PIL.ExifTags import TAGS

from ..models import DetectionResult, FileInfo, RenameResult
from ..utils import sanitize_filename
from .base import BaseRenamer, format_date


# Image extensions that may contain EXIF
EXIF_EXTENSIONS = {"jpg", "jpeg", "tiff", "tif", "heic", "heif"}


def extract_exif_date(file: FileInfo) -> Optional[datetime]:
    """Extract date from image EXIF metadata.

    Tries multiple EXIF date fields in order of preference.

    Args:
        file: FileInfo for the image file.

    Returns:
        Datetime from EXIF or None.
    """
    try:
        with Image.open(file.path) as img:
            exif_data = img._getexif()
            if not exif_data:
                return None

            # Map tag IDs to names
            exif = {TAGS.get(k, k): v for k, v in exif_data.items()}

            # Try date fields in order of preference
            for field in ["DateTimeOriginal", "DateTimeDigitized", "DateTime"]:
                if field in exif:
                    date_str = exif[field]
                    if isinstance(date_str, str):
                        # Parse EXIF date format: "YYYY:MM:DD HH:MM:SS"
                        try:
                            return datetime.strptime(date_str, "%Y:%m:%d %H:%M:%S")
                        except ValueError:
                            continue

            return None

    except Exception:
        return None


class ImageRenamer(BaseRenamer):
    """Renamer for images using EXIF date.

    Pattern: {exif_date}_{original_name}.{ext}

    Uses EXIF DateTimeOriginal if available, falls back to file
    modified date.
    """

    @property
    def name(self) -> str:
        return "ImageRenamer"

    def rename(
        self,
        file: FileInfo,
        detection: DetectionResult,
    ) -> Optional[RenameResult]:
        """Generate a new filename using EXIF date.

        Args:
            file: FileInfo for the image file.
            detection: DetectionResult from category detection.

        Returns:
            RenameResult if file should be renamed, None otherwise.
        """
        if not self.should_rename(file):
            return None

        ext = file.extension.lower()

        # Try to extract EXIF date for supported formats
        exif_date = None
        if ext in EXIF_EXTENSIONS:
            exif_date = extract_exif_date(file)

        # Determine the date to use
        if exif_date:
            date_str = format_date(exif_date)
            date_extracted = exif_date.date()
        else:
            date_str = format_date(file.modified)
            date_extracted = file.modified.date()

        # Build new filename
        sanitized_name = sanitize_filename(file.path.stem)
        if len(sanitized_name) < 3:
            new_stem = f"{date_str}_image"
        else:
            new_stem = f"{date_str}_{sanitized_name}"

        new_name = f"{new_stem}.{file.extension}" if file.extension else new_stem

        if new_name == file.name:
            return None

        return RenameResult(
            original_name=file.name,
            new_name=new_name,
            renamer_name=self.name,
            date_extracted=date_extracted,
        )
