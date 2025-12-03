"""Category management for TidyUp.

Provides dynamic category configuration that can be stored in config
and modified via CLI commands.
"""

from dataclasses import dataclass, field
from pathlib import Path

import yaml

# Default categories in order (position determines number)
DEFAULT_CATEGORIES = [
    "Documents",
    "Screenshots",
    "Images",
    "Videos",
    "Audio",
    "Archives",
    "Code",
    "Books",
    "Papers",
    "Data",
    "Installers",
]

# Unsorted is always last at 99
UNSORTED_CATEGORY = "Unsorted"
UNSORTED_NUMBER = 99


@dataclass
class Category:
    """A file category with number and name.

    Attributes:
        number: The category number (01-98, or 99 for Unsorted).
        name: The display name of the category.
    """

    number: int
    name: str

    @property
    def folder_name(self) -> str:
        """Return the folder name in NN_Name format."""
        return f"{self.number:02d}_{self.name}"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Category):
            return self.name == other.name
        return False

    def __hash__(self) -> int:
        return hash(self.name)


@dataclass
class CategoryManager:
    """Manages file categories with config persistence.

    Categories are stored as a simple list in config, where position
    determines the number (first = 01, second = 02, etc.).

    Attributes:
        categories: List of Category objects.
        config_path: Path to config file.
    """

    categories: list[Category] = field(default_factory=list)
    config_path: Path | None = None

    def __post_init__(self) -> None:
        """Set default config path if not provided."""
        if self.config_path is None:
            self.config_path = Path.home() / ".tidy" / "config.yaml"

    def load(self) -> None:
        """Load categories from config file or use defaults.

        If config file doesn't exist or has no categories section,
        uses DEFAULT_CATEGORIES.
        """
        category_names = DEFAULT_CATEGORIES.copy()

        if self.config_path and self.config_path.exists():
            try:
                with open(self.config_path) as f:
                    config = yaml.safe_load(f) or {}

                if "categories" in config and config["categories"]:
                    # Extract names from config (can be strings or dicts)
                    category_names = []
                    for item in config["categories"]:
                        if isinstance(item, str):
                            category_names.append(item)
                        elif isinstance(item, dict) and "name" in item:
                            category_names.append(item["name"])
            except (yaml.YAMLError, OSError):
                # Fall back to defaults on any error
                category_names = DEFAULT_CATEGORIES.copy()

        # Build categories with numbers
        self.categories = []
        for i, name in enumerate(category_names, start=1):
            self.categories.append(Category(number=i, name=name))

        # Always add Unsorted at 99
        self.categories.append(Category(number=UNSORTED_NUMBER, name=UNSORTED_CATEGORY))

    def save(self) -> None:
        """Save categories to config file.

        Creates config directory if it doesn't exist.
        Preserves other config sections.
        """
        if not self.config_path:
            return

        # Ensure directory exists
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        # Load existing config to preserve other sections
        config: dict = {}
        if self.config_path.exists():
            try:
                with open(self.config_path) as f:
                    config = yaml.safe_load(f) or {}
            except (yaml.YAMLError, OSError):
                config = {}

        # Update categories section (exclude Unsorted, it's implicit)
        config["categories"] = [
            cat.name for cat in self.categories if cat.name != UNSORTED_CATEGORY
        ]

        # Write config
        with open(self.config_path, "w") as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)

    def get_by_name(self, name: str) -> Category | None:
        """Get category by name (case-insensitive).

        Args:
            name: Category name to look up.

        Returns:
            Category if found, None otherwise.
        """
        name_lower = name.lower()
        for cat in self.categories:
            if cat.name.lower() == name_lower:
                return cat
        return None

    def get_folder_name(self, name: str) -> str:
        """Get folder name for a category.

        Args:
            name: Category name.

        Returns:
            Folder name in NN_Name format.

        Raises:
            ValueError: If category not found.
        """
        cat = self.get_by_name(name)
        if cat is None:
            raise ValueError(f"Unknown category: {name}")
        return cat.folder_name

    def add(self, name: str, position: int | None = None) -> Category:
        """Add a new category at the specified position.

        Args:
            name: Name of the new category.
            position: Position (1-based). None means append at end.

        Returns:
            The newly created Category.

        Raises:
            ValueError: If category already exists or position invalid.
        """
        # Check for duplicates
        if self.get_by_name(name) is not None:
            raise ValueError(f"Category already exists: {name}")

        # Filter out Unsorted for positioning
        regular_cats = [c for c in self.categories if c.name != UNSORTED_CATEGORY]

        # Determine position
        if position is None:
            position = len(regular_cats) + 1
        elif position < 1 or position > len(regular_cats) + 1:
            raise ValueError(
                f"Position must be between 1 and {len(regular_cats) + 1}"
            )

        # Insert at position (convert to 0-based index)
        new_cat = Category(number=position, name=name)
        regular_cats.insert(position - 1, new_cat)

        # Renumber all categories
        self.categories = []
        for i, cat in enumerate(regular_cats, start=1):
            self.categories.append(Category(number=i, name=cat.name))

        # Add back Unsorted
        self.categories.append(Category(number=UNSORTED_NUMBER, name=UNSORTED_CATEGORY))

        return self.get_by_name(name)  # type: ignore

    def remove(self, name: str) -> None:
        """Remove a category.

        Args:
            name: Name of the category to remove.

        Raises:
            ValueError: If category not found or is Unsorted.
        """
        if name.lower() == UNSORTED_CATEGORY.lower():
            raise ValueError("Cannot remove Unsorted category")

        cat = self.get_by_name(name)
        if cat is None:
            raise ValueError(f"Category not found: {name}")

        # Filter out the category and Unsorted
        regular_cats = [
            c for c in self.categories
            if c.name != name and c.name != UNSORTED_CATEGORY
        ]

        # Renumber remaining categories
        self.categories = []
        for i, cat in enumerate(regular_cats, start=1):
            self.categories.append(Category(number=i, name=cat.name))

        # Add back Unsorted
        self.categories.append(Category(number=UNSORTED_NUMBER, name=UNSORTED_CATEGORY))

    def reorder(self, new_order: list[str]) -> None:
        """Reorder categories according to the given name list.

        Args:
            new_order: List of category names in desired order.

        Raises:
            ValueError: If names don't match existing categories.
        """
        # Get current regular categories
        regular_cats = {
            c.name.lower(): c.name
            for c in self.categories
            if c.name != UNSORTED_CATEGORY
        }

        # Validate new order
        new_order_lower = [n.lower() for n in new_order]

        if set(new_order_lower) != set(regular_cats.keys()):
            missing = set(regular_cats.keys()) - set(new_order_lower)
            extra = set(new_order_lower) - set(regular_cats.keys())
            msg = []
            if missing:
                msg.append(f"Missing: {', '.join(regular_cats[m] for m in missing)}")
            if extra:
                msg.append(f"Unknown: {', '.join(extra)}")
            raise ValueError("; ".join(msg))

        # Rebuild with new order
        self.categories = []
        for i, name_lower in enumerate(new_order_lower, start=1):
            original_name = regular_cats[name_lower]
            self.categories.append(Category(number=i, name=original_name))

        # Add back Unsorted
        self.categories.append(Category(number=UNSORTED_NUMBER, name=UNSORTED_CATEGORY))

    def apply_to_filesystem(
        self,
        dest: Path,
        dry_run: bool = False,
    ) -> list[tuple[Path, Path]]:
        """Rename existing folders to match current category numbering.

        This handles the case where category order has changed and
        existing folders need to be renamed.

        Args:
            dest: Destination directory containing category folders.
            dry_run: If True, return what would be renamed without doing it.

        Returns:
            List of (old_path, new_path) tuples for renamed folders.
        """
        if not dest.exists():
            return []

        renames: list[tuple[Path, Path]] = []

        # Build mapping of name -> expected folder name
        expected = {cat.name.lower(): cat.folder_name for cat in self.categories}

        # Find existing category folders
        for item in dest.iterdir():
            if not item.is_dir():
                continue

            # Parse folder name (NN_Name format)
            parts = item.name.split("_", 1)
            if len(parts) != 2:
                continue

            try:
                int(parts[0])  # Validate number prefix
            except ValueError:
                continue

            folder_name = parts[1]
            folder_name_lower = folder_name.lower()

            # Check if this category exists and needs renaming
            if folder_name_lower in expected:
                expected_name = expected[folder_name_lower]
                if item.name != expected_name:
                    new_path = dest / expected_name
                    renames.append((item, new_path))

        # Sort renames to avoid conflicts (rename to temp first if needed)
        # For now, simple approach: rename in reverse number order
        renames.sort(key=lambda x: x[0].name, reverse=True)

        if not dry_run:
            # Execute renames (may need temp names to avoid conflicts)
            for old_path, new_path in renames:
                if new_path.exists():
                    # Use temp name to avoid conflict
                    temp_path = dest / f"_temp_{old_path.name}"
                    old_path.rename(temp_path)
                    # Will be renamed properly in second pass
                else:
                    old_path.rename(new_path)

        return renames

    def list_categories(self) -> list[Category]:
        """Return all categories in order.

        Returns:
            List of Category objects.
        """
        return self.categories.copy()

    def get_default_folders(self) -> list[dict]:
        """Return categories in the legacy DEFAULT_FOLDERS format.

        This provides backwards compatibility with existing code
        that expects the old format.

        Returns:
            List of dicts with 'number' and 'name' keys.
        """
        return [{"number": cat.number, "name": cat.name} for cat in self.categories]


# Global instance
_manager: CategoryManager | None = None


def get_category_manager() -> CategoryManager:
    """Get the global CategoryManager instance.

    Creates and loads from config if not already initialized.

    Returns:
        The global CategoryManager.
    """
    global _manager
    if _manager is None:
        _manager = CategoryManager()
        _manager.load()
    return _manager


def reset_category_manager() -> None:
    """Reset the global CategoryManager (for testing)."""
    global _manager
    _manager = None
