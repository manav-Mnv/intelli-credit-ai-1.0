"""
Document Celery Task
Dedicated async task for heavy document processing — OCR, embedding, chunking.
"""
import logging
from app.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="process_document")
def process_document_task(self, document_id: str, file_path: str, company_id: str):
    """
    Async document processing task:
    1. Extract text from PDF/Excel
    2. Store embeddings in ChromaDB
    3. Update document status in Supabase
    """
    import asyncio

    async def _run():
        from app.services.document_processor import processor
        from app.services.vector_store import vector_store
        from app.services.financial_analyzer import analyzer
        from app.database import update_record, insert_record
        import uuid

        self.update_state(state="PROGRESS", meta={"step": "extracting_text", "progress": 20})
        result = processor.process_file(file_path)
        raw_text = result.get("raw_text", "")
        financial_data = result.get("financial_data", {})

        # Store in ChromaDB
        self.update_state(state="PROGRESS", meta={"step": "embedding", "progress": 50})
        if raw_text:
            vector_store.add_document(
                doc_id=document_id,
                company_id=company_id,
                text=raw_text,
                metadata={"file_path": file_path},
            )

        # Update document record
        self.update_state(state="PROGRESS", meta={"step": "saving", "progress": 75})
        await update_record("documents", document_id, {
            "processing_status": "completed",
            "extracted_text": raw_text[:4000],
            "page_count": result.get("page_count", 1),
        })

        # Save financials if extracted
        if financial_data:
            analysis = analyzer.analyze(financial_data)
            ratios = analysis.get("ratios", {})
            ratios_db = {k: v for k, v in ratios.items() if k not in ["dscr", "tol_tnw", "ebitda_margin", "gross_margin", "debt_to_assets"]}
            await insert_record("financials", {
                "id": str(uuid.uuid4()),
                "company_id": company_id,
                "document_id": document_id,
                **financial_data,
                **ratios_db,
            })

        return {
            "status": "completed",
            "document_id": document_id,
            "text_length": len(raw_text),
            "financial_fields": len(financial_data),
        }

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(_run())
    except Exception as e:
        logger.error(f"Document task failed: {e}")
        raise
    finally:
        loop.close()
