"""
Psychologist Agent — detects dark patterns, cognitive manipulation, and
deceptive framing in legal language.
Returns: manipulation_detected, patterns_found, psychological_impact.
"""

from typing import Dict, Any, List


def analyze(clause_number: int, title: str, text: str) -> Dict[str, Any]:
    """
    Evaluates clause for psychological manipulation tactics.
    In production: call LLM with PSYCHOLOGIST_SYSTEM_PROMPT.
    """
    text_lower = text.lower()

    dark_patterns: List[Dict] = []
    manipulation_score = 0

    pattern_library = [
        {
            "trigger": "sole discretion",
            "pattern": "False Legitimacy",
            "weight": 3,
            "explanation": "Wraps unilateral control in formal legal language, implying fairness that doesn't exist."
        },
        {
            "trigger": "whether or not",
            "pattern": "Scope Creep Camouflage",
            "weight": 3,
            "explanation": "Expands rights beyond obvious boundaries using ambiguous phrasing — user may not notice."
        },
        {
            "trigger": "waives any right",
            "pattern": "Consent Hijacking",
            "weight": 3,
            "explanation": "User 'agrees' to surrender rights without realizing the downstream consequences."
        },
        {
            "trigger": "as deemed necessary",
            "pattern": "Vague Authority",
            "weight": 2,
            "explanation": "Undefined standard gives company unlimited discretion while appearing reasonable."
        },
        {
            "trigger": "including but not limited to",
            "pattern": "Open-Ended Expansion",
            "weight": 2,
            "explanation": "Creates false sense of specificity while leaving scope fully open."
        },
        {
            "trigger": "without cause",
            "pattern": "False Security",
            "weight": 2,
            "explanation": "User may feel protected by notice periods, not realizing 'without cause' removes them."
        },
        {
            "trigger": "binding arbitration",
            "pattern": "Access Denial",
            "weight": 3,
            "explanation": "Removes access to courts using formal-sounding alternative — user loses class action rights."
        },
        {
            "trigger": "regardless",
            "pattern": "Unconditional Surrender",
            "weight": 2,
            "explanation": "Removes any scenario where user could claim protection — creates hopelessness."
        },
        {
            "trigger": "exclusively",
            "pattern": "Monopoly Framing",
            "weight": 1,
            "explanation": "Suggests no alternatives exist — user feels locked in without seeking legal advice."
        },
    ]

    for item in pattern_library:
        if item["trigger"] in text_lower:
            dark_patterns.append({
                "pattern": item["pattern"],
                "explanation": item["explanation"]
            })
            manipulation_score += item["weight"]

    manipulation_detected = manipulation_score >= 3

    if manipulation_score >= 8:
        severity = "severe"
        verdict = "Highly manipulative language. Multiple dark patterns designed to obscure user rights."
        confidence = 0.91
    elif manipulation_score >= 4:
        severity = "moderate"
        verdict = "Dark patterns present. User comprehension is intentionally impaired."
        confidence = 0.84
    elif manipulation_detected:
        severity = "mild"
        verdict = "Minor manipulation signals detected. Clause benefits from clearer framing."
        confidence = 0.77
    else:
        severity = "none"
        verdict = "No significant manipulation detected. Language appears straightforward."
        confidence = 0.72

    return {
        "agent": "Psychologist",
        "manipulation_detected": manipulation_detected,
        "severity": severity,
        "verdict": verdict,
        "dark_patterns": dark_patterns,
        "manipulation_score": manipulation_score,
        "confidence": confidence,
        "notes": f"{len(dark_patterns)} dark pattern(s) found"
    }
