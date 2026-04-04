# test/test_nutrition.py

import unittest
from services.nutrition_service import calculate_nutrition_targets

class TestNutritionService(unittest.TestCase):
    def test_calculate_targets_with_weight(self):
        # Test weight 60kg, no urine amount
        weight = 60.0
        targets = calculate_nutrition_targets(weight)

        self.assertEqual(targets["calories_min"], 1800)
        self.assertEqual(targets["calories_max"], 2100)
        self.assertEqual(targets["protein_min"], 66.0)
        self.assertEqual(targets["protein_max"], 84.0)
        self.assertEqual(targets["water_min"], 500)
        self.assertEqual(targets["water_max"], 800)
        self.assertTrue(targets["is_water_range"])

    def test_calculate_targets_with_urine(self):
        # Test weight 60kg, urine 1000ml
        weight = 60.0
        urine = 1000.0
        targets = calculate_nutrition_targets(weight, urine)

        self.assertEqual(targets["water_min"], 1500)
        self.assertEqual(targets["water_max"], 1500)
        self.assertFalse(targets["is_water_range"])

    def test_calculate_targets_zero_weight(self):
        targets = calculate_nutrition_targets(0)
        self.assertEqual(targets["calories_min"], 0)
        self.assertEqual(targets["protein_min"], 0.0)

if __name__ == "__main__":
    unittest.main()
