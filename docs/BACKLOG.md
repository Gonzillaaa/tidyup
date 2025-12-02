# Tidy - Product Backlog

This document tracks all implementation tasks with story points, dependencies, and acceptance criteria.

**Story Point Scale:**
- 1 = Trivial (< 30 min)
- 2 = Small (30 min - 2 hours)
- 3 = Medium (2-4 hours)
- 5 = Large (4-8 hours)
- 8 = Very Large (1-2 days)
- 13 = Epic (needs breakdown)

**Task Format:**
Each task includes: description of what to build, acceptance criteria, and testing requirements.

---

## Phase 1: Scaffolding ✅

### 1.1 Project Setup (Complete)

| ID | Task | Points | Status |
|----|------|--------|--------|
| 1.1.1 | Create directory structure: `src/tidy/`, `src/tidy/detectors/`, `src/tidy/renamers/`, `tests/`, `docs/` | 1 | ✅ Done |
| 1.1.2 | Initialize git repository with `git init` | 1 | ✅ Done |
| 1.1.3 | Create `pyproject.toml` with hatchling build, dependencies (click, pyyaml, pypdf, pillow, rich), and `[project.scripts]` entry point `tidy = "tidy.cli:main"` | 2 | ✅ Done |
| 1.1.4 | Create `.gitignore` for Python projects (pycache, venv, .egg-info, etc.) | 1 | ✅ Done |
| 1.1.5 | Create `README.md` with project overview, installation, and basic usage examples | 2 | ✅ Done |
| 1.1.6 | Create `docs/REQUIREMENTS.md` with full specification | 3 | ✅ Done |

### 1.2 CLI Skeleton (Complete)

| ID | Task | Points | Status |
|----|------|--------|--------|
| 1.2.1 | Create `src/tidy/cli.py` with Click group and `main()` entry point | 2 | ✅ Done |
| 1.2.2 | Add positional arguments: `source` (required, Path), `destination` (optional, Path) | 2 | ✅ Done |
| 1.2.3 | Add flags: `--move` (only move, keep names), `--rename` (only rename in place), `--skip` (skip uncertain files) | 1 | ✅ Done |
| 1.2.4 | Add flags: `--dry-run`, `--interactive` / `-i`, `--limit N` / `-n`, `--verbose` / `-v`, `--version` | 1 | ✅ Done |
| 1.2.5 | Add `status` subcommand stub that prints placeholder | 1 | ✅ Done |
| 1.2.6 | Add `reindex` subcommand stub that prints placeholder | 1 | ✅ Done |

### 1.3 CLI Tests (Todo)

| ID | Task | Points | Status | Dependencies |
|----|------|--------|--------|--------------|
| 1.3.1 | Set up pytest with `tests/conftest.py` and basic fixtures | 2 | Todo | 1.2.6 |
| 1.3.2 | Test: `tidy --help` shows usage with all flags and commands | 1 | Todo | 1.3.1 |
| 1.3.3 | Test: `tidy --version` outputs version string | 1 | Todo | 1.3.1 |
| 1.3.4 | Test: `tidy` with no args shows help | 1 | Todo | 1.3.1 |
| 1.3.5 | Test: `tidy /nonexistent` returns error for missing source | 1 | Todo | 1.3.1 |
| 1.3.6 | Test: `tidy status` runs without error | 1 | Todo | 1.3.1 |
| 1.3.7 | Test: `tidy reindex` runs without error | 1 | Todo | 1.3.1 |

**Phase 1 Acceptance Criteria:**
- [ ] `pip install -e .` succeeds
- [ ] `tidy --help` displays all flags and subcommands
- [ ] `tidy --version` shows `0.1.0`
- [ ] All CLI tests pass

---

## Phase 2: Core Engine

### 2.1 Data Models

| ID | Task | Points | Status | Dependencies |
|----|------|--------|--------|--------------|
| 2.1.1 | Create `src/tidy/models.py` with `FileInfo` dataclass containing: `path: Path`, `name: str`, `extension: str`, `size: int`, `modified: datetime`, `created: datetime` | 2 | Todo | 1.3.7 |
| 2.1.2 | Add `DetectionResult` dataclass: `category: str`, `confidence: float` (0.0-1.0), `detector_name: str`, `reason: str | None` | 2 | Todo | 2.1.1 |
| 2.1.3 | Add `RenameResult` dataclass: `original_name: str`, `new_name: str`, `date_extracted: date | None`, `title_extracted: str | None`, `renamer_name: str` | 2 | Todo | 2.1.1 |
| 2.1.4 | Add `Action` dataclass: `file: FileInfo`, `detection: DetectionResult`, `rename: RenameResult | None`, `source_path: Path`, `dest_path: Path`, `status: Literal["pending", "success", "error", "skipped"]`, `error: str | None` | 2 | Todo | 2.1.2, 2.1.3 |
| 2.1.5 | Add `RunSummary` dataclass: `processed: int`, `moved: int`, `renamed: int`, `unsorted: int`, `skipped: int`, `errors: int`, `duplicates: int` | 1 | Todo | 2.1.4 |
| 2.1.6 | Add `RunResult` dataclass: `timestamp: datetime`, `source: Path`, `destination: Path`, `options: dict`, `actions: list[Action]`, `summary: RunSummary` | 2 | Todo | 2.1.5 |
| 2.1.7 | Write unit tests for all dataclasses (creation, serialization to dict) | 2 | Todo | 2.1.6 |

