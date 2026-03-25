from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import Order, OrderItem, OrderStatus


async def create(
    db: AsyncSession,
    user_id: int,
    total_amount: float,
    shipping_address: str | None,
    items: list[dict],
) -> Order:
    order = Order(
        user_id=user_id,
        total_amount=total_amount,
        shipping_address=shipping_address,
        status=OrderStatus.PENDING,
    )
    db.add(order)
    await db.flush()

    for item in items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item["product_id"],
            quantity=item["quantity"],
            unit_price=item["unit_price"],
            subtotal=item["subtotal"],
        )
        db.add(order_item)

    await db.commit()
    return await get_by_id(db, order.id)


async def get_by_id(db: AsyncSession, order_id: int) -> Order | None:
    stmt = (
        select(Order)
        .options(selectinload(Order.order_items))
        .where(Order.id == order_id, Order.deleted_at.is_(None))
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_orders(db: AsyncSession, user_id: int) -> list[Order]:
    stmt = (
        select(Order)
        .options(selectinload(Order.order_items))
        .where(Order.user_id == user_id, Order.deleted_at.is_(None))
        .order_by(Order.created_at.desc())
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def update(
    db: AsyncSession,
    order: Order,
    shipping_address: str | None = None,
    items: list[dict] | None = None,
    new_total: float | None = None,
) -> Order:
    if shipping_address is not None:
        order.shipping_address = shipping_address
    if new_total is not None:
        order.total_amount = new_total

    if items is not None:
        for old_item in order.order_items:
            await db.delete(old_item)
        await db.flush()

        for item in items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item["product_id"],
                quantity=item["quantity"],
                unit_price=item["unit_price"],
                subtotal=item["subtotal"],
            )
            db.add(order_item)

    await db.commit()
    db.expire_all()
    return await get_by_id(db, order.id)


async def update_status(db: AsyncSession, order: Order, status: OrderStatus) -> Order:
    order.status = status
    await db.commit()
    db.expire_all()
    return await get_by_id(db, order.id)
