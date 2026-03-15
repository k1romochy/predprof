from pydantic import BaseModel


class PredictionItem(BaseModel):
    index: int
    true_label: int
    predicted_label: int
    correct: bool
    confidence: float


class PredictResponse(BaseModel):
    accuracy: float
    loss: float
    total: int
    predictions: list[PredictionItem]
