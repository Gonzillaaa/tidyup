# TidyUp - Product Backlog

This document tracks all implementation tasks with story points, dependencies, and acceptance criteria.

**Story Point Scale:**
- 1 = Trivial (< 30 min)
- 2 = Small (30 min - 2 hours)
- 3 = Medium (2-4 hours)
- 5 = Large (4-8 hours)
- 8 = Very Large (1-2 days)
- 13 = Epic (needs breakdown)

---

## Phase 1: Scaffolding ✅ Complete

### 1.1 Project Setup ✅

| ID | Task | Points | Status |
|----|------|--------|--------|
| 1.1.1 | Create directory structure: `src/tidyup/`, `src/tidyup/detectors/`, `src/tidyup/renamers/`, `tests/`, `docs/` | 1 | ✅ Done |
| 1.1.2 | Initialize git repository with `git init` | 1 | ✅ Done |
| 1.1.3 | Create `pyproject.toml` with hatchling build, dependencies, entry point `tidyup = "tidyup.cli:main"` | 2 | ✅ Done |
| 1.1.4 | Create `.gitignore` for Python projects | 1 | ✅ Done |
| 1.1.5 | Create `README.md` with project overview, installation, and usage | 2 | ✅ Done |
| 1.1.6 | Create `docs/REQUIREMENTS.md` with full specification | 3 | ✅ Done |

### 1.2 CLI Skeleton ✅

| ID | Task | Points | Status |
|----|------|--------|--------|
| 1.2.1 | Create `src/tidyup/cli.py` with Click group and `main()` entry point | 2 | ✅ Done |
| 1.2.2 | Add positional arguments: `source` (required), `destination` (optional) | 2 | ✅ Done |
| 1.2.3 | Add flags: `--move`, `--rename`, `--skip` | 1 | ✅ Done |
| 1.2.4 | Add flags: `--dry-run`, `--interactive`, `--limit`, `--verbose`, `--version` | 1 | ✅ Done |
| 1.2.5 | Add `status` subcommand stub | 1 | ✅ Done |
| 1.2.6 | Add `reindex` subcommand stub | 1 | ✅ Done |

### 1.3 CLI Tests ✅

| ID | Task | Points | Status |
|----|------|--------|--------|
| 1.3.1 | Set up pytest with `tests/conftest.py` and fixtures | 2 | ✅ Done |
| 1.3.2-7 | CLI tests (help, version, args, subcommands) | 6 | ✅ Done |

**Phase 1 Acceptance Criteria:** ✅ All met
- [x] `pip install -e .` succeeds
- [x] `tidyup --help` displays all flags and subcommands
- [x] `tidyup --version` shows `0.1.0`
- [x] All CLI tests pass

---

## Phase 2: Core Engine ✅ Complete

### 2.1 Data Models ✅

| ID | Task | Points | Status |
|----|------|--------|--------|
| 2.1.1 | `FileInfo` dataclass with path, name, extension, size, dates | 2 | ✅ Done |
| 2.1.2 | `DetectionResult` dataclass with category, confidence, detector_name, reason | 2 | ✅ Done |
| 2.1.3 | `RenameResult` dataclass with original/new name, extracted data | 2 | ✅ Done |
| 2.1.4 | `Action` dataclass with file, detection, rename, paths, status | 2 | ✅ Done |
| 2.1.5 | `RunSummary` dataclass with counts | 1 | ✅ Done |
| 2.1.6 | `RunResult` dataclass with timestamp, paths, options, actions, summary | 2 | ✅ Done |
| 2.1.7 | Unit tests for all dataclasses | 2 | ✅ Done |

### 2.2 Utilities ✅

| ID | Task | Points | Status |
|----|------|--------|--------|
| 2.2.1 | `sanitize_filename()` - clean special chars, collapse whitespace | 3 | ✅ Done |
| 2.2.2 | `format_size()` - human readable sizes | 1 | ✅ Done |
| 2.2.3 | `compute_file_hash()` - streaming SHA256 | 2 | ✅ Done |
| 2.2.4 | `get_file_dates()` - created/modified dates | 2 | ✅ Done |
| 2.2.5 | `generate_unique_path()` - append (1), (2) for conflicts | 2 | ✅ Done |
| 2.2.6 | Utility tests | 3 | ✅ Done |

### 2.3 File Discovery ✅

