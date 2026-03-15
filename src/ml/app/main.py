import logging

from fastapi import FastAPI

from .config import settings
from .predictor import Predictor
from .schemas import HealthResponse, PredictRequest, PredictResponse

logging.basicConfig(level=getattr(logging, settings.log_level.upper()))
logger = logging.getLogger(__name__)

app = FastAPI(title="ML Service", version="1.0.0")

predictor: Predictor | None = None


@app.on_event("startup")
def load_model() -> None:
    global predictor
    try:
        predictor = Predictor(
            weights_path=settings.weights_path,
            mapping_path=settings.label_mapping_path,
        )
        logger.info("Model loaded successfully")
    except FileNotFoundError:
        logger.warning("Model files not found — /predict will be unavailable")


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        model_loaded=predictor is not None,
    )


@app.post("/predict", response_model=PredictResponse)
def predict(body: PredictRequest) -> PredictResponse:
    if predictor is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail="Model not loaded")

    raw_predictions = predictor.predict_batch(body.signals)
    return PredictResponse(predictions=raw_predictions)
