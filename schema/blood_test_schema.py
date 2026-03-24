from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
from typing import Optional
from datetime import datetime


class BloodTestCreate(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

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
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

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


class BloodTestSummary(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

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
