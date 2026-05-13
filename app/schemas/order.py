from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator


class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int

    @field_validator("quantity")
    @classmethod
    def quantity_must_be_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("Quantity must be greater than 0")
        return v


class OrderCreate(BaseModel):
    items: list[OrderItemCreate]
    shipping_address: str | None = None

    @field_validator("items")
    @classmethod
    def items_must_not_be_empty(cls, v: list) -> list:
        if not v:
            raise ValueError("Order must contain at least one item")
        return v


class OrderUpdate(BaseModel):
    items: list[OrderItemCreate] | None = None
    shipping_address: str | None = None

    @field_validator("items")
    @classmethod
    def items_must_not_be_empty(cls, v: list | None) -> list | None:
        if v is not None and not v:
            raise ValueError("Items list cannot be empty if provided")
        return v


class OrderItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    quantity: int
    unit_price: float
    subtotal: float


class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    status: str
    total_amount: float
    shipping_address: str | None
    order_items: list[OrderItemResponse]
    created_at: datetime
    updated_at: datetime
