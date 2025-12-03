"""Tests for the CLI interface."""

import pytest
from click.testing import CliRunner
from pathlib import Path

from tidyup.cli import main
from tidyup import __version__


class TestCLIHelp:
    """Tests for CLI help and version output."""

    def test_help_shows_usage(self, cli_runner: CliRunner) -> None:
        """tidy --help shows usage with all commands."""
        result = cli_runner.invoke(main, ["--help"])

        assert result.exit_code == 0
        assert "TidyUp - Organize, rename, and categorize files" in result.output
        assert "status" in result.output
        assert "reindex" in result.output
        assert "run" in result.output

    def test_run_help_shows_all_flags(self, cli_runner: CliRunner) -> None:
        """tidy run --help shows all flags."""
        result = cli_runner.invoke(main, ["run", "--help"])

        assert result.exit_code == 0
        assert "--move" in result.output
        assert "--rename" in result.output
        assert "--skip" in result.output
        assert "--dry-run" in result.output
        assert "--interactive" in result.output
        assert "--limit" in result.output
        assert "--verbose" in result.output

    def test_version_shows_version_string(self, cli_runner: CliRunner) -> None:
        """tidy --version outputs version string."""
        result = cli_runner.invoke(main, ["--version"])

        assert result.exit_code == 0
        assert __version__ in result.output

    def test_no_args_shows_help(self, cli_runner: CliRunner) -> None:
        """tidy with no args shows help."""
        result = cli_runner.invoke(main, [])

        assert result.exit_code == 0
        assert "TidyUp - Organize, rename, and categorize files" in result.output


class TestCLISourceValidation:
    """Tests for source directory validation."""

    def test_nonexistent_source_returns_error(self, cli_runner: CliRunner) -> None:
        """tidy /nonexistent returns error for missing source."""
        result = cli_runner.invoke(main, ["run", "/nonexistent/path/that/does/not/exist"])

        assert result.exit_code != 0

    def test_valid_source_runs(self, cli_runner: CliRunner, temp_source: Path) -> None:
        """tidy with valid source runs without error."""
        result = cli_runner.invoke(main, [str(temp_source), "--dry-run"])

        assert result.exit_code == 0
        assert "TidyUp" in result.output


class TestSubcommands:
    """Tests for subcommands."""

    def test_status_runs_without_error(self, cli_runner: CliRunner) -> None:
        """tidy status runs without error."""
        result = cli_runner.invoke(main, ["status"])

        assert result.exit_code == 0
        assert "Status" in result.output

    def test_reindex_runs_without_error(self, cli_runner: CliRunner) -> None:
        """tidy reindex runs without error."""
        result = cli_runner.invoke(main, ["reindex"])

        assert result.exit_code == 0
        assert "Reindex" in result.output or "not yet implemented" in result.output


class TestCLIFlags:
    """Tests for CLI flag combinations."""

    def test_move_flag_sets_mode(self, cli_runner: CliRunner, temp_source: Path) -> None:
        """--move flag sets move-only mode."""
        result = cli_runner.invoke(main, [str(temp_source), "--move", "--dry-run"])

        assert result.exit_code == 0
        assert "Move only" in result.output

    def test_rename_flag_sets_mode(self, cli_runner: CliRunner, temp_source: Path) -> None:
        """--rename flag sets rename-only mode."""
        result = cli_runner.invoke(main, [str(temp_source), "--rename", "--dry-run"])

        assert result.exit_code == 0
        assert "Rename only" in result.output

    def test_default_mode_is_both(self, cli_runner: CliRunner, temp_source: Path) -> None:
        """Default mode (no flags) is move + rename."""
        result = cli_runner.invoke(main, [str(temp_source), "--dry-run"])

        assert result.exit_code == 0
        assert "Move + Rename" in result.output

    def test_dry_run_shows_warning(self, cli_runner: CliRunner, temp_source: Path) -> None:
        """--dry-run shows dry run warning."""
        result = cli_runner.invoke(main, [str(temp_source), "--dry-run"])

        assert result.exit_code == 0
        assert "DRY RUN" in result.output

    def test_skip_flag_shows_message(self, cli_runner: CliRunner, temp_source: Path) -> None:
        """--skip flag shows skip message."""
        result = cli_runner.invoke(main, [str(temp_source), "--skip", "--dry-run"])

        assert result.exit_code == 0
        assert "skip" in result.output.lower() or "Skip" in result.output

    def test_path_without_run_command_works(self, cli_runner: CliRunner, temp_source: Path) -> None:
        """Passing a path directly (without 'run') should work."""
        result = cli_runner.invoke(main, [str(temp_source), "--dry-run"])

        assert result.exit_code == 0
        assert "TidyUp" in result.output

    def test_explicit_run_command_works(self, cli_runner: CliRunner, temp_source: Path) -> None:
        """Using explicit 'run' command should work."""
        result = cli_runner.invoke(main, ["run", str(temp_source), "--dry-run"])

        assert result.exit_code == 0
        assert "TidyUp" in result.output


class TestCategoriesCommands:
    """Tests for categories subcommands."""

    def test_categories_list(self, cli_runner: CliRunner) -> None:
        """categories list shows all categories."""
        result = cli_runner.invoke(main, ["categories", "list"])

        assert result.exit_code == 0
        assert "Documents" in result.output
        assert "Screenshots" in result.output
        assert "Images" in result.output
        assert "Unsorted" in result.output

    def test_categories_help(self, cli_runner: CliRunner) -> None:
        """categories --help shows all subcommands."""
        result = cli_runner.invoke(main, ["categories", "--help"])

        assert result.exit_code == 0
        assert "list" in result.output
        assert "add" in result.output
        assert "remove" in result.output
        assert "apply" in result.output

    def test_categories_add_shows_in_help(self, cli_runner: CliRunner) -> None:
        """categories add --help shows usage."""
        result = cli_runner.invoke(main, ["categories", "add", "--help"])

        assert result.exit_code == 0
        assert "--position" in result.output

    def test_categories_remove_shows_in_help(self, cli_runner: CliRunner) -> None:
        """categories remove --help shows usage."""
        result = cli_runner.invoke(main, ["categories", "remove", "--help"])

        assert result.exit_code == 0
        assert "NAME" in result.output

    def test_categories_apply_shows_in_help(self, cli_runner: CliRunner) -> None:
        """categories apply --help shows usage."""
        result = cli_runner.invoke(main, ["categories", "apply", "--help"])

        assert result.exit_code == 0
        assert "--dry-run" in result.output

    def test_categories_apply_dry_run(self, cli_runner: CliRunner, tmp_path: Path) -> None:
        """categories apply --dry-run shows preview."""
        # Create some folders
        (tmp_path / "01_Documents").mkdir()
        (tmp_path / "02_Screenshots").mkdir()

        result = cli_runner.invoke(main, ["categories", "apply", str(tmp_path), "--dry-run"])

        assert result.exit_code == 0
        # Either shows "No folders need renaming" or "DRY RUN"
        assert "No folders" in result.output or "DRY RUN" in result.output
