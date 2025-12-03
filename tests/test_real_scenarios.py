"""Real-world scenario tests for Phase 7 features.

Tests with realistic file collections that mimic actual Downloads folders.
"""

import pytest
from pathlib import Path
from unittest.mock import patch

from tidyup.engine import Engine
from tidyup.categories import CategoryManager
from tidyup.rules import CategoryRule


@pytest.fixture
def isolated_manager(tmp_path: Path) -> CategoryManager:
    """Create an isolated CategoryManager for testing with default categories."""
    config_path = tmp_path / "config.yaml"
    manager = CategoryManager(config_path=config_path)
    manager.load()  # Load default categories
    return manager


class TestFreelancerDownloads:
    """Test scenarios typical for freelancers: invoices, contracts, client files."""

    def test_client_invoice_organization(self, tmp_path: Path, isolated_manager: CategoryManager) -> None:
        """Invoices from multiple clients can be organized with keyword rules."""
        source = tmp_path / "source"
        source.mkdir()
        dest = tmp_path / "dest"

        # Create realistic invoice files with client keywords in content
        files = [
            ("acme_invoice_2024-01.pdf", b"%PDF-1.4\nInvoice for Acme Corp\nAmount: $5000"),
            ("acme_invoice_2024-02.pdf", b"%PDF-1.4\nAcme Invoice\nAmount: $3500"),
            ("techcorp_invoice_q4.pdf", b"%PDF-1.4\nTechCorp Invoice\nTotal: $12000"),
            ("personal_receipt.pdf", b"%PDF-1.4\nReceipt\nThank you"),
        ]

        for filename, content in files:
            (source / filename).write_bytes(content)

        # Set up client-specific subcategories under Documents with keywords
        acme_rule = CategoryRule(keywords=["acme"])
        isolated_manager.add("Acme Client", parent="Documents", rules=acme_rule)

        techcorp_rule = CategoryRule(keywords=["techcorp"])
        isolated_manager.add("TechCorp Client", parent="Documents", rules=techcorp_rule)

        # Run engine - patch both locations where get_category_manager is used
        with patch("tidyup.categories.get_category_manager", return_value=isolated_manager):
            with patch("tidyup.engine.get_category_manager", return_value=isolated_manager):
                engine = Engine(source, destination=dest, options={"dry_run": True})
                result = engine.run()

        # All files should be processed
        assert result.summary.processed == 4

        # Verify at least some files go to client subcategories (filename keywords match)
        # Category names are normalized, so use case-insensitive matching
        acme_count = sum(1 for a in result.actions if "acme" in str(a.dest_path).lower())
        techcorp_count = sum(1 for a in result.actions if "techcorp" in str(a.dest_path).lower())

        # Both clients should have files
        assert acme_count >= 1, "Expected at least one file in Acme Client"
        assert techcorp_count >= 1, "Expected at least one file in TechCorp Client"

    def test_contract_and_proposal_workflow(self, tmp_path: Path, isolated_manager: CategoryManager) -> None:
        """Contracts and proposals organized into Work subcategories."""
        source = tmp_path / "source"
        source.mkdir()
        dest = tmp_path / "dest"

        files = [
            ("client_contract_signed.pdf", b"%PDF-1.4\nContract Agreement"),
            ("proposal_website_redesign.pdf", b"%PDF-1.4\nProposal for services"),
            ("statement_of_work.docx", b"PK\x03\x04Statement of Work"),
            ("nda_mutual.pdf", b"%PDF-1.4\nNon-Disclosure Agreement"),
        ]

        for filename, content in files:
            (source / filename).write_bytes(content)

        # Create Work subcategories with keyword rules
        contracts_rule = CategoryRule(keywords=["contract", "agreement", "nda", "signed"])
        isolated_manager.add("Contracts", rules=contracts_rule)

        proposals_rule = CategoryRule(keywords=["proposal", "quote", "estimate", "bid"])
        isolated_manager.add("Proposals", rules=proposals_rule)

        with patch("tidyup.categories.get_category_manager", return_value=isolated_manager):
            engine = Engine(source, destination=dest, options={"dry_run": True})
            result = engine.run()

        assert result.summary.processed == 4


