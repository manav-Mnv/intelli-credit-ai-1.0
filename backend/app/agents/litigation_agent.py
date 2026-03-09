"""
Litigation Research Agent
Searches for lawsuits, NCLT cases, and legal disputes involving the company.
"""
import logging

logger = logging.getLogger(__name__)


class LitigationAgent:
    """Research agent for legal risk signals."""

    LITIGATION_TERMS = [
        "lawsuit", "nclt", "nclat", "drt", "drat", "arbitration",
        "court case", "legal notice", "contempt", "injunction",
        "writ petition", "high court", "supreme court", "criminal case",
    ]

    def research(self, company_name: str) -> dict:
        results = []
        risk_level = "Low"
        summary = f"No significant litigation found for {company_name}."
        cases_found = []

        queries = [
            f"{company_name} lawsuit court case",
            f"{company_name} NCLT insolvency petition",
            f"{company_name} legal dispute arbitration",
        ]

        try:
            from duckduckgo_search import DDGS
            with DDGS() as ddgs:
                for query in queries[:2]:
                    try:
                        for r in ddgs.text(query, max_results=3):
                            title = r.get("title", "")
                            body = r.get("body", "")
                            combined = (title + " " + body).lower()
                            found_terms = [t for t in self.LITIGATION_TERMS if t in combined]
                            if found_terms:
                                cases_found.extend(found_terms)
                                results.append({
                                    "title": title,
                                    "snippet": body[:200],
                                    "url": r.get("href", ""),
                                    "litigation_terms": found_terms,
                                })
                    except Exception as e:
                        logger.warning(f"DDG search error: {e}")
        except ImportError:
            logger.warning("duckduckgo-search not installed")

        unique_cases = list(set(cases_found))
        if len(unique_cases) >= 3:
            risk_level = "High"
            summary = f"⚠️ Significant litigation risk: {', '.join(unique_cases[:4])}"
        elif unique_cases:
            risk_level = "Medium"
            summary = f"ℹ️ Some litigation indicators: {', '.join(unique_cases[:2])}"

        return {
            "company": company_name,
            "litigation_cases": results,
            "litigation_risk_level": risk_level,
            "litigation_summary": summary,
            "terms_found": unique_cases,
        }


litigation_agent = LitigationAgent()
