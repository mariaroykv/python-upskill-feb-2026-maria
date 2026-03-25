from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import user as user_repo
from app.schemas.auth import Token, UserLogin, UserRegister, UserResponse
from app.utils.security import create_access_token, hash_password, verify_password


async def register(db: AsyncSession, data: UserRegister) -> UserResponse:
    if await user_repo.get_by_email(db, data.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    user = await user_repo.create(
        db,
        email=data.email,
        hashed_password=hash_password(data.password),
        full_name=data.full_name,
    )
    return UserResponse.model_validate(user)


async def login(db: AsyncSession, data: UserLogin) -> Token:
    user = await user_repo.get_by_email(db, data.email)
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(data={"sub": str(user.id)})
    return Token(access_token=token)
