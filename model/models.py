from typing import List, Optional
from sqlmodel import Field, SQLModel,Column
from sqlalchemy import ARRAY, Integer

from datetime import datetime, timezone
from enum import Enum

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    line_user_id: str = Field(index=True, unique=True)
    display_name: Optional[str] = None
    picture_url: Optional[str] = None

    real_name: Optional[str] = None
    surname: Optional[str] = None


class SpentNafScore(SQLModel, table=True):
    __tablename__ = "user_answer_table"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None)

    # --- Page 1: Spent answers ---
    user_answer_spent: List[int] = Field(
        default=[],
        sa_column=Column(ARRAY(Integer), nullable=True)
    )
    spent_score: Optional[int] = Field(default=None)

    # --- Routing decision ---
    is_high_risk: Optional[bool] = Field(default=None)

    # --- Page 2: NAF answers (only if high risk) ---
    user_answer_naf: List[int] = Field(
        default=[],
        sa_column=Column(ARRAY(Integer), nullable=True)
    )
    naf_score: Optional[int] = Field(default=None)

    # --- Session state ---
    status: str = Field(default="pending_spent")
    # pending_spent → pending_naf → completed (skipped_naf if not high risk)

    submitted_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )