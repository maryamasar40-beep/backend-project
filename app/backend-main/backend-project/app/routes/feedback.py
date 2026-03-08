from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.db import get_db
from app.rate_limit import limit_by_user_or_ip
from app.schemas import FeedbackCreate, FeedbackListResponse, FeedbackResponse
from app.services.feedback_service import (
    create_feedback_service,
    get_all_feedback_service,
    get_feedback_by_id_service,
    get_feedback_by_result_id_service,
)

router = APIRouter(prefix="/api/v1", tags=["feedback"])


@router.post("/feedback", response_model=FeedbackResponse)
async def create_feedback(
    feedback_data: FeedbackCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
    __=Depends(limit_by_user_or_ip("feedback-write")),
):
    new_feedback = await create_feedback_service(db, feedback_data)
    if not new_feedback:
        raise HTTPException(status_code=404, detail="Result not found")
    return new_feedback


@router.get("/feedbacks", response_model=FeedbackListResponse)
async def get_feedbacks(db: AsyncSession = Depends(get_db)):
    feedbacks = await get_all_feedback_service(db)
    return {"feedbacks": feedbacks}


@router.get("/feedback/{feedback_id}", response_model=FeedbackResponse)
async def get_feedback_by_id(feedback_id: int, db: AsyncSession = Depends(get_db)):
    one_feedback = await get_feedback_by_id_service(db, feedback_id)

    if not one_feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")

    return one_feedback


@router.get("/feedback/result/{result_id}", response_model=FeedbackListResponse)
async def get_feedback_by_result_id(result_id: int, db: AsyncSession = Depends(get_db)):
    feedbacks = await get_feedback_by_result_id_service(db, result_id)
    return {"feedbacks": feedbacks}