| ID | Task | Points | Status |
|----|------|--------|--------|
| 2.3.1 | `discover_files()` iterator with skip patterns | 3 | ✅ Done |
| 2.3.2 | Hidden file skip (files starting with `.`) | 1 | ✅ Done |
| 2.3.3 | Recent file skip (configurable hours) | 2 | ✅ Done |
| 2.3.4 | Pattern skip (`.DS_Store`, `*.tmp`, `*.crdownload`) | 2 | ✅ Done |
| 2.3.5 | `--limit N` handling | 1 | ✅ Done |
| 2.3.6 | Only return files (not directories) | 1 | ✅ Done |
| 2.3.7 | Discovery tests | 3 | ✅ Done |

### 2.4 File Operations ✅

| ID | Task | Points | Status |
|----|------|--------|--------|
| 2.4.1 | `safe_move()` - cross-device moves, create parent dirs | 3 | ✅ Done |
| 2.4.2 | `safe_rename()` - rename in place with conflict handling | 2 | ✅ Done |
| 2.4.3 | `ensure_dest_structure()` - create numbered folders | 3 | ✅ Done |
| 2.4.4 | `is_duplicate()` - hash-based duplicate detection | 3 | ✅ Done |
| 2.4.5 | `move_to_duplicates()` - move to _duplicates subfolder | 2 | ✅ Done |
| 2.4.6 | Operations tests | 5 | ✅ Done |

### 2.5 Logging System ✅

| ID | Task | Points | Status |
|----|------|--------|--------|
| 2.5.1 | `ensure_log_dir()` - create `~/.tidy/logs/` | 1 | ✅ Done |
| 2.5.2 | `ActionLogger` class with run data initialization | 2 | ✅ Done |
| 2.5.3 | `ActionLogger.log_action()` - append to actions list | 1 | ✅ Done |
| 2.5.4 | `ActionLogger.save()` - write JSON log file | 3 | ✅ Done |
| 2.5.5 | `load_log()` - parse JSON back to dataclass | 2 | ✅ Done |
| 2.5.6 | `list_logs()` - return sorted log files | 1 | ✅ Done |
| 2.5.7 | `aggregate_logs()` - sum stats from recent logs | 3 | ✅ Done |
| 2.5.8 | Logging tests | 3 | ✅ Done |

### 2.6 Engine Core ✅

| ID | Task | Points | Status |
|----|------|--------|--------|
| 2.6.1 | `Engine` class with initialization | 2 | ✅ Done |
| 2.6.2 | `Engine.run()` - main orchestration loop | 3 | ✅ Done |
| 2.6.3 | Processing loop: detect → rename → move → log | 3 | ✅ Done |
| 2.6.4 | `--move` mode (skip rename) | 2 | ✅ Done |
| 2.6.5 | `--rename` mode (skip move) | 2 | ✅ Done |
| 2.6.6 | Combined mode (default) | 1 | ✅ Done |
| 2.6.7 | `--skip` mode for uncertain files | 2 | ✅ Done |
| 2.6.8 | Uncertain file handling (move to Unsorted) | 2 | ✅ Done |
| 2.6.9 | `--dry-run` mode | 3 | ✅ Done |
| 2.6.10 | `--verbose` mode | 1 | ✅ Done |
| 2.6.11 | Wire engine to CLI | 2 | ✅ Done |
| 2.6.12 | Engine integration tests | 5 | ✅ Done |

**Phase 2 Acceptance Criteria:** ✅ All met
- [x] Can discover files respecting skip rules
- [x] Can move files with conflict handling
- [x] Can rename files in place
- [x] `--move`, `--rename`, `--skip` flags work
- [x] `--dry-run` shows accurate preview
- [x] Operations logged to `~/.tidy/logs/`
- [x] Duplicate files detected by hash
- [x] All tests pass (148 tests in Phase 2)

---

## Phase 2.5: Documentation ✅ Complete

| ID | Task | Points | Status |
|----|------|--------|--------|
| 2.7.1 | Update README.md with installation instructions | 2 | ✅ Done |
| 2.7.2 | Add CLI reference section | 2 | ✅ Done |
| 2.7.3 | Add usage examples | 2 | ✅ Done |
| 2.7.4 | Document folder structure | 1 | ✅ Done |
| 2.7.5 | Add configuration section | 2 | ✅ Done |
| 2.7.6 | Add troubleshooting section | 1 | ✅ Done |

---

## Phase 3: Detectors ✅ Complete

### 3.1 Detector Framework ✅

