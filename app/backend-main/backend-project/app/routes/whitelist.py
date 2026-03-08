from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.db import get_db
from app.rate_limit import limit_by_user_or_ip
from app.schemas import WhitelistCheckResponse, WhitelistCreate, WhitelistResponse
from app.services.whitelist_service import create_whitelist_entry_service, whitelist_check_service

router = APIRouter(prefix="/api/v1", tags=["whitelist"])


@router.post("/whitelist", response_model=WhitelistResponse)
async def create_whitelist_entry(
    payload: WhitelistCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
    __=Depends(limit_by_user_or_ip("whitelist-write")),
):
    entry = await create_whitelist_entry_service(db, payload)
    return entry


@router.get("/whitelist/check", response_model=WhitelistCheckResponse)
async def whitelist_check(domain: str = Query(...), db: AsyncSession = Depends(get_db)):
    return await whitelist_check_service(db, domain)
