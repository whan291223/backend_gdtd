from model.models import PatientProfile, NutritionTarget

def calculate_nutrition_targets(profile: PatientProfile) -> NutritionTarget:
    """
    Calculate nutrition targets based on patient profile (weight and urine amount).
    """
    targets = NutritionTarget()

    weight = profile.weight
    urine_amount = profile.urine_amount

    if weight and weight > 0:
        targets.calories_min = round(weight * 30)
        targets.calories_max = round(weight * 35)
        targets.protein_min = round(weight * 1.1 * 10) / 10
        targets.protein_max = round(weight * 1.4 * 10) / 10

    if urine_amount is not None:
        targets.water_min = urine_amount + 500
        targets.water_max = urine_amount + 500
        targets.is_water_range = False
    else:
        # Default if urine amount is not set
        targets.water_min = 500
        targets.water_max = 800
        targets.is_water_range = True

    return targets
