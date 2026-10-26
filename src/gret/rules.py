# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/golden_retriever
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Rules CLI commands for displaying golden rules and guidelines."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from gret.config import (
    find_rule_file,
    get_builtin_rules_dir,
    list_rule_topics,
    suggest_rule_topics,
)

rules_app = typer.Typer(
    name="rules",
    help="Display golden rules, architectural guidelines, and conventions.",
    no_args_is_help=True,
)

console = Console()
err_console = Console(stderr=True)


def _extract_topic_summary(file_path: Path) -> str:
    """Extract a short summary or title from a rule Markdown file.

    Args:
        file_path: Path to the markdown file.

    Returns:
        str: Summary text extracted from the document.
    """
    if not file_path.is_file():
        return "No description available"

    try:
        content = file_path.read_text(encoding="utf-8")
    except OSError:
        return "No description available"

    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    return "No description available"


@rules_app.command("list")
def cmd_rules_list() -> None:
    """List all available rule topics and their descriptions."""
    topics = list_rule_topics()

    if not topics:
        console.print("[yellow]No rule topics found.[/yellow]")
        return

    console.print("[bold cyan]Available Golden Rules:[/bold cyan]\n")

    # Group topics by category (first segment of topic name)
    categories: dict[str, list[tuple[str, Path, str]]] = {}
    builtin_dir = get_builtin_rules_dir().resolve()

    for topic_name, file_path in sorted(topics.items()):
        category = topic_name.split("/")[0] if "/" in topic_name else "general"
        summary = _extract_topic_summary(file_path)
        categories.setdefault(category, []).append((topic_name, file_path, summary))

    for category, items in sorted(categories.items()):
        console.print(f"[bold green]Category: {category}[/bold green]")
        for topic_name, file_path, summary in items:
            # Check if this topic is overriding the built-in rule
            is_overridden = not file_path.resolve().is_relative_to(builtin_dir)
            override_badge = " [bold magenta](custom)[/bold magenta]" if is_overridden else ""
            console.print(f"  • [bold]{topic_name:<28}[/bold]: {summary}{override_badge}")
        console.print()

    console.print("Run [bold]gret rules show <topic>[/bold] to view full rules.")


@rules_app.command("show")
def cmd_rules_show(
    topic: Annotated[
        str,
        typer.Argument(help="Rule topic name to display (e.g. python/error-handling)."),
    ],
) -> None:
    """Display rules and best practices for a specified topic."""
    file_path = find_rule_file(topic)

    if file_path is None or not file_path.is_file():
        err_console.print(f"[bold red]Error:[/bold red] Unknown rule topic '{topic}'.\n")
        suggestions = suggest_rule_topics(topic)
        if suggestions:
            err_console.print("[yellow]Did you mean one of these?[/yellow]")
            for s in suggestions:
                err_console.print(f"  • {s}")
            err_console.print()
        err_console.print("Run [bold]gret rules list[/bold] to see all available topics.")
        raise typer.Exit(code=1)

    try:
        content = file_path.read_text(encoding="utf-8")
        console.print(content)
    except Exception as exc:
        err_console.print(f"[bold red]Error reading rule '{topic}':[/bold red] {exc}")
        raise typer.Exit(code=1) from exc


@rules_app.command("search")
def cmd_rules_search(
    query: Annotated[
        str,
        typer.Argument(help="Search keyword or phrase across all golden rules."),
    ],
) -> None:
    """Search for keywords across all rule markdown contents."""
    topics = list_rule_topics()
    query_lower = query.strip().lower()

    matches: list[tuple[str, list[str]]] = []

    for topic_name, file_path in topics.items():
        try:
            content = file_path.read_text(encoding="utf-8")
        except OSError:
            content = ""

        matched_lines: list[str] = []
        for line in content.splitlines():
            if query_lower in line.lower():
                matched_lines.append(line.strip())
                if len(matched_lines) >= 3:
                    break

        if matched_lines or query_lower in topic_name:
            matches.append((topic_name, matched_lines))

    if not matches:
        console.print(f"[yellow]No rules found matching query '{query}'.[/yellow]")
        return

    console.print(f"[bold cyan]Search results for '{query}':[/bold cyan]\n")
    for topic_name, lines in matches:
        console.print(f"• [bold green]{topic_name}[/bold green]")
        for line in lines:
            console.print(f"    {line}")
        console.print()

    console.print("Run [bold]gret rules show <topic>[/bold] to inspect full details.")


@rules_app.command("bootstrap")
def cmd_rules_bootstrap() -> None:
    """Generate instructions for AI coding agents to reference golden rules."""
    instruction = """# AI Agent Instructions for Project Architecture & Standards

This project uses Golden Retriever (`gret`) to enforce organizational rules
and provide production-ready templates.

Before writing code or designing services, AI agents must consult the applicable golden rules:

1. **Discover Available Rules**:
   Run `uv run gret rules list` (or `uvx gret rules list`) to find the relevant guideline topic.
2. **Read Specific Guidelines**:
   Run `uv run gret rules show <topic>` to view concrete standards, patterns, and exception rules.
3. **Inspect & Use Examples**:
   Run `uv run gret sample list` to see available working samples.
   Run `uv run gret sample tree <topic>` or `uv run gret sample cat <topic> <file>` to inspect code.
   Run `uv run gret sample init <topic> [dest]` to scaffold new components.
"""
    console.print(instruction.strip())
