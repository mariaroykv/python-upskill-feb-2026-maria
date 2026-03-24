from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import product as product_repo
from app.schemas.product import ProductResponse


async def list_products(db: AsyncSession) -> list[ProductResponse]:
    products = await product_repo.get_all(db)
    return [ProductResponse.model_validate(p) for p in products]
