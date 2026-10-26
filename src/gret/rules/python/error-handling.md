# Python Error Handling Golden Rules

This document specifies the standard error handling conventions, exception design patterns, and operational logging rules for Python applications and services.

---

## 1. Core Principles

1. **Be Specific (Never Catch Generic `Exception` Silently)**:
   Avoid bare `except:` or catching `Exception` without re-raising or detailed logging. Catch concrete exceptions whenever feasible.
2. **Fail Fast with Clear Messages**:
   Validate arguments, inputs, and environment configurations at system boundaries. Fail immediately with informative error messages.
3. **Prefer Custom Domain Exceptions**:
   Model domain-specific failure modes with custom exception classes inheriting from a project base exception (e.g. `AppError`).
4. **Preserve Stack Traces**:
   When re-raising or translating low-level exceptions into domain exceptions, always use `raise NewException(...) from exc` to maintain the causal chain.

---

## 2. Standard Exception Hierarchy

Organize domain exceptions under a single top-level base class:

```python
class AppError(Exception):
    """Base exception for all application errors."""
    def __init__(self, message: str, code: str = "INTERNAL_ERROR") -> None:
        super().__init__(message)
        self.message = message
        self.code = code


class ValidationError(AppError):
    """Raised when input validation fails."""
    def __init__(self, message: str) -> None:
        super().__init__(message, code="VALIDATION_ERROR")


class ResourceNotFoundError(AppError):
    """Raised when a requested resource does not exist."""
    def __init__(self, resource: str, identifier: str) -> None:
        super().__init__(f"{resource} '{identifier}' not found.", code="NOT_FOUND")


class ConflictError(AppError):
    """Raised when an operation conflicts with existing state."""
    def __init__(self, message: str) -> None:
        super().__init__(message, code="CONFLICT")
```

---

## 3. Boundary Translation Pattern (Clean Architecture)

Do not let third-party or database driver exceptions (e.g., `psycopg.Error`, `httpx.HTTPError`) leak into business logic or API callers. Translate them at service/repository boundaries:

```python
import httpx


def fetch_remote_user(user_id: str) -> dict[str, str]:
    """Fetch user profile from upstream service.

    Args:
        user_id: Unique user identifier.

    Returns:
        dict[str, str]: User data dictionary.

    Raises:
        ResourceNotFoundError: If user is not found.
        AppError: For connection or unexpected failures.
    """
    try:
        response = httpx.get(f"https://api.internal/users/{user_id}", timeout=5.0)
        if response.status_code == 404:
            raise ResourceNotFoundError("User", user_id)
        response.raise_for_status()
        return response.json()
    except httpx.RequestError as exc:
        raise AppError(f"Failed to communicate with user service: {exc}", code="UPSTREAM_ERROR") from exc
```

---

## 4. Logging & Diagnostics

- **Log with Context**: Include request IDs, user IDs, or entity identifiers in log messages.
- **Log Level Discipline**:
  - `DEBUG`: Verbose operational diagnostics.
  - `INFO`: Normal lifecycle events (service startup, batch job completion).
  - `WARNING`: Recoverable anomalies or expected 4xx errors.
  - `ERROR`: Unhandled 5xx exceptions, operational failures requiring team attention.
  - `CRITICAL`: System-wide failure (database connection loss, fatal crash).
