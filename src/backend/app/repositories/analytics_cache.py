from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.analytics_cache import AnalyticsCache


class AnalyticsCacheRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_key(self, key: str) -> AnalyticsCache | None:
        result = await self.session.execute(
            select(AnalyticsCache).where(AnalyticsCache.key == key)
        )
        return result.scalar_one_or_none()

    async def count(self) -> int:
        result = await self.session.execute(
            select(func.count(AnalyticsCache.id))
        )
        return result.scalar_one()

    async def upsert(self, key: str, data: dict) -> None:
        existing = await self.get_by_key(key)
        if existing:
            existing.data = data
        else:
            self.session.add(AnalyticsCache(key=key, data=data))
        await self.session.commit()
