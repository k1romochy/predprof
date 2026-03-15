import json
import logging
from collections import Counter
from pathlib import Path

import h5py
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from tqdm import tqdm

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
)
log = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_PATH = BASE_DIR / "data" / "Data.npz"
WEIGHTS_DIR = BASE_DIR / "weights"
ARTIFACTS_DIR = BASE_DIR / "artifacts"

NUM_CLASSES = 20
BATCH_SIZE = 32
MAX_EPOCHS = 50
PATIENCE = 10
LR = 1e-3
HEX_PREFIX_LEN = 32


def _get_device() -> torch.device:
    if torch.cuda.is_available():
        return torch.device("cuda")
    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


DEVICE = _get_device()


def extract_planet_name(raw_label: str) -> str:
    return raw_label[HEX_PREFIX_LEN:] if len(raw_label) > HEX_PREFIX_LEN else raw_label


def load_data() -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    raw = np.load(DATA_PATH)
    train_x, train_y = raw["train_x"], raw["train_y"]
    valid_x, valid_y = raw["valid_x"], raw["valid_y"]
    log.info("train_x %s  valid_x %s", train_x.shape, valid_x.shape)
    return train_x, train_y, valid_x, valid_y


def build_label_mapping(
    train_y: np.ndarray,
    valid_y: np.ndarray,
) -> dict[str, int]:
    all_labels = np.concatenate([train_y, valid_y])
    planet_names = sorted({extract_planet_name(lbl) for lbl in all_labels})
    mapping = {name: idx for idx, name in enumerate(planet_names)}
    log.info("Label mapping: %d classes", len(mapping))
    return mapping


def encode_labels(raw_y: np.ndarray, mapping: dict[str, int]) -> np.ndarray:
    return np.array(
        [mapping[extract_planet_name(lbl)] for lbl in raw_y],
        dtype=np.int64,
    )


