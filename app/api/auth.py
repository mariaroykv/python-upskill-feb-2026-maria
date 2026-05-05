from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.connection import get_db
from app.schemas.auth import Token, UserLogin, UserRegister, UserResponse
from app.services import auth as auth_service
from app.utils.logger import logger

router = APIRouter()


@router.post("/register", response_model=UserResponse)
async def register(data: UserRegister, db: AsyncSession = Depends(get_db)):
    logger.info(f"Register attempt for email: {data.email}")
    user = await auth_service.register(db, data)
    logger.info(f"User registered successfully: {user.id}")
    return user


@router.post("/login", response_model=Token)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    logger.info(f"Login attempt for email: {data.email}")
    token = await auth_service.login(db, data)
    logger.info(f"Login successful for email: {data.email}")
    return token
