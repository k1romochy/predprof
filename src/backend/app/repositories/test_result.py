from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.test_result import TestResult


class TestResultRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        user_id: int,
        session_id: str,
        accuracy: float,
        loss: float,
        predictions: list[dict],
    ) -> TestResult:
        record = TestResult(
            user_id=user_id,
            session_id=session_id,
            accuracy=accuracy,
            loss=loss,
            predictions=predictions,
        )
        self.session.add(record)
        await self.session.commit()
        await self.session.refresh(record)
        return record

    async def get_latest_by_user(self, user_id: int) -> TestResult | None:
        result = await self.session.execute(
            select(TestResult)
            .where(TestResult.user_id == user_id)
            .order_by(TestResult.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()
