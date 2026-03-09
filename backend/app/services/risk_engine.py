"""
Risk Detection Engine — three-layer approach:
1. Rule-based checks on financial ratios
2. XGBoost ML model for default probability
3. Keyword-based NLP for text risk signals
"""
import logging
import numpy as np
from typing import Optional

logger = logging.getLogger(__name__)

# ─── NLP Risk Keywords ─────────────────────────────────────────────────────────
NEGATIVE_KEYWORDS = [
    "fraud", "scam", "investigation", "regulatory action", "penalty", "fine",
    "lawsuit", "litigation", "insolvency", "bankruptcy", "nclt", "npa",
    "default", "winding up", "criminal", "arrested", "seized", "raid",
    "misappropriation", "embezzlement", "money laundering", "shell company",
    "ponzi", "wilful defaulter", "drt", "written off",
]

POSITIVE_KEYWORDS = [
    "profit growth", "revenue increase", "expansion", "new contract",
    "government approval", "export growth", "award", "rating upgrade",
    "debt reduction", "equity infusion",
]

SECTOR_RISK_KEYWORDS = {
    "high": ["real estate", "construction", "telecom", "aviation", "power"],
    "medium": ["retail", "textile", "hospitality", "auto"],
    "low": ["fmcg", "pharma", "it", "technology", "healthcare"],
}


