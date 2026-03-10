from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
import uuid
import os
import shutil
import logging

from app.config import settings
from app.database import insert_record, fetch_record, update_record
from app.services.document_processor import processor

router = APIRouter()
logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {".pdf", ".xlsx", ".xls", ".docx", ".txt"}
MAX_SIZE = settings.MAX_FILE_SIZE_MB * 1024 * 1024  # bytes


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    company_id: str = Form(None),
    company_name: str = Form(None),
    industry: str = Form(None),
):
    """
    Upload a financial document for a company.
    If company_id is not provided, creates a new company using company_name.
    """
    # Validate extension
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type '{ext}' not supported. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # If no company_id, create company
    if not company_id:
        if not company_name:
            raise HTTPException(status_code=400, detail="Provide company_id or company_name")
        company_data = {
            "id": str(uuid.uuid4()),
            "company_name": company_name,
            "industry": industry or "Unknown",
        }
        company = await insert_record("companies", company_data) or company_data
        company_id = company["id"]

    # Save file to disk
    doc_id = str(uuid.uuid4())
    save_dir = os.path.join(settings.UPLOAD_DIR, company_id)
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, f"{doc_id}{ext}")

    contents = await file.read()
    if len(contents) > MAX_SIZE:
        raise HTTPException(status_code=413, detail=f"File too large (max {settings.MAX_FILE_SIZE_MB} MB)")

    with open(save_path, "wb") as f:
        f.write(contents)

    # Record in DB
    doc_record = {
        "id": doc_id,
        "company_id": company_id,
        "file_name": file.filename,
        "file_type": ext,
        "file_size_bytes": len(contents),
        "storage_path": save_path,
        "processing_status": "processing",
    }
    await insert_record("documents", doc_record)

    # Process document synchronously (in MVP; Celery handles this in production)
    try:
        result = processor.process_file(save_path)
        financial_data = result.get("financial_data", {})

        # Update document status
        await update_record("documents", doc_id, {
            "processing_status": "completed",
            "extracted_text": result.get("raw_text", "")[:4000],
            "page_count": result.get("page_count", 1),
        })

        # Embed document text into ChromaDB vector store
        raw_text = result.get("raw_text", "")
        if raw_text:
            try:
                from app.services.vector_store import vector_store
                vector_store.add_document(
                    doc_id=doc_id,
                    company_id=company_id,
                    text=raw_text,
                    metadata={"file_name": file.filename, "file_type": ext},
                )
            except Exception as ve:
                logger.warning(f"ChromaDB embedding failed (non-fatal): {ve}")

        # Save extracted financials if data found
        if financial_data:
            from app.services.financial_analyzer import analyzer
            analysis = analyzer.analyze(financial_data)
            
            # We must iterate over the nested 'ratios' dict, not the outer analysis response
            ratios_dict = analysis.get("ratios", {})
            ratios_db = {k: v for k, v in ratios_dict.items() if k not in ["dscr", "tol_tnw", "ebitda_margin", "gross_margin", "debt_to_assets"]}
            
            fin_record = {
                "id": str(uuid.uuid4()),
                "company_id": company_id,
                "document_id": doc_id,
                **financial_data,
                **ratios_db,
            }
            await insert_record("financials", fin_record)

        return {
            "success": True,
            "document_id": doc_id,
            "company_id": company_id,
            "file_name": file.filename,
            "processing_status": "completed",
            "financial_data_extracted": bool(financial_data),
            "financial_summary": financial_data,
            "page_count": result.get("page_count", 1),
        }

    except Exception as e:
        logger.error(f"Document processing failed: {e}")
        await update_record("documents", doc_id, {"processing_status": "failed", "error_message": str(e)})
        return {
            "success": True,
            "document_id": doc_id,
            "company_id": company_id,
            "file_name": file.filename,
            "processing_status": "failed",
            "error": str(e),
        }


@router.get("/company/{company_id}")
async def list_company_documents(company_id: str):
    """List all documents for a company."""
    records = await fetch_record("documents", {"company_id": company_id})
    return records
