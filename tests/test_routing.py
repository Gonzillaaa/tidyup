"""Tests for category routing functionality."""

from pathlib import Path

from tidyup.categories import (
    CategoryManager,
    RoutingConfig,
    get_category_manager,
    reset_category_manager,
)


class TestRoutingConfig:
    """Tests for RoutingConfig dataclass."""

    def test_apply_remap_no_rules(self) -> None:
        """Returns original category when no rules defined."""
        routing = RoutingConfig()
        result = routing.apply_remap("TestDetector", "Documents")
        assert result == "Documents"

    def test_apply_remap_global(self) -> None:
        """Applies global remap rule."""
        routing = RoutingConfig(remap={"Documents": "PDF"})
        result = routing.apply_remap("TestDetector", "Documents")
        assert result == "PDF"

    def test_apply_remap_detector_specific(self) -> None:
        """Applies detector-specific remap rule."""
        routing = RoutingConfig(
            remap={"InvoiceDetector": {"Documents": "Invoices"}}
        )
        result = routing.apply_remap("InvoiceDetector", "Documents")
        assert result == "Invoices"

    def test_apply_remap_detector_specific_precedence(self) -> None:
        """Detector-specific rules take precedence over global."""
        routing = RoutingConfig(
            remap={
                "Documents": "PDF",  # Global
                "InvoiceDetector": {"Documents": "Invoices"},  # Specific
            }
        )
        # Detector-specific should win
        result = routing.apply_remap("InvoiceDetector", "Documents")
        assert result == "Invoices"

        # Other detectors should use global
        result = routing.apply_remap("GenericDetector", "Documents")
        assert result == "PDF"

    def test_apply_remap_no_match(self) -> None:
        """Returns original if category not in remap."""
        routing = RoutingConfig(remap={"Books": "Library"})
        result = routing.apply_remap("TestDetector", "Documents")
        assert result == "Documents"

    def test_set_remap_global(self) -> None:
        """Sets global remap rule."""
        routing = RoutingConfig()
        routing.set_remap("Documents", "PDF")
        assert routing.remap == {"Documents": "PDF"}

    def test_set_remap_detector_specific(self) -> None:
        """Sets detector-specific remap rule."""
        routing = RoutingConfig()
        routing.set_remap("Documents", "Invoices", detector_name="InvoiceDetector")
        assert routing.remap == {"InvoiceDetector": {"Documents": "Invoices"}}

    def test_set_remap_multiple(self) -> None:
        """Can set multiple remap rules."""
        routing = RoutingConfig()
        routing.set_remap("Documents", "PDF")
        routing.set_remap("Documents", "Invoices", detector_name="InvoiceDetector")
        routing.set_remap("Books", "Library")

        assert routing.remap == {
            "Documents": "PDF",
            "InvoiceDetector": {"Documents": "Invoices"},
            "Books": "Library",
        }

    def test_remove_remap_global(self) -> None:
        """Removes global remap rule."""
        routing = RoutingConfig(remap={"Documents": "PDF", "Books": "Library"})
        result = routing.remove_remap("Documents")
        assert result is True
        assert routing.remap == {"Books": "Library"}

    def test_remove_remap_detector_specific(self) -> None:
        """Removes detector-specific remap rule."""
        routing = RoutingConfig(
            remap={"InvoiceDetector": {"Documents": "Invoices", "Books": "Archive"}}
        )
        result = routing.remove_remap("Documents", detector_name="InvoiceDetector")
        assert result is True
        assert routing.remap == {"InvoiceDetector": {"Books": "Archive"}}

    def test_remove_remap_cleans_empty_detector(self) -> None:
        """Removes empty detector dict after last rule removed."""
        routing = RoutingConfig(
            remap={"InvoiceDetector": {"Documents": "Invoices"}}
        )
        result = routing.remove_remap("Documents", detector_name="InvoiceDetector")
        assert result is True
        assert routing.remap == {}

    def test_remove_remap_not_found(self) -> None:
        """Returns False if rule not found."""
        routing = RoutingConfig(remap={"Books": "Library"})
        result = routing.remove_remap("Documents")
        assert result is False
        assert routing.remap == {"Books": "Library"}

    def test_list_remaps_empty(self) -> None:
        """Returns empty list when no rules."""
        routing = RoutingConfig()
        assert routing.list_remaps() == []

    def test_list_remaps_global(self) -> None:
        """Lists global remap rules."""
        routing = RoutingConfig(remap={"Documents": "PDF"})
        remaps = routing.list_remaps()
        assert remaps == [{"detector": "*", "from": "Documents", "to": "PDF"}]

    def test_list_remaps_detector_specific(self) -> None:
        """Lists detector-specific remap rules."""
        routing = RoutingConfig(
            remap={"InvoiceDetector": {"Documents": "Invoices"}}
        )
        remaps = routing.list_remaps()
        assert remaps == [
            {"detector": "InvoiceDetector", "from": "Documents", "to": "Invoices"}
        ]

    def test_list_remaps_mixed(self) -> None:
        """Lists both global and detector-specific rules."""
        routing = RoutingConfig(
            remap={
                "Books": "Library",
                "InvoiceDetector": {"Documents": "Invoices"},
            }
        )
        remaps = routing.list_remaps()
        # Order may vary, so check both are present
        assert len(remaps) == 2
        assert {"detector": "*", "from": "Books", "to": "Library"} in remaps
        assert {
            "detector": "InvoiceDetector",
            "from": "Documents",
            "to": "Invoices",
        } in remaps


