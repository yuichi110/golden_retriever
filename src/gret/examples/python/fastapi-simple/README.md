# FastAPI Simple Service Sample

Production-grade starter template for a FastAPI backend service following Golden Retriever architecture standards.

---

## Features

- **FastAPI** with Pydantic v2 data modeling.
- Standard error envelope matching RFC 7807 (`gret rules show api/rest-design`).
- Modular routing (`src/app/api.py`).
- Docker & Docker Compose setup with non-root user.
- Pre-configured `uv` environment with fast dependency resolution.

---

## Quickstart

```bash
# Install dependencies
uv sync

# Run development server
uv run uvicorn app.main:app --reload --port 8000

# Run tests
uv run pytest

# Run with Docker
docker compose up --build
```
