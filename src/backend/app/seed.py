import asyncio
import json
import sys

from .core.database import async_session_factory, engine
from .models import Base
from .repositories.analytics_cache import AnalyticsCacheRepository
from .repositories.training_history import TrainingHistoryRepository


async def seed(history_path: str, class_dist_path: str, top_val_path: str):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    with open(history_path) as f:
        history = json.load(f)
    with open(class_dist_path) as f:
        class_dist = json.load(f)
    with open(top_val_path) as f:
        top_val = json.load(f)

    async with async_session_factory() as session:
        th_repo = TrainingHistoryRepository(session)
        count = await th_repo.count()
        if count == 0:
            epochs = len(history["val_accuracy"])
            records = [
                {
                    "epoch": i + 1,
                    "val_accuracy": history["val_accuracy"][i],
                    "val_loss": history["val_loss"][i],
                    "train_accuracy": history["accuracy"][i],
                    "train_loss": history["loss"][i],
                }
                for i in range(epochs)
            ]
            await th_repo.bulk_create(records)
            print(f"Seeded {epochs} training history records")

        ac_repo = AnalyticsCacheRepository(session)
        await ac_repo.upsert("class_distribution", class_dist)
        await ac_repo.upsert("top_val_classes", top_val)
        print("Seeded analytics cache")

    await engine.dispose()


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python -m app.seed <history.json> <class_distribution.json> <top_val.json>")
        sys.exit(1)
    asyncio.run(seed(sys.argv[1], sys.argv[2], sys.argv[3]))
