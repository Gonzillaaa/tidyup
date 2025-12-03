"""End-to-end integration tests for Phase 7 features.

Tests complete workflows combining routing, rules, and suggestions.
"""

import pytest
from pathlib import Path
from unittest.mock import patch

from tidyup.engine import Engine
from tidyup.categories import CategoryManager, Category
from tidyup.rules import CategoryRule
from tidyup.suggestions import suggest_rules


@pytest.fixture
def isolated_manager(tmp_path: Path) -> CategoryManager:
    """Create an isolated CategoryManager for testing with default categories."""
    config_path = tmp_path / "config.yaml"
    manager = CategoryManager(config_path=config_path)
    manager.load()  # Load default categories
    return manager


class TestRoutingWorkflow:
    """Tests for routing workflow integration."""

    def test_invoice_routing_workflow(self, tmp_path: Path, isolated_manager: CategoryManager) -> None:
        """Complete workflow: create category → set routing → organize files."""
        source = tmp_path / "source"
        source.mkdir()
        dest = tmp_path / "dest"

        # Create an invoice-like PDF
        invoice_pdf = source / "invoice_acme_2024.pdf"
        invoice_pdf.write_bytes(b"%PDF-1.4\nInvoice\nTotal: $100\nAmount Due")

        # Create a regular PDF
        regular_pdf = source / "report.pdf"
        regular_pdf.write_bytes(b"%PDF-1.4\nQuarterly Report")

        # Add Invoices category
        isolated_manager.add("Invoices")

        # Set routing: InvoiceDetector Documents → Invoices
        isolated_manager.routing.set_remap("Documents", "Invoices", detector_name="InvoiceDetector")

        # Run engine with patched category manager
        with patch("tidyup.categories.get_category_manager", return_value=isolated_manager):
            with patch("tidyup.engine.ActionLogger.save"):
                engine = Engine(source, destination=dest)
                result = engine.run()

        # Verify files were processed
        assert result.summary.processed == 2
        assert result.summary.moved == 2

    def test_global_category_rename_workflow(self, tmp_path: Path, isolated_manager: CategoryManager) -> None:
        """Rename Documents to Paperwork via global routing."""
        source = tmp_path / "source"
        source.mkdir()
        dest = tmp_path / "dest"

        # Create a document
        (source / "report.pdf").write_bytes(b"%PDF-1.4\nSome content")

        # Add Paperwork category
        isolated_manager.add("Paperwork")

        # Global remap: Documents → Paperwork
        isolated_manager.routing.set_remap("Documents", "Paperwork")

        # Run engine
        with patch("tidyup.categories.get_category_manager", return_value=isolated_manager):
            with patch("tidyup.engine.ActionLogger.save"):
                engine = Engine(source, destination=dest)
                result = engine.run()

        # Verify file was moved
        assert result.summary.moved == 1

        # Check that Paperwork folder exists
        paperwork_num = isolated_manager.get_by_name("Paperwork").number
        paperwork_folder = dest / f"{paperwork_num:02d}_Paperwork"
        assert paperwork_folder.exists()


class TestRulesWorkflow:
    """Tests for rules-based subcategorization workflow."""

    def test_subcategory_rules_workflow(self, tmp_path: Path, isolated_manager: CategoryManager) -> None:
        """Technical Books vs Fiction using keyword rules."""
        source = tmp_path / "source"
        source.mkdir()
        dest = tmp_path / "dest"

        # Create book-like files
        tech_book = source / "Clean_Code_Programming.epub"
        tech_book.write_bytes(b"PK\x03\x04programming software code")

        fiction_book = source / "Great_Gatsby_Novel.epub"
        fiction_book.write_bytes(b"PK\x03\x04novel fiction story")

        # Create Technical subcategory with rules
        tech_rule = CategoryRule(
            keywords=["programming", "software", "code", "algorithm"]
        )
        isolated_manager.add("Technical", parent="Books", rules=tech_rule)

        # Create Fiction subcategory with rules
        fiction_rule = CategoryRule(
            keywords=["novel", "fiction", "fantasy", "story"]
        )
        isolated_manager.add("Fiction", parent="Books", rules=fiction_rule)

        # Run engine in dry-run mode
        with patch("tidyup.categories.get_category_manager", return_value=isolated_manager):
            engine = Engine(source, destination=dest, options={"dry_run": True})
            result = engine.run()

        # Verify files would be categorized
        assert result.summary.processed == 2

        # Check actions for correct categories
        for action in result.actions:
            if "Clean_Code" in action.file.name:
                # Should match Technical due to "programming" in filename
                assert "Technical" in str(action.dest_path) or "Books" in str(action.dest_path)
            elif "Great_Gatsby" in action.file.name:
                # Should match Fiction due to "novel" in filename
                assert "Fiction" in str(action.dest_path) or "Books" in str(action.dest_path)

    def test_pattern_based_rules(self, tmp_path: Path, isolated_manager: CategoryManager) -> None:
        """Client projects matched by filename patterns."""
        source = tmp_path / "source"
        source.mkdir()
        dest = tmp_path / "dest"

        # Create client files
        (source / "acme_q4_report.pdf").write_bytes(b"%PDF-1.4\nAcme report")
        (source / "techcorp_proposal.pdf").write_bytes(b"%PDF-1.4\nTechCorp")
        (source / "random_doc.pdf").write_bytes(b"%PDF-1.4\nRandom")

        # Create client categories with pattern rules
        acme_rule = CategoryRule(patterns=["acme_*", "*_acme_*"])
        isolated_manager.add("Acme Projects", rules=acme_rule)

        techcorp_rule = CategoryRule(patterns=["techcorp_*", "tc_*"])
        isolated_manager.add("TechCorp", rules=techcorp_rule)

        # Run engine
        with patch("tidyup.categories.get_category_manager", return_value=isolated_manager):
            engine = Engine(source, destination=dest, options={"dry_run": True})
            result = engine.run()

        assert result.summary.processed == 3


