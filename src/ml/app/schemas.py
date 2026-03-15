from pydantic import BaseModel


class PredictRequest(BaseModel):
    signals: list[list[float]]


class SinglePrediction(BaseModel):
    class_id: int
    label: str
    confidence: float


class PredictResponse(BaseModel):
    predictions: list[SinglePrediction]


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