### 2.2 Utilities

| ID | Task | Points | Status | Dependencies |
|----|------|--------|--------|--------------|
| 2.2.1 | Create `src/tidy/utils.py` with `sanitize_filename(name: str) -> str`: remove/replace special chars (`/\:*?"<>|`), collapse whitespace, limit length to 200 chars, handle unicode | 3 | Todo | - |
| 2.2.2 | Add `format_size(bytes: int) -> str`: convert to human readable (KB, MB, GB) | 1 | Todo | 2.2.1 |
| 2.2.3 | Add `compute_file_hash(path: Path, algorithm="sha256", chunk_size=8192) -> str`: streaming hash for large files | 2 | Todo | 2.2.1 |
| 2.2.4 | Add `get_file_dates(path: Path) -> tuple[datetime, datetime]`: return (created, modified) handling OS differences | 2 | Todo | 2.2.1 |
| 2.2.5 | Add `generate_unique_path(dest: Path) -> Path`: if exists, append ` (1)`, ` (2)`, etc. until unique | 2 | Todo | 2.2.1 |
| 2.2.6 | Write unit tests for all utility functions | 3 | Todo | 2.2.1-2.2.5 |

### 2.3 File Discovery

| ID | Task | Points | Status | Dependencies |
|----|------|--------|--------|--------------|
| 2.3.1 | Create `src/tidy/discovery.py` with `discover_files(source: Path, skip_patterns: list[str], skip_hidden: bool, skip_recent_hours: int) -> Iterator[FileInfo]` | 3 | Todo | 2.1.1 |
| 2.3.2 | Implement hidden file skip: files starting with `.` | 1 | Todo | 2.3.1 |
| 2.3.3 | Implement recent file skip: check modified time against `skip_recent_hours` config value | 2 | Todo | 2.3.1 |
| 2.3.4 | Implement pattern skip: match against `.DS_Store`, `*.tmp`, `*.crdownload`, `*.part` and custom patterns | 2 | Todo | 2.3.1 |
| 2.3.5 | Implement `--limit N` handling: yield only first N files | 1 | Todo | 2.3.1 |
| 2.3.6 | Ensure only files are returned (not directories) | 1 | Todo | 2.3.1 |
| 2.3.7 | Write discovery tests with temp directories containing various file types | 3 | Todo | 2.3.1-2.3.6 |

### 2.4 File Operations

| ID | Task | Points | Status | Dependencies |
|----|------|--------|--------|--------------|
| 2.4.1 | Create `src/tidy/operations.py` with `safe_move(src: Path, dest: Path) -> Path`: create parent dirs, handle cross-device moves, return final path | 3 | Todo | 2.2.5 |
| 2.4.2 | Add `safe_rename(path: Path, new_name: str) -> Path`: rename in same directory, handle conflicts with `(1)` suffix | 2 | Todo | 2.2.5 |
| 2.4.3 | Add `ensure_dest_structure(dest: Path, folders: list[dict]) -> None`: create numbered folders like `01_Documents/`, `02_Images/`, etc. based on config | 3 | Todo | - |
| 2.4.4 | Add `is_duplicate(file: Path, dest_folder: Path) -> Path | None`: hash file, check against existing files in dest, return existing path if duplicate | 3 | Todo | 2.2.3 |
| 2.4.5 | Add `move_to_duplicates(file: Path, dest: Path) -> Path`: move to `99_Unsorted/_duplicates/` subfolder | 2 | Todo | 2.4.1 |
| 2.4.6 | Write operations tests using temp directories, verify files actually moved/renamed | 5 | Todo | 2.4.1-2.4.5 |

### 2.5 Logging System

| ID | Task | Points | Status | Dependencies |
|----|------|--------|--------|--------------|
| 2.5.1 | Create `src/tidy/logger.py` with `ensure_log_dir() -> Path`: create `~/.tidy/logs/` if not exists, return path | 1 | Todo | - |
| 2.5.2 | Add `ActionLogger` class with `__init__(source: Path, dest: Path, options: dict)` that initializes run data | 2 | Todo | 2.5.1, 2.1.6 |
| 2.5.3 | Add `ActionLogger.log_action(action: Action)`: append to internal actions list | 1 | Todo | 2.5.2 |
| 2.5.4 | Add `ActionLogger.save() -> Path`: write JSON to `~/.tidy/logs/YYYY-MM-DD_HHMMSS.json` with format matching REQUIREMENTS (timestamp, source, destination, options, actions array, summary) | 3 | Todo | 2.5.3 |
| 2.5.5 | Add `load_log(path: Path) -> RunResult`: parse JSON log file back to dataclass | 2 | Todo | 2.1.6 |
| 2.5.6 | Add `list_logs(limit: int = None) -> list[Path]`: return log files sorted by date descending | 1 | Todo | 2.5.1 |
| 2.5.7 | Add `aggregate_logs(days: int = 7) -> dict`: sum up stats from recent logs for status command | 3 | Todo | 2.5.5, 2.5.6 |
| 2.5.8 | Write logging tests: create log, read it back, verify contents | 3 | Todo | 2.5.1-2.5.7 |

