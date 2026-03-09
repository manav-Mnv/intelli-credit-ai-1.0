"""
Financial Analysis Engine
Calculates all key financial ratios from extracted financial data.
"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class FinancialAnalyzer:
    """Calculate financial ratios and flag anomalies."""

    def analyze(self, financials: dict) -> dict:
        """
        Accepts raw financial figures and returns computed ratios.

        Input keys (all optional, in local currency units):
            revenue, net_profit, gross_profit, ebitda,
            total_debt, total_equity, total_assets, total_liabilities,
            current_assets, current_liabilities, interest_expense

        Returns dict with ratios + interpretations.
        """
        rev = financials.get("revenue")
        profit = financials.get("net_profit")
        debt = financials.get("total_debt")
        equity = financials.get("total_equity")
        assets = financials.get("total_assets")
        curr_assets = financials.get("current_assets")
        curr_liab = financials.get("current_liabilities")
        interest = financials.get("interest_expense")
        ebitda = financials.get("ebitda")
        gross_profit = financials.get("gross_profit")
        prev_revenue = financials.get("prev_revenue")  # previous year

        ratios = {}
        flags = []

        # ── Profitability ──────────────────────────────────────
        if profit is not None and rev and rev > 0:
            ratios["profit_margin"] = round(profit / rev * 100, 2)
            if ratios["profit_margin"] < 0:
                flags.append("Negative profit margin — company is loss-making")
            elif ratios["profit_margin"] < 5:
                flags.append("Very thin profit margin (<5%)")

        if gross_profit is not None and rev and rev > 0:
            ratios["gross_margin"] = round(gross_profit / rev * 100, 2)

        if ebitda is not None and rev and rev > 0:
            ratios["ebitda_margin"] = round(ebitda / rev * 100, 2)

        # ── Leverage ───────────────────────────────────────────
        if debt is not None and equity and equity > 0:
            ratios["debt_equity_ratio"] = round(debt / equity, 2)
            if ratios["debt_equity_ratio"] > 3:
                flags.append(f"High D/E ratio ({ratios['debt_equity_ratio']:.2f}) — heavily leveraged")
            elif ratios["debt_equity_ratio"] > 2:
                flags.append(f"Elevated D/E ratio ({ratios['debt_equity_ratio']:.2f})")

        if assets is not None and debt is not None:
            total_liab = financials.get("total_liabilities", debt)
            if assets > 0:
                ratios["debt_to_assets"] = round(total_liab / assets, 2)

        # ── Liquidity ──────────────────────────────────────────
        if curr_assets is not None and curr_liab and curr_liab > 0:
            ratios["current_ratio"] = round(curr_assets / curr_liab, 2)
            if ratios["current_ratio"] < 1:
                flags.append(f"Current ratio below 1 ({ratios['current_ratio']:.2f}) — liquidity risk")
            elif ratios["current_ratio"] < 1.5:
                flags.append(f"Low current ratio ({ratios['current_ratio']:.2f})")

        # ── Debt Service ───────────────────────────────────────
        if interest and interest > 0:
            if ebitda is not None:
                ratios["interest_coverage"] = round(ebitda / interest, 2)
                if ratios["interest_coverage"] < 1.5:
                    flags.append(f"Very low interest coverage ({ratios['interest_coverage']:.2f}x)")
                elif ratios["interest_coverage"] < 2.5:
                    flags.append(f"Low interest coverage ({ratios['interest_coverage']:.2f}x)")
                
                # DSCR (Debt Service Coverage Ratio)
                # Proxy: Principal repayment = 10% of total debt
                if debt is not None and debt > 0:
                    principal = debt / 10.0
                    total_debt_service = interest + principal
                    ratios["dscr"] = round(ebitda / total_debt_service, 2)
                    if ratios["dscr"] < 1.0:
                        flags.append(f"Critical DSCR ({ratios['dscr']:.2f}x) — insufficient cash limits")
                    elif ratios["dscr"] < 1.25:
                        flags.append(f"Low DSCR ({ratios['dscr']:.2f}x) — tight coverage")

            elif profit is not None:
                ratios["interest_coverage"] = round((profit + interest) / interest, 2)

        # ── Return Ratios ──────────────────────────────────────
        if profit is not None and equity and equity > 0:
            ratios["roe"] = round(profit / equity * 100, 2)

        if ebitda is not None and assets and assets > 0:
            ratios["roce"] = round(ebitda / assets * 100, 2)

        # ── Extended Leverage (TOL/TNW) ────────────────────────
        if equity is not None and equity > 0:
            total_liab = financials.get("total_liabilities", debt)
            if total_liab is not None:
                ratios["tol_tnw"] = round(total_liab / equity, 2)
                if ratios["tol_tnw"] > 4:
                    flags.append(f"High TOL/TNW ({ratios['tol_tnw']:.2f}) — severe leverage risk")

        # ── Growth ─────────────────────────────────────────────
        if prev_revenue and prev_revenue > 0 and rev:
            ratios["revenue_growth"] = round((rev - prev_revenue) / prev_revenue * 100, 2)
            if ratios["revenue_growth"] < 0:
                flags.append(f"Revenue declined {abs(ratios['revenue_growth']):.1f}% YoY")

        # ── Scoring ────────────────────────────────────────────
        financial_score = self._calculate_financial_score(ratios)

        return {
            "ratios": ratios,
            "flags": flags,
            "financial_score": financial_score,
            "raw_financials": financials,
        }

    def _calculate_financial_score(self, ratios: dict) -> float:
        """
        Score 0-100 (higher = better financial health).
        Weighted across profitability, leverage, liquidity, and debt service.
        """
        score = 50.0  # neutral baseline

        # Profit margin: ±15 points
        pm = ratios.get("profit_margin")
        if pm is not None:
            if pm > 15: score += 15
            elif pm > 10: score += 10
            elif pm > 5: score += 5
            elif pm > 0: score -= 5
            else: score -= 15

        # D/E ratio: ±15 points
        de = ratios.get("debt_equity_ratio")
        if de is not None:
            if de < 0.5: score += 15
            elif de < 1: score += 10
            elif de < 1.5: score += 5
            elif de < 2: score -= 5
            elif de < 3: score -= 10
            else: score -= 15

        # Current ratio: ±10 points
        cr = ratios.get("current_ratio")
        if cr is not None:
            if cr > 2: score += 10
            elif cr > 1.5: score += 5
            elif cr > 1: score += 2
            else: score -= 10

        # DSCR: ±20 points (Most critical for debt repayment)
        dscr = ratios.get("dscr")
        if dscr is not None:
            if dscr > 2.0: score += 20
            elif dscr > 1.5: score += 12
            elif dscr > 1.25: score += 5
            elif dscr < 1.0: score -= 20
            else: score -= 5
        else:
            # Fallback to ICR if DSCR is missing
            ic = ratios.get("interest_coverage")
            if ic is not None:
                if ic > 5: score += 15
                elif ic > 3: score += 8
                elif ic > 1.5: score += 2
                else: score -= 15

        return round(max(0.0, min(100.0, score)), 1)


# Singleton instance
analyzer = FinancialAnalyzer()
