from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Scan


async def create_scan_service(db: AsyncSession, scan):
    new_scan = Scan(
        url=scan.url,
        domain=scan.domain,
        screenshot_hash=scan.screenshot_hash,
        status="pending"
    )

    db.add(new_scan)
    await db.commit()
    await db.refresh(new_scan)

    return new_scan


async def get_all_scans_service(db: AsyncSession):
    result = await db.execute(select(Scan))
    scans = result.scalars().all()
    return scans


async def get_scan_by_id_service(db: AsyncSession, scan_id: int):
    result = await db.execute(select(Scan).where(Scan.id == scan_id))
    scan = result.scalar_one_or_none()
    return scan
async def delete_scan_service(db: AsyncSession, scan_id: int):
    result = await db.execute(select(Scan).where(Scan.id == scan_id))
    scan = result.scalar_one_or_none()

    if not scan:
        return None

    await db.delete(scan)
    await db.commit()
    return scan

async def update_scan_service(db: AsyncSession, scan_id: int, scan_data):
    result = await db.execute(select(Scan).where(Scan.id == scan_id))
    scan = result.scalar_one_or_none()

    if not scan:
        return None

    scan.url = scan_data.url
    scan.domain = scan_data.domain
    scan.screenshot_hash = scan_data.screenshot_hash
    scan.status = scan_data.status

    await db.commit()
    await db.refresh(scan)
    return scan