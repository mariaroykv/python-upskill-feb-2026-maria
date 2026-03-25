from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Product


async def get_all(db: AsyncSession) -> list[Product]:
    stmt = select(Product).where(Product.deleted_at.is_(None))
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_by_id(db: AsyncSession, product_id: int) -> Product | None:
    stmt = select(Product).where(Product.id == product_id, Product.deleted_at.is_(None))
    result = await db.execute(stmt)
    return result.scalar_one_or_none()