class TestDeveloperDownloads:
    """Test scenarios typical for developers: books, papers, code, screenshots."""

    def test_technical_books_organization(self, tmp_path: Path, isolated_manager: CategoryManager) -> None:
        """Technical books organized into Books/Technical subcategory."""
        source = tmp_path / "source"
        source.mkdir()
        dest = tmp_path / "dest"

        files = [
            ("Clean_Code_A_Handbook.epub", b"PK\x03\x04programming best practices"),
            ("Design_Patterns.epub", b"PK\x03\x04software architecture patterns"),
            ("The_Pragmatic_Programmer.epub", b"PK\x03\x04software development"),
            ("Python_Cookbook.epub", b"PK\x03\x04python recipes code"),
        ]

        for filename, content in files:
            (source / filename).write_bytes(content)

        # Create Technical Books subcategory
        tech_rule = CategoryRule(
            keywords=["programming", "software", "code", "developer", "algorithm", "python", "javascript"]
        )
        isolated_manager.add("Technical", parent="Books", rules=tech_rule)

        with patch("tidyup.categories.get_category_manager", return_value=isolated_manager):
            engine = Engine(source, destination=dest, options={"dry_run": True})
            result = engine.run()

        assert result.summary.processed == 4

        # All should go to Technical under Books
        for action in result.actions:
            assert "Technical" in str(action.dest_path) or "Books" in str(action.dest_path)

    def test_arxiv_papers_organization(self, tmp_path: Path, isolated_manager: CategoryManager) -> None:
        """arXiv papers with numeric IDs organized into Papers category."""
        source = tmp_path / "source"
        source.mkdir()
        dest = tmp_path / "dest"

        # Realistic arXiv-style filenames
        files = [
            ("2401.05712.pdf", b"%PDF-1.4\nAbstract: Deep learning..."),
            ("2312.00001.pdf", b"%PDF-1.4\nIntroduction: Large language models..."),
            ("2311.12345v2.pdf", b"%PDF-1.4\nWe present a novel approach..."),
            ("research_notes.pdf", b"%PDF-1.4\nMeeting notes from research"),
        ]

        for filename, content in files:
            (source / filename).write_bytes(content)

        # Create Research Papers subcategory with pattern for arXiv IDs
        arxiv_rule = CategoryRule(patterns=["[0-9][0-9][0-9][0-9].*"])
        isolated_manager.add("arXiv Papers", parent="Papers", rules=arxiv_rule)

        with patch("tidyup.categories.get_category_manager", return_value=isolated_manager):
            engine = Engine(source, destination=dest, options={"dry_run": True})
            result = engine.run()

        assert result.summary.processed == 4

    def test_screenshot_organization(self, tmp_path: Path, isolated_manager: CategoryManager) -> None:
        """Screenshots organized by date pattern."""
        source = tmp_path / "source"
        source.mkdir()
        dest = tmp_path / "dest"

        # macOS-style screenshot filenames
        files = [
            ("Screenshot 2024-01-15 at 10.30.45.png", b"\x89PNG\r\n\x1a\n"),
            ("Screenshot 2024-01-16 at 14.22.00.png", b"\x89PNG\r\n\x1a\n"),
            ("Screen Recording 2024-01-15.mov", b"\x00\x00\x00\x1cftyp"),
            ("profile_photo.jpg", b"\xff\xd8\xff\xe0"),
        ]

        for filename, content in files:
            (source / filename).write_bytes(content)

        # Create Mac Captures subcategory under Screenshots with pattern
        screenshot_rule = CategoryRule(patterns=["Screenshot*", "Screen Recording*"])
        isolated_manager.add("Mac Captures", parent="Screenshots", rules=screenshot_rule)

        with patch("tidyup.categories.get_category_manager", return_value=isolated_manager):
            engine = Engine(source, destination=dest, options={"dry_run": True})
            result = engine.run()

        assert result.summary.processed == 4


