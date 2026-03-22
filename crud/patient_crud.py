from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from model.models import PatientProfile
from schema.patient_schema import PatientProfileCreate, PatientProfileUpdate


async def create_patient_profile(session: AsyncSession, user_id: int, patient_data: PatientProfileCreate):
    bmi = patient_data.weight / ((patient_data.height / 100) ** 2)

    profile = PatientProfile(
        user_id=user_id,
        first_name=patient_data.firstName,
        last_name=patient_data.lastName,
        age=patient_data.age,
        gender=patient_data.gender,
        phone=patient_data.phone,
        height=patient_data.height,
        weight=patient_data.weight,
        bmi=bmi,
        blood_pressure=patient_data.bloodPressure,
        existing_diseases=patient_data.existingDiseases,
        smoking=patient_data.smoking,
        alcohol=patient_data.alcohol,
        activity_level=patient_data.activityLevel,
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


async def update_patient_profile(session: AsyncSession, profile: PatientProfile, data):
    update_data = data.dict(exclude_unset=True)

    for key, value in update_data.items():
        # map camelCase → snake_case
        mapping = {
            "firstName": "first_name",
            "lastName": "last_name",
            "bloodPressure": "blood_pressure",
            "existingDiseases": "existing_diseases",
            "activityLevel": "activity_level",
        }
        setattr(profile, mapping.get(key, key), value)

    # recalc BMI if needed
    if profile.height and profile.weight:
        profile.bmi = profile.weight / ((profile.height / 100) ** 2)

    session.add(profile)
    await session.commit()
    await session.refresh(profile)
    return profile


async def delete_patient_profile(session: AsyncSession, profile: PatientProfile):
    await session.delete(profile)
    await session.commit()