| ID | Task | Points | Status |
|----|------|--------|--------|
| 3.1.1 | `BaseDetector` abstract class with priority | 2 | ✅ Done |
| 3.1.2 | Confidence constants (HIGH=0.9, MEDIUM=0.7, LOW=0.5) | 1 | ✅ Done |
| 3.1.3 | `DetectorRegistry` class | 2 | ✅ Done |
| 3.1.4 | `DetectorRegistry.detect()` - run all, return best | 3 | ✅ Done |
| 3.1.5 | Tie-breaking by priority | 2 | ✅ Done |
| 3.1.6 | Framework tests | 3 | ✅ Done |

### 3.2 Extension-Based Detectors ✅

| ID | Task | Points | Status |
|----|------|--------|--------|
| 3.2.1 | `GenericDetector` with extension mapping (~80 extensions) | 3 | ✅ Done |
| 3.2.2-4 | Extension mappings for Documents, Images, Videos, Audio, Archives, Code, Books, Data | 3 | ✅ Done |
| 3.2.5 | `InstallerDetector` for dmg, pkg, exe, msi, deb, rpm, appimage | 2 | ✅ Done |
| 3.2.6 | Extension detector tests | 3 | ✅ Done |

### 3.3 Pattern-Based Detectors ✅

| ID | Task | Points | Status |
|----|------|--------|--------|
| 3.3.1 | `ScreenshotDetector` with filename patterns | 2 | ✅ Done |
| 3.3.2 | Screenshot patterns (macOS, Windows, CleanShot, Spanish, German, French) | 2 | ✅ Done |
| 3.3.3 | `ArxivDetector` with YYMM.NNNNN pattern | 2 | ✅ Done |
| 3.3.4 | arXiv pattern regex | 1 | ✅ Done |
| 3.3.5 | Pattern detector tests | 2 | ✅ Done |

### 3.4 Content-Based Detectors ✅

| ID | Task | Points | Status |
|----|------|--------|--------|
| 3.4.1 | `extract_pdf_text()` using pypdf | 3 | ✅ Done |
| 3.4.2 | Archive content listing | 3 | Skipped (not needed) |
| 3.4.3 | `InvoiceDetector` with PDF text analysis | 3 | ✅ Done |
| 3.4.4 | Invoice keywords (6 languages) | 1 | ✅ Done |
| 3.4.5 | Invoice detection logic | 2 | ✅ Done |
| 3.4.6 | `BookDetector` with ISBN and keyword detection | 3 | ✅ Done |
| 3.4.7 | Book detection for ebook extensions | 2 | ✅ Done |
| 3.4.8 | Book detection by ISBN pattern | 2 | ✅ Done |
| 3.4.9 | Content detector tests | 5 | ✅ Done |

### 3.5 Register All Detectors ✅

| ID | Task | Points | Status |
|----|------|--------|--------|
| 3.5.1 | Register all detectors in priority order | 2 | ✅ Done |
| 3.5.2 | Integration tests | 3 | ✅ Done |

**Phase 3 Acceptance Criteria:** ✅ All met
- [x] All file types correctly categorized by extension
- [x] Screenshots detected by filename pattern
- [x] arXiv papers detected by YYMM.NNNNN pattern
- [x] Invoices detected by keywords in PDF text
- [x] Books detected by ISBN/keywords
- [x] Installers detected (dmg, pkg, exe, msi, deb, etc.)
- [x] Confidence scores appropriate
- [x] Generic detector is fallback
- [x] All detector tests pass (219 total tests)

**Detectors Implemented:**
1. ScreenshotDetector (priority=10)
2. ArxivDetector (priority=10)
3. InvoiceDetector (priority=15)
4. InstallerDetector (priority=15)
5. BookDetector (priority=20)
6. GenericDetector (priority=50)

**Categories:**
- 01_Documents
- 02_Images
- 03_Videos
- 04_Audio
- 05_Archives
- 06_Code
- 07_Books
- 08_Data
- 09_Installers
- 99_Unsorted

---

## Phase 4: Renamers ✅ Complete

### 4.1 Renamer Framework ✅

| ID | Task | Points | Status |
|----|------|--------|--------|
| 4.1.1 | `BaseRenamer` abstract class | 2 | ✅ Done |
| 4.1.2 | `format_date()` helper (YYYY-MM-DD) | 1 | ✅ Done |
| 4.1.3 | `format_datetime()` helper (YYYY-MM-DD_HH-MM-SS) | 1 | ✅ Done |
| 4.1.4 | `RenamerRegistry` with detector-based lookup | 2 | ✅ Done |
| 4.1.5 | Framework tests | 2 | ✅ Done |

