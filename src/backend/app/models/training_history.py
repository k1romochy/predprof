from sqlalchemy import Float, Integer
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class TrainingHistory(Base):
    __tablename__ = "training_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    epoch: Mapped[int] = mapped_column(Integer, nullable=False)
    val_accuracy: Mapped[float] = mapped_column(Float, nullable=False)
    val_loss: Mapped[float] = mapped_column(Float, nullable=False)
    train_accuracy: Mapped[float] = mapped_column(Float, nullable=False)
    train_loss: Mapped[float] = mapped_column(Float, nullable=False)
