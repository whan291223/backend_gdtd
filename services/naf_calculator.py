"""Business logic for NAF score calculation"""
from schema.spent_naf_schema import NafAnswers


def calculate_naf_score(answers: NafAnswers) -> int:
    """
    Calculate NAF (Nutritional Assessment Form) score from user answers.
    
    Args:
        answers: NafAnswers object containing all form responses
        
    Returns:
        int: Calculated NAF score
    """
    score = 0
    
    # Weight method
    if answers.weight_method == "lying":
        score += 1
    
    # BMI
    bmi = float(answers.bmi) if answers.bmi else 0
    if bmi > 0:
        if bmi < 16:
            score += 2
        elif bmi < 18.5:
            score += 1
        elif bmi >= 30:
            score += 1
    
    # Obesity level
    if answers.obeseLevel == "thinest":
        score += 2
    elif answers.obeseLevel == "thin":
        score += 1
    elif answers.obeseLevel == "obese":
        score += 1
    
    # Weight change
    if answers.weight_change == "decreased":
        score += 2
    elif answers.weight_change == "increased":
        score += 1
    
    # Food consistency
    if answers.food_consistency in ["watery", "liquid"]:
        score += 2
    elif answers.food_consistency == "soft":
        score += 1
    
    # Food quantity
    if answers.food_quantity == "veryLittle":
        score += 2
    elif answers.food_quantity == "less":
        score += 1
    
    # Food access
    if "bedridden" in answers.food_access:
        score += 2
    if "needsHelp" in answers.food_access:
        score += 1
    
    # Swallow problems
    for val in answers.swallow_problem:
        if val == "immobile":
            score += 2
        elif val == "limited":
            score += 1
    
    # Intestine problems
    for val in answers.intestine_problem:
        if val == "severe":
            score += 3
        elif val == "moderate":
            score += 2
        elif val == "mild":
            score += 1
    
    # Eating problems
    for val in answers.eating_problem:
        if val == "poor":
            score += 2
        elif val == "reduced":
            score += 1
    
    # Disease severity
    score += len(answers.disease_severity3) * 3
    score += len(answers.disease_severity3_other.split(',')) * 3
    score += len(answers.disease_severity6) * 6
    score += len(answers.disease_severity6_other.split(',')) * 6
    return score