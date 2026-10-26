# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/golden_retriever
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Sample CLI commands for inspecting and scaffolding practical code examples."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from gret.config import (
    find_example_dir,
    get_builtin_examples_dir,
    list_example_topics,
    suggest_example_topics,
)

samples_app = typer.Typer(
    name="sample",
    help="Inspect and scaffold practical code samples, templates, and full project skeletons.",
    no_args_is_help=True,
)

console = Console()
err_console = Console(stderr=True)

IGNORED_PATTERNS = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    ".DS_Store",
    "*.pyc",
}


def _should_ignore(path: Path) -> bool:
    """Check if a path should be ignored when inspecting or copying samples.

    Args:
        path: Path to evaluate.

    Returns:
        bool: True if path matches ignored directories or patterns.
    """
    for part in path.parts:
        if part in {".git", "__pycache__", ".pytest_cache", ".ruff_cache", ".venv", ".DS_Store"}:
            return True
        if part.endswith(".pyc"):
            return True
    return False


def _extract_sample_summary(sample_dir: Path) -> str:
    """Extract summary from README.md inside the sample directory.

    Args:
        sample_dir: Path to the sample directory.

    Returns:
        str: Summary text.
    """
    readme = sample_dir / "README.md"
    if not readme.is_file():
        return "No description available"

    try:
        content = readme.read_text(encoding="utf-8")
    except OSError:
        return "No description available"

    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    return "No description available"


@samples_app.command("list")
def cmd_sample_list() -> None:
    """List all available practical code samples and starter templates."""
    examples = list_example_topics()

    if not examples:
        console.print("[yellow]No code samples found.[/yellow]")
        return

    console.print("[bold cyan]Available Practical Code Samples:[/bold cyan]\n")

    categories: dict[str, list[tuple[str, Path, str]]] = {}
    builtin_dir = get_builtin_examples_dir().resolve()

    for topic_name, dir_path in sorted(examples.items()):
        category = topic_name.split("/")[0] if "/" in topic_name else "general"
        summary = _extract_sample_summary(dir_path)
        categories.setdefault(category, []).append((topic_name, dir_path, summary))

    for category, items in sorted(categories.items()):
        console.print(f"[bold green]Category: {category}[/bold green]")
        for topic_name, dir_path, summary in items:
            is_overridden = not dir_path.resolve().is_relative_to(builtin_dir)
            override_badge = " [bold magenta](custom)[/bold magenta]" if is_overridden else ""
            console.print(f"  • [bold]{topic_name:<28}[/bold]: {summary}{override_badge}")
        console.print()

    console.print("Run [bold]gret sample tree <topic>[/bold] to view file layout.")
    console.print("Run [bold]gret sample cat <topic> <file>[/bold] to view code.")
    console.print("Run [bold]gret sample init <topic> [dest][/bold] to scaffold a new project.")


@samples_app.command("tree")
def cmd_sample_tree(
    topic: Annotated[
        str,
        typer.Argument(help="Sample topic name to inspect (e.g. python/fastapi-simple)."),
    ],
) -> None:
    """Display file tree hierarchy of a specified sample."""
    sample_dir = find_example_dir(topic)

    if sample_dir is None or not sample_dir.is_dir():
        err_console.print(f"[bold red]Error:[/bold red] Unknown sample topic '{topic}'.\n")
        suggestions = suggest_example_topics(topic)
        if suggestions:
            err_console.print("[yellow]Did you mean one of these?[/yellow]")
            for s in suggestions:
                err_console.print(f"  • {s}")
            err_console.print()
        err_console.print("Run [bold]gret sample list[/bold] to see all available samples.")
        raise typer.Exit(code=1)

    console.print(f"[bold cyan]File tree for sample '{topic}':[/bold cyan]")

    file_paths = sorted([p for p in sample_dir.rglob("*") if not _should_ignore(p)])
    for path in file_paths:
        rel = path.relative_to(sample_dir)
        depth = len(rel.parts) - 1
        indent = "  " * depth
        if path.is_dir():
            console.print(f"{indent}📁 [bold blue]{rel.name}/[/bold blue]")
        else:
            console.print(f"{indent}📄 {rel.name}")


@samples_app.command("cat")
def cmd_sample_cat(
    topic: Annotated[
        str,
        typer.Argument(help="Sample topic name (e.g. python/fastapi-simple)."),
    ],
    file_path: Annotated[
        str,
        typer.Argument(help="Relative path of file inside sample (e.g. Dockerfile or src/app/main.py)."),
    ],
) -> None:
    """Output the contents of a specific file inside a sample without extracting."""
    sample_dir = find_example_dir(topic)

    if sample_dir is None or not sample_dir.is_dir():
        err_console.print(f"[bold red]Error:[/bold red] Unknown sample topic '{topic}'.\n")
        suggestions = suggest_example_topics(topic)
        if suggestions:
            err_console.print("[yellow]Did you mean one of these?[/yellow]")
            for s in suggestions:
                err_console.print(f"  • {s}")
        raise typer.Exit(code=1)

    # Secure target file resolution (prevent directory traversal)
    target = (sample_dir / file_path).resolve()
    try:
        target.relative_to(sample_dir.resolve())
    except ValueError:
        err_console.print("[bold red]Error:[/bold red] Attempted path traversal outside sample directory.")
        raise typer.Exit(code=1) from None

    if not target.is_file():
        err_console.print(f"[bold red]Error:[/bold red] File '{file_path}' does not exist in sample '{topic}'.\n")
        err_console.print(f"Run [bold]gret sample tree {topic}[/bold] to inspect available files.")
        raise typer.Exit(code=1)

    try:
        content = target.read_text(encoding="utf-8")
        console.print(content)
    except Exception as exc:
        err_console.print(f"[bold red]Error reading file '{file_path}':[/bold red] {exc}")
        raise typer.Exit(code=1) from exc


@samples_app.command("init")
def cmd_sample_init(
    topic: Annotated[
        str,
        typer.Argument(help="Sample topic name to scaffold (e.g. python/fastapi-simple)."),
    ],
    destination: Annotated[
        str | None,
        typer.Argument(help="Destination directory path (defaults to sample name)."),
    ] = None,
) -> None:
    """Scaffold a new project by copying the sample template to a destination."""
    sample_dir = find_example_dir(topic)

    if sample_dir is None or not sample_dir.is_dir():
        err_console.print(f"[bold red]Error:[/bold red] Unknown sample topic '{topic}'.\n")
        suggestions = suggest_example_topics(topic)
        if suggestions:
            err_console.print("[yellow]Did you mean one of these?[/yellow]")
            for s in suggestions:
                err_console.print(f"  • {s}")
        raise typer.Exit(code=1)

    dest_name = destination or sample_dir.name
    dest_path = Path(dest_name).resolve()

    if dest_path.exists() and any(dest_path.iterdir()):
        err_console.print(f"[bold red]Error:[/bold red] Destination '{dest_path}' already exists and is not empty.")
        raise typer.Exit(code=1)

    dest_path.mkdir(parents=True, exist_ok=True)

    # Copy files while respecting ignore patterns
    for item in sample_dir.rglob("*"):
        if _should_ignore(item):
            continue
        rel = item.relative_to(sample_dir)
        target = dest_path / rel
        if item.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        else:
            shutil.copy2(item, target)

    console.print(f"[bold green]✓ Successfully scaffolded '{topic}' into '{dest_path}'![/bold green]\n")
    console.print("Next steps:")
    console.print(f"  cd {dest_path.name}")
    console.print("  uv sync")
