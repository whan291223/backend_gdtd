from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from schema.config import common_config


class BloodTestCreate(BaseModel):
    model_config = common_config

    serum_albumin:  Optional[float] = None
    npcr:           Optional[float] = None
    bun:            Optional[float] = None
    creatinine:     Optional[float] = None
    cholesterol:    Optional[float] = None
    hemoglobin:     Optional[float] = None
    hematocrit:     Optional[float] = None
    potassium:      Optional[float] = None
    phosphorus:     Optional[float] = None
    bicarbonate:    Optional[float] = None
    note:           Optional[str]   = None


class BloodTestRead(BaseModel):
    model_config = common_config

    id: int
    user_id: int
    serum_albumin:  Optional[float] = None
    npcr:           Optional[float] = None
    bun:            Optional[float] = None
    creatinine:     Optional[float] = None
    cholesterol:    Optional[float] = None
    hemoglobin:     Optional[float] = None
    hematocrit:     Optional[float] = None
    potassium:      Optional[float] = None
    phosphorus:     Optional[float] = None
    bicarbonate:    Optional[float] = None
    note:           Optional[str] = None
    recorded_at:    Optional[datetime] = None


class BloodTestSummary(BaseModel):
    model_config = common_config

    id: int
    serum_albumin: Optional[float] = None
    npcr: Optional[float] = None
    bun: Optional[float] = None
    creatinine: Optional[float] = None
    cholesterol: Optional[float] = None
    hemoglobin: Optional[float] = None
    hematocrit: Optional[float] = None
    potassium: Optional[float] = None
    phosphorus: Optional[float] = None
    bicarbonate: Optional[float] = None
    note: Optional[str] = None
    recorded_at: Optional[datetime] = None
