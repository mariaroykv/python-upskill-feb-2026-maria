from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.connection import get_db
from app.schemas.auth import Token, UserLogin, UserRegister, UserResponse
from app.services import auth as auth_service

router = APIRouter()


@router.post("/register", response_model=UserResponse)
async def register(data: UserRegister, db: AsyncSession = Depends(get_db)):
    return await auth_service.register(db, data)


@router.post("/login", response_model=Token)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    return await auth_service.login(db, data)
