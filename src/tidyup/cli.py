"""Command-line interface for TidyUp."""

from pathlib import Path

import click

from . import __version__


class TidyGroup(click.Group):
    """Custom Click group that handles both subcommands and the default organize action."""

    def parse_args(self, ctx: click.Context, args: list[str]) -> list[str]:
        """Parse arguments, treating paths as the organize command."""
        # If first arg looks like a path (not a known command), insert 'run' command
        if args and args[0] not in self.commands and not args[0].startswith("-"):
            # Check if it could be a path
            if args[0] == "." or "/" in args[0] or Path(args[0]).exists():
                args = ["run"] + args
        return super().parse_args(ctx, args)


@click.group(cls=TidyGroup, invoke_without_command=True)
@click.version_option(version=__version__)
@click.pass_context
def main(ctx: click.Context) -> None:
    """TidyUp - Organize, rename, and categorize files.

    \b
    Examples:
        tidyup ~/Downloads                  # Move + rename (default)
        tidyup ~/Downloads ~/Organized      # Explicit destination
        tidyup ~/Downloads --move           # Only move, keep names
        tidyup ~/Downloads --rename         # Only rename in place
        tidyup . --dry-run                  # Preview changes
        tidyup status                       # Show statistics
        tidyup reindex                      # Renumber folders
    """
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@main.command(name="run")
@click.argument("source", type=click.Path(exists=True, path_type=Path))
@click.argument("destination", type=click.Path(path_type=Path), required=False)
@click.option("--move", is_flag=True, help="Only categorize and move, keep original names")
@click.option("--rename", is_flag=True, help="Only rename in place, don't move")
@click.option("--skip", is_flag=True, help="Skip uncertain files entirely")
@click.option("--dry-run", is_flag=True, help="Preview changes without moving files")
@click.option("--interactive", "-i", is_flag=True, help="Prompt for uncertain categorizations")
@click.option("--limit", "-n", type=int, help="Only process N files")
@click.option("--verbose", "-v", is_flag=True, help="Show detailed output")
def run_command(
    source: Path,
    destination: Path | None,
    move: bool,
    rename: bool,
    skip: bool,
    dry_run: bool,
    interactive: bool,
    limit: int | None,
    verbose: bool,
) -> None:
    """Organize files from SOURCE to DESTINATION.

    \b
    SOURCE is the directory to organize (required).
    DESTINATION is where to move files (optional, defaults to ~/Documents/Organized).
    """
    options = {
        "move": move,
        "rename": rename,
        "skip": skip,
        "dry_run": dry_run,
        "interactive": interactive,
        "limit": limit,
        "verbose": verbose,
    }
    run_organize(source, destination, options)


def run_organize(source: Path, destination: Path | None, options: dict) -> None:
    """Execute the organize operation."""
    from rich.console import Console
    from rich.table import Table

    from .engine import Engine

    console = Console()

    # Determine operation mode
    do_move = options.get("move", False)
    do_rename = options.get("rename", False)

    # Default: both move and rename
    if not do_move and not do_rename:
        do_move = True
        do_rename = True

    # Load default destination if not provided
    if destination is None and do_move:
        destination = Path.home() / "Documents" / "Organized"

    console.print(f"[bold]TidyUp[/bold] v{__version__}")
    console.print(f"Source: {source.resolve()}")

    if do_move:
        console.print(f"Destination: {destination.resolve() if destination else 'N/A'}")

    # Show operation mode
    if do_move and do_rename:
        mode = "Move + Rename"
    elif do_move:
        mode = "Move only (keep original names)"
    else:
        mode = "Rename only (in place)"
    console.print(f"Mode: {mode}")

    if options.get("dry_run"):
        console.print("[yellow]DRY RUN - no files will be changed[/yellow]")

    if options.get("skip"):
        console.print("[dim]Skipping uncertain files[/dim]")

    console.print()

    # Run the engine
    engine = Engine(source, destination=destination, options=options)
    result = engine.run()

    # Display results
    if options.get("verbose") or options.get("dry_run"):
        # Show individual actions
        if result.actions:
            table = Table(title="Actions")
            table.add_column("File", style="cyan")
            table.add_column("Category", style="green")
            table.add_column("Status", style="yellow")
            table.add_column("Destination")

            for action in result.actions:
                status_style = {
                    "success": "green",
                    "error": "red",
                    "skipped": "dim",
                }.get(action.status, "white")

                # Show actual destination: parent folder + filename
                dest_display = f"{action.dest_path.parent.name}/{action.dest_path.name}"

                table.add_row(
                    action.file.name,
                    action.detection.category,
                    f"[{status_style}]{action.status}[/{status_style}]",
                    dest_display,
                )

            console.print(table)
            console.print()

    # Show summary
    summary = result.summary
    console.print("[bold]Summary[/bold]")
    console.print(f"  Processed: {summary.processed}")
    console.print(f"  Moved:     {summary.moved}")
    console.print(f"  Renamed:   {summary.renamed}")
    if summary.unsorted > 0:
        console.print(f"  Unsorted:  {summary.unsorted}")
    if summary.skipped > 0:
        console.print(f"  Skipped:   {summary.skipped}")
    if summary.errors > 0:
        console.print(f"  [red]Errors:    {summary.errors}[/red]")
    if summary.duplicates > 0:
        console.print(f"  Duplicates: {summary.duplicates}")


