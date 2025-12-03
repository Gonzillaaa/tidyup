"""Tests for category management."""

import pytest
from pathlib import Path

from tidyup.categories import (
    Category,
    CategoryManager,
    DEFAULT_CATEGORIES,
    UNSORTED_CATEGORY,
    UNSORTED_NUMBER,
    get_category_manager,
    reset_category_manager,
)


class TestCategory:
    """Tests for Category dataclass."""

    def test_folder_name_single_digit(self) -> None:
        """Formats single digit numbers with leading zero."""
        cat = Category(number=1, name="Documents")
        assert cat.folder_name == "01_Documents"

    def test_folder_name_double_digit(self) -> None:
        """Formats double digit numbers correctly."""
        cat = Category(number=11, name="Installers")
        assert cat.folder_name == "11_Installers"

    def test_folder_name_unsorted(self) -> None:
        """Formats Unsorted category correctly."""
        cat = Category(number=99, name="Unsorted")
        assert cat.folder_name == "99_Unsorted"

    def test_equality_by_name(self) -> None:
        """Categories are equal if names match."""
        cat1 = Category(number=1, name="Documents")
        cat2 = Category(number=5, name="Documents")
        assert cat1 == cat2

    def test_inequality_different_names(self) -> None:
        """Categories with different names are not equal."""
        cat1 = Category(number=1, name="Documents")
        cat2 = Category(number=1, name="Images")
        assert cat1 != cat2


class TestCategoryManagerLoad:
    """Tests for CategoryManager loading."""

    def test_load_defaults_no_config(self, tmp_path: Path) -> None:
        """Loads default categories when no config exists."""
        manager = CategoryManager(config_path=tmp_path / "config.yaml")
        manager.load()

        names = [c.name for c in manager.categories]
        assert names[:-1] == DEFAULT_CATEGORIES
        assert names[-1] == UNSORTED_CATEGORY

    def test_load_defaults_correct_numbers(self, tmp_path: Path) -> None:
        """Default categories have sequential numbers."""
        manager = CategoryManager(config_path=tmp_path / "config.yaml")
        manager.load()

        for i, cat in enumerate(manager.categories[:-1], start=1):
            assert cat.number == i

        assert manager.categories[-1].number == UNSORTED_NUMBER

    def test_load_from_config(self, tmp_path: Path) -> None:
        """Loads categories from config file."""
        config_path = tmp_path / "config.yaml"
        config_path.write_text("categories:\n  - Foo\n  - Bar\n  - Baz\n")

        manager = CategoryManager(config_path=config_path)
        manager.load()

        names = [c.name for c in manager.categories]
        assert names == ["Foo", "Bar", "Baz", "Unsorted"]

    def test_load_from_config_dict_format(self, tmp_path: Path) -> None:
        """Loads categories from config with dict format."""
        config_path = tmp_path / "config.yaml"
        config_path.write_text(
            "categories:\n  - name: Foo\n  - name: Bar\n"
        )

        manager = CategoryManager(config_path=config_path)
        manager.load()

        names = [c.name for c in manager.categories]
        assert names == ["Foo", "Bar", "Unsorted"]

    def test_load_preserves_unsorted(self, tmp_path: Path) -> None:
        """Always includes Unsorted at 99 even if in config."""
        config_path = tmp_path / "config.yaml"
        config_path.write_text("categories:\n  - Foo\n  - Unsorted\n  - Bar\n")

        manager = CategoryManager(config_path=config_path)
        manager.load()

        # Unsorted should be at the end with number 99
        assert manager.categories[-1].name == "Unsorted"
        assert manager.categories[-1].number == 99


class TestCategoryManagerSave:
    """Tests for CategoryManager saving."""

    def test_save_creates_directory(self, tmp_path: Path) -> None:
        """Creates config directory if it doesn't exist."""
        config_path = tmp_path / "subdir" / "config.yaml"
        manager = CategoryManager(config_path=config_path)
        manager.load()
        manager.save()

        assert config_path.exists()

    def test_save_writes_categories(self, tmp_path: Path) -> None:
        """Saves categories to config file."""
        config_path = tmp_path / "config.yaml"
        manager = CategoryManager(config_path=config_path)
        manager.load()
        manager.save()

        content = config_path.read_text()
        assert "Documents" in content
        assert "Images" in content

    def test_save_excludes_unsorted(self, tmp_path: Path) -> None:
        """Does not save Unsorted category (it's implicit)."""
        config_path = tmp_path / "config.yaml"
        manager = CategoryManager(config_path=config_path)
        manager.load()
        manager.save()

        content = config_path.read_text()
        assert "Unsorted" not in content

    def test_save_preserves_other_config(self, tmp_path: Path) -> None:
        """Preserves other config sections when saving."""
        config_path = tmp_path / "config.yaml"
        config_path.write_text("other_setting: value\ncategories:\n  - Old\n")

        manager = CategoryManager(config_path=config_path)
        manager.load()
        manager.save()

        content = config_path.read_text()
        assert "other_setting: value" in content


