"""
AI Decision Engine
Aggregates all signals into a final credit decision.
"""
import logging

logger = logging.getLogger(__name__)


RISK_LEVEL_WEIGHTS = {"Low": 0.2, "Medium": 0.5, "High": 0.9}


class DecisionEngine:
    """Combine risk score, research findings, and financials into a loan decision."""

    def decide(
        self,
        company_name: str,
        financials: dict,
        risk_analysis: dict,
        research_report: dict,
        requested_loan_amount: float = None,
    ) -> dict:
        """
        Generate credit decision.

        Returns decision, recommended loan amount, interest rate,
        risk score, and conditions.
        """
        risk_score = risk_analysis.get("overall_risk_score", 50.0)
        risk_grade = risk_analysis.get("risk_grade", "Medium")
        revenue = financials.get("revenue", 0) or 0

        # Incorporate research risk
        news_risk = research_report.get("news_risk_level", "Low")
        lit_risk = research_report.get("litigation_risk_level", "Low")
        news_score = RISK_LEVEL_WEIGHTS.get(news_risk, 0.5) * 10
        lit_score = RISK_LEVEL_WEIGHTS.get(lit_risk, 0.5) * 10
        adjusted_score = min(100.0, risk_score + news_score + lit_score)

        # Decision logic
        conditions = []
        if adjusted_score < 35:
            decision = "Approve"
            interest_rate = 9.5
        elif adjusted_score < 55:
            decision = "Approve with Conditions"
            interest_rate = 11.0
            conditions = ["Quarterly financial review required", "Collateral security mandatory"]
        elif adjusted_score < 75:
            decision = "Approve with Conditions"
            interest_rate = 13.5
            conditions = [
                "Personal guarantee from promoters required",
                "Additional collateral of 150% loan value",
                "Monthly financial reporting required",
                "Escrow account for loan repayment",
            ]
        else:
            decision = "Reject"
            interest_rate = 0
            conditions = ["Risk profile too high for approval", "Suggest re-application after 12 months of improved financials"]

        # Loan amount recommendation (up to 3x EBITDA or 60% of annual revenue)
        ebitda = financials.get("ebitda") or financials.get("net_profit", 0) or 0
        max_by_ebitda = ebitda * 3 if ebitda > 0 else 0
        max_by_revenue = revenue * 0.6 if revenue > 0 else 0
        base_cap = max(max_by_ebitda, max_by_revenue)

        if requested_loan_amount and base_cap > 0:
            recommended_amount = min(requested_loan_amount, base_cap)
        elif base_cap > 0:
            recommended_amount = base_cap * 0.7  # 70% of maximum capacity
        else:
            recommended_amount = 0

        # Reduce for higher risk
        risk_reduction = {
            "Low": 1.0,
            "Medium": 0.85,
            "High": 0.65,
            "Critical": 0.0,
        }
        recommended_amount *= risk_reduction.get(risk_grade, 0.75)

        # Loan tenor (months)
        tenor = 60 if adjusted_score < 55 else 36

        return {
            "decision": decision,
            "risk_score": round(adjusted_score, 1),
            "risk_grade": risk_grade,
            "recommended_loan_amount": round(recommended_amount, 2),
            "interest_rate": interest_rate,
            "loan_tenor_months": tenor,
            "conditions": conditions,
        }


decision_engine = DecisionEngine()
