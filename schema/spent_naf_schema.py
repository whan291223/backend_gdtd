from typing import List, Optional
from schema.base_schema import BaseSchema
from datetime import datetime


# POST /test/spent/{line_user_id} — user_id now comes from URL, not body
class SpentSubmit(BaseSchema):
    answers: List[int]


# PUT /test/naf/{test_session_id} — session_id now comes from URL, not body
class NafSubmit(BaseSchema):
    answers: List[int]


# Response after submitting SPENT
class SpentSubmitResponse(BaseSchema):
    session_id: int
    spent_score: int
    is_high_risk: bool
    status: str


# Response after submitting NAF
class NafSubmitResponse(BaseSchema):
    session_id: int
    naf_score: int
    status: str


# Full session record (for history / result pages)
class SpentNafScoreRead(BaseSchema):
    id: int
    user_id: int
    user_answer_spent: List[int]
    spent_score: Optional[int]
    is_high_risk: Optional[bool]
    user_answer_naf: List[int]
    naf_score: Optional[int]
    status: str
    submitted_at: Optional[datetime]


class SpentNafSummary(BaseSchema):
    id: int
    spent_score: Optional[int]
    is_high_risk: Optional[bool]
    naf_score: Optional[int]
    status: str
    submitted_at: Optional[datetime]