@main.command()
def status() -> None:
    """Show organization statistics from logs."""
    from rich.console import Console

    console = Console()

    console.print("[bold]TidyUp Status[/bold]")
    console.print("═" * 50)
    console.print()
    console.print("Destination: ~/Documents/Organized")
    console.print("Config:      ~/.tidy/config.yaml")
    console.print("Logs:        ~/.tidy/logs/")
    console.print()
    console.print("[dim]Full status not yet implemented.[/dim]")


@main.command()
def reindex() -> None:
    """Renumber destination folders."""
    from rich.console import Console

    console = Console()
    console.print("[dim]Reindex not yet implemented.[/dim]")


@main.group(invoke_without_command=True)
@click.pass_context
def categories(ctx: click.Context) -> None:
    """Manage category configuration.

    \b
    Examples:
        tidyup categories              # List all categories
        tidyup categories add Music    # Add new category at end
        tidyup categories add Music --position 5  # Add at position 5
        tidyup categories remove Music            # Remove a category
        tidyup categories apply ~/Organized       # Rename folders to match config
    """
    if ctx.invoked_subcommand is None:
        # No subcommand given, show list
        ctx.invoke(categories_list)


@categories.command(name="list")
def categories_list() -> None:
    """List all configured categories."""
    from rich.console import Console
    from rich.table import Table

    from .categories import get_category_manager

    console = Console()
    manager = get_category_manager()

    # Check if any categories have rules
    has_rules = any(cat.parent or cat.rules for cat in manager.categories)

    table = Table(title="Categories")
    table.add_column("#", style="dim", justify="right")
    table.add_column("Name", style="cyan")
    table.add_column("Folder", style="green")
    if has_rules:
        table.add_column("Parent", style="yellow")
        table.add_column("Rules", style="dim")

    for cat in manager.categories:
        if has_rules:
            parent_display = cat.parent or ""
            rules_display = ""
            if cat.rules:
                parts = []
                if cat.rules.keywords:
                    parts.append(f"kw: {len(cat.rules.keywords)}")
                if cat.rules.patterns:
                    parts.append(f"pat: {len(cat.rules.patterns)}")
                rules_display = ", ".join(parts)
            table.add_row(str(cat.number), cat.name, cat.folder_name, parent_display, rules_display)
        else:
            table.add_row(str(cat.number), cat.name, cat.folder_name)

    console.print(table)
    console.print()
    console.print(f"Config: {manager.config_path or 'Using defaults'}")


