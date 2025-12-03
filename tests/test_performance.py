"""Performance tests for Phase 7 features.

Benchmarks rules evaluation, suggestions, and config loading.
"""

import time
from pathlib import Path

import pytest

from tidyup.categories import CategoryManager
from tidyup.rules import CategoryRule
from tidyup.suggestions import suggest_rules


class TestRulesEvaluationPerformance:
    """Performance tests for rules evaluation."""

    @pytest.fixture
    def manager_with_rules(self, tmp_path: Path) -> CategoryManager:
        """Create a manager with multiple categories and rules."""
        config_path = tmp_path / "config.yaml"
        manager = CategoryManager(config_path=config_path)
        manager.load()

        # Add 10 categories with rules
        for i in range(10):
            rule = CategoryRule(
                keywords=[f"keyword{i}", f"term{i}", f"pattern{i}"],
                patterns=[f"*file{i}*", f"doc{i}_*"],
            )
            manager.add(f"Category{i}", parent="Documents", rules=rule)

        return manager

    def test_rules_evaluation_speed(self, manager_with_rules: CategoryManager) -> None:
        """Rules should evaluate in <10ms per file on average."""
        test_files = [
            (f"document_{i}.pdf", "pdf", f"content with keyword{i % 10}")
            for i in range(100)
        ]

        start = time.perf_counter()
        for filename, extension, content in test_files:
            manager_with_rules.evaluate_rules(
                filename=filename,
                extension=extension,
                parent_category="Documents",
                content=content,
            )
        elapsed = time.perf_counter() - start

        avg_time_ms = (elapsed / len(test_files)) * 1000
        assert avg_time_ms < 10, f"Average evaluation time {avg_time_ms:.2f}ms exceeds 10ms"

    def test_rules_evaluation_without_content(self, manager_with_rules: CategoryManager) -> None:
        """Rules evaluation without content should be faster."""
        test_files = [(f"file{i}.pdf", "pdf") for i in range(100)]

        start = time.perf_counter()
        for filename, extension in test_files:
            manager_with_rules.evaluate_rules(
                filename=filename,
                extension=extension,
                parent_category="Documents",
            )
        elapsed = time.perf_counter() - start

        avg_time_ms = (elapsed / len(test_files)) * 1000
        assert avg_time_ms < 5, f"Average evaluation time {avg_time_ms:.2f}ms exceeds 5ms"

    def test_many_subcategories(self, tmp_path: Path) -> None:
        """Performance with many subcategories."""
        config_path = tmp_path / "config.yaml"
        manager = CategoryManager(config_path=config_path)
        manager.load()

        # Add 50 subcategories
        for i in range(50):
            rule = CategoryRule(keywords=[f"kw{i}"])
            manager.add(f"Sub{i}", parent="Documents", rules=rule)

        # Time evaluation
        start = time.perf_counter()
        for _ in range(100):
            manager.evaluate_rules(
                filename="test_file.pdf",
                extension="pdf",
                parent_category="Documents",
            )
        elapsed = time.perf_counter() - start

        avg_time_ms = (elapsed / 100) * 1000
        assert avg_time_ms < 20, f"Average evaluation time {avg_time_ms:.2f}ms exceeds 20ms"


class TestSuggestionsPerformance:
    """Performance tests for suggestions."""

    def test_suggest_rules_speed(self) -> None:
        """Suggestions should return in <5ms."""
        test_names = [
            "Technical Books",
            "Fiction",
            "Invoices",
            "Research Papers",
            "Work Projects",
            "Music Collection",
            "Photos",
            "Screenshots",
            "Client Documents",
            "Personal Files",
        ]

        start = time.perf_counter()
        for name in test_names:
            suggest_rules(name)
        elapsed = time.perf_counter() - start

        avg_time_ms = (elapsed / len(test_names)) * 1000
        assert avg_time_ms < 5, f"Average suggestion time {avg_time_ms:.2f}ms exceeds 5ms"

    def test_suggest_rules_unknown_name(self) -> None:
        """Unknown names should still be fast (no match is quick)."""
        start = time.perf_counter()
        for i in range(100):
            suggest_rules(f"UnknownCategory{i}XYZ")
        elapsed = time.perf_counter() - start

        avg_time_ms = (elapsed / 100) * 1000
        assert avg_time_ms < 2, f"Average time for unknown {avg_time_ms:.2f}ms exceeds 2ms"

    def test_suggest_rules_long_names(self) -> None:
        """Long category names should still be fast."""
        long_names = [
            "Very Long Technical Programming Books Category Name",
            "Client Project Documents and Proposals for 2024",
            "Research Papers on Machine Learning and AI",
        ]

        start = time.perf_counter()
        for _ in range(50):
            for name in long_names:
                suggest_rules(name)
        elapsed = time.perf_counter() - start

        avg_time_ms = (elapsed / (50 * len(long_names))) * 1000
        assert avg_time_ms < 5, f"Average time for long names {avg_time_ms:.2f}ms exceeds 5ms"


