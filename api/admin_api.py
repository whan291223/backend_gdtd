from fastapi import APIRouter, HTTPException, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from typing import List, Dict
from datetime import datetime, timedelta, timezone
from core.db import get_session
from core.config import settings
from model.models import User, PatientProfile, SpentNafScore, BloodTest
from schema.admin_schema import (
    AdminLoginRequest,
    AdminLoginResponse,
    PatientManagementRow,
    PatientDetail,
)
from schema.lab_schema import (
    LabCategoryRead,
    LabCategoryUpdate,
    LabRecordRead,
    LabRecordCreate,
    LabValueRead,
    LabFieldRead
)
from schema.blood_test_schema import BloodTestCreate, BloodTestSummary
from schema.spent_naf_schema import SpentNafSummary
from schema.food_log_schema import FoodLogEntry, ExerciseLogEntry, DailySetupRead
from crud.food_log_crud import get_daily_setup
import secrets
import hashlib
from crud.patient_crud import update_patient_profile  # Add this to your imports
from crud.lab_crud import get_lab_config, update_lab_config, create_lab_record, delete_lab_record, get_lab_history
from schema.patient_schema import PatientProfileUpdate
router = APIRouter(prefix="/admin", tags=["Admin"])

# token -> {"username": str, "created_at": datetime}
_active_tokens: Dict[str, dict] = {}


# --- Auth --------------------------------------------------------------------

def _make_token(username: str) -> str:
    raw = secrets.token_hex(32)
    return hashlib.sha256(f"{username}:{raw}".encode()).hexdigest() + raw


def verify_token(x_admin_token: str = Header(...)) -> str:
    token_info = _active_tokens.get(x_admin_token)
    if not token_info:
        raise HTTPException(status_code=401, detail="Invalid admin token")

    # Check expiration (e.g., 24 hours)
    created_at = token_info["created_at"]
    if datetime.now(timezone.utc) - created_at > timedelta(hours=24):
        del _active_tokens[x_admin_token]
        raise HTTPException(status_code=401, detail="Admin token expired")

    return x_admin_token


@router.post("/login", response_model=AdminLoginResponse)
async def admin_login(payload: AdminLoginRequest):
    if (
        payload.username != settings.ADMIN_USERNAME
        or payload.password != settings.ADMIN_PASSWORD
    ):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = _make_token(payload.username)
    _active_tokens[token] = {
        "username": payload.username,
        "created_at": datetime.now(timezone.utc)
    }
    return AdminLoginResponse(token=token, username=payload.username)


@router.post("/logout")
async def admin_logout(token: str = Depends(verify_token)):
    if token in _active_tokens:
        del _active_tokens[token]
    return {"message": "Logged out"}


# --- Endpoints ---------------------------------------------------------------

