"""Book renamer.

Renames book files using metadata (title, author, year).
"""

import re
import xml.etree.ElementTree as ET
import zipfile

from ..models import DetectionResult, FileInfo, RenameResult
from ..utils import sanitize_filename
from .base import BaseRenamer

# Maximum title length for filename
MAX_TITLE_LENGTH = 60
MAX_AUTHOR_LENGTH = 30


class BookRenamer(BaseRenamer):
    """Renamer for book files.

    Renames books using pattern: {year}_{title}_{author}.ext
    Extracts metadata from PDF and EPUB files.
    """

    @property
    def name(self) -> str:
        return "BookRenamer"

    def rename(
        self,
        file: FileInfo,
        detection: DetectionResult,
    ) -> RenameResult | None:
        """Generate a new filename for a book.

        Args:
            file: FileInfo for the file to rename.
            detection: DetectionResult from category detection.

        Returns:
            RenameResult if file should be renamed, None otherwise.
        """
        ext = file.extension.lower()

        # Extract metadata based on file type
        metadata = None
        if ext == "pdf":
            metadata = self._extract_pdf_metadata(file)
        elif ext == "epub":
            metadata = self._extract_epub_metadata(file)

        if not metadata:
            # Fall back to filename-based metadata
            metadata = self._extract_from_filename(file)

        if not metadata:
            return None

        # Build new filename
        new_name = self._build_filename(metadata, ext)
        if new_name == file.name:
            return None

        return RenameResult(
            original_name=file.name,
            new_name=new_name,
            renamer_name=self.name,
            title_extracted=metadata.get("title"),
        )

    def _extract_pdf_metadata(self, file: FileInfo) -> dict | None:
        """Extract metadata from PDF file."""
        try:
            import pypdf

            with open(file.path, "rb") as f:
                reader = pypdf.PdfReader(f)
                meta = reader.metadata

                if not meta:
                    return None

                title = meta.get("/Title", "").strip() if meta.get("/Title") else None
                author = meta.get("/Author", "").strip() if meta.get("/Author") else None
                creation_date = meta.get("/CreationDate")

                # Parse PDF date format (D:YYYYMMDDHHmmSS)
                year = None
                if creation_date and isinstance(creation_date, str):
                    match = re.search(r"D:(\d{4})", creation_date)
                    if match:
                        year = match.group(1)

                # Need at least a title
                if not title or len(title) < 3:
                    return None

                return {
                    "title": title,
                    "author": author,
                    "year": year,
                }

        except Exception:
            return None

    def _extract_epub_metadata(self, file: FileInfo) -> dict | None:
        """Extract metadata from EPUB file."""
        try:
            with zipfile.ZipFile(file.path, "r") as zf:
                # Find the OPF file
                opf_path = self._find_opf_in_epub(zf)
                if not opf_path:
                    return None

                # Parse the OPF file
                with zf.open(opf_path) as opf_file:
                    tree = ET.parse(opf_file)
                    root = tree.getroot()

                    # Handle XML namespaces
                    ns = {
                        "opf": "http://www.idpf.org/2007/opf",
                        "dc": "http://purl.org/dc/elements/1.1/",
                    }

                    # Try to find metadata
                    metadata = root.find("opf:metadata", ns) or root.find("metadata")
                    if metadata is None:
                        # Try without namespace
                        for child in root:
                            if "metadata" in child.tag.lower():
                                metadata = child
                                break

                    if metadata is None:
                        return None

                    # Extract fields
                    title = self._find_dc_element(metadata, "title", ns)
                    author = self._find_dc_element(metadata, "creator", ns)
                    date = self._find_dc_element(metadata, "date", ns)

                    # Extract year from date
                    year = None
                    if date:
                        match = re.search(r"(\d{4})", date)
                        if match:
                            year = match.group(1)

                    if not title or len(title) < 3:
                        return None

                    return {
                        "title": title,
                        "author": author,
                        "year": year,
                    }

        except Exception:
            return None

    def _find_opf_in_epub(self, zf: zipfile.ZipFile) -> str | None:
        """Find the OPF file path in an EPUB."""
        try:
            # First, look in META-INF/container.xml
            container_path = "META-INF/container.xml"
            if container_path in zf.namelist():
                with zf.open(container_path) as container_file:
                    tree = ET.parse(container_file)
                    root = tree.getroot()

                    # Find rootfile element
                    for rootfile in root.iter():
                        if "rootfile" in rootfile.tag:
                            opf_path = rootfile.get("full-path")
                            if opf_path:
                                return opf_path

            # Fallback: look for .opf files
            for name in zf.namelist():
                if name.endswith(".opf"):
                    return name

        except Exception:
            pass

        return None

    def _find_dc_element(
        self,
        metadata: ET.Element,
        name: str,
        ns: dict,
    ) -> str | None:
        """Find a Dublin Core element in metadata."""
        # Try with namespace
        elem = metadata.find(f"dc:{name}", ns)
        if elem is not None and elem.text:
            return elem.text.strip()

        # Try without namespace prefix
        for child in metadata:
            if name in child.tag.lower():
                if child.text:
                    return child.text.strip()

        return None

    def _extract_from_filename(self, file: FileInfo) -> dict | None:
        """Extract metadata from filename patterns."""
        stem = file.path.stem

        # Try to find year in filename
        year_match = re.search(r"\b(19|20)\d{2}\b", stem)
        year = year_match.group(0) if year_match else None

        # Clean up the stem as title
        # Remove common patterns
        title = stem
        title = re.sub(r"\b(19|20)\d{2}\b", "", title)  # Remove year
        title = re.sub(r"[_\-]+", " ", title)  # Replace separators
        title = re.sub(r"\s+", " ", title)  # Normalize spaces
        title = title.strip()

        if len(title) < 3:
            return None

        return {
            "title": title,
            "author": None,
            "year": year or str(file.modified.year),
        }

    def _build_filename(self, metadata: dict, ext: str) -> str:
        """Build filename from metadata."""
        title = metadata.get("title", "")
        author = metadata.get("author")
        year = metadata.get("year")

        # Truncate title if too long
        if len(title) > MAX_TITLE_LENGTH:
            title = title[:MAX_TITLE_LENGTH].rsplit(" ", 1)[0]

        # Clean up title
        title = sanitize_filename(title)

        # Build parts
        parts = []
        if year:
            parts.append(year)
        parts.append(title)
        if author:
            # Truncate author if needed
            if len(author) > MAX_AUTHOR_LENGTH:
                author = author[:MAX_AUTHOR_LENGTH].rsplit(" ", 1)[0]
            author = sanitize_filename(author)
            parts.append(author)

        # Join with underscores
        name = "_".join(parts)

        # Add extension
        return f"{name}.{ext}"