class TestCategoryManagerLookup:
    """Tests for CategoryManager lookups."""

    def test_get_by_name_found(self, tmp_path: Path) -> None:
        """Finds category by exact name."""
        manager = CategoryManager(config_path=tmp_path / "config.yaml")
        manager.load()

        cat = manager.get_by_name("Documents")
        assert cat is not None
        assert cat.name == "Documents"

    def test_get_by_name_case_insensitive(self, tmp_path: Path) -> None:
        """Finds category regardless of case."""
        manager = CategoryManager(config_path=tmp_path / "config.yaml")
        manager.load()

        cat = manager.get_by_name("DOCUMENTS")
        assert cat is not None
        assert cat.name == "Documents"

    def test_get_by_name_not_found(self, tmp_path: Path) -> None:
        """Returns None for unknown category."""
        manager = CategoryManager(config_path=tmp_path / "config.yaml")
        manager.load()

        cat = manager.get_by_name("NonExistent")
        assert cat is None

    def test_get_folder_name(self, tmp_path: Path) -> None:
        """Returns folder name for category."""
        manager = CategoryManager(config_path=tmp_path / "config.yaml")
        manager.load()

        folder = manager.get_folder_name("Documents")
        assert folder == "01_Documents"

    def test_get_folder_name_unknown_raises(self, tmp_path: Path) -> None:
        """Raises ValueError for unknown category."""
        manager = CategoryManager(config_path=tmp_path / "config.yaml")
        manager.load()

        with pytest.raises(ValueError, match="Unknown category"):
            manager.get_folder_name("NonExistent")


class TestCategoryManagerAdd:
    """Tests for adding categories."""

    def test_add_at_end(self, tmp_path: Path) -> None:
        """Adds category at end when no position specified."""
        config_path = tmp_path / "config.yaml"
        config_path.write_text("categories:\n  - Foo\n  - Bar\n")

        manager = CategoryManager(config_path=config_path)
        manager.load()
        manager.add("Baz")

        names = [c.name for c in manager.categories if c.name != "Unsorted"]
        assert names == ["Foo", "Bar", "Baz"]

    def test_add_at_position(self, tmp_path: Path) -> None:
        """Adds category at specified position."""
        config_path = tmp_path / "config.yaml"
        config_path.write_text("categories:\n  - Foo\n  - Bar\n")

        manager = CategoryManager(config_path=config_path)
        manager.load()
        manager.add("Baz", position=2)

        names = [c.name for c in manager.categories if c.name != "Unsorted"]
        assert names == ["Foo", "Baz", "Bar"]

    def test_add_renumbers_existing(self, tmp_path: Path) -> None:
        """Renumbers existing categories after insert."""
        config_path = tmp_path / "config.yaml"
        config_path.write_text("categories:\n  - Foo\n  - Bar\n")

        manager = CategoryManager(config_path=config_path)
        manager.load()
        manager.add("Baz", position=1)

        numbers = [c.number for c in manager.categories if c.name != "Unsorted"]
        assert numbers == [1, 2, 3]

        names = [c.name for c in manager.categories if c.name != "Unsorted"]
        assert names == ["Baz", "Foo", "Bar"]

    def test_add_duplicate_raises(self, tmp_path: Path) -> None:
        """Raises ValueError when adding duplicate."""
        manager = CategoryManager(config_path=tmp_path / "config.yaml")
        manager.load()

        with pytest.raises(ValueError, match="already exists"):
            manager.add("Documents")

    def test_add_invalid_position_raises(self, tmp_path: Path) -> None:
        """Raises ValueError for invalid position."""
        config_path = tmp_path / "config.yaml"
        config_path.write_text("categories:\n  - Foo\n")

        manager = CategoryManager(config_path=config_path)
        manager.load()

        with pytest.raises(ValueError, match="Position must be"):
            manager.add("Bar", position=10)

    def test_add_normalizes_name_lowercase(self, tmp_path: Path) -> None:
        """Normalizes lowercase input to Title Case."""
        config_path = tmp_path / "config.yaml"
        config_path.write_text("categories:\n  - Foo\n")

        manager = CategoryManager(config_path=config_path)
        manager.load()
        cat = manager.add("invoices")

        assert cat.name == "Invoices"
        assert cat.folder_name == "02_Invoices"

    def test_add_normalizes_name_uppercase(self, tmp_path: Path) -> None:
        """Normalizes uppercase input to Title Case."""
        config_path = tmp_path / "config.yaml"
        config_path.write_text("categories:\n  - Foo\n")

        manager = CategoryManager(config_path=config_path)
        manager.load()
        cat = manager.add("PDF")

        assert cat.name == "Pdf"

    def test_add_normalizes_name_mixed(self, tmp_path: Path) -> None:
        """Normalizes mixed case input to Title Case."""
        config_path = tmp_path / "config.yaml"
        config_path.write_text("categories:\n  - Foo\n")

        manager = CategoryManager(config_path=config_path)
        manager.load()
        cat = manager.add("myCategory")

        assert cat.name == "Mycategory"


