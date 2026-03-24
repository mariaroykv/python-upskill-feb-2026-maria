import enum

from sqlalchemy import Boolean, Enum, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseModel


class User(BaseModel):
    __tablename__ = "user"

    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String)
    full_name: Mapped[str] = mapped_column(String)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    orders: Mapped[list["Order"]] = relationship("Order", back_populates="user")


class Product(BaseModel):
    __tablename__ = "product"

    name: Mapped[str] = mapped_column(String, unique=True, index=True)
    description: Mapped[str] = mapped_column(String)
    price: Mapped[float] = mapped_column(Float)
    stock_quantity: Mapped[int] = mapped_column(Integer)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)


class OrderStatus(enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class Order(BaseModel):
    __tablename__ = "order"

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus), default=OrderStatus.PENDING
    )
    total_amount: Mapped[float] = mapped_column(Float, nullable=False)
    shipping_address: Mapped[str] = mapped_column(String, nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="orders")
    order_items: Mapped[list["OrderItem"]] = relationship(
        "OrderItem", back_populates="order", cascade="all, delete-orphan"
    )


class OrderItem(BaseModel):
    __tablename__ = "order_item"

    order_id: Mapped[int] = mapped_column(ForeignKey("order.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("product.id"))
    quantity: Mapped[int] = mapped_column(Integer)
    unit_price: Mapped[float] = mapped_column(Float)
    subtotal: Mapped[float] = mapped_column(Float)

    order: Mapped["Order"] = relationship("Order", back_populates="order_items")
    product: Mapped["Product"] = relationship("Product")
