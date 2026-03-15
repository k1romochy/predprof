import json
import logging
from pathlib import Path

import h5py
import numpy as np
import torch

from .model import SignalCNN

logger = logging.getLogger(__name__)

SIGNAL_LENGTH = 80000


def _load_state_from_h5(path: Path) -> dict[str, torch.Tensor]:
    state: dict[str, torch.Tensor] = {}
    with h5py.File(path, "r") as hf:
        for key in hf.keys():
            state[key] = torch.from_numpy(np.array(hf[key]))
    return state


class Predictor:
    def __init__(self, weights_path: Path, mapping_path: Path) -> None:
        with open(mapping_path) as fh:
            raw = json.load(fh)

        self.label_to_id: dict[str, int] = raw["label_to_int"]
        self.id_to_label: dict[int, str] = {
            int(k): v for k, v in raw["int_to_label"].items()
        }
        num_classes = raw.get("num_classes", len(self.label_to_id))

        self._device = torch.device("cpu")
        self.model = SignalCNN(num_classes=num_classes)

        state = _load_state_from_h5(weights_path)
        self.model.load_state_dict(state)
        self.model.to(self._device)
        self.model.eval()

        logger.info(
            "Predictor ready — %d classes, device=%s",
            num_classes,
            self._device,
        )

    def predict_batch(self, signals: list[list[float]]) -> list[dict]:
        arr = np.array(signals, dtype=np.float32)
        if arr.ndim == 1:
            arr = arr.reshape(1, -1)

        x = torch.from_numpy(arr).unsqueeze(1).to(self._device)

        with torch.no_grad():
            logits = self.model(x)
            probs = torch.softmax(logits, dim=1).cpu().numpy()

        results: list[dict] = []
        for row in probs:
            class_id = int(row.argmax())
            results.append({
                "class_id": class_id,
                "label": self.id_to_label[class_id],
                "confidence": round(float(row[class_id]), 6),
            })
        return results
