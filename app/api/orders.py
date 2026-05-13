from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.db.connection import get_db
from app.db.models import User
from app.schemas.order import OrderCreate, OrderResponse, OrderUpdate
from app.services import order as order_service
from app.utils.logger import logger

router = APIRouter()


@router.post("/", response_model=OrderResponse)
async def create_order(
    data: OrderCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    logger.info(f"Creating order for user {current_user.id} with {len(data.items)} item(s)")
    order = await order_service.create_order(db, current_user, data)
    logger.info(f"Order {order.id} created for user {current_user.id}")
    return order


@router.get("/", response_model=list[OrderResponse])
async def list_orders(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    logger.info(f"Listing orders for user {current_user.id}")
    return await order_service.list_orders(db, current_user)


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    logger.info(f"Fetching order {order_id} for user {current_user.id}")
    return await order_service.get_order(db, current_user, order_id)


@router.put("/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: int,
    data: OrderUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    logger.info(f"Updating order {order_id} for user {current_user.id}")
    order = await order_service.update_order(db, current_user, order_id, data)
    logger.info(f"Order {order_id} updated successfully")
    return order


@router.post("/{order_id}/cancel", response_model=OrderResponse)
async def cancel_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    logger.info(f"Cancelling order {order_id} for user {current_user.id}")
    order = await order_service.cancel_order(db, current_user, order_id)
    logger.info(f"Order {order_id} cancelled")
    return order