### 4.2 Generic Renamer ✅

| ID | Task | Points | Status |
|----|------|--------|--------|
| 4.2.1 | `GenericRenamer` class | 2 | ✅ Done |
| 4.2.2 | Pattern: `{date}_{sanitized_name}.{ext}` | 2 | ✅ Done |
| 4.2.3 | Handle "ugly names" (random strings, hashes) | 2 | ✅ Done |
| 4.2.4 | Keep nice filenames unchanged | 1 | ✅ Done |
| 4.2.5 | Tests | 2 | ✅ Done |

### 4.3 PDF Renamer ✅

| ID | Task | Points | Status |
|----|------|--------|--------|
| 4.3.1 | `extract_pdf_metadata()` for title and creation date | 3 | ✅ Done |
| 4.3.2 | `extract_title_from_text()` fallback to text heading | 2 | ✅ Done |
| 4.3.3 | Validate extracted title (length, garbage detection) | 2 | ✅ Done |
| 4.3.4 | `PDFRenamer` class | 2 | ✅ Done |
| 4.3.5 | Pattern: `{date}_{title}.pdf` | 1 | ✅ Done |
| 4.3.6 | Tests | 2 | ✅ Done |

### 4.4 Image Renamer ✅

| ID | Task | Points | Status |
|----|------|--------|--------|
| 4.4.1 | `extract_exif_date()` using Pillow | 3 | ✅ Done |
| 4.4.2 | Try DateTimeOriginal, DateTimeDigitized, DateTime | 1 | ✅ Done |
| 4.4.3 | `ImageRenamer` class | 2 | ✅ Done |
| 4.4.4 | Pattern: `{exif_date}_{original_name}.{ext}` | 1 | ✅ Done |
| 4.4.5 | Tests | 2 | ✅ Done |

### 4.5 Category-Specific Renamers ✅

| ID | Task | Points | Status |
|----|------|--------|--------|
| 4.5.1 | `ScreenshotRenamer` - standardize to `Screenshot_{date}_{time}.{ext}` | 3 | ✅ Done |
| 4.5.2 | Screenshot datetime extraction (macOS, Windows, CleanShot patterns) | 2 | ✅ Done |
| 4.5.3 | `ArxivRenamer` - pattern `{date}_{arxiv_id}.pdf` | 2 | ✅ Done |
| 4.5.4 | `InvoiceRenamer` - pattern `{date}_Invoice_{vendor}.pdf` | 3 | ✅ Done |
| 4.5.5 | Vendor extraction from invoice text | 2 | ✅ Done |
| 4.5.6 | Tests | 3 | ✅ Done |

### 4.6 Integration ✅

| ID | Task | Points | Status |
|----|------|--------|--------|
| 4.6.1 | Wire `RenamerRegistry` into engine | 2 | ✅ Done |
| 4.6.2 | Register all renamers by detector name | 1 | ✅ Done |
| 4.6.3 | Integration tests | 2 | ✅ Done |

**Phase 4 Acceptance Criteria:** ✅ All met
- [x] BaseRenamer abstract class with rename() method
- [x] RenamerRegistry maps detectors to specialized renamers
- [x] GenericRenamer as fallback for ugly names
- [x] PDFRenamer extracts title from metadata/text
- [x] ImageRenamer uses EXIF dates
- [x] ScreenshotRenamer standardizes patterns
- [x] ArxivRenamer keeps ID with date prefix
- [x] InvoiceRenamer extracts vendor name
- [x] Engine uses renamer registry
- [x] All renamer tests pass (22 tests)

**Renamers Implemented:**
1. GenericRenamer (default fallback)
2. PDFRenamer (for GenericDetector with PDFs)
3. ImageRenamer (for photos with EXIF)
4. ScreenshotRenamer (for ScreenshotDetector)
5. ArxivRenamer (for ArxivDetector)
6. InvoiceRenamer (for InvoiceDetector)

---

## Phase 4.5: Content-Based Enhancements ✅ Complete

### 4.5.0 Dynamic Category Management (Foundation) ✅

