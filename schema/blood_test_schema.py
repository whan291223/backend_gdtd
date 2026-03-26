from typing import Optional
from schema.base_schema import BaseSchema
from datetime import datetime


class BloodTestCreate(BaseSchema):
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


class BloodTestRead(BaseSchema):
    id: int
    user_id: int
    serum_albumin:  Optional[float]
    npcr:           Optional[float]
    bun:            Optional[float]
    creatinine:     Optional[float]
    cholesterol:    Optional[float]
    hemoglobin:     Optional[float]
    hematocrit:     Optional[float]
    potassium:      Optional[float]
    phosphorus:     Optional[float]
    bicarbonate:    Optional[float]
    note:           Optional[str]
    recorded_at:    Optional[datetime]


class BloodTestSummary(BaseSchema):
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
