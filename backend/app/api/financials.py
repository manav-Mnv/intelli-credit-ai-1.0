from fastapi import APIRouter, HTTPException
from app.database import fetch_record
from app.services.financial_analyzer import analyzer

router = APIRouter()


@router.get("/{company_id}")
async def get_financials(company_id: str):
    """Get financial data and computed ratios for a company."""
    records = await fetch_record("financials", {"company_id": company_id})
    if not records:
        raise HTTPException(status_code=404, detail="No financial data found for this company")
    return records


@router.post("/analyze")
async def analyze_financials(data: dict):
    """
    Analyze raw financial figures and return computed ratios.
    Useful for direct analysis without document upload.
    """
    result = analyzer.analyze(data)
    return result
