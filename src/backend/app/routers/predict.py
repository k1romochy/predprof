import io

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_session
from ..dependencies.auth import get_current_user
from ..models.user import User
from ..repositories.test_result import TestResultRepository
from ..schemas.predict import PredictResponse, PredictionItem
from ..services.predict import (
    call_ml_predict,
    compute_metrics,
    flatten_signals,
    generate_session_id,
    normalize_labels,
)

router = APIRouter(prefix="/api/predict", tags=["predict"])


@router.post("/upload", response_model=PredictResponse)
async def upload(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    contents = await file.read()
    try:
        data = np.load(io.BytesIO(contents))
        keys = set(data.keys())
        if "test_x" in keys and "test_y" in keys:
            test_x, test_y = data["test_x"], data["test_y"]
        elif "valid_x" in keys and "valid_y" in keys:
            test_x, test_y = data["valid_x"], data["valid_y"]
        else:
            raise HTTPException(
                status_code=400,
                detail=".npz must contain test_x/test_y or valid_x/valid_y",
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid .npz file: {str(e)}",
        )

    true_labels = normalize_labels(test_y)
    signals = flatten_signals(test_x)

    ml_predictions = await call_ml_predict(signals)

    predicted_labels = [p["class_id"] for p in ml_predictions]
    confidences = [p["confidence"] for p in ml_predictions]

    accuracy, loss = compute_metrics(true_labels.tolist(), predicted_labels, confidences)

    predictions = [
        PredictionItem(
            index=i,
            true_label=int(true_labels[i]),
            predicted_label=predicted_labels[i],
            correct=int(true_labels[i]) == predicted_labels[i],
            confidence=confidences[i],
        )
        for i in range(len(true_labels))
    ]

    session_id = generate_session_id()
    repo = TestResultRepository(session)
    await repo.create(
        user_id=user.id,
        session_id=session_id,
        accuracy=accuracy,
        loss=loss,
        predictions=[p.model_dump() for p in predictions],
    )

    return PredictResponse(
        accuracy=accuracy,
        loss=loss,
        total=len(predictions),
        predictions=predictions,
    )
