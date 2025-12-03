# TidyUp Development Guide

## Prerequisites

- Python 3.11+
- pip or pipx

## Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/tidyup.git
cd tidyup

# Install in development mode with dev dependencies
pip install -e ".[dev]"

# Verify installation
tidyup --version
```

## Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=tidyup

# Run specific test file
pytest tests/test_engine.py -v

# Run tests matching a pattern
pytest -k "dry_run" -v
```

## Linting & Type Checking

```bash
# Run linter
ruff check src/

# Run type checker
mypy src/
```

## Project Structure

```
tidyup/
├── src/tidyup/
│   ├── __init__.py      # Package metadata
│   ├── cli.py           # Click CLI interface
│   ├── engine.py        # Core orchestration logic
│   ├── config.py        # Configuration loading
│   ├── models.py        # Dataclasses (FileInfo, Action, etc.)
│   ├── utils.py         # Utility functions
│   ├── operations.py    # File move/rename operations
│   ├── discovery.py     # File discovery and filtering
│   ├── logger.py        # JSON logging system
│   ├── content.py       # PDF/archive content extraction
│   ├── output.py        # Rich output formatting
│   ├── categories.py    # Category management
│   ├── detectors/       # File type detectors (plugin architecture)
│   │   ├── base.py      # BaseDetector class
│   │   ├── generic.py   # Extension-based detection
│   │   ├── screenshot.py
│   │   ├── invoice.py
│   │   ├── book.py
│   │   ├── arxiv.py
│   │   ├── paper.py
│   │   ├── archive_book.py
│   │   └── installer.py
│   └── renamers/        # File renamers (plugin architecture)
│       ├── base.py      # BaseRenamer class
│       ├── generic.py   # Fallback renamer
│       ├── pdf.py
│       ├── image.py
│       ├── screenshot.py
│       ├── book.py
│       ├── invoice.py
│       └── arxiv.py
├── tests/               # Test suite (pytest)
├── docs/
│   ├── USER_GUIDE.md    # User documentation
│   ├── DEVELOPMENT.md   # This file
│   ├── REQUIREMENTS.md  # Full specification
│   └── BACKLOG.md       # Development tasks
└── README.md
```

## Adding a New Detector

Detectors analyze files and assign them to categories.

1. Create `src/tidyup/detectors/{name}.py`:

```python
from tidyup.detectors.base import BaseDetector, CONFIDENCE_HIGH, CONFIDENCE_MEDIUM
from tidyup.models import FileInfo, DetectionResult


class MyDetector(BaseDetector):
    """Detects my file type."""

    name = "MyDetector"
    priority = 15  # Lower = runs earlier (10-50 typical range)

    def detect(self, file: FileInfo) -> DetectionResult | None:
        # Return None to skip (let other detectors try)
        if not self._matches_my_criteria(file):
            return None

        return DetectionResult(
            category="MyCategory",  # Must exist in categories config
            confidence=CONFIDENCE_HIGH,
            detector_name=self.name,
            metadata={"key": "value"},  # Optional extra data
        )

    def _matches_my_criteria(self, file: FileInfo) -> bool:
        # Your detection logic here
        return file.extension == ".xyz"
```

2. Register in `src/tidyup/detectors/__init__.py`:

```python
from .my_detector import MyDetector

DETECTORS = [
    # ... existing detectors ...
    MyDetector(),
]
```

3. Add tests in `tests/test_detectors.py`

### Confidence Levels

- `CONFIDENCE_HIGH = 0.9` - Very certain (content-based match)
- `CONFIDENCE_MEDIUM = 0.7` - Reasonably sure (filename patterns)
- `CONFIDENCE_LOW = 0.5` - Uncertain (extension-only)

## Adding a New Renamer

Renamers generate new filenames based on file metadata.

1. Create `src/tidyup/renamers/{name}.py`:

```python
from tidyup.renamers.base import BaseRenamer
from tidyup.models import FileInfo, DetectionResult, RenameResult


class MyRenamer(BaseRenamer):
    """Renames my file type."""

    name = "MyRenamer"

    def rename(self, file: FileInfo, detection: DetectionResult) -> RenameResult | None:
        # Return None if you can't rename this file
        if file.extension != ".xyz":
            return None

        # Extract metadata and build new name
        new_name = f"{file.modified_date:%Y-%m-%d}_{self._extract_title(file)}.xyz"

        # Return None if name wouldn't change
        if new_name == file.name:
            return None

        return RenameResult(
            new_name=new_name,
            renamer_name=self.name,
        )

    def _extract_title(self, file: FileInfo) -> str:
        # Your metadata extraction logic
        return "extracted_title"
```

2. Register in `src/tidyup/renamers/__init__.py`:

```python
from .my_renamer import MyRenamer

# Map detector names to renamers
RENAMER_MAP = {
    # ... existing mappings ...
    "MyDetector": MyRenamer(),
}
```

3. Add tests in `tests/test_renamers.py`

## Configuration Files

### User Config: `~/.tidy/config.yaml`

```yaml
categories:
  - Documents
  - Screenshots
  - Images
  # ... order determines folder numbers (01, 02, 03...)
```

### Log Files: `~/.tidy/logs/`

Each run creates a JSON log:

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
      "from": "/path/from",
      "to": "/path/to",
      "category": "01_Documents",
      "confidence": 0.9,
      "status": "success"
    }
  ],
  "summary": {
    "processed": 10,
    "moved": 8,
    "renamed": 5,
    "skipped": 0,
    "errors": 0
  }
}
```

## Code Standards

- Python 3.10+ with type hints on all public functions
- Use `pathlib.Path` for file operations (not `os.path`)
- Use dataclasses for data structures
- Follow PEP 8, enforced by `ruff`
- Maximum line length: 100 characters

### Naming Conventions

- Classes: `PascalCase` (e.g., `FileInfo`, `InvoiceDetector`)
- Functions/methods: `snake_case` (e.g., `detect_category`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `CONFIDENCE_HIGH`)
- Private methods: prefix with `_` (e.g., `_parse_metadata`)

## Dependencies

**Core:**
- `click` - CLI framework
- `rich` - Terminal output
- `pyyaml` - Config parsing
- `pypdf` - PDF metadata
- `pillow` - Image EXIF

**Dev:**
- `pytest` - Testing
- `pytest-cov` - Coverage
- `ruff` - Linting
- `mypy` - Type checking

## Contributing

1. Check `docs/BACKLOG.md` for open tasks
2. Create a feature branch
3. Write tests for new functionality
4. Run `pytest` and `ruff check src/`
5. Submit a pull request

See `docs/REQUIREMENTS.md` for the full specification.
