# schema/nutrition_schema.py

from pydantic import BaseModel
from schema.config import common_config

class NutritionTargets(BaseModel):
    model_config = common_config

    calories_min: int
    calories_max: int
    protein_min: float
    protein_max: float
    sodium: float
    potassium: float
    phosphorus: float
    water_min: float
    water_max: float
    is_water_range: bool
