import pytest
from app.core.scoring import calculate_transparent_match_score

def test_empty_assessments_returns_none():
    score, mand_cov, pref_cov, note = calculate_transparent_match_score([])
    assert score is None
    assert "Insufficient" in note

def test_perfect_alignment_score():
    assessments = [
        {"priority": "mandatory", "classification": "Demonstrated"},
        {"priority": "mandatory", "classification": "Demonstrated"},
        {"priority": "preferred", "classification": "Demonstrated"}
    ]
    score, mand_cov, pref_cov, note = calculate_transparent_match_score(assessments)
    assert score == 100.0
    assert mand_cov == 100.0
    assert pref_cov == 100.0

def test_weighted_formula_calculation():
    # Mandatory (weight 3.0), Preferred (weight 1.5)
    # Case: 1 Mandatory Demonstrated (3.0 * 1.0 = 3.0)
    #       1 Mandatory Missing (3.0 * 0.0 = 0.0)
    #       1 Preferred Partially Demonstrated (1.5 * 0.5 = 0.75)
    # Total weight: 3.0 + 3.0 + 1.5 = 7.5
    # Earned: 3.0 + 0.0 + 0.75 = 3.75
    # Expected overall: (3.75 / 7.5) * 100 = 50.0%
    assessments = [
        {"priority": "mandatory", "classification": "Demonstrated"},
        {"priority": "mandatory", "classification": "Not found in resume"},
        {"priority": "preferred", "classification": "Partially demonstrated"}
    ]
    score, mand_cov, pref_cov, note = calculate_transparent_match_score(assessments)
    assert score == 50.0
    assert mand_cov == 50.0 # 1 out of 2 mandatory
    assert pref_cov == 50.0 # 0.5 out of 1 preferred