@router.get("/patients", response_model=List[PatientManagementRow])
async def list_patients(
    session: AsyncSession = Depends(get_session),
    _: str = Depends(verify_token),
):
    users_result = await session.execute(select(User))
    users = users_result.scalars().all()

    rows: List[PatientManagementRow] = []

    for user in users:
        profile_result = await session.execute(
            select(PatientProfile).where(PatientProfile.user_id == user.id)
        )
        profile = profile_result.scalar_one_or_none()
        if not profile:
            continue

        scores_result = await session.execute(
            select(SpentNafScore)
            .where(SpentNafScore.user_id == user.id)
            .order_by(SpentNafScore.submitted_at.desc())
        )
        all_scores = scores_result.scalars().all()
        latest_score = all_scores[0] if all_scores else None

        blood_result = await session.execute(
            select(BloodTest)
            .where(BloodTest.user_id == user.id)
            .order_by(BloodTest.recorded_at.desc())
            .limit(1)
        )
        latest_blood = blood_result.scalar_one_or_none()

        rows.append(PatientManagementRow(
            user_id=user.id,
            line_user_id=user.line_user_id,
            display_name=user.display_name,
            picture_url=user.picture_url,
            first_name=profile.first_name,
            last_name=profile.last_name,
            age=profile.age,
            gender=profile.gender,
            phone=profile.phone,
            height=profile.height,
            weight=profile.weight,
            bmi=round(profile.bmi, 2) if profile.bmi else None,
            blood_pressure=profile.blood_pressure,
            existing_diseases=profile.existing_diseases,
            smoking=profile.smoking,
            alcohol=profile.alcohol,
            urine_amount=profile.urine_amount,
            latest_spent=SpentNafSummary(
                id=latest_score.id,
                user_answer_spent=latest_score.user_answer_spent,
                spent_score=latest_score.spent_score,
                is_high_risk=latest_score.is_high_risk,
                user_answer_naf=latest_score.user_answer_naf,
                naf_score=latest_score.naf_score,
                naf_score_breakdown=latest_score.naf_score_breakdown,
                status=latest_score.status,
                submitted_at=latest_score.submitted_at,
            ) if latest_score else None,
            latest_blood_test=BloodTestSummary(
                id=latest_blood.id,
                serum_albumin=latest_blood.serum_albumin,
                npcr=latest_blood.npcr,
                bun=latest_blood.bun,
                creatinine=latest_blood.creatinine,
                cholesterol=latest_blood.cholesterol,
                hemoglobin=latest_blood.hemoglobin,
                hematocrit=latest_blood.hematocrit,
                potassium=latest_blood.potassium,
                phosphorus=latest_blood.phosphorus,
                bicarbonate=latest_blood.bicarbonate,
                note=latest_blood.note,
                recorded_at=latest_blood.recorded_at,
            ) if latest_blood else None,
            total_screenings=len(all_scores),
        ))

    return rows


# --- Patient detail endpoint -------------------------------------------------

# --- Lab Config --------------------------------------------------------------

@router.get("/lab-config", response_model=List[LabCategoryRead])
async def admin_get_lab_config(
    session: AsyncSession = Depends(get_session),
    _: str = Depends(verify_token),
):
    return await get_lab_config(session)


@router.put("/lab-config", response_model=List[LabCategoryRead])
async def admin_update_lab_config(
    payload: List[LabCategoryUpdate],
    session: AsyncSession = Depends(get_session),
    _: str = Depends(verify_token),
):
    await update_lab_config(session, payload)
    # Return updated config
    return await get_lab_config(session)


# --- Patient detail endpoint -------------------------------------------------

