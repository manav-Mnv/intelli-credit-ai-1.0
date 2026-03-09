"""
Ollama LLM Service
Uses locally-running Ollama (llama3/mistral) to enhance CAM sections
with richer, more natural language summaries.
Falls back to template-based text if Ollama is not running.
"""
import logging
import httpx

logger = logging.getLogger(__name__)


class LLMService:
    """Local LLM via Ollama for enhanced CAM generation."""

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3"):
        self.base_url = base_url
        self.model = model
        self._available = None  # None = not checked yet

    def _check_available(self) -> bool:
        if self._available is None:
            try:
                resp = httpx.get(f"{self.base_url}/api/tags", timeout=2.0)
                self._available = resp.status_code == 200
                if self._available:
                    logger.info(f"Ollama available at {self.base_url} with model {self.model}")
            except Exception:
                self._available = False
                logger.warning("Ollama not available — LLM enhancement disabled")
        return self._available

    def generate(self, prompt: str, max_tokens: int = 500) -> str:
        """Generate text from a prompt."""
        if not self._check_available():
            return ""
        try:
            resp = httpx.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"num_predict": max_tokens, "temperature": 0.3},
                },
                timeout=60.0,
            )
            if resp.status_code == 200:
                return resp.json().get("response", "").strip()
        except Exception as e:
            logger.warning(f"Ollama generation failed: {e}")
        return ""

    def enhance_executive_summary(
        self,
        company_name: str,
        industry: str,
        risk_score: float,
        risk_grade: str,
        decision: str,
        loan_amount_cr: float,
        key_risks: list[str],
    ) -> str:
        """Generate an enhanced executive summary using LLM."""
        risks_text = "; ".join(key_risks[:3]) if key_risks else "No major risks identified"
        prompt = f"""You are a senior credit analyst at a bank. Write a concise, professional 3-sentence executive summary for a Credit Appraisal Memo.

Company: {company_name}
Industry: {industry}
Risk Score: {risk_score}/100 ({risk_grade} risk)
Decision: {decision}
Recommended Loan: ₹{loan_amount_cr:.1f} Crore
Key Risks: {risks_text}

Write only the summary, no headers, no bullet points. Be factual and precise:"""

        enhanced = self.generate(prompt, max_tokens=200)
        return enhanced or ""

    def enhance_risk_assessment(
        self,
        company_name: str,
        risk_factors: list[str],
        financial_flags: list[str],
        news_risk: str,
        litigation_risk: str,
    ) -> str:
        """Generate enhanced risk narrative."""
        all_risks = risk_factors + financial_flags
        risks_text = "\n".join(f"- {r}" for r in all_risks[:6]) if all_risks else "- No critical risks"
        prompt = f"""As a credit analyst, write a brief risk assessment paragraph for {company_name}.

Identified risks:
{risks_text}
News risk level: {news_risk}
Litigation risk level: {litigation_risk}

Write 2-3 sentences summarizing the risk profile. Be concise:"""

        enhanced = self.generate(prompt, max_tokens=150)
        return enhanced or ""

    def enhance_industry_outlook(self, industry: str, industry_summary: str) -> str:
        """Generate enhanced industry analysis."""
        prompt = f"""As a credit analyst, write a 2-sentence industry outlook for the {industry} sector in India for 2024-2025.

Research finding: {industry_summary[:300] if industry_summary else 'No specific data'}

Be concise and analytical:"""

        enhanced = self.generate(prompt, max_tokens=120)
        return enhanced or ""


# Singleton
llm_service = LLMService()
