from schema.user_schema import UserRead
from schema.food_log_schema import FoodLogRead
from datetime import datetime

def test_user_read_camel_case():
    print("Testing UserRead camelCase output...")
    user = UserRead(
        id=1,
        line_user_id="U123456",
        display_name="John Doe",
        picture_url="http://example.com/pic.jpg",
        real_name="John"
    )
    data = user.model_dump(by_alias=True)
    print("UserRead serialized with aliases:", data)
    assert "lineUserId" in data
    assert "displayName" in data
    assert "pictureUrl" in data
    assert "realName" in data
    print("UserRead camelCase OK")

def test_food_log_read_camel_case():
    print("Testing FoodLogRead camelCase output...")
    food = FoodLogRead(
        id=1,
        user_id=1,
        food_name="Apple",
        calories=52.0,
        protein=0.3,
        sodium=1.0,
        potassium=107.0,
        phosphorus=11.0,
        meal_category="Snack",
        eaten_date="2023-10-27",
        created_at=datetime.now()
    )
    data = food.model_dump(by_alias=True)
    print("FoodLogRead serialized with aliases:", data)
    assert "userId" in data
    assert "foodName" in data
    assert "mealCategory" in data
    assert "eatenDate" in data
    assert "createdAt" in data
    print("FoodLogRead camelCase OK")

if __name__ == "__main__":
    try:
        test_user_read_camel_case()
        test_food_log_read_camel_case()
        print("\nAll response tests passed successfully!")
    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()
