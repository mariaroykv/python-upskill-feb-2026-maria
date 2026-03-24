from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.db.connection import get_db
from app.db.models import User
from app.schemas.order import OrderCreate, OrderResponse, OrderUpdate
from app.services import order as order_service

router = APIRouter()


@router.post("/", response_model=OrderResponse)
async def create_order(
    data: OrderCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await order_service.create_order(db, current_user, data)


@router.get("/", response_model=list[OrderResponse])
async def list_orders(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await order_service.list_orders(db, current_user)


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await order_service.get_order(db, current_user, order_id)


@router.put("/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: int,
    data: OrderUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await order_service.update_order(db, current_user, order_id, data)


@router.post("/{order_id}/cancel", response_model=OrderResponse)
async def cancel_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await order_service.cancel_order(db, current_user, order_id)
