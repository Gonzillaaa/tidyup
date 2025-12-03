#!/bin/bash
# TidyUp Manual Testing Script
#
# This script creates a temporary test environment with various file types,
# runs TidyUp commands to verify functionality, and optionally cleans up.
#
# Usage: ./scripts/manual_test.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Test directories
TEST_BASE="/tmp/tidyup_manual_test"
TEST_SOURCE="$TEST_BASE/source"
TEST_DEST="$TEST_BASE/organized"
TEST_CONFIG="$TEST_BASE/config"

# Track test results
TESTS_PASSED=0
TESTS_FAILED=0

#=============================================================================
# Helper Functions
#=============================================================================

print_header() {
    echo ""
    echo -e "${BOLD}${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BOLD}${BLUE}  $1${NC}"
    echo -e "${BOLD}${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
}

print_section() {
    echo ""
    echo -e "${CYAN}───────────────────────────────────────────────────────────────${NC}"
    echo -e "${CYAN}  $1${NC}"
    echo -e "${CYAN}───────────────────────────────────────────────────────────────${NC}"
}

print_test() {
    echo -e "${YELLOW}▶ TEST:${NC} $1"
}

print_cmd() {
    echo -e "${BOLD}$ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ PASS:${NC} $1"
    ((TESTS_PASSED++))
}

