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

---

## Features

### 1. Golden Rules (`gret rules`)

Inspect organizational guidelines and best practices:

```bash
# List available rule topics
uv run gret rules list

# Display detailed rules for a topic
uv run gret rules show python/error-handling

# Search keywords across rules
uv run gret rules search "exception"

# Output instructions prompt for AI coding agents
uv run gret rules bootstrap
```

### 2. Practical Code Samples (`gret sample`)

Inspect and scaffold production-ready project templates without creating temporary clutter:

```bash
# List available samples
uv run gret sample list

# Inspect file hierarchy tree
uv run gret sample tree python/fastapi-simple

# View raw source file directly in stdout
uv run gret sample cat python/fastapi-simple Dockerfile

# Scaffold sample into target project
uv run gret sample init python/fastapi-simple ./my-api-service
```

### 3. Cascade Override (`.gret/`)

Customize or override built-in rules and samples for your specific repository:

- **Project Rules**: Place Markdown files in `./.gret/rules/<topic>.md`.
- **Project Samples**: Place sample projects in `./.gret/examples/<topic>/`.
- Local configurations seamlessly take precedence over built-in defaults.