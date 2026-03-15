from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_session
from ..dependencies.auth import get_current_user
from ..models.user import User
from ..schemas.analytics import (
    ClassDistributionResponse,
    EpochStats,
    TopClassesResponse,
    TrainingHistoryResponse,
)
from ..schemas.predict import PredictResponse
from ..services.analytics import (
    get_class_distribution,
    get_test_accuracy,
    get_top_classes,
    get_training_history,
)

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/training-history", response_model=TrainingHistoryResponse)
async def training_history(
    session: AsyncSession = Depends(get_session),
    _user: User = Depends(get_current_user),
):
    epochs = await get_training_history(session)
    return TrainingHistoryResponse(epochs=[EpochStats(**e) for e in epochs])


@router.get("/class-distribution", response_model=ClassDistributionResponse)
async def class_distribution(
    session: AsyncSession = Depends(get_session),
    _user: User = Depends(get_current_user),
):
    return await get_class_distribution(session)


@router.get("/top-classes", response_model=TopClassesResponse)
async def top_classes(
    session: AsyncSession = Depends(get_session),
    _user: User = Depends(get_current_user),
):
    return await get_top_classes(session)


@router.get("/test-accuracy", response_model=PredictResponse)
async def test_accuracy(
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    return await get_test_accuracy(session, user.id)
