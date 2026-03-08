from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Whitelist


async def create_whitelist_entry_service(db: AsyncSession, data):
    domain = data.domain.strip().lower()
    row = await db.execute(select(Whitelist).where(Whitelist.domain == domain))
    existing = row.scalar_one_or_none()
    if existing:
        return existing

    entry = Whitelist(domain=domain, logo_hash=data.logo_hash)
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return entry


async def whitelist_check_service(db: AsyncSession, domain: str):
    normalized = domain.strip().lower()
    row = await db.execute(select(Whitelist).where(Whitelist.domain == normalized))
    entry = row.scalar_one_or_none()
    if entry is None:
        return {"domain": normalized, "whitelisted": False, "matched_logo_hash": None}
    return {"domain": normalized, "whitelisted": True, "matched_logo_hash": entry.logo_hash}