### 2.6 Engine Core

| ID | Task | Points | Status | Dependencies |
|----|------|--------|--------|--------------|
| 2.6.1 | Create `src/tidy/engine.py` with `Engine` class, `__init__(source: Path, dest: Path | None, options: dict, config: Config)` | 2 | Todo | 2.3.1, 2.4.1 |
| 2.6.2 | Add `Engine.run() -> RunResult`: main orchestration loop that processes files | 3 | Todo | 2.6.1 |
| 2.6.3 | Implement processing loop: for each file → detect category → rename → move → log action | 3 | Todo | 2.6.2 |
| 2.6.4 | Implement `--move` mode: skip rename step, use original filename, still detect and move to category folder | 2 | Todo | 2.6.3 |
| 2.6.5 | Implement `--rename` mode: skip move step, rename file in place within source directory, no destination needed | 2 | Todo | 2.6.3 |
| 2.6.6 | Implement combined mode (default): both detect→rename→move | 1 | Todo | 2.6.4, 2.6.5 |
| 2.6.7 | Implement `--skip` mode: when detection confidence < 0.7, skip file entirely (leave in source), log as skipped | 2 | Todo | 2.6.3 |
| 2.6.8 | Implement uncertain file handling (no --skip): move to `99_Unsorted/` with original name, log reason | 2 | Todo | 2.6.3 |
| 2.6.9 | Implement `--dry-run` mode: run full pipeline but don't execute moves/renames, collect actions, return result | 3 | Todo | 2.6.3 |
| 2.6.10 | Implement `--verbose` mode: set flag for detailed console output (handled in CLI layer) | 1 | Todo | 2.6.3 |
| 2.6.11 | Wire engine to CLI: import and call from `run_organize()` function | 2 | Todo | 2.6.1-2.6.10 |
| 2.6.12 | Write engine integration tests: create source with test files, run engine, verify results | 5 | Todo | 2.6.11 |

**Phase 2 Acceptance Criteria:**
- [x] Can discover files in source directory respecting skip rules
- [x] Can move files to destination with `(1)` conflict handling
- [x] Can rename files in place
- [x] `--move`, `--rename`, `--skip` flags work correctly
- [x] `--dry-run` shows accurate preview without making changes
- [x] All operations logged to `~/.tidy/logs/` in correct JSON format
- [x] Duplicate files detected by hash and moved to `_duplicates/`
- [x] All tests pass (148 tests)

---

## Phase 2.5: Documentation

Documentation should be completed before moving to Phase 3 (Detectors).

### 2.7 User Documentation

| ID | Task | Points | Status | Dependencies |
|----|------|--------|--------|--------------|
| 2.7.1 | Update `README.md` with comprehensive installation instructions (pip, pipx, from source) | 2 | ✅ Done | 2.6.12 |
| 2.7.2 | Add CLI reference section to README with all commands, flags, and options | 2 | ✅ Done | 2.7.1 |
| 2.7.3 | Add usage examples covering common workflows (dry-run, move-only, rename-only, etc.) | 2 | ✅ Done | 2.7.2 |
| 2.7.4 | Document folder structure and category mapping | 1 | ✅ Done | 2.7.3 |
| 2.7.5 | Add configuration section explaining ~/.tidy/ directory and config options | 2 | ✅ Done | 2.7.4 |
| 2.7.6 | Add troubleshooting section with common issues and solutions | 1 | ✅ Done | 2.7.5 |

**Phase 2.5 Acceptance Criteria:**
- [x] README.md contains complete installation instructions
- [x] All CLI commands and flags are documented
- [x] Usage examples cover all major use cases
- [x] New users can install and use tidy without external help

---

## Phase 3: Detectors

### 3.1 Detector Framework

| ID | Task | Points | Status | Dependencies |
|----|------|--------|--------|--------------|
| 3.1.1 | Create `src/tidy/detectors/base.py` with `BaseDetector` abstract class: `name: str` property, `detect(file: FileInfo) -> DetectionResult | None` abstract method | 2 | Todo | 2.1.2 |
| 3.1.2 | Add `CONFIDENCE_HIGH = 0.9`, `CONFIDENCE_MEDIUM = 0.7`, `CONFIDENCE_LOW = 0.5` constants | 1 | Todo | 3.1.1 |
| 3.1.3 | Create `src/tidy/detectors/__init__.py` with `DetectorRegistry`: list of detector instances, method to register new detectors | 2 | Todo | 3.1.1 |
| 3.1.4 | Add `DetectorRegistry.detect(file: FileInfo) -> DetectionResult`: run all detectors, collect results, return highest confidence result | 3 | Todo | 3.1.3 |
| 3.1.5 | Handle tie-breaking: if multiple detectors have same confidence, prefer more specific detector (invoice > document) | 2 | Todo | 3.1.4 |
| 3.1.6 | Write framework tests: mock detectors, verify pipeline behavior | 3 | Todo | 3.1.1-3.1.5 |

