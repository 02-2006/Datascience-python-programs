"""
Adversarial Lawyer Agent — thinks like opposing counsel exploiting every loophole.
Returns: exploitability_score (1-10), attack_vectors, and worst_case_interpretation.
"""

from typing import Dict, Any


def analyze(clause_number: int, title: str, text: str) -> Dict[str, Any]:
    """
    Simulates an aggressive lawyer finding every way to weaponize the clause against the user.
    In production: call LLM with ADVERSARIAL_SYSTEM_PROMPT.
    """
    text_lower = text.lower()

    # High-exploit signals
    exploit_patterns = {
        "sole discretion":        (3, "Company can redefine terms unilaterally at any time"),
        "at any time":            (2, "No time-bound protections — termination or change possible immediately"),
        "without cause":          (3, "Zero accountability required — termination requires no justification"),
        "without notice":         (2, "User gets no warning before adverse action"),
        "waives any right":       (3, "User permanently surrenders legal protections"),
        "regardless of":          (2, "Caps protection — company escapes liability even in negligence"),
        "intellectual property":  (2, "Potential assignment of IP created off-hours / on personal devices"),
        "whether or not":         (2, "Broadens scope beyond employment boundaries"),
        "personal data":          (2, "Data rights transferred without meaningful consent"),
        "arbitration":            (2, "Forces private dispute resolution; blocks class action"),
        "shall be limited":       (2, "Asymmetric cap disadvantages the weaker party"),
        "binding":                (1, "Irrevocable commitment — hard to undo"),
    }

    total_score = 0
    attack_vectors = []
    worst_interpretations = []

    for pattern, (weight, attack) in exploit_patterns.items():
        if pattern in text_lower:
            total_score += weight
            attack_vectors.append(attack)
            worst_interpretations.append(f"'{pattern}' → {attack}")

    # Scale to 1-10
    exploitability = min(10, max(1, total_score))

    if exploitability >= 9:
        confidence = 0.94
        verdict = "Extremely dangerous. Multiple high-severity attack vectors confirmed."
    elif exploitability >= 7:
        confidence = 0.89
        verdict = "High exploitability. A skilled opposing counsel would use this aggressively."
    elif exploitability >= 4:
        confidence = 0.82
        verdict = "Moderate exploitability. Risk is real but requires specific circumstances."
    else:
        confidence = 0.75
        verdict = "Low exploitability. Standard protective language present."

    return {
        "agent": "Adversarial Lawyer",
        "exploitability_score": exploitability,
        "verdict": verdict,
        "attack_vectors": attack_vectors[:3],  # Top 3 most dangerous
        "worst_case_interpretation": worst_interpretations,
        "confidence": confidence,
        "notes": f"Identified {len(attack_vectors)} exploit vector(s)"
    }
