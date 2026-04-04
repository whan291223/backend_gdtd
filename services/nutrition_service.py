# services/nutrition_service.py

from typing import Optional, Dict, Any, List

def calculate_nutrition_targets(weight: float, urine_amount: Optional[float] = None) -> Dict[str, Any]:
    """
    Calculate nutrition targets based on patient weight and urine amount.
    Logic moved from frontend FoodLogPage.
    """
    # Initialize with default values (matching frontend 'base' object)
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

    # If weight is provided and positive, calculate calorie and protein targets
    if weight and weight > 0:
        base["calories_min"] = int(round(weight * 30))
        base["calories_max"] = int(round(weight * 35))
        base["protein_min"] = round(weight * 1.1, 1)
        base["protein_max"] = round(weight * 1.4, 1)

    # If urine amount is provided, calculate exact water target
    if urine_amount is not None:
        base["water_min"] = float(urine_amount + 500)
        base["water_max"] = float(urine_amount + 500)
        base["is_water_range"] = False

    return base

def get_naf_recommendations(naf_score: Optional[int]) -> Dict[str, Any]:
    """
    Determine NAF level and get recommendations based on the NAF score.
    Logic moved from frontend FoodLogPage.
    """
    if naf_score is None or naf_score <= 0:
        return {
            "naf_level": "unknown",
            "naf_recommendations": []
        }

    if naf_score >= 11:
        level = "high"
        recs = [
            "อาหารให้พลังงานสูง (โยเกิร์ตเสริมโปรตีน, สมูทตี้โปรตีน)",
            "อาหารเคี้ยวง่าย/บดนิ่ม (โจ๊ก, ซุปครีม)",
            "พลังงานเสริม (ผลิตภัณฑ์เสริมอาหาร)"
        ]
    elif naf_score >= 6:
        level = "moderate"
        recs = [
            "เน้นโปรตีนคุณภาพ (ปลา ไก่ เต้าหู้)",
            "เพิ่มมื้อเล็กระหว่างวัน",
            "ใส่ไขมันดี (อะโวคาโด เมล็ดพืช)"
        ]
    else:
        level = "low"
        recs = [
            "ทานอาหารหลากหลายครบ 5 หมู่",
            "ควบคุมโซเดียมและน้ำตาล",
            "ดื่มน้ำให้เพียงพอ"
        ]

    return {
        "naf_level": level,
        "naf_recommendations": recs
    }