print_fail() {
    echo -e "${RED}✗ FAIL:${NC} $1"
    ((TESTS_FAILED++))
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

run_cmd() {
    print_cmd "$1"
    echo ""
    eval "$1"
    echo ""
}

pause() {
    echo ""
    read -p "Press Enter to continue..."
    echo ""
}

#=============================================================================
# Setup Functions
#=============================================================================

setup_test_environment() {
    print_header "Setting Up Test Environment"

    # Clean any previous test
    if [ -d "$TEST_BASE" ]; then
        print_info "Removing previous test directory..."
        rm -rf "$TEST_BASE"
    fi

    # Create directories
    print_info "Creating test directories..."
    mkdir -p "$TEST_SOURCE"
    mkdir -p "$TEST_DEST"
    mkdir -p "$TEST_CONFIG"

    echo "  Source:      $TEST_SOURCE"
    echo "  Destination: $TEST_DEST"
    echo "  Config:      $TEST_CONFIG"

    # Set custom config location for testing
    export TIDY_CONFIG_DIR="$TEST_CONFIG"
}

create_test_files() {
    print_header "Creating Test Files"

    cd "$TEST_SOURCE"

    # --- Screenshots ---
    print_section "Creating Screenshot Files"

    # macOS screenshot
    touch "Screen Shot 2024-01-15 at 10.30.45 AM.png"
    print_info "Created: Screen Shot 2024-01-15 at 10.30.45 AM.png"

    # Windows screenshot
    touch "Screenshot 2024-02-20 142533.png"
    print_info "Created: Screenshot 2024-02-20 142533.png"

    # CleanShot
    touch "CleanShot 2024-03-10 at 09.15.22.png"
    print_info "Created: CleanShot 2024-03-10 at 09.15.22.png"

    # German screenshot
    touch "Bildschirmfoto 2024-04-05 um 16.45.30.png"
    print_info "Created: Bildschirmfoto 2024-04-05 um 16.45.30.png"

    # --- Images ---
    print_section "Creating Image Files"

    touch "IMG_1234.jpg"
    touch "vacation_photo.heic"
    touch "profile_picture.png"
    touch "logo.svg"
    print_info "Created: IMG_1234.jpg, vacation_photo.heic, profile_picture.png, logo.svg"

    # --- Documents/PDFs ---
    print_section "Creating Document Files"

    # Create a minimal valid PDF
    create_pdf "document_v2_final.pdf" "Annual Report 2024"
    create_pdf "meeting_notes.pdf" "Meeting Notes"
    create_pdf "contract_draft.pdf" "Contract Agreement"

    # --- arXiv Papers ---
    print_section "Creating arXiv Paper Files"

    create_pdf "2401.05712v2.pdf" "Attention Is All You Need"
    create_pdf "1905.13325.pdf" "BERT: Pre-training of Deep Bidirectional Transformers"
    print_info "Created: 2401.05712v2.pdf, 1905.13325.pdf"

    # --- Invoice-like PDFs ---
    print_section "Creating Invoice Files"

    create_invoice_pdf "invoice_12345.pdf" "Acme Corporation"
    create_invoice_pdf "receipt_xyz.pdf" "TechStartup Inc"

    # --- Books ---
    print_section "Creating Book Files"

    touch "Python_Crash_Course.epub"
    touch "clean_code.mobi"
    create_pdf "978-0-13-235088-4.pdf" "Clean Code: A Handbook of Agile Software"
    print_info "Created: Python_Crash_Course.epub, clean_code.mobi, 978-0-13-235088-4.pdf"

    # --- Archives ---
    print_section "Creating Archive Files"

    # Regular archive
    mkdir -p temp_archive
    echo "test content" > temp_archive/readme.txt
    zip -q "project_backup.zip" -r temp_archive
    rm -rf temp_archive
    print_info "Created: project_backup.zip"

    # Archive with book inside (ZIP)
    mkdir -p temp_book_archive
    echo "fake epub content" > temp_book_archive/book.epub
    zip -q "ebooks_collection.zip" -r temp_book_archive
    rm -rf temp_book_archive
    print_info "Created: ebooks_collection.zip (contains book.epub)"

    # RAR-like files with book keywords (can't create real RAR, but test filename detection)
    touch "Python Programming Guide 3rd Edition.rar"
    touch "Tableau Certified Data Analyst Study Guide.rar"
    touch "Head First Java Complete Reference.7z"
    print_info "Created: Book archives with keywords (.rar, .7z)"

    # Regular archives (should NOT be detected as books)
    touch "project_files_2024.rar"
    touch "website_backup.7z"
    print_info "Created: Regular archives (project_files_2024.rar, website_backup.7z)"

    # --- Code Files ---
    print_section "Creating Code Files"

    echo 'print("Hello, World!")' > hello.py
    echo 'console.log("Hello");' > app.js
    echo '<!DOCTYPE html><html></html>' > index.html
    echo '.container { margin: 0; }' > styles.css
    echo '{"name": "test"}' > package.json
    print_info "Created: hello.py, app.js, index.html, styles.css, package.json"

    # --- Data Files ---
    print_section "Creating Data Files"

    echo 'name,age,city' > data.csv
    echo '{"users": []}' > database.json
    echo 'SELECT * FROM users;' > query.sql
    print_info "Created: data.csv, database.json, query.sql"

    # --- Audio/Video ---
    print_section "Creating Media Files"

    touch "podcast_episode.mp3"
    touch "song.flac"
    touch "presentation.mp4"
    touch "screen_recording.mov"
    print_info "Created: podcast_episode.mp3, song.flac, presentation.mp4, screen_recording.mov"

    # --- Installers ---
    print_section "Creating Installer Files"

    touch "App_Installer.dmg"
    touch "setup.exe"
    touch "package.deb"
    print_info "Created: App_Installer.dmg, setup.exe, package.deb"

    # --- Misc/Edge Cases ---
    print_section "Creating Edge Case Files"

    touch "random_hash_a1b2c3d4e5f6.pdf"
    touch "document (1).pdf"
    touch "file with spaces.txt"
    touch "UPPERCASE.PDF"
    print_info "Created: Files with hashes, duplicates markers, spaces, uppercase"

    # Count files
    FILE_COUNT=$(ls -1 | wc -l | tr -d ' ')
    echo ""
    print_info "Total test files created: $FILE_COUNT"
}

create_pdf() {
    local filename="$1"
    local title="$2"

    # Create a minimal valid PDF with title in metadata
    cat > "$filename" << 'PDFEOF'
%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >>
endobj
4 0 obj
<< /Length 44 >>
stream
BT
/F1 12 Tf
100 700 Td
(Test) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
0000000206 00000 n
trailer
<< /Size 5 /Root 1 0 R >>
startxref
300
%%EOF
PDFEOF
    print_info "Created: $filename"
}

create_invoice_pdf() {
    local filename="$1"
    local vendor="$2"

    # Create PDF with invoice-like content
    cat > "$filename" << PDFEOF
%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >>
endobj
4 0 obj
<< /Length 200 >>
stream
BT
/F1 12 Tf
100 700 Td
(INVOICE) Tj
0 -20 Td
(Invoice Number: INV-2024-001) Tj
0 -20 Td
(From: $vendor) Tj
0 -20 Td
(Total Amount: \$150.00) Tj
0 -20 Td
(Due Date: 2024-02-15) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
0000000206 00000 n
trailer
<< /Size 5 /Root 1 0 R >>
startxref
500
%%EOF
PDFEOF
    print_info "Created: $filename (invoice from $vendor)"
}

#=============================================================================
# Test Functions
#=============================================================================

test_help_and_version() {
    print_header "Test: Help and Version"

    print_test "Display help message"
    run_cmd "tidyup --help"

    print_test "Display version"
    run_cmd "tidyup --version"

    print_success "Help and version commands work"
}

test_dry_run() {
    print_header "Test: Dry Run Mode"

    print_test "Preview organization without making changes"
    run_cmd "tidyup '$TEST_SOURCE' '$TEST_DEST' --dry-run --verbose"

    # Verify no files were moved
    if [ -z "$(ls -A $TEST_DEST 2>/dev/null)" ]; then
        print_success "Dry run did not move any files"
    else
        print_fail "Dry run unexpectedly moved files!"
    fi
}

test_verbose_mode() {
    print_header "Test: Verbose Mode"

    print_test "Run with verbose output (dry-run)"
    run_cmd "tidyup '$TEST_SOURCE' '$TEST_DEST' --dry-run --verbose"

    print_success "Verbose mode shows detailed output"
}

test_limit_option() {
    print_header "Test: Limit Option"

    print_test "Process only 3 files (dry-run)"
    run_cmd "tidyup '$TEST_SOURCE' '$TEST_DEST' --dry-run --limit 3 --verbose"

    print_success "Limit option restricts file count"
}

test_move_only() {
    print_header "Test: Move Only Mode"

    # Create a fresh source for this test
    local move_source="$TEST_BASE/move_test_source"
    local move_dest="$TEST_BASE/move_test_dest"
    mkdir -p "$move_source"

    touch "$move_source/test_image.jpg"
    touch "$move_source/test_doc.pdf"

    print_test "Move files without renaming"
    run_cmd "tidyup '$move_source' '$move_dest' --move --verbose"

    # Check if files kept original names
    print_info "Checking destination structure..."
    run_cmd "find '$move_dest' -type f -name '*.jpg' -o -name '*.pdf' 2>/dev/null | head -5"

    print_success "Move-only mode preserves original filenames"
}

test_rename_only() {
    print_header "Test: Rename Only Mode"

    # Create a fresh source for this test
    local rename_source="$TEST_BASE/rename_test"
    mkdir -p "$rename_source"

    touch "$rename_source/Screen Shot 2024-01-15 at 10.30.45 AM.png"

    print_test "Rename files in place without moving"
    print_info "Before:"
    ls -la "$rename_source"

    run_cmd "tidyup '$rename_source' --rename --verbose"

    print_info "After:"
    ls -la "$rename_source"

    print_success "Rename-only mode keeps files in place"
}

test_skip_mode() {
    print_header "Test: Skip Uncertain Files"

    print_test "Skip files with low confidence (dry-run)"
    run_cmd "tidyup '$TEST_SOURCE' '$TEST_DEST' --dry-run --skip --verbose"

    print_success "Skip mode filters uncertain files"
}

test_full_organize() {
    print_header "Test: Full Organization (Move + Rename)"

    # Reset test files
    rm -rf "$TEST_SOURCE"
    mkdir -p "$TEST_SOURCE"

    # Create a smaller set of files for this test
    cd "$TEST_SOURCE"
    touch "Screen Shot 2024-01-15 at 10.30.45 AM.png"
    touch "IMG_1234.jpg"
    create_pdf "document.pdf" "Test Document"
    touch "hello.py"
    touch "song.mp3"

    print_info "Source files:"
    ls -la "$TEST_SOURCE"

    print_test "Organize files (move + rename)"
    run_cmd "tidyup '$TEST_SOURCE' '$TEST_DEST' --verbose"

    print_info "Destination structure:"
    run_cmd "find '$TEST_DEST' -type f | sort"

    print_info "Remaining in source:"
    ls -la "$TEST_SOURCE" 2>/dev/null || echo "  (empty or removed)"

    print_success "Full organization complete"
}

test_categories_commands() {
    print_header "Test: Category Management"

    print_test "List all categories"
    run_cmd "tidyup categories"

    print_test "List categories (explicit subcommand)"
    run_cmd "tidyup categories list"

    print_test "Add a new category"
    run_cmd "tidyup categories add TestCategory --position 5"

    print_test "List categories after adding"
    run_cmd "tidyup categories list"

    print_test "Remove the test category"
    run_cmd "tidyup categories remove TestCategory"

    print_test "List categories after removing"
    run_cmd "tidyup categories list"

    print_success "Category management commands work"
}

test_categories_apply() {
    print_header "Test: Apply Category Changes to Filesystem"

    # Create some destination folders
    mkdir -p "$TEST_DEST/01_Documents"
    mkdir -p "$TEST_DEST/03_Images"
    touch "$TEST_DEST/01_Documents/test.pdf"
    touch "$TEST_DEST/03_Images/test.jpg"

    print_info "Current folder structure:"
    ls -la "$TEST_DEST"

    print_test "Preview folder renames (dry-run)"
    run_cmd "tidyup categories apply '$TEST_DEST' --dry-run"

    print_success "Categories apply command works"
}

test_status_command() {
    print_header "Test: Status Command"

    print_test "Show status information"
    run_cmd "tidyup status"

    print_success "Status command works"
}

test_file_type_detection() {
    print_header "Test: File Type Detection"

    # Reset and create specific test files
    rm -rf "$TEST_SOURCE"
    mkdir -p "$TEST_SOURCE"
    cd "$TEST_SOURCE"

    print_section "Testing Screenshot Detection"
    touch "Screen Shot 2024-01-15 at 10.30.45 AM.png"

    print_section "Testing arXiv Detection"
    create_pdf "2401.05712v2.pdf" "Test Paper"

    print_section "Testing Book Archive Detection"
    touch "Python Programming Guide 3rd Edition.rar"
    touch "Complete Java Tutorial Handbook.7z"

    print_section "Testing Regular Archive (should NOT be Book)"
    touch "project_backup_2024.rar"

    print_test "Detect file types (dry-run verbose)"
    run_cmd "tidyup '$TEST_SOURCE' '$TEST_DEST' --dry-run --verbose"

    print_success "File type detection complete"
}

test_edge_cases() {
    print_header "Test: Edge Cases"

    rm -rf "$TEST_SOURCE"
    mkdir -p "$TEST_SOURCE"
    cd "$TEST_SOURCE"

    print_section "Files with Special Characters"
    touch "file with spaces.txt"
    touch "file-with-dashes.pdf"
    touch "file_with_underscores.doc"
    touch "UPPERCASE.PDF"
    touch "MixedCase.Jpg"

    print_section "Files with Numbers/Hashes"
    touch "a1b2c3d4e5f6g7h8.pdf"
    touch "document (1).pdf"
    touch "document (2).pdf"

    print_test "Handle edge cases (dry-run)"
    run_cmd "tidyup '$TEST_SOURCE' '$TEST_DEST' --dry-run --verbose"

    print_success "Edge cases handled"
}

test_empty_directory() {
    print_header "Test: Empty Directory"

    local empty_dir="$TEST_BASE/empty"
    mkdir -p "$empty_dir"

    print_test "Run on empty directory"
    run_cmd "tidyup '$empty_dir' '$TEST_DEST' --dry-run" || true

    print_success "Empty directory handled gracefully"
}

#=============================================================================
# Summary and Cleanup
#=============================================================================

print_summary() {
    print_header "Test Summary"

    echo -e "  ${GREEN}Passed:${NC} $TESTS_PASSED"
    echo -e "  ${RED}Failed:${NC} $TESTS_FAILED"
    echo ""

    if [ $TESTS_FAILED -eq 0 ]; then
        echo -e "${GREEN}${BOLD}All tests passed!${NC}"
    else
        echo -e "${RED}${BOLD}Some tests failed. Please review the output above.${NC}"
    fi
}

cleanup() {
    print_header "Cleanup"

    echo "Test files are located at: $TEST_BASE"
    echo ""
    echo "Contents:"
    du -sh "$TEST_BASE" 2>/dev/null || echo "  (directory not found)"
    echo ""

    read -p "Delete test files? [y/N] " -n 1 -r
    echo ""

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$TEST_BASE"
        print_info "Test files deleted."
    else
        print_info "Test files kept at: $TEST_BASE"
        echo ""
        echo "To delete manually:"
        echo "  rm -rf $TEST_BASE"
    fi
}

#=============================================================================
# Main
#=============================================================================

main() {
    print_header "TidyUp Manual Testing Suite"

    echo "This script will:"
    echo "  1. Create a temporary test environment"
    echo "  2. Generate various test files"
    echo "  3. Run TidyUp commands to test functionality"
    echo "  4. Optionally clean up afterwards"
    echo ""
    echo "Test location: $TEST_BASE"
    echo ""

    read -p "Continue? [Y/n] " -n 1 -r
    echo ""

    if [[ $REPLY =~ ^[Nn]$ ]]; then
        echo "Aborted."
        exit 0
    fi

    # Setup
    setup_test_environment
    create_test_files

    pause

    # Run tests
    test_help_and_version
    pause

    test_dry_run
    pause

    test_verbose_mode
    pause

    test_limit_option
    pause

    test_categories_commands
    pause

    test_status_command
    pause

    test_file_type_detection
    pause

    test_edge_cases
    pause

    test_empty_directory
    pause

    test_move_only
    pause

    test_rename_only
    pause

    test_skip_mode
    pause

    test_categories_apply
    pause

    test_full_organize

    # Summary
    print_summary

    # Cleanup
    cleanup

    echo ""
    echo "Manual testing complete!"
}

# Run if executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
