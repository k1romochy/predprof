from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.training_history import TrainingHistory


class TrainingHistoryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self) -> list[TrainingHistory]:
        result = await self.session.execute(
            select(TrainingHistory).order_by(TrainingHistory.epoch)
        )
        return list(result.scalars().all())

    async def count(self) -> int:
        result = await self.session.execute(
            select(func.count(TrainingHistory.id))
        )
        return result.scalar_one()

    async def bulk_create(self, records: list[dict]) -> None:
        objects = [TrainingHistory(**r) for r in records]
        self.session.add_all(objects)
        await self.session.commit()
