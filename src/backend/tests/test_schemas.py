import pytest
from pydantic import ValidationError

from app.schemas.analytics import (
    ClassCount,
    ClassDistributionResponse,
    EpochStats,
    TopClassesResponse,
    TrainingHistoryResponse,
)
from app.schemas.auth import LoginRequest, TokenResponse, UserResponse
from app.schemas.predict import PredictionItem, PredictResponse
from app.schemas.admin import CreateUserRequest


class TestEpochStats:
    def test_valid(self):
        s = EpochStats(epoch=1, val_accuracy=0.9, val_loss=0.1, train_accuracy=0.85, train_loss=0.15)
        assert s.epoch == 1
        assert s.val_accuracy == 0.9

    def test_missing_field(self):
        with pytest.raises(ValidationError):
            EpochStats(epoch=1, val_accuracy=0.9)

    def test_wrong_type_coerced(self):
        s = EpochStats(epoch="3", val_accuracy="0.9", val_loss="0.1", train_accuracy="0.8", train_loss="0.2")
        assert s.epoch == 3
        assert isinstance(s.val_accuracy, float)


class TestTrainingHistoryResponse:
    def test_empty_epochs(self):
        r = TrainingHistoryResponse(epochs=[])
        assert r.epochs == []

    def test_with_data(self):
        stats = EpochStats(epoch=1, val_accuracy=0.9, val_loss=0.1, train_accuracy=0.85, train_loss=0.15)
        r = TrainingHistoryResponse(epochs=[stats])
        assert len(r.epochs) == 1


class TestClassCount:
    def test_default_label(self):
        c = ClassCount(class_id=5, count=100)
        assert c.label == ""

    def test_with_label(self):
        c = ClassCount(class_id=1, count=50, label="cat")
        assert c.label == "cat"


class TestClassDistributionResponse:
    def test_serialization(self):
        resp = ClassDistributionResponse(
            classes=[ClassCount(class_id=0, count=10), ClassCount(class_id=1, count=20)]
        )
        data = resp.model_dump()
        assert len(data["classes"]) == 2
        assert data["classes"][0]["class_id"] == 0


class TestTopClassesResponse:
    def test_empty(self):
        resp = TopClassesResponse(top_classes=[])
        assert resp.top_classes == []


class TestPredictionItem:
    def test_valid(self):
        p = PredictionItem(index=0, true_label=3, predicted_label=3, correct=True, confidence=0.95)
        assert p.correct is True

    def test_bool_coercion(self):
        p = PredictionItem(index=0, true_label=0, predicted_label=1, correct=0, confidence=0.5)
        assert p.correct is False

    def test_missing_confidence(self):
        with pytest.raises(ValidationError):
            PredictionItem(index=0, true_label=0, predicted_label=0, correct=True)


class TestPredictResponse:
    def test_full(self):
        item = PredictionItem(index=0, true_label=1, predicted_label=1, correct=True, confidence=0.9)
        r = PredictResponse(accuracy=1.0, loss=0.05, total=1, predictions=[item])
        assert r.total == 1
        assert r.predictions[0].confidence == 0.9

    def test_empty_predictions(self):
        r = PredictResponse(accuracy=0.0, loss=0.0, total=0, predictions=[])
        assert r.predictions == []

    def test_json_round_trip(self):
        item = PredictionItem(index=0, true_label=1, predicted_label=2, correct=False, confidence=0.3)
        r = PredictResponse(accuracy=0.5, loss=0.7, total=1, predictions=[item])
        json_str = r.model_dump_json()
        restored = PredictResponse.model_validate_json(json_str)
        assert restored == r


class TestLoginRequest:
    def test_valid(self):
        req = LoginRequest(username="admin", password="pass123")
        assert req.username == "admin"

    def test_missing_password(self):
        with pytest.raises(ValidationError):
            LoginRequest(username="admin")


class TestUserResponse:
    def test_valid(self):
        u = UserResponse(id=1, username="test", first_name="John", last_name="Doe", role="user")
        assert u.role == "user"

    def test_serialization(self):
        u = UserResponse(id=1, username="test", first_name="A", last_name="B", role="admin")
        d = u.model_dump()
        assert d["id"] == 1
        assert d["role"] == "admin"


class TestTokenResponse:
    def test_valid(self):
        user = UserResponse(id=1, username="x", first_name="F", last_name="L", role="user")
        t = TokenResponse(token="abc.def.ghi", role="user", user=user)
        assert t.token == "abc.def.ghi"

    def test_nested_user(self):
        t = TokenResponse(
            token="tok",
            role="admin",
            user={"id": 2, "username": "u", "first_name": "F", "last_name": "L", "role": "admin"},
        )
        assert t.user.id == 2


class TestCreateUserRequest:
    def test_valid(self):
        req = CreateUserRequest(username="new_user", password="pwd", first_name="A", last_name="B")
        assert req.username == "new_user"

    def test_missing_field(self):
        with pytest.raises(ValidationError):
            CreateUserRequest(username="u", password="p")
