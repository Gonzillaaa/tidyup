# TidyUp Manual Testing Guide

This guide provides commands for manually testing TidyUp functionality. All tests use temporary directories and won't affect your real files.

## Quick Start: Automated Test Suite

Run the full automated test suite:

```bash
./scripts/manual_test.sh
```

This creates test files, runs all tests interactively, and offers cleanup at the end.

---

## Individual Test Commands

### Setup Test Environment

Create a temporary test environment:

```bash
# Create test directories
export TEST_DIR="/tmp/tidyup_test"
mkdir -p "$TEST_DIR/source" "$TEST_DIR/dest"
cd "$TEST_DIR/source"
```

### Create Test Files

```bash
# Screenshots (various patterns)
touch "Screen Shot 2024-01-15 at 10.30.45 AM.png"
touch "Screenshot 2024-02-20 142533.png"
touch "CleanShot 2024-03-10 at 09.15.22.png"
touch "Bildschirmfoto 2024-04-05 um 16.45.30.png"

# Images
touch "IMG_1234.jpg"
touch "vacation_photo.heic"
touch "profile.png"

# Documents
touch "document.pdf"
touch "report_final.pdf"
touch "meeting_notes.txt"

# arXiv papers
touch "2401.05712v2.pdf"
touch "1905.13325.pdf"

# Books
touch "Python_Crash_Course.epub"
touch "clean_code.mobi"

# Book archives (with keywords - should detect as Books)
touch "Python Programming Guide 3rd Edition.rar"
touch "Head First Java Complete Handbook.7z"
touch "Tableau Certified Data Analyst Study Guide.rar"

# Regular archives (should NOT detect as Books)
touch "project_backup_2024.rar"
touch "website_files.7z"

# Create ZIP with book inside
mkdir -p temp && echo "fake" > temp/book.epub
zip -q "ebooks.zip" -r temp && rm -rf temp

# Code files
echo 'print("hello")' > hello.py
echo 'console.log("hi")' > app.js
touch "styles.css"

# Data files
echo "name,age" > data.csv
echo "{}" > config.json

# Media
touch "podcast.mp3"
touch "video.mp4"

# Installers
touch "App.dmg"
touch "setup.exe"

# Edge cases
touch "file with spaces.txt"
touch "UPPERCASE.PDF"
touch "a1b2c3d4e5f6.pdf"
```

---

## Test Commands

### 1. Help and Version

```bash
# Show help
tidyup --help

# Show version
tidyup --version

# Show run command help
tidyup run --help

# Show categories help
tidyup categories --help
```

### 2. Dry Run (Preview Changes)

```bash
# Preview what would happen
tidyup "$TEST_DIR/source" "$TEST_DIR/dest" --dry-run

# Dry run with verbose output
tidyup "$TEST_DIR/source" "$TEST_DIR/dest" --dry-run --verbose

# Dry run with limit
tidyup "$TEST_DIR/source" "$TEST_DIR/dest" --dry-run --limit 5 --verbose
```

### 3. Move Only (Keep Original Names)

```bash
# Move files without renaming
tidyup "$TEST_DIR/source" "$TEST_DIR/dest" --move --verbose
```

### 4. Rename Only (Keep in Place)

```bash
# Rename files without moving
tidyup "$TEST_DIR/source" --rename --verbose
```

### 5. Skip Uncertain Files

```bash
# Skip files with low confidence
tidyup "$TEST_DIR/source" "$TEST_DIR/dest" --dry-run --skip --verbose
```

### 6. Full Organization (Move + Rename)

```bash
# Default mode: categorize, rename, and move
tidyup "$TEST_DIR/source" "$TEST_DIR/dest" --verbose
```

### 7. Limit Processing

```bash
# Only process first N files
tidyup "$TEST_DIR/source" "$TEST_DIR/dest" --dry-run --limit 3 --verbose
```

---

## Category Management

### List Categories

```bash
# Default: list all categories
tidyup categories

# Explicit list command
tidyup categories list
```

### Add Category

