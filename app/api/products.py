from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.db.connection import get_db
from app.db.models import User
from app.schemas.product import ProductResponse
from app.services import product as product_service
from app.utils.logger import logger

router = APIRouter()


@router.get("/", response_model=list[ProductResponse])
async def list_products(
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    logger.info("Listing all available products")
    return await product_service.list_products(db)
