"""
Full analysis pipeline Celery task.
Runs document → financials → risk → research → decision → CAM in sequence.
"""
import logging
from app.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="run_full_pipeline")
def run_full_pipeline(self, company_id: str, document_path: str, company_name: str, industry: str = ""):
    """
    Run the complete IntelliCredit AI analysis pipeline.

    Steps:
    1. Process document → extract financial data
    2. Calculate financial ratios
    3. Run risk analysis (rules + ML + NLP)
    4. Run research agents (news + litigation + industry)
    5. Generate decision
    6. Generate CAM report
    """
    import asyncio

    async def _pipeline():
        from app.services.document_processor import processor
        from app.services.financial_analyzer import analyzer
        from app.services.risk_engine import risk_engine
        from app.services.decision_engine import decision_engine
        from app.services.cam_generator import cam_generator
        from app.agents.news_agent import news_agent
        from app.agents.litigation_agent import litigation_agent
        from app.agents.industry_agent import industry_agent
        from app.database import insert_record, fetch_record, update_record
        import uuid

        logger.info(f"[Pipeline] Starting for company_id={company_id}")

        # Step 1: Document processing
        self.update_state(state="PROGRESS", meta={"step": "processing_document", "progress": 10})
        doc_result = processor.process_file(document_path)
        financial_data = doc_result.get("financial_data", {})
        raw_text = doc_result.get("raw_text", "")
        logger.info(f"[Pipeline] Document processed: {len(raw_text)} chars, {len(financial_data)} financial fields")

        # Step 2: Financial analysis
        self.update_state(state="PROGRESS", meta={"step": "financial_analysis", "progress": 25})
        analysis = analyzer.analyze(financial_data)
        ratios_db = {k: v for k, v in ratios.items() if k not in ["dscr", "tol_tnw", "ebitda_margin", "gross_margin", "debt_to_assets"]}
        fin_record = {
            "id": str(uuid.uuid4()),
            "company_id": company_id,
            **financial_data,
            **ratios_db,
        }
        await insert_record("financials", fin_record)

        # Step 3: Risk analysis
        self.update_state(state="PROGRESS", meta={"step": "risk_analysis", "progress": 45})
        merged = {**financial_data, **ratios}
        risk_result = risk_engine.analyze(merged, raw_text, industry)
        risk_record = {
            "id": str(uuid.uuid4()),
            "company_id": company_id,
            "overall_risk_score": risk_result["overall_risk_score"],
            "risk_grade": risk_result["risk_grade"],
            "default_probability": risk_result["default_probability"],
            "risk_factors": risk_result["risk_factors"],
        }
        await insert_record("risk_scores", risk_record)

        # Step 4: Research agents
        self.update_state(state="PROGRESS", meta={"step": "research_agents", "progress": 65})
        news_r = news_agent.research(company_name)
        lit_r = litigation_agent.research(company_name)
        ind_r = industry_agent.research(industry, company_name)
        research_record = {
            "id": str(uuid.uuid4()),
            "company_id": company_id,
            "news_summary": news_r["news_summary"],
            "news_risk_level": news_r["news_risk_level"],
            "news_articles": news_r["news_articles"],
            "litigation_summary": lit_r["litigation_summary"],
            "litigation_risk_level": lit_r["litigation_risk_level"],
            "litigation_cases": lit_r["litigation_cases"],
            "industry_summary": ind_r["industry_summary"],
            "industry_risk_level": ind_r["industry_risk_level"],
        }
        await insert_record("research_reports", research_record)

        # Step 5 + 6: Decision + CAM
        self.update_state(state="PROGRESS", meta={"step": "generating_cam", "progress": 85})
        company_rec = (await fetch_record("companies", {"id": company_id}) or [{}])[0]
        decision = decision_engine.decide(company_name, merged, risk_result, research_record)
        cam = cam_generator.generate(company_rec, merged, ratios, risk_result, research_record, decision)

        cam_record = {
            "id": str(uuid.uuid4()),
            "company_id": company_id,
            **{k: cam[k] for k in [
                "executive_summary", "company_overview", "financial_analysis",
                "risk_assessment", "industry_outlook", "loan_recommendation",
                "decision", "risk_score", "recommended_loan_amount",
                "interest_rate", "loan_tenor_months",
            ]},
        }
        await insert_record("cam_reports", cam_record)

        logger.info(f"[Pipeline] Complete! Decision: {decision['decision']}, Score: {risk_result['overall_risk_score']}")
        return {
            "status": "completed",
            "decision": decision["decision"],
            "risk_score": risk_result["overall_risk_score"],
            "cam_id": cam_record["id"],
        }

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(_pipeline())
    finally:
        loop.close()
