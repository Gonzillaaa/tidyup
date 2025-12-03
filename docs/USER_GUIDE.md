# TidyUp User Guide

## How It Works

TidyUp scans a source directory (like Downloads), analyzes each file, and:

1. **Categorizes** it based on type, content, and filename patterns
2. **Renames** it using extracted metadata (dates, titles, authors)
3. **Moves** it to an organized folder structure

Files are never deleted—only moved and renamed.

## CLI Reference

### Basic Usage

```bash
tidyup <source> [destination]
```

| Argument | Description |
|----------|-------------|
| `source` | Directory to organize (required) |
| `destination` | Where to move files (default: `~/Documents/Organized`) |

### Options

| Option | Short | Description |
|--------|-------|-------------|
| `--dry-run` | | Preview changes without moving/renaming files |
| `--move` | | Only categorize and move files, keep original names |
| `--rename` | | Only rename files in place, don't move them |
| `--skip` | | Skip files with uncertain categorization (confidence < 70%) |
| `--limit N` | `-n` | Only process the first N files |
| `--verbose` | `-v` | Show detailed output with file-by-file actions |
| `--interactive` | `-i` | Prompt for confirmation on uncertain files *(coming soon)* |

### Subcommands

| Command | Description |
|---------|-------------|
| `tidyup status` | Show configuration paths *(full statistics coming soon)* |
| `tidyup categories` | List all configured categories |
| `tidyup categories list` | Same as above |
| `tidyup categories add <name>` | Add a new category |
| `tidyup categories remove <name>` | Remove a category |
| `tidyup categories apply <path>` | Rename folders to match current config |
| `tidyup routing` | List all routing rules |
| `tidyup routing list` | Same as above |
| `tidyup routing set <from> <to>` | Add a routing rule (global) |
| `tidyup routing set <from> <to> -d <detector>` | Add a detector-specific routing rule |
| `tidyup routing remove <from>` | Remove a routing rule |

## Category Management

Categories determine the folder structure where files are organized. Each category gets a numbered folder (01, 02, 03...) based on its position in the config.

### Default Categories

```
01_Documents      PDFs, Word docs, spreadsheets, text files
02_Screenshots    macOS/Windows screenshots, CleanShot captures
03_Images         Photos, graphics (PNG, JPEG, GIF, HEIC)
04_Videos         MP4, MOV, AVI, MKV
05_Audio          MP3, WAV, FLAC, podcasts
06_Archives       ZIP, RAR, 7Z, TAR
07_Code           Python, JavaScript, HTML, CSS, source files
08_Books          EPUB, MOBI, PDFs with ISBN
09_Papers         arXiv papers, academic PDFs with DOI
10_Data           CSV, JSON, SQL, databases
11_Installers     DMG, PKG, EXE, MSI
99_Unsorted       Files that couldn't be categorized
```

### Viewing Categories

```bash
tidyup categories
```

Shows all categories with their folder numbers.

### Adding a Category

```bash
# Add at end of list
tidyup categories add Music

# Add at specific position (becomes 05_Music)
tidyup categories add Music --position 5
```

### Removing a Category

```bash
tidyup categories remove Music
```

### Applying Changes to Existing Folders

After adding, removing, or reordering categories, use `apply` to rename existing folders:

```bash
# Preview what would change
tidyup categories apply ~/Documents/Organized --dry-run

# Actually rename folders
tidyup categories apply ~/Documents/Organized
```

### Configuration File

Categories are stored in `~/.tidy/config.yaml`:

```yaml
categories:
  - Documents
  - Screenshots
  - Images
  - Videos
  # ... order determines folder numbers
```

## Category Routing

Routing allows you to redirect files from one category to another. This is useful when:
- You want to rename a default category (e.g., "Documents" → "Paperwork")
- You want certain file types to go to a custom category
- You want invoices to go to an "Invoices" folder instead of "Documents"

### Viewing Routing Rules

```bash
tidyup routing
```

Shows all configured routing rules.

### Setting a Global Remap

Redirect ALL files from one category to another:

```bash
# All files detected as "Documents" now go to "PDF" folder
tidyup routing set Documents PDF
```

### Setting a Detector-Specific Remap

Redirect only files from a specific detector:

```bash
# Only files detected as invoices go to "Invoices" folder
tidyup routing set Documents Invoices --detector InvoiceDetector
```

