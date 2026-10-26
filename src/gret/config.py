# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/golden_retriever
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Configuration and cascade path resolution for rules and examples."""

from __future__ import annotations

import difflib
from importlib.resources import files
from pathlib import Path


def get_builtin_rules_dir() -> Path:
    """Get the path to the built-in rules directory.

    Returns:
        Path: Path to the built-in rules directory.
    """
    return Path(str(files("gret").joinpath("rules")))


def get_builtin_examples_dir() -> Path:
    """Get the path to the built-in examples directory.

    Returns:
        Path: Path to the built-in examples directory.
    """
    return Path(str(files("gret").joinpath("examples")))


def get_rules_dirs() -> list[Path]:
    """Get ordered list of rules search directories from high to low priority.

    Priority:
    1. Project local (.gret/rules)
    2. User/Org config (~/.config/gret/rules)
    3. Built-in package rules (src/gret/rules)

    Returns:
        list[Path]: List of existing rules directories in priority order.
    """
    candidates = [
        Path.cwd() / ".gret" / "rules",
        Path.home() / ".config" / "gret" / "rules",
        get_builtin_rules_dir(),
    ]
    return [d for d in candidates if d.is_dir()]


def get_examples_dirs() -> list[Path]:
    """Get ordered list of examples search directories from high to low priority.

    Priority:
    1. Project local (.gret/examples)
    2. User/Org config (~/.config/gret/examples)
    3. Built-in package examples (src/gret/examples)

    Returns:
        list[Path]: List of existing examples directories in priority order.
    """
    candidates = [
        Path.cwd() / ".gret" / "examples",
        Path.home() / ".config" / "gret" / "examples",
        get_builtin_examples_dir(),
    ]
    return [d for d in candidates if d.is_dir()]


def normalize_topic_name(topic: str) -> str:
    """Normalize a topic name for case and delimiter insensitivity.

    Args:
        topic: The topic name (e.g. 'python/error-handling' or 'python/error_handling').

    Returns:
        str: Normalized topic string.
    """
    return topic.strip().lower().replace("_", "-")


def list_rule_topics() -> dict[str, Path]:
    """Discover all available rule topics across cascading directories.

    Higher priority sources override lower priority ones if topic names conflict.

    Returns:
        dict[str, Path]: Mapping of normalized topic name to rule markdown Path.
    """
    topics: dict[str, Path] = {}

    # Iterate in reverse priority order so that higher priority entries overwrite lower ones
    for rules_dir in reversed(get_rules_dirs()):
        for md_file in rules_dir.glob("**/*.md"):
            rel_path = md_file.relative_to(rules_dir)
            topic_parts = list(rel_path.parts)
            # Remove '.md' from the last part
            topic_parts[-1] = md_file.stem
            topic_name = "/".join(topic_parts)
            normalized_name = normalize_topic_name(topic_name)
            topics[normalized_name] = md_file

    return topics


def find_rule_file(topic: str) -> Path | None:
    """Find the markdown file path for a specified rule topic.

    Args:
        topic: The requested topic name.

    Returns:
        Path | None: File path if found, None otherwise.
    """
    topics = list_rule_topics()
    norm = normalize_topic_name(topic)
    return topics.get(norm)


def suggest_rule_topics(topic: str, max_results: int = 3) -> list[str]:
    """Suggest closest matching rule topics for a misspelled query.

    Args:
        topic: The user's input topic name.
        max_results: Maximum number of suggestions to return.

    Returns:
        list[str]: Closest matching topic names.
    """
    topics = list(list_rule_topics().keys())
    norm = normalize_topic_name(topic)
    return difflib.get_close_matches(norm, topics, n=max_results, cutoff=0.4)


def list_example_topics() -> dict[str, Path]:
    """Discover all available example topics across cascading directories.

    Higher priority sources override lower priority ones if topic names conflict.
    An example directory is identified by containing files and not being internal cache.

    Returns:
        dict[str, Path]: Mapping of normalized example topic name to project directory Path.
    """
    examples: dict[str, Path] = {}

    for examples_dir in reversed(get_examples_dirs()):
        # Scan immediate subcategories (e.g. python/fastapi-simple)
        for path in examples_dir.glob("*/*"):
            if path.is_dir() and not path.name.startswith((".", "_")):
                rel_path = path.relative_to(examples_dir)
                norm_topic = normalize_topic_name(str(rel_path))
                examples[norm_topic] = path

    return examples


def find_example_dir(topic: str) -> Path | None:
    """Find the directory path for a specified example topic.

    Args:
        topic: The requested example topic name.

    Returns:
        Path | None: Directory path if found, None otherwise.
    """
    examples = list_example_topics()
    norm = normalize_topic_name(topic)
    return examples.get(norm)


def suggest_example_topics(topic: str, max_results: int = 3) -> list[str]:
    """Suggest closest matching example topics for a misspelled query.

    Args:
        topic: The user's input example topic name.
        max_results: Maximum number of suggestions to return.

    Returns:
        list[str]: Closest matching example topic names.
    """
    topics = list(list_example_topics().keys())
    norm = normalize_topic_name(topic)
    return difflib.get_close_matches(norm, topics, n=max_results, cutoff=0.4)
