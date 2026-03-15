import json
import logging
from collections import Counter
from pathlib import Path

import h5py
import numpy as np
import torch
import torch.nn as nn
from torch.optim.lr_scheduler import OneCycleLR
from torch.utils.data import DataLoader, TensorDataset
from tqdm import tqdm

from ..model import SignalClassifier

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
NUM_FEATURES = 1600
BATCH_SIZE = 512
MAX_EPOCHS = 15
PATIENCE = 20
LR = 3e-4
GRAD_CLIP = 1.0
LABEL_SMOOTHING = 0.1
NOISE_STD = 0.05

def _get_device() -> torch.device:
    if torch.cuda.is_available():
        return torch.device("cuda")
    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


DEVICE = _get_device()


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
    all_labels = sorted(set(train_y) | set(valid_y))
    mapping = {name: idx for idx, name in enumerate(all_labels)}
    log.info("Label mapping: %d classes", len(mapping))
    return mapping


def encode_labels(raw_y: np.ndarray, mapping: dict[str, int]) -> np.ndarray:
    return np.array([mapping[lbl] for lbl in raw_y], dtype=np.int64)


def compute_class_weights(y_int: np.ndarray, num_classes: int) -> torch.Tensor:
    counts = np.bincount(y_int, minlength=num_classes).astype(float)
    counts = np.maximum(counts, 1.0)
    weights = np.sqrt(counts.mean() / counts)
    weights = np.clip(weights, 0.5, 3.0)
    log.info("Class weights: %s", np.round(weights, 3))
    return torch.from_numpy(weights).float()


def normalize(x: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    mean = x.mean(axis=0, keepdims=True)
    std = x.std(axis=0, keepdims=True) + 1e-8
    return ((x - mean) / std).astype(np.float32), mean, std


def make_loaders(
    train_x: np.ndarray,
    train_y_int: np.ndarray,
    valid_x: np.ndarray,
    valid_y_int: np.ndarray,
) -> tuple[DataLoader, DataLoader, np.ndarray, np.ndarray]:
    train_x_norm, mean, std = normalize(train_x)
    valid_x_norm = ((valid_x - mean) / (std + 1e-8)).astype(np.float32)

    tx = torch.from_numpy(train_x_norm[:, np.newaxis, :]).float()
    ty = torch.from_numpy(train_y_int).long()
    vx = torch.from_numpy(valid_x_norm[:, np.newaxis, :]).float()
    vy = torch.from_numpy(valid_y_int).long()

    use_pin = DEVICE.type == "cuda"
    train_loader = DataLoader(
        TensorDataset(tx, ty),
        batch_size=BATCH_SIZE,
        shuffle=True,
        num_workers=0,
        pin_memory=use_pin,
    )
    valid_loader = DataLoader(
        TensorDataset(vx, vy),
        batch_size=BATCH_SIZE,
        num_workers=0,
        pin_memory=use_pin,
    )
    return train_loader, valid_loader, mean, std


def train_model(
    model: nn.Module,
    train_loader: DataLoader,
    valid_loader: DataLoader,
    class_weights: torch.Tensor | None = None,
) -> dict[str, list[float]]:
    model.to(DEVICE)
    optimizer = torch.optim.AdamW(model.parameters(), lr=LR, weight_decay=1e-4)
    scheduler = OneCycleLR(
        optimizer,
        max_lr=LR * 10,
        epochs=MAX_EPOCHS,
        steps_per_epoch=len(train_loader),
        pct_start=0.1,
        anneal_strategy="cos",
    )

    criterion = nn.CrossEntropyLoss(
        weight=class_weights.to(DEVICE) if class_weights is not None else None,
        label_smoothing=LABEL_SMOOTHING,
    )

    history: dict[str, list[float]] = {
        "accuracy": [], "val_accuracy": [], "loss": [], "val_loss": [],
    }
    best_val_acc = 0.0
    patience_counter = 0

    for epoch in range(1, MAX_EPOCHS + 1):
        log.info("── Epoch %02d/%d  lr=%.2e ──", epoch, MAX_EPOCHS, optimizer.param_groups[0]["lr"])

        model.train()
        running_loss, correct, total = 0.0, 0, 0
        for xb, yb in tqdm(train_loader, desc=f"  train {epoch}", leave=False):
            xb, yb = xb.to(DEVICE), yb.to(DEVICE)
            if NOISE_STD > 0:
                xb = xb + torch.randn_like(xb) * NOISE_STD
            optimizer.zero_grad()
            logits = model(xb)
            loss = criterion(logits, yb)
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), GRAD_CLIP)
            optimizer.step()
            scheduler.step()
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

        if DEVICE.type == "mps":
            torch.mps.empty_cache()

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
            save_model_h5(model, WEIGHTS_DIR / "best-model.h5")
            log.info("  ✓ saved best-model.h5 (val_acc=%.4f)", val_acc)
        else:
            patience_counter += 1
            if patience_counter >= PATIENCE:
                log.info("Early stopping at epoch %d", epoch)
                break

    load_model_h5(model, WEIGHTS_DIR / "best-model.h5")
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


def save_normalization(mean: np.ndarray, std: np.ndarray) -> None:
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    np.savez(ARTIFACTS_DIR / "normalization.npz", mean=mean, std=std)
    log.info("Saved normalization.npz")


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

    num_classes = len(mapping)
    class_weights = compute_class_weights(train_y_int, num_classes)
    train_loader, valid_loader, mean, std = make_loaders(
        train_x, train_y_int, valid_x, valid_y_int,
    )

    model = SignalClassifier(num_features=NUM_FEATURES, num_classes=num_classes)
    param_count = sum(p.numel() for p in model.parameters())
    log.info("Model params: %s", f"{param_count:,}")

    history = train_model(model, train_loader, valid_loader, class_weights=class_weights)

    save_metrics(history)
    save_class_distribution(train_y_int, mapping)
    save_label_mapping(mapping)
    save_normalization(mean, std)
    evaluate_and_save(model, valid_loader, valid_y_int, mapping)

    log.info("Done")


if __name__ == "__main__":
    main()
