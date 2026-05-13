"""Unit tests for Pydantic schema validation — confirms 422-triggering rules."""

import pytest
from pydantic import ValidationError

from app.schemas.auth import UserRegister
from app.schemas.order import OrderCreate, OrderItemCreate


def test_order_quantity_must_be_positive():
    """quantity=0 should fail validation with a clear message."""
    with pytest.raises(ValidationError) as exc_info:
        OrderItemCreate(product_id=1, quantity=0)
    assert "Quantity must be greater than 0" in str(exc_info.value)


def test_order_quantity_negative_also_fails():
    """Negative quantity should also fail validation."""
    with pytest.raises(ValidationError):
        OrderItemCreate(product_id=1, quantity=-5)


def test_order_items_must_not_be_empty():
    """An order with an empty items list should fail validation."""
    with pytest.raises(ValidationError) as exc_info:
        OrderCreate(items=[])
    assert "Order must contain at least one item" in str(exc_info.value)


def test_password_min_length_validation():
    """Passwords shorter than 8 characters should fail validation."""
    with pytest.raises(ValidationError) as exc_info:
        UserRegister(email="a@b.com", password="short", full_name="Test User")
    assert "at least 8 characters" in str(exc_info.value)


def test_blank_full_name_validation():
    """A full_name of only whitespace should fail validation."""
    with pytest.raises(ValidationError) as exc_info:
        UserRegister(email="a@b.com", password="password123", full_name="   ")
    assert "cannot be blank" in str(exc_info.value)


def test_valid_order_passes():
    """A well-formed order should be created without errors."""
    order = OrderCreate(
        items=[OrderItemCreate(product_id=1, quantity=2)],
        shipping_address="123 Main St",
    )
    assert len(order.items) == 1
    assert order.items[0].quantity == 2