| ID | Task | Points | Status |
|----|------|--------|--------|
| 4.5.0.1 | Create `Category` dataclass with number, name fields | 1 | ✅ Done |
| 4.5.0.2 | Create `CategoryManager` class with load/save methods | 3 | ✅ Done |
| 4.5.0.3 | Implement `add()` - add category at position, renumber others | 2 | ✅ Done |
| 4.5.0.4 | Implement `remove()` - remove category (must be empty) | 2 | ✅ Done |
| 4.5.0.5 | Implement `reorder()` - reorder categories by name list | 2 | ✅ Done |
| 4.5.0.6 | Implement `get_folder_name()` - return `NN_Name` format | 1 | ✅ Done |
| 4.5.0.7 | Implement `apply_to_filesystem()` - rename folders on disk | 3 | ✅ Done |
| 4.5.0.8 | Add YAML config support for categories in `~/.tidy/config.yaml` | 2 | ✅ Done |
| 4.5.0.9 | Add `tidyup categories` CLI subcommand group | 2 | ✅ Done |
| 4.5.0.10 | Add `tidyup categories list` - show current categories | 1 | ✅ Done |
| 4.5.0.11 | Add `tidyup categories add <name> --position N` | 2 | ✅ Done |
| 4.5.0.12 | Add `tidyup categories remove <name>` | 2 | ✅ Done |
| 4.5.0.13 | Migrate `operations.py` to use CategoryManager | 3 | ✅ Done |
| 4.5.0.14 | Update all detectors to use category names (not hardcoded strings) | 3 | ✅ Done |
| 4.5.0.15 | CategoryManager tests | 5 | ✅ Done |

### 4.5.1 Screenshots Category ✅

| ID | Task | Points | Status |
|----|------|--------|--------|
| 4.5.1.1 | Add "Screenshots" to default categories (position 2) | 1 | ✅ Done |
| 4.5.1.2 | Update `ScreenshotDetector` to return category "Screenshots" | 1 | ✅ Done |
| 4.5.1.3 | Update screenshot tests for new category | 1 | ✅ Done |

### 4.5.2 Papers Category ✅

| ID | Task | Points | Status |
|----|------|--------|--------|
| 4.5.2.1 | Add "Papers" to default categories (position 9) | 1 | ✅ Done |
| 4.5.2.2 | Update `ArxivDetector` to return category "Papers" | 1 | ✅ Done |
| 4.5.2.3 | Create `PaperDetector` (priority 12) for non-arXiv papers | 3 | ✅ Done |
| 4.5.2.4 | Paper keywords: abstract, references, citations, et al., DOI | 2 | ✅ Done |
| 4.5.2.5 | Register `PaperDetector` in registry | 1 | ✅ Done |
| 4.5.2.6 | Paper detector tests | 3 | ✅ Done |

### 4.5.3 Enhanced Book Detection ✅

| ID | Task | Points | Status |
|----|------|--------|--------|
| 4.5.3.1 | Create `ArchiveBookDetector` (priority 18) | 3 | ✅ Done |
| 4.5.3.2 | ZIP content inspection for ebook files (.epub, .mobi, .pdf) | 2 | ✅ Done |
| 4.5.3.3 | Filename heuristics for RAR/7z (edition, handbook, etc.) | 2 | ✅ Done |
| 4.5.3.4 | Register `ArchiveBookDetector` in registry | 1 | ✅ Done |
| 4.5.3.5 | Archive book detector tests | 3 | ✅ Done |

### 4.5.4 Book Renamer ✅

| ID | Task | Points | Status |
|----|------|--------|--------|
| 4.5.4.1 | Create `BookRenamer` class | 2 | ✅ Done |
| 4.5.4.2 | Pattern: `{pub_year}_{title}_{author}.ext` | 1 | ✅ Done |
| 4.5.4.3 | PDF metadata extraction (title, author, date) | 2 | ✅ Done |
| 4.5.4.4 | EPUB OPF metadata extraction (dc:title, dc:creator, dc:date) | 3 | ✅ Done |
| 4.5.4.5 | Register `BookRenamer` for BookDetector and ArchiveBookDetector | 1 | ✅ Done |
| 4.5.4.6 | Book renamer tests | 3 | ✅ Done |

### 4.5.5 Update Tests and Documentation ✅

| ID | Task | Points | Status |
|----|------|--------|--------|
| 4.5.5.1 | Update all detector tests for new category names | 3 | ✅ Done |
| 4.5.5.2 | Update operations tests for CategoryManager | 2 | ✅ Done |
| 4.5.5.3 | Update README.md with new categories | 1 | ✅ Done |
| 4.5.5.4 | Update REQUIREMENTS.md with category management | 2 | Skipped |

