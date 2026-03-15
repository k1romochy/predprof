#!/usr/bin/env python3
"""Create a small test .npz from first 1000 rows of Data.npz for upload testing."""

import numpy as np
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent / "src/ml/data/Data.npz"
OUTPUT_PATH = Path(__file__).resolve().parent / "test_sample_1000.npz"
N_SAMPLES = 1000


def main() -> None:
    data = np.load(DATA_PATH)
    valid_x = data["valid_x"]
    valid_y = data["valid_y"]

    test_x = valid_x[:N_SAMPLES]
    test_y = valid_y[:N_SAMPLES]

    np.savez(OUTPUT_PATH, test_x=test_x, test_y=test_y)
    print(f"Saved {OUTPUT_PATH}")
    print(f"  test_x: {test_x.shape}")
    print(f"  test_y: {test_y.shape}")


if __name__ == "__main__":
    main()
