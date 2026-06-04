"""MET-based calorie burn calculations."""

MET_VALUES = {
    "bicycle_easy": 4.0,
    "bicycle_moderate": 6.0,
    "bicycle": 6.0,
    "weight_training": 3.5,
    "swimming_easy": 5.8,
    "swimming_moderate": 7.0,
    "swimming_hard": 8.3,
    "swimming": 7.0,
    "walking": 3.5,
    "elliptical": 5.0,
    "stair_climber": 8.0,
    "incline_walk": 4.5,
    "treadmill": 4.5,
}

CARDIO_TYPE_MAP = {
    "bicycle": "bicycle_moderate",
    "treadmill": "treadmill",
    "elliptical": "elliptical",
    "stair_climber": "stair_climber",
    "stair climber": "stair_climber",
    "walking": "walking",
    "incline walk": "incline_walk",
    "incline_walk": "incline_walk",
}


def calories_burned(met: float, weight_kg: float, duration_minutes: float) -> float:
    """calories = MET × weight_kg × duration_hours"""
    if not weight_kg or not duration_minutes:
        return 0.0
    hours = duration_minutes / 60.0
    return round(met * weight_kg * hours, 1)


def get_met(cardio_type: str, intensity: str = "moderate") -> float:
    key = CARDIO_TYPE_MAP.get(cardio_type.lower().strip(), cardio_type.lower().replace(" ", "_"))
    if cardio_type.lower() == "bicycle":
        key = "bicycle_easy" if intensity == "easy" else "bicycle_moderate"
    if "swimming" in cardio_type.lower() or cardio_type.lower() == "swimming":
        key = f"swimming_{intensity}" if intensity in ("easy", "moderate", "hard") else "swimming_moderate"
    return MET_VALUES.get(key, MET_VALUES.get("weight_training", 3.5))


def estimate_cardio_calories(cardio_type: str, weight_kg: float, duration_minutes: float, intensity: str = "moderate") -> float:
    met = get_met(cardio_type, intensity)
    return calories_burned(met, weight_kg, duration_minutes)


def estimate_swimming_calories(weight_kg: float, minutes: float, intensity: str = "moderate") -> float:
    met = get_met("swimming", intensity)
    return calories_burned(met, weight_kg, minutes)


def estimate_weight_training_calories(weight_kg: float, duration_minutes: float = 45) -> float:
    return calories_burned(MET_VALUES["weight_training"], weight_kg, duration_minutes)
