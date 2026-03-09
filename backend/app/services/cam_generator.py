"""
CAM (Credit Appraisal Memo) Generator
Generates a comprehensive credit appraisal memo from all analysis data.
"""
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class CAMGenerator:
    """Generate Credit Appraisal Memo from aggregated analysis."""

    def generate(
        self,
        company: dict,
        financials: dict,
        ratios: dict,
        risk_analysis: dict,
        research_report: dict,
        decision: dict,
    ) -> dict:
        """Generate a full CAM report."""
        company_name = company.get("company_name", "Unknown Company")
        industry = company.get("industry", "Unknown")
        now = datetime.utcnow().strftime("%B %d, %Y")

        # ── Company Overview ─────────────────────────────────────────────
        company_overview = f"""
{company_name} is engaged in the {industry} sector.
Registration: {company.get('registration_number', 'Not provided')}
CIN: {company.get('cin', 'Not provided')}
Website: {company.get('website', 'Not provided')}
Contact: {company.get('contact_email', 'Not provided')}
        """.strip()

        # ── Financial Analysis ────────────────────────────────────────────
        rev = financials.get("revenue", 0) or 0
        profit = financials.get("net_profit", 0) or 0
        debt = financials.get("total_debt", 0) or 0

        def fmt_cr(val):
            if not val:
                return "N/A"
            cr = val / 10_000_000
            return f"₹{cr:.2f} Cr"

        financial_analysis = f"""
FINANCIAL HIGHLIGHTS (Latest Year):
• Revenue: {fmt_cr(rev)}
• Net Profit: {fmt_cr(profit)}
• Total Debt: {fmt_cr(debt)}
• Profit Margin: {ratios.get('profit_margin', 'N/A')}%
• Debt-to-Equity: {ratios.get('debt_equity_ratio', 'N/A')}
• Current Ratio: {ratios.get('current_ratio', 'N/A')}
• Interest Coverage: {ratios.get('interest_coverage', 'N/A')}x
• Return on Equity: {ratios.get('roe', 'N/A')}%
• EBITDA Margin: {ratios.get('ebitda_margin', 'N/A')}%
        """.strip()

        # ── Risk Assessment ───────────────────────────────────────────────
        risk_factors = risk_analysis.get("risk_factors", [])
        risk_factors_text = "\n".join(f"  - {f}" for f in risk_factors) if risk_factors else "  - No significant risk factors detected"

        risk_assessment = f"""
RISK SCORE: {risk_analysis.get('overall_risk_score', 'N/A')}/100
RISK GRADE: {risk_analysis.get('risk_grade', 'N/A')}
DEFAULT PROBABILITY: {float(risk_analysis.get('default_probability', 0)) * 100:.1f}%

COMPONENT SCORES:
• Rule-Based Financial Risk: {risk_analysis.get('component_scores', {}).get('rule_based', 'N/A')}/100
• ML Model Risk: {risk_analysis.get('component_scores', {}).get('ml_model', 'N/A')}/100
• NLP Text Risk: {risk_analysis.get('component_scores', {}).get('nlp_text', 'N/A')}/100
• Sector Risk: {risk_analysis.get('component_scores', {}).get('sector', 'N/A')}/100

KEY RISK FACTORS:
{risk_factors_text}
        """.strip()

        # ── Industry Outlook ──────────────────────────────────────────────
        industry_outlook = f"""
INDUSTRY: {industry}
NEWS RISK: {research_report.get('news_risk_level', 'N/A')}
LITIGATION RISK: {research_report.get('litigation_risk_level', 'N/A')}
SECTOR RISK: {research_report.get('industry_risk_level', 'N/A')}

NEWS SUMMARY: {research_report.get('news_summary', 'No data')}
LITIGATION SUMMARY: {research_report.get('litigation_summary', 'No data')}
INDUSTRY SUMMARY: {research_report.get('industry_summary', 'No data')}
        """.strip()

        # ── Loan Recommendation ───────────────────────────────────────────
        loan_amt = decision.get("recommended_loan_amount", 0)
        conditions = decision.get("conditions", [])
        conditions_text = "\n".join(f"  {i+1}. {c}" for i, c in enumerate(conditions)) if conditions else "  None"

        loan_recommendation = f"""
DECISION: {decision.get('decision', 'N/A')}
RECOMMENDED LOAN AMOUNT: {fmt_cr(loan_amt)}
INTEREST RATE: {decision.get('interest_rate', 'N/A')}% per annum
LOAN TENOR: {decision.get('loan_tenor_months', 'N/A')} months

CONDITIONS:
{conditions_text}
        """.strip()

        executive_summary = f"""
This Credit Appraisal Memo has been prepared by IntelliCredit AI on {now}
for the loan application submitted by {company_name} ({industry} sector).

Based on comprehensive analysis of financial statements, ML-based risk modeling,
NLP text analysis, and AI research agents:

FINAL DECISION: {decision.get('decision', 'N/A')}
CREDIT LIMIT: {fmt_cr(loan_amt)}
INTEREST RATE: {decision.get('interest_rate', 0)}% p.a.
RISK SCORE: {risk_analysis.get('overall_risk_score', 'N/A')}/100

{"The company demonstrates acceptable financial metrics for loan approval."
 if decision.get('decision') == 'Approve'
 else "This recommendation is subject to the conditions outlined in the report."}
        """.strip()

        # ── LLM Enhancement (Ollama) ──────────────────────────────────────
        # Try to enhance sections with LLM if Ollama is running
        try:
            from app.services.llm_service import llm_service
            loan_amt_cr = (loan_amt or 0) / 10_000_000

            llm_exec = llm_service.enhance_executive_summary(
                company_name=company_name,
                industry=industry,
                risk_score=risk_analysis.get("overall_risk_score", 50),
                risk_grade=risk_analysis.get("risk_grade", "Medium"),
                decision=decision.get("decision", "N/A"),
                loan_amount_cr=loan_amt_cr,
                key_risks=list(risk_analysis.get("risk_factors", []))[:3],
            )
            if llm_exec:
                executive_summary = executive_summary + f"\n\nAI NARRATIVE:\n{llm_exec}"

            llm_risk = llm_service.enhance_risk_assessment(
                company_name=company_name,
                risk_factors=list(risk_analysis.get("risk_factors", [])),
                financial_flags=[],
                news_risk=research_report.get("news_risk_level", "Low"),
                litigation_risk=research_report.get("litigation_risk_level", "Low"),
            )
            if llm_risk:
                risk_assessment = risk_assessment + f"\n\nAI RISK NARRATIVE:\n{llm_risk}"

            llm_ind = llm_service.enhance_industry_outlook(
                industry=industry,
                industry_summary=research_report.get("industry_summary", ""),
            )
            if llm_ind:
                industry_outlook = industry_outlook + f"\n\nAI INDUSTRY ANALYSIS:\n{llm_ind}"

        except Exception as llm_err:
            logger.debug(f"LLM enhancement skipped: {llm_err}")


        return {
            "executive_summary": executive_summary,
            "company_overview": company_overview,
            "financial_analysis": financial_analysis,
            "risk_assessment": risk_assessment,
            "industry_outlook": industry_outlook,
            "loan_recommendation": loan_recommendation,
            "decision": decision.get("decision"),
            "risk_score": risk_analysis.get("overall_risk_score"),
            "recommended_loan_amount": loan_amt,
            "interest_rate": decision.get("interest_rate"),
            "loan_tenor_months": decision.get("loan_tenor_months"),
            "conditions": conditions,
        }


cam_generator = CAMGenerator()
