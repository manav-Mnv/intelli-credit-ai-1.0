from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import uuid

from app.agents.news_agent import news_agent
from app.agents.litigation_agent import litigation_agent
from app.agents.industry_agent import industry_agent
from app.database import insert_record, fetch_record

router = APIRouter()


class ResearchRequest(BaseModel):
    company_id: str
    company_name: str
    industry: Optional[str] = ""


@router.post("/run")
async def run_research(request: ResearchRequest):
    """Run all research agents for a company."""

    # Run all three agents
    news_result = news_agent.research(request.company_name)
    litigation_result = litigation_agent.research(request.company_name)
    industry_result = industry_agent.research(request.industry or "", request.company_name)

    # Compute overall sentiment from risk levels
    levels = {
        "Low": 0.3,
        "Medium": 0.6,
        "High": 0.9,
    }
    avg_sentiment = -(
        levels.get(news_result["news_risk_level"], 0.5)
        + levels.get(litigation_result["litigation_risk_level"], 0.5)
        + levels.get(industry_result["industry_risk_level"], 0.5)
    ) / 3.0

    record = {
        "id": str(uuid.uuid4()),
        "company_id": request.company_id,
        "news_summary": news_result["news_summary"],
        "news_risk_level": news_result["news_risk_level"],
        "news_articles": news_result["news_articles"],
        "litigation_summary": litigation_result["litigation_summary"],
        "litigation_risk_level": litigation_result["litigation_risk_level"],
        "litigation_cases": litigation_result["litigation_cases"],
        "industry_summary": industry_result["industry_summary"],
        "industry_risk_level": industry_result["industry_risk_level"],
        "industry_trends": industry_result.get("industry_trends", []),
        "overall_sentiment": avg_sentiment,
    }
    await insert_record("research_reports", record)

    return {
        "news": news_result,
        "litigation": litigation_result,
        "industry": industry_result,
        "overall_sentiment": avg_sentiment,
    }


@router.get("/{company_id}")
async def get_research(company_id: str):
    """Get latest research report for a company."""
    records = await fetch_record("research_reports", {"company_id": company_id})
    if not records:
        raise HTTPException(status_code=404, detail="No research report found for this company")
    return records[-1]
