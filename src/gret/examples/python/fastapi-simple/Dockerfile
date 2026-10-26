FROM python:3.12-slim

# Install uv for deterministic dependency resolution
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

# Enable bytecode compilation & non-buffered stdout
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_COMPILE_BYTECODE=1

# Copy dependency definition
COPY pyproject.toml .

# Install dependencies into system environment or virtualenv
RUN uv pip install --system -r pyproject.toml

# Copy application source
COPY src/ /app/src/

# Run as non-privileged user for security
RUN useradd -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

ENV PYTHONPATH=/app/src
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
