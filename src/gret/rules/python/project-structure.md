# Python Project Structure Golden Rules

This document specifies the standard layout, package conventions, and dependency management rules for Python libraries and backend services.

---

## 1. Standard Repository Layout (`src`-layout)

Always use the **`src`-layout** to prevent accidental importing of uninstalled local packages during testing:

```text
my_project/
├── pyproject.toml              # Build backend and dependency declarations
├── README.md                   # Project overview, setup, and usage
├── LICENSE                     # License terms
├── uv.lock                     # Deterministic dependency lockfile
├── .gitignore                  # Git ignore rules
│
├── src/
│   └── my_package/             # Production source code
│       ├── __init__.py         # Package exports and version
│       ├── py.typed            # PEP 561 typing marker
│       └── core/ ...
│
├── tests/                      # Unit, integration, and property tests
│   ├── conftest.py             # Shared fixtures
│   └── test_*.py
│
└── tools/                      # Developer scripts, build automation, gcli
```

---

## 2. Tooling and Packaging Standard

1. **Package Manager**: Use [uv](https://github.com/astral-sh/uv) as the single source of truth for dependencies and virtual environments.
2. **Build Backend**: Use `uv_build` or `hatchling`.
3. **Linter & Formatter**: Use `ruff` (`line-length = 120`).
4. **Static Type Checking**: Use `ty` or `mypy` in strict mode (`py.typed` required for all distributed packages).
5. **Testing**: Use `pytest` with `pytest-cov` and `pytest-xdist`.

---

## 3. Package Exports and `__all__`

- Keep `__init__.py` minimal. Explicitly declare public API symbols using `__all__`.
- Use lazy imports or internal subpackages (`_internal/`) to keep the top-level namespace clean and optimize import times.