@router.get("/patients/{user_id}", response_model=PatientDetail)
async def get_patient_detail(
    user_id: int,
    session: AsyncSession = Depends(get_session),
    _: str = Depends(verify_token),
):
    from model.models import FoodLog, ExerciseLog

    user_result = await session.execute(select(User).where(User.id == user_id))
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    profile_result = await session.execute(
        select(PatientProfile).where(PatientProfile.user_id == user_id)
    )
    profile = profile_result.scalar_one_or_none()

    # SPENT/NAF history — all sessions newest first
    scores_result = await session.execute(
        select(SpentNafScore)
        .where(SpentNafScore.user_id == user_id)
        .order_by(SpentNafScore.submitted_at.desc())
    )
    scores = scores_result.scalars().all()

    # Blood test history — all records newest first
    blood_result = await session.execute(
        select(BloodTest)
        .where(BloodTest.user_id == user_id)
        .order_by(BloodTest.recorded_at.desc())
    )
    blood_tests = blood_result.scalars().all()

    # Food log history — last 30 days newest first
    food_result = await session.execute(
        select(FoodLog)
        .where(FoodLog.user_id == user_id)
        .order_by(FoodLog.eaten_date.desc(), FoodLog.created_at.desc())
        .limit(200)
    )
    food_logs = food_result.scalars().all()

    # Exercise log history — last 30 days newest first
    exercise_result = await session.execute(
        select(ExerciseLog)
        .where(ExerciseLog.user_id == user_id)
        .order_by(ExerciseLog.logged_date.desc(), ExerciseLog.created_at.desc())
        .limit(100)
    )
    exercise_logs = exercise_result.scalars().all()

    # Lab history and config
    lab_history = await get_lab_history(session, user_id)
    lab_config = await get_lab_config(session)

    return PatientDetail(
        user_id=user.id,
        line_user_id=user.line_user_id,
        display_name=user.display_name,
        picture_url=user.picture_url,
        first_name=profile.first_name if profile else None,
        last_name=profile.last_name if profile else None,
        age=profile.age if profile else None,
        gender=profile.gender if profile else None,
        phone=profile.phone if profile else None,
        height=profile.height if profile else None,
        weight=profile.weight if profile else None,
        bmi=round(profile.bmi, 2) if profile and profile.bmi else None,
        blood_pressure=profile.blood_pressure if profile else None,
        existing_diseases=profile.existing_diseases if profile else None,
        smoking=profile.smoking if profile else None,
        alcohol=profile.alcohol if profile else None,
        urine_amount=profile.urine_amount if profile else None,
        daily_setup=DailySetupRead.model_validate(daily, from_attributes=True) if (daily := await get_daily_setup(session, user_id, datetime.now(timezone.utc).strftime("%Y-%m-%d"))) else None,
        spent_naf_history=[SpentNafSummary.model_validate(s, from_attributes=True) for s in scores],
        blood_test_history=[BloodTestSummary.model_validate(b, from_attributes=True) for b in blood_tests],
        food_log_history=[FoodLogEntry.model_validate(f, from_attributes=True) for f in food_logs],
        exercise_log_history=[ExerciseLogEntry.model_validate(e, from_attributes=True) for e in exercise_logs],
        lab_history=[LabRecordRead.model_validate(lr, from_attributes=True) for lr in lab_history],
        lab_config=[LabCategoryRead.model_validate(lc, from_attributes=True) for lc in lab_config]
    )


# --- Blood test management for admin -----------------------------------------

@router.post("/patients/{user_id}/blood-test", response_model=BloodTestSummary)
async def admin_add_blood_test(
    user_id: int,
    data: BloodTestCreate,
    session: AsyncSession = Depends(get_session),
    _: str = Depends(verify_token),
):
    """Admin can manually add a blood test record for a patient."""
    user_result = await session.execute(select(User).where(User.id == user_id))
    if not user_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="User not found")

    record = BloodTest(user_id=user_id, **data.model_dump())
    session.add(record)
    await session.commit()
    await session.refresh(record)

    return BloodTestSummary(
        id=record.id, serum_albumin=record.serum_albumin, npcr=record.npcr,
        bun=record.bun, creatinine=record.creatinine, cholesterol=record.cholesterol,
        hemoglobin=record.hemoglobin, hematocrit=record.hematocrit,
        potassium=record.potassium, phosphorus=record.phosphorus,
        bicarbonate=record.bicarbonate, note=record.note, recorded_at=record.recorded_at,
    )


@router.delete("/blood-test/{blood_test_id}", status_code=204)
async def admin_delete_blood_test(
    blood_test_id: int,
    session: AsyncSession = Depends(get_session),
    _: str = Depends(verify_token),
):
    """Admin can delete a specific blood test record."""
    result = await session.execute(select(BloodTest).where(BloodTest.id == blood_test_id))
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="Blood test record not found")
    await session.delete(record)
    await session.commit()

# --- Lab Record management for admin -----------------------------------------

@router.post("/patients/{user_id}/lab-record", response_model=LabRecordRead)
async def admin_add_lab_record(
    user_id: int,
    data: LabRecordCreate,
    session: AsyncSession = Depends(get_session),
    _: str = Depends(verify_token),
):
    """Admin can manually add a lab record for a patient."""
    user_result = await session.execute(select(User).where(User.id == user_id))
    if not user_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="User not found")

    record = await create_lab_record(session, user_id, data)

    return LabRecordRead.model_validate(record, from_attributes=True)


