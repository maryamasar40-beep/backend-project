from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.db import get_db
from app.rate_limit import limit_by_user_or_ip
from app.schemas import (
    HashCheckRequest,
    HashCheckResponse,
    ScanListResponse,
    ScanRequest,
    ScanResponse,
    ScanUpdateRequest,
)
from app.services.scan_service import (
    check_hash_match_service,
    create_scan_service,
    delete_scan_service,
    get_all_scans_service,
    get_scan_by_id_service,
    update_scan_service,
)

router = APIRouter(prefix="/api/v1", tags=["scans"])


@router.post("/scan", response_model=ScanResponse)
async def create_scan(
    scan: ScanRequest,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
    __=Depends(limit_by_user_or_ip("scan-write")),
):
    new_scan = await create_scan_service(db, scan)
    return new_scan


@router.get("/scans", response_model=ScanListResponse)
async def get_scans(db: AsyncSession = Depends(get_db)):
    scans = await get_all_scans_service(db)
    return {"scans": scans}


@router.get("/scan/{scan_id}", response_model=ScanResponse)
async def get_scan_by_id(scan_id: int, db: AsyncSession = Depends(get_db)):
    scan = await get_scan_by_id_service(db, scan_id)

    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    return scan


@router.delete("/scan/{scan_id}")
async def delete_scan(
    scan_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
    __=Depends(limit_by_user_or_ip("scan-write")),
):
    scan = await delete_scan_service(db, scan_id)

    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    return {"message": "scan deleted successfully"}


@router.put("/scan/{scan_id}", response_model=ScanResponse)
async def update_scan(
    scan_id: int,
    scan_data: ScanUpdateRequest,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
    __=Depends(limit_by_user_or_ip("scan-write")),
):
    updated_scan = await update_scan_service(db, scan_id, scan_data)

    if not updated_scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    return updated_scan


@router.post("/hash-check", response_model=HashCheckResponse)
async def hash_check(payload: HashCheckRequest, db: AsyncSession = Depends(get_db)):
    result = await check_hash_match_service(db, payload.screenshot_hash, payload.max_distance)
    return result
