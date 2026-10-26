"""API routes and endpoints for user management."""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr, Field

router = APIRouter(tags=["users"])


class UserCreateRequest(BaseModel):
    """Payload for creating a new user."""

    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr


class UserResponse(BaseModel):
    """User response model."""

    id: int
    username: str
    email: str


# In-memory database simulation for sample purposes
USERS_DB: dict[int, dict[str, str | int]] = {
    1: {"id": 1, "username": "alice", "email": "alice@example.com"},
    2: {"id": 2, "username": "bob", "email": "bob@example.com"},
}


@router.get("/users", response_model=list[UserResponse])
def list_users() -> list[dict[str, str | int]]:
    """Retrieve list of registered users."""
    return list(USERS_DB.values())


@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int) -> dict[str, str | int]:
    """Retrieve a single user by ID."""
    user = USERS_DB.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} was not found.",
        )
    return user


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreateRequest) -> dict[str, str | int]:
    """Register a new user."""
    new_id = max(USERS_DB.keys(), default=0) + 1
    new_user = {
        "id": new_id,
        "username": payload.username,
        "email": payload.email,
    }
    USERS_DB[new_id] = new_user
    return new_user
