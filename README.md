# golden_retriever

Golden Retriever CLI and developer toolkit.

---

## Overview

- **Package Name (PyPI)**: `gret`
- **Import Module**: `gret`
- **CLI Command**: `gret`
- **Developer Management Tool**: `./gcli`

---

## Development Setup

This project uses [uv](https://github.com/astral-sh/uv) for dependency management and packaging.

```bash
# Sync dependencies and set up virtual environment
uv sync

# Run the CLI
uv run gret --help

# Run developer CLI toolsets
./gcli --help
./gcli code-check all
./gcli test all
```

---

## Developer Toolset (`./gcli`)

The `./gcli` script provides unified developer utilities:

- `./gcli code-check all`: Run Ruff linter and Ty type checker.
- `./gcli test all`: Run full pytest suite with coverage.
- `./gcli pypi check-version`: Verify package release version against PyPI.