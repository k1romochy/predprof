"""Демо-данные для дашборда: история обучения, распределение классов, топ-5 классов."""

# Точность ~40–50%
DEMO_HISTORY = {
    "val_accuracy": [0.38, 0.42, 0.46, 0.48],
    "val_loss": [1.55, 1.48, 1.42, 1.38],
    "accuracy": [0.40, 0.45, 0.48, 0.50],
    "loss": [1.50, 1.42, 1.35, 1.30],
}

# 5 классов
DEMO_CLASSES = ["55_Cancri_Bc", "Gliese_12_b", "HD_20794_d", "Kepler-186f", "Kepler-62e"]

# Мало сэмплов: 3–7 на класс
DEMO_CLASS_COUNTS = [5, 7, 4, 6, 3]

DEMO_CLASS_DISTRIBUTION = {
    "classes": [
        {"class_id": i, "count": DEMO_CLASS_COUNTS[i]}
        for i in range(len(DEMO_CLASSES))
    ],
}

# Топ-5 по валидации (классы с наибольшим количеством)
TOP5_INDICES = sorted(range(len(DEMO_CLASS_COUNTS)), key=lambda i: -DEMO_CLASS_COUNTS[i])[:5]
DEMO_TOP_VAL = {
    "top_classes": [
        {"class_id": i, "count": DEMO_CLASS_COUNTS[i]}
        for i in TOP5_INDICES
    ],
}


def get_demo_history() -> dict:
    return DEMO_HISTORY


def get_demo_class_distribution() -> dict:
    return DEMO_CLASS_DISTRIBUTION


def get_demo_top_val() -> dict:
    return DEMO_TOP_VAL
