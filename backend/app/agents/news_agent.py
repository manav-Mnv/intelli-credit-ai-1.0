"""
News Research Agent
Searches for company news, fraud cases, and scandals using DuckDuckGo.
"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class NewsAgent:
    """Research agent that searches for company news and risk signals."""

    RISK_TERMS = [
        "fraud", "scam", "investigation", "penalty", "fine",
        "arrested", "raid", "laundering", "default", "npa",
        "insolvency", "winding up", "bankrupt",
    ]

    def research(self, company_name: str) -> dict:
        """Search for news about the company and assess sentiment."""
        results = []
        risk_level = "Low"
        summary = f"No significant adverse news found for {company_name}."
        risk_keywords_found = []

        queries = [
            f"{company_name} fraud investigation",
            f"{company_name} financial scandal",
            f"{company_name} RBI penalty SEBI",
            f"{company_name} NPA default bank",
        ]

        try:
            from duckduckgo_search import DDGS
            with DDGS() as ddgs:
                for query in queries[:2]:  # Limit queries to avoid rate limits
                    try:
                        for r in ddgs.text(query, max_results=3):
                            title = r.get("title", "")
                            body = r.get("body", "")
                            url = r.get("href", "")
                            combined = (title + " " + body).lower()

                            # Check for risk keywords in result
                            found = [kw for kw in self.RISK_TERMS if kw in combined]
                            results.append({
                                "title": title,
                                "snippet": body[:200] if body else "",
                                "url": url,
                                "risk_keywords": found,
                            })
                            risk_keywords_found.extend(found)
                    except Exception as e:
                        logger.warning(f"DDG search failed for '{query}': {e}")

        except ImportError:
            logger.warning("duckduckgo-search not installed — using demo mode")
            results = [{"title": "Demo mode — install duckduckgo-search", "snippet": "", "url": "", "risk_keywords": []}]

        # Assess risk level
        unique_risks = list(set(risk_keywords_found))
        if len(unique_risks) >= 3:
            risk_level = "High"
            summary = f"⚠️ Multiple risk signals found for {company_name}: {', '.join(unique_risks[:5])}"
        elif len(unique_risks) >= 1:
            risk_level = "Medium"
            summary = f"ℹ️ Some risk signals found for {company_name}: {', '.join(unique_risks[:3])}"

        return {
            "company": company_name,
            "news_articles": results,
            "news_risk_level": risk_level,
            "news_summary": summary,
            "risk_keywords_found": unique_risks,
        }


news_agent = NewsAgent()
