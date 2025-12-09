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
| `tidyup categories add <name>` | Add a new category (with suggestions) |
| `tidyup categories add <name> --parent <cat>` | Add as subcategory |
| `tidyup categories add <name> --keywords "kw1,kw2"` | Add with keyword rules |
| `tidyup categories add <name> --patterns "pat1,pat2"` | Add with pattern rules |
| `tidyup categories add <name> --no-suggestions` | Add without auto-suggestions |
| `tidyup categories remove <name>` | Remove a category |
| `tidyup categories apply <path>` | Rename folders to match current config |
| `tidyup routing` | List all routing rules |
| `tidyup routing list` | Same as above |
| `tidyup routing set <from> <to>` | Add a routing rule (global) |
| `tidyup routing set <from> <to> -d <detector>` | Add a detector-specific routing rule |
| `tidyup routing remove <from>` | Remove a routing rule |

## Quick Start: Customizing Your Organization

TidyUp works great out of the box, but you can customize it to match your workflow. Here's a quick overview of your options:

| I want to... | Use | Example |
|--------------|-----|---------|
| Put all invoices in their own folder | **Routing** | `tidyup routing set Documents Invoices -d InvoiceDetector` |
| Separate tech books from fiction | **Rules** | `tidyup categories add Technical --parent Books --keywords "code,programming"` |
| Create a new category quickly | **Suggestions** | `tidyup categories add "Work Projects"` (auto-suggests keywords) |
| Rename "Documents" to "Paperwork" | **Routing** | `tidyup routing set Documents Paperwork` |

**Typical workflow:**

```bash
# 1. Create your custom category
tidyup categories add Invoices

# 2. Tell TidyUp which files should go there
tidyup routing set Documents Invoices --detector InvoiceDetector

# 3. Test it
tidyup ~/Downloads --dry-run

# 4. Run it for real
tidyup ~/Downloads
```

See the sections below for detailed examples of each feature.

---

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

### Smart Suggestions

When you add a category, TidyUp analyzes the name and automatically suggests:
- **Parent category**: Which existing category this should be a subcategory of
- **Keywords**: Words to match files against

This saves you from manually figuring out which keywords to use.

**Example:**

```bash
$ tidyup categories add "Technical Books"

Suggestions based on category name:
  Parent: Books
  Keywords: api, chapter, code, developer, edition, framework, isbn, programming

Accept these suggestions? [Y/n]
```

- Press **Enter** to accept (recommended)
- Type **n** to add without any rules
- Or use `--keywords` to provide your own instead

### How Suggestions Work

TidyUp has a built-in dictionary of ~100 patterns. When your category name contains a known pattern, it suggests relevant keywords:

| Your category name contains... | Suggested keywords |
|-------------------------------|-------------------|
| "tech", "programming", "code" | programming, software, developer, api, framework |
| "invoice", "receipt", "bill" | invoice, receipt, payment, amount, total |
| "fiction", "novel" | novel, story, fantasy, romance, mystery |
| "work", "project", "client" | project, meeting, client, report, presentation |
| "research", "paper", "academic" | paper, research, study, journal, thesis |
| "photo", "image" | photo, image, picture, camera, shot |

TidyUp also infers parent categories:

| Your category name contains... | Suggested parent |
|-------------------------------|-----------------|
| "fiction", "novel", "textbook" | Books |
| "invoice", "receipt", "contract" | Documents |
| "photo", "picture", "graphic" | Images |
| "research", "thesis", "paper" | Papers |

### When to Use Suggestions

**Good for:**
- Common category types (invoices, tech books, work projects)
- Quick setup without thinking about keywords
- Getting a reasonable starting point to customize later

**Skip suggestions when:**
- You have very specific keyword requirements
- The category name doesn't match common patterns
- You want complete control over matching

### Skipping or Customizing Suggestions

