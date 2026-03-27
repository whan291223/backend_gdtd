from pydantic import ValidationError
from schema.user_schema import UserCreate
from schema.admin_schema import AdminLoginRequest
from schema.blood_test_schema import BloodTestCreate
from schema.food_log_schema import FoodLogCreate
from schema.patient_schema import PatientProfileCreate
from schema.spent_naf_schema import SpentSubmit

def test_user_create():
    print("Testing UserCreate...")
    data = {
        "lineUserId": "U123456",
        "displayName": "John Doe",
        "pictureUrl": "http://example.com/pic.jpg",
        "realName": "John",
        "surname": "Doe"
    }
    user = UserCreate(**data)
    assert user.line_user_id == "U123456"
    assert user.display_name == "John Doe"
    print("UserCreate OK")

def test_admin_login():
    print("Testing AdminLoginRequest...")
    data = {
        "username": "admin",
        "password": "password"
    }
    req = AdminLoginRequest(**data)
    assert req.username == "admin"
    print("AdminLoginRequest OK")

def test_blood_test_create():
    print("Testing BloodTestCreate...")
    data = {
        "serumAlbumin": 4.5,
        "npcr": 1.2
    }
    req = BloodTestCreate(**data)
    assert req.serum_albumin == 4.5
    assert req.npcr == 1.2
    print("BloodTestCreate OK")

def test_food_log_create():
    print("Testing FoodLogCreate...")
    data = {
        "foodName": "Apple",
        "calories": 52.0,
        "mealCategory": "Snack",
        "eatenDate": "2023-10-27"
    }
    req = FoodLogCreate(**data)
    assert req.food_name == "Apple"
    assert req.meal_category == "Snack"
    assert req.eaten_date == "2023-10-27"
    print("FoodLogCreate OK")

def test_patient_profile_create():
    print("Testing PatientProfileCreate...")
    data = {
        "firstName": "John",
        "lastName": "Doe",
        "age": 30,
        "gender": "Male",
        "phone": "123456789",
        "height": 180,
        "weight": 75,
        "bloodPressure": "120/80",
        "existingDiseases": ["None"],
        "smoking": "No",
        "alcohol": "No",
        "activityLevel": "Moderate"
    }
    req = PatientProfileCreate(**data)
    assert req.first_name == "John"
    assert req.last_name == "Doe"
    assert req.blood_pressure == "120/80"
    print("PatientProfileCreate OK")

def test_spent_submit():
    print("Testing SpentSubmit...")
    data = {
        "answers": [1, 0, 1]
    }
    req = SpentSubmit(**data)
    assert req.answers == [1, 0, 1]
    print("SpentSubmit OK")

def test_snake_case():
    print("Testing UserCreate with snake_case...")
    data = {
        "line_user_id": "U123456",
        "display_name": "John Doe"
    }
    user = UserCreate(**data)
    assert user.line_user_id == "U123456"
    assert user.display_name == "John Doe"
    print("UserCreate snake_case OK")

if __name__ == "__main__":
    try:
        test_user_create()
        test_admin_login()
        test_blood_test_create()
        test_food_log_create()
        test_patient_profile_create()
        test_spent_submit()
        test_snake_case()
        print("\nAll tests passed successfully!")
    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()
