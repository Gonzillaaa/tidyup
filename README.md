# TidyUp

**Stop drowning in Downloads chaos.** TidyUp automatically organizes your files into a clean folder structure—categorizing by type, extracting metadata, and renaming with useful dates and titles.

## What It Does

```
~/Downloads/                          ~/Documents/Organized/
├── IMG_4521.jpg                      ├── 01_Documents/
├── Screen Shot 2024-01-15...png  →   │   └── 2024-01-10_Annual_Report.pdf
├── 2401.05712v2.pdf                  ├── 02_Screenshots/
├── invoice_xyz123.pdf                │   └── Screenshot_2024-01-15_10-30-45.png
└── document_v2_final.pdf             ├── 03_Images/
                                      │   └── 2024-01-12_IMG_4521.jpg
                                      └── 09_Papers/
                                          └── 2024-01-15_2401.05712v2.pdf
```

- **Smart categorization**: 11 categories including Screenshots, Books, Papers, Invoices
- **Metadata extraction**: Renames using PDF titles, EXIF dates, arXiv IDs, vendor names
- **Safe by design**: Never deletes files, only moves and renames
- **Dry run mode**: Preview everything before committing

## Installation

```bash
# Using pipx (recommended - installs globally in isolation)
pipx install -e /path/to/tidyup

# Or using pip
pip install -e /path/to/tidyup
```

## Quick Start

```bash
# Preview what would happen
tidyup ~/Downloads --dry-run

# Actually organize files
tidyup ~/Downloads

# Just rename files in place (no moving)
tidyup ~/Downloads --rename
```

## Example Renames

| Before | After |
|--------|-------|
| `Screen Shot 2024-01-15 at 10.30.45 AM.png` | `Screenshot_2024-01-15_10-30-45.png` |
| `document_v2_final.pdf` (title: "Annual Report") | `2024-01-15_Annual_Report.pdf` |
| `book.epub` (Dune Messiah by Frank Herbert) | `1969_Dune_Messiah_Frank_Herbert.epub` |
| `invoice_xyz.pdf` (from Acme Corp) | `2024-01-15_Invoice_Acme_Corporation.pdf` |
| `2401.05712v2.pdf` | `2024-01-20_2401.05712v2.pdf` |

## Documentation

- **[User Guide](docs/USER_GUIDE.md)** — Full CLI reference, category management, troubleshooting
- **[Development Guide](docs/DEVELOPMENT.md)** — Setup, testing, adding detectors/renamers

## License

MIT
