# services/nutrition_service.py

from typing import Optional, Dict, Any

def calculate_nutrition_targets(weight: float, urine_amount: Optional[float] = None) -> Dict[str, Any]:
    """
    Calculate nutrition targets based on patient weight and urine amount.
    Logic moved from frontend FoodLogPage.
    """
    base = {
        "calories_min": 0,
        "calories_max": 0,
        "protein_min": 0.0,
        "protein_max": 0.0,
        "sodium": 2000,
        "potassium": 2000,
        "phosphorus": 800,
        "water_min": 500,
        "water_max": 800,
        "is_water_range": True
    }

    if weight and weight > 0:
        base["calories_min"] = int(round(weight * 30))
        base["calories_max"] = int(round(weight * 35))
        base["protein_min"] = round(weight * 1.1, 1)
        base["protein_max"] = round(weight * 1.4, 1)

    if urine_amount is not None:
        base["water_min"] = float(urine_amount + 500)
        base["water_max"] = float(urine_amount + 500)
        base["is_water_range"] = False

    return base
