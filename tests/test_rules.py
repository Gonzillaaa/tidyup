"""Tests for the rules engine."""

from pathlib import Path

from tidyup.categories import CategoryManager
from tidyup.rules import CategoryRule


class TestCategoryRule:
    """Tests for CategoryRule dataclass."""

    def test_matches_extension(self) -> None:
        """Matches by file extension."""
        rule = CategoryRule(extensions=["pdf", "doc"])
        assert rule.matches("report.pdf", "pdf") is True
        assert rule.matches("report.doc", "doc") is True
        assert rule.matches("report.txt", "txt") is False

    def test_matches_extension_case_insensitive(self) -> None:
        """Extension matching is case-insensitive."""
        rule = CategoryRule(extensions=["PDF"])
        assert rule.matches("report.pdf", "pdf") is True
        assert rule.matches("report.PDF", "PDF") is True

    def test_matches_pattern(self) -> None:
        """Matches by filename pattern."""
        rule = CategoryRule(patterns=["acme_*", "*_project_*"])
        assert rule.matches("acme_report.pdf", "pdf") is True
        assert rule.matches("big_project_v2.doc", "doc") is True
        assert rule.matches("report.pdf", "pdf") is False

    def test_matches_pattern_case_insensitive(self) -> None:
        """Pattern matching is case-insensitive."""
        rule = CategoryRule(patterns=["ACME_*"])
        assert rule.matches("acme_report.pdf", "pdf") is True
        assert rule.matches("Acme_Report.pdf", "pdf") is True

    def test_matches_keyword_in_filename(self) -> None:
        """Matches keywords in filename."""
        rule = CategoryRule(keywords=["invoice", "receipt"])
        assert rule.matches("invoice_acme.pdf", "pdf") is True
        assert rule.matches("acme_receipt_2024.pdf", "pdf") is True
        assert rule.matches("report.pdf", "pdf") is False

    def test_matches_keyword_in_content(self) -> None:
        """Matches keywords in content."""
        rule = CategoryRule(keywords=["programming", "software"])
        content = "This book is about software development."
        assert rule.matches("book.pdf", "pdf", content=content) is True
        assert rule.matches("book.pdf", "pdf", content="fiction novel") is False

    def test_matches_keyword_case_insensitive(self) -> None:
        """Keyword matching is case-insensitive."""
        rule = CategoryRule(keywords=["Programming"])
        assert rule.matches("PROGRAMMING_guide.pdf", "pdf") is True
        content = "Learn PROGRAMMING today"
        assert rule.matches("guide.pdf", "pdf", content=content) is True

    def test_matches_min_keyword_matches(self) -> None:
        """Respects min_keyword_matches setting."""
        rule = CategoryRule(
            keywords=["programming", "software", "code"],
            min_keyword_matches=2,
        )
        # Only one keyword match - not enough
        assert rule.matches("programming_guide.pdf", "pdf") is False
        # Two keyword matches - sufficient
        assert rule.matches("programming_software.pdf", "pdf") is True
        # Two in content
        content = "Learn programming and write code"
        assert rule.matches("guide.pdf", "pdf", content=content) is True

    def test_no_match_when_no_rules(self) -> None:
        """Returns False when no rules configured."""
        rule = CategoryRule()
        assert rule.matches("anything.pdf", "pdf") is False

    def test_extension_match_takes_priority(self) -> None:
        """Extension match returns True even without keyword match."""
        rule = CategoryRule(
            extensions=["pdf"],
            keywords=["invoice"],  # Won't match filename
        )
        assert rule.matches("report.pdf", "pdf") is True

    def test_to_dict(self) -> None:
        """Converts rule to dictionary."""
        rule = CategoryRule(
            keywords=["programming", "code"],
            patterns=["acme_*"],
            extensions=["pdf"],
            min_keyword_matches=2,
        )
        d = rule.to_dict()
        assert d == {
            "keywords": ["programming", "code"],
            "patterns": ["acme_*"],
            "extensions": ["pdf"],
            "min_keyword_matches": 2,
        }

    def test_to_dict_omits_empty(self) -> None:
        """Omits empty fields from dictionary."""
        rule = CategoryRule(keywords=["test"])
        d = rule.to_dict()
        assert d == {"keywords": ["test"]}
        assert "patterns" not in d
        assert "extensions" not in d
        assert "min_keyword_matches" not in d

    def test_from_dict(self) -> None:
        """Creates rule from dictionary."""
        d = {
            "keywords": ["programming", "code"],
            "patterns": ["acme_*"],
            "extensions": ["pdf"],
            "min_keyword_matches": 2,
        }
        rule = CategoryRule.from_dict(d)
        assert rule.keywords == ["programming", "code"]
        assert rule.patterns == ["acme_*"]
        assert rule.extensions == ["pdf"]
        assert rule.min_keyword_matches == 2

    def test_from_dict_defaults(self) -> None:
        """Uses defaults for missing fields."""
        rule = CategoryRule.from_dict({"keywords": ["test"]})
        assert rule.keywords == ["test"]
        assert rule.patterns == []
        assert rule.extensions == []
        assert rule.min_keyword_matches == 1