### 3.2 Extension-Based Detectors

| ID | Task | Points | Status | Dependencies |
|----|------|--------|--------|--------------|
| 3.2.1 | Create `src/tidy/detectors/generic.py` with `GenericDetector`: map extensions to categories using config, return CONFIDENCE_MEDIUM (0.7) | 3 | Todo | 3.1.1 |
| 3.2.2 | Extension mapping for Documents: `pdf`, `docx`, `doc`, `txt`, `rtf`, `md`, `odt` → `01_Documents` | 1 | Todo | 3.2.1 |
| 3.2.3 | Extension mapping for Images: `png`, `jpg`, `jpeg`, `heic`, `webp`, `gif`, `bmp`, `tiff`, `svg` → `02_Images` | 1 | Todo | 3.2.1 |
| 3.2.4 | Extension mapping for Archives: `zip`, `rar`, `tgz`, `tar`, `gz`, `7z`, `bz2` → `04_Archives` | 1 | Todo | 3.2.1 |
| 3.2.5 | Create `InstallerDetector`: extensions `dmg`, `pkg`, `app`, `exe`, `msi` → `05_Installers`, CONFIDENCE_HIGH (0.9) | 2 | Todo | 3.1.1 |
| 3.2.6 | Create `MediaDetector`: extensions `mp3`, `mp4`, `mov`, `wav`, `avi`, `mkv`, `m4a`, `flac`, `m4v`, `webm` → `06_Media`, CONFIDENCE_HIGH | 2 | Todo | 3.1.1 |
| 3.2.7 | Create `DataDetector`: extensions `csv`, `json`, `xlsx`, `xls`, `xml`, `yaml`, `yml` → `07_Data`, CONFIDENCE_HIGH | 2 | Todo | 3.1.1 |
| 3.2.8 | Write tests for all extension detectors | 3 | Todo | 3.2.1-3.2.7 |

### 3.3 Pattern-Based Detectors

| ID | Task | Points | Status | Dependencies |
|----|------|--------|--------|--------------|
| 3.3.1 | Create `src/tidy/detectors/screenshot.py` with `ScreenshotDetector`: detect by filename patterns, return `02_Images` category, CONFIDENCE_HIGH | 2 | Todo | 3.1.1 |
| 3.3.2 | Screenshot patterns to match: `Screenshot*`, `Screen Shot*`, `Captura*`, `Bildschirmfoto*`, macOS format `Screen Shot YYYY-MM-DD at HH.MM.SS` | 2 | Todo | 3.3.1 |
| 3.3.3 | Create `src/tidy/detectors/arxiv.py` with `ArxivDetector`: detect by filename pattern, return `08_Papers`, CONFIDENCE_HIGH | 2 | Todo | 3.1.1 |
| 3.3.4 | arXiv pattern regex: `^\d{4}\.\d{4,5}(v\d+)?\.pdf$` (e.g., `2501.12948v1.pdf`) | 1 | Todo | 3.3.3 |
| 3.3.5 | Write tests for pattern detectors with various filename examples | 2 | Todo | 3.3.1-3.3.4 |

### 3.4 Content-Based Detectors

