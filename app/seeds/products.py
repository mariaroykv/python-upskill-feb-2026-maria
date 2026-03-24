"""Seed script: inserts sample products into the database.

Usage:
    uv run python -m app.seeds.products
"""

import asyncio

from sqlalchemy import select

from app.db.connection import AsyncSessionLocal
from app.db.models import Product

PRODUCTS = [
    {"name": "Wireless Mouse", "description": "Ergonomic wireless mouse", "price": 29.99, "stock_quantity": 150},
    {"name": "Mechanical Keyboard", "description": "RGB mechanical keyboard", "price": 79.99, "stock_quantity": 80},
    {"name": "USB-C Hub", "description": "7-in-1 USB-C adapter", "price": 49.99, "stock_quantity": 200},
    {"name": "Monitor Stand", "description": "Adjustable monitor stand", "price": 39.99, "stock_quantity": 60},
    {"name": "Webcam HD", "description": "1080p HD webcam", "price": 59.99, "stock_quantity": 100},
    {"name": "Desk Lamp", "description": "LED desk lamp with dimmer", "price": 34.99, "stock_quantity": 120},
    {"name": "Laptop Sleeve", "description": "15-inch neoprene sleeve", "price": 19.99, "stock_quantity": 300},
    {"name": "Bluetooth Speaker", "description": "Portable bluetooth speaker", "price": 44.99, "stock_quantity": 90},
    {"name": "Mouse Pad XL", "description": "Extended gaming mouse pad", "price": 14.99, "stock_quantity": 250},
    {"name": "Cable Organizer", "description": "Silicone cable management clips", "price": 9.99, "stock_quantity": 500},
    {"name": "Noise Cancelling Headphones", "description": "Over-ear ANC headphones", "price": 149.99, "stock_quantity": 50},
    {"name": "Laptop Stand", "description": "Aluminum foldable laptop stand", "price": 54.99, "stock_quantity": 70},
    {"name": "Wireless Charger", "description": "15W fast wireless charger", "price": 24.99, "stock_quantity": 180},
    {"name": "External SSD 1TB", "description": "Portable USB-C SSD", "price": 89.99, "stock_quantity": 40},
    {"name": "Webcam Light", "description": "Ring light for video calls", "price": 22.99, "stock_quantity": 110},
]


async def seed():
    async with AsyncSessionLocal() as db:
        existing = await db.execute(select(Product).limit(1))
        if existing.scalar_one_or_none():
            print("Products already seeded, skipping.")
            return

        for data in PRODUCTS:
            db.add(Product(**data))
        await db.commit()
        print(f"Seeded {len(PRODUCTS)} products.")


if __name__ == "__main__":
    asyncio.run(seed())