class TestCategoryManagerRules:
    """Tests for CategoryManager with rules."""

    def test_add_with_rules(self, tmp_path: Path) -> None:
        """Can add category with rules."""
        config_path = tmp_path / "config.yaml"
        manager = CategoryManager(config_path=config_path)
        manager.load()

        rules = CategoryRule(keywords=["programming", "code"])
        cat = manager.add("Technical", parent="Books", rules=rules)

        assert cat.name == "Technical"
        assert cat.parent == "Books"
        assert cat.rules is not None
        assert cat.rules.keywords == ["programming", "code"]

    def test_save_and_load_with_rules(self, tmp_path: Path) -> None:
        """Rules persist through save/load cycle."""
        config_path = tmp_path / "config.yaml"

        # Create and save
        manager = CategoryManager(config_path=config_path)
        manager.load()
        rules = CategoryRule(
            keywords=["programming", "software"],
            patterns=["tech_*"],
        )
        manager.add("Technical", parent="Books", rules=rules)
        manager.save()

        # Reload
        manager2 = CategoryManager(config_path=config_path)
        manager2.load()

        tech = manager2.get_by_name("Technical")
        assert tech is not None
        assert tech.parent == "Books"
        assert tech.rules is not None
        assert tech.rules.keywords == ["programming", "software"]
        assert tech.rules.patterns == ["tech_*"]

    def test_add_validates_parent_exists(self, tmp_path: Path) -> None:
        """Raises error if parent category doesn't exist."""
        config_path = tmp_path / "config.yaml"
        manager = CategoryManager(config_path=config_path)
        manager.load()

        import pytest
        with pytest.raises(ValueError, match="Parent category not found"):
            manager.add("SubCategory", parent="NonExistent")

    def test_get_subcategories(self, tmp_path: Path) -> None:
        """Returns subcategories of a parent."""
        config_path = tmp_path / "config.yaml"
        manager = CategoryManager(config_path=config_path)
        manager.load()

        manager.add("Technical", parent="Books")
        manager.add("Fiction", parent="Books")
        manager.add("Invoices", parent="Documents")

        books_subs = manager.get_subcategories("Books")
        assert len(books_subs) == 2
        assert {c.name for c in books_subs} == {"Technical", "Fiction"}

        docs_subs = manager.get_subcategories("Documents")
        assert len(docs_subs) == 1
        assert docs_subs[0].name == "Invoices"

    def test_get_subcategories_case_insensitive(self, tmp_path: Path) -> None:
        """Subcategory lookup is case-insensitive."""
        config_path = tmp_path / "config.yaml"
        manager = CategoryManager(config_path=config_path)
        manager.load()

        manager.add("Technical", parent="Books")

        # Different cases should all work
        assert len(manager.get_subcategories("books")) == 1
        assert len(manager.get_subcategories("BOOKS")) == 1

    def test_evaluate_rules_no_match(self, tmp_path: Path) -> None:
        """Returns None when no rules match."""
        config_path = tmp_path / "config.yaml"
        manager = CategoryManager(config_path=config_path)
        manager.load()

        rules = CategoryRule(keywords=["programming"])
        manager.add("Technical", parent="Books", rules=rules)

        result = manager.evaluate_rules(
            filename="fiction_novel.epub",
            extension="epub",
            parent_category="Books",
        )
        assert result is None

    def test_evaluate_rules_matches(self, tmp_path: Path) -> None:
        """Returns subcategory name when rules match."""
        config_path = tmp_path / "config.yaml"
        manager = CategoryManager(config_path=config_path)
        manager.load()

        rules = CategoryRule(keywords=["programming", "software"])
        manager.add("Technical", parent="Books", rules=rules)

        result = manager.evaluate_rules(
            filename="clean_code_programming.epub",
            extension="epub",
            parent_category="Books",
        )
        assert result == "Technical"

    def test_evaluate_rules_with_content(self, tmp_path: Path) -> None:
        """Matches keywords in content."""
        config_path = tmp_path / "config.yaml"
        manager = CategoryManager(config_path=config_path)
        manager.load()

        rules = CategoryRule(keywords=["software", "development"])
        manager.add("Technical", parent="Books", rules=rules)

        result = manager.evaluate_rules(
            filename="book.epub",
            extension="epub",
            parent_category="Books",
            content="This is a book about software development",
        )
        assert result == "Technical"

    def test_evaluate_rules_first_match_wins(self, tmp_path: Path) -> None:
        """First matching subcategory wins."""
        config_path = tmp_path / "config.yaml"
        manager = CategoryManager(config_path=config_path)
        manager.load()

        # Add two subcategories that could both match
        manager.add("Technical", parent="Books", rules=CategoryRule(keywords=["code"]))
        manager.add("Programming", parent="Books", rules=CategoryRule(keywords=["code"]))

        result = manager.evaluate_rules(
            filename="learn_code.epub",
            extension="epub",
            parent_category="Books",
        )
        # First added should match
        assert result == "Technical"

    def test_evaluate_rules_wrong_parent(self, tmp_path: Path) -> None:
        """Doesn't match subcategories of different parent."""
        config_path = tmp_path / "config.yaml"
        manager = CategoryManager(config_path=config_path)
        manager.load()

        rules = CategoryRule(keywords=["invoice"])
        manager.add("Invoices", parent="Documents", rules=rules)

        # This file has "invoice" but parent is Books, not Documents
        result = manager.evaluate_rules(
            filename="invoice_tracker.epub",
            extension="epub",
            parent_category="Books",
        )
        assert result is None

    def test_remove_preserves_other_rules(self, tmp_path: Path) -> None:
        """Removing category preserves rules on other categories."""
        config_path = tmp_path / "config.yaml"
        manager = CategoryManager(config_path=config_path)
        manager.load()

        manager.add("Technical", parent="Books", rules=CategoryRule(keywords=["code"]))
        manager.add("Fiction", parent="Books", rules=CategoryRule(keywords=["novel"]))

        manager.remove("Technical")

        fiction = manager.get_by_name("Fiction")
        assert fiction is not None
        assert fiction.rules is not None
        assert fiction.rules.keywords == ["novel"]

    def test_reorder_preserves_rules(self, tmp_path: Path) -> None:
        """Reordering categories preserves rules."""
        config_path = tmp_path / "config.yaml"
        config_path.write_text("categories:\n  - Foo\n  - Bar\n")

        manager = CategoryManager(config_path=config_path)
        manager.load()

        # Add rules to Bar
        bar = manager.get_by_name("Bar")
        # We need to remove and re-add with rules since load doesn't have rules
        manager.remove("Bar")
        manager.add("Bar", rules=CategoryRule(keywords=["test"]))

        manager.reorder(["Bar", "Foo"])

        bar = manager.get_by_name("Bar")
        assert bar is not None
        assert bar.number == 1  # Now first
        assert bar.rules is not None
        assert bar.rules.keywords == ["test"]
