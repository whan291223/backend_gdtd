from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# POST /test/spent — submit spent answers
class SpentSubmit(BaseModel):
    user_id: int
    answers: List[int]

# POST /test/naf — submit naf answers (high risk only)
class NafSubmit(BaseModel):
    session_id: int
    answers: List[int]

# Response after submitting spent
class SpentSubmitResponse(BaseModel):
    session_id: int
    spent_score: int
    is_high_risk: bool
    status: str

# Response after submitting naf
class NafSubmitResponse(BaseModel):
    session_id: int
    naf_score: int
    status: str

# Full session record (for history page)
class SpentNafScoreRead(BaseModel):
    id: int
    user_id: int
    user_answer_spent: List[int]
    spent_score: Optional[int]
    is_high_risk: Optional[bool]
    user_answer_naf: List[int]
    naf_score: Optional[int]
    status: str
    submitted_at: Optional[datetime]
