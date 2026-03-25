from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str
    price: float
    stock_quantity: int
    is_available: bool
    created_at: datetime
    updated_at: datetime
