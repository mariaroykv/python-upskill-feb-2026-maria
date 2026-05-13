# Phase 4 — Learning Notes

Topics covered in this phase: Validation, Error Handling, Logging, Testing, API Documentation.

---

## 1. Request Validation with Pydantic

FastAPI uses Pydantic models to validate incoming request bodies automatically. When validation fails FastAPI returns **HTTP 422 Unprocessable Entity** before your function is ever called.

### Two ways to add constraints

**`Field()` — declarative, inline**

```python
from pydantic import BaseModel, Field

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(gt=0, description="Must be greater than 0")
```

`gt`, `ge`, `lt`, `le`, `min_length`, `max_length` — these map directly to JSON Schema and show up in `/docs`.

**`@field_validator` — custom logic**

```python
from pydantic import BaseModel, field_validator

class OrderCreate(BaseModel):
    items: list[OrderItemCreate]

    @field_validator("items")
    @classmethod
    def items_must_not_be_empty(cls, v: list) -> list:
        if not v:
            raise ValueError("Order must contain at least one item")
        return v
```

- `@classmethod` is required by Pydantic v2.
- Raising `ValueError` inside a validator turns into a `ValidationError`, which FastAPI surfaces as a 422 response with a clear `detail` array.

### Where to find it in this project

- `app/schemas/order.py` — quantity > 0, non-empty items list
- `app/schemas/auth.py` — password ≥ 8 chars, non-blank full_name

---

## 2. Global Error Handling

### The problem without central handlers

Without a global handler, every unhandled exception produces FastAPI's default 500 response with no logging. HTTPExceptions give structured responses, but there's no single place to add logging or shape the output format.

### FastAPI exception handlers

```python
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

async def http_exception_handler(request: Request, exc: HTTPException):
    # Runs for every HTTPException raised anywhere in the app
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})

async def global_exception_handler(request: Request, exc: Exception):
    # Catches anything that isn't an HTTPException
    return JSONResponse(status_code=500, content={"error": "Internal Server Error"})

app = FastAPI()
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)
```

**Why two handlers?**

| Handler | Catches | Typical use |
|---------|---------|-------------|
| `HTTPException` | Intentional errors you raise (`raise HTTPException(404, ...)`) | Return structured error + log |
| `Exception` | Bugs, DB timeouts, unexpected crashes | Log, hide internal details from client |

### Where to find it in this project

- `app/core/exception_handlers.py` — both handlers
- `app/main.py` — registration with `add_exception_handler`

---

## 3. Logging

### Why not `print()`?

`print()` has no level, no timestamp, no file/line info, and no way to turn it off in production. The `logging` module gives you all of that.

### Python logging basics

```
Logger
  └── Handler (where output goes: console, file, etc.)
        └── Formatter (how each line looks)
```

```python
import logging

logger = logging.getLogger("app")          # named logger — forms a hierarchy
logger.setLevel(logging.INFO)

handler = logging.StreamHandler()          # write to stdout
formatter = logging.Formatter(
    "%(asctime)s | %(levelname)-8s | %(filename)s:%(lineno)d | %(message)s"
)
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.propagate = False                   # don't bubble up to root logger
```

### Log levels

| Level | When to use |
|-------|-------------|
| `DEBUG` | Detailed diagnostic info (disabled in prod) |
| `INFO` | Normal operations — request received, user created |
| `WARNING` | Something unexpected but not an error |
| `ERROR` | An error occurred but the app kept running |
| `EXCEPTION` | Like ERROR but also logs the full stack trace |

### Usage pattern in this project

```python
# In a route handler
logger.info(f"Creating order for user {current_user.id}")
order = await order_service.create_order(db, current_user, data)
logger.info(f"Order {order.id} created")
```

```python
# In the global exception handler
logger.exception("Unhandled exception", exception=exc)
```

### Where to find it in this project

- `app/utils/logger.py` — Logger class, formatter, HealthCheckFilter, uvicorn log config
- All `app/api/*.py` files — log calls in route handlers

---

## 4. Testing

### Unit tests vs integration tests

