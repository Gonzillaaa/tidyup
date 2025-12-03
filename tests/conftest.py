"""Pytest configuration and fixtures for TidyUp tests."""

import pytest
from pathlib import Path
from click.testing import CliRunner


@pytest.fixture
def cli_runner() -> CliRunner:
    """Provide a Click CLI test runner."""
    return CliRunner()


@pytest.fixture
def temp_source(tmp_path: Path) -> Path:
    """Create a temporary source directory with sample files."""
    source = tmp_path / "source"
    source.mkdir()

    # Create sample files
    (source / "document.pdf").write_bytes(b"%PDF-1.4 fake pdf content")
    (source / "image.png").write_bytes(b"\x89PNG\r\n\x1a\n fake png")
    (source / "data.csv").write_text("col1,col2\nval1,val2")
    (source / "archive.zip").write_bytes(b"PK fake zip")
    (source / "Screenshot 2024-01-15 at 10.30.45.png").write_bytes(b"\x89PNG\r\n\x1a\n")
    (source / "2501.12948v1.pdf").write_bytes(b"%PDF-1.4 arxiv paper")
    (source / ".hidden_file").write_text("hidden")
    (source / ".DS_Store").write_bytes(b"fake ds store")

    return source


@pytest.fixture
def temp_dest(tmp_path: Path) -> Path:
    """Create a temporary destination directory."""
    dest = tmp_path / "dest"
    dest.mkdir()
    return dest


@pytest.fixture
def sample_pdf(tmp_path: Path) -> Path:
    """Create a sample PDF file with basic structure."""
    pdf_path = tmp_path / "sample.pdf"
    # Minimal valid PDF structure
    pdf_content = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [] /Count 0 >>
endobj
xref
0 3
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
trailer
<< /Size 3 /Root 1 0 R >>
startxref
115
%%EOF"""
    pdf_path.write_bytes(pdf_content)
    return pdf_path


@pytest.fixture
def sample_image(tmp_path: Path) -> Path:
    """Create a sample PNG image."""
    img_path = tmp_path / "sample.png"
    # Minimal valid PNG (1x1 transparent pixel)
    png_content = bytes([
        0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,  # PNG signature
        0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52,  # IHDR chunk
        0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,  # 1x1
        0x08, 0x06, 0x00, 0x00, 0x00, 0x1F, 0x15, 0xC4,  # 8-bit RGBA
        0x89, 0x00, 0x00, 0x00, 0x0A, 0x49, 0x44, 0x41,  # IDAT chunk
        0x54, 0x78, 0x9C, 0x63, 0x00, 0x01, 0x00, 0x00,
        0x05, 0x00, 0x01, 0x0D, 0x0A, 0x2D, 0xB4, 0x00,
        0x00, 0x00, 0x00, 0x49, 0x45, 0x4E, 0x44, 0xAE,  # IEND chunk
        0x42, 0x60, 0x82
    ])
    img_path.write_bytes(png_content)
    return img_path
