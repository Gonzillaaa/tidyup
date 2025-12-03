"""Interactive prompts for TidyUp.

Handles user interaction for uncertain file categorizations.
"""

from rich.console import Console
from rich.prompt import Prompt

from .categories import get_category_manager
from .models import DetectionResult, FileInfo


class InteractiveHandler:
    """Handles interactive prompts for uncertain files.

    Tracks user preferences for the current session (e.g., "skip all PDFs").
    """

    def __init__(self) -> None:
        """Initialize the interactive handler."""
        self.console = Console()
        self.skip_categories: set[str] = set()  # Categories to auto-skip
        self.skip_extensions: set[str] = set()  # Extensions to auto-skip

    def should_prompt(self, file: FileInfo, detection: DetectionResult) -> bool:
        """Check if we should prompt for this file.

        Returns False if user has chosen to skip this type.
        """
        if detection.category in self.skip_categories:
            return False
        if file.extension.lower() in self.skip_extensions:
            return False
        return True

    def prompt_for_file(
        self,
        file: FileInfo,
        detection: DetectionResult,
    ) -> tuple[str, str | None]:
        """Prompt user for action on uncertain file.

        Args:
            file: The file being processed.
            detection: The detection result.

        Returns:
            Tuple of (action, category):
            - ("accept", None): Use the detected category
            - ("skip", None): Skip this file
            - ("skip_type", None): Skip all files of this type
            - ("change", category): Use the specified category
        """
        self.console.print()
        self.console.print(
            f"[yellow]Uncertain:[/yellow] \"{file.name}\" detected as "
            f"[cyan]{detection.category}[/cyan] ({detection.confidence:.0%})"
        )

        if detection.reason:
            self.console.print(f"  [dim]Reason: {detection.reason}[/dim]")

        # Show options
        self.console.print()
        self.console.print("  [bold]Y[/bold] - Accept (move to {})".format(detection.category))
        self.console.print("  [bold]n[/bold] - Skip this file")
        self.console.print("  [bold]s[/bold] - Skip all {} files".format(file.extension.upper()))
        self.console.print("  [bold]c[/bold] - Change category")

        choice = Prompt.ask(
            "  Choice",
            choices=["y", "Y", "n", "N", "s", "S", "c", "C", ""],
            default="y",
            show_choices=False,
        )

        choice = choice.lower() if choice else "y"

        if choice == "y" or choice == "":
            return ("accept", None)
        elif choice == "n":
            return ("skip", None)
        elif choice == "s":
            self.skip_extensions.add(file.extension.lower())
            return ("skip_type", None)
        elif choice == "c":
            return self._prompt_category_change()

        return ("accept", None)

    def _prompt_category_change(self) -> tuple[str, str | None]:
        """Prompt user to select a different category.

        Returns:
            ("change", category_name) or ("skip", None) if cancelled.
        """
        manager = get_category_manager()
        categories = manager.categories

        self.console.print()
        self.console.print("  [bold]Available categories:[/bold]")

        for i, cat in enumerate(categories, 1):
            self.console.print(f"    {i:2}. {cat.name}")

        self.console.print()
        choice = Prompt.ask(
            "  Enter number (or 'q' to skip)",
            default="q",
        )

        if choice.lower() == "q":
            return ("skip", None)

        try:
            idx = int(choice) - 1
            if 0 <= idx < len(categories):
                return ("change", categories[idx].name)
        except ValueError:
            pass

        self.console.print("  [red]Invalid choice, skipping file[/red]")
        return ("skip", None)
