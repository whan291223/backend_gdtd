# services/naf_calculator.py

"""Business logic for NAF score calculation"""
from schema.spent_naf_schema import NafAnswers, NafScoreBreakdown
from typing import Tuple


def calculate_naf_score(answers: NafAnswers) -> Tuple[int, NafScoreBreakdown]:
    """
    Calculate NAF (Nutritional Assessment Form) score from user answers.
    
    Args:
        answers: NafAnswers object containing all form responses
        
    Returns:
        Tuple[int, NafScoreBreakdown]: Total score and detailed breakdown
    """
    breakdown = NafScoreBreakdown()
    
    # Weight method
    if answers.weight_method == "lying":
        breakdown.weight_method = 1
    
    # BMI
    bmi = float(answers.bmi) if answers.bmi else 0
    if bmi > 0:
        if bmi < 16:
            breakdown.bmi = 2
        elif bmi < 18.5:
            breakdown.bmi = 1
        elif bmi >= 30:
            breakdown.bmi = 1
    
    # Obesity level
    if answers.obeseLevel == "thinest":
        breakdown.obese_level = 2
    elif answers.obeseLevel == "thin":
        breakdown.obese_level = 1
    elif answers.obeseLevel == "obese":
        breakdown.obese_level = 1
    
    # Weight change
    if answers.weight_change == "decreased":
        breakdown.weight_change = 2
    elif answers.weight_change == "increased":
        breakdown.weight_change = 1
    
    # Food consistency
    if answers.food_consistency in ["watery", "liquid"]:
        breakdown.food_consistency = 2
    elif answers.food_consistency == "soft":
        breakdown.food_consistency = 1
    
    # Food quantity
    if answers.food_quantity == "veryLittle":
        breakdown.food_quantity = 2
    elif answers.food_quantity == "less":
        breakdown.food_quantity = 1
    
    # Food access
    if "bedridden" in answers.food_access:
        breakdown.food_access += 2
    if "needsHelp" in answers.food_access:
        breakdown.food_access += 1
    
    # Swallow problems
    for val in answers.swallow_problem:
        if val == "immobile":
            breakdown.swallow_problem += 2
        elif val == "limited":
            breakdown.swallow_problem += 1
    
    # Intestine problems
    for val in answers.intestine_problem:
        if val == "severe":
            breakdown.intestine_problem += 3
        elif val == "moderate":
            breakdown.intestine_problem += 2
        elif val == "mild":
            breakdown.intestine_problem += 1
    
    # Eating problems
    for val in answers.eating_problem:
        if val == "poor":
            breakdown.eating_problem += 2
        elif val == "reduced":
            breakdown.eating_problem += 1
    
    # Disease severity 3 points
    breakdown.disease_severity3 = len(answers.disease_severity3) * 3
    if answers.disease_severity3_other and answers.disease_severity3_other.strip():
        other_diseases = [d.strip() for d in answers.disease_severity3_other.split(',') if d.strip()]
        breakdown.disease_severity3 += len(other_diseases) * 3
    
    # Disease severity 6 points
    breakdown.disease_severity6 = len(answers.disease_severity6) * 6
    if answers.disease_severity6_other and answers.disease_severity6_other.strip():
        other_diseases = [d.strip() for d in answers.disease_severity6_other.split(',') if d.strip()]
        breakdown.disease_severity6 += len(other_diseases) * 6
    
    # Calculate total
    breakdown.total = (
        breakdown.weight_method +
        breakdown.bmi +
        breakdown.obese_level +
        breakdown.weight_change +
        breakdown.food_consistency +
        breakdown.food_quantity +
        breakdown.food_access +
        breakdown.swallow_problem +
        breakdown.intestine_problem +
        breakdown.eating_problem +
        breakdown.disease_severity3 +
        breakdown.disease_severity6
    )
    
    return breakdown.total, breakdown