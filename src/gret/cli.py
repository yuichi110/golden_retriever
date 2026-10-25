# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/golden_retriever
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Command line interface for Golden Retriever (gr)."""

from __future__ import annotations

import typer
from rich.console import Console

from gret import LIB_NAME, LIB_VERSION

app = typer.Typer(
    name="gr",
    help="Golden Retriever CLI application.",
    no_args_is_help=False,
)

console = Console()


@app.command("version")
def version() -> None:
    """Display version information."""
    console.print(f"[bold cyan]{LIB_NAME}[/bold cyan] version [bold green]{LIB_VERSION}[/bold green]")


@app.callback(invoke_without_command=True)
def callback(ctx: typer.Context) -> None:
    """Golden Retriever entrypoint callback.

    Args:
        ctx: Typer context object.
    """
    if ctx.invoked_subcommand is None:
        console.print("[bold cyan]Golden Retriever CLI[/bold cyan]")
        console.print(f"{LIB_NAME} version [bold green]{LIB_VERSION}[/bold green]\n")
        console.print("Run [bold]gr --help[/bold] for available commands.")


def main() -> None:
    """Execute gr CLI."""
    app()


if __name__ == "__main__":
    main()
