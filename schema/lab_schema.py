from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from schema.config import common_config


class LabFieldBase(BaseModel):
    model_config = common_config

    name: str
    unit: str
    display_order: Optional[int] = None


class LabFieldCreate(LabFieldBase):
    pass


class LabFieldUpdate(LabFieldBase):
    id: Optional[UUID] = None


class LabFieldRead(LabFieldBase):
    id: UUID


class LabCategoryBase(BaseModel):
    model_config = common_config

    name: str
    display_order: Optional[int] = None


class LabCategoryCreate(LabCategoryBase):
    fields: List[LabFieldCreate] = []


class LabCategoryUpdate(LabCategoryBase):
    id: Optional[UUID] = None
    fields: List[LabFieldUpdate] = []


class LabCategoryRead(LabCategoryBase):
    id: UUID
    fields: List[LabFieldRead] = []


class LabValueBase(BaseModel):
    model_config = common_config

    field_id: UUID
    value: Optional[float] = None


class LabValueCreate(LabValueBase):
    pass


class LabValueRead(LabValueBase):
    id: int


class LabRecordBase(BaseModel):
    model_config = common_config

    note: Optional[str] = None


class LabRecordCreate(LabRecordBase):
    values: List[LabValueCreate]


class LabRecordRead(LabRecordBase):
    id: int
    recorded_at: datetime
    values: List[LabValueRead]
