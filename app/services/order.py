from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import OrderStatus, User
from app.repositories import order as order_repo
from app.repositories import product as product_repo
from app.schemas.order import OrderCreate, OrderResponse, OrderUpdate


async def _validate_items(db: AsyncSession, items):
    """Validate products exist and are available, return enriched item dicts."""
    enriched = []
    for item in items:
        product = await product_repo.get_by_id(db, item.product_id)
        if not product:
            raise HTTPException(
                status_code=400, detail=f"Product {item.product_id} not found"
            )
        if not product.is_available:
            raise HTTPException(
                status_code=400, detail=f"Product '{product.name}' is not available"
            )
        if item.quantity > product.stock_quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for '{product.name}' (available: {product.stock_quantity})",
            )
        enriched.append(
            {
                "product_id": product.id,
                "quantity": item.quantity,
                "unit_price": product.price,
                "subtotal": product.price * item.quantity,
            }
        )
    return enriched


async def create_order(
    db: AsyncSession, user: User, data: OrderCreate
) -> OrderResponse:
    if not data.items:
        raise HTTPException(status_code=400, detail="Order must have at least one item")

    enriched = await _validate_items(db, data.items)
    total = sum(i["subtotal"] for i in enriched)

    order = await order_repo.create(
        db,
        user_id=user.id,
        total_amount=total,
        shipping_address=data.shipping_address,
        items=enriched,
    )
    return _to_response(order)


async def get_order(db: AsyncSession, user: User, order_id: int) -> OrderResponse:
    order = await order_repo.get_by_id(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.user_id != user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    return _to_response(order)


async def list_orders(db: AsyncSession, user: User) -> list[OrderResponse]:
    orders = await order_repo.get_user_orders(db, user.id)
    return [_to_response(o) for o in orders]


async def update_order(
    db: AsyncSession, user: User, order_id: int, data: OrderUpdate
) -> OrderResponse:
    order = await order_repo.get_by_id(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.user_id != user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    if order.status != OrderStatus.PENDING:
        raise HTTPException(status_code=400, detail="Only pending orders can be updated")

    enriched = None
    new_total = None
    if data.items is not None:
        if not data.items:
            raise HTTPException(
                status_code=400, detail="Order must have at least one item"
            )
        enriched = await _validate_items(db, data.items)
        new_total = sum(i["subtotal"] for i in enriched)

    order = await order_repo.update(
        db,
        order,
        shipping_address=data.shipping_address,
        items=enriched,
        new_total=new_total,
    )
    return _to_response(order)


async def cancel_order(db: AsyncSession, user: User, order_id: int) -> OrderResponse:
    order = await order_repo.get_by_id(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.user_id != user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    if order.status == OrderStatus.CANCELLED:
        raise HTTPException(status_code=400, detail="Order is already cancelled")
    if order.status == OrderStatus.DELIVERED:
        raise HTTPException(status_code=400, detail="Delivered orders cannot be cancelled")

    order = await order_repo.update_status(db, order, OrderStatus.CANCELLED)
    return _to_response(order)


def _to_response(order) -> OrderResponse:
    return OrderResponse(
        id=order.id,
        user_id=order.user_id,
        status=order.status.value,
        total_amount=order.total_amount,
        shipping_address=order.shipping_address,
        order_items=order.order_items,
        created_at=order.created_at,
        updated_at=order.updated_at,
    )
