from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.agents.graph_agent import graph_agent

router = APIRouter()


class AddDirectorRequest(BaseModel):
    company_name: str
    director_name: str
    role: Optional[str] = "Director"
    company_industry: Optional[str] = ""


class RiskCheckRequest(BaseModel):
    company_name: str


@router.post("/add-director")
async def add_director(req: AddDirectorRequest):
    """Add a director-company relationship to the graph."""
    graph_agent.add_company(req.company_name, req.company_industry or "")
    graph_agent.add_director(req.director_name, req.company_name, req.role or "Director")
    return {"success": True, "message": f"Added {req.director_name} → {req.company_name}"}


@router.post("/risk-check")
async def check_graph_risk(req: RiskCheckRequest):
    """Check cross-default risk via Neo4j director graph."""
    result = graph_agent.detect_cross_default_risk(req.company_name)
    return result


@router.get("/related/{company_name}")
async def get_related_companies(company_name: str):
    """Get companies connected through shared directors."""
    related = graph_agent.find_related_companies(company_name)
    return {"company": company_name, "related_companies": related}


@router.get("/status")
async def graph_status():
    """Check Neo4j connection status."""
    return {
        "neo4j_available": graph_agent._available,
        "message": "Connected" if graph_agent._available else "Neo4j not running. Start with: docker run -d -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j"
    }
