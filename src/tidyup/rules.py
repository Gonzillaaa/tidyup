"""Rules engine for category matching.

Provides keyword and pattern-based matching for subcategorization.
Rules are evaluated after detector runs, allowing fine-grained routing
of files to subcategories based on content and filename patterns.
"""

from dataclasses import dataclass, field
from fnmatch import fnmatch
from pathlib import Path


@dataclass
class CategoryRule:
    """Rule for matching files to a category.

    A rule can match by:
    - keywords: Words that appear in filename or content
    - patterns: Glob patterns for filename matching (e.g., "acme_*")
    - extensions: File extensions (without dot, e.g., "pdf")

    Attributes:
        keywords: List of keywords to search for in filename/content.
        patterns: List of glob patterns to match against filename.
        extensions: List of file extensions (without leading dot).
        min_keyword_matches: Minimum keywords required for match (default 1).
    """

    keywords: list[str] = field(default_factory=list)
    patterns: list[str] = field(default_factory=list)
    extensions: list[str] = field(default_factory=list)
    min_keyword_matches: int = 1

    def matches(
        self,
        filename: str,
        extension: str,
        content: str | None = None,
    ) -> bool:
        """Check if this rule matches the given file.

        Args:
            filename: The filename (without path).
            extension: The file extension (without dot).
            content: Optional file content text for keyword matching.

        Returns:
            True if the rule matches, False otherwise.
        """
        # Check extension match
        if self.extensions:
            if extension.lower() in [e.lower() for e in self.extensions]:
                return True

        # Check pattern match
        for pattern in self.patterns:
            if fnmatch(filename.lower(), pattern.lower()):
                return True

        # Check keyword match
        if self.keywords:
            # Build text to search (filename + content)
            text = filename.lower()
            if content:
                text += " " + content.lower()

            # Count keyword matches
            matches = sum(1 for kw in self.keywords if kw.lower() in text)
            if matches >= self.min_keyword_matches:
                return True

        return False

    def to_dict(self) -> dict:
        """Convert rule to dictionary for config serialization."""
        result: dict = {}
        if self.keywords:
            result["keywords"] = self.keywords
        if self.patterns:
            result["patterns"] = self.patterns
        if self.extensions:
            result["extensions"] = self.extensions
        if self.min_keyword_matches != 1:
            result["min_keyword_matches"] = self.min_keyword_matches
        return result

    @classmethod
    def from_dict(cls, data: dict) -> "CategoryRule":
        """Create rule from dictionary (config deserialization)."""
        return cls(
            keywords=data.get("keywords", []),
            patterns=data.get("patterns", []),
            extensions=data.get("extensions", []),
            min_keyword_matches=data.get("min_keyword_matches", 1),
        )


class RulesEngine:
    """Engine for evaluating category rules.

    Evaluates rules to determine if a file should be routed to
    a subcategory instead of the detector's original category.
    """

    def __init__(self) -> None:
        """Initialize the rules engine."""
        self._content_cache: dict[Path, str | None] = {}

    def evaluate(
        self,
        filename: str,
        extension: str,
        parent_category: str,
        categories: list[tuple[str, str | None, "CategoryRule | None"]],
        content: str | None = None,
    ) -> str | None:
        """Evaluate rules to find matching subcategory.

        Args:
            filename: The filename to match.
            extension: File extension (without dot).
            parent_category: The original category from detector.
            categories: List of (name, parent, rule) tuples to evaluate.
            content: Optional file content for keyword matching.

        Returns:
            Name of matching subcategory, or None if no match.
        """
        # Find subcategories of the parent
        for name, parent, rule in categories:
            if parent and parent.lower() == parent_category.lower():
                if rule and rule.matches(filename, extension, content):
                    return name

        return None

    def clear_cache(self) -> None:
        """Clear the content cache."""
        self._content_cache.clear()
