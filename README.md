# Tidy

A command-line tool to organize, rename, and categorize files from your Downloads folder (or any directory) into a clean, structured destination.

## Features

- **Smart categorization**: Automatically sorts files into logical folders based on type
- **Intelligent renaming**: Cleans up ugly filenames (timestamps, UUIDs, hex strings)
- **Safe by design**: Never deletes files, only moves and renames
- **Dry run mode**: Preview all changes before committing
- **Flexible modes**: Move only, rename only, or both
- **Detailed logging**: Every operation logged to JSON for auditability
- **Duplicate detection**: Identifies duplicates by content hash

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [CLI Reference](#cli-reference)
- [Usage Examples](#usage-examples)
- [Folder Structure](#folder-structure)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Development](#development)

## Installation

### Using pip (from source)

```bash
git clone https://github.com/yourusername/tidyup.git
cd tidyup
pip install -e .
```

### Using pipx (recommended for CLI tools)

[pipx](https://pypa.github.io/pipx/) installs CLI tools in isolated environments:

```bash
# Install pipx if you don't have it
brew install pipx  # macOS
# or: pip install pipx

# Install tidy
cd /path/to/tidy
pipx install -e .
```

### Verify Installation

```bash
tidyup --version
# Output: tidyup, version 0.1.0
```

## Quick Start

```bash
# Preview what would happen (recommended first run)
tidyup ~/Downloads --dry-run

# Actually organize files
tidyup ~/Downloads

# Organize to a specific destination
tidyup ~/Downloads ~/Documents/Organized
```

## CLI Reference

### Main Command

```
tidyup [OPTIONS] SOURCE [DESTINATION]
```

| Argument | Description |
|----------|-------------|
| `SOURCE` | Directory to organize (required) |
| `DESTINATION` | Where to move files (default: `~/Documents/Organized`) |

### Options

| Option | Short | Description |
|--------|-------|-------------|
| `--move` | | Only categorize and move files, keep original names |
| `--rename` | | Only rename files in place, don't move them |
| `--skip` | | Skip files with uncertain categorization (confidence < 70%) |
| `--dry-run` | | Preview changes without actually moving/renaming files |
| `--interactive` | `-i` | Prompt for confirmation on uncertain files |
| `--limit N` | `-n N` | Only process the first N files |
| `--verbose` | `-v` | Show detailed output with file-by-file actions |
| `--version` | | Show version and exit |
| `--help` | | Show help message and exit |

### Subcommands

| Command | Description |
|---------|-------------|
| `tidyup status` | Show organization statistics from logs |
| `tidyup reindex` | Renumber destination folders (coming soon) |

## Usage Examples

### Preview Changes (Dry Run)

Always recommended before your first run:

```bash
tidyup ~/Downloads --dry-run
```

Output:
```
TidyUp v0.1.0
Source: /Users/you/Downloads
Destination: /Users/you/Documents/Organized
Mode: Move + Rename
DRY RUN - no files will be changed

                        Actions
┏━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━┓
┃ File          ┃ Category     ┃ Status  ┃ Destination  ┃
┡━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━┩
│ report.pdf    │ 01_Documents │ success │ report.pdf   │
│ photo.jpg     │ 02_Images    │ success │ photo.jpg    │
│ unknown.xyz   │ 99_Unsorted  │ success │ unknown.xyz  │
└───────────────┴──────────────┴─────────┴──────────────┘

Summary
  Processed: 3
  Moved:     3
  Renamed:   0
```

### Move Only (Keep Original Names)

Organize files into categories without renaming them:

```bash
tidyup ~/Downloads --move
```

### Rename Only (In Place)

Clean up ugly filenames without moving files:

```bash
tidyup ~/Downloads --rename
```

Example transformations:
- `1743151465964.pdf` → `2024-12-15_1743151465964.pdf`
- `a1b2c3d4-e5f6-7890-abcd.pdf` → `2024-12-15_a1b2c3d4-e5f6-7890-abcd.pdf`

### Skip Uncertain Files

Leave files in source if categorization confidence is below 70%:

```bash
tidyup ~/Downloads --skip
```

### Process Limited Files

Test with a small batch first:

```bash
tidyup ~/Downloads --limit 10 --dry-run
```

### Verbose Output

See detailed information about each file:

```bash
tidyup ~/Downloads --verbose
```

### Custom Destination

Organize to a specific location:

```bash
tidyup ~/Downloads /Volumes/External/Organized
```

## Folder Structure

Files are organized into numbered folders at the destination:

```
~/Documents/Organized/
├── 01_Documents/     # PDFs, DOCX, TXT, RTF, etc.
├── 02_Images/        # PNG, JPEG, GIF, HEIC, etc.
├── 03_Videos/        # MP4, MOV, AVI, MKV, etc.
├── 04_Audio/         # MP3, WAV, FLAC, M4A, etc.
├── 05_Archives/      # ZIP, RAR, 7Z, TAR, etc.
├── 06_Code/          # PY, JS, TS, HTML, CSS, etc.
├── 07_Books/         # EPUB, MOBI, AZW, etc.
├── 08_Data/          # CSV, JSON, SQL, DB, etc.
└── 99_Unsorted/      # Files that couldn't be categorized
    └── _duplicates/  # Duplicate files (same content hash)
```

### Category Detection

Files are categorized primarily by extension:

| Category | Extensions |
|----------|------------|
| Documents | pdf, doc, docx, txt, rtf, odt, xls, xlsx, ppt, pptx |
| Images | jpg, jpeg, png, gif, bmp, webp, svg, heic, heif |
| Videos | mp4, mov, avi, mkv, wmv, webm |
| Audio | mp3, wav, flac, aac, ogg, m4a |
| Archives | zip, rar, 7z, tar, gz, bz2 |
| Code | py, js, ts, java, c, cpp, go, rs, rb, html, css |
| Books | epub, mobi, azw, azw3 |
| Data | db, sqlite, sql, csv, json, yaml, yml |

## Configuration

### Directory Structure

Tidy stores its configuration and logs in `~/.tidy/`:

```
~/.tidy/
├── config.yaml      # Configuration file (optional)
└── logs/            # Operation logs
    ├── 2024-12-01_143052.json
    ├── 2024-12-02_091523.json
    └── ...
```

### Log Format

Each run creates a JSON log file with full details:

```json
{
  "timestamp": "2024-12-02T14:30:52",
  "source": "/Users/you/Downloads",
  "destination": "/Users/you/Documents/Organized",
  "options": {
    "move": false,
    "rename": false,
    "dry_run": false
  },
  "actions": [
    {
      "file": "report.pdf",
      "from": "/Users/you/Downloads/report.pdf",
      "to": "/Users/you/Documents/Organized/01_Documents/report.pdf",
      "category": "01_Documents",
      "confidence": 0.9,
      "status": "success"
    }
  ],
  "summary": {
    "processed": 10,
    "moved": 8,
    "renamed": 5,
    "unsorted": 2,
    "skipped": 0,
    "errors": 0,
    "duplicates": 1
  }
}
```

## Troubleshooting

### Common Issues

#### "Permission denied" errors

Make sure you have read access to the source and write access to the destination:

```bash
# Check permissions
ls -la ~/Downloads
ls -la ~/Documents/Organized
```

#### Files not being categorized correctly

Unknown file extensions are placed in `99_Unsorted/`. Check the file extension:

```bash
tidyup ~/Downloads --dry-run --verbose
```

#### Duplicate files

Files with identical content (same SHA-256 hash) are moved to `99_Unsorted/_duplicates/` to prevent data loss. The original in the destination is kept.

#### "No files to process"

Tidy automatically skips:
- Hidden files (starting with `.`)
- System files (`.DS_Store`, `Thumbs.db`)
- Partial downloads (`.crdownload`, `.part`, `.download`)
- Temporary files (`.tmp`, `.temp`)

### Getting Help

```bash
# Show all options
tidyup --help

# Show subcommand help
tidyup run --help
tidyup status --help
```

### Viewing Logs

Check what happened in previous runs:

```bash
# List recent logs
ls -la ~/.tidy/logs/

# View a specific log
cat ~/.tidy/logs/2024-12-02_143052.json | python -m json.tool
```

## Development

### Prerequisites

- Python 3.11+
- pip or pipx

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/tidyup.git
cd tidyup

# Install in development mode
pip install -e .

# Run tests
pytest

# Run tests with coverage
pytest --cov=tidy

# Run a specific test file
pytest tests/test_engine.py -v
```

### Project Structure

```
tidyup/
├── src/tidyup/
│   ├── __init__.py      # Package metadata
│   ├── cli.py           # Click CLI interface
│   ├── engine.py        # Core orchestration logic
│   ├── discovery.py     # File discovery and filtering
│   ├── operations.py    # Safe move/rename operations
│   ├── logger.py        # JSON logging system
│   ├── models.py        # Data models (dataclasses)
│   └── utils.py         # Utility functions
├── tests/               # Test suite (pytest)
├── docs/
│   ├── REQUIREMENTS.md  # Full specification
│   └── BACKLOG.md       # Development tasks
└── README.md            # This file
```

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test class
pytest tests/test_engine.py::TestEngineRun -v

# Run tests matching a pattern
pytest -k "dry_run" -v
```

## License

MIT

## Contributing

Contributions welcome! Please read the requirements in `docs/REQUIREMENTS.md` before submitting PRs.
