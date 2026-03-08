from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Feedback, Result


async def create_feedback_service(db: AsyncSession, feedback_data):
    result_row = await db.execute(select(Result).where(Result.id == feedback_data.result_id))
    one_result = result_row.scalar_one_or_none()
    if one_result is None:
        return None

    new_feedback = Feedback(
        result_id=feedback_data.result_id,
        user_verdict=feedback_data.user_verdict,
        comment=feedback_data.comment,
    )

    db.add(new_feedback)
    await db.commit()
    await db.refresh(new_feedback)
    return new_feedback


async def get_all_feedback_service(db: AsyncSession):
    result = await db.execute(select(Feedback))
    feedback_list = result.scalars().all()
    return feedback_list


async def get_feedback_by_id_service(db: AsyncSession, feedback_id: int):
    result = await db.execute(select(Feedback).where(Feedback.id == feedback_id))
    one_feedback = result.scalar_one_or_none()
    return one_feedback


async def get_feedback_by_result_id_service(db: AsyncSession, result_id: int):
    result = await db.execute(select(Feedback).where(Feedback.result_id == result_id))
    feedback_list = result.scalars().all()
    return feedback_list
