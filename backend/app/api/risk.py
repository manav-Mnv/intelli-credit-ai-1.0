from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import uuid

from app.services.risk_engine import risk_engine
from app.database import insert_record, fetch_record

router = APIRouter()


class RiskAnalysisRequest(BaseModel):
    company_id: str
    company_text: Optional[str] = ""
    industry: Optional[str] = ""


@router.post("/analyze")
async def analyze_risk(request: RiskAnalysisRequest):
    """Run full three-layer risk analysis for a company."""
    # Fetch financials
    fin_records = await fetch_record("financials", {"company_id": request.company_id})
    financials = fin_records[0] if fin_records else {}

    result = risk_engine.analyze(
        financials=financials,
        company_text=request.company_text or "",
        industry=request.industry or "",
    )

    # Save to DB
    record = {
        "id": str(uuid.uuid4()),
        "company_id": request.company_id,
        "financial_score": result["component_scores"]["rule_based"],
        "ml_score": result["component_scores"]["ml_model"],
        "nlp_score": result["component_scores"]["nlp_text"],
        "research_score": result["component_scores"]["sector"],
        "overall_risk_score": result["overall_risk_score"],
        "risk_grade": result["risk_grade"],
        "default_probability": result["default_probability"],
        "risk_factors": result["risk_factors"],
    }
    await insert_record("risk_scores", record)

    return result


@router.get("/{company_id}")
async def get_risk_score(company_id: str):
    """Get latest risk score for a company."""
    records = await fetch_record("risk_scores", {"company_id": company_id})
    if not records:
        raise HTTPException(status_code=404, detail="No risk analysis found for this company")
    return records[-1]  # Return most recent
