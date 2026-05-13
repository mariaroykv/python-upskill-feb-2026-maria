"""Unit tests for the auth service layer — DB is mocked via AsyncMock."""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException

from app.schemas.auth import UserLogin, UserRegister
from app.services import auth as auth_service
from app.utils.security import hash_password


async def test_register_duplicate_email_raises_400(mock_db, valid_user_data):
    """Registering with an already-used email raises HTTPException 400."""
    existing_user = AsyncMock()
    existing_user.email = valid_user_data.email

    with patch("app.repositories.user.get_by_email", AsyncMock(return_value=existing_user)):
        with pytest.raises(HTTPException) as exc_info:
            await auth_service.register(mock_db, valid_user_data)

    assert exc_info.value.status_code == 400
    assert "already registered" in exc_info.value.detail


async def test_register_new_user_succeeds(mock_db, valid_user_data):
    """Registering with a fresh email creates and returns the user."""
    mock_created_user = AsyncMock()
    mock_created_user.id = 1
    mock_created_user.email = valid_user_data.email
    mock_created_user.full_name = valid_user_data.full_name
    mock_created_user.is_active = True

    with (
        patch("app.repositories.user.get_by_email", AsyncMock(return_value=None)),
        patch("app.repositories.user.create", AsyncMock(return_value=mock_created_user)),
    ):
        result = await auth_service.register(mock_db, valid_user_data)

    assert result.email == valid_user_data.email


async def test_login_wrong_password_raises_401(mock_db):
    """Logging in with the wrong password raises HTTPException 401."""
    mock_user = AsyncMock()
    mock_user.hashed_password = hash_password("correct_password_123")

    with patch("app.repositories.user.get_by_email", AsyncMock(return_value=mock_user)):
        with pytest.raises(HTTPException) as exc_info:
            await auth_service.login(
                mock_db,
                UserLogin(email="test@example.com", password="wrong_password"),
            )

    assert exc_info.value.status_code == 401
    assert "Invalid credentials" in exc_info.value.detail


async def test_login_unknown_email_raises_401(mock_db):
    """Logging in with an email not in the DB raises HTTPException 401."""
    with patch("app.repositories.user.get_by_email", AsyncMock(return_value=None)):
        with pytest.raises(HTTPException) as exc_info:
            await auth_service.login(
                mock_db,
                UserLogin(email="nobody@example.com", password="password123"),
            )

    assert exc_info.value.status_code == 401
