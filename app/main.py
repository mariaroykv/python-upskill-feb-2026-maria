from fastapi import FastAPI

from app.api.health import router as health_router
from app.core.config import settings
from app.utils.logger import logger


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    app = FastAPI(
        title=settings.APP_NAME,
        version="0.1.0",
        description="Simple Order Management System REST API",
    )

    # Register routes
    app.include_router(health_router, prefix="/api/v1")

    logger.info(f"Application '{settings.APP_NAME}' initialized")

    return app


app = create_app()