class TestStudentDownloads:
    """Test scenarios typical for students: papers, textbooks, lecture materials."""

    def test_course_materials_organization(self, tmp_path: Path, isolated_manager: CategoryManager) -> None:
        """Course materials organized by subject."""
        source = tmp_path / "source"
        source.mkdir()
        dest = tmp_path / "dest"

        files = [
            ("CS101_lecture_notes.pdf", b"%PDF-1.4\nComputer Science 101"),
            ("CS101_assignment_3.pdf", b"%PDF-1.4\nAssignment 3"),
            ("MATH201_textbook_ch5.pdf", b"%PDF-1.4\nCalculus Chapter 5"),
            ("PHYS101_lab_report.docx", b"PK\x03\x04Physics Lab"),
        ]

        for filename, content in files:
            (source / filename).write_bytes(content)

        # Create course-specific categories
        cs_rule = CategoryRule(patterns=["CS101*", "CS201*", "CS*_*"])
        isolated_manager.add("Computer Science", rules=cs_rule)

        math_rule = CategoryRule(patterns=["MATH*", "math*"])
        isolated_manager.add("Mathematics", rules=math_rule)

        with patch("tidyup.categories.get_category_manager", return_value=isolated_manager):
            engine = Engine(source, destination=dest, options={"dry_run": True})
            result = engine.run()

        assert result.summary.processed == 4

    def test_research_paper_organization(self, tmp_path: Path, isolated_manager: CategoryManager) -> None:
        """Research papers and thesis materials organized."""
        source = tmp_path / "source"
        source.mkdir()
        dest = tmp_path / "dest"

        files = [
            ("thesis_draft_v3.pdf", b"%PDF-1.4\nThesis: Machine Learning Applications"),
            ("literature_review.pdf", b"%PDF-1.4\nLiterature Review"),
            ("methodology_chapter.docx", b"PK\x03\x04Research Methodology"),
            ("references.bib", b"@article{smith2024,"),
        ]

        for filename, content in files:
            (source / filename).write_bytes(content)

        # Create Thesis category with keywords
        thesis_rule = CategoryRule(keywords=["thesis", "dissertation", "methodology", "literature"])
        isolated_manager.add("Thesis", parent="Papers", rules=thesis_rule)

        with patch("tidyup.categories.get_category_manager", return_value=isolated_manager):
            engine = Engine(source, destination=dest, options={"dry_run": True})
            result = engine.run()

        assert result.summary.processed == 4


class TestMixedDownloads:
    """Test scenarios with mixed file types typical of daily use."""

    def test_weekly_downloads_mix(self, tmp_path: Path, isolated_manager: CategoryManager) -> None:
        """Typical week of downloads: various file types."""
        source = tmp_path / "source"
        source.mkdir()
        dest = tmp_path / "dest"

        # Realistic mix of files
        files = [
            # Documents
            ("resume_2024.pdf", b"%PDF-1.4\nResume"),
            ("meeting_notes_jan15.docx", b"PK\x03\x04Notes"),
            # Images
            ("vacation_photo.jpg", b"\xff\xd8\xff\xe0"),
            ("logo_design_v2.png", b"\x89PNG\r\n\x1a\n"),
            # Archives
            ("project_backup.zip", b"PK\x03\x04backup"),
            ("fonts.tar.gz", b"\x1f\x8b\x08\x00fonts"),
            # Books
            ("novel_bestseller.epub", b"PK\x03\x04novel fiction"),
            # Audio
            ("podcast_episode_42.mp3", b"ID3\x04\x00\x00"),
        ]

        for filename, content in files:
            (source / filename).write_bytes(content)

        with patch("tidyup.categories.get_category_manager", return_value=isolated_manager):
            with patch("tidyup.engine.ActionLogger.save"):
                engine = Engine(source, destination=dest)
                result = engine.run()

        # All files should be processed
        assert result.summary.processed == 8
        assert result.summary.moved == 8

        # Verify destination structure was created
        assert dest.exists()

    def test_duplicate_filename_handling(self, tmp_path: Path, isolated_manager: CategoryManager) -> None:
        """Handle files with same base name but different content."""
        source = tmp_path / "source"
        source.mkdir()
        dest = tmp_path / "dest"

        # Create files with similar names in the source folder
        (source / "report.pdf").write_bytes(b"%PDF-1.4\nReport 1")
        (source / "report_copy.pdf").write_bytes(b"%PDF-1.4\nReport 2")

        with patch("tidyup.categories.get_category_manager", return_value=isolated_manager):
            with patch("tidyup.engine.ActionLogger.save"):
                engine = Engine(source, destination=dest)
                result = engine.run()

        # Both should be processed
        assert result.summary.processed == 2
        assert result.summary.moved == 2


