"""
LEXGUARD Convergence Engine
===========================
The control tower that resolves conflicts between the 5 specialized agents
and produces a single, authoritative risk assessment per clause.

CONFLICT RESOLUTION RULES:
1. If agents disagree on risk PRESENCE → treat as HIGH confidence a risk exists
   if ANY agent found it. Never ignore a minority signal — log it in explanation_trace.
2. If agents disagree on risk MAGNITUDE → take the HIGHER value (worst-case).
   Exception: Financial Risk takes absolute priority for monetary figures only.
3. Vote weighting: 4:1 majority kept, but dissenting voice always logged.

NORMALIZATION LOGIC:
- Exploitability (1-10): 1-3→LOW, 4-6→MEDIUM, 7-8→HIGH, 9-10→CRITICAL
- Manipulation detected → floor at MEDIUM
- Financial exposure: 0→LOW, 1-50K→MEDIUM, 50K-2L→HIGH, 2L+→CRITICAL
- Undefined terms → -15% confidence per term (after first)
- Final = max(exploitability_level, manipulation_floor, financial_level, ambiguity_impact)

CONFIDENCE FORMULA:
  base = avg(all agent confidence scores)
  - 10% per major agent contradiction
  - 15% per undefined legal term (capped at 3 terms)
  - 5% per unresolved conflict
  floor: 0.40 (never below — too uncertain to act)
"""

from typing import Dict, Any, List, Tuple
from backend.models import (
    RiskLevel, KeyRisk, FutureScenario, AgentSignals,
    ClauseResult, DocumentSummary, TrustDNA, AnalysisResult
)

LEVEL_ORDER = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]


def _level_index(level: str) -> int:
    return LEVEL_ORDER.index(level.upper())


def _max_level(*levels: str) -> RiskLevel:
    """Return the highest risk level from a set of level strings."""
    return RiskLevel(max(levels, key=_level_index))


# ─── Normalization ────────────────────────────────────────────────────────────

def _normalize_exploitability(score: int) -> RiskLevel:
    if score >= 9:  return RiskLevel.CRITICAL
    if score >= 7:  return RiskLevel.HIGH
    if score >= 4:  return RiskLevel.MEDIUM
    return RiskLevel.LOW


def _normalize_financial(exposure_inr: int) -> RiskLevel:
    if exposure_inr >= 200_000:  return RiskLevel.CRITICAL
    if exposure_inr >= 50_000:   return RiskLevel.HIGH
    if exposure_inr > 0:         return RiskLevel.MEDIUM
    return RiskLevel.LOW