@categories.command(name="add")
@click.argument("name")
@click.option("--position", "-p", type=int, help="Position for the new category (1-based)")
@click.option("--parent", help="Parent category for subcategorization (e.g., Books)")
@click.option(
    "--keywords", "-k",
    help="Comma-separated keywords for rule matching (e.g., 'programming,software,code')",
)
@click.option(
    "--patterns",
    help="Comma-separated filename patterns (e.g., 'acme_*,*_project_*')",
)
@click.option(
    "--no-suggestions",
    is_flag=True,
    help="Skip automatic keyword/parent suggestions",
)
def categories_add(
    name: str,
    position: int | None,
    parent: str | None,
    keywords: str | None,
    patterns: str | None,
    no_suggestions: bool,
) -> None:
    """Add a new category.

    When adding a category without explicit rules, TidyUp will suggest
    keywords and parent categories based on the name. Use --no-suggestions
    to skip this.

    \\b
    Examples:
        tidyup categories add Invoices
        tidyup categories add "Technical Books" --parent Books --keywords "programming,software,code"
        tidyup categories add "Client Work" --patterns "acme_*,techcorp_*"
        tidyup categories add "Random" --no-suggestions
    """
    from rich.console import Console

    from .categories import get_category_manager
    from .rules import CategoryRule
    from .suggestions import suggest_rules

    console = Console()
    manager = get_category_manager()

    # Check for suggestions if no rules explicitly provided
    final_parent = parent
    final_keywords: list[str] = []
    final_patterns: list[str] = []

    if keywords:
        final_keywords = [k.strip() for k in keywords.split(",")]
    if patterns:
        final_patterns = [p.strip() for p in patterns.split(",")]

    # Offer suggestions if no rules provided and not disabled
    if not no_suggestions and not keywords and not patterns and not parent:
        suggestion = suggest_rules(name)
        if suggestion.has_suggestions:
            console.print()
            console.print("[bold]Suggestions based on category name:[/bold]")

            if suggestion.parent:
                console.print(f"  Parent: [yellow]{suggestion.parent}[/yellow]")
            if suggestion.keywords:
                kw_display = ", ".join(suggestion.keywords[:8])
                if len(suggestion.keywords) > 8:
                    kw_display += f" (+{len(suggestion.keywords) - 8} more)"
                console.print(f"  Keywords: [cyan]{kw_display}[/cyan]")

            console.print()

            # Ask user if they want to accept suggestions
            if click.confirm("Accept these suggestions?", default=True):
                final_parent = suggestion.parent
                final_keywords = suggestion.keywords
            else:
                console.print("[dim]Suggestions skipped. Adding category without rules.[/dim]")

    # Build rules if any keywords or patterns
    rules = None
    if final_keywords or final_patterns:
        rules = CategoryRule(keywords=final_keywords, patterns=final_patterns)

    try:
        category = manager.add(name, position, parent=final_parent, rules=rules)
        manager.save()
        console.print(f"[green]Added category:[/green] {category.folder_name}")
        if final_parent:
            console.print(f"[dim]Parent: {final_parent}[/dim]")
        if rules:
            if rules.keywords:
                console.print(f"[dim]Keywords: {', '.join(rules.keywords)}[/dim]")
            if rules.patterns:
                console.print(f"[dim]Patterns: {', '.join(rules.patterns)}[/dim]")
        console.print(f"[dim]Config saved to {manager.config_path}[/dim]")
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)


@categories.command(name="remove")
@click.argument("name")
def categories_remove(name: str) -> None:
    """Remove a category."""
    from rich.console import Console

    from .categories import get_category_manager

    console = Console()
    manager = get_category_manager()

    try:
        manager.remove(name)
        manager.save()
        console.print(f"[green]Removed category:[/green] {name}")
        console.print(f"[dim]Config saved to {manager.config_path}[/dim]")
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)


@categories.command(name="apply")
@click.argument("path", type=click.Path(exists=True, path_type=Path))
@click.option("--dry-run", is_flag=True, help="Preview changes without renaming")
def categories_apply(path: Path, dry_run: bool) -> None:
    """Rename folders in PATH to match current category configuration.

    This is useful after adding, removing, or reordering categories.
    """
    from rich.console import Console
    from rich.table import Table

    from .categories import get_category_manager

    console = Console()
    manager = get_category_manager()

    changes = manager.apply_to_filesystem(path, dry_run=dry_run)

    if not changes:
        console.print("[dim]No folders need renaming.[/dim]")
        return

    if dry_run:
        console.print("[yellow]DRY RUN - no changes will be made[/yellow]")

    table = Table(title="Folder Renames")
    table.add_column("From", style="red")
    table.add_column("To", style="green")
    table.add_column("Status")

    for old_name, new_name in changes:
        status = "[dim]would rename[/dim]" if dry_run else "[green]renamed[/green]"
        table.add_row(str(old_name), str(new_name), status)

    console.print(table)

    if not dry_run:
        console.print(f"\n[green]Renamed {len(changes)} folder(s)[/green]")