```bash
# Skip suggestions entirely
tidyup categories add "My Category" --no-suggestions

# Provide your own keywords instead
tidyup categories add "My Category" --keywords "custom,keywords,here"

# Override parent suggestion
tidyup categories add "My Category" --parent Documents --keywords "my,keywords"
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

Routing redirects files from one category to another **after** TidyUp detects what type of file it is. Think of it as: "When TidyUp says this file is X, actually put it in Y."

### Why Use Routing?

**Problem**: TidyUp's detectors output hardcoded category names. The `InvoiceDetector` always outputs "Documents", the `BookDetector` always outputs "Books", etc.

**Solution**: Routing lets you intercept these outputs and redirect them wherever you want.

### Common Use Cases

| Scenario | Before Routing | After Routing |
|----------|---------------|---------------|
| Separate invoices from other PDFs | All invoices → `01_Documents` | Invoices → `12_Invoices` |
| Rename a category | "Documents" folder | "Paperwork" folder |
| Consolidate categories | Books + Papers separate | Both → "Reading" folder |

### How It Works

```
File: invoice_acme.pdf
        ↓
┌─────────────────────────────────┐
│ 1. InvoiceDetector analyzes it  │
│    → "This is an invoice"       │
│    → Returns: category=Documents│
└─────────────────────────────────┘
        ↓
┌─────────────────────────────────┐
│ 2. Routing layer checks config  │
│    → "InvoiceDetector:Documents │
│        should go to Invoices"   │
│    → Changes to: Invoices       │
└─────────────────────────────────┘
        ↓
    File goes to: 12_Invoices/
```

### Setting Up Routing

**Step 1: View current rules**

```bash
tidyup routing
```

**Step 2: Add a routing rule**

```bash
# Global: redirect ALL "Documents" to "Paperwork"
tidyup routing set Documents Paperwork

# Detector-specific: only invoices go to "Invoices"
tidyup routing set Documents Invoices --detector InvoiceDetector
```

**Step 3: Test it**

```bash
tidyup ~/Downloads --dry-run --verbose
```

### Real-World Examples

#### Example 1: Invoices to Their Own Folder

```bash
# Create the target category
tidyup categories add Invoices

# Route only invoice detections (not all documents)
tidyup routing set Documents Invoices --detector InvoiceDetector

# Result:
# - invoice_amazon.pdf     → 12_Invoices/  (detected as invoice)
# - quarterly_report.pdf   → 01_Documents/ (regular document)
```

#### Example 2: Rename "Documents" to "Paperwork"

```bash
# Create the new category name
tidyup categories add Paperwork --position 1

# Redirect everything
tidyup routing set Documents Paperwork

# Remove the old category (optional)
tidyup categories remove Documents
```

#### Example 3: All Academic Content Together

```bash
# Create a unified category
tidyup categories add Reading

# Route both books and papers there
tidyup routing set Books Reading
tidyup routing set Papers Reading
```

### Available Detectors

When using `--detector`, these are the detector names:

| Detector | Detects | Default Output |
|----------|---------|----------------|
| `ScreenshotDetector` | macOS/Windows screenshots | Screenshots |
| `ArxivDetector` | arXiv papers (2401.12345.pdf) | Papers |
| `PaperDetector` | PDFs with DOI | Papers |
| `InvoiceDetector` | Invoices and receipts | Documents |
| `InstallerDetector` | DMG, PKG, EXE, MSI | Installers |
| `ArchiveBookDetector` | EPUB/MOBI in ZIP files | Books |
| `BookDetector` | EPUB, MOBI, PDFs with ISBN | Books |
| `GenericDetector` | Extension-based fallback | (varies) |

### Removing Routing Rules

```bash
# Remove a global remap
tidyup routing remove Documents

# Remove a detector-specific remap
tidyup routing remove Documents --detector InvoiceDetector
```

### Configuration File

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

    # Global: all "Books" → "Library"
    Books: Library
```

## Category Rules (Subcategorization)

Rules let you split a category into subcategories based on file content. Unlike Routing (which redirects detector output), Rules analyze the **file itself** to decide which subcategory it belongs to.

### When to Use Rules vs Routing

| Feature | Rules | Routing |
|---------|-------|---------|
| **Purpose** | Split categories (Books → Technical/Fiction) | Redirect categories (Documents → Invoices) |
| **Based on** | File content, filename patterns | Detector output |
| **Use case** | "I want programming books separate from novels" | "I want invoices in their own folder" |