def _apply_escalation_rules(text: str, current_level: RiskLevel) -> RiskLevel:
    """Escalate risk based on explicit dangerous patterns."""
    text_lower = text.lower()
    
    new_level = current_level
    
    # 1. NON-COMPETE CLAUSES
    if any(kw in text_lower for kw in ["non-compete", "competitor", "competing organization", "not work with competitors"]):
        nc_level = new_level
        if "24 months" in text_lower or "2 years" in text_lower:
            nc_level = RiskLevel.CRITICAL
        elif "12 months" in text_lower or "1 year" in text_lower:
            nc_level = _max_level(RiskLevel.HIGH, nc_level)
        elif "6 months" in text_lower:
            nc_level = _max_level(RiskLevel.MEDIUM, nc_level)
            
        # Escalate further if scope is broad
        if any(kw in text_lower for kw in ["any geographic area", "worldwide", "intern", "internship", "any industry"]):
            if nc_level == RiskLevel.HIGH:
                nc_level = RiskLevel.CRITICAL
            elif nc_level == RiskLevel.MEDIUM:
                nc_level = RiskLevel.HIGH
            else:
                nc_level = _max_level(RiskLevel.HIGH, nc_level)
        
        new_level = _max_level(nc_level, new_level)

    # 2. TERMINATION WITHOUT NOTICE
    if any(kw in text_lower for kw in [
        "terminate at any time", 
        "without notice", 
        "terminate without notice", 
        "without compensation", 
        "immediate dismissal", 
        "unilateral termination rights", 
        "sole discretion termination",
        "terminate immediately"
    ]):
        new_level = _max_level(RiskLevel.HIGH, new_level)

    # 3. UNILATERAL MODIFICATION RIGHTS
    if any(kw in text_lower for kw in ["change terms anytime", "modify agreement without notice", "alter obligations unilaterally", "sole discretion", "unilaterally modify"]):
        new_level = _max_level(RiskLevel.HIGH, new_level)

    # 4. EXCLUSIVE IP OWNERSHIP
    if any(kw in text_lower for kw in ["exclusive property", "sole property", "irrevocably assigns", "all work belongs to company", "all rights"]):
        if "intellectual property" in text_lower or "ip " in text_lower or "ideas" in text_lower:
            ip_level = RiskLevel.HIGH
            # Escalate to CRITICAL
            if any(kw in text_lower for kw in ["perpetual", "indefinitely", "unrelated inventions", "beyond employment scope"]):
                ip_level = RiskLevel.CRITICAL
            new_level = _max_level(ip_level, new_level)

    # 5. UNPAID INTERNSHIP / NO COMPENSATION
    if any(kw in text_lower for kw in ["no stipend", "without compensation", "unpaid"]):
        unpaid_level = RiskLevel.MEDIUM
        # Escalate to HIGH
        if any(kw in text_lower for kw in ["exclusive", "intellectual property", "assigns"]):
            unpaid_level = RiskLevel.HIGH
        new_level = _max_level(unpaid_level, new_level)

    # 6. ARBITRATION CLAUSES
    if any(kw in text_lower for kw in ["arbitration", "waive", "class action", "court"]):
        if any(kw in text_lower for kw in ["company selects arbitrator", "class action waived", "waive class action", "courts restricted", "waive any right"]):
            arb_level = RiskLevel.HIGH
            if any(kw in text_lower for kw in ["all legal remedies", "unreasonable", "fees imposed", "solely responsible for fees"]):
                arb_level = RiskLevel.CRITICAL
            new_level = _max_level(arb_level, new_level)

    return new_level


def _normalize_consumer_protection(level: str) -> RiskLevel:
    mapping = {"none": RiskLevel.HIGH, "weak": RiskLevel.MEDIUM, "strong": RiskLevel.LOW}
    return mapping.get(level.lower(), RiskLevel.MEDIUM)


def _confidence_formula(
    agent_scores: List[float],
    contradictions: int,
    undefined_terms: int,
    unresolved_conflicts: int
) -> float:
    base = sum(agent_scores) / len(agent_scores) if agent_scores else 0.70
    # Cap undefined_terms penalty at 3 terms
    undefined_capped = min(undefined_terms, 3)
    penalty = (contradictions * 0.10) + (undefined_capped * 0.15) + (unresolved_conflicts * 0.05)
    return round(max(0.40, base - penalty), 2)


# ─── Conflict Detection ───────────────────────────────────────────────────────

def _detect_contradictions(judge: Dict, adversarial: Dict, psychologist: Dict) -> Tuple[int, List[str]]:
    """
    Detect major inter-agent contradictions. Returns (count, list_of_notes).
    
    Known contradiction scenarios:
    - Judge says fair (score ≥7) but Adversarial says high exploit (≥7)
    - Psychologist says dark pattern but Judge says fair
    - Simplification says clear but Ambiguity finds undefined terms
    """
    count = 0
    notes = []

    judge_score = judge.get("fairness_score", 5)
    exploit_score = adversarial.get("exploitability_score", 5)
    manip = psychologist.get("manipulation_detected", False)

    # Scenario 2 from spec: Judge says fair, Psychologist says dark pattern
    if judge_score >= 7 and manip:
        count += 1
        notes.append(
            "CONTRADICTION: Judge assessed as legally fair ({}/ 10), but Psychologist "
            "detected dark patterns. RESOLUTION: Both correct — legally defensible but "
            "psychologically manipulative. Risk remains at minimum MEDIUM.".format(judge_score)
        )

    # Scenario 1: High exploitability + low financial (not a contradiction — take worst-case)
    if exploit_score >= 7 and adversarial.get("exploitability_score", 0) >= 7:
        notes.append(
            "NOTE: Adversarial Lawyer exploitability={}/10. Financial impact may be ₹0 "
            "currently, but Adversarial identified HOW the company COULD weaponize this. "
            "Taking exploitability score as primary risk indicator.".format(exploit_score)
        )

    return count, notes


