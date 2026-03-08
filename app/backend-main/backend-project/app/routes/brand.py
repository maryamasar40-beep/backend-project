from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import require_admin
from app.db import get_db
from app.rate_limit import limit_by_user_or_ip
from app.schemas import BrandCreate, BrandListResponse, BrandResponse, BrandUpdate
from app.services.brand_service import (
    create_brand_service,
    delete_brand_service,
    get_brand_by_id_service,
    list_brands_service,
    update_brand_service,
)

router = APIRouter(prefix="/api/v1", tags=["brands"])


@router.get("/brands", response_model=BrandListResponse)
async def list_brands(db: AsyncSession = Depends(get_db)):
    brands = await list_brands_service(db)
    return {"brands": brands}


@router.get("/brand/{brand_id}", response_model=BrandResponse)
async def get_brand(brand_id: int, db: AsyncSession = Depends(get_db)):
    brand = await get_brand_by_id_service(db, brand_id)
    if brand is None:
        raise HTTPException(status_code=404, detail="Brand not found")
    return brand


@router.post("/brand", response_model=BrandResponse, status_code=status.HTTP_201_CREATED)
async def create_brand(
    payload: BrandCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
    __=Depends(limit_by_user_or_ip("brand-write")),
):
    brand = await create_brand_service(db, payload)
    if brand is None:
        raise HTTPException(status_code=409, detail="Brand name already exists")
    return brand


@router.put("/brand/{brand_id}", response_model=BrandResponse)
async def update_brand(
    brand_id: int,
    payload: BrandUpdate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
    __=Depends(limit_by_user_or_ip("brand-write")),
):
    brand = await update_brand_service(db, brand_id, payload)
    if brand is None:
        raise HTTPException(status_code=404, detail="Brand not found")
    return brand


@router.delete("/brand/{brand_id}")
async def delete_brand(
    brand_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
    __=Depends(limit_by_user_or_ip("brand-write")),
):
    deleted = await delete_brand_service(db, brand_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Brand not found")
    return {"message": "brand deleted successfully"}
