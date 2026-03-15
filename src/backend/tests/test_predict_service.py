import math
import uuid

import numpy as np
import pytest

from app.services.predict import (
    compute_metrics,
    flatten_signals,
    generate_session_id,
    load_npz,
    normalize_labels,
)


class TestComputeMetrics:
    def test_perfect_predictions(self):
        true = [0, 1, 2]
        pred = [0, 1, 2]
        conf = [0.9, 0.8, 0.95]
        acc, loss = compute_metrics(true, pred, conf)
        assert acc == 1.0
        assert loss > 0

    def test_all_wrong(self):
        true = [0, 1, 2]
        pred = [1, 2, 0]
        conf = [0.9, 0.8, 0.95]
        acc, loss = compute_metrics(true, pred, conf)
        assert acc == 0.0
        assert loss > 0

    def test_partial(self):
        true = [0, 1, 2, 3]
        pred = [0, 1, 0, 0]
        conf = [0.9, 0.8, 0.7, 0.6]
        acc, _ = compute_metrics(true, pred, conf)
        assert acc == pytest.approx(0.5)

    def test_empty(self):
        acc, loss = compute_metrics([], [], [])
        assert acc == 0.0
        assert loss == 0.0

    def test_loss_value_correct(self):
        true = [0]
        pred = [0]
        conf = [0.8]
        _, loss = compute_metrics(true, pred, conf)
        assert loss == pytest.approx(-math.log(0.8), abs=1e-6)

    def test_loss_wrong_prediction(self):
        true = [0]
        pred = [1]
        conf = [0.8]
        _, loss = compute_metrics(true, pred, conf)
        assert loss == pytest.approx(-math.log(0.2), abs=1e-6)

    def test_confidence_zero_no_crash(self):
        acc, loss = compute_metrics([0], [0], [0.0])
        assert acc == 1.0
        assert math.isfinite(loss)


class TestNormalizeLabels:
    def test_int_array(self):
        arr = np.array([2, 0, 1, 2])
        result = normalize_labels(arr)
        np.testing.assert_array_equal(result, [2, 0, 1, 2])

    def test_float_to_int(self):
        arr = np.array([2.0, 0.0, 1.0])
        result = normalize_labels(arr)
        assert result.dtype == int
        np.testing.assert_array_equal(result, [2, 0, 1])

    def test_string_labels(self):
        arr = np.array(["cat", "dog", "cat", "bird"])
        result = normalize_labels(arr)
        assert result.dtype == int
        assert len(result) == 4
        assert result[0] == result[2]  # "cat" == "cat"
        assert result[1] != result[3]  # "dog" != "bird"

    def test_2d_flatten(self):
        arr = np.array([[0], [1], [2]])
        result = normalize_labels(arr)
        np.testing.assert_array_equal(result, [0, 1, 2])


class TestFlattenSignals:
    def test_2d_passthrough(self):
        arr = np.array([[1.0, 2.0], [3.0, 4.0]])
        result = flatten_signals(arr)
        assert result == [[1.0, 2.0], [3.0, 4.0]]

    def test_3d_reshape(self):
        arr = np.ones((3, 10, 2))
        result = flatten_signals(arr)
        assert len(result) == 3
        assert len(result[0]) == 20


class TestLoadNpz:
    def test_round_trip(self, tmp_path):
        test_x = np.random.randn(5, 100).astype(np.float32)
        test_y = np.array([0, 1, 2, 3, 4])
        path = tmp_path / "data.npz"
        np.savez(path, test_x=test_x, test_y=test_y)
        loaded_x, loaded_y = load_npz(path.read_bytes())
        np.testing.assert_array_almost_equal(loaded_x, test_x)
        np.testing.assert_array_equal(loaded_y, test_y)


class TestGenerateSessionId:
    def test_is_valid_uuid(self):
        sid = generate_session_id()
        uuid.UUID(sid)

    def test_unique(self):
        ids = {generate_session_id() for _ in range(100)}
        assert len(ids) == 100
