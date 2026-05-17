from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum


class RiskLevel(str, Enum):
    INFORMATIONAL = "INFORMATIONAL"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class KeyRisk(BaseModel):
    risk: str
    source: List[str]
    severity: RiskLevel
    why_it_matters: str


class FutureScenario(BaseModel):
    best_case: str
    neutral_case: str
    worst_case: str


class AgentSignals(BaseModel):
    judge_fairness: Optional[int] = None          # 1-10
    adversarial_exploitability: Optional[int] = None  # 1-10
    consumer_protection: Optional[str] = None     # "strong" / "weak" / "none"
    manipulation_detected: Optional[bool] = None
    financial_exposure_inr: Optional[int] = None  # rupees
    undefined_terms: Optional[int] = None
    agent_notes: Optional[Dict[str, str]] = None


class ClauseResult(BaseModel):
    clause_id: str
    clause_number: int
    title: str
    clause_type: str = "General"
    is_informational: bool = False
    original_text: str
    plain_english: str
    risk_level: RiskLevel
    confidence_score: float = Field(ge=0.0, le=1.0)
    why_it_matters: str = ""
    industry_benchmark: str = ""
    key_risks: List[KeyRisk]
    explanation_trace: str
    future_scenarios: FutureScenario
    negotiation_tip: str
    suggested_rewrite: str
    agent_signals: AgentSignals


class TrustDNA(BaseModel):
    fairness: int = Field(ge=0, le=100)
    transparency: int = Field(ge=0, le=100)
    balance: int = Field(ge=0, le=100)
    legal_clarity: int = Field(ge=0, le=100)
    user_protection: int = Field(ge=0, le=100)


class DocumentSummary(BaseModel):
    total_clauses: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    overall_risk: RiskLevel
    trust_dna: TrustDNA
    headline: str
    one_liner: str


class AnalysisResult(BaseModel):
    document_summary: DocumentSummary
    clauses: List[ClauseResult]


class AnalyzeRequest(BaseModel):
    text: str
    document_name: Optional[str] = "Untitled Contract"
