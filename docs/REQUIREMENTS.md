# TidyUp - Downloads Organizer

## Overview

A global CLI tool written in Python that organizes, renames, and categorizes files from any directory into a structured destination.

**Core Principle:** TidyUp never deletes files. It only moves and renames.

---

## CLI Interface

```bash
tidyup <source> [destination]       # Move + rename (default behavior)
tidyup ~/Downloads                  # Uses default destination from config
tidyup ~/Downloads ~/Organized      # Explicit destination
tidyup . --dry-run                  # Preview changes
tidyup ~/Downloads --move           # Only categorize and move, keep original names
tidyup ~/Downloads --rename         # Only rename in place (no destination needed)
tidyup ~/Downloads --skip           # Skip uncertain files entirely
tidyup ~/Downloads --interactive    # Prompt for uncertain files
tidyup ~/Downloads --limit 20       # Process only 20 files

# Utility commands
tidyup reindex                      # Renumber destination folders
tidyup status                       # Show statistics from logs
```

### Arguments

- `source` (required): Directory to organize
- `destination` (optional): Where to move files. Defaults to `~/Documents/Organized/`
  - Ignored when using `--rename` (operates in place)

### Flags

| Flag | Description |
|------|-------------|
| `--move` | Only categorize and move files. Keep original filenames. |
| `--rename` | Only rename files in place. Don't move to destination. |
| `--skip` | Skip uncertain files entirely (don't move to Unsorted). |
| `--dry-run` | Preview what would happen without making changes (paginated). |
| `--interactive` | Prompt for confirmation on uncertain categorizations. |
| `--limit N` | Only process N files. |
| `--verbose` | Show detailed output. |

**Default behavior (no flags):** Both move AND rename.

### Flag Combinations

```bash
tidyup ~/Downloads                       # Move + rename (default)
tidyup ~/Downloads --move                # Move only, keep names
tidyup ~/Downloads --rename              # Rename only, stay in place
tidyup ~/Downloads --move --dry-run      # Preview moves
tidyup ~/Downloads --rename --dry-run    # Preview renames
tidyup ~/Downloads --skip                # Move + rename, skip uncertain
tidyup ~/Downloads --skip --move         # Move only, skip uncertain
```

---

## Operations: Move vs Rename

TidyUp has two core operations that can be used independently or together:

### Move (Categorization)

Determines WHERE a file should go based on its type.

- Analyzes file to determine category (Document, Image, Book, etc.)
- Moves file to the appropriate numbered folder
- Keeps original filename if `--move` flag is used alone

### Rename (Metadata Extraction)

Determines WHAT to call a file based on its content.

- Reads file metadata (PDF title, EXIF date, etc.)
- Generates a clean, informative filename
- Operates in place if `--rename` flag is used alone (no destination)

### Combined (Default)

Both operations together: categorize AND rename.

---

## Content Inspection

TidyUp reads inside files to make smart decisions. This is the core intelligence.

### For Categorization (Move)

| File Type | What We Inspect | Looking For |
|-----------|-----------------|-------------|
| **PDF** | First 1-2 pages of text | "invoice", "receipt", "factura", "rechnung", arXiv patterns |
| **RAR/ZIP** | File listing (no extraction) | .epub, .pdf, .mobi files inside → likely a book |
| **Images** | Filename only | Screenshot patterns |
| **Other** | Extension | Direct mapping to category |

### For Naming (Rename)

| File Type | What We Extract | Fallback |
|-----------|-----------------|----------|
| **PDF** | Metadata: `/Title`, `/Author`, `/CreationDate` | First heading from text, then file modified date |
| **Images** | EXIF: `DateTimeOriginal`, `CreateDate` | File modified date |
| **RAR/ZIP (books)** | List contents, inspect inner PDF/EPUB metadata | Archive filename |
| **Invoices** | Scan first page for vendor name, date, amount | "Invoice" + file date |
| **Other** | N/A | File modified date + sanitized original name |

### Confidence Scoring

Each detection returns a confidence score (0.0 - 1.0):

- **≥ 0.7**: High confidence → proceed automatically
- **< 0.7**: Uncertain → behavior depends on flags:
  - Default: Move to `99_Unsorted/`, log the reason
  - `--interactive`: Prompt user for decision
  - `--skip`: Skip file entirely, leave in source

---

## Folder Structure

Files are organized into numbered folders for predictable ordering:

```
00_Inbox/          # Optional staging area for recent files
01_Documents/      # PDFs, DOCX, general documents
02_Images/         # PNG, JPEG, JPG, HEIC, WEBP
03_Books/          # Detected books (RAR/ZIP with ebooks, ISBN patterns)
04_Archives/       # ZIP, RAR, TGZ (non-book archives)
05_Installers/     # DMG, PKG, APP
06_Media/          # MP3, MP4, MOV, WAV
07_Data/           # CSV, JSON, XLSX
08_Papers/         # arXiv papers, research documents
09_Invoices/       # Detected invoices/receipts
99_Unsorted/       # Files that couldn't be categorized + _duplicates/
```

---

## Naming Conventions

**Date Format:** ISO 8601 (`YYYY-MM-DD`) for sortability

| File Type | Pattern | Example |
|-----------|---------|---------|
| **PDFs** | `{date}_{extracted_title}.pdf` | `2024-09-30_Annual_Report.pdf` |
| **Invoices** | `{date}_Invoice_{vendor}.pdf` | `2024-09-30_Invoice_Amazon.pdf` |
| **Books** | `{pub_date}_{title}_{author}.ext` | `2023_Clean_Code_Robert_Martin.pdf` |
| **Screenshots** | `Screenshot_{date}_{time}.png` | `Screenshot_2024-09-30_14-30-25.png` |
| **Images** | `{exif_date}_{original_name}.ext` | `2024-09-30_IMG_1234.jpg` |
| **arXiv Papers** | `{date}_{arxiv_id}.pdf` | `2025-01-15_2501.12948v1.pdf` |
| **Ugly names** | `{download_date}_{best_effort_name}.ext` | Falls back to file modified date |

---

## Logging

Every operation is logged for auditability and undo potential.

### Log Location

```
~/.tidy/logs/
├── 2024-12-02_143052.json
├── 2024-12-01_091523.json
└── ...
```

### Log Format

```json
{
  "timestamp": "2024-12-02T14:30:52",
  "source": "/Users/gonzalo/Downloads",
  "destination": "/Users/gonzalo/Documents/Organized",
  "options": {
    "move": true,
    "rename": true,
    "skip": false,
    "dry_run": false
  },
  "actions": [
    {
      "file": "report.pdf",
      "from": "/Users/gonzalo/Downloads/report.pdf",
      "to": "/Users/gonzalo/Documents/Organized/01_Documents/2024-12-02_Annual_Report.pdf",
      "category": "Documents",
      "confidence": 0.95,
      "renamed_from": "report.pdf",
      "renamed_to": "2024-12-02_Annual_Report.pdf"
    },
    {
      "file": "mystery.zip",
      "from": "/Users/gonzalo/Downloads/mystery.zip",
      "to": "/Users/gonzalo/Documents/Organized/99_Unsorted/mystery.zip",
      "category": "Unsorted",
      "confidence": 0.45,
      "reason": "Could not determine: Archive or Book?"
    }
  ],
  "summary": {
    "processed": 50,
    "moved": 47,
    "renamed": 45,
    "unsorted": 3,
    "skipped": 2,
    "errors": 0
  }
}
```

---

## Status Command

`tidyup status` reads from logs and shows aggregate statistics.

```
$ tidyup status

TidyUp Status
═══════════════════════════════════════════════════

Destination: ~/Documents/Organized
Config:      ~/.tidy/config.yaml
Logs:        ~/.tidy/logs/ (23 files)

Folder              Files      Size
────────────────────────────────────────────────────
01_Documents/         234     1.2 GB
02_Images/            891     4.5 GB
03_Books/              47     2.1 GB
04_Archives/           12     340 MB
05_Installers/          8     2.8 GB
06_Media/              34     8.2 GB
07_Data/               56     120 MB
08_Papers/             19     450 MB
09_Invoices/           67      85 MB
99_Unsorted/           23     156 MB
────────────────────────────────────────────────────
Total               1,391    19.9 GB

Last Run: 2024-12-02 14:30
  → Moved 47 files, renamed 45, skipped 2

Recent Activity (last 7 days):
  → 156 files processed
  → 12 moved to Unsorted
```

---

## Reindex Command

`tidy reindex` renumbers destination folders to allow inserting new categories.

### Usage

```bash
$ tidy reindex

Current structure:
  01_Documents/
  02_Images/
  03_Books/
  04_Archives/

Options:
  1. Insert new folder (specify position)
  2. Remove empty folder
  3. Renumber all (close gaps)
  4. Cancel

Choice: 1
New folder name: Courses
Position (01-99): 04

Result:
  01_Documents/
  02_Images/
  03_Books/
  04_Courses/     ← NEW
  05_Archives/    ← was 04

Apply changes? [y/N]
```

---

## File Type Detection (Plugin Architecture)

Each detector is a modular Python class. New detectors can be added without modifying core code.

### Core Detectors

| Detector | Logic |
|----------|-------|
| `InvoiceDetector` | Filename or PDF text contains "invoice", "factura", "receipt", "rechnung" |
| `BookDetector` | RAR/ZIP with epub/pdf inside, ISBN patterns, "Edition" in name |
| `ArxivDetector` | Filename matches `YYMM.NNNNN` pattern |
| `ScreenshotDetector` | "Screenshot", "Screen Shot", "Captura", macOS patterns |
| `InstallerDetector` | DMG, PKG extensions |
| `MediaDetector` | Audio/video extensions |
| `DataDetector` | CSV, JSON, XLSX extensions |
| `GenericDetector` | Fallback: categorize by extension only |

### Detection Pipeline

1. Run all detectors on each file
2. Each returns `(matches: bool, confidence: float, category: str)`
3. Highest confidence wins
4. Handle based on confidence and flags (see Confidence Scoring above)

---

## Renaming Engine (Plugin Architecture)

| Renamer | Behavior |
|---------|----------|
| `PDFRenamer` | Extract title from PDF metadata, fall back to first-page text |
| `ImageRenamer` | Extract date from EXIF data |
| `ArchiveRenamer` | Inspect contents, extract inner file metadata if book |
| `GenericRenamer` | Use file modified date + sanitized original filename |

---

## Safety Features

### No Deletion Policy

TidyUp **never deletes files**. It only:
- Moves files to the destination
- Renames files according to patterns

### Conflict Handling

When destination filename exists:
- Add incremental suffix: `file (1).pdf`, `file (2).pdf`, etc.

### Duplicate Detection

Files with identical content (by hash):
- Move to `99_Unsorted/_duplicates/` for manual review
- Keep the version with better filename in the proper category

### Skip Rules

- Hidden files (starting with `.`)
- Files modified within last N hours (configurable, default: 1)
- Files matching ignore patterns in config

### Dry Run Mode

- `--dry-run` shows exactly what would happen
- Paginated output (10 files per page)
- Summary statistics

### Interactive Mode

- `--interactive` prompts for uncertain categorizations
- Shows: `Move "filename.pdf" to 01_Documents? [Y/n/skip/custom]`

---

## Configuration

**Location:** `~/.tidy/config.yaml`

```yaml
# Default destination when not specified on command line
destination: ~/Documents/Organized

# Folder definitions
folders:
  - prefix: "01"
    name: Documents
    extensions: [pdf, docx, doc, txt, rtf, md]
  - prefix: "02"
    name: Images
    extensions: [png, jpg, jpeg, heic, webp, gif, bmp, tiff]
  - prefix: "03"
    name: Books
    # Uses BookDetector, not just extensions
  - prefix: "04"
    name: Archives
    extensions: [zip, rar, tgz, tar, gz, 7z]
  - prefix: "05"
    name: Installers
    extensions: [dmg, pkg, app]
  - prefix: "06"
    name: Media
    extensions: [mp3, mp4, mov, wav, avi, mkv, m4a]
  - prefix: "07"
    name: Data
    extensions: [csv, json, xlsx, xls]
  - prefix: "08"
    name: Papers
    # Uses ArxivDetector
  - prefix: "09"
    name: Invoices
    # Uses InvoiceDetector

# Files to skip
skip:
  modified_within_hours: 1
  patterns:
    - ".DS_Store"
    - "*.tmp"
    - "*.crdownload"
    - "*.part"

# Detection settings
detection:
  confidence_threshold: 0.7
```

---

## Configurable Routing (Planned - Phase 7)

Allow users to customize how files are routed to categories beyond the built-in detectors.

### Problem

When users create custom categories (e.g., `tidyup categories add PDF`), no files route there because:
- Detectors return hardcoded category names
- There's no bridge between user-defined categories and detection logic

### Solution: Three-Level Approach

#### Level 1: Category Remapping

Redirect detector outputs to different categories:

```yaml
routing:
  remap:
    # Global remap: all Documents → PDF
    Documents: PDF

    # Detector-specific remap: only invoices → Receipts
    InvoiceDetector:
      Documents: Receipts
```

**Use cases:**
- Rename default categories (Documents → Paperwork)
- Redirect specific detections (invoices → Receipts folder)

#### Level 2: Config-Based Rules

Categories can define matching rules for subcategorization:

```yaml
categories:
  - name: Technical Books
    parent: Books
    rules:
      keywords: [programming, software, algorithm, code]
      patterns: ["*_programming_*"]

  - name: Fiction
    parent: Books
    rules:
      keywords: [novel, fiction, fantasy, romance]

  - name: Client Work
    rules:
      patterns: ["acme_*", "techcorp_*"]
      keywords: [client, proposal, project]
```

**How it works:**
1. Detector chain runs, returns category (e.g., "Books")
2. Rules engine checks for subcategories with matching rules
3. If rules match, route to subcategory instead

**Use cases:**
- Split books into Technical vs Fiction
- Create client-specific folders
- Organize invoices by vendor

#### Level 3: Smart Defaults

When adding a category, suggest keywords based on name:

```bash
$ tidyup categories add "Technical Books"

Detected: Subcategory of "Books"
Suggested keywords: programming, software, code, developer, technical

Accept these suggestions? [Y/n/edit]
```

### CLI Commands (Planned)

```bash
# Routing management
tidyup routing list                              # Show current routing config
tidyup routing set <detector> <from> <to>        # Add detector-specific remap
tidyup routing remove <detector> <from>          # Remove remap

# Enhanced category creation
tidyup categories add "Technical Books"          # Interactive with suggestions
tidyup categories add "Tech" --keywords "python,java" --parent Books  # Explicit
tidyup categories add "PDF" --no-suggestions     # Skip suggestions
```

### Future: LLM-Powered Detection

See [FUTURE_DIRECTIONS.md](FUTURE_DIRECTIONS.md) for planned AI/LLM integration that enables:
- Semantic classification for novel categories
- Natural language category descriptions
- Handling ambiguous files intelligently

---

## Unsorted Handling

Files that can't be categorized go to `99_Unsorted/`.

After each run, tidy prints suggestions:
```
=== Moved to Unsorted (3 files) ===
- mystery_file.xyz → Unknown extension. Consider adding to config.
- 1234567890.pdf   → No metadata found. Possibly a scan?
- random.zip       → Low confidence (0.45): Archive or Book?
```

---

## Project Structure

```
~/Code/tidy/
├── docs/
│   └── REQUIREMENTS.md
├── src/
│   └── tidy/
│       ├── __init__.py
│       ├── cli.py              # Click-based CLI
│       ├── config.py           # Config loading & defaults
│       ├── engine.py           # Main orchestration
│       ├── models.py           # FileInfo, Action, Result dataclasses
│       ├── utils.py            # File ops, hashing, sanitization
│       ├── logger.py           # Action logging
│       ├── detectors/
│       │   ├── __init__.py
│       │   ├── base.py
│       │   ├── invoice.py
│       │   ├── book.py
│       │   ├── arxiv.py
│       │   ├── screenshot.py
│       │   └── generic.py
│       └── renamers/
│           ├── __init__.py
│           ├── base.py
│           ├── pdf.py
│           ├── image.py
│           └── generic.py
├── tests/
├── pyproject.toml
├── README.md
└── .gitignore
```

---

## Dependencies

```
click>=8.0        # CLI framework
pyyaml>=6.0       # Config parsing
pypdf>=3.0        # PDF metadata + text extraction
pillow>=10.0      # Image EXIF extraction
rich>=13.0        # Pretty CLI output
```

---

## Implementation

See [BACKLOG.md](BACKLOG.md) for detailed implementation tasks, story points, and progress tracking.