class RiskEngine:
    """Multi-layer risk detection engine."""

    def __init__(self):
        self._xgboost_model = None
        self._model_loaded = False

    def _load_xgboost(self):
        """Lazy-load XGBoost model or train a simple one on synthetic data."""
        if self._model_loaded:
            return
        try:
            import xgboost as xgb
            from sklearn.datasets import make_classification
            from sklearn.model_selection import train_test_split

            # Train on synthetic financial features (demo model)
            X, y = make_classification(
                n_samples=2000,
                n_features=8,
                n_informative=6,
                n_redundant=2,
                random_state=42,
            )
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            self._xgboost_model = xgb.XGBClassifier(
                n_estimators=100,
                max_depth=4,
                learning_rate=0.1,
                use_label_encoder=False,
                eval_metric="logloss",
                random_state=42,
            )
            self._xgboost_model.fit(X_train, y_train)
            logger.info("XGBoost model trained on synthetic data")
        except ImportError:
            logger.warning("XGBoost not available — skipping ML layer")
        self._model_loaded = True

    def analyze(self, financials: dict, company_text: str = "", industry: str = "") -> dict:
        """
        Full three-layer risk analysis.

        Args:
            financials: dict of raw financial figures + ratios
            company_text: extracted document text for NLP analysis
            industry: company industry for sector risk

        Returns:
            risk_score (0-100, 100 = highest risk)
            risk_grade: Low | Medium | High | Critical
            default_probability (0.0-1.0)
            risk_factors: list of detected risks
        """
        risk_factors = []

        # Layer 1: Rule-based ─────────────────────────────────
        rule_score, rule_flags = self._rule_based_analysis(financials)
        risk_factors.extend(rule_flags)

        # Layer 2: ML model ───────────────────────────────────
        ml_prob = self._ml_analysis(financials)

        # Layer 3: NLP text analysis ──────────────────────────
        nlp_score, nlp_flags = self._nlp_analysis(company_text)
        risk_factors.extend(nlp_flags)

        # Layer 4: Sector risk ────────────────────────────────
        sector_score, sector_flags = self._sector_analysis(industry)
        risk_factors.extend(sector_flags)

        # ── Weighted Final Score (0-100, higher = riskier) ────
        # Note: rule_score, nlp_score, sector_score are risk scores (0-100)
        # ml_prob is 0-1; convert to 0-100
        ml_score_100 = ml_prob * 100

        final_score = (
            rule_score * 0.45
            + ml_score_100 * 0.25
            + nlp_score * 0.20
            + sector_score * 0.10
        )
        final_score = round(min(100.0, max(0.0, final_score)), 1)

        # Grade
        if final_score < 30:
            grade = "Low"
        elif final_score < 55:
            grade = "Medium"
        elif final_score < 75:
            grade = "High"
        else:
            grade = "Critical"

        return {
            "overall_risk_score": final_score,
            "risk_grade": grade,
            "default_probability": round(ml_prob, 4),
            "risk_factors": risk_factors,
            "component_scores": {
                "rule_based": round(rule_score, 1),
                "ml_model": round(ml_score_100, 1),
                "nlp_text": round(nlp_score, 1),
                "sector": round(sector_score, 1),
            },
        }

    def _rule_based_analysis(self, financials: dict) -> tuple[float, list]:
        """Rule-based scoring inverted from the financial health score."""
        score = 20.0  # base risk
        flags = []

        # Use the advanced 0-100 financial health score if available
        if "financial_score" in financials:
            health_score = financials["financial_score"]
            # 100 health (perfect) = 0 risk. 0 health = 100 risk.
            score = max(0.0, 100.0 - health_score)

        de = financials.get("debt_equity_ratio")
        pm = financials.get("profit_margin")
        cr = financials.get("current_ratio")
        ic = financials.get("interest_coverage")
        growth = financials.get("revenue_growth")

        if de is not None:
            if de > 4:
                score += 30; flags.append(f"⚠️ Very high D/E ratio: {de:.2f}")
            elif de > 2:
                score += 20; flags.append(f"⚠️ High D/E ratio: {de:.2f}")
            elif de > 1:
                score += 8

        if pm is not None:
            if pm < 0:
                score += 30; flags.append(f"❌ Negative profit margin: {pm:.1f}%")
            elif pm < 3:
                score += 20; flags.append(f"⚠️ Low profit margin: {pm:.1f}%")
            elif pm < 7:
                score += 8

        if cr is not None:
            if cr < 0.8:
                score += 25; flags.append(f"❌ Critical liquidity — current ratio: {cr:.2f}")
            elif cr < 1.2:
                score += 15; flags.append(f"⚠️ Tight liquidity — current ratio: {cr:.2f}")

        if ic is not None:
            if ic < 1:
                flags.append(f"❌ Cannot cover interest — coverage: {ic:.2f}x")
            elif ic < 2:
                flags.append(f"⚠️ Weak interest coverage: {ic:.2f}x")

        dscr = financials.get("dscr")
        if dscr is not None:
            if dscr < 1.0:
                flags.append(f"❌ Critical DSCR limit breached: {dscr:.2f}x")
            elif dscr < 1.25:
                flags.append(f"⚠️ Tight DSCR: {dscr:.2f}x")

        if growth is not None and growth < -10:
            score += 15; flags.append(f"⚠️ Significant revenue decline: {growth:.1f}%")

        return min(score, 100.0), flags

    def _ml_analysis(self, financials: dict) -> float:
        """XGBoost default probability prediction."""
        self._load_xgboost()
        if not self._xgboost_model:
            # Fallback: simple heuristic
            de = financials.get("debt_equity_ratio", 1)
            pm = financials.get("profit_margin", 10)
            cr = financials.get("current_ratio", 1.5)
            prob = min(1.0, max(0.0, (de * 0.15 + max(0, 10 - pm) * 0.03 + max(0, 1.5 - cr) * 0.2)))
            return round(prob, 4)

        try:
            # Build feature vector (must match training features)
            de = financials.get("debt_equity_ratio", 1.0) or 1.0
            pm = financials.get("profit_margin", 10.0) or 10.0
            cr = financials.get("current_ratio", 1.5) or 1.5
            ic = financials.get("interest_coverage", 3.0) or 3.0
            roe = financials.get("roe", 10.0) or 10.0
            da = financials.get("debt_to_assets", 0.5) or 0.5
            em = financials.get("ebitda_margin", 12.0) or 12.0
            rg = financials.get("revenue_growth", 5.0) or 5.0

            features = np.array([[de, pm, cr, ic, roe, da, em, rg]])
            prob = float(self._xgboost_model.predict_proba(features)[0][1])
            return round(prob, 4)
        except Exception as e:
            logger.warning(f"XGBoost prediction failed: {e}")
            return 0.3

    def _nlp_analysis(self, text: str) -> tuple[float, list]:
        """Keyword-based NLP risk detection."""
        if not text:
            return 20.0, []

        text_lower = text.lower()
        score = 10.0
        flags = []

        neg_count = sum(1 for kw in NEGATIVE_KEYWORDS if kw in text_lower)
        pos_count = sum(1 for kw in POSITIVE_KEYWORDS if kw in text_lower)

        for kw in NEGATIVE_KEYWORDS:
            if kw in text_lower:
                score += 8
                flags.append(f"📰 Risk keyword detected: '{kw}'")
                if len(flags) >= 5:  # cap flags
                    break

        score -= pos_count * 3  # positive signals reduce risk
        return round(min(100.0, max(0.0, score)), 1), flags

    def _sector_analysis(self, industry: str) -> tuple[float, list]:
        """Sector-based risk scoring."""
        if not industry:
            return 30.0, []  # unknown sector = medium risk

        industry_lower = industry.lower()
        for level, keywords in SECTOR_RISK_KEYWORDS.items():
            for kw in keywords:
                if kw in industry_lower:
                    if level == "high":
                        return 70.0, [f"🏭 High-risk sector: {industry}"]
                    elif level == "medium":
                        return 45.0, [f"🏭 Medium-risk sector: {industry}"]
                    else:
                        return 20.0, []

        return 35.0, []  # default medium-low


# Singleton instance
risk_engine = RiskEngine()