class TestCategoryManagerRouting:
    """Tests for CategoryManager routing integration."""

    def test_load_routing_empty(self, tmp_path: Path) -> None:
        """Routing is empty when no config."""
        manager = CategoryManager(config_path=tmp_path / "config.yaml")
        manager.load()
        assert manager.routing.remap == {}

    def test_load_routing_from_config(self, tmp_path: Path) -> None:
        """Loads routing from config file."""
        config_path = tmp_path / "config.yaml"
        config_path.write_text(
            "categories:\n  - Documents\n  - Invoices\n"
            "routing:\n  remap:\n    InvoiceDetector:\n      Documents: Invoices\n"
        )

        manager = CategoryManager(config_path=config_path)
        manager.load()

        assert manager.routing.remap == {
            "InvoiceDetector": {"Documents": "Invoices"}
        }

    def test_save_routing(self, tmp_path: Path) -> None:
        """Saves routing to config file."""
        config_path = tmp_path / "config.yaml"
        manager = CategoryManager(config_path=config_path)
        manager.load()

        manager.routing.set_remap("Documents", "Invoices", "InvoiceDetector")
        manager.save()

        # Read back and verify
        content = config_path.read_text()
        assert "routing:" in content
        assert "InvoiceDetector:" in content

    def test_save_routing_removes_empty(self, tmp_path: Path) -> None:
        """Removes routing section if empty."""
        config_path = tmp_path / "config.yaml"
        config_path.write_text(
            "categories:\n  - Documents\n"
            "routing:\n  remap:\n    Documents: PDF\n"
        )

        manager = CategoryManager(config_path=config_path)
        manager.load()
        manager.routing.remove_remap("Documents")
        manager.save()

        content = config_path.read_text()
        assert "routing:" not in content

    def test_resolve_category_no_remap(self, tmp_path: Path) -> None:
        """Returns original category when no remap."""
        manager = CategoryManager(config_path=tmp_path / "config.yaml")
        manager.load()

        result = manager.resolve_category("Documents", "TestDetector")
        assert result == "Documents"

    def test_resolve_category_with_remap(self, tmp_path: Path) -> None:
        """Applies remap when resolving category."""
        manager = CategoryManager(config_path=tmp_path / "config.yaml")
        manager.load()
        manager.routing.set_remap("Documents", "Invoices", "InvoiceDetector")

        result = manager.resolve_category("Documents", "InvoiceDetector")
        assert result == "Invoices"

        # Other detectors not affected
        result = manager.resolve_category("Documents", "GenericDetector")
        assert result == "Documents"

    def test_get_folder_for_detection_no_remap(self, tmp_path: Path) -> None:
        """Returns correct folder without remap."""
        manager = CategoryManager(config_path=tmp_path / "config.yaml")
        manager.load()

        folder = manager.get_folder_for_detection("Documents", "TestDetector")
        assert folder == "01_Documents"

    def test_get_folder_for_detection_with_remap(self, tmp_path: Path) -> None:
        """Returns remapped folder with remap rule."""
        manager = CategoryManager(config_path=tmp_path / "config.yaml")
        manager.load()

        # Add Invoices category and set up remap
        manager.add("Invoices")
        manager.routing.set_remap("Documents", "Invoices", "InvoiceDetector")

        folder = manager.get_folder_for_detection("Documents", "InvoiceDetector")
        assert folder == "12_Invoices"

    def test_get_folder_for_detection_invalid_remap_fallback(
        self, tmp_path: Path
    ) -> None:
        """Falls back to Unsorted if remapped category doesn't exist."""
        manager = CategoryManager(config_path=tmp_path / "config.yaml")
        manager.load()

        # Remap to non-existent category
        manager.routing.set_remap("Documents", "NonExistent")

        folder = manager.get_folder_for_detection("Documents", "TestDetector")
        assert folder == "99_Unsorted"


class TestCategoryManagerRoutingGlobal:
    """Tests for global CategoryManager with routing."""

    def setup_method(self) -> None:
        """Reset global manager before each test."""
        reset_category_manager()

    def teardown_method(self) -> None:
        """Reset global manager after each test."""
        reset_category_manager()

    def test_global_manager_has_routing(self) -> None:
        """Global manager includes routing config."""
        manager = get_category_manager()
        assert hasattr(manager, "routing")
        assert isinstance(manager.routing, RoutingConfig)
