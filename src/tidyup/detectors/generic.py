"""Generic extension-based detector.

This detector categorizes files based on their file extension.
"""


from ..models import DetectionResult, FileInfo
from .base import CONFIDENCE_HIGH, CONFIDENCE_MEDIUM, BaseDetector

# Extension to category mapping (uses category names, not folder names)
EXTENSION_MAP: dict[str, tuple[str, float]] = {
    # Documents (CONFIDENCE_MEDIUM - could be more specific types)
    "pdf": ("Documents", CONFIDENCE_MEDIUM),
    "doc": ("Documents", CONFIDENCE_MEDIUM),
    "docx": ("Documents", CONFIDENCE_MEDIUM),
    "txt": ("Documents", CONFIDENCE_MEDIUM),
    "rtf": ("Documents", CONFIDENCE_MEDIUM),
    "odt": ("Documents", CONFIDENCE_MEDIUM),
    "md": ("Documents", CONFIDENCE_MEDIUM),
    "pages": ("Documents", CONFIDENCE_MEDIUM),
    # Spreadsheets/Presentations (Documents)
    "xls": ("Documents", CONFIDENCE_MEDIUM),
    "xlsx": ("Documents", CONFIDENCE_MEDIUM),
    "ppt": ("Documents", CONFIDENCE_MEDIUM),
    "pptx": ("Documents", CONFIDENCE_MEDIUM),
    "key": ("Documents", CONFIDENCE_MEDIUM),
    "numbers": ("Documents", CONFIDENCE_MEDIUM),
    # Images
    "jpg": ("Images", CONFIDENCE_HIGH),
    "jpeg": ("Images", CONFIDENCE_HIGH),
    "png": ("Images", CONFIDENCE_HIGH),
    "gif": ("Images", CONFIDENCE_HIGH),
    "bmp": ("Images", CONFIDENCE_HIGH),
    "webp": ("Images", CONFIDENCE_HIGH),
    "svg": ("Images", CONFIDENCE_MEDIUM),
    "heic": ("Images", CONFIDENCE_HIGH),
    "heif": ("Images", CONFIDENCE_HIGH),
    "tiff": ("Images", CONFIDENCE_HIGH),
    "tif": ("Images", CONFIDENCE_HIGH),
    "ico": ("Images", CONFIDENCE_HIGH),
    "raw": ("Images", CONFIDENCE_HIGH),
    "cr2": ("Images", CONFIDENCE_HIGH),
    "nef": ("Images", CONFIDENCE_HIGH),
    # Videos
    "mp4": ("Videos", CONFIDENCE_HIGH),
    "mov": ("Videos", CONFIDENCE_HIGH),
    "avi": ("Videos", CONFIDENCE_HIGH),
    "mkv": ("Videos", CONFIDENCE_HIGH),
    "wmv": ("Videos", CONFIDENCE_HIGH),
    "webm": ("Videos", CONFIDENCE_HIGH),
    "m4v": ("Videos", CONFIDENCE_HIGH),
    "flv": ("Videos", CONFIDENCE_HIGH),
    # Audio
    "mp3": ("Audio", CONFIDENCE_HIGH),
    "wav": ("Audio", CONFIDENCE_HIGH),
    "flac": ("Audio", CONFIDENCE_HIGH),
    "aac": ("Audio", CONFIDENCE_HIGH),
    "ogg": ("Audio", CONFIDENCE_HIGH),
    "m4a": ("Audio", CONFIDENCE_HIGH),
    "wma": ("Audio", CONFIDENCE_HIGH),
    "aiff": ("Audio", CONFIDENCE_HIGH),
    # Archives
    "zip": ("Archives", CONFIDENCE_MEDIUM),  # Could contain books
    "rar": ("Archives", CONFIDENCE_MEDIUM),
    "7z": ("Archives", CONFIDENCE_MEDIUM),
    "tar": ("Archives", CONFIDENCE_HIGH),
    "gz": ("Archives", CONFIDENCE_HIGH),
    "bz2": ("Archives", CONFIDENCE_HIGH),
    "xz": ("Archives", CONFIDENCE_HIGH),
    "tgz": ("Archives", CONFIDENCE_HIGH),
    # Code
    "py": ("Code", CONFIDENCE_HIGH),
    "js": ("Code", CONFIDENCE_HIGH),
    "ts": ("Code", CONFIDENCE_HIGH),
    "java": ("Code", CONFIDENCE_HIGH),
    "c": ("Code", CONFIDENCE_HIGH),
    "cpp": ("Code", CONFIDENCE_HIGH),
    "h": ("Code", CONFIDENCE_HIGH),
    "go": ("Code", CONFIDENCE_HIGH),
    "rs": ("Code", CONFIDENCE_HIGH),
    "rb": ("Code", CONFIDENCE_HIGH),
    "php": ("Code", CONFIDENCE_HIGH),
    "swift": ("Code", CONFIDENCE_HIGH),
    "kt": ("Code", CONFIDENCE_HIGH),
    "html": ("Code", CONFIDENCE_MEDIUM),
    "css": ("Code", CONFIDENCE_MEDIUM),
    "scss": ("Code", CONFIDENCE_MEDIUM),
    "sh": ("Code", CONFIDENCE_HIGH),
    "bash": ("Code", CONFIDENCE_HIGH),
    # Books
    "epub": ("Books", CONFIDENCE_HIGH),
    "mobi": ("Books", CONFIDENCE_HIGH),
    "azw": ("Books", CONFIDENCE_HIGH),
    "azw3": ("Books", CONFIDENCE_HIGH),
    "fb2": ("Books", CONFIDENCE_HIGH),
    # Data
    "csv": ("Data", CONFIDENCE_HIGH),
    "json": ("Data", CONFIDENCE_MEDIUM),
    "xml": ("Data", CONFIDENCE_MEDIUM),
    "yaml": ("Data", CONFIDENCE_MEDIUM),
    "yml": ("Data", CONFIDENCE_MEDIUM),
    "sql": ("Data", CONFIDENCE_HIGH),
    "db": ("Data", CONFIDENCE_HIGH),
    "sqlite": ("Data", CONFIDENCE_HIGH),
    "sqlite3": ("Data", CONFIDENCE_HIGH),
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

    def detect(self, file: FileInfo) -> DetectionResult | None:
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
            category="Unsorted",
            confidence=0.3,
            detector_name=self.name,
            reason=f"Unknown extension: .{ext}" if ext else "No file extension",
        )
