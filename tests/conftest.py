from unittest.mock import AsyncMock

import pytest

from app.schemas.auth import UserRegister


@pytest.fixture
def valid_user_data() -> UserRegister:
    """Standard user payload for auth tests."""
    return UserRegister(
        email="test@example.com",
        password="secure_password_123",
        full_name="Test User",
    )


@pytest.fixture
def mock_db() -> AsyncMock:
    """Async mock for the SQLAlchemy session — avoids real DB connections in unit tests."""
    return AsyncMock()
