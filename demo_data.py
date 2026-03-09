"""
Demo Data Generator
Creates a sample company with realistic financial data for hackathon demo.
Run: python demo_data.py
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

# Sample companies for demo
DEMO_COMPANIES = [
    {
        "company": {
            "company_name": "ABC Steel Manufacturing Ltd",
            "industry": "Steel & Metals",
            "registration_number": "U27100MH2010PLC123456",
            "cin": "U27100MH2010PLC123456",
            "pan": "AABCS1234C",
            "website": "https://abcsteel.example.com",
            "contact_email": "finance@abcsteel.example.com",
        },
        "financials": {
            "revenue": 65_00_00_000,          # ₹65 Crore
            "net_profit": 7_00_00_000,         # ₹7 Crore
            "gross_profit": 12_00_00_000,       # ₹12 Crore
            "ebitda": 10_50_00_000,            # ₹10.5 Crore
            "total_debt": 18_00_00_000,        # ₹18 Crore
            "total_equity": 25_00_00_000,      # ₹25 Crore
            "total_assets": 45_00_00_000,      # ₹45 Crore
            "current_assets": 22_00_00_000,    # ₹22 Crore
            "current_liabilities": 14_00_00_000, # ₹14 Crore
            "interest_expense": 2_10_00_000,   # ₹2.1 Crore
        },
        "loan_request": 10_00_00_000,  # ₹10 Crore
    },
    {
        "company": {
            "company_name": "TechSoft Solutions Pvt Ltd",
            "industry": "IT & Technology",
            "registration_number": "U72200KA2015PTC234567",
        },
        "financials": {
            "revenue": 28_00_00_000,
            "net_profit": 5_60_00_000,
            "ebitda": 7_00_00_000,
            "total_debt": 3_00_00_000,
            "total_equity": 15_00_00_000,
            "total_assets": 20_00_00_000,
            "current_assets": 12_00_00_000,
            "current_liabilities": 4_00_00_000,
            "interest_expense": 36_00_000,
        },
        "loan_request": 5_00_00_000,
    },
    {
        "company": {
            "company_name": "Sunrise Real Estate Developers Ltd",
            "industry": "Real Estate",
            "registration_number": "U45200DL2008PLC345678",
        },
        "financials": {
            "revenue": 85_00_00_000,
            "net_profit": 2_10_00_000,  # thin margins
            "ebitda": 8_50_00_000,
            "total_debt": 62_00_00_000,  # heavy debt
            "total_equity": 20_00_00_000,
            "total_assets": 120_00_00_000,
            "current_assets": 18_00_00_000,
            "current_liabilities": 22_00_00_000,  # current ratio < 1
            "interest_expense": 7_44_00_000,
        },
        "loan_request": 25_00_00_000,
    },
]


async def create_demo_company(demo: dict):
    """Create one demo company with all analysis."""
    try:
        from app.database import insert_record
        from app.services.financial_analyzer import analyzer
        from app.services.risk_engine import risk_engine
        from app.services.decision_engine import decision_engine
        from app.services.cam_generator import cam_generator
        import uuid

        company_id = str(uuid.uuid4())
        company_data = {"id": company_id, **demo["company"]}
        await insert_record("companies", company_data)
        print(f"  ✅ Created company: {demo['company']['company_name']}")

        # Financial analysis
        fin_data = demo["financials"]
        analysis = analyzer.analyze(fin_data)
        ratios = analysis["ratios"]

        # Create a mock document record so FK constraint passes
        doc_id = str(uuid.uuid4())
        await insert_record("documents", {
            "id": doc_id,
            "company_id": company_id,
            "file_name": "demo_data.pdf",
            "processing_status": "completed"
        })

        ratios.pop("debt_to_assets", None)
        ratios.pop("gross_margin", None)
        ratios.pop("ebitda_margin", None)

        fin_record = {
            "id": str(uuid.uuid4()),
            "company_id": company_id,
            "document_id": doc_id,
            **fin_data,
            **ratios,
        }
        await insert_record("financials", fin_record)
        print(f"     💰 Profit margin: {ratios.get('profit_margin', 'N/A')}%, D/E: {ratios.get('debt_equity_ratio', 'N/A')}")

        # Risk analysis
        merged = {**fin_data, **ratios}
        risk_result = risk_engine.analyze(
            financials=merged,
            industry=demo["company"].get("industry", ""),
        )
        risk_record = {
            "id": str(uuid.uuid4()),
            "company_id": company_id,
            "overall_risk_score": risk_result["overall_risk_score"],
            "risk_grade": risk_result["risk_grade"],
            "default_probability": risk_result["default_probability"],
            "risk_factors": risk_result["risk_factors"],
        }
        await insert_record("risk_scores", risk_record)
        print(f"     🛡️  Risk score: {risk_result['overall_risk_score']}/100 ({risk_result['risk_grade']})")

        # Research (stub — no real web search in demo)
        research_record = {
            "id": str(uuid.uuid4()),
            "company_id": company_id,
            "news_summary": "No significant adverse news found in demo data.",
            "news_risk_level": "Low",
            "news_articles": [],
            "litigation_summary": "No active litigation found in demo data.",
            "litigation_risk_level": "Low",
            "litigation_cases": [],
            "industry_summary": f"The {demo['company'].get('industry', 'Unknown')} sector shows mixed outlook.",
            "industry_risk_level": "Medium",
            "industry_trends": [],
            "overall_sentiment": -0.2,
        }
        await insert_record("research_reports", research_record)

        # Decision + CAM
        decision = decision_engine.decide(
            company_name=demo["company"]["company_name"],
            financials=merged,
            risk_analysis=risk_result,
            research_report=research_record,
            requested_loan_amount=demo.get("loan_request"),
        )
        cam = cam_generator.generate(
            company=company_data,
            financials=merged,
            ratios=ratios,
            risk_analysis=risk_result,
            research_report=research_record,
            decision=decision,
        )
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
        recommended_cr = (cam["recommended_loan_amount"] or 0) / 10_000_000
        print(f"     📋 Decision: {decision['decision']} | Loan: ₹{recommended_cr:.1f} Cr @ {decision['interest_rate']}%")
        print(f"     🆔 Company ID: {company_id}")
        return company_id

    except Exception as e:
        print(f"  ❌ Failed: {e}")
        return None


async def main():
    print("\n🏦 IntelliCredit AI — Demo Data Generator")
    print("==========================================\n")
    print("Creating demo companies...\n")

    ids = []
    for demo in DEMO_COMPANIES:
        cid = await create_demo_company(demo)
        if cid:
            ids.append((demo["company"]["company_name"], cid))

    print("\n==========================================")
    print("✅ Demo data created!\n")
    print("Open the dashboard to see them:")
    print("  http://localhost:3000/dashboard\n")
    for name, cid in ids:
        print(f"  {name}")
        print(f"  → Analysis: http://localhost:3000/analysis/{cid}")
        print(f"  → CAM:      http://localhost:3000/cam/{cid}\n")


if __name__ == "__main__":
    asyncio.run(main())