@main.group(invoke_without_command=True)
@click.pass_context
def routing(ctx: click.Context) -> None:
    """Manage category routing rules.

    Routing allows remapping detector outputs to different categories.
    For example, redirect all files detected as "Documents" by the
    InvoiceDetector to an "Invoices" category instead.

    \\b
    Examples:
        tidyup routing                           # List all routing rules
        tidyup routing list                      # Same as above
        tidyup routing set Documents PDF         # Global: Documents → PDF
        tidyup routing set Documents Invoices --detector InvoiceDetector
        tidyup routing remove Documents          # Remove global remap
        tidyup routing remove Documents --detector InvoiceDetector
    """
    if ctx.invoked_subcommand is None:
        # No subcommand given, show list
        ctx.invoke(routing_list)


@routing.command(name="list")
def routing_list() -> None:
    """List all configured routing rules."""
    from rich.console import Console
    from rich.table import Table

    from .categories import get_category_manager

    console = Console()
    manager = get_category_manager()

    remaps = manager.routing.list_remaps()

    if not remaps:
        console.print("[dim]No routing rules configured.[/dim]")
        console.print()
        console.print("Add a rule with:")
        console.print("  tidyup routing set <from> <to>")
        console.print("  tidyup routing set <from> <to> --detector <name>")
        console.print()
        console.print("[dim]Example: Route invoices to a custom Invoices folder:[/dim]")
        console.print("  tidyup categories add Invoices")
        console.print("  tidyup routing set Documents Invoices --detector InvoiceDetector")
        return

    table = Table(title="Routing Rules")
    table.add_column("Detector", style="cyan")
    table.add_column("From", style="yellow")
    table.add_column("To", style="green")

    for remap in remaps:
        detector_display = remap["detector"] if remap["detector"] != "*" else "[dim]*[/dim]"
        table.add_row(detector_display, remap["from"], remap["to"])

    console.print(table)
    console.print()
    console.print(f"[dim]Config: {manager.config_path}[/dim]")


@routing.command(name="set")
@click.argument("from_category")
@click.argument("to_category")
@click.option(
    "--detector", "-d",
    help="Only apply to this detector (e.g., InvoiceDetector)",
)
def routing_set(from_category: str, to_category: str, detector: str | None) -> None:
    """Set a routing rule to remap categories.

    \\b
    Arguments:
        FROM_CATEGORY  Original category from detector
        TO_CATEGORY    Target category to route to
    """
    from rich.console import Console

    from .categories import get_category_manager

    console = Console()
    manager = get_category_manager()

    # Validate that target category exists
    if manager.get_by_name(to_category) is None:
        console.print(f"[red]Error:[/red] Category '{to_category}' does not exist.")
        console.print(f"[dim]Create it first with: tidyup categories add {to_category}[/dim]")
        raise SystemExit(1)

    # Set the remap
    manager.routing.set_remap(from_category, to_category, detector)
    manager.save()

    if detector:
        console.print(
            f"[green]Routing set:[/green] {detector}: {from_category} → {to_category}"
        )
    else:
        console.print(f"[green]Routing set:[/green] {from_category} → {to_category}")

    console.print(f"[dim]Config saved to {manager.config_path}[/dim]")


@routing.command(name="remove")
@click.argument("from_category")
@click.option(
    "--detector", "-d",
    help="Only remove for this detector",
)
def routing_remove(from_category: str, detector: str | None) -> None:
    """Remove a routing rule."""
    from rich.console import Console

    from .categories import get_category_manager

    console = Console()
    manager = get_category_manager()

    removed = manager.routing.remove_remap(from_category, detector)

    if removed:
        manager.save()
        if detector:
            console.print(
                f"[green]Removed routing:[/green] {detector}: {from_category}"
            )
        else:
            console.print(f"[green]Removed routing:[/green] {from_category}")
        console.print(f"[dim]Config saved to {manager.config_path}[/dim]")
    else:
        console.print(f"[yellow]No routing rule found for:[/yellow] {from_category}")
        if detector:
            console.print(f"[dim]Detector: {detector}[/dim]")


if __name__ == "__main__":
    main()