class SignalCNN(nn.Module):
    def __init__(self, num_classes: int = NUM_CLASSES):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv1d(1, 32, kernel_size=7, padding=3),
            nn.BatchNorm1d(32),
            nn.ReLU(),
            nn.MaxPool1d(4),

            nn.Conv1d(32, 64, kernel_size=5, padding=2),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.MaxPool1d(4),

            nn.Conv1d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.MaxPool1d(4),
        )
        self.head = nn.Sequential(
            nn.AdaptiveAvgPool1d(1),
            nn.Flatten(),
            nn.Dropout(0.3),
            nn.Linear(128, num_classes),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.head(self.features(x))


def compute_class_weights(y_int: np.ndarray, num_classes: int) -> torch.Tensor:
    counts = np.bincount(y_int, minlength=num_classes).astype(float)
    counts = np.maximum(counts, 1.0)
    weights = 1.0 / counts
    weights = weights / weights.sum() * num_classes
    weights = np.minimum(weights, 5.0)
    log.info("Class weights: %s", np.round(weights, 3))
    return torch.from_numpy(weights).float()


def make_loaders(
    train_x: np.ndarray,
    train_y_int: np.ndarray,
    valid_x: np.ndarray,
    valid_y_int: np.ndarray,
) -> tuple[DataLoader, DataLoader]:
    tx = torch.from_numpy(train_x.squeeze(-1)[:, np.newaxis, :]).float()
    ty = torch.from_numpy(train_y_int).long()
    vx = torch.from_numpy(valid_x.squeeze(-1)[:, np.newaxis, :]).float()
    vy = torch.from_numpy(valid_y_int).long()

    train_loader = DataLoader(TensorDataset(tx, ty), batch_size=BATCH_SIZE, shuffle=True)
    valid_loader = DataLoader(TensorDataset(vx, vy), batch_size=BATCH_SIZE)
    return train_loader, valid_loader


def train_model(
    model: nn.Module,
    train_loader: DataLoader,
    valid_loader: DataLoader,
    class_weights: torch.Tensor | None = None,
) -> dict[str, list[float]]:
    model.to(DEVICE)
    optimizer = torch.optim.Adam(model.parameters(), lr=LR)

    criterion = (
        nn.CrossEntropyLoss(weight=class_weights.to(DEVICE))
        if class_weights is not None
        else nn.CrossEntropyLoss()
    )

    history: dict[str, list[float]] = {
        "accuracy": [], "val_accuracy": [], "loss": [], "val_loss": [],
    }
    best_val_acc = 0.0
    patience_counter = 0

    for epoch in range(1, MAX_EPOCHS + 1):
        log.info("── Epoch %02d/%d ──", epoch, MAX_EPOCHS)

        model.train()
        running_loss, correct, total = 0.0, 0, 0
        for xb, yb in tqdm(train_loader, desc=f"  train {epoch}", leave=False):
            xb, yb = xb.to(DEVICE), yb.to(DEVICE)
            optimizer.zero_grad()
            logits = model(xb)
            loss = criterion(logits, yb)
            loss.backward()
            optimizer.step()
            running_loss += loss.item() * xb.size(0)
            correct += (logits.argmax(1) == yb).sum().item()
            total += xb.size(0)

        train_loss = running_loss / total
        train_acc = correct / total

        model.eval()
        val_loss_sum, val_correct, val_total = 0.0, 0, 0
        with torch.no_grad():
            for xb, yb in valid_loader:
                xb, yb = xb.to(DEVICE), yb.to(DEVICE)
                logits = model(xb)
                val_loss_sum += criterion(logits, yb).item() * xb.size(0)
                val_correct += (logits.argmax(1) == yb).sum().item()
                val_total += xb.size(0)

        val_loss = val_loss_sum / val_total
        val_acc = val_correct / val_total

        history["loss"].append(round(train_loss, 6))
        history["accuracy"].append(round(train_acc, 6))
        history["val_loss"].append(round(val_loss, 6))
        history["val_accuracy"].append(round(val_acc, 6))

        log.info(
            "  loss %.4f  acc %.4f  val_loss %.4f  val_acc %.4f",
            train_loss, train_acc, val_loss, val_acc,
        )

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            patience_counter = 0
            save_model_h5(model, WEIGHTS_DIR / "best_model.h5")
            log.info("  ✓ saved best_model.h5 (val_acc=%.4f)", val_acc)
        else:
            patience_counter += 1
            if patience_counter >= PATIENCE:
                log.info("Early stopping at epoch %d", epoch)
                break

    load_model_h5(model, WEIGHTS_DIR / "best_model.h5")
    return history


def save_model_h5(model: nn.Module, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    state = model.state_dict()
    with h5py.File(path, "w") as hf:
        for key, tensor in state.items():
            hf.create_dataset(key, data=tensor.cpu().numpy())


def load_model_h5(model: nn.Module, path: Path) -> None:
    state = {}
    with h5py.File(path, "r") as hf:
        for key in hf.keys():
            state[key] = torch.from_numpy(np.array(hf[key]))
    model.load_state_dict(state)


def save_metrics(history: dict[str, list[float]]) -> None:
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    (ARTIFACTS_DIR / "metrics.json").write_text(
        json.dumps(history, ensure_ascii=False, indent=2),
    )
    log.info("Saved metrics.json")


def save_class_distribution(
    train_y_int: np.ndarray,
    mapping: dict[str, int],
) -> None:
    reverse_map = {v: k for k, v in mapping.items()}
    counts = Counter(train_y_int.tolist())
    dist = [
        {"class_id": cid, "label": reverse_map[cid], "count": counts.get(cid, 0)}
        for cid in range(len(mapping))
    ]
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    (ARTIFACTS_DIR / "class_distribution.json").write_text(
        json.dumps(dist, indent=2),
    )
    log.info("Saved class_distribution.json")


def save_label_mapping(mapping: dict[str, int]) -> None:
    reverse = {v: k for k, v in mapping.items()}
    data = {
        "label_to_int": mapping,
        "int_to_label": {str(k): v for k, v in reverse.items()},
        "num_classes": len(mapping),
    }
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    (ARTIFACTS_DIR / "label_mapping.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
    )
    log.info("Saved label_mapping.json")


def evaluate_and_save(
    model: nn.Module,
    valid_loader: DataLoader,
    valid_y_int: np.ndarray,
    mapping: dict[str, int],
) -> None:
    model.eval()
    criterion = nn.CrossEntropyLoss()
    reverse_map = {v: k for k, v in mapping.items()}

    all_preds: list[int] = []
    loss_sum, total = 0.0, 0

    with torch.no_grad():
        for xb, yb in valid_loader:
            xb, yb = xb.to(DEVICE), yb.to(DEVICE)
            logits = model(xb)
            loss_sum += criterion(logits, yb).item() * xb.size(0)
            total += xb.size(0)
            all_preds.extend(logits.argmax(1).cpu().tolist())

    predicted = np.array(all_preds)
    per_sample_correct = (predicted == valid_y_int).astype(int).tolist()
    val_acc = float(np.mean(per_sample_correct))
    val_loss = loss_sum / total

    top5_counts = Counter(valid_y_int.tolist())
    top5 = dict(sorted(top5_counts.items(), key=lambda kv: -kv[1])[:5])

    result = {
        "val_accuracy": round(val_acc, 6),
        "val_loss": round(val_loss, 6),
        "per_sample_correct": per_sample_correct,
        "predicted_classes": predicted.tolist(),
        "true_classes": valid_y_int.tolist(),
        "top5_valid_classes": {
            str(cid): {"label": reverse_map[cid], "count": cnt}
            for cid, cnt in top5.items()
        },
    }

    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    (ARTIFACTS_DIR / "validation_results.json").write_text(
        json.dumps(result, indent=2),
    )
    log.info("Saved validation_results.json (val_acc=%.4f)", val_acc)


def main() -> None:
    log.info("Device: %s", DEVICE)
    train_x, train_y_raw, valid_x, valid_y_raw = load_data()

    mapping = build_label_mapping(train_y_raw, valid_y_raw)
    train_y_int = encode_labels(train_y_raw, mapping)
    valid_y_int = encode_labels(valid_y_raw, mapping)

    class_weights = compute_class_weights(train_y_int, NUM_CLASSES)
    train_loader, valid_loader = make_loaders(train_x, train_y_int, valid_x, valid_y_int)

    model = SignalCNN(num_classes=NUM_CLASSES)
    param_count = sum(p.numel() for p in model.parameters())
    log.info("Model params: %s", f"{param_count:,}")

    history = train_model(model, train_loader, valid_loader, class_weights=class_weights)

    save_metrics(history)
    save_class_distribution(train_y_int, mapping)
    save_label_mapping(mapping)
    evaluate_and_save(model, valid_loader, valid_y_int, mapping)

    log.info("Done")


if __name__ == "__main__":
    main()
