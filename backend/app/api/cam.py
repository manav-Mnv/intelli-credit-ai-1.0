from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import uuid

from app.services.decision_engine import decision_engine
from app.services.cam_generator import cam_generator
from app.database import insert_record, fetch_record

router = APIRouter()


class CAMRequest(BaseModel):
    company_id: str
    requested_loan_amount: Optional[float] = None


@router.post("/generate")
async def generate_cam(request: CAMRequest):
    """Generate a full Credit Appraisal Memo for a company."""

    # Gather all data
    company_recs = await fetch_record("companies", {"id": request.company_id})
    if not company_recs:
        raise HTTPException(status_code=404, detail="Company not found")
    company = company_recs[0]

    fin_recs = await fetch_record("financials", {"company_id": request.company_id})
    financials = fin_recs[0] if fin_recs else {}

    risk_recs = await fetch_record("risk_scores", {"company_id": request.company_id})
    research_recs = await fetch_record("research_reports", {"company_id": request.company_id})

    risk_analysis = risk_recs[-1] if risk_recs else {}
    research_report = research_recs[-1] if research_recs else {}

    # If no risk analysis yet, run it now
    if not risk_analysis:
        from app.services.risk_engine import risk_engine
        risk_analysis = risk_engine.analyze(
            financials=financials,
            industry=company.get("industry", ""),
        )

    # Generate decision
    decision = decision_engine.decide(
        company_name=company.get("company_name", ""),
        financials=financials,
        risk_analysis=risk_analysis,
        research_report=research_report,
        requested_loan_amount=request.requested_loan_amount,
    )

    # Generate CAM
    ratios = {k: financials.get(k) for k in [
        "profit_margin", "debt_equity_ratio", "current_ratio",
        "interest_coverage", "roe", "roce", "ebitda_margin", "revenue_growth"
    ]}
    cam = cam_generator.generate(
        company=company,
        financials=financials,
        ratios=ratios,
        risk_analysis=risk_analysis,
        research_report=research_report,
        decision=decision,
    )

    # Save to DB
    cam_record = {
        "id": str(uuid.uuid4()),
        "company_id": request.company_id,
        **{k: cam[k] for k in [
            "executive_summary", "company_overview", "financial_analysis",
            "risk_assessment", "industry_outlook", "loan_recommendation",
            "decision", "risk_score", "recommended_loan_amount",
            "interest_rate", "loan_tenor_months",
        ]},
        "conditions": str(cam.get("conditions", [])),
    }
    result = await insert_record("cam_reports", cam_record)

    return {
        **cam,
        "cam_id": cam_record["id"],
        "company": company,
        "decision_details": decision,
    }


@router.get("/{company_id}")
async def get_cam(company_id: str):
    """Get the latest CAM report for a company."""
    records = await fetch_record("cam_reports", {"company_id": company_id})
    if not records:
        raise HTTPException(status_code=404, detail="No CAM report found. Please generate one first.")
    return records[-1]


@router.get("/full/{company_id}")
async def get_full_analysis(company_id: str):
    """Get full analysis including financials, risk, research, and CAM."""
    company = (await fetch_record("companies", {"id": company_id}) or [{}])[0]
    financials = (await fetch_record("financials", {"company_id": company_id}) or [{}])[0]
    risk = (await fetch_record("risk_scores", {"company_id": company_id}) or [{}])
    research = (await fetch_record("research_reports", {"company_id": company_id}) or [{}])
    cam = (await fetch_record("cam_reports", {"company_id": company_id}) or [{}])

    return {
        "company": company,
        "financials": financials,
        "risk_scores": risk,
        "research_reports": research,
        "cam_reports": cam,
    }
