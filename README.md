# Order Management System

A simple Order Management System (OMS) backend built with **FastAPI**, exposing REST APIs for user authentication, product listing, and order CRUD.

## Tech Stack

- **Framework:** FastAPI
- **Server:** Uvicorn
- **Database:** PostgreSQL 16 (via Docker)
- **Config:** pydantic-settings (`.env` based)
- **Package Manager:** uv


## Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager
- Docker & Docker Compose (for PostgreSQL)

## Setup

1. **Clone the repository** and navigate into the project:

   ```bash
   cd order-management-system
   ```

2. **Copy the environment file** and adjust if needed:

   ```bash
   cp .env.example .env
   ```

3. **Install dependencies:**

   ```bash
   uv sync
   ```

4. **Start the PostgreSQL database:**

   ```bash
   docker-compose up -d
   ```

## Running the Application

```bash
uv run python main.py
```

The server starts at **http://localhost:8000** with auto-reload enabled in debug mode.

### Verify it works

```bash
curl http://localhost:8000/api/v1/health
# → {"status":"ok"}
```

### API Documentation

FastAPI auto-generates interactive docs:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Running Tests

```bash
uv run pytest
```

## Stopping the Database

```bash
docker-compose down
```

To also remove persisted data:

```bash
docker-compose down -v
```
