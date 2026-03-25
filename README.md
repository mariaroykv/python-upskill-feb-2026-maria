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
uv run pytest
```

## Stop

```bash
docker-compose down        # keep data
docker-compose down -v     # remove data
```