| ID | Task | Points | Status | Dependencies |
|----|------|--------|--------|--------------|
| 3.4.1 | Create `src/tidy/content.py` with `extract_pdf_text(path: Path, max_pages: int = 2) -> str`: use pypdf to extract text from first N pages | 3 | Todo | - |
| 3.4.2 | Add `list_archive_contents(path: Path) -> list[str]`: list filenames inside zip/rar without extracting, handle errors gracefully | 3 | Todo | - |
| 3.4.3 | Create `src/tidy/detectors/invoice.py` with `InvoiceDetector`: check filename AND PDF text for invoice keywords | 3 | Todo | 3.1.1, 3.4.1 |
| 3.4.4 | Invoice keywords to search (case-insensitive): `invoice`, `receipt`, `factura`, `rechnung`, `quittung`, `bill`, `payment`, `order confirmation` | 1 | Todo | 3.4.3 |
| 3.4.5 | Invoice detection logic: if keyword in filename → CONFIDENCE_HIGH, if keyword in PDF text → CONFIDENCE_MEDIUM, return `09_Invoices` | 2 | Todo | 3.4.3 |
| 3.4.6 | Create `src/tidy/detectors/book.py` with `BookDetector`: detect ebooks in archives or by filename patterns | 3 | Todo | 3.1.1, 3.4.2 |
| 3.4.7 | Book detection for archives: if contains `.epub`, `.mobi`, `.pdf` files → likely book, return `03_Books`, CONFIDENCE_MEDIUM | 2 | Todo | 3.4.6 |
| 3.4.8 | Book detection by filename: ISBN pattern `\d{10}|\d{13}`, "Edition" keyword, publisher names (O'Reilly, Packt, Manning, Apress) → CONFIDENCE_MEDIUM | 2 | Todo | 3.4.6 |
| 3.4.9 | Write content detector tests with fixture files (sample PDF, sample ZIP with ebook) | 5 | Todo | 3.4.1-3.4.8 |

### 3.5 Register All Detectors

| ID | Task | Points | Status | Dependencies |
|----|------|--------|--------|--------------|
| 3.5.1 | Update `detectors/__init__.py` to instantiate and register all detectors in priority order: Invoice, Book, Arxiv, Screenshot, Installer, Media, Data, Generic | 2 | Todo | 3.2.8, 3.3.5, 3.4.9 |
| 3.5.2 | Write integration test: pass various files through full detection pipeline, verify correct categories | 3 | Todo | 3.5.1 |

**Phase 3 Acceptance Criteria:**
- [ ] All file types correctly categorized by extension
- [ ] Screenshots detected by filename pattern (macOS, Windows, Linux formats)
- [ ] arXiv papers detected by `YYMM.NNNNN` pattern
- [ ] Invoices detected by keywords in filename or PDF text
- [ ] Books detected by archive contents or ISBN/publisher patterns
- [ ] Confidence scores appropriate: CONFIDENCE_HIGH for certain, CONFIDENCE_MEDIUM for probable
- [ ] Generic detector is fallback for unknown extensions
- [ ] All detector tests pass

---

## Phase 4: Renamers

### 4.1 Renamer Framework

| ID | Task | Points | Status | Dependencies |
|----|------|--------|--------|--------------|
| 4.1.1 | Create `src/tidy/renamers/base.py` with `BaseRenamer` abstract class: `name: str` property, `rename(file: FileInfo, detection: DetectionResult) -> RenameResult` abstract method | 2 | Todo | 2.1.3 |
| 4.1.2 | Add `format_date(dt: datetime) -> str`: return ISO format `YYYY-MM-DD` | 1 | Todo | 4.1.1 |
| 4.1.3 | Add `format_datetime(dt: datetime) -> str`: return `YYYY-MM-DD_HH-MM-SS` for screenshots | 1 | Todo | 4.1.1 |
| 4.1.4 | Create `RenamerRegistry` in `renamers/__init__.py`: map category → renamer | 2 | Todo | 4.1.1 |
| 4.1.5 | Write framework tests | 2 | Todo | 4.1.1-4.1.4 |

### 4.2 Generic Renamer

| ID | Task | Points | Status | Dependencies |
|----|------|--------|--------|--------------|
| 4.2.1 | Create `src/tidy/renamers/generic.py` with `GenericRenamer`: fallback renamer for any file type | 2 | Todo | 4.1.1, 2.2.1 |
| 4.2.2 | Implement pattern: `{date}_{sanitized_original_name}.{ext}` where date is file modified date | 2 | Todo | 4.2.1 |
| 4.2.3 | Handle "ugly names" (random strings, UUIDs, timestamps): if filename is mostly digits/random, use just date + generic name | 2 | Todo | 4.2.2 |
| 4.2.4 | Write tests for generic renamer with various filename inputs | 2 | Todo | 4.2.1-4.2.3 |

### 4.3 PDF Renamer

| ID | Task | Points | Status | Dependencies |
|----|------|--------|--------|--------------|
| 4.3.1 | Create `src/tidy/renamers/pdf.py` with `PDFRenamer`: extract title and date from PDF metadata | 3 | Todo | 4.1.1, 3.4.1 |
| 4.3.2 | Extract metadata using pypdf: `/Title`, `/Author`, `/CreationDate`, `/ModDate` | 2 | Todo | 4.3.1 |
| 4.3.3 | Fallback 1: if no title in metadata, extract first heading or bold text from first page | 3 | Todo | 4.3.1, 3.4.1 |
| 4.3.4 | Fallback 2: if no title found, use sanitized original filename | 1 | Todo | 4.3.3 |
| 4.3.5 | Implement pattern: `{date}_{title}.pdf` using creation date or file date | 1 | Todo | 4.3.2 |
| 4.3.6 | Write tests with sample PDFs (with metadata, without metadata, scanned) | 3 | Todo | 4.3.1-4.3.5 |

### 4.4 Image Renamer

| ID | Task | Points | Status | Dependencies |
|----|------|--------|--------|--------------|
| 4.4.1 | Create `src/tidy/renamers/image.py` with `ImageRenamer`: extract date from EXIF | 3 | Todo | 4.1.1 |
| 4.4.2 | Extract EXIF tags using Pillow: `DateTimeOriginal`, `CreateDate`, `DateTime` | 2 | Todo | 4.4.1 |
| 4.4.3 | Fallback: if no EXIF date, use file modified date | 1 | Todo | 4.4.2 |
| 4.4.4 | Implement pattern: `{exif_date}_{original_name}.{ext}` | 1 | Todo | 4.4.2 |
| 4.4.5 | Write tests with sample images (with EXIF, without EXIF) | 2 | Todo | 4.4.1-4.4.4 |

### 4.5 Category-Specific Patterns

| ID | Task | Points | Status | Dependencies |
|----|------|--------|--------|--------------|
| 4.5.1 | Create `InvoiceRenamer`: pattern `{date}_Invoice_{vendor}.pdf`, extract vendor from text if possible | 3 | Todo | 4.3.1, 3.4.3 |
| 4.5.2 | Vendor extraction: look for company names near "invoice" keyword, or use domain from email if present | 2 | Todo | 4.5.1 |
| 4.5.3 | Create `ScreenshotRenamer`: pattern `Screenshot_{date}_{time}.{ext}`, extract time from filename if present | 2 | Todo | 4.2.1 |
| 4.5.4 | Create `ArxivRenamer`: pattern `{date}_{arxiv_id}.pdf`, keep original arXiv ID | 2 | Todo | 4.2.1 |
| 4.5.5 | Create `BookRenamer`: pattern `{year}_{title}_{author}.{ext}`, extract from inner PDF metadata if archive | 3 | Todo | 4.3.1, 3.4.6 |
| 4.5.6 | Write tests for all category-specific renamers | 3 | Todo | 4.5.1-4.5.5 |

### 4.6 Register All Renamers

| ID | Task | Points | Status | Dependencies |
|----|------|--------|--------|--------------|
| 4.6.1 | Update `renamers/__init__.py` to register: Invoice→InvoiceRenamer, Screenshot→ScreenshotRenamer, Arxiv→ArxivRenamer, Book→BookRenamer, Document→PDFRenamer, Image→ImageRenamer, default→GenericRenamer | 2 | Todo | 4.5.6 |
| 4.6.2 | Write integration test: pass files through detection → renaming pipeline | 3 | Todo | 4.6.1 |

**Phase 4 Acceptance Criteria:**
- [ ] PDF titles extracted from metadata when available
- [ ] Fallback to text extraction when no PDF metadata
- [ ] EXIF dates extracted from images
- [ ] All dates formatted as ISO 8601 (`YYYY-MM-DD`)
- [ ] Filenames properly sanitized (no special chars, reasonable length)
- [ ] Invoice pattern: `{date}_Invoice_{vendor}.pdf`
- [ ] Screenshot pattern: `Screenshot_{date}_{time}.png`
- [ ] arXiv pattern: `{date}_{arxiv_id}.pdf`
- [ ] Book pattern: `{year}_{title}_{author}.ext`
- [ ] All renamer tests pass

---

## Phase 5: Safety & Polish

### 5.1 Dry Run Mode

| ID | Task | Points | Status | Dependencies |
|----|------|--------|--------|--------------|
| 5.1.1 | Create `src/tidy/output.py` with `DryRunFormatter` class | 2 | Todo | 2.6.9 |
| 5.1.2 | Implement `format_action(action: Action) -> str`: show `{filename} → {dest_folder}/{new_name}` | 2 | Todo | 5.1.1 |
| 5.1.3 | Implement pagination: show 10 actions per page, prompt "Press Enter for next page, q to quit" | 3 | Todo | 5.1.2 |
| 5.1.4 | Implement summary: show counts for each category (Documents: 15, Images: 23, Unsorted: 3) | 2 | Todo | 5.1.2 |
| 5.1.5 | Add color coding: green for confident, yellow for uncertain, red for errors | 2 | Todo | 5.1.2 |
| 5.1.6 | Write dry run output tests | 2 | Todo | 5.1.1-5.1.5 |

### 5.2 Interactive Mode

| ID | Task | Points | Status | Dependencies |
|----|------|--------|--------|--------------|
| 5.2.1 | Create `src/tidy/interactive.py` with `InteractivePrompt` class | 2 | Todo | - |
| 5.2.2 | Implement prompt for uncertain files: show file, proposed category, confidence, ask `[Y/n/skip/custom]` | 3 | Todo | 5.2.1 |
| 5.2.3 | Handle `Y` (accept), `n` (reject, move to Unsorted), `skip` (leave in source), `custom` (show category menu) | 2 | Todo | 5.2.2 |
| 5.2.4 | Implement custom category selection: numbered list of available folders | 2 | Todo | 5.2.3 |
| 5.2.5 | Integrate with engine: call prompt when confidence < 0.7 and `--interactive` flag set | 2 | Todo | 5.2.4, 2.6.3 |
| 5.2.6 | Write interactive mode tests with mocked input | 3 | Todo | 5.2.1-5.2.5 |

### 5.3 Configuration

| ID | Task | Points | Status | Dependencies |
|----|------|--------|--------|--------------|
| 5.3.1 | Create `src/tidy/config.py` with `Config` dataclass matching REQUIREMENTS YAML structure | 2 | Todo | - |
| 5.3.2 | Define default config values: destination=`~/Documents/Organized`, confidence_threshold=0.7, skip_recent_hours=1 | 1 | Todo | 5.3.1 |
| 5.3.3 | Define default folder list with prefixes and extensions (10 folders from 00 to 99) | 2 | Todo | 5.3.1 |
| 5.3.4 | Implement `load_config(path: Path = None) -> Config`: load from `~/.tidy/config.yaml` or default | 3 | Todo | 5.3.1 |
| 5.3.5 | Implement config validation: check paths exist, prefixes are valid, required fields present | 2 | Todo | 5.3.4 |
| 5.3.6 | Implement `ensure_config() -> Path`: create default config on first run if not exists | 2 | Todo | 5.3.4 |
| 5.3.7 | Integrate config with CLI: load config before running engine | 2 | Todo | 5.3.6 |
| 5.3.8 | Write config tests | 2 | Todo | 5.3.1-5.3.7 |

### 5.4 Rich Output

| ID | Task | Points | Status | Dependencies |
|----|------|--------|--------|--------------|
| 5.4.1 | Add progress bar using Rich: `Processing files... [####------] 40%` | 2 | Todo | 2.6.3 |
| 5.4.2 | Add colored status messages: `[green]✓ Moved report.pdf → 01_Documents/` | 2 | Todo | 2.6.3 |
| 5.4.3 | Add Rich table for run summary: columns for Category, Count, Size | 2 | Todo | 5.1.4 |
| 5.4.4 | Implement `--verbose` output: show all details including confidence scores, renamer used | 2 | Todo | 2.6.10 |
| 5.4.5 | Add error formatting: `[red]✗ Error: {message}` | 1 | Todo | 5.4.2 |

### 5.5 Status Command

| ID | Task | Points | Status | Dependencies |
|----|------|--------|--------|--------------|
| 5.5.1 | Implement destination folder scanning: list all numbered folders, count files, sum sizes | 3 | Todo | 2.5.6 |
| 5.5.2 | Format as Rich table: Folder, Files, Size columns with totals row | 2 | Todo | 5.5.1 |
| 5.5.3 | Show config and log paths: `Config: ~/.tidy/config.yaml`, `Logs: ~/.tidy/logs/ (23 files)` | 1 | Todo | 5.5.1 |
| 5.5.4 | Show last run summary: read most recent log, display "Last Run: {date} → Moved {n}, renamed {n}, skipped {n}" | 2 | Todo | 2.5.6 |
| 5.5.5 | Show recent activity: aggregate last 7 days from logs, show total processed and unsorted | 2 | Todo | 2.5.7 |
| 5.5.6 | Wire to CLI: replace status stub with full implementation | 1 | Todo | 5.5.5 |
| 5.5.7 | Write status command tests | 2 | Todo | 5.5.1-5.5.6 |

### 5.6 Reindex Command

| ID | Task | Points | Status | Dependencies |
|----|------|--------|--------|--------------|
| 5.6.1 | Implement `list_destination_folders(dest: Path) -> list[tuple[str, str]]`: return list of (prefix, name) for existing folders | 2 | Todo | - |
| 5.6.2 | Display current structure with Rich: `01_Documents/`, `02_Images/`, etc. | 1 | Todo | 5.6.1 |
| 5.6.3 | Implement menu: `1. Insert new folder`, `2. Remove empty folder`, `3. Renumber all`, `4. Cancel` | 2 | Todo | 5.6.2 |
| 5.6.4 | Insert folder: prompt for name and position, shift subsequent folders up | 3 | Todo | 5.6.3 |
| 5.6.5 | Remove folder: only allow if empty, shift subsequent folders down | 2 | Todo | 5.6.3 |
| 5.6.6 | Renumber all: remove gaps in numbering, reassign sequential prefixes | 2 | Todo | 5.6.3 |
| 5.6.7 | Preview changes before applying: show before/after, prompt "Apply changes? [y/N]" | 2 | Todo | 5.6.4-5.6.6 |
| 5.6.8 | Perform actual folder renames using `os.rename()` | 2 | Todo | 5.6.7 |
| 5.6.9 | Wire to CLI: replace reindex stub | 1 | Todo | 5.6.8 |
| 5.6.10 | Write reindex tests with temp directories | 3 | Todo | 5.6.1-5.6.9 |

### 5.7 Unsorted Suggestions

| ID | Task | Points | Status | Dependencies |
|----|------|--------|--------|--------------|
| 5.7.1 | After run, collect all files moved to Unsorted | 1 | Todo | 2.6.8 |
| 5.7.2 | Generate suggestion for each: analyze why unsorted (unknown extension, low confidence, no metadata) | 2 | Todo | 5.7.1 |
| 5.7.3 | Format output: `=== Moved to Unsorted (3 files) ===` with bullet list of file → reason | 2 | Todo | 5.7.2 |
| 5.7.4 | Integrate into run output: display after summary table | 1 | Todo | 5.7.3 |

**Phase 5 Acceptance Criteria:**
- [ ] `--dry-run` shows paginated preview with color coding
- [ ] `--interactive` prompts for uncertain files with Y/n/skip/custom options
- [ ] Config loads from `~/.tidy/config.yaml` or uses defaults
- [ ] First run creates default config if not exists
- [ ] Progress bar shows during processing
- [ ] Rich table shows run summary
- [ ] `tidy status` shows folder stats, last run, recent activity
- [ ] `tidy reindex` allows inserting/removing/renumbering folders
- [ ] Unsorted files get suggestions printed after run
- [ ] All tests pass

---

## Phase 6: Quality & Release

### 6.1 Code Quality

| ID | Task | Points | Status | Dependencies |
|----|------|--------|--------|--------------|
| 6.1.1 | Run `ruff check src/` and fix all linting issues | 2 | Todo | All |
| 6.1.2 | Run `ruff format src/` to ensure consistent formatting | 1 | Todo | 6.1.1 |
| 6.1.3 | Add type hints to all public functions and methods | 3 | Todo | All |
| 6.1.4 | Run `mypy src/` and fix all type errors | 3 | Todo | 6.1.3 |
| 6.1.5 | Add docstrings to all modules (module-level), classes, and public methods | 3 | Todo | All |

### 6.2 Testing

| ID | Task | Points | Status | Dependencies |
|----|------|--------|--------|--------------|
| 6.2.1 | Set up pytest-cov: add to dev dependencies, configure in pyproject.toml | 1 | Todo | - |
| 6.2.2 | Run coverage report, identify gaps below 80% | 2 | Todo | 6.2.1 |
| 6.2.3 | Add missing unit tests to achieve 80% coverage | 5 | Todo | 6.2.2 |
| 6.2.4 | Create `tests/fixtures/` with sample files: PDFs, images, archives, invoices | 3 | Todo | - |
| 6.2.5 | Add end-to-end integration test: create realistic Downloads folder, run tidy, verify results | 5 | Todo | 6.2.4 |

### 6.3 Documentation

| ID | Task | Points | Status | Dependencies |
|----|------|--------|--------|--------------|
| 6.3.1 | Update README.md with final CLI usage, all flags, examples | 2 | Todo | All |
| 6.3.2 | Add installation section: pip install, pipx install, from source | 1 | Todo | 6.3.1 |
| 6.3.3 | Add configuration section explaining config.yaml options | 2 | Todo | 6.3.1 |
| 6.3.4 | Create CHANGELOG.md with v0.1.0 release notes | 1 | Todo | All |

### 6.4 Release

| ID | Task | Points | Status | Dependencies |
|----|------|--------|--------|--------------|
| 6.4.1 | Test `pip install -e .` in fresh virtual environment | 1 | Todo | All |
| 6.4.2 | Test `pipx install .` for global installation | 1 | Todo | 6.4.1 |
| 6.4.3 | Verify `tidy --help`, `tidy status`, `tidy ~/Downloads --dry-run` work after install | 1 | Todo | 6.4.2 |
| 6.4.4 | Create git tag `v0.1.0` | 1 | Todo | 6.4.3 |
| 6.4.5 | Push to GitHub (if desired) | 1 | Todo | 6.4.4 |

**Phase 6 Acceptance Criteria:**
- [ ] `ruff check` passes with no errors
- [ ] `mypy` passes with no errors
- [ ] Test coverage ≥ 80%
- [ ] README is complete and accurate
- [ ] Can install globally via `pipx install .`
- [ ] All commands work after fresh install

---

## Summary

| Phase | Tasks | Story Points | Status |
|-------|-------|--------------|--------|
| 1. Scaffolding | 20 | 24 | Mostly Done |
| 2. Core Engine | 35 | 78 | Todo |
| 3. Detectors | 23 | 54 | Todo |
| 4. Renamers | 23 | 52 | Todo |
| 5. Safety & Polish | 41 | 71 | Todo |
| 6. Quality & Release | 17 | 34 | Todo |
| **Total** | **159** | **313** | |

---

## Future Enhancements (Icebox)

Not scheduled for v1.0:

- [ ] **Watch mode**: Monitor Downloads folder, auto-organize new files (fswatch/watchdog) - 13 pts
- [ ] **Custom plugins**: Load detector/renamer plugins from `~/.tidy/plugins/` - 8 pts
- [ ] **Duplicate finder**: Scan destination for duplicates, offer to consolidate - 5 pts
- [ ] **Undo command**: Read from logs, reverse most recent run - 8 pts
- [ ] **GUI wrapper**: Simple Electron or native macOS app - 13 pts
- [ ] **Cloud sync**: Integrate with Dropbox/GDrive for backup - 8 pts
