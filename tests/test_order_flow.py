"""
Integration test: Register → Login → Create Order

Uses httpx.AsyncClient against the real FastAPI app.
The database dependency is overridden with an AsyncMock so no real
PostgreSQL connection is needed. Repositories are patched at the
module level so the full route → service → (mock) repo chain runs.
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.db.connection import get_db
from app.db.models import OrderStatus
from app.main import app
from app.utils.security import hash_password


@pytest.fixture
def mock_user():
    user = MagicMock()
    user.id = 1
    user.email = "flow@example.com"
    user.full_name = "Flow User"
    user.is_active = True
    user.hashed_password = hash_password("password123")
    return user


@pytest.fixture
def mock_product():
    product = MagicMock()
    product.id = 1
    product.name = "Widget A"
    product.price = 9.99
    product.stock_quantity = 100
    product.is_available = True
    return product


@pytest.fixture
def mock_order(mock_user):
    order = MagicMock()
    order.id = 42
    order.user_id = mock_user.id
    order.status = OrderStatus.PENDING
    order.total_amount = 19.98
    order.shipping_address = "123 Test St"
    order.order_items = []
    order.created_at = datetime.now()
    order.updated_at = datetime.now()
    return order


async def test_register_login_create_order_flow(mock_user, mock_product, mock_order):
    """
    Full auth → order flow through real HTTP handlers.
    - Register: user_repo returns None (no duplicate), then creates the user.
    - Login:    user_repo returns the mock user so credentials can be checked.
    - Create order: product and order repos return mock objects.
    """
    # Override get_db so no real DB connection is attempted
    app.dependency_overrides[get_db] = lambda: AsyncMock()

    try:
        with (
            # side_effect=[None, mock_user]: first call (register check) → no user,
            # second call (login lookup) → return mock user
            patch("app.repositories.user.get_by_email", AsyncMock(side_effect=[None, mock_user])),
            patch("app.repositories.user.create", AsyncMock(return_value=mock_user)),
            patch("app.repositories.user.get_by_id", AsyncMock(return_value=mock_user)),
            patch("app.repositories.product.get_by_id", AsyncMock(return_value=mock_product)),
            patch("app.repositories.order.create", AsyncMock(return_value=mock_order)),
        ):
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                # Step 1 — Register
                reg = await client.post(
                    "/api/v1/auth/register",
                    json={
                        "email": "flow@example.com",
                        "password": "password123",
                        "full_name": "Flow User",
                    },
                )
                assert reg.status_code == 200, reg.text

                # Step 2 — Login and capture the JWT
                login = await client.post(
                    "/api/v1/auth/login",
                    json={"email": "flow@example.com", "password": "password123"},
                )
                assert login.status_code == 200, login.text
                token = login.json()["access_token"]
                assert token

                # Step 3 — Create an order using the real JWT
                order = await client.post(
                    "/api/v1/orders/",
                    json={
                        "items": [{"product_id": 1, "quantity": 2}],
                        "shipping_address": "123 Test St",
                    },
                    headers={"Authorization": f"Bearer {token}"},
                )
                assert order.status_code == 200, order.text
                body = order.json()
                assert body["id"] == 42
                assert body["total_amount"] == 19.98
    finally:
        app.dependency_overrides.clear()
