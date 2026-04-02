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
    user_answer_naf: "NafAnswers"
    naf_score: Optional[int]
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
    disease_severity3_other: str
    disease_severity6: List[str]
    disease_severity6_other: str
#to be done
class SpentNafSummary(BaseModel):
    model_config = common_config

    id: int
    user_answer_spent: List[int]
    spent_score: Optional[int]
    is_high_risk: Optional[bool]
    naf_score: Optional[int]
    status: str
    submitted_at: Optional[datetime]
