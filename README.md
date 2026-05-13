# Order Management System

Simple Order Management System REST API built with FastAPI.

## Tech Choices

| Framework | FastAPI | Async-native, auto-generated docs, Pydantic validation |
| Server | Uvicorn | ASGI server, pairs with FastAPI |
| Database | PostgreSQL 16 | Relational, strong for transactional data |
| ORM | SQLAlchemy 2.x (async) | Mature, async support, migration-friendly |
| Migrations | Alembic (sync) | Standard for SQLAlchemy, autogenerate support |
| Auth | JWT (python-jose) | Stateless token auth, simple for REST APIs |
| Password Hashing | Argon2id (argon2-cffi) | OWASP recommended, memory-hard |
| Config | pydantic-settings | Type-safe env loading with validation |

## Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/)
- Docker & Docker Compose

## Setup

```bash
cp .env.example .env
uv sync
docker-compose up -d
```

## Database Migrations

```bash
uv run alembic revision --autogenerate -m "description"
uv run alembic upgrade head
```

## Seed Products

```bash
uv run python -m app.seeds.products
```

## Run

```bash
uv run python main.py
```

Server starts at http://localhost:8000. API docs at http://localhost:8000/docs.

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | /api/v1/health | No | Health check |
| POST | /api/v1/auth/register | No | Register user |
| POST | /api/v1/auth/login | No | Login, returns JWT |
| GET | /api/v1/products | Yes | List products |
| POST | /api/v1/orders | Yes | Create order |
| GET | /api/v1/orders | Yes | List user's orders |
| GET | /api/v1/orders/{id} | Yes | Get order by ID |
| PUT | /api/v1/orders/{id} | Yes | Update order |
| POST | /api/v1/orders/{id}/cancel | Yes | Cancel order |

Protected routes require `Authorization: Bearer <token>` header.

## Tests

```bash
uv run pytest                    # run all tests
uv run pytest tests/test_utils.py   # single file
uv run pytest -v                 # verbose output
```

## API Reference

Base URL: `http://localhost:8000`  
Auth header: `Authorization: Bearer <token>`  
Error format: `{"error": "<message>", "path": "<request path>"}`

### Auth

**Register**
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123", "full_name": "Jane Doe"}'
```
Response `200`: `{"id": 1, "email": "user@example.com", "full_name": "Jane Doe", "is_active": true}`  
Response `400`: `{"error": "Email already registered"}`  
Response `422`: `{"detail": [...]}` — validation failed (e.g. password < 8 chars)

**Login**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'
```
Response `200`: `{"access_token": "<jwt>", "token_type": "bearer"}`  
Response `401`: `{"error": "Invalid credentials"}`

### Products

**List products** _(requires auth)_
```bash
curl http://localhost:8000/api/v1/products \
  -H "Authorization: Bearer <token>"
```
Response `200`: array of `{id, name, description, price, stock_quantity, is_available, ...}`

### Orders

**Create order** _(requires auth)_
```bash
curl -X POST http://localhost:8000/api/v1/orders/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"items": [{"product_id": 1, "quantity": 2}], "shipping_address": "123 Main St"}'
```
Response `200`: order object with `id`, `status`, `total_amount`, `order_items`  
Response `400`: product not found / insufficient stock / empty items  
Response `422`: quantity ≤ 0 or items list empty

**List orders** _(requires auth)_
```bash
curl http://localhost:8000/api/v1/orders/ -H "Authorization: Bearer <token>"
```

**Get order**
```bash
curl http://localhost:8000/api/v1/orders/1 -H "Authorization: Bearer <token>"
```
Response `404`: `{"error": "Order not found"}`  
Response `403`: `{"error": "Access denied"}`

**Update order** _(PENDING only)_
```bash
curl -X PUT http://localhost:8000/api/v1/orders/1 \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"shipping_address": "456 New St"}'
```

**Cancel order**
```bash
curl -X POST http://localhost:8000/api/v1/orders/1/cancel \
  -H "Authorization: Bearer <token>"
```
Response `400`: already cancelled or delivered

Interactive docs (Swagger UI) are also available at http://localhost:8000/docs.

## Stop

```bash
docker-compose down        # keep data
docker-compose down -v     # remove data
```