@router.delete("/lab-record/{lab_record_id}", status_code=204)
async def admin_delete_lab_record(
    lab_record_id: int,
    session: AsyncSession = Depends(get_session),
    _: str = Depends(verify_token),
):
    """Admin can delete a specific lab record."""
    success = await delete_lab_record(session, lab_record_id)
    if not success:
        raise HTTPException(status_code=404, detail="Lab record not found")


# To be done Admin edit user profile and screen ing update in dashboard still shown 0
@router.put("/patients/{user_id}", response_model=PatientDetail)
async def admin_update_patient_profile(
    user_id: int,
    data: PatientProfileUpdate,
    session: AsyncSession = Depends(get_session),
    _: str = Depends(verify_token),
):
    """Admin can update patient profile information."""
    from model.models import FoodLog, ExerciseLog
    
    # Verify user exists
    user_result = await session.execute(select(User).where(User.id == user_id))
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get or create profile
    profile_result = await session.execute(
        select(PatientProfile).where(PatientProfile.user_id == user_id)
    )
    profile = profile_result.scalar_one_or_none()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Patient profile not found")

    # Use existing update function
    await update_patient_profile(session, profile, data)

    # Fetch complete patient detail to return
    scores_result = await session.execute(
        select(SpentNafScore)
        .where(SpentNafScore.user_id == user_id)
        .order_by(SpentNafScore.submitted_at.desc())
    )
    scores = scores_result.scalars().all()

    blood_result = await session.execute(
        select(BloodTest)
        .where(BloodTest.user_id == user_id)
        .order_by(BloodTest.recorded_at.desc())
    )
    blood_tests = blood_result.scalars().all()

    food_result = await session.execute(
        select(FoodLog)
        .where(FoodLog.user_id == user_id)
        .order_by(FoodLog.eaten_date.desc(), FoodLog.created_at.desc())
        .limit(200)
    )
    food_logs = food_result.scalars().all()

    exercise_result = await session.execute(
        select(ExerciseLog)
        .where(ExerciseLog.user_id == user_id)
        .order_by(ExerciseLog.logged_date.desc(), ExerciseLog.created_at.desc())
        .limit(100)
    )
    exercise_logs = exercise_result.scalars().all()

    # Refresh profile to get updated BMI
    await session.refresh(profile)

    # Lab history and config
    lab_history = await get_lab_history(session, user_id)
    lab_config = await get_lab_config(session)

    return PatientDetail(
        user_id=user.id,
        line_user_id=user.line_user_id,
        display_name=user.display_name,
        picture_url=user.picture_url,
        first_name=profile.first_name,
        last_name=profile.last_name,
        age=profile.age,
        gender=profile.gender,
        phone=profile.phone,
        height=profile.height,
        weight=profile.weight,
        bmi=round(profile.bmi, 2) if profile.bmi else None,
        blood_pressure=profile.blood_pressure,
        existing_diseases=profile.existing_diseases,
        smoking=profile.smoking,
        alcohol=profile.alcohol,
        urine_amount=profile.urine_amount,
        daily_setup=DailySetupRead.model_validate(daily, from_attributes=True) if (daily := await get_daily_setup(session, user_id, datetime.now(timezone.utc).strftime("%Y-%m-%d"))) else None,
        spent_naf_history=[SpentNafSummary.model_validate(s, from_attributes=True) for s in scores],
        blood_test_history=[BloodTestSummary.model_validate(b, from_attributes=True) for b in blood_tests],
        food_log_history=[FoodLogEntry.model_validate(f, from_attributes=True) for f in food_logs],
        exercise_log_history=[ExerciseLogEntry.model_validate(e, from_attributes=True) for e in exercise_logs],
        lab_history=[LabRecordRead.model_validate(lr, from_attributes=True) for lr in lab_history],
        lab_config=[LabCategoryRead.model_validate(lc, from_attributes=True) for lc in lab_config]
    )