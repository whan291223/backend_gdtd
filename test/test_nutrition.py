import unittest
from model.models import PatientProfile
from services.nutrition_service import calculate_nutrition_targets

class TestNutritionService(unittest.TestCase):
    def test_calculate_nutrition_targets_with_weight(self):
        profile = PatientProfile(
            user_id=1, first_name="Test", last_name="User", age=30, gender="M", phone="123",
            height=170, weight=70, blood_pressure="120/80", smoking="no", alcohol="no"
        )
        targets = calculate_nutrition_targets(profile)
        self.assertEqual(targets.calories_min, 2100) # 70 * 30
        self.assertEqual(targets.calories_max, 2450) # 70 * 35
        self.assertEqual(targets.protein_min, 77.0)  # 70 * 1.1
        self.assertEqual(targets.protein_max, 98.0)  # 70 * 1.4
        self.assertEqual(targets.water_min, 500)
        self.assertEqual(targets.water_max, 800)
        self.assertTrue(targets.is_water_range)

    def test_calculate_nutrition_targets_with_urine(self):
        profile = PatientProfile(
            user_id=1, first_name="Test", last_name="User", age=30, gender="M", phone="123",
            height=170, weight=70, blood_pressure="120/80", smoking="no", alcohol="no",
            urine_amount=1000
        )
        targets = calculate_nutrition_targets(profile)
        self.assertEqual(targets.water_min, 1500) # 1000 + 500
        self.assertEqual(targets.water_max, 1500)
        self.assertFalse(targets.is_water_range)

if __name__ == "__main__":
    unittest.main()
