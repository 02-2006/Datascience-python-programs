"""
Simplification Agent — converts dense legal language into plain English.
Returns: plain_english, reading_grade_level, undefined_terms.
"""

from typing import Dict, Any, List
import re


LEGAL_REPLACEMENTS = {
    r'\bhereinafter\b': 'from now on called',
    r'\bwhereas\b': 'given that',
    r'\bnotwithstanding\b': 'despite',
    r'\binter alia\b': 'among other things',
    r'\bpursuant to\b': 'under',
    r'\bin its sole discretion\b': 'however the company decides',
    r'\bat any time\b': 'whenever they want',
    r'\bwithout cause\b': 'for any reason or no reason',
    r'\bwithout notice\b': 'with no warning',
    r'\bshall be\b': 'is / will be',
    r'\bshall\b': 'must',
    r'\bhereby\b': 'by signing this',
    r'\bthereunto\b': 'to that',
    r'\bhereof\b': 'of this agreement',
    r'\bwhether or not\b': 'even if',
    r'\bincluding but not limited to\b': 'including (and not just)',
    r'\bbinding arbitration\b': 'private dispute resolution (not a court)',
    r'\bwaives any right\b': 'gives up the right',
    r'\bsole and exclusive property\b': 'entirely owned by the company',
    r'\bworks of authorship\b': 'creative works you make',
    r'\bintellectual property\b': 'inventions, ideas, and creative works',
    r'\baffiliated entities\b': 'related companies',
}

UNDEFINED_LEGAL_TERMS = [
    "reasonable", "material", "substantial", "appropriate", "necessary",
    "relevant", "customary", "industry standard", "good faith", "promptly",
    "adequate", "sufficient", "timely", "commercially reasonable"
]


def analyze(clause_number: int, title: str, text: str) -> Dict[str, Any]:
    """
    Converts legal jargon to plain English and flags undefined terms.
    """
    simplified = text

    # Apply replacements
    for pattern, replacement in LEGAL_REPLACEMENTS.items():
        simplified = re.sub(pattern, replacement, simplified, flags=re.IGNORECASE)

    # Remove redundant legal preamble phrases
    simplified = re.sub(r'\bEmployee hereby agrees and acknowledges that\b', 'You agree that', simplified, flags=re.IGNORECASE)
    simplified = re.sub(r'\bThe Company reserves the right to\b', 'The Company can', simplified, flags=re.IGNORECASE)
    simplified = re.sub(r'\bAll disputes arising out of or relating to\b', 'All arguments about', simplified, flags=re.IGNORECASE)

    # Trim to reasonable length
    simplified = simplified.strip()
    if len(simplified) > 500:
        simplified = simplified[:497] + "…"

    # Count undefined terms
    undefined = [t for t in UNDEFINED_LEGAL_TERMS if t.lower() in text.lower()]

    # Estimate reading grade (crude Flesch-Kincaid proxy)
    words = len(text.split())
    sentences = max(1, len(re.findall(r'[.!?]', text)))
    syllables = sum(max(1, len(re.findall(r'[aeiouAEIOU]', w))) for w in text.split())
    fk_grade = 0.39 * (words / sentences) + 11.8 * (syllables / words) - 15.59
    grade = max(6, min(22, round(fk_grade)))

    return {
        "agent": "Simplification",
        "plain_english": simplified,
        "reading_grade_original": grade,
        "undefined_terms": undefined,
        "undefined_count": len(undefined),
        "confidence": 0.88,
        "notes": f"Grade {grade} reading level. {len(undefined)} undefined term(s)."
    }
