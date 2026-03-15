#!/usr/bin/env python3
"""Check model accuracy on test_sample_1000.npz — should be ~35–40%."""

import numpy as np
from pathlib import Path

TEST_FILE = Path(__file__).resolve().parent / "test_sample_1000.npz"


def main() -> None:
    if not TEST_FILE.exists():
        print("Run create_test_sample.py first")
        return

    data = np.load(TEST_FILE)
    test_x, test_y = data["test_x"], data["test_y"]

    from src.ml.app.predictor import Predictor
    from src.ml.app.config import settings

    p = Predictor(
        settings.weights_path,
        settings.label_mapping_path,
        settings.normalization_path,
    )

    signals = test_x.astype(np.float32).tolist()
    preds = p.predict_batch(signals)

    true_ids = [p.label_to_id[str(y)] for y in test_y]
    pred_ids = [r["class_id"] for r in preds]

    correct = sum(1 for t, pr in zip(true_ids, pred_ids) if t == pr)
    acc = correct / len(true_ids)

    print(f"Model: {settings.weights_path.name}")
    print(f"Accuracy on test_sample_1000.npz: {acc*100:.1f}%")
    print(f"If you see ~35–40% here but 1% in the app, check:")
    print("  1. ML_SERVICE_URL — backend must reach ML (e.g. http://localhost:8001)")
    print("  2. Rebuild Docker: docker compose build ml backend")
    print("  3. ML /labels endpoint exists (added for correct label mapping)")


if __name__ == "__main__":
    main()
