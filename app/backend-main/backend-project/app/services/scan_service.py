import os

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.cache import get_cached_json, set_cached_json
from app.models import Scan
from app.tasks import analyze_screenshot

ENABLE_ASYNC_TASKS = os.getenv("ENABLE_ASYNC_TASKS", "false").lower() == "true"


async def create_scan_service(db: AsyncSession, scan):
    new_scan = Scan(
        url=scan.url,
        domain=scan.domain,
        screenshot_hash=scan.screenshot_hash,
        status="pending",
    )

    db.add(new_scan)
    await db.commit()
    await db.refresh(new_scan)

    if ENABLE_ASYNC_TASKS:
        try:
            analyze_screenshot.delay(new_scan.id, new_scan.screenshot_hash)
        except Exception:
            pass

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

    if scan_data.url is not None:
        scan.url = scan_data.url
    if scan_data.domain is not None:
        scan.domain = scan_data.domain
    if scan_data.screenshot_hash is not None:
        scan.screenshot_hash = scan_data.screenshot_hash
    if scan_data.status is not None:
        scan.status = scan_data.status

    await db.commit()
    await db.refresh(scan)
    return scan


def _hex_hamming_distance(left: str, right: str) -> int | None:
    if not left or not right or len(left) != len(right):
        return None
    try:
        return (int(left, 16) ^ int(right, 16)).bit_count()
    except ValueError:
        return None


async def check_hash_match_service(db: AsyncSession, screenshot_hash: str, max_distance: int):
    cache_key = f"hash-check:{screenshot_hash}:{max_distance}"
    cached = await get_cached_json(cache_key)
    if cached is not None:
        return cached

    result = await db.execute(select(Scan).where(Scan.screenshot_hash.is_not(None)))
    scans = result.scalars().all()

    nearest_scan = None
    nearest_distance = None
    exact_match = False

    for scan in scans:
        distance = _hex_hamming_distance(scan.screenshot_hash, screenshot_hash)
        if distance is None:
            continue

        if distance == 0:
            exact_match = True

        if distance <= max_distance and (nearest_distance is None or distance < nearest_distance):
            nearest_scan = scan
            nearest_distance = distance

    if nearest_scan is None:
        payload = {"exact_match": exact_match, "nearest_match": None}
        await set_cached_json(cache_key, payload)
        return payload

    payload = {
        "exact_match": exact_match,
        "nearest_match": {"scan_id": nearest_scan.id, "distance": nearest_distance},
    }
    await set_cached_json(cache_key, payload)
    return payload
