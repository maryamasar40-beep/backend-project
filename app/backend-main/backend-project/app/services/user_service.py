from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import hash_password, verify_password
from app.models import User


async def create_user_service(db: AsyncSession, email: str, password: str) -> User | None:
    normalized_email = email.strip().lower()
    result = await db.execute(select(User).where(User.email == normalized_email))
    existing_user = result.scalar_one_or_none()
    if existing_user is not None:
        return None

    users_count_result = await db.execute(select(func.count()).select_from(User))
    users_count = users_count_result.scalar_one()
    role = "admin" if users_count == 0 else "analyst"

    user = User(email=normalized_email, hashed_password=hash_password(password), role=role)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def authenticate_user_service(db: AsyncSession, email: str, password: str) -> User | None:
    normalized_email = email.strip().lower()
    result = await db.execute(select(User).where(User.email == normalized_email))
    user = result.scalar_one_or_none()
    if user is None:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


async def update_user_role_service(db: AsyncSession, user_id: int, role: str) -> User | None:
    if role not in {"admin", "analyst"}:
        return None
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        return None
    user.role = role
    await db.commit()
    await db.refresh(user)
    return user
