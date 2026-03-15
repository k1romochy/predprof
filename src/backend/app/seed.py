import asyncio
import json
import sys

from .core.database import async_session_factory, engine
from .models import Base
from .repositories.analytics_cache import AnalyticsCacheRepository
from .repositories.training_history import TrainingHistoryRepository


async def seed_from_files(history_path: str, class_dist_path: str, top_val_path: str):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    with open(history_path) as f:
        history = json.load(f)
    with open(class_dist_path) as f:
        class_dist = json.load(f)
    with open(top_val_path) as f:
        top_val = json.load(f)

    added = await _seed_data(history, class_dist, top_val)
    if added:
        print(f"Seeded {len(history['val_accuracy'])} training history records")
    print("Seeded analytics cache")
    await engine.dispose()


async def seed_demo() -> bool:
    """Заполняет БД демо-данными, если training_history пуста. Возвращает True, если что-то добавлено."""
    from .seed_demo import get_demo_history, get_demo_class_distribution, get_demo_top_val

    async with async_session_factory() as session:
        th_repo = TrainingHistoryRepository(session)
        if await th_repo.count() > 0:
            return False  

    history = get_demo_history()
    class_dist = get_demo_class_distribution()
    top_val = get_demo_top_val()
    return await _seed_data(history, class_dist, top_val)


async def _seed_data(history: dict, class_dist: dict, top_val: dict) -> bool:
    """Внутренняя функция: записывает данные в БД. Возвращает True, если добавлена история."""
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

        ac_repo = AnalyticsCacheRepository(session)
        await ac_repo.upsert("class_distribution", class_dist)
        await ac_repo.upsert("top_val_classes", top_val)

    return count == 0


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python -m app.seed <history.json> <class_distribution.json> <top_val.json>")
        sys.exit(1)
    asyncio.run(seed_from_files(sys.argv[1], sys.argv[2], sys.argv[3]))
