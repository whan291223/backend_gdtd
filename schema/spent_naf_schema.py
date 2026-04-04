from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from schema.config import common_config


# POST /test/spent/{line_user_id} — user_id now comes from URL, not body
class SpentSubmit(BaseModel):
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
    user_answer_naf: Optional["NafAnswers"] = None
    naf_score: Optional[int]
    naf_score_breakdown: Optional["NafScoreBreakdown"] = None
    naf_level: Optional[str] = None
    naf_recommendations: Optional[List[str]] = None
    status: str
    submitted_at: Optional[datetime]

class NafAnswers(BaseModel):
    model_config = common_config

    height: str
    arm_span: str
    body_length: str
    weight: str
    weight_method: str
    relatives: str
    obeseLevel: str
    bmi: str
    weight_change: str
    food_consistency: str
    food_quantity: str
    swallow_problem: List[str]
    intestine_problem: List[str]
    eating_problem: List[str]
    food_access: List[str]
    disease_severity3: List[str]
    disease_severity6: List[str]
#to be done
class SpentNafSummary(BaseModel):
    model_config = common_config

    id: int
    user_answer_spent: List[int]
    spent_score: Optional[int]
    is_high_risk: Optional[bool]
    naf_score: Optional[int]
    naf_score_breakdown: Optional["NafScoreBreakdown"] = None
    status: str
    submitted_at: Optional[datetime]

# NAF Score Breakdown - shows how the score was calculated
class NafScoreBreakdown(BaseModel):
    model_config = common_config

    weight_method: int = 0
    bmi: int = 0
    obese_level: int = 0
    weight_change: int = 0
    food_consistency: int = 0
    food_quantity: int = 0
    food_access: int = 0
    swallow_problem: int = 0
    intestine_problem: int = 0
    eating_problem: int = 0
    disease_severity3: int = 0
    disease_severity6: int = 0
    total: int = 0