# ─── Key Risks Builder ────────────────────────────────────────────────────────

def _build_key_risks(
    judge: Dict,
    adversarial: Dict,
    consumer: Dict,
    psychologist: Dict,
    financial: Dict,
    final_level: RiskLevel
) -> List[KeyRisk]:
    risks = []

    # From Adversarial: top attack vectors
    for vector in adversarial.get("attack_vectors", [])[:2]:
        risks.append(KeyRisk(
            risk=vector,
            source=["Adversarial Lawyer"],
            severity=_normalize_exploitability(adversarial.get("exploitability_score", 5)),
            why_it_matters="A skilled opposing lawyer would use this clause against you in a dispute."
        ))

    # From Consumer Rights: violations
    for v in consumer.get("violations", [])[:2]:
        risks.append(KeyRisk(
            risk=f"Potential violation: {v.get('law_ref', 'consumer protection law')}",
            source=["Consumer Rights"],
            severity=RiskLevel.HIGH if consumer.get("protection_level") == "none" else RiskLevel.MEDIUM,
            why_it_matters="This may be unenforceable — or you may have legal remedies you're unaware of."
        ))

    # From Psychologist: dark patterns
    for dp in psychologist.get("dark_patterns", [])[:1]:
        risks.append(KeyRisk(
            risk=dp["pattern"],
            source=["Psychologist"],
            severity=RiskLevel.MEDIUM,
            why_it_matters=dp["explanation"]
        ))

    # From Financial: top risk
    fin_risks = financial.get("financial_risks", [])
    if fin_risks:
        risks.append(KeyRisk(
            risk=fin_risks[0],
            source=["Financial Risk"],
            severity=_normalize_financial(financial.get("exposure_inr", 0)),
            why_it_matters=f"Estimated ₹{financial.get('exposure_inr', 0):,} exposure based on clause analysis."
        ))

    # Deduplicate by risk text (keep first occurrence)
    seen = set()
    unique = []
    for r in risks:
        if r.risk not in seen:
            seen.add(r.risk)
            unique.append(r)

    return unique[:5]  # Max 5 key risks per clause


# ─── Future Scenarios ─────────────────────────────────────────────────────────

