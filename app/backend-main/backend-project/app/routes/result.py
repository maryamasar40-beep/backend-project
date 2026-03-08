from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.db import get_db
from app.rate_limit import limit_by_user_or_ip
from app.schemas import ResultCreate, ResultListResponse, ResultResponse
from app.services.result_service import (
    create_result_service,
    get_all_results_service,
    get_result_by_id_service,
    get_result_by_scan_id_service,
)

router = APIRouter(prefix="/api/v1", tags=["results"])


@router.post("/result", response_model=ResultResponse)
async def create_result(
    result_data: ResultCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
    __=Depends(limit_by_user_or_ip("result-write")),
):
    new_result = await create_result_service(db, result_data)
    if not new_result:
        raise HTTPException(status_code=404, detail="Scan not found")
    return new_result


@router.get("/results", response_model=ResultListResponse)
async def get_results(db: AsyncSession = Depends(get_db)):
    results = await get_all_results_service(db)
    return {"results": results}


@router.get("/result/{result_id}", response_model=ResultResponse)
async def get_result_by_id(result_id: int, db: AsyncSession = Depends(get_db)):
    one_result = await get_result_by_id_service(db, result_id)

    if not one_result:
        raise HTTPException(status_code=404, detail="Result not found")

    return one_result


@router.get("/result/scan/{scan_id}", response_model=ResultResponse)
async def get_result_by_scan_id(scan_id: int, db: AsyncSession = Depends(get_db)):
    one_result = await get_result_by_scan_id_service(db, scan_id)

    if not one_result:
        raise HTTPException(status_code=404, detail="Result not found for this scan")

    return one_result
