from pydantic import BaseModel


class EpochStats(BaseModel):
    epoch: int
    val_accuracy: float
    val_loss: float
    train_accuracy: float
    train_loss: float


class TrainingHistoryResponse(BaseModel):
    epochs: list[EpochStats]


class ClassCount(BaseModel):
    class_id: int
    count: int
    label: str = ""


class ClassDistributionResponse(BaseModel):
    classes: list[ClassCount]


class TopClassesResponse(BaseModel):
    top_classes: list[ClassCount]