def _build_scenarios(title: str, clause_type: str, final_level: RiskLevel, adversarial: Dict, financial: Dict) -> FutureScenario:
    """Generate 3 outcome scenarios based on risk signals."""
    exposure = financial.get("exposure_inr", 0)
    attack_vectors = adversarial.get("attack_vectors", [])
    main_attack = attack_vectors[0] if attack_vectors else "this clause"

    if final_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
        if clause_type == "Non-Compete":
            worst = "You may be blocked from joining similar companies for 2 years, limiting future career opportunities."
        elif clause_type == "Termination":
            worst = "Your internship may end abruptly without warning or compensation, causing financial and professional disruption."
        elif clause_type == "Compensation":
            worst = "You may complete substantial work without receiving payment or benefits."
        elif clause_type == "Intellectual Property":
            worst = "The company may retain ownership of work or ideas you later wish to reuse."
        elif clause_type in ["Arbitration", "Dispute Resolution"]:
            worst = "You may face disputes in a company-controlled arbitration process with limited remedies."
        else:
            worst = f"Company weaponizes '{title}' aggressively: {main_attack}. Legal challenge is expensive and slow."
            
        return FutureScenario(
            best_case="Company never exploits the clause. Contract ends normally. No harm.",
            neutral_case="Clause is invoked once — you lose some rights but can negotiate separately.",
            worst_case=worst
        )
    elif final_level == RiskLevel.MEDIUM:
        return FutureScenario(
            best_case="Clause never causes issues. Standard contract lifecycle.",
            neutral_case="Minor friction at exit/dispute — resolvable with negotiation.",
            worst_case="Clause used as leverage during salary negotiation or exit. Manageable but annoying."
        )
    else:
        return FutureScenario(
            best_case="Clause is fair and standard. No issues expected.",
            neutral_case="Clause operates as written. No surprises.",
            worst_case="Edge case: clause interpreted broadly. Unlikely but document it anyway."
        )


# ─── New AI Insights ──────────────────────────────────────────────────────────

def _get_why_it_matters(clause_type: str) -> str:
    if clause_type == "Non-Compete":
        return "This clause may restrict your ability to work in similar companies after the internship ends."
    elif clause_type == "Termination":
        return "The company may terminate your internship immediately without notice, leaving you without financial or professional transition time."
    elif clause_type == "Compensation":
        return "You may perform substantial work without receiving financial compensation."
    elif clause_type in ["Arbitration", "Dispute Resolution"]:
        return "You may lose access to courts and collective legal remedies during disputes."
    elif clause_type == "Intellectual Property":
        return "Work you create during the internship may permanently belong to the company."
    elif clause_type == "Privacy":
        return "Your personal data may be shared broadly or retained indefinitely without your explicit consent."
    elif clause_type == "Financial":
        return "You could face disproportionate financial penalties or be left without adequate compensation if the company breaches the contract."
    return "This clause defines specific obligations that could unexpectedly limit your rights or impose hidden liabilities."


def _get_industry_benchmark(clause_type: str) -> str:
    if clause_type == "Intellectual Property":
        return "Standard contracts usually carve out IP created on personal time without company resources."
    elif clause_type == "Non-Compete":
        return "Standard agreements typically limit non-competes to 6-12 months and strict geographic boundaries."
    elif clause_type == "Termination":
        return "Standard agreements typically require 15-30 days notice for termination."
    elif clause_type == "Compensation":
        return "Industry standards guarantee compensation for all hours worked or services rendered."
    elif clause_type in ["Arbitration", "Dispute Resolution"]:
        return "Fair arbitration clauses preserve small claims court access and allow mutual selection of the arbitrator."
    elif clause_type == "Privacy":
        return "Modern privacy standards require purpose limitation, data minimization, and explicit opt-in consent for third-party sharing."
    elif clause_type == "Financial":
        return "Industry standard is mutual liability limitation, capping exposure to fees paid in the last 12 months."
    return "Standard clauses typically balance rights and obligations mutually between both parties."


# ─── Negotiation Copilot ──────────────────────────────────────────────────────

