"""
Consumer Rights Agent — evaluates clause against Indian consumer protection law
(Consumer Protection Act 2019, IT Act, DPDP Act 2023).
Returns: protection_level, violations, and user_rights_impact.
"""

from typing import Dict, Any


def analyze(clause_number: int, title: str, text: str) -> Dict[str, Any]:
    """
    Evaluates clause from a consumer / worker rights perspective.
    In production: call LLM with CONSUMER_RIGHTS_SYSTEM_PROMPT.
    """
    text_lower = text.lower()

    # Consumer protection red flags
    violations = []
    protection_score = 10  # Start high, deduct for violations

    checks = [
        ("waives any right",        3, "CPA 2019 §47 — waiver of statutory rights is non-enforceable"),
        ("sole discretion",         2, "Violates principle of equitable treatment (CPA 2019 §2(9))"),
        ("without cause",           2, "May violate natural justice under employment law"),
        ("without notice",          2, "Due process violation — notice is a fundamental right"),
        ("personal data",           2, "Must comply with DPDP Act 2023 — explicit consent required"),
        ("third parties",           2, "DPDP Act mandates data localization and transfer restrictions"),
        ("arbitration",             1, "CPA 2019 allows consumer forums; mandatory arbitration may be void"),
        ("shall be limited to",     2, "Asymmetric liability cap may be unconscionable under CPA"),
        ("intellectual property",   1, "IP assignment scope must be reasonable — Indian Patents Act §6"),
        ("whether or not",          2, "Excessive scope contradicts reasonable person standard"),
    ]

    for term, penalty, law_ref in checks:
        if term in text_lower:
            protection_score = max(0, protection_score - penalty)
            violations.append({"term": term, "law_ref": law_ref})

    if protection_score >= 8:
        protection_level = "strong"
        verdict = "Clause adequately protects consumer rights."
        confidence = 0.80
    elif protection_score >= 5:
        protection_level = "weak"
        verdict = "Significant consumer protection gaps. User rights partially compromised."
        confidence = 0.85
    else:
        protection_level = "none"
        verdict = "Consumer rights severely undermined. Multiple statutory violations likely."
        confidence = 0.90

    return {
        "agent": "Consumer Rights",
        "protection_level": protection_level,
        "protection_score": protection_score,
        "verdict": verdict,
        "violations": violations,
        "confidence": confidence,
        "notes": f"{len(violations)} potential statutory violation(s) identified"
    }
