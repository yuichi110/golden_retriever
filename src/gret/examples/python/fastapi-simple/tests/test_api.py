"""Unit tests for FastAPI simple service endpoints."""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check() -> None:
    """Test health endpoint returns 200 OK."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_list_users() -> None:
    """Test listing users returns predefined seed data."""
    response = client.get("/api/v1/users")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2


def test_get_user_not_found() -> None:
    """Test fetching non-existent user returns 404."""
    response = client.get("/api/v1/users/9999")
    assert response.status_code == 404