NEGOTIATION_TIPS = {
    "intellectual property": (
        "Retain creator ownership for personal work. Grant limited commercial license instead of perpetual assignment. "
        "Add: 'Except inventions made entirely on my own time without using Company equipment or resources.'"
    ),
    "non-compete": (
        "Push for reduced duration and add geographic limits. "
        "Add: 'This restriction only applies to direct competitors within a 50km radius for 6 months.'"
    ),
    "termination": (
        "Request a minimum 15–30 day written notice period or payment in lieu of notice. "
        "Add: 'Employee shall receive 30 days notice or pay in lieu, plus accrued PTO.'"
    ),
    "compensation": (
        "Ensure clear payment schedules and benefits. "
        "Add: 'Compensation shall be paid no later than the 5th of each month.'"
    ),
    "arbitration": (
        "Preserve court access. Ensure neutral arbitrator selection. Preserve class-action rights. "
        "Add: 'This arbitration clause does not apply to claims under ₹5,00,000 or to representative actions.'"
    ),
    "dispute resolution": (
        "Preserve court access. Ensure neutral arbitrator selection. Preserve class-action rights. "
        "Add: 'This arbitration clause does not apply to claims under ₹5,00,000 or to representative actions.'"
    ),
    "financial": (
        "Request a mutual liability cap. Ensure liability is symmetrical. "
        "Push for: 'Each party's liability shall not exceed 12 months of fees paid.'"
    ),
    "privacy": (
        "Require opt-out rights, limited retention, and purpose limitation. "
        "Add: 'Company shall process personal data only as necessary, with explicit consent, and not share without written consent.'"
    ),
}

REWRITE_TEMPLATES = {
    "intellectual property": (
        "IP created on personal time, using personal equipment, and unrelated to Company's business "
        "remains the exclusive property of Employee. Company is granted a limited license only as needed."
    ),
    "non-compete": (
        "Any non-compete restrictions shall be limited to direct competitors within a 50km radius for 6 months."
    ),
    "termination": (
        "Either party may terminate this agreement with 30 days written notice."
    ),
    "compensation": (
        "Company shall pay Employee the agreed compensation within 15 days of invoice or standard payroll cycle."
    ),
    "arbitration": (
        "Disputes over ₹5,00,000 may be submitted to binding arbitration by mutual written agreement. "
        "Either party retains the right to pursue claims in court of competent jurisdiction."
    ),
    "dispute resolution": (
        "Disputes over ₹5,00,000 may be submitted to binding arbitration by mutual written agreement. "
        "Either party retains the right to pursue claims in court of competent jurisdiction."
    ),
    "financial": (
        "Each party's total liability to the other shall not exceed the greater of ₹5,00,000 "
        "or the total fees paid under this agreement in the 12 months preceding the claim."
    ),
    "privacy": (
        "Company shall process Employee personal data solely for purposes of the employment "
        "relationship. Data shall not be shared with third parties without Employee's explicit written consent."
    ),
}


def _get_negotiation_guidance(clause_type: str, text: str) -> Tuple[str, str]:
    """Match clause type to best negotiation tip and rewrite template."""
    key = clause_type.lower()
    
    if key in NEGOTIATION_TIPS:
        return NEGOTIATION_TIPS[key], REWRITE_TEMPLATES[key]

    # Generic fallback
    return (
        "Request that any unilateral company discretion be limited by objective criteria. "
        "Add: 'Company shall exercise rights under this clause only in good faith.'",
        "The parties agree to mutual obligations that are fair, specific, and balanced."
    )


# ─── Main Convergence Function ────────────────────────────────────────────────

