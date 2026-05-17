"""
Financial Risk Agent — estimates monetary exposure from the clause.
Returns: exposure_inr, exposure_category, financial_risks.
"""

from typing import Dict, Any
import re


def analyze(clause_number: int, title: str, text: str) -> Dict[str, Any]:
    """
    Estimates financial exposure in INR from clause language.
    In production: call LLM with FINANCIAL_RISK_SYSTEM_PROMPT.
    """
    text_lower = text.lower()

    exposure_inr = 0
    financial_risks = []
    confidence = 0.78

    # Pattern-based financial risk estimation
    risk_patterns = [
        {
            "triggers": ["intellectual property", "inventions", "discoveries", "works of authorship"],
            "exposure": 500000,  # ₹5L — lost IP ownership potential
            "risk": "IP ownership transfer could be worth ₹5L–₹50L+ if invention is commercialized"
        },
        {
            "triggers": ["sole and exclusive property"],
            "exposure": 300000,
            "risk": "Exclusivity clause forfeits all future royalties and licensing revenue"
        },
        {
            "triggers": ["termination", "without cause", "24 hours"],
            "exposure": 150000,
            "risk": "Zero severance + 24hr termination = potential ₹1.5L+ lost income"
        },
        {
            "triggers": ["waives any right", "severance", "compensation upon termination"],
            "exposure": 200000,
            "risk": "Waiver of severance rights can cost ₹2L–₹10L depending on tenure"
        },
        {
            "triggers": ["liability", "shall be limited to", "5,000", "five thousand"],
            "exposure": 0,  # Company liability is near zero
            "risk": "Asymmetric cap: Company's liability to you is ₹5,000 regardless of harm"
        },
        {
            "triggers": ["personal data", "third parties", "affiliated entities"],
            "exposure": 50000,
            "risk": "Data misuse / breach liability shifts to user; DPDP Act penalties could apply"
        },
        {
            "triggers": ["arbitration", "waives the right", "class action"],
            "exposure": 100000,
            "risk": "Forced arbitration forecloses class action; individual claim value drops ~₹1L"
        },
    ]

    triggered_risks = set()
    for pattern in risk_patterns:
        hits = sum(1 for t in pattern["triggers"] if t in text_lower)
        if hits >= 1 and pattern["risk"] not in triggered_risks:
            exposure_inr += pattern["exposure"]
            financial_risks.append(pattern["risk"])
            triggered_risks.add(pattern["risk"])

    # Detect explicit currency amounts in text
    inr_amounts = re.findall(r'₹\s*([\d,]+)', text)
    for amt in inr_amounts:
        val = int(amt.replace(",", ""))
        if val < 10000:
            # Likely a cap that limits YOUR protection
            financial_risks.append(f"Explicit ₹{val:,} liability cap — dangerously low for real damages")

    # Exposure category
    if exposure_inr >= 200000:
        category = "CRITICAL"
        verdict = f"Estimated financial exposure: ₹{exposure_inr:,}+. Significant monetary risk to user."
    elif exposure_inr >= 50000:
        category = "HIGH"
        verdict = f"Estimated financial exposure: ₹{exposure_inr:,}. Material risk to user finances."
    elif exposure_inr > 0:
        category = "MEDIUM"
        verdict = f"Estimated financial exposure: ₹{exposure_inr:,}. Moderate risk."
    else:
        category = "LOW"
        verdict = "No direct financial exposure identified. Monitor indirect risks."

    return {
        "agent": "Financial Risk",
        "exposure_inr": exposure_inr,
        "exposure_category": category,
        "verdict": verdict,
        "financial_risks": financial_risks,
        "confidence": confidence,
        "notes": f"₹{exposure_inr:,} estimated exposure | {len(financial_risks)} risk factor(s)"
    }
