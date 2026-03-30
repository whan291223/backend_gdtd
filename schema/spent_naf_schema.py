from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from schema.config import common_config


# POST /test/spent/{line_user_id} — user_id now comes from URL, not body
class SpentSubmit(BaseModel):
    model_config = common_config

    answers: List[int]


# PUT /test/naf/{test_session_id} — session_id now comes from URL, not body
class NafSubmit(BaseModel):
    model_config = common_config

    answers: List[int]


# Response after submitting SPENT
class SpentSubmitResponse(BaseModel):
    model_config = common_config

    session_id: int
    spent_score: int
    is_high_risk: bool
    status: str


# Response after submitting NAF
class NafSubmitResponse(BaseModel):
    model_config = common_config

    session_id: int
    naf_score: int
    status: str


# Full session record (for history / result pages)
class SpentNafScoreRead(BaseModel):
    model_config = common_config

    id: int
    user_id: int
    user_answer_spent: List[int]
    spent_score: Optional[int]
    is_high_risk: Optional[bool]
    # user_answer_naf: List[int]
    naf_score: Optional[int]
    status: str
    submitted_at: Optional[datetime]


class SpentNafSummary(BaseModel):
    model_config = common_config

    id: int
    user_answer_spent: List[int]
    spent_score: Optional[int]
    is_high_risk: Optional[bool]
    naf_score: Optional[int]
    status: str
    submitted_at: Optional[datetime]
