from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import uuid

from app.database import insert_record, fetch_record

router = APIRouter()


class CompanyCreate(BaseModel):
    company_name: str
    industry: Optional[str] = None
    registration_number: Optional[str] = None
    cin: Optional[str] = None
    pan: Optional[str] = None
    address: Optional[str] = None
    website: Optional[str] = None
    contact_email: Optional[str] = None


class CompanyResponse(BaseModel):
    id: str
    company_name: str
    industry: Optional[str]
    registration_number: Optional[str]
    created_at: Optional[str]


@router.post("/", response_model=dict)
async def create_company(company: CompanyCreate):
    """Create a new company record."""
    data = {
        "id": str(uuid.uuid4()),
        **company.model_dump(exclude_none=True),
    }
    result = await insert_record("companies", data)
    if not result:
        raise HTTPException(status_code=500, detail="Failed to create company")
    return result


@router.get("/{company_id}", response_model=dict)
async def get_company(company_id: str):
    """Get company details by ID."""
    records = await fetch_record("companies", {"id": company_id})
    if not records:
        raise HTTPException(status_code=404, detail="Company not found")
    return records[0]


@router.get("/", response_model=list)
async def list_companies():
    """List all companies."""
    from app.database import get_supabase
    client = get_supabase()
    if not client:
        return []
    try:
        result = client.table("companies").select("*").order("created_at", desc=True).execute()
        return result.data or []
    except Exception:
        return []
