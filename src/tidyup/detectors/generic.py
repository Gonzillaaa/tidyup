"""Generic extension-based detector.

This detector categorizes files based on their file extension.
"""

from typing import Optional

from ..models import DetectionResult, FileInfo
from .base import BaseDetector, CONFIDENCE_HIGH, CONFIDENCE_MEDIUM


# Extension to category mapping
EXTENSION_MAP: dict[str, tuple[str, float]] = {
    # Documents (CONFIDENCE_MEDIUM - could be more specific types)
    "pdf": ("01_Documents", CONFIDENCE_MEDIUM),
    "doc": ("01_Documents", CONFIDENCE_MEDIUM),
    "docx": ("01_Documents", CONFIDENCE_MEDIUM),
    "txt": ("01_Documents", CONFIDENCE_MEDIUM),
    "rtf": ("01_Documents", CONFIDENCE_MEDIUM),
    "odt": ("01_Documents", CONFIDENCE_MEDIUM),
    "md": ("01_Documents", CONFIDENCE_MEDIUM),
    "pages": ("01_Documents", CONFIDENCE_MEDIUM),
    # Spreadsheets/Presentations (Documents)
    "xls": ("01_Documents", CONFIDENCE_MEDIUM),
    "xlsx": ("01_Documents", CONFIDENCE_MEDIUM),
    "ppt": ("01_Documents", CONFIDENCE_MEDIUM),
    "pptx": ("01_Documents", CONFIDENCE_MEDIUM),
    "key": ("01_Documents", CONFIDENCE_MEDIUM),
    "numbers": ("01_Documents", CONFIDENCE_MEDIUM),
    # Images
    "jpg": ("02_Images", CONFIDENCE_HIGH),
    "jpeg": ("02_Images", CONFIDENCE_HIGH),
    "png": ("02_Images", CONFIDENCE_HIGH),
    "gif": ("02_Images", CONFIDENCE_HIGH),
    "bmp": ("02_Images", CONFIDENCE_HIGH),
    "webp": ("02_Images", CONFIDENCE_HIGH),
    "svg": ("02_Images", CONFIDENCE_MEDIUM),
    "heic": ("02_Images", CONFIDENCE_HIGH),
    "heif": ("02_Images", CONFIDENCE_HIGH),
    "tiff": ("02_Images", CONFIDENCE_HIGH),
    "tif": ("02_Images", CONFIDENCE_HIGH),
    "ico": ("02_Images", CONFIDENCE_HIGH),
    "raw": ("02_Images", CONFIDENCE_HIGH),
    "cr2": ("02_Images", CONFIDENCE_HIGH),
    "nef": ("02_Images", CONFIDENCE_HIGH),
    # Videos
    "mp4": ("03_Videos", CONFIDENCE_HIGH),
    "mov": ("03_Videos", CONFIDENCE_HIGH),
    "avi": ("03_Videos", CONFIDENCE_HIGH),
    "mkv": ("03_Videos", CONFIDENCE_HIGH),
    "wmv": ("03_Videos", CONFIDENCE_HIGH),
    "webm": ("03_Videos", CONFIDENCE_HIGH),
    "m4v": ("03_Videos", CONFIDENCE_HIGH),
    "flv": ("03_Videos", CONFIDENCE_HIGH),
    # Audio
    "mp3": ("04_Audio", CONFIDENCE_HIGH),
    "wav": ("04_Audio", CONFIDENCE_HIGH),
    "flac": ("04_Audio", CONFIDENCE_HIGH),
    "aac": ("04_Audio", CONFIDENCE_HIGH),
    "ogg": ("04_Audio", CONFIDENCE_HIGH),
    "m4a": ("04_Audio", CONFIDENCE_HIGH),
    "wma": ("04_Audio", CONFIDENCE_HIGH),
    "aiff": ("04_Audio", CONFIDENCE_HIGH),
    # Archives
    "zip": ("05_Archives", CONFIDENCE_MEDIUM),  # Could contain books
    "rar": ("05_Archives", CONFIDENCE_MEDIUM),
    "7z": ("05_Archives", CONFIDENCE_MEDIUM),
    "tar": ("05_Archives", CONFIDENCE_HIGH),
    "gz": ("05_Archives", CONFIDENCE_HIGH),
    "bz2": ("05_Archives", CONFIDENCE_HIGH),
    "xz": ("05_Archives", CONFIDENCE_HIGH),
    "tgz": ("05_Archives", CONFIDENCE_HIGH),
    # Code
    "py": ("06_Code", CONFIDENCE_HIGH),
    "js": ("06_Code", CONFIDENCE_HIGH),
    "ts": ("06_Code", CONFIDENCE_HIGH),
    "java": ("06_Code", CONFIDENCE_HIGH),
    "c": ("06_Code", CONFIDENCE_HIGH),
    "cpp": ("06_Code", CONFIDENCE_HIGH),
    "h": ("06_Code", CONFIDENCE_HIGH),
    "go": ("06_Code", CONFIDENCE_HIGH),
    "rs": ("06_Code", CONFIDENCE_HIGH),
    "rb": ("06_Code", CONFIDENCE_HIGH),
    "php": ("06_Code", CONFIDENCE_HIGH),
    "swift": ("06_Code", CONFIDENCE_HIGH),
    "kt": ("06_Code", CONFIDENCE_HIGH),
    "html": ("06_Code", CONFIDENCE_MEDIUM),
    "css": ("06_Code", CONFIDENCE_MEDIUM),
    "scss": ("06_Code", CONFIDENCE_MEDIUM),
    "sh": ("06_Code", CONFIDENCE_HIGH),
    "bash": ("06_Code", CONFIDENCE_HIGH),
    # Books
    "epub": ("07_Books", CONFIDENCE_HIGH),
    "mobi": ("07_Books", CONFIDENCE_HIGH),
    "azw": ("07_Books", CONFIDENCE_HIGH),
    "azw3": ("07_Books", CONFIDENCE_HIGH),
    "fb2": ("07_Books", CONFIDENCE_HIGH),
    # Data
    "csv": ("08_Data", CONFIDENCE_HIGH),
    "json": ("08_Data", CONFIDENCE_MEDIUM),
    "xml": ("08_Data", CONFIDENCE_MEDIUM),
    "yaml": ("08_Data", CONFIDENCE_MEDIUM),
    "yml": ("08_Data", CONFIDENCE_MEDIUM),
    "sql": ("08_Data", CONFIDENCE_HIGH),
    "db": ("08_Data", CONFIDENCE_HIGH),
    "sqlite": ("08_Data", CONFIDENCE_HIGH),
    "sqlite3": ("08_Data", CONFIDENCE_HIGH),
}


class GenericDetector(BaseDetector):
    """Extension-based file detector.

    Categorizes files based on their file extension using a
    predefined mapping.
    """

    priority = 50  # Lower priority than specialized detectors

    @property
    def name(self) -> str:
        return "GenericDetector"

    def detect(self, file: FileInfo) -> Optional[DetectionResult]:
        """Detect file type by extension.

        Args:
            file: FileInfo for the file to detect.

        Returns:
            DetectionResult if extension is recognized, None otherwise.
        """
        ext = file.extension.lower()

        if ext in EXTENSION_MAP:
            category, confidence = EXTENSION_MAP[ext]
            return DetectionResult(
                category=category,
                confidence=confidence,
                detector_name=self.name,
            )

        # Unknown extension
        return DetectionResult(
            category="99_Unsorted",
            confidence=0.3,
            detector_name=self.name,
            reason=f"Unknown extension: .{ext}" if ext else "No file extension",
        )