```bash
# Add at end
tidyup categories add TestCategory

# Add at specific position
tidyup categories add Music --position 5
```

### Remove Category

```bash
tidyup categories remove TestCategory
```

### Apply to Filesystem

```bash
# Create test folders
mkdir -p "$TEST_DIR/dest/01_Documents"
mkdir -p "$TEST_DIR/dest/03_Images"

# Preview folder renames
tidyup categories apply "$TEST_DIR/dest" --dry-run

# Actually rename folders
tidyup categories apply "$TEST_DIR/dest"
```

---

## Status Command

```bash
tidyup status
```

---

## Verification Commands

### Check Results

```bash
# List organized files
find "$TEST_DIR/dest" -type f | sort

# Show folder structure
tree "$TEST_DIR/dest" 2>/dev/null || find "$TEST_DIR/dest" -type d | sort

# Check what's left in source
ls -la "$TEST_DIR/source"
```

### Check Logs

```bash
# List log files
ls -la ~/.tidy/logs/

# View most recent log
cat ~/.tidy/logs/$(ls -t ~/.tidy/logs/ | head -1) | python -m json.tool
```

---

## Test Scenarios

### Scenario 1: Screenshot Organization

```bash
cd "$TEST_DIR/source"
touch "Screen Shot 2024-01-15 at 10.30.45 AM.png"
touch "Screenshot 2024-02-20 142533.png"

tidyup "$TEST_DIR/source" "$TEST_DIR/dest" --verbose

# Expected: Files moved to 02_Screenshots with standardized names
ls "$TEST_DIR/dest/02_Screenshots/"
```

### Scenario 2: Book Archive Detection

```bash
cd "$TEST_DIR/source"
touch "Python Programming Guide 3rd Edition.rar"
touch "project_backup_2024.rar"

tidyup "$TEST_DIR/source" "$TEST_DIR/dest" --dry-run --verbose

# Expected:
# - "Python Programming Guide 3rd Edition.rar" -> 08_Books (detected by keywords)
# - "project_backup_2024.rar" -> 06_Archives (no book keywords)
```

### Scenario 3: arXiv Paper Detection

```bash
cd "$TEST_DIR/source"
touch "2401.05712v2.pdf"

tidyup "$TEST_DIR/source" "$TEST_DIR/dest" --verbose

# Expected: File moved to 09_Papers with date prefix
ls "$TEST_DIR/dest/09_Papers/"
```

### Scenario 4: Duplicate Handling

```bash
cd "$TEST_DIR/source"
echo "same content" > file1.txt
echo "same content" > file2.txt

tidyup "$TEST_DIR/source" "$TEST_DIR/dest" --verbose

# Expected: One file in destination, duplicate in 99_Unsorted/_duplicates
find "$TEST_DIR/dest" -name "*.txt"
```

---

## Cleanup

```bash
# Remove test environment
rm -rf "$TEST_DIR"

# Or keep for inspection
echo "Test files at: $TEST_DIR"
```

---

## Troubleshooting Tests

### Test Permission Errors

```bash
# Create unreadable file
touch "$TEST_DIR/source/secret.txt"
chmod 000 "$TEST_DIR/source/secret.txt"

tidyup "$TEST_DIR/source" "$TEST_DIR/dest" --verbose

# Cleanup
chmod 644 "$TEST_DIR/source/secret.txt"
```

### Test Empty Directory

```bash
mkdir -p "$TEST_DIR/empty"
tidyup "$TEST_DIR/empty" "$TEST_DIR/dest" --verbose
```

### Test Files That Should Be Skipped

```bash
cd "$TEST_DIR/source"
touch ".hidden_file"
touch ".DS_Store"
touch "download.crdownload"
touch "temp.tmp"

tidyup "$TEST_DIR/source" "$TEST_DIR/dest" --dry-run --verbose

# Expected: These files should be skipped
```

---

## Quick Reset

Start fresh between tests:

```bash
rm -rf "$TEST_DIR"
mkdir -p "$TEST_DIR/source" "$TEST_DIR/dest"
cd "$TEST_DIR/source"
```
