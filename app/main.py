from fastapi import FastAPI, HTTPException

from app.api.auth import router as auth_router
from app.api.health import router as health_router
from app.api.orders import router as orders_router
from app.api.products import router as products_router
from app.core.config import settings
from app.core.exception_handlers import global_exception_handler, http_exception_handler
from app.utils.logger import logger


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    app = FastAPI(
        title=settings.APP_NAME,
        version="0.1.0",
        description="Simple Order Management System REST API",
    )

    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(Exception, global_exception_handler)

    app.include_router(health_router, prefix="/api/v1")
    app.include_router(auth_router, prefix="/api/v1/auth", tags=["Auth"])
    app.include_router(products_router, prefix="/api/v1/products", tags=["Products"])
    app.include_router(orders_router, prefix="/api/v1/orders", tags=["Orders"])

    logger.info(f"Application '{settings.APP_NAME}' initialized")

    return app


app = create_app()