class TestEdgeCaseScenarios:
    """Edge cases that can occur in real-world usage."""

    def test_unicode_filenames(self, tmp_path: Path, isolated_manager: CategoryManager) -> None:
        """Handle files with unicode characters in names."""
        source = tmp_path / "source"
        source.mkdir()
        dest = tmp_path / "dest"

        files = [
            ("日本語ドキュメント.pdf", b"%PDF-1.4\nJapanese"),
            ("Présentation_été.pdf", b"%PDF-1.4\nFrench"),
            ("Übersicht_2024.pdf", b"%PDF-1.4\nGerman"),
            ("документ.pdf", b"%PDF-1.4\nRussian"),
        ]

        for filename, content in files:
            (source / filename).write_bytes(content)

        with patch("tidyup.categories.get_category_manager", return_value=isolated_manager):
            engine = Engine(source, destination=dest, options={"dry_run": True})
            result = engine.run()

        # All unicode files should be processed
        assert result.summary.processed == 4

    def test_very_long_filenames(self, tmp_path: Path, isolated_manager: CategoryManager) -> None:
        """Handle files with very long names."""
        source = tmp_path / "source"
        source.mkdir()
        dest = tmp_path / "dest"

        # Create a very long filename (within filesystem limits)
        long_name = "a" * 200 + ".pdf"
        (source / long_name).write_bytes(b"%PDF-1.4\nLong name")

        with patch("tidyup.categories.get_category_manager", return_value=isolated_manager):
            engine = Engine(source, destination=dest, options={"dry_run": True})
            result = engine.run()

        assert result.summary.processed == 1

    def test_hidden_files_skipped(self, tmp_path: Path, isolated_manager: CategoryManager) -> None:
        """Hidden files (starting with .) should be skipped."""
        source = tmp_path / "source"
        source.mkdir()
        dest = tmp_path / "dest"

        files = [
            (".hidden_file.pdf", b"%PDF-1.4\nHidden"),
            (".DS_Store", b"\x00\x00\x00\x01"),
            ("visible_file.pdf", b"%PDF-1.4\nVisible"),
        ]

        for filename, content in files:
            (source / filename).write_bytes(content)

        with patch("tidyup.categories.get_category_manager", return_value=isolated_manager):
            engine = Engine(source, destination=dest, options={"dry_run": True})
            result = engine.run()

        # Only visible file should be processed
        assert result.summary.processed == 1

    def test_empty_file_handling(self, tmp_path: Path, isolated_manager: CategoryManager) -> None:
        """Handle empty files gracefully."""
        source = tmp_path / "source"
        source.mkdir()
        dest = tmp_path / "dest"

        # Create empty file
        (source / "empty_file.pdf").write_bytes(b"")
        (source / "normal_file.pdf").write_bytes(b"%PDF-1.4\nContent")

        with patch("tidyup.categories.get_category_manager", return_value=isolated_manager):
            engine = Engine(source, destination=dest, options={"dry_run": True})
            result = engine.run()

        # Both files should be processed
        assert result.summary.processed == 2