### How Rules Work

```
File: Clean_Code_Robert_Martin.epub
        ↓
┌─────────────────────────────────────────────┐
│ 1. BookDetector identifies it as a book     │
│    → Returns: category=Books                │
└─────────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────────┐
│ 2. Rules engine checks subcategories        │
│    → "Technical" has parent=Books           │
│    → Keywords: programming, software, code  │
│    → File contains "code"? YES              │
│    → Match! Use "Technical" instead         │
└─────────────────────────────────────────────┘
        ↓
    File goes to: 09_Technical/
```

### Rule Types

Rules can match files using:

| Type | Matches | Example |
|------|---------|---------|
| **Keywords** | Words in filename or content | `--keywords "invoice,receipt,payment"` |
| **Patterns** | Glob patterns on filename | `--patterns "acme_*,*_report_*"` |
| **Extensions** | File extensions (no dot) | `--extensions "py,js,ts"` |

### Creating Categories with Rules

**Basic subcategory:**
```bash
tidyup categories add "Technical" --parent Books --keywords "programming,software,code"
```

**Pattern-based category:**
```bash
tidyup categories add "Acme Projects" --patterns "acme_*,*_acme_*"
```

**Combined rules:**
```bash
tidyup categories add "Invoices" --parent Documents --keywords "invoice,receipt" --patterns "*_invoice_*"
```

### Real-World Examples

#### Example 1: Organize Books by Genre

**Goal**: Separate programming books from fiction

```bash
# Step 1: Create subcategories under Books
tidyup categories add "Technical" --parent Books \
    --keywords "programming,software,code,algorithm,database,api"

tidyup categories add "Fiction" --parent Books \
    --keywords "novel,fiction,fantasy,romance,mystery,thriller"

# Step 2: Test with a dry run
tidyup ~/Downloads --dry-run --verbose
```

**Result:**
| File | Category | Why |
|------|----------|-----|
| `Clean_Code.epub` | Technical | Contains "code" |
| `The_Great_Gatsby.epub` | Fiction | Contains "novel" in metadata |
| `random_book.epub` | Books | No rules matched, stays in parent |

#### Example 2: Client Project Folders

**Goal**: Automatically sort files by client

```bash
# Create client-specific categories using filename patterns
tidyup categories add "Acme Corp" --patterns "acme_*,*_acme_*,acme-*"
tidyup categories add "TechCorp" --patterns "techcorp_*,tc_*,*_techcorp_*"
tidyup categories add "Startup Inc" --patterns "startup_*,si_*"
```

**Result:**
| File | Category | Why |
|------|----------|-----|
| `acme_q4_report.pdf` | Acme Corp | Matches `acme_*` pattern |
| `tc_invoice_2024.pdf` | TechCorp | Matches `tc_*` pattern |
| `random_report.pdf` | Documents | No pattern matched |

#### Example 3: Work vs Personal Documents

**Goal**: Split documents by context

```bash
# Work documents
tidyup categories add "Work" --parent Documents \
    --keywords "meeting,project,client,deadline,quarterly" \
    --patterns "*_work_*,work_*"

# Personal documents
tidyup categories add "Personal" --parent Documents \
    --keywords "family,vacation,medical,insurance,tax" \
    --patterns "*_personal_*"
```

### Viewing Categories with Rules

```bash
tidyup categories
```

Output shows parent relationships and rule counts:

```
┏━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━┓
┃ # ┃ Name           ┃ Folder            ┃ Parent ┃ Rules    ┃
┡━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━┩
│ 1 │ Documents      │ 01_Documents      │        │          │
│ 2 │ Work           │ 02_Work           │ Docs   │ kw:5 pt:2│
│ 3 │ Personal       │ 03_Personal       │ Docs   │ kw:5 pt:1│
│ 8 │ Books          │ 08_Books          │        │          │
│ 9 │ Technical      │ 09_Technical      │ Books  │ kw: 6    │
│10 │ Fiction        │ 10_Fiction        │ Books  │ kw: 6    │
└───┴────────────────┴───────────────────┴────────┴──────────┘
```

