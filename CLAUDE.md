# Claude Code Directives for TidyUp

## CRITICAL: Commit After Each Unit of Work

**Make atomic git commits as you work, not at the end.** After implementing each logical unit (a new class, a detector, a feature) and tests pass, commit immediately. Do not batch changes.

## CRITICAL: Maintain the Backlog

**Keep BACKLOG.md current as you work.** Mark tasks complete when done, add new tasks as they emerge, and update estimates based on learnings. The backlog should always reflect the true state of the project.

## CRITICAL: Keep Documentation Current

**Update documentation as you implement features, not at the end.** When adding new functionality (commands, detectors, options), immediately update the relevant docs (README, BACKLOG, etc.). Documentation should never lag behind implementation.

## CRITICAL: Documentation Principles

Documentation must be:
- **Accurate**: Reflects actual implementation, no "coming soon" for shipped features
- **Consistent**: Use "TidyUp" (not "Tidy") everywhere, consistent terminology
- **Concise**: Clear and helpful without unnecessary verbosity
- **Current**: Updated immediately when features change, not as an afterthought

## Project Overview

TidyUp is a CLI tool for organizing, renaming, and categorizing files. It uses a plugin architecture for file detection and renaming.

## Key Documentation

- **User Guide**: `docs/USER_GUIDE.md` - CLI reference, categories, troubleshooting
- **Development**: `docs/DEVELOPMENT.md` - Setup, testing, adding detectors/renamers
- **Requirements**: `docs/REQUIREMENTS.md` - Full specification
- **Backlog**: `docs/BACKLOG.md` - Implementation tasks with story points

## Code Standards

### Python Style

- Python 3.10+ with type hints on all public functions
- Use `pathlib.Path` for all file operations (not `os.path`)
- Use dataclasses for data structures
- Follow PEP 8, enforced by `ruff`
- Maximum line length: 100 characters

### Naming Conventions

- Classes: `PascalCase` (e.g., `FileInfo`, `InvoiceDetector`)
- Functions/methods: `snake_case` (e.g., `detect_category`, `extract_title`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `CONFIDENCE_HIGH`)
- Private methods: prefix with `_` (e.g., `_parse_metadata`)

### File Organization

```
src/tidyup/
├── cli.py          # Entry point, Click commands
├── engine.py       # Main orchestration
├── config.py       # Configuration loading
├── models.py       # Dataclasses (FileInfo, Action, etc.)
├── utils.py        # Utility functions
├── operations.py   # File move/rename operations
├── discovery.py    # File discovery and filtering
├── logger.py       # Action logging
├── content.py      # PDF/archive content extraction
├── output.py       # Rich output formatting
├── interactive.py  # Interactive prompts
├── detectors/      # File type detectors (plugin architecture)
└── renamers/       # File renamers (plugin architecture)
```

### Testing

- Every new module must have corresponding tests in `tests/`
- Use pytest fixtures for common test data
- Use `tmp_path` fixture for file operations (no real filesystem pollution)
- Mock external dependencies (file system in unit tests)
- Target 80% code coverage

### Error Handling

- Never delete files (core safety principle)
- Handle file permission errors gracefully
- Log all errors to the action log
- Continue processing other files if one fails

## Development Workflow

### Before Implementing a Task

1. Read the task description in `docs/BACKLOG.md`
2. Check dependencies are complete
3. Review related code in requirements

### After Implementing

1. Run tests: `pytest tests/`
2. Run linter: `ruff check src/`
3. **Commit immediately** - Make a git commit as soon as a feature is implemented and tests pass
4. Update task status in `docs/BACKLOG.md`

### Git Workflow

- **Commit frequently**: Make small, atomic commits after each logical unit of work
- **Don't batch commits**: Commit as soon as tests pass, not at the end of a session
- **Each commit should**: Pass all tests, be self-contained, have a clear purpose

### Feature Branch Workflow

- **Always use feature branches** for new features and significant changes
- **Create Pull Requests** from feature branches to main
- **PRs require manual review** - never auto-merge or squash-merge without approval
- **Wait for approval** before merging any PR

### Commit Messages

- Use conventional commits: `feat:`, `fix:`, `test:`, `docs:`, `refactor:`
- Reference task ID when applicable: `feat: implement FileInfo dataclass (2.1.1)`

## Common Patterns

### Adding a New Detector

1. Create `src/tidy/detectors/{name}.py`
2. Inherit from `BaseDetector`
3. Implement `detect(file: FileInfo) -> DetectionResult | None`
4. Register in `detectors/__init__.py`
5. Add tests in `tests/test_detectors.py`

### Adding a New Renamer

1. Create `src/tidy/renamers/{name}.py`
2. Inherit from `BaseRenamer`
3. Implement `rename(file: FileInfo, detection: DetectionResult) -> RenameResult`
4. Register in `renamers/__init__.py`
5. Add tests in `tests/test_renamers.py`

## Dependencies

Core:

- `click` - CLI framework
- `rich` - Terminal output
- `pyyaml` - Config parsing
- `pypdf` - PDF metadata
- `pillow` - Image EXIF

Dev:

- `pytest` - Testing
- `pytest-cov` - Coverage
- `ruff` - Linting
- `mypy` - Type checking

## Quick Reference

```bash
# Install for development
pip install -e ".[dev]"

# Run CLI
tidyup ~/Downloads --dry-run

# Run tests
pytest

# Run linter
ruff check src/

# Run type checker
mypy src/
```
