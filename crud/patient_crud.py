from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from model.models import PatientProfile
from schema.patient_schema import PatientProfileCreate, PatientProfileUpdate
from services.nutrition_calculator import calculate_nutrition_targets

async def create_patient_profile(session: AsyncSession, user_id: int, patient_data: PatientProfileCreate):
    bmi = patient_data.weight / ((patient_data.height / 100) ** 2)
    nutrition_targets = calculate_nutrition_targets(patient_data.weight, patient_data.urine_amount)
    profile = PatientProfile(
        user_id=user_id,
        first_name=patient_data.first_name,
        last_name=patient_data.last_name,
        age=patient_data.age,
        gender=patient_data.gender,
        phone=patient_data.phone,
        height=patient_data.height,
        weight=patient_data.weight,
        bmi=bmi,
        blood_pressure=patient_data.blood_pressure,
        existing_diseases=patient_data.existing_diseases,
        smoking=patient_data.smoking,
        alcohol=patient_data.alcohol,
        urine_amount=patient_data.urine_amount,
        nutrition_targets=nutrition_targets
    )
    session.add(profile)
    await session.commit()
    await session.refresh(profile)
    return profile


async def get_patient_profile(session: AsyncSession, user_id: int):
    result = await session.execute(
        select(PatientProfile).where(PatientProfile.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def update_patient_profile(session: AsyncSession, profile: PatientProfile, data: PatientProfileUpdate):
    update_data = data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(profile, key, value)

    # recalc BMI if needed
    if profile.height and profile.weight:
        profile.bmi = profile.weight / ((profile.height / 100) ** 2)
    if (profile.weight and profile.urine_amount) or profile.urine_amount is None:
        profile.nutrition_targets = calculate_nutrition_targets(profile.weight, profile.urine_amount)

    session.add(profile)
    await session.commit()
    await session.refresh(profile)
    return profile


async def delete_patient_profile(session: AsyncSession, profile: PatientProfile):
    await session.delete(profile)
    await session.commit()
