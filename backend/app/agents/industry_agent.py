"""
Industry Research Agent
Searches for sector trends, industry outlook, and regulatory environment.
"""
import logging

logger = logging.getLogger(__name__)


class IndustryAgent:
    """Research agent for industry and macro risk signals."""

    POSITIVE_SIGNALS = ["growth", "expansion", "boom", "recovery", "investment", "export growth"]
    NEGATIVE_SIGNALS = ["slowdown", "downturn", "oversupply", "overcapacity", "regulatory risk",
                        "anti-dumping", "import ban", "crisis", "recession"]

    def research(self, industry: str, company_name: str = "") -> dict:
        results = []
        risk_level = "Medium"
        summary = f"Industry analysis for {industry} sector."
        trends = []

        if not industry or industry.lower() in ("unknown", ""):
            return {
                "industry": "Unknown",
                "industry_summary": "Industry not specified — cannot perform sector analysis.",
                "industry_risk_level": "Medium",
                "industry_trends": [],
            }

        queries = [
            f"{industry} industry outlook India 2024",
            f"{industry} sector risks challenges 2024",
        ]

        positive_count = 0
        negative_count = 0

        try:
            from duckduckgo_search import DDGS
            with DDGS() as ddgs:
                for query in queries[:2]:
                    try:
                        for r in ddgs.text(query, max_results=3):
                            title = r.get("title", "")
                            body = r.get("body", "")
                            combined = (title + " " + body).lower()

                            pos = [s for s in self.POSITIVE_SIGNALS if s in combined]
                            neg = [s for s in self.NEGATIVE_SIGNALS if s in combined]
                            positive_count += len(pos)
                            negative_count += len(neg)

                            results.append({
                                "title": title,
                                "snippet": body[:200],
                                "url": r.get("href", ""),
                                "positive_signals": pos,
                                "negative_signals": neg,
                            })
                            trends.extend(neg)
                    except Exception as e:
                        logger.warning(f"DDG search error: {e}")
        except ImportError:
            logger.warning("duckduckgo-search not installed")

        # Assess risk
        if negative_count > positive_count + 2:
            risk_level = "High"
            summary = f"⚠️ {industry} sector facing headwinds: {', '.join(list(set(trends))[:3])}"
        elif negative_count > positive_count:
            risk_level = "Medium"
            summary = f"ℹ️ Mixed outlook for {industry} sector."
        else:
            risk_level = "Low"
            summary = f"✅ {industry} sector shows positive trends."

        return {
            "industry": industry,
            "industry_summary": summary,
            "industry_risk_level": risk_level,
            "industry_trends": results,
            "positive_signals_count": positive_count,
            "negative_signals_count": negative_count,
        }


industry_agent = IndustryAgent()
