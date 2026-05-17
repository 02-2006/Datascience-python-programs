"""
Judge Agent — evaluates contractual fairness based on established legal principles.
Returns: fairness_score (1-10), assessment, and flagged issues.
"""

from typing import Dict, Any
import re


def analyze(clause_number: int, title: str, text: str) -> Dict[str, Any]:
    """
    Simulates a senior contract law judge evaluating clause fairness.
    In production: call LLM with JUDGE_SYSTEM_PROMPT.
    """
    text_lower = text.lower()

    # Heuristic signals
    one_sided_terms = [
        "sole discretion", "at any time", "without cause", "without notice",
        "without liability", "in its sole judgment", "as determined by company",
        "waives any right", "regardless of"
    ]
    fair_terms = [
        "mutual", "both parties", "reasonable notice", "fair compensation",
        "equitable", "in good faith"
    ]

    one_sided_count = sum(1 for t in one_sided_terms if t in text_lower)
    fair_count = sum(1 for t in fair_terms if t in text_lower)

    # Compute fairness score (1=most unfair, 10=most fair)
    base = 7
    score = max(1, min(10, base - (one_sided_count * 1.5) + (fair_count * 1.0)))
    score = round(score)

    # Legal assessment
    if score <= 3:
        assessment = "Severely one-sided. Would likely be challenged under unconscionability doctrine."
        confidence = 0.88
    elif score <= 5:
        assessment = "Below standard fairness. Favors one party disproportionately."
        confidence = 0.82
    elif score <= 7:
        assessment = "Moderately fair. Some terms could be more balanced."
        confidence = 0.75
    else:
        assessment = "Reasonably balanced. Consistent with standard contract law principles."
        confidence = 0.80

    flagged = [t for t in one_sided_terms if t in text_lower]

    return {
        "agent": "Judge",
        "fairness_score": score,
        "assessment": assessment,
        "flagged_terms": flagged,
        "confidence": confidence,
        "notes": f"Found {one_sided_count} one-sided term(s), {fair_count} fair term(s)"
    }
