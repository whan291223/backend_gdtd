from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class BloodTestCreate(BaseModel):
    user_id: int
    blood_level: int
    note: Optional[str] = None


class BloodTestUpdate(BaseModel):
    blood_level: int
    note: Optional[str] = None


class BloodTestRead(BaseModel):
    id: int
    user_id: int
    blood_level: int
    note: Optional[str] = None
    recorded_at: Optional[datetime] = None

    class Config:
        from_attributes = True