**Phase 4.5 Acceptance Criteria:** ✅ All met
- [x] Categories stored in config, not hardcoded
- [x] Can add/remove/reorder categories via CLI
- [x] Filesystem folders renamed when categories change
- [x] Screenshots → separate 02_Screenshots category
- [x] Research papers → 09_Papers category
- [x] Archives containing ebooks → Books category
- [x] Books renamed with title/author from metadata
- [x] All tests pass (321 tests)

**New Detectors:**
- PaperDetector (priority=12) → Papers
- ArchiveBookDetector (priority=18) → Books

**New Renamers:**
- BookRenamer (for BookDetector, ArchiveBookDetector)

**New Category Structure:**
```
01_Documents, 02_Screenshots, 03_Images, 04_Videos, 05_Audio,
06_Archives, 07_Code, 08_Books, 09_Papers, 10_Data, 11_Installers, 99_Unsorted
```

---

## Phase 5: Safety & Polish 🔲 Partial

### 5.1 Dry Run Mode

| ID | Task | Points | Status |
|----|------|--------|--------|
| 5.1.1-6 | DryRunFormatter, pagination, color coding | 13 | Partial (basic table done) |

### 5.2 Interactive Mode

| ID | Task | Points | Status |
|----|------|--------|--------|
| 5.2.1-6 | Interactive prompts for uncertain files | 14 | Todo |

### 5.3 Configuration

| ID | Task | Points | Status |
|----|------|--------|--------|
| 5.3.1-8 | Config loading, validation, defaults | 16 | Todo |

### 5.4 Rich Output

| ID | Task | Points | Status |
|----|------|--------|--------|
| 5.4.1-5 | Progress bar, colors, tables | 9 | Partial (basic Rich output) |

### 5.5 Status Command

| ID | Task | Points | Status |
|----|------|--------|--------|
| 5.5.1-7 | Full status implementation | 13 | Todo (stub exists) |

### 5.6 Reindex Command

| ID | Task | Points | Status |
|----|------|--------|--------|
| 5.6.1-10 | Folder reindexing | 20 | Todo (stub exists) |

---

## Phase 6: Quality & Release 🟡 Partial

### 6.1 Code Quality ✅

| ID | Task | Points | Status |
|----|------|--------|--------|
| 6.1.1 | Fix all ruff linting issues | 2 | ✅ Done |
| 6.1.2 | Add mypy configuration | 2 | ✅ Done |
| 6.1.3 | Fix all type errors | 3 | ✅ Done |
| 6.1.4 | Verify 85%+ test coverage | 3 | ✅ Done (85%)

### 6.2 Testing

| ID | Task | Points | Status |
|----|------|--------|--------|
| 6.2.1-5 | Coverage, fixtures, E2E tests | 16 | Partial (219 tests) |

### 6.3 Documentation

| ID | Task | Points | Status |
|----|------|--------|--------|
| 6.3.1-4 | Final docs, CHANGELOG | 6 | Todo |

### 6.4 Release

| ID | Task | Points | Status |
|----|------|--------|--------|
| 6.4.1-5 | Test installs, tag, push | 5 | Partial (pushed to GitHub) |

---

## Summary

| Phase | Status | Tests |
|-------|--------|-------|
| 1. Scaffolding | ✅ Complete | - |
| 2. Core Engine | ✅ Complete | 148 |
| 2.5 Documentation | ✅ Complete | - |
| 3. Detectors | ✅ Complete | 71 |
| 4. Renamers | ✅ Complete | 22 |
| 4.5 Content-Based Enhancements | ✅ Complete | 80 |
| 5. Safety & Polish | 🟡 Partial | - |
| 6. Quality & Release | 🟡 Partial | - |
| **Total** | | **321 tests** |

---

## Repository

- **GitHub**: https://github.com/Gonzillaaa/tidyup
- **Package**: `tidyup`
- **CLI Command**: `tidyup`

---

## Future Enhancements (Icebox)

Not scheduled for v1.0:

- [ ] **Watch mode**: Monitor Downloads folder, auto-organize new files
- [ ] **Custom plugins**: Load detector/renamer plugins from `~/.tidy/plugins/`
- [ ] **Duplicate finder**: Scan destination for duplicates
- [ ] **Undo command**: Reverse most recent run from logs
- [ ] **GUI wrapper**: Simple native macOS app