### Configuration File

Rules are saved in `~/.tidy/config.yaml`:

```yaml
categories:
  - Documents
  - Books

  # Subcategory with keywords
  - name: Technical
    parent: Books
    rules:
      keywords:
        - programming
        - software
        - code

  # Subcategory with patterns
  - name: Acme Corp
    rules:
      patterns:
        - acme_*
        - "*_acme_*"

  # Combined rules
  - name: Work
    parent: Documents
    rules:
      keywords:
        - meeting
        - project
      patterns:
        - "*_work_*"
```

### Rule Matching Details

- **Keywords**: Case-insensitive, searches filename and file content
- **Patterns**: Glob patterns (e.g., `acme_*`, `*_report_*`), case-insensitive
- **Extensions**: Match without the dot (e.g., `py` not `.py`)
- **Multiple rules on same file**: First matching subcategory wins
- **No match**: File stays in parent category (or base detection)

## When to Use What: Routing vs Rules vs Suggestions

### Decision Flowchart

```
Do you want to create a new category?
├── YES → Use "tidyup categories add <name>"
│         │
│         └── Does TidyUp suggest good keywords?
│             ├── YES → Accept suggestions (Smart Suggestions)
│             └── NO  → Add your own with --keywords/--patterns (Rules)
│
└── NO, I want to redirect existing detections
    │
    └── Use "tidyup routing set" (Routing)
```

### Feature Comparison

| Feature | Routing | Rules | Suggestions |
|---------|---------|-------|-------------|
| **What it does** | Redirects detector output | Matches file content | Auto-generates keywords |
| **When it runs** | After detection | After detection + routing | When you add a category |
| **Configuration** | `tidyup routing set` | `--keywords`, `--patterns` | Automatic or `--no-suggestions` |

### Common Scenarios

| I want to... | Solution |
|--------------|----------|
| Put invoices in their own folder | Routing: `tidyup routing set Documents Invoices -d InvoiceDetector` |
| Rename "Documents" to "Paperwork" | Routing: `tidyup routing set Documents Paperwork` |
| Separate tech books from fiction | Rules: `tidyup categories add Technical --parent Books --keywords "code"` |
| Organize files by client name | Rules: `tidyup categories add "Acme" --patterns "acme_*"` |
| Quickly add a common category | Suggestions: `tidyup categories add "Work Projects"` (auto-suggests) |

### How They Work Together

TidyUp processes files in this order:

```
File: acme_invoice_2024.pdf
        ↓
┌──────────────────────────────────────┐
│ 1. DETECTION                         │
│    InvoiceDetector → "Documents"     │
└──────────────────────────────────────┘
        ↓
┌──────────────────────────────────────┐
│ 2. RULES (subcategorization)         │
│    Check if "Work" subcategory       │
│    matches (has parent=Documents     │
│    and keywords match)               │
│    → No match, stays "Documents"     │
└──────────────────────────────────────┘
        ↓
┌──────────────────────────────────────┐
│ 3. ROUTING (redirection)             │
│    Check routing config              │
│    → InvoiceDetector:Documents       │
│      maps to "Invoices"              │
│    → Final: "Invoices"               │
└──────────────────────────────────────┘
        ↓
    File goes to: 12_Invoices/
```

### Examples: Combining Features

**Example 1: Client invoices in separate folders**

```bash
# Create client-specific invoice categories
tidyup categories add "Acme Invoices" --patterns "acme_*invoice*,*acme*invoice*"
tidyup categories add "TechCorp Invoices" --patterns "techcorp_*invoice*,tc_*invoice*"
tidyup categories add "Other Invoices"

# Route all uncategorized invoices to "Other Invoices"
tidyup routing set Documents "Other Invoices" --detector InvoiceDetector
```

**Example 2: Organized book library**

```bash
# Use smart suggestions for common book types
tidyup categories add "Technical Books"     # Suggests: programming, software, code
tidyup categories add "Fiction"             # Suggests: novel, fantasy, romance
tidyup categories add "Self Help"           # Suggests: motivation, habit, productivity

# All suggestions create subcategories under Books
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
