from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import create_access_token, get_current_user, require_admin
from app.db import get_db
from app.rate_limit import limit_by_ip
from app.schemas import TokenResponse, UserLogin, UserRegister, UserResponse, UserRoleUpdate
from app.services.user_service import (
    authenticate_user_service,
    create_user_service,
    update_user_role_service,
)

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    payload: UserRegister,
    db: AsyncSession = Depends(get_db),
    _=Depends(limit_by_ip("register")),
):
    user = await create_user_service(db, payload.email, payload.password)
    if user is None:
        raise HTTPException(status_code=409, detail="Email already exists")
    return user


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: UserLogin,
    db: AsyncSession = Depends(get_db),
    _=Depends(limit_by_ip("login")),
):
    user = await authenticate_user_service(db, payload.email, payload.password)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_access_token(user.id, user.email)
    return {"access_token": token}


@router.get("/me", response_model=UserResponse)
async def me(current_user=Depends(get_current_user)):
    return current_user


@router.patch("/users/{user_id}/role", response_model=UserResponse)
async def update_user_role(
    user_id: int,
    payload: UserRoleUpdate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    user = await update_user_role_service(db, user_id, payload.role)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found or invalid role")
    return user
