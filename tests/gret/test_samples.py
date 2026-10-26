# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/golden_retriever
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Tests for gret sample CLI commands and project scaffolding."""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from gret.cli import app

runner = CliRunner()


def test_sample_list() -> None:
    """Test 'gret sample list' lists available starter templates."""
    result = runner.invoke(app, ["sample", "list"])
    assert result.exit_code == 0
    assert "Available Practical Code Samples:" in result.stdout
    assert "python/fastapi-simple" in result.stdout


def test_sample_tree_success() -> None:
    """Test 'gret sample tree' displays directory hierarchy."""
    result = runner.invoke(app, ["sample", "tree", "python/fastapi-simple"])
    assert result.exit_code == 0
    assert "File tree for sample 'python/fastapi-simple':" in result.stdout
    assert "Dockerfile" in result.stdout
    assert "main.py" in result.stdout


def test_sample_tree_unknown() -> None:
    """Test 'gret sample tree' with unknown topic shows suggestions."""
    result = runner.invoke(app, ["sample", "tree", "python/fastapi"])
    assert result.exit_code == 1
    assert "Unknown sample topic 'python/fastapi'" in result.output
    assert "Did you mean one of these?" in result.output
    assert "python/fastapi-simple" in result.output


def test_sample_cat_success() -> None:
    """Test 'gret sample cat' outputs raw file content to stdout."""
    result = runner.invoke(app, ["sample", "cat", "python/fastapi-simple", "Dockerfile"])
    assert result.exit_code == 0
    assert "FROM python:3.12-slim" in result.stdout
    assert "uvicorn" in result.stdout


def test_sample_cat_not_found() -> None:
    """Test 'gret sample cat' when target file does not exist."""
    result = runner.invoke(app, ["sample", "cat", "python/fastapi-simple", "non_existent.py"])
    assert result.exit_code == 1
    assert "does not exist in sample" in result.output


def test_sample_cat_path_traversal() -> None:
    """Test 'gret sample cat' prevents directory traversal attacks."""
    result = runner.invoke(app, ["sample", "cat", "python/fastapi-simple", "../../cli.py"])
    assert result.exit_code == 1
    assert "Attempted path traversal outside sample directory" in result.output


def test_sample_init_success(tmp_path: Path) -> None:
    """Test 'gret sample init' scaffolds template files into target directory."""
    target_dir = tmp_path / "my_service"
    result = runner.invoke(app, ["sample", "init", "python/fastapi-simple", str(target_dir)])
    assert result.exit_code == 0
    assert "Successfully scaffolded" in result.stdout

    # Verify generated files exist
    assert (target_dir / "Dockerfile").is_file()
    assert (target_dir / "pyproject.toml").is_file()
    assert (target_dir / "src" / "app" / "main.py").is_file()
    assert (target_dir / "tests" / "test_api.py").is_file()


def test_sample_init_dest_exists_and_not_empty(tmp_path: Path) -> None:
    """Test 'gret sample init' errors if destination exists and is not empty."""
    target_dir = tmp_path / "occupied"
    target_dir.mkdir()
    (target_dir / "existing_file.txt").write_text("content", encoding="utf-8")

    result = runner.invoke(app, ["sample", "init", "python/fastapi-simple", str(target_dir)])
    assert result.exit_code == 1
    assert "already exists and is not empty" in result.output


def test_sample_cascade_override(tmp_path: Path, monkeypatch) -> None:
    """Test that project-local .gret/examples overrides built-in samples."""
    custom_sample = tmp_path / ".gret" / "examples" / "custom" / "demo-app"
    custom_sample.mkdir(parents=True)
    (custom_sample / "README.md").write_text("# Custom Demo Starter\n", encoding="utf-8")
    (custom_sample / "app.py").write_text("print('hello')", encoding="utf-8")

    monkeypatch.chdir(tmp_path)

    result_list = runner.invoke(app, ["sample", "list"])
    assert result_list.exit_code == 0
    assert "custom/demo-app" in result_list.stdout
    assert "(custom)" in result_list.stdout