class TestConfigPerformance:
    """Performance tests for config loading."""

    def test_config_loading_speed(self, tmp_path: Path) -> None:
        """Config with 50 categories should load in <100ms."""
        config_path = tmp_path / "config.yaml"
        manager = CategoryManager(config_path=config_path)
        manager.load()

        # Add 50 categories
        for i in range(50):
            rule = CategoryRule(keywords=[f"kw{i}", f"term{i}"])
            manager.add(f"Category{i}", rules=rule)

        # Save config
        manager.save()

        # Time loading
        start = time.perf_counter()
        new_manager = CategoryManager(config_path=config_path)
        new_manager.load()
        elapsed = time.perf_counter() - start

        elapsed_ms = elapsed * 1000
        assert elapsed_ms < 100, f"Config loading took {elapsed_ms:.2f}ms, exceeds 100ms"
        assert len(new_manager.categories) >= 50

    def test_category_lookup_speed(self, tmp_path: Path) -> None:
        """Category lookup should be fast."""
        config_path = tmp_path / "config.yaml"
        manager = CategoryManager(config_path=config_path)
        manager.load()

        # Add many categories
        for i in range(50):
            manager.add(f"TestCategory{i}")

        # Time lookups by name
        start = time.perf_counter()
        for _ in range(1000):
            manager.get_by_name("TestCategory25")
            manager.get_by_name("TestCategory10")
        elapsed = time.perf_counter() - start

        avg_time_us = (elapsed / 2000) * 1_000_000  # microseconds
        assert avg_time_us < 100, f"Average lookup time {avg_time_us:.2f}us exceeds 100us"

    def test_routing_resolution_speed(self, tmp_path: Path) -> None:
        """Routing resolution should be fast."""
        config_path = tmp_path / "config.yaml"
        manager = CategoryManager(config_path=config_path)
        manager.load()

        # Set up some routing rules
        manager.add("Invoices")
        manager.add("Paperwork")
        manager.routing.set_remap("Documents", "Paperwork")
        manager.routing.set_remap("Documents", "Invoices", detector_name="InvoiceDetector")

        # Time resolution
        start = time.perf_counter()
        for _ in range(1000):
            manager.resolve_category("Documents", "InvoiceDetector")
            manager.resolve_category("Documents", "GenericDetector")
            manager.resolve_category("Images", None)
        elapsed = time.perf_counter() - start

        avg_time_us = (elapsed / 3000) * 1_000_000
        assert avg_time_us < 50, f"Average routing resolution {avg_time_us:.2f}us exceeds 50us"


class TestRulesMatchingPerformance:
    """Performance tests for individual rule matching."""

    def test_keyword_matching_speed(self) -> None:
        """Keyword matching should be fast."""
        rule = CategoryRule(keywords=["programming", "software", "code", "algorithm", "data"])

        start = time.perf_counter()
        for i in range(1000):
            rule.matches(f"document_{i}.pdf", "pdf", "This is about programming and software")
        elapsed = time.perf_counter() - start

        avg_time_us = (elapsed / 1000) * 1_000_000
        assert avg_time_us < 100, f"Average keyword matching {avg_time_us:.2f}us exceeds 100us"

    def test_pattern_matching_speed(self) -> None:
        """Pattern matching should be fast."""
        rule = CategoryRule(patterns=["invoice_*", "*_receipt_*", "doc_????_*.pdf"])

        start = time.perf_counter()
        for i in range(1000):
            rule.matches(f"invoice_{i:04d}.pdf", "pdf")
        elapsed = time.perf_counter() - start

        avg_time_us = (elapsed / 1000) * 1_000_000
        assert avg_time_us < 50, f"Average pattern matching {avg_time_us:.2f}us exceeds 50us"

    def test_extension_matching_speed(self) -> None:
        """Extension matching should be fastest."""
        rule = CategoryRule(extensions=["pdf", "doc", "docx", "txt", "rtf"])

        start = time.perf_counter()
        for i in range(1000):
            rule.matches(f"document_{i}.pdf", "pdf")
        elapsed = time.perf_counter() - start

        avg_time_us = (elapsed / 1000) * 1_000_000
        assert avg_time_us < 20, f"Average extension matching {avg_time_us:.2f}us exceeds 20us"

    def test_combined_rules_speed(self) -> None:
        """Combined rules (keywords + patterns + extensions) should still be fast."""
        rule = CategoryRule(
            keywords=["tech", "programming", "code"],
            patterns=["*_project_*", "dev_*"],
            extensions=["py", "js", "ts"],
        )

        start = time.perf_counter()
        for i in range(1000):
            rule.matches(f"test_{i}.py", "py", "programming code example")
        elapsed = time.perf_counter() - start

        avg_time_us = (elapsed / 1000) * 1_000_000
        assert avg_time_us < 150, f"Average combined matching {avg_time_us:.2f}us exceeds 150us"
