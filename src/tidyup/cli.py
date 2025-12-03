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
    from rich.table import Table

    from .logger import aggregate_logs, list_logs, load_log, get_tidy_dir
    from .utils import format_size

    console = Console()

    # Default destination
    dest = Path.home() / "Documents" / "Organized"
    config_path = Path.home() / ".tidy" / "config.yaml"
    logs_dir = get_tidy_dir() / "logs"

    # Count log files
    log_count = len(list_logs()) if logs_dir.exists() else 0

    console.print()
    console.print("[bold]TidyUp Status[/bold]")
    console.print("═" * 50)
    console.print()
    console.print(f"Destination: {dest}")
    console.print(f"Config:      {config_path}")
    console.print(f"Logs:        {logs_dir} ({log_count} files)")
    console.print()

    # Scan destination folders for stats
    if dest.exists():
        table = Table(show_header=True, header_style="bold")
        table.add_column("Folder", style="cyan")
        table.add_column("Files", justify="right")
        table.add_column("Size", justify="right")

        total_files = 0
        total_size = 0

        # Get all numbered folders sorted
        folders = sorted(
            [f for f in dest.iterdir() if f.is_dir() and not f.name.startswith(".")],
            key=lambda f: f.name,
        )

        for folder in folders:
            # Count files and size
            file_count = 0
            folder_size = 0
            for item in folder.rglob("*"):
                if item.is_file():
                    file_count += 1
                    folder_size += item.stat().st_size

            total_files += file_count
            total_size += folder_size

            if file_count > 0:  # Only show non-empty folders
                table.add_row(
                    f"{folder.name}/",
                    str(file_count),
                    format_size(folder_size),
                )

        # Add separator and total
        table.add_row("─" * 20, "─" * 6, "─" * 8, style="dim")
        table.add_row(
            "[bold]Total[/bold]",
            f"[bold]{total_files}[/bold]",
            f"[bold]{format_size(total_size)}[/bold]",
        )

        console.print(table)
    else:
        console.print(f"[dim]Destination not found: {dest}[/dim]")

    console.print()

    # Last run info
    logs = list_logs(limit=1)
    if logs:
        try:
            last_run = load_log(logs[0])
            console.print(f"[bold]Last Run:[/bold] {last_run.timestamp.strftime('%Y-%m-%d %H:%M')}")
            s = last_run.summary
            console.print(f"  → Moved {s.moved} files, renamed {s.renamed}, skipped {s.skipped}")
        except Exception:
            pass

    # Recent activity
    stats = aggregate_logs(days=7)
    if stats["total_runs"] > 0:
        console.print()
        console.print("[bold]Recent Activity (last 7 days):[/bold]")
        console.print(f"  → {stats['total_processed']} files processed in {stats['total_runs']} runs")
        if stats["total_errors"] > 0:
            console.print(f"  → [red]{stats['total_errors']} errors[/red]")

    console.print()


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

    table = Table(title="Categories")
    table.add_column("#", style="dim", justify="right")
    table.add_column("Name", style="cyan")
    table.add_column("Folder", style="green")

    for cat in manager.categories:
        table.add_row(str(cat.number), cat.name, cat.folder_name)

    console.print(table)
    console.print()
    console.print(f"Config: {manager.config_path or 'Using defaults'}")


@categories.command(name="add")
@click.argument("name")
@click.option("--position", "-p", type=int, help="Position for the new category (1-based)")
def categories_add(name: str, position: int | None) -> None:
    """Add a new category."""
    from rich.console import Console

    from .categories import get_category_manager

    console = Console()
    manager = get_category_manager()

    try:
        category = manager.add(name, position)
        manager.save()
        console.print(f"[green]Added category:[/green] {category.folder_name}")
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


if __name__ == "__main__":
    main()