**Available detectors:**
- `ScreenshotDetector` - Screenshots
- `ArxivDetector` - arXiv papers
- `PaperDetector` - Academic PDFs with DOI
- `InvoiceDetector` - Invoices and receipts
- `InstallerDetector` - App installers
- `ArchiveBookDetector` - Books in archives
- `BookDetector` - E-books (EPUB, MOBI)
- `GenericDetector` - Fallback extension-based detection

### Removing a Routing Rule

```bash
# Remove global remap
tidyup routing remove Documents

# Remove detector-specific remap
tidyup routing remove Documents --detector InvoiceDetector
```

### Example: Custom Invoices Folder

```bash
# 1. Create the Invoices category
tidyup categories add Invoices

# 2. Route invoice detections to it
tidyup routing set Documents Invoices --detector InvoiceDetector

# 3. Now invoices go to your new Invoices folder!
tidyup ~/Downloads --dry-run
```

### Routing Configuration

Routing rules are saved in `~/.tidy/config.yaml`:

```yaml
categories:
  - Documents
  - Screenshots
  - Invoices  # Custom category

routing:
  remap:
    # Detector-specific: only invoices → Invoices
    InvoiceDetector:
      Documents: Invoices

    # Global: all "Books" → "Library" (if you had this)
    # Books: Library
```

## Rename Examples

TidyUp extracts metadata to create clean, informative filenames.

### Screenshots

Standardizes screenshot filenames from any OS:

| Before | After |
|--------|-------|
| `Screen Shot 2024-01-15 at 10.30.45 AM.png` | `Screenshot_2024-01-15_10-30-45.png` |
| `Bildschirmfoto 2024-03-20 um 14.25.30.png` | `Screenshot_2024-03-20_14-25-30.png` |
| `CleanShot 2024-02-10 at 09.15.22.png` | `Screenshot_2024-02-10_09-15-22.png` |

### PDFs with Metadata

Extracts title from PDF metadata or first heading:

| Before | After |
|--------|-------|
| `document_v2_final.pdf` (title: "Annual Report") | `2024-01-15_Annual_Report.pdf` |
| `1743151465964.pdf` (extracted heading) | `2024-01-15_Introduction_to_Python.pdf` |

### Books (EPUB/PDF)

Uses embedded metadata: title, author, publication year:

| Before | After |
|--------|-------|
| `book.epub` (Dune Messiah by Frank Herbert) | `1969_Dune_Messiah_Frank_Herbert.epub` |
| `978-0-13-235088-4.pdf` (Clean Code by Robert Martin) | `2008_Clean_Code_Robert_Martin.pdf` |

### Invoices

Extracts vendor name from invoice content:

| Before | After |
|--------|-------|
| `Invoice-2024-001.pdf` (from Acme Corp) | `2024-01-15_Invoice_Acme_Corporation.pdf` |
| `receipt_xyz123.pdf` (from @techstartup.io) | `2024-01-10_Invoice_techstartup.pdf` |

### Images with EXIF

Uses photo date from camera metadata:

| Before | After |
|--------|-------|
| `IMG_1234.jpg` (shot 2023-06-15) | `2023-06-15_IMG_1234.jpg` |
| `holiday photo.heic` (EXIF: 2024-07-20) | `2024-07-20_holiday_photo.heic` |

### Academic Papers (arXiv)

Preserves arXiv ID with date prefix:

| Before | After |
|--------|-------|
| `2401.05712v2.pdf` | `2024-01-15_2401.05712v2.pdf` |
| `arXiv_1905.13325.pdf` | `2024-01-20_1905.13325.pdf` |

## Troubleshooting

### "Permission denied" errors

Ensure you have read access to source and write access to destination:

```bash
ls -la ~/Downloads
ls -la ~/Documents/Organized
```

### Files going to Unsorted

Files land in `99_Unsorted/` when:
- Unknown file extension
- Content doesn't match any detector
- Categorization confidence is low

Use `--verbose` to see why:

```bash
tidyup ~/Downloads --dry-run --verbose
```

### Duplicate files

Files with identical content (same SHA-256 hash) are moved to `99_Unsorted/_duplicates/` to prevent data loss. The original in the destination is kept.

### "No files to process"

TidyUp automatically skips:
- Hidden files (starting with `.`)
- System files (`.DS_Store`, `Thumbs.db`)
- Partial downloads (`.crdownload`, `.part`)
- Temporary files (`.tmp`, `.temp`)

### Viewing operation logs

Each run creates a JSON log in `~/.tidy/logs/`:

```bash
ls ~/.tidy/logs/
cat ~/.tidy/logs/2024-12-02_143052.json | python -m json.tool
```
