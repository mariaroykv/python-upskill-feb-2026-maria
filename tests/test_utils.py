"""Unit tests for password hashing and JWT utilities."""

import pytest
from fastapi import HTTPException

from app.utils.security import (
    create_access_token,
    decode_token,
    hash_password,
    verify_password,
)


def test_password_hash_and_verify():
    """Hashed password is different from plain text and verifies correctly."""
    password = "my_super_secure_pass"
    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrong_password", hashed) is False


def test_jwt_encode_and_decode():
    """Token created from a user id can be decoded back to the same id."""
    user_id = "99"
    token = create_access_token({"sub": user_id})

    assert isinstance(token, str)
    decoded = decode_token(token)
    assert decoded == user_id


def test_decode_invalid_token_raises_401():
    """A garbage token string raises HTTPException with status 401."""
    with pytest.raises(HTTPException) as exc_info:
        decode_token("this.is.not.a.valid.token")
    assert exc_info.value.status_code == 401
