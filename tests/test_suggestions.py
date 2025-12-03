"""Tests for the suggestions module."""

from tidyup.suggestions import (
    CATEGORY_SUGGESTIONS,
    PARENT_INFERENCE,
    SuggestionResult,
    get_all_parent_patterns,
    get_all_suggestion_patterns,
    suggest_rules,
)


class TestSuggestionResult:
    """Tests for SuggestionResult dataclass."""

    def test_has_suggestions_with_parent(self) -> None:
        """Returns True when parent is set."""
        result = SuggestionResult(parent="Books", keywords=[], confidence=0.5)
        assert result.has_suggestions is True

    def test_has_suggestions_with_keywords(self) -> None:
        """Returns True when keywords are set."""
        result = SuggestionResult(parent=None, keywords=["test"], confidence=0.5)
        assert result.has_suggestions is True

    def test_has_suggestions_empty(self) -> None:
        """Returns False when no suggestions."""
        result = SuggestionResult(parent=None, keywords=[], confidence=0.0)
        assert result.has_suggestions is False


class TestSuggestRules:
    """Tests for suggest_rules function."""

    def test_suggests_keywords_for_tech(self) -> None:
        """Suggests programming keywords for 'Technical'."""
        result = suggest_rules("Technical")
        assert result.has_suggestions
        assert "technical" in result.keywords

    def test_suggests_keywords_for_invoice(self) -> None:
        """Suggests finance keywords for 'Invoice'."""
        result = suggest_rules("Invoice")
        assert result.has_suggestions
        assert "invoice" in result.keywords
        assert "receipt" in result.keywords or "payment" in result.keywords

    def test_suggests_parent_for_fiction(self) -> None:
        """Suggests Books as parent for 'Fiction'."""
        result = suggest_rules("Fiction")
        assert result.parent == "Books"

    def test_suggests_parent_for_receipt(self) -> None:
        """Suggests Documents as parent for 'Receipt'."""
        result = suggest_rules("Receipt")
        assert result.parent == "Documents"

    def test_suggests_parent_for_photo(self) -> None:
        """Suggests Images as parent for 'Photo'."""
        result = suggest_rules("Photo")
        assert result.parent == "Images"

    def test_multi_word_category(self) -> None:
        """Handles multi-word category names."""
        result = suggest_rules("Technical Books")
        assert result.has_suggestions
        # Should find 'tech' pattern and 'book' pattern
        assert len(result.keywords) > 0

    def test_case_insensitive(self) -> None:
        """Pattern matching is case-insensitive."""
        result1 = suggest_rules("INVOICE")
        result2 = suggest_rules("invoice")
        result3 = suggest_rules("Invoice")

        assert result1.has_suggestions
        assert result2.has_suggestions
        assert result3.has_suggestions
        # All should suggest Documents as parent
        assert result1.parent == result2.parent == result3.parent == "Documents"

    def test_no_suggestions_for_unknown(self) -> None:
        """Returns no suggestions for unknown patterns."""
        result = suggest_rules("Xyz123")
        assert result.keywords == []
        assert result.parent is None
        assert result.confidence == 0.0

    def test_confidence_increases_with_matches(self) -> None:
        """Confidence increases with more pattern matches."""
        # Single match
        result1 = suggest_rules("Tech")
        # Multiple matches
        result2 = suggest_rules("Technical Books")

        # More matches should have higher confidence
        assert result2.confidence >= result1.confidence

    def test_keywords_limited_to_10(self) -> None:
        """Keywords list is limited to 10 items."""
        # Use a name that matches many patterns
        result = suggest_rules("Technical Programming Software Code")
        assert len(result.keywords) <= 10

    def test_keywords_sorted(self) -> None:
        """Keywords are returned in sorted order."""
        result = suggest_rules("Finance")
        if result.keywords:
            assert result.keywords == sorted(result.keywords)

    def test_common_categories(self) -> None:
        """Test suggestions for common category names."""
        test_cases = [
            ("Invoices", "Documents", ["invoice"]),
            ("Receipts", "Documents", ["receipt"]),
            ("Fiction", "Books", ["fiction", "novel"]),
            ("Research", "Papers", ["research"]),
            ("Music", "Audio", ["music"]),
            ("Photos", "Images", ["photo"]),
        ]

        for name, expected_parent, expected_keywords in test_cases:
            result = suggest_rules(name)
            assert result.parent == expected_parent, f"Failed for {name}"
            for kw in expected_keywords:
                assert kw in result.keywords, f"Missing '{kw}' for {name}"


