"""
Document Processor — splits raw contract text into labeled clauses.
Handles common patterns: "CLAUSE N", numbered sections, headers in ALL CAPS.
"""

import re
from typing import List, Tuple


def extract_clauses(text: str) -> List[Tuple[int, str, str]]:
    """
    Returns list of (clause_number, title, body_text) tuples.
    Falls back to paragraph splitting if no structure detected.
    """
    text = text.strip()
    clauses = []

    # Pattern 1: CLAUSE N — TITLE
    pattern1 = re.compile(
        r'(?:CLAUSE|SECTION|ARTICLE)\s+(\d+)\s*[—\-–:]\s*([A-Z][^\n]+)',
        re.IGNORECASE
    )
    matches = list(pattern1.finditer(text))

    if len(matches) >= 2:
        for i, match in enumerate(matches):
            num = int(match.group(1))
            title = match.group(2).strip().title()
            start = match.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            body = text[start:end].strip()
            if body:
                clauses.append((num, title, body))
        return clauses

    # Pattern 2: Numbered sections like "1. TITLE\n body"
    pattern2 = re.compile(
        r'^(\d+)\.\s+([A-Z][A-Z\s]+)\n([\s\S]+?)(?=^\d+\.\s+[A-Z]|\Z)',
        re.MULTILINE
    )
    matches = list(pattern2.finditer(text))
    if len(matches) >= 2:
        for match in matches:
            num = int(match.group(1))
            title = match.group(2).strip().title()
            body = match.group(3).strip()
            if body:
                clauses.append((num, title, body))
        return clauses

    # Fallback: split by double newlines, treat each block as a clause
    paragraphs = [p.strip() for p in re.split(r'\n{2,}', text) if p.strip()]
    for i, para in enumerate(paragraphs):
        # Try to extract title from first line
        lines = para.split('\n')
        first = lines[0].strip()
        if len(first) < 80 and first.isupper():
            title = first.title()
            body = '\n'.join(lines[1:]).strip() or para
        else:
            title = f"Clause {i + 1}"
            body = para
        clauses.append((i + 1, title, body))

    return clauses

def analyze_clause_metadata(title: str, text: str) -> dict:
    """
    Analyzes raw title and text to generate a meaningful title, 
    detect informational headings, and assign a clause type.
    """
    text_lower = text.lower()
    title_lower = title.lower()
    
    # 1. Detect Informational
    # Headings ONLY should be informational. 
    # A clause may ONLY be informational if it contains no obligations/rights/liabilities
    words = text.split()
    obligations = ['shall', 'must', 'will', 'agrees', 'liability', 'warrant', 'indemnify', 'waive', 'terminate', 'right', 'may', 'reserve', 'restrict', 'consent', 'prohibit']
    has_obligations = any(o in text_lower for o in obligations)
    
    is_informational = False
    if len(words) < 10 and not has_obligations and not text.endswith('.'):
        is_informational = True
        
    # 2. Determine Clause Type and Meaningful Title
    clause_type = "General"
    meaningful_title = title if not title.startswith("Clause") else "General Provisions"
    
    if any(k in text_lower or k in title_lower for k in ["competing organization", "non compete", "not work with competitors", "non-compete", "competitor"]):
        clause_type = "Non-Compete"
        meaningful_title = "Post-Employment Non-Compete"
    elif any(k in text_lower or k in title_lower for k in ["terminate", "without notice", "termination"]):
        clause_type = "Termination"
        if "without cause" in text_lower or "without notice" in text_lower:
            meaningful_title = "Unilateral Termination Rights"
        else:
            meaningful_title = "Termination Conditions"
    elif any(k in text_lower or k in title_lower for k in ["stipend", "compensation", "salary", "bonus", "payment"]):
        clause_type = "Compensation"
        meaningful_title = "Compensation & Benefits"
    elif any(k in text_lower or k in title_lower for k in ["ideas", "code", "ownership", "exclusive property", "intellectual property", "ip", "invention"]):
        clause_type = "Intellectual Property"
        if "exclusive" in text_lower or "sole" in text_lower:
            meaningful_title = "Exclusive IP Ownership"
        else:
            meaningful_title = "Intellectual Property Rights"
    elif any(k in text_lower or k in title_lower for k in ["arbitration", "disputes", "court", "dispute"]):
        clause_type = "Dispute Resolution"
        if "waive" in text_lower and "class action" in text_lower:
            meaningful_title = "One-Sided Arbitration & Class Action Waiver"
        else:
            meaningful_title = "Dispute Resolution"
    elif any(k in text_lower or k in title_lower for k in ["data", "privacy", "personal data"]):
        clause_type = "Privacy"
        if "waives" in text_lower or "sole discretion" in text_lower:
            meaningful_title = "Broad Data Collection Rights"
        else:
            meaningful_title = "Data Privacy & Handling"
    elif "liabilit" in title_lower or "liabilit" in text_lower:
        clause_type = "Financial"
        if "exceed" in text_lower and "limited" in text_lower:
            meaningful_title = "Asymmetrical Liability Limitation"
        else:
            meaningful_title = "Limitation of Liability"

    # Use original title if we already had a decent one and it wasn't generic
    if title != meaningful_title and not title.lower().startswith("clause"):
        pass

    # Override for strictly headings
    if is_informational:
        clause_type = "Compliance"
        meaningful_title = title if title.strip() else "Document Heading"

    return {
        "title": meaningful_title,
        "clause_type": clause_type,
        "is_informational": is_informational
    }
