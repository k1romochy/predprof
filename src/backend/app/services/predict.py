import io
import math
import uuid

import httpx
import numpy as np

from ..core.config import settings


async def call_ml_predict(signals: list[list[float]]) -> list[dict]:
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{settings.ml_service_url}/predict",
            json={"signals": signals},
        )
        response.raise_for_status()
        return response.json()["predictions"]


def load_npz(file_bytes: bytes) -> tuple[np.ndarray, np.ndarray]:
    data = np.load(io.BytesIO(file_bytes))
    return data["test_x"], data["test_y"]


def normalize_labels(test_y: np.ndarray) -> np.ndarray:
    if test_y.dtype.kind in ("U", "S", "O"):
        unique_sorted = sorted(set(test_y.flat))
        mapping = {v: i for i, v in enumerate(unique_sorted)}
        return np.array([mapping[v] for v in test_y.flat], dtype=int)
    return test_y.astype(int).flatten()


def flatten_signals(test_x: np.ndarray) -> list[list[float]]:
    if test_x.ndim == 3:
        return test_x.reshape(test_x.shape[0], -1).tolist()
    return test_x.tolist()


def compute_metrics(
    true_labels: list[int],
    predicted_labels: list[int],
    confidences: list[float],
) -> tuple[float, float]:
    total = len(true_labels)
    if total == 0:
        return 0.0, 0.0

    correct = sum(1 for t, p in zip(true_labels, predicted_labels) if t == p)
    accuracy = correct / total

    eps = 1e-7
    loss = 0.0
    for t, p, c in zip(true_labels, predicted_labels, confidences):
        if t == p:
            loss += -math.log(max(c, eps))
        else:
            loss += -math.log(max(1.0 - c, eps))
    loss /= total

    return accuracy, loss


def generate_session_id() -> str:
    return str(uuid.uuid4())