class TestCategoryManagerRemove:
    """Tests for removing categories."""

    def test_remove_category(self, tmp_path: Path) -> None:
        """Removes category by name."""
        config_path = tmp_path / "config.yaml"
        config_path.write_text("categories:\n  - Foo\n  - Bar\n  - Baz\n")

        manager = CategoryManager(config_path=config_path)
        manager.load()
        manager.remove("Bar")

        names = [c.name for c in manager.categories if c.name != "Unsorted"]
        assert names == ["Foo", "Baz"]

    def test_remove_renumbers(self, tmp_path: Path) -> None:
        """Renumbers remaining categories after removal."""
        config_path = tmp_path / "config.yaml"
        config_path.write_text("categories:\n  - Foo\n  - Bar\n  - Baz\n")

        manager = CategoryManager(config_path=config_path)
        manager.load()
        manager.remove("Foo")

        numbers = [c.number for c in manager.categories if c.name != "Unsorted"]
        assert numbers == [1, 2]

    def test_remove_unsorted_raises(self, tmp_path: Path) -> None:
        """Raises ValueError when trying to remove Unsorted."""
        manager = CategoryManager(config_path=tmp_path / "config.yaml")
        manager.load()

        with pytest.raises(ValueError, match="Cannot remove Unsorted"):
            manager.remove("Unsorted")

    def test_remove_unknown_raises(self, tmp_path: Path) -> None:
        """Raises ValueError for unknown category."""
        manager = CategoryManager(config_path=tmp_path / "config.yaml")
        manager.load()

        with pytest.raises(ValueError, match="not found"):
            manager.remove("NonExistent")

    def test_remove_case_insensitive(self, tmp_path: Path) -> None:
        """Removes category regardless of case in user input."""
        config_path = tmp_path / "config.yaml"
        config_path.write_text("categories:\n  - Invoices\n  - Documents\n")

        manager = CategoryManager(config_path=config_path)
        manager.load()

        # Remove with different case than stored
        manager.remove("invoices")  # lowercase, stored as "Invoices"

        names = [c.name for c in manager.categories if c.name != "Unsorted"]
        assert "Invoices" not in names
        assert names == ["Documents"]

    def test_remove_case_insensitive_uppercase(self, tmp_path: Path) -> None:
        """Removes category when user provides uppercase variant."""
        config_path = tmp_path / "config.yaml"
        config_path.write_text("categories:\n  - invoices\n  - Documents\n")

        manager = CategoryManager(config_path=config_path)
        manager.load()

        # Remove with uppercase when stored as lowercase
        manager.remove("INVOICES")

        names = [c.name for c in manager.categories if c.name != "Unsorted"]
        assert "invoices" not in names
        assert names == ["Documents"]