class TestCategorySuggestions:
    """Tests for CATEGORY_SUGGESTIONS dictionary."""

    def test_has_programming_patterns(self) -> None:
        """Contains programming-related patterns."""
        assert "tech" in CATEGORY_SUGGESTIONS
        assert "programming" in CATEGORY_SUGGESTIONS
        assert "code" in CATEGORY_SUGGESTIONS

    def test_has_finance_patterns(self) -> None:
        """Contains finance-related patterns."""
        assert "invoice" in CATEGORY_SUGGESTIONS
        assert "receipt" in CATEGORY_SUGGESTIONS
        assert "finance" in CATEGORY_SUGGESTIONS

    def test_has_book_patterns(self) -> None:
        """Contains book-related patterns."""
        assert "book" in CATEGORY_SUGGESTIONS
        assert "fiction" in CATEGORY_SUGGESTIONS
        assert "nonfiction" in CATEGORY_SUGGESTIONS

    def test_has_media_patterns(self) -> None:
        """Contains media-related patterns."""
        assert "photo" in CATEGORY_SUGGESTIONS
        assert "video" in CATEGORY_SUGGESTIONS
        assert "music" in CATEGORY_SUGGESTIONS

    def test_has_work_patterns(self) -> None:
        """Contains work-related patterns."""
        assert "work" in CATEGORY_SUGGESTIONS
        assert "project" in CATEGORY_SUGGESTIONS
        assert "client" in CATEGORY_SUGGESTIONS

    def test_all_values_are_lists(self) -> None:
        """All values in dictionary are non-empty lists."""
        for key, value in CATEGORY_SUGGESTIONS.items():
            assert isinstance(value, list), f"Value for '{key}' is not a list"
            assert len(value) > 0, f"Value for '{key}' is empty"

    def test_minimum_pattern_count(self) -> None:
        """Dictionary has reasonable number of patterns."""
        # Should have at least 50 patterns as specified in backlog
        assert len(CATEGORY_SUGGESTIONS) >= 50


class TestParentInference:
    """Tests for PARENT_INFERENCE dictionary."""

    def test_has_book_subcategories(self) -> None:
        """Maps book-related names to Books."""
        assert PARENT_INFERENCE.get("fiction") == "Books"
        assert PARENT_INFERENCE.get("nonfiction") == "Books"
        assert PARENT_INFERENCE.get("novel") == "Books"

    def test_has_document_subcategories(self) -> None:
        """Maps document-related names to Documents."""
        assert PARENT_INFERENCE.get("invoice") == "Documents"
        assert PARENT_INFERENCE.get("receipt") == "Documents"
        assert PARENT_INFERENCE.get("contract") == "Documents"

    def test_has_media_subcategories(self) -> None:
        """Maps media-related names to appropriate parents."""
        assert PARENT_INFERENCE.get("photo") == "Images"
        assert PARENT_INFERENCE.get("movie") == "Videos"
        assert PARENT_INFERENCE.get("music") == "Audio"

    def test_has_paper_subcategories(self) -> None:
        """Maps academic names to Papers."""
        assert PARENT_INFERENCE.get("research") == "Papers"
        assert PARENT_INFERENCE.get("thesis") == "Papers"

    def test_all_values_are_valid_categories(self) -> None:
        """All parent values are valid default categories."""
        from tidyup.categories import DEFAULT_CATEGORIES

        valid_parents = set(DEFAULT_CATEGORIES) | {"Unsorted"}

        for pattern, parent in PARENT_INFERENCE.items():
            assert parent in valid_parents, f"Invalid parent '{parent}' for '{pattern}'"


class TestHelperFunctions:
    """Tests for helper functions."""

    def test_get_all_suggestion_patterns(self) -> None:
        """Returns sorted list of all patterns."""
        patterns = get_all_suggestion_patterns()
        assert len(patterns) > 0
        assert patterns == sorted(patterns)
        assert "tech" in patterns
        assert "invoice" in patterns

    def test_get_all_parent_patterns(self) -> None:
        """Returns sorted list of all parent patterns."""
        patterns = get_all_parent_patterns()
        assert len(patterns) > 0
        assert patterns == sorted(patterns)
        assert "fiction" in patterns
        assert "invoice" in patterns
