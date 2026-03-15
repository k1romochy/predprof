from sqlalchemy import JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class AnalyticsCache(Base):
    __tablename__ = "analytics_cache"

    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    data: Mapped[dict] = mapped_column(JSON, nullable=False)