class TestCategoryManagerReorder:
    """Tests for reordering categories."""

    def test_reorder_categories(self, tmp_path: Path) -> None:
        """Reorders categories according to list."""
        config_path = tmp_path / "config.yaml"
        config_path.write_text("categories:\n  - Foo\n  - Bar\n  - Baz\n")

        manager = CategoryManager(config_path=config_path)
        manager.load()
        manager.reorder(["Baz", "Foo", "Bar"])

        names = [c.name for c in manager.categories if c.name != "Unsorted"]
        assert names == ["Baz", "Foo", "Bar"]

    def test_reorder_updates_numbers(self, tmp_path: Path) -> None:
        """Updates numbers after reorder."""
        config_path = tmp_path / "config.yaml"
        config_path.write_text("categories:\n  - Foo\n  - Bar\n  - Baz\n")

        manager = CategoryManager(config_path=config_path)
        manager.load()
        manager.reorder(["Baz", "Foo", "Bar"])

        baz = manager.get_by_name("Baz")
        foo = manager.get_by_name("Foo")
        bar = manager.get_by_name("Bar")

        assert baz.number == 1
        assert foo.number == 2
        assert bar.number == 3

    def test_reorder_case_insensitive(self, tmp_path: Path) -> None:
        """Reorder handles case differences."""
        config_path = tmp_path / "config.yaml"
        config_path.write_text("categories:\n  - Foo\n  - Bar\n")

        manager = CategoryManager(config_path=config_path)
        manager.load()
        manager.reorder(["BAR", "FOO"])

        names = [c.name for c in manager.categories if c.name != "Unsorted"]
        assert names == ["Bar", "Foo"]

    def test_reorder_missing_raises(self, tmp_path: Path) -> None:
        """Raises ValueError when categories missing from new order."""
        config_path = tmp_path / "config.yaml"
        config_path.write_text("categories:\n  - Foo\n  - Bar\n")

        manager = CategoryManager(config_path=config_path)
        manager.load()

        with pytest.raises(ValueError, match="Missing"):
            manager.reorder(["Foo"])

    def test_reorder_unknown_raises(self, tmp_path: Path) -> None:
        """Raises ValueError for unknown categories in new order."""
        config_path = tmp_path / "config.yaml"
        config_path.write_text("categories:\n  - Foo\n  - Bar\n")

        manager = CategoryManager(config_path=config_path)
        manager.load()

        with pytest.raises(ValueError, match="Unknown"):
            manager.reorder(["Foo", "Baz"])


class TestCategoryManagerFilesystem:
    """Tests for filesystem operations."""

    def test_apply_renames_folders(self, tmp_path: Path) -> None:
        """Renames existing folders to match new numbering."""
        # Create folders with old numbering
        (tmp_path / "01_Foo").mkdir()
        (tmp_path / "02_Bar").mkdir()

        # Create manager with different order
        config_path = tmp_path / "config.yaml"
        config_path.write_text("categories:\n  - Bar\n  - Foo\n")

        manager = CategoryManager(config_path=config_path)
        manager.load()

        renames = manager.apply_to_filesystem(tmp_path)

        assert len(renames) == 2
        assert (tmp_path / "01_Bar").exists()
        assert (tmp_path / "02_Foo").exists()

    def test_apply_dry_run(self, tmp_path: Path) -> None:
        """Dry run returns renames without executing."""
        (tmp_path / "01_Foo").mkdir()
        (tmp_path / "02_Bar").mkdir()

        config_path = tmp_path / "config.yaml"
        config_path.write_text("categories:\n  - Bar\n  - Foo\n")

        manager = CategoryManager(config_path=config_path)
        manager.load()

        renames = manager.apply_to_filesystem(tmp_path, dry_run=True)

        assert len(renames) == 2
        # Original folders should still exist
        assert (tmp_path / "01_Foo").exists()
        assert (tmp_path / "02_Bar").exists()

    def test_apply_ignores_non_category_folders(self, tmp_path: Path) -> None:
        """Ignores folders that don't match category pattern."""
        (tmp_path / "random_folder").mkdir()
        (tmp_path / "01_Documents").mkdir()

        manager = CategoryManager(config_path=tmp_path / "config.yaml")
        manager.load()

        renames = manager.apply_to_filesystem(tmp_path)

        # Should not rename random_folder
        assert (tmp_path / "random_folder").exists()


class TestCategoryManagerLegacy:
    """Tests for legacy compatibility."""

    def test_get_default_folders_format(self, tmp_path: Path) -> None:
        """Returns categories in legacy format."""
        manager = CategoryManager(config_path=tmp_path / "config.yaml")
        manager.load()

        folders = manager.get_default_folders()

        assert isinstance(folders, list)
        assert all("number" in f and "name" in f for f in folders)
        assert folders[0] == {"number": 1, "name": "Documents"}


class TestGlobalManager:
    """Tests for global manager functions."""

    def test_get_category_manager_singleton(self) -> None:
        """Returns same instance on multiple calls."""
        reset_category_manager()

        m1 = get_category_manager()
        m2 = get_category_manager()

        assert m1 is m2

        reset_category_manager()

    def test_reset_clears_instance(self) -> None:
        """Reset clears the global instance."""
        m1 = get_category_manager()
        reset_category_manager()
        m2 = get_category_manager()

        assert m1 is not m2

        reset_category_manager()
