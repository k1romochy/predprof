import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]


class Settings:
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    host: str = os.getenv("ML_HOST", "0.0.0.0")
    port: int = int(os.getenv("ML_PORT", "8001"))
    weights_path: Path = BASE_DIR / "weights" / "best_model.h5"
    label_mapping_path: Path = BASE_DIR / "artifacts" / "label_mapping.json"


settings = Settings()
