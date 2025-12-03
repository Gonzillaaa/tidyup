"""Command-line interface for Tidy."""

import click
from pathlib import Path
from typing import Optional

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
    destination: Optional[Path],
    move: bool,
    rename: bool,
    skip: bool,
    dry_run: bool,
    interactive: bool,
    limit: Optional[int],
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


def run_organize(source: Path, destination: Optional[Path], options: dict) -> None:
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

                # Show category folder + filename for destination
                dest_display = f"{action.detection.category}/{action.dest_path.name}"

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

    console.print("[bold]Tidy Status[/bold]")
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


if __name__ == "__main__":
    main()
