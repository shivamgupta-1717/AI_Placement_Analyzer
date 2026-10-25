from typing import List, Dict, Any, Optional, Tuple

MANDATORY_WEIGHT = 3.0
PREFERRED_WEIGHT = 1.5

ADEQUACY_MAP = {
    "Demonstrated": 1.0,
    "Partially demonstrated": 0.5,
    "Not found in resume": 0.0,
    "Uncertain": 0.0
}

def calculate_transparent_match_score(assessments: List[Dict[str, Any]]) -> Tuple[Optional[float], Optional[float], Optional[float], str]:
    """
    Calculates transparent, weighted match scores:
    Match Score = (Sum(weight_i * adequacy_i) / Sum(weight_i)) * 100

    Returns:
        (overall_score, mandatory_coverage, preferred_coverage, explanation_notes)
    """
    if not assessments:
        return (None, None, None, "Insufficient requirements found in job description to calculate a meaningful score.")

    total_weight = 0.0
    weighted_adequacy_sum = 0.0

    mandatory_total = 0.0
    mandatory_earned = 0.0

    preferred_total = 0.0
    preferred_earned = 0.0

    for a in assessments:
        priority = a.get("priority", "mandatory").lower()
        classification = a.get("classification", "Not found in resume")
        adequacy = ADEQUACY_MAP.get(classification, 0.0)

        weight = MANDATORY_WEIGHT if priority == "mandatory" else PREFERRED_WEIGHT
        total_weight += weight
        weighted_adequacy_sum += (weight * adequacy)

        if priority == "mandatory":
            mandatory_total += 1.0
            mandatory_earned += adequacy
        else:
            preferred_total += 1.0
            preferred_earned += adequacy

    if total_weight == 0:
        return (None, None, None, "No weighted requirements available.")

    overall_score = round((weighted_adequacy_sum / total_weight) * 100.0, 1)

    mandatory_cov = round((mandatory_earned / mandatory_total) * 100.0, 1) if mandatory_total > 0 else 100.0
    preferred_cov = round((preferred_earned / preferred_total) * 100.0, 1) if preferred_total > 0 else 100.0

    explanation = (
        f"Alignment Score: {overall_score}% based on {len(assessments)} evaluated requirements "
        f"(Mandatory Coverage: {mandatory_cov}%, Preferred Coverage: {preferred_cov}%). "
        "Notice: This reflects resume-to-job description alignment and does not represent a hiring guarantee."
    )

    return (overall_score, mandatory_cov, preferred_cov, explanation)
