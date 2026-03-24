from fastapi import APIRouter, HTTPException, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from typing import List, Optional, Set
from pydantic import BaseModel
from datetime import datetime
from core.db import get_session
from core.config import settings
from model.models import User, PatientProfile, SpentNafScore, BloodTest
import secrets
import hashlib

router = APIRouter(prefix="/admin", tags=["Admin"])

_active_tokens: Set[str] = set()


# --- Auth --------------------------------------------------------------------

class AdminLoginRequest(BaseModel):
    username: str
    password: str


class AdminLoginResponse(BaseModel):
    token: str
    username: str


def _make_token(username: str) -> str:
    raw = secrets.token_hex(32)
    return hashlib.sha256(f"{username}:{raw}".encode()).hexdigest() + raw


def verify_token(x_admin_token: str = Header(...)) -> str:
    if x_admin_token not in _active_tokens:
        raise HTTPException(status_code=401, detail="Invalid or expired admin token")
    return x_admin_token


@router.post("/login", response_model=AdminLoginResponse)
async def admin_login(payload: AdminLoginRequest):
    if (
        payload.username != settings.ADMIN_USERNAME
        or payload.password != settings.ADMIN_PASSWORD
    ):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = _make_token(payload.username)
    _active_tokens.add(token)
    return AdminLoginResponse(token=token, username=payload.username)


@router.post("/logout")
async def admin_logout(token: str = Depends(verify_token)):
    _active_tokens.discard(token)
    return {"message": "Logged out"}


# --- Response schemas --------------------------------------------------------

class BloodTestSummary(BaseModel):
    id: int
    serum_albumin: Optional[float]
    npcr: Optional[float]
    bun: Optional[float]
    creatinine: Optional[float]
    cholesterol: Optional[float]
    hemoglobin: Optional[float]
    hematocrit: Optional[float]
    potassium: Optional[float]
    phosphorus: Optional[float]
    bicarbonate: Optional[float]
    note: Optional[str]
    recorded_at: Optional[datetime]


class SpentNafSummary(BaseModel):
    id: int
    spent_score: Optional[int]
    is_high_risk: Optional[bool]
    naf_score: Optional[int]
    status: str
    submitted_at: Optional[datetime]


class PatientManagementRow(BaseModel):
    user_id: int
    line_user_id: str
    display_name: Optional[str]
    picture_url: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    age: Optional[int]
    gender: Optional[str]
    phone: Optional[str]
    height: Optional[float]
    weight: Optional[float]
    bmi: Optional[float]
    blood_pressure: Optional[str]
    existing_diseases: Optional[List[str]]
    smoking: Optional[str]
    alcohol: Optional[str]
    activity_level: Optional[str]
    latest_spent: Optional[SpentNafSummary]
    latest_blood_test: Optional[BloodTestSummary]
    total_screenings: int


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
            activity_level=profile.activity_level,
            latest_spent=SpentNafSummary(
                id=latest_score.id,
                spent_score=latest_score.spent_score,
                is_high_risk=latest_score.is_high_risk,
                naf_score=latest_score.naf_score,
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


# --- Patient detail schemas --------------------------------------------------

class FoodLogEntry(BaseModel):
    id: int
    food_name: str
    calories: float
    protein: float
    sodium: float
    potassium: float
    phosphorus: float
    meal_category: str
    eaten_date: str
    created_at: Optional[datetime]


class ExerciseLogEntry(BaseModel):
    id: int
    exercise_name: str
    duration_minutes: int
    calories_burned: float
    logged_date: str
    created_at: Optional[datetime]


class PatientDetail(BaseModel):
    # Identity
    user_id: int
    line_user_id: str
    display_name: Optional[str]
    picture_url: Optional[str]
    # Profile
    first_name: Optional[str]
    last_name: Optional[str]
    age: Optional[int]
    gender: Optional[str]
    phone: Optional[str]
    height: Optional[float]
    weight: Optional[float]
    bmi: Optional[float]
    blood_pressure: Optional[str]
    existing_diseases: Optional[List[str]]
    smoking: Optional[str]
    alcohol: Optional[str]
    activity_level: Optional[str]
    # Full histories
    spent_naf_history: List[SpentNafSummary]
    blood_test_history: List[BloodTestSummary]
    food_log_history: List[FoodLogEntry]
    exercise_log_history: List[ExerciseLogEntry]


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
        activity_level=profile.activity_level if profile else None,
        spent_naf_history=[
            SpentNafSummary(
                id=s.id, spent_score=s.spent_score, is_high_risk=s.is_high_risk,
                naf_score=s.naf_score, status=s.status, submitted_at=s.submitted_at,
            ) for s in scores
        ],
        blood_test_history=[
            BloodTestSummary(
                id=b.id, serum_albumin=b.serum_albumin, npcr=b.npcr, bun=b.bun,
                creatinine=b.creatinine, cholesterol=b.cholesterol, hemoglobin=b.hemoglobin,
                hematocrit=b.hematocrit, potassium=b.potassium, phosphorus=b.phosphorus,
                bicarbonate=b.bicarbonate, note=b.note, recorded_at=b.recorded_at,
            ) for b in blood_tests
        ],
        food_log_history=[
            FoodLogEntry(
                id=f.id, food_name=f.food_name, calories=f.calories, protein=f.protein,
                sodium=f.sodium, potassium=f.potassium, phosphorus=f.phosphorus,
                meal_category=f.meal_category, eaten_date=f.eaten_date, created_at=f.created_at,
            ) for f in food_logs
        ],
        exercise_log_history=[
            ExerciseLogEntry(
                id=e.id, exercise_name=e.exercise_name, duration_minutes=e.duration_minutes,
                calories_burned=e.calories_burned, logged_date=e.logged_date, created_at=e.created_at,
            ) for e in exercise_logs
        ],
    )


# --- Blood test management for admin -----------------------------------------

class BloodTestCreate(BaseModel):
    serum_albumin: Optional[float] = None
    npcr:          Optional[float] = None
    bun:           Optional[float] = None
    creatinine:    Optional[float] = None
    cholesterol:   Optional[float] = None
    hemoglobin:    Optional[float] = None
    hematocrit:    Optional[float] = None
    potassium:     Optional[float] = None
    phosphorus:    Optional[float] = None
    bicarbonate:   Optional[float] = None
    note:          Optional[str]   = None


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