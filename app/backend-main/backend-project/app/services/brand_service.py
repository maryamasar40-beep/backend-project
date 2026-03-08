from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Brand


async def create_brand_service(db: AsyncSession, payload) -> Brand | None:
    result = await db.execute(select(Brand).where(Brand.name == payload.name.strip()))
    existing = result.scalar_one_or_none()
    if existing is not None:
        return None

    brand = Brand(
        name=payload.name.strip(),
        domains=payload.domains,
        logo_embeddings=payload.logo_embeddings,
        colors_json=payload.colors_json,
    )
    db.add(brand)
    await db.commit()
    await db.refresh(brand)
    return brand


async def list_brands_service(db: AsyncSession) -> list[Brand]:
    result = await db.execute(select(Brand))
    return list(result.scalars().all())


async def get_brand_by_id_service(db: AsyncSession, brand_id: int) -> Brand | None:
    result = await db.execute(select(Brand).where(Brand.id == brand_id))
    return result.scalar_one_or_none()


async def update_brand_service(db: AsyncSession, brand_id: int, payload) -> Brand | None:
    brand = await get_brand_by_id_service(db, brand_id)
    if brand is None:
        return None

    if payload.name is not None:
        brand.name = payload.name.strip()
    if payload.domains is not None:
        brand.domains = payload.domains
    if payload.logo_embeddings is not None:
        brand.logo_embeddings = payload.logo_embeddings
    if payload.colors_json is not None:
        brand.colors_json = payload.colors_json

    await db.commit()
    await db.refresh(brand)
    return brand


async def delete_brand_service(db: AsyncSession, brand_id: int) -> bool:
    brand = await get_brand_by_id_service(db, brand_id)
    if brand is None:
        return False
    await db.delete(brand)
    await db.commit()
    return True