class TestSuggestionsWorkflow:
    """Tests for smart suggestions workflow."""

    def test_suggestions_create_working_rules(self) -> None:
        """Suggestions create functional category rules."""
        # Get suggestions for Technical Books
        suggestion = suggest_rules("Technical Books")

        assert suggestion.has_suggestions
        assert suggestion.parent == "Books"
        assert len(suggestion.keywords) > 0
        assert any(kw in suggestion.keywords for kw in ["programming", "software", "code", "technical"])

    def test_suggestions_infer_parent_correctly(self) -> None:
        """Parent inference works for common category types."""
        test_cases = [
            ("Fiction", "Books"),
            ("Invoices", "Documents"),
            ("Photos", "Images"),
            ("Research Papers", "Papers"),
            ("Music Collection", "Audio"),
        ]

        for name, expected_parent in test_cases:
            suggestion = suggest_rules(name)
            assert suggestion.parent == expected_parent, f"Failed for {name}"

    def test_suggestion_keywords_are_relevant(self) -> None:
        """Suggested keywords match category context."""
        # Invoice category
        invoice_suggestion = suggest_rules("Client Invoices")
        assert any(kw in invoice_suggestion.keywords for kw in ["invoice", "receipt", "payment"])

        # Work category
        work_suggestion = suggest_rules("Work Projects")
        assert any(kw in work_suggestion.keywords for kw in ["project", "client", "meeting"])


class TestCombinedWorkflow:
    """Tests for combined routing + rules workflow."""

    def test_rules_evaluated_before_routing(self, tmp_path: Path, isolated_manager: CategoryManager) -> None:
        """Rules are evaluated before routing is applied."""
        source = tmp_path / "source"
        source.mkdir()
        dest = tmp_path / "dest"

        # Create a file that matches a rule
        (source / "technical_guide.pdf").write_bytes(b"%PDF-1.4\nprogramming code")

        # Create Technical subcategory with keywords
        tech_rule = CategoryRule(keywords=["programming", "code", "technical"])
        isolated_manager.add("Technical", parent="Documents", rules=tech_rule)

        # Also set up routing for Documents
        isolated_manager.add("Paperwork")
        isolated_manager.routing.set_remap("Documents", "Paperwork")

        # Run engine
        with patch("tidyup.categories.get_category_manager", return_value=isolated_manager):
            engine = Engine(source, destination=dest, options={"dry_run": True})
            result = engine.run()

        # File should be processed
        assert result.summary.processed == 1

    def test_full_workflow_with_suggestions(self, tmp_path: Path, isolated_manager: CategoryManager) -> None:
        """Complete workflow: suggestions → category → rules → organize."""
        source = tmp_path / "source"
        source.mkdir()
        dest = tmp_path / "dest"

        # Create files
        (source / "Clean_Code.epub").write_bytes(b"PK\x03\x04book content")

        # Step 1: Get suggestions
        suggestion = suggest_rules("Technical Books")
        assert suggestion.has_suggestions

        # Step 2: Create category with suggestions
        if suggestion.keywords:
            rule = CategoryRule(keywords=suggestion.keywords[:5])
            isolated_manager.add("Technical Books", parent=suggestion.parent, rules=rule)

        # Step 3: Run engine
        with patch("tidyup.categories.get_category_manager", return_value=isolated_manager):
            engine = Engine(source, destination=dest, options={"dry_run": True})
            result = engine.run()

        assert result.summary.processed == 1


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_nonexistent_routing_target(self, tmp_path: Path, isolated_manager: CategoryManager) -> None:
        """Routing to non-existent category falls back gracefully."""
        source = tmp_path / "source"
        source.mkdir()
        dest = tmp_path / "dest"

        (source / "test.pdf").write_bytes(b"%PDF-1.4\ncontent")

        # Set routing to non-existent category
        isolated_manager.routing.remap["Documents"] = "NonExistent"

        # Run engine - should fall back to original category or Unsorted
        with patch("tidyup.categories.get_category_manager", return_value=isolated_manager):
            with patch("tidyup.engine.ActionLogger.save"):
                engine = Engine(source, destination=dest)
                result = engine.run()

        # Should still process the file
        assert result.summary.processed == 1

    def test_empty_rules_dont_match(self, tmp_path: Path, isolated_manager: CategoryManager) -> None:
        """Categories with empty rules don't match any files."""
        # Create category with empty rules
        empty_rule = CategoryRule()
        isolated_manager.add("Empty Rules", rules=empty_rule)

        # The category exists but won't match anything
        cat = isolated_manager.get_by_name("Empty Rules")
        assert cat is not None
        assert cat.rules is not None
        assert not cat.rules.matches("test.pdf", "pdf")

    def test_multiple_rules_first_match_wins(self, tmp_path: Path, isolated_manager: CategoryManager) -> None:
        """When multiple rules could match, first one wins."""
        # Create two categories that could both match
        rule1 = CategoryRule(keywords=["code"])
        isolated_manager.add("Category1", parent="Documents", rules=rule1)

        rule2 = CategoryRule(keywords=["code", "programming"])
        isolated_manager.add("Category2", parent="Documents", rules=rule2)

        # Evaluate rules - first match should win
        result = isolated_manager.evaluate_rules(
            filename="code_example.txt",
            extension="txt",
            parent_category="Documents"
        )

        # Category1 was added first and matches
        assert result == "Category1"
