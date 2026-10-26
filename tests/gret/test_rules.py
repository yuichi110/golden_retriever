# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/golden_retriever
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Tests for gret rules CLI commands and cascade resolution."""

from __future__ import annotations

import os
from pathlib import Path

from typer.testing import CliRunner

from gret.cli import app

runner = CliRunner()


def test_rules_list() -> None:
    """Test 'gret rules list' lists available topics."""
    result = runner.invoke(app, ["rules", "list"])
    assert result.exit_code == 0
    assert "Available Golden Rules:" in result.stdout
    assert "python/error-handling" in result.stdout
    assert "python/project-structure" in result.stdout
    assert "api/rest-design" in result.stdout


def test_rules_show_success() -> None:
    """Test 'gret rules show' displays full rule markdown."""
    result = runner.invoke(app, ["rules", "show", "python/error-handling"])
    assert result.exit_code == 0
    assert "Python Error Handling Golden Rules" in result.stdout
    assert "Standard Exception Hierarchy" in result.stdout


def test_rules_show_unknown_topic() -> None:
    """Test 'gret rules show' with invalid topic displays suggestion and error."""
    result = runner.invoke(app, ["rules", "show", "python/error"])
    assert result.exit_code == 1
    assert "Unknown rule topic 'python/error'" in result.output
    assert "Did you mean one of these?" in result.output
    assert "python/error-handling" in result.output


def test_rules_search_match() -> None:
    """Test 'gret rules search' finds matching keywords."""
    result = runner.invoke(app, ["rules", "search", "exception"])
    assert result.exit_code == 0
    assert "Search results for 'exception':" in result.stdout
    assert "python/error-handling" in result.stdout


def test_rules_search_no_match() -> None:
    """Test 'gret rules search' when nothing matches."""
    result = runner.invoke(app, ["rules", "search", "xyznonexistentquery987"])
    assert result.exit_code == 0
    assert "No rules found matching query" in result.stdout


def test_rules_bootstrap() -> None:
    """Test 'gret rules bootstrap' outputs AI agent instruction prompt."""
    result = runner.invoke(app, ["rules", "bootstrap"])
    assert result.exit_code == 0
    assert "AI Agent Instructions for Project Architecture & Standards" in result.stdout
    assert "gret rules list" in result.stdout
    assert "gret sample list" in result.stdout


def test_rules_cascade_override(tmp_path: Path, monkeypatch) -> None:
    """Test that project-local .gret/rules overrides built-in rules."""
    local_rules = tmp_path / ".gret" / "rules" / "python"
    local_rules.mkdir(parents=True)
    custom_rule = local_rules / "error-handling.md"
    custom_rule.write_text("# Custom Org Error Handling\n\nCustom rule content.", encoding="utf-8")

    monkeypatch.chdir(tmp_path)

    result_list = runner.invoke(app, ["rules", "list"])
    assert result_list.exit_code == 0
    assert "(custom)" in result_list.stdout

    result_show = runner.invoke(app, ["rules", "show", "python/error-handling"])
    assert result_show.exit_code == 0
    assert "Custom Org Error Handling" in result_show.stdout
    assert "Custom rule content." in result_show.stdout
