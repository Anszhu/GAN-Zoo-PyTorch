from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from fastapi import FastAPI, HTTPException

from backend.models.schemas import (
    AnalysisRequest,
    AnalysisResponse,
    ReportRequest,
    ReportResponse,
)
from backend.services.analytics_service import load_dashboard_snapshot
from backend.services.evidence_logger import log_evidence, log_report
from backend.services.language_service import detect_language, normalize_text
from backend.services.ml_engine import run_ml_engine
from backend.services.rule_engine import run_rule_engine
from backend.services.scoring_engine import fuse_scores


app = FastAPI(
    title="DetectNet API",
    version="1.0.0",
    description="Hybrid rule-based and BERT-inspired multilingual cyberbullying detection API.",
)


def analyze_payload(request: AnalysisRequest) -> AnalysisResponse:
    if not request.consent:
        raise HTTPException(status_code=400, detail="User consent is required for analysis.")

    normalized_text = normalize_text(request.text)
    language = detect_language(request.text)
    rule_result = run_rule_engine(request.text, language)
    ml_result = run_ml_engine(normalized_text, language)
    fused = fuse_scores(rule_result.score, ml_result.score)

    evidence = log_evidence(
        {
            "text": request.text,
            "language": language,
            "rule_score": rule_result.score,
            "ml_score": ml_result.score,
            "final_score": fused.final_score,
            "severity": fused.severity,
        },
        source=request.source,
        consent=request.consent,
    )

    recommendations = [
        "Send high-risk cases for human review before final enforcement.",
        "Store only hashed evidence and minimal metadata for privacy-aware auditing.",
        "Use the API report endpoint to simulate cybercrime escalation for critical cases.",
    ]
    if fused.severity in {"high", "critical"}:
        recommendations.insert(0, "Flag this content for moderator attention and preserve evidence.")

    return AnalysisResponse(
        language=language,
        normalized_text=normalized_text,
        rule_engine=rule_result,
        ml_engine=ml_result,
        fused=fused,
        evidence=evidence,
        recommendations=recommendations,
        disclaimer=(
            "This student prototype supports moderation decisions and should not be used as the only basis for legal action."
        ),
    )


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "DetectNet API is running"}


@app.post("/analyze", response_model=AnalysisResponse)
def analyze(request: AnalysisRequest) -> AnalysisResponse:
    return analyze_payload(request)


@app.get("/dashboard")
def dashboard():
    return load_dashboard_snapshot()


@app.post("/mock-report", response_model=ReportResponse)
def mock_report(request: ReportRequest) -> ReportResponse:
    payload = request.model_dump()
    payload["report_id"] = f"DN-{uuid4().hex[:10].upper()}"
    payload["created_at"] = datetime.now(timezone.utc).isoformat()
    evidence = log_report(payload)

    return ReportResponse(
        report_id=payload["report_id"],
        created_at=datetime.fromisoformat(payload["created_at"]),
        payload_hash=evidence["payload_hash"],
        status="queued-for-review",
        export_ready={
            "format": "json",
            "integrity": "sha256-hash-attached",
            "note": "This mock payload is designed to simulate NGO/government portal integration.",
        },
    )
