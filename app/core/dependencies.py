from fastapi import Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.connection import get_db
from app.db.models import User
from app.repositories import user as user_repo
from app.utils.security import decode_token


async def get_current_user(
    request: Request, db: AsyncSession = Depends(get_db)
) -> User:
    token = request.headers.get("Authorization")
    if not token or not token.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")

    user_id = decode_token(token.split(" ")[1])

    user = await user_repo.get_by_id(db, int(user_id))
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user
