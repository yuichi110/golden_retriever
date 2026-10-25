# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/golden_retriever
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Test gret CLI."""

from __future__ import annotations

from typer.testing import CliRunner

from gret.cli import app

runner = CliRunner()


def test_cli_version() -> None:
    """Test 'gret version' command."""
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "gret" in result.stdout
    assert "0.1.0" in result.stdout


def test_cli_default() -> None:
    """Test invoking gret without subcommands."""
    result = runner.invoke(app, [])
    assert result.exit_code == 0
    assert "Golden Retriever CLI" in result.stdout
    assert "gret --help" in result.stdout
