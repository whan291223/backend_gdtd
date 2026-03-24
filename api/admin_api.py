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