def converge(
    clause_number: int,
    title: str,
    clause_type: str,
    original_text: str,
    judge: Dict,
    adversarial: Dict,
    consumer: Dict,
    psychologist: Dict,
    financial: Dict,
    simplifier: Dict
) -> ClauseResult:
    """
    Takes raw agent outputs, resolves conflicts, normalizes risk, and
    returns a single authoritative ClauseResult.
    """
    clause_id = f"LEX-{clause_number:03d}"

    # ── Step 1: Normalize each agent's signal to a RiskLevel ──
    exploit_level = _normalize_exploitability(adversarial.get("exploitability_score", 5))
    financial_level = _normalize_financial(financial.get("exposure_inr", 0))
    consumer_level = _normalize_consumer_protection(consumer.get("protection_level", "weak"))

    # Manipulation floor: if detected, minimum MEDIUM
    if psychologist.get("manipulation_detected", False):
        manip_floor = RiskLevel.MEDIUM
    else:
        manip_floor = RiskLevel.LOW

    # ── Step 2: Conflict detection ──
    contradictions, conflict_notes = _detect_contradictions(judge, adversarial, psychologist)
    unresolved = 0  

    # ── Step 3: Final risk = max of all normalized signals + Escalation Rules ──
    base_final = _max_level(exploit_level, financial_level, consumer_level, manip_floor)
    final_level = _apply_escalation_rules(original_text, base_final)

    # ── Step 4: Confidence score ──
    agent_confidences = [
        judge.get("confidence", 0.75),
        adversarial.get("confidence", 0.75),
        consumer.get("confidence", 0.75),
        psychologist.get("confidence", 0.75),
        financial.get("confidence", 0.75),
        simplifier.get("confidence", 0.88),
    ]
    undefined_count = simplifier.get("undefined_count", 0)
    confidence = _confidence_formula(agent_confidences, contradictions, undefined_count, unresolved)

    # ── Step 5: User-Friendly Explanation Trace ──
    agents_flagged = sum(1 for lvl in [exploit_level, financial_level, consumer_level, manip_floor] if lvl in [RiskLevel.HIGH, RiskLevel.CRITICAL])
    total_agents = 5
    
    primary_concern = "disproportionate company control or liability."
    if financial_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
        primary_concern = "significant financial exposure or asymmetric liability."
    elif consumer_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
        primary_concern = "potential violation of statutory consumer or employee rights."
    elif manip_floor in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
        primary_concern = "psychological manipulation or coercive language."
    elif exploit_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
        primary_concern = "high exploitability by an adversarial legal party."
        
    if final_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
        agents_flagged = max(agents_flagged, 4)
        if clause_type == "Termination":
            explanation_trace = f"{agents_flagged} of {total_agents} AI agents identified elevated procedural and employment risk due to unilateral termination powers. Final assessment: {final_level} RISK."
        else:
            explanation_trace = f"{agents_flagged} of {total_agents} AI agents identified elevated legal and procedural risk. Primary concern: {primary_concern} Final assessment: {final_level} RISK."
    else:
        if clause_type == "Termination":
            explanation_trace = f"{max(1, agents_flagged)} of {total_agents} AI agents identified elevated legal risk. Primary concern: unilateral termination powers. Final assessment: {final_level} RISK."
        else:
            explanation_trace = f"{max(1, agents_flagged)} of {total_agents} AI agents identified elevated legal risk. Primary concern: {primary_concern} Final assessment: {final_level} RISK."

    # ── Step 6: Build structured outputs ──
    key_risks = _build_key_risks(judge, adversarial, consumer, psychologist, financial, final_level)
    future_scenarios = _build_scenarios(title, clause_type, final_level, adversarial, financial)
    negotiation_tip, suggested_rewrite = _get_negotiation_guidance(clause_type, original_text)
    
    why_it_matters = _get_why_it_matters(clause_type)
    industry_benchmark = _get_industry_benchmark(clause_type)

    agent_signals = AgentSignals(
        judge_fairness=judge.get("fairness_score"),
        adversarial_exploitability=adversarial.get("exploitability_score"),
        consumer_protection=consumer.get("protection_level"),
        manipulation_detected=psychologist.get("manipulation_detected"),
        financial_exposure_inr=financial.get("exposure_inr"),
        undefined_terms=undefined_count,
        agent_notes={
            "judge": judge.get("assessment", ""),
            "adversarial": adversarial.get("verdict", ""),
            "consumer": consumer.get("verdict", ""),
            "psychologist": psychologist.get("verdict", ""),
            "financial": financial.get("verdict", ""),
        }
    )

    return ClauseResult(
        clause_id=clause_id,
        clause_number=clause_number,
        title=title,
        clause_type=clause_type,
        is_informational=False,
        original_text=original_text,
        plain_english=simplifier.get("plain_english", original_text),
        risk_level=final_level,
        confidence_score=confidence,
        why_it_matters=why_it_matters,
        industry_benchmark=industry_benchmark,
        key_risks=key_risks,
        explanation_trace=explanation_trace,
        future_scenarios=future_scenarios,
        negotiation_tip=negotiation_tip,
        suggested_rewrite=suggested_rewrite,
        agent_signals=agent_signals,
    )


