#!/usr/bin/env python3
"""Создаёт небольшой тестовый .npz файл для загрузки в приложение."""

import numpy as np
from pathlib import Path

LABELS = [
    "55_Cancri_Bc", "Gliese_", "Gliese_12_b", "Gliese_163_c", "HD_20794_d",
    "HD_216520_c", "HIP_38594_b", "K2-155d", "K2-288Bb", "K2-332b",
    "K2-72e", "Kepler-155c", "Kepler-174d", "Kepler-186f", "Kepler-22b",
    "Kepler-283c", "Kepler-296e", "Kepler-296f", "Kepler-62e", "Kepler-62f",
]

NUM_SAMPLES = 5
SIGNAL_LENGTH = 80000

np.random.seed(42)

test_x = np.random.randn(NUM_SAMPLES, SIGNAL_LENGTH, 1).astype(np.float32) * 0.1

test_y = np.array([LABELS[i % len(LABELS)] for i in range(NUM_SAMPLES)], dtype="U")

out_path = Path(__file__).parent.parent / "test_data.npz"
np.savez(out_path, test_x=test_x, test_y=test_y)

print(f"Создан: {out_path}")
print(f"  test_x: {test_x.shape}, dtype={test_x.dtype}")
print(f"  test_y: {test_y.shape} — {list(test_y)}")
