"""
LEXGUARD — FastAPI Application
Serves the frontend + provides /analyze endpoint.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from backend.models import AnalyzeRequest, AnalysisResult
from backend.document_processor import extract_clauses, analyze_clause_metadata
from backend.agents import judge, adversarial, consumer_rights, psychologist, financial, simplifier
from backend.convergence import converge, build_document_summary

import concurrent.futures
import time

app = FastAPI(title="LEXGUARD", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Demo contract (risky employment agreement) ──────────────────────────────

DEMO_CONTRACT = """INTERNSHIP AGREEMENT

CLAUSE 1 — INTELLECTUAL PROPERTY ASSIGNMENT
All intellectual property, inventions, discoveries, ideas, concepts, designs, and works of authorship created by the Employee, whether or not during working hours, whether or not on Company premises, and whether or not using Company equipment, shall be the sole and exclusive property of the Company. Employee hereby irrevocably assigns all rights, title, and interest therein to the Company without additional compensation.

CLAUSE 2 — DATA COLLECTION AND SHARING
The Company may collect, process, and share Employee personal data with third parties including but not limited to affiliated entities, service providers, business partners, and government agencies, as deemed necessary by the Company in its sole discretion. Employee consents to such collection and waives any right to notification of subsequent data transfers.

CLAUSE 3 — TERMINATION WITHOUT CAUSE
The Company reserves the right to terminate this agreement at any time, with or without cause, with 24 hours written notice. Employee waives any right to severance pay, transition allowance, or compensation of any kind upon termination, regardless of tenure or performance record.

CLAUSE 4 — LIABILITY LIMITATION
Employee's total liability to the Company for any breach of this agreement shall not exceed the amount paid to Employee in the preceding 12 months. However, the Company's total liability to Employee shall be limited to ₹5,000 regardless of the nature, extent, or severity of the breach.

CLAUSE 5 — MANDATORY ARBITRATION
All disputes arising out of or relating to this agreement shall be resolved exclusively through binding arbitration administered by the Company-selected arbitrator in the Company-selected jurisdiction. Employee waives the right to jury trial, class action, and participation in any representative proceeding. Arbitration decisions shall be final and non-appealable.

CLAUSE 6 — POST-EMPLOYMENT NON-COMPETE
Employee agrees not to work for, consult with, or provide services to any competitor of the Company, anywhere in the world, for a period of 2 years following the termination of this agreement."""

DEMO_DOCUMENT_NAME = "TechCorp Employment Agreement (RISKY DEMO)"


def _run_all_agents(clause_number: int, title: str, text: str) -> dict:
    """Run all 6 agents on a single clause (parallel-ready)."""
    return {
        "judge":          judge.analyze(clause_number, title, text),
        "adversarial":    adversarial.analyze(clause_number, title, text),
        "consumer":       consumer_rights.analyze(clause_number, title, text),
        "psychologist":   psychologist.analyze(clause_number, title, text),
        "financial":      financial.analyze(clause_number, title, text),
        "simplifier":     simplifier.analyze(clause_number, title, text),
    }


def _analyze_text(text: str, document_name: str) -> AnalysisResult:
    """Core analysis pipeline."""
    clauses_raw = extract_clauses(text)
    if not clauses_raw:
        raise HTTPException(status_code=400, detail="Could not extract any clauses from the document.")

    clause_results = []

    # Pre-process metadata to skip informational clauses
    analyzed_clauses = []
    for num, title, body in clauses_raw:
        metadata = analyze_clause_metadata(title, body)
        analyzed_clauses.append((num, title, body, metadata))
        
    # Run agents on all substantive clauses in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        futures = {}
        for num, original_title, body, metadata in analyzed_clauses:
            if metadata["is_informational"]:
                continue
            futures[executor.submit(_run_all_agents, num, metadata["title"], body)] = (num, metadata, body)
            
        for future in concurrent.futures.as_completed(futures):
            num, metadata, body = futures[future]
            signals = future.result()
            result = converge(
                clause_number=num,
                title=metadata["title"],
                clause_type=metadata["clause_type"],
                original_text=body,
                judge=signals["judge"],
                adversarial=signals["adversarial"],
                consumer=signals["consumer"],
                psychologist=signals["psychologist"],
                financial=signals["financial"],
                simplifier=signals["simplifier"],
            )
            clause_results.append(result)
            
    # Add informational clauses manually
    for num, original_title, body, metadata in analyzed_clauses:
        if metadata["is_informational"]:
            from backend.models import ClauseResult, RiskLevel, FutureScenario, AgentSignals
            clause_results.append(ClauseResult(
                clause_id=f"LEX-{num:03d}",
                clause_number=num,
                title=metadata["title"],
                clause_type=metadata["clause_type"],
                is_informational=True,
                original_text=body,
                plain_english="This section is informational and imposes no substantive legal obligations.",
                risk_level=RiskLevel.INFORMATIONAL,
                confidence_score=1.0,
                why_it_matters="No direct legal risks. This text establishes context.",
                industry_benchmark="",
                key_risks=[],
                explanation_trace="Skipped agent analysis (Informational).",
                future_scenarios=FutureScenario(best_case="", neutral_case="", worst_case=""),
                negotiation_tip="No negotiation necessary.",
                suggested_rewrite="",
                agent_signals=AgentSignals()
            ))

    # Sort by clause number
    clause_results.sort(key=lambda c: c.clause_number)

    summary = build_document_summary(clause_results)
    return AnalysisResult(document_summary=summary, clauses=clause_results)


# ── Routes ──────────────────────────────────────────────────────────────────

@app.post("/analyze", response_model=AnalysisResult)
async def analyze_contract(request: AnalyzeRequest):
    """Analyze a contract text through the full LEXGUARD pipeline."""
    if not request.text or len(request.text.strip()) < 50:
        raise HTTPException(status_code=400, detail="Contract text too short. Please provide at least 50 characters.")
    if len(request.text) > 100_000:
        raise HTTPException(status_code=400, detail="Contract text too long. Maximum 100,000 characters.")
    return _analyze_text(request.text, request.document_name or "Untitled Contract")


@app.get("/demo")
async def demo_analysis():
    """Return analysis of the built-in demo contract."""
    return _analyze_text(DEMO_CONTRACT, DEMO_DOCUMENT_NAME)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "LEXGUARD", "version": "1.0.0"}


# ── Static frontend ──────────────────────────────────────────────────────────

FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend", "dist")

if os.path.exists(FRONTEND_DIR):
    app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIR, "assets")), name="assets")

    @app.get("/")
    async def root():
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))
else:
    @app.get("/")
    async def root():
        return {"message": "LEXGUARD API is running. Frontend build (dist) not found. Run 'npm run build' in the frontend directory."}