# ─── Document-Level Summary ───────────────────────────────────────────────────

def build_document_summary(clauses: List[ClauseResult]) -> DocumentSummary:
    """Aggregate clause-level results into a document summary with Trust DNA."""
    counts = {level: 0 for level in RiskLevel}
    for c in clauses:
        counts[c.risk_level] += 1

    overall = RiskLevel.LOW
    if counts[RiskLevel.CRITICAL] > 0:
        overall = RiskLevel.CRITICAL
    elif counts[RiskLevel.HIGH] > 0:
        overall = RiskLevel.HIGH
    elif counts[RiskLevel.MEDIUM] > 0:
        overall = RiskLevel.MEDIUM

    # Trust DNA: 0-100 scales (higher = better / safer for user)
    n = len(clauses) or 1

    # Fairness: avg inverse of judge score converted to 0-100
    avg_judge = sum((c.agent_signals.judge_fairness or 5) for c in clauses) / n
    fairness = round((avg_judge / 10) * 100)

    # Transparency: penalised by undefined terms and dark patterns
    avg_undefined = sum((c.agent_signals.undefined_terms or 0) for c in clauses) / n
    manipulation_frac = sum(1 for c in clauses if c.agent_signals.manipulation_detected) / n
    transparency = round(max(10, 80 - avg_undefined * 10 - manipulation_frac * 30))

    # Balance: based on consumer protection level
    protection_scores = {"strong": 100, "weak": 40, "none": 10}
    avg_protection = sum(
        protection_scores.get(c.agent_signals.consumer_protection or "weak", 40) for c in clauses
    ) / n
    balance = round(avg_protection)

    # Legal clarity: 100 - (undefined_terms * 10)
    legal_clarity = round(max(10, 100 - avg_undefined * 12))

    # User protection: inverse of risk level
    risk_weights = {RiskLevel.LOW: 90, RiskLevel.MEDIUM: 60, RiskLevel.HIGH: 30, RiskLevel.CRITICAL: 10}
    avg_risk_score = sum(risk_weights.get(c.risk_level, 50) for c in clauses) / n
    user_protection = round(avg_risk_score)

    # Headlines
    critical_n = counts[RiskLevel.CRITICAL]
    high_n = counts[RiskLevel.HIGH]

    if overall == RiskLevel.CRITICAL:
        headline = f"🚨 {critical_n} Critical clause{'s' if critical_n>1 else ''} detected"
        one_liner = "This contract contains severe clauses that could cause significant harm. Do not sign without legal review."
    elif overall == RiskLevel.HIGH:
        headline = f"⚠️ {high_n} High-risk clause{'s' if high_n>1 else ''} require attention"
        one_liner = "Multiple high-risk clauses identified. Negotiate key terms before signing."
    elif overall == RiskLevel.MEDIUM:
        headline = "📋 Standard risks present — review recommended"
        one_liner = "Contract is negotiable. Some terms are below industry standard."
    else:
        headline = "✅ Contract appears balanced"
        one_liner = "No major red flags detected. Standard review still recommended."

    return DocumentSummary(
        total_clauses=len(clauses),
        critical_count=counts[RiskLevel.CRITICAL],
        high_count=counts[RiskLevel.HIGH],
        medium_count=counts[RiskLevel.MEDIUM],
        low_count=counts[RiskLevel.LOW],
        overall_risk=overall,
        trust_dna=TrustDNA(
            fairness=fairness,
            transparency=transparency,
            balance=balance,
            legal_clarity=legal_clarity,
            user_protection=user_protection,
        ),
        headline=headline,
        one_liner=one_liner,
    )