| | Unit test | Integration test |
|-|-----------|-----------------|
| Scope | One function / class | Multiple layers working together |
| Dependencies | Mocked | Real or partially mocked |
| Speed | Very fast | Slower |
| Goal | Verify logic in isolation | Verify components fit together |

### pytest basics

```bash
uv run pytest            # run all tests
uv run pytest -v         # verbose (shows each test name)
uv run pytest tests/test_utils.py   # single file
```

`pytest.ini` sets project-wide options:

```ini
[pytest]
pythonpath = .       # lets tests import from the project root
asyncio_mode = auto  # all async test functions automatically run under asyncio
```

### AsyncMock — mocking async functions

Normal `MagicMock` returns a regular value. `AsyncMock` returns a coroutine, so you can `await` it.

```python
from unittest.mock import AsyncMock, patch

async def test_register_duplicate_email():
    existing_user = AsyncMock()     # pretend this came from the DB
    with patch("app.repositories.user.get_by_email", AsyncMock(return_value=existing_user)):
        with pytest.raises(HTTPException) as exc:
            await auth_service.register(mock_db, user_data)
    assert exc.value.status_code == 400
```

**Key rule:** patch the function at the location where it is *used*, not where it is *defined*.  
`app.services.auth` imports `user_repo` from `app.repositories.user`. Since Python imports resolve to the same module object, patching `app.repositories.user.get_by_email` updates the function for all callers.

### Fixtures — shared test setup

```python
# tests/conftest.py  — automatically loaded by pytest
import pytest

@pytest.fixture
def valid_user_data():
    return UserRegister(email="test@example.com", password="pass1234", full_name="Test")
```

Any test function that names `valid_user_data` as a parameter gets the value automatically.

### Integration test with httpx

`httpx.AsyncClient` can talk to a FastAPI app in-process (no real HTTP server needed):

```python
from httpx import AsyncClient, ASGITransport

async def test_full_flow():
    app.dependency_overrides[get_db] = lambda: AsyncMock()   # no real DB
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/api/v1/auth/register", json={...})
        assert resp.status_code == 200
    app.dependency_overrides.clear()
```

`dependency_overrides` lets you swap out any FastAPI `Depends(...)` for tests — very useful for replacing real DB sessions.

### Where to find it in this project

```
tests/
├── conftest.py          # shared fixtures
├── test_utils.py        # password hashing, JWT
├── test_schemas.py      # Pydantic validation errors
├── test_auth_service.py # service layer with mocked repos
└── test_order_flow.py   # register → login → create order (integration)
```

---

## 5. API Documentation

FastAPI auto-generates an OpenAPI spec from your code. No extra work needed.

| URL | What you get |
|-----|-------------|
| `/docs` | Swagger UI — interactive, try requests in browser |
| `/redoc` | ReDoc — cleaner reading format |
| `/openapi.json` | Raw OpenAPI 3.x JSON spec |

### What drives the generated docs

| Code element | What it documents |
|---|---|
| `response_model=OrderResponse` | Response schema |
| Pydantic field types + `Field(description=...)` | Request body schema |
| `tags=["Orders"]` on `include_router` | Groups endpoints in the UI |
| `title`, `description` on `FastAPI(...)` | API overview |
| Docstrings on route functions | Endpoint description |

### Keeping docs accurate

Because docs are generated from the same code that runs, they are always in sync. There is no separate file to maintain. If you add a validator to a schema, it appears in the docs automatically.

---

## Summary

| Area | Key concept | Where in this project |
|------|-------------|----------------------|
| Validation | `@field_validator`, `Field(gt=0)` → 422 | `app/schemas/` |
| Error handling | `add_exception_handler` for HTTP + bare Exception | `app/core/exception_handlers.py` |
| Logging | Named logger, levels, formatters | `app/utils/logger.py`, `app/api/` |
| Unit tests | `AsyncMock`, `patch`, `pytest.raises` | `tests/test_*.py` |
| Integration tests | `httpx.AsyncClient`, `dependency_overrides` | `tests/test_order_flow.py` |
| API docs | Auto-generated from Pydantic + route metadata | `/docs`, `/redoc` |
