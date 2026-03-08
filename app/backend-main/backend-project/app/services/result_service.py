from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Result, Scan


async def create_result_service(db: AsyncSession, result_data):
    scan_result = await db.execute(select(Scan).where(Scan.id == result_data.scan_id))
    scan = scan_result.scalar_one_or_none()
    if scan is None:
        return None

    new_result = Result(
        scan_id=result_data.scan_id,
        risk_score=result_data.risk_score,
        classification=result_data.classification,
        details_json=result_data.details_json,
        model_version=result_data.model_version,
    )

    db.add(new_result)
    await db.commit()
    await db.refresh(new_result)
    return new_result


async def get_all_results_service(db: AsyncSession):
    result = await db.execute(select(Result))
    results = result.scalars().all()
    return results


async def get_result_by_id_service(db: AsyncSession, result_id: int):
    result = await db.execute(select(Result).where(Result.id == result_id))
    one_result = result.scalar_one_or_none()
    return one_result


async def get_result_by_scan_id_service(db: AsyncSession, scan_id: int):
    result = await db.execute(select(Result).where(Result.scan_id == scan_id))
    one_result = result.scalar_one_or_none()
    return one_result
