from sqlalchemy.ext.asyncio import AsyncSession

from ..repositories.analytics_cache import AnalyticsCacheRepository
from ..repositories.test_result import TestResultRepository
from ..repositories.training_history import TrainingHistoryRepository


async def get_training_history(session: AsyncSession) -> list[dict]:
    repo = TrainingHistoryRepository(session)
    rows = await repo.get_all()
    return [
        {
            "epoch": r.epoch,
            "val_accuracy": r.val_accuracy,
            "val_loss": r.val_loss,
            "train_accuracy": r.train_accuracy,
            "train_loss": r.train_loss,
        }
        for r in rows
    ]


async def get_class_distribution(session: AsyncSession) -> dict:
    repo = AnalyticsCacheRepository(session)
    entry = await repo.get_by_key("class_distribution")
    if entry:
        return entry.data
    return {"classes": []}


async def get_top_classes(session: AsyncSession) -> dict:
    repo = AnalyticsCacheRepository(session)
    entry = await repo.get_by_key("top_val_classes")
    if entry:
        return entry.data
    return {"top_classes": []}


async def get_test_accuracy(session: AsyncSession, user_id: int) -> dict:
    repo = TestResultRepository(session)
    result = await repo.get_latest_by_user(user_id)
    if result:
        return {
            "accuracy": result.accuracy,
            "loss": result.loss,
            "total": len(result.predictions),
            "predictions": result.predictions,
        }
    return {"accuracy": 0.0, "loss": 0.0, "total": 0, "predictions": []}
