"""
Google Gemini LLM Service
Uses Google's generative AI (Gemini) to enhance CAM sections
with richer, more natural language summaries.
Falls back to empty strings/templates if API key is not provided.
"""
import logging
import os
import google.generativeai as genai  # type: ignore

logger = logging.getLogger(__name__)

class LLMService:
    """Cloud LLM via Google Gemini for enhanced CAM generation."""

    def __init__(self, model: str = "gemini-2.5-flash"):
        self.model_name = model
        self._available = False
        
        # Initialize Gemini API
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            try:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel(self.model_name)
                self._available = True
                logger.info(f"Google Gemini configured with model {self.model_name}")
            except Exception as e:
                logger.warning(f"Failed to configure Gemini: {e}")
        else:
            logger.warning("GEMINI_API_KEY not found in environment variables — LLM enhancement disabled")

    def generate(self, prompt: str, max_tokens: int = 500) -> str:
        """Generate text from a prompt."""
        if not self._available:
            return ""
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=0.3,
                )
            )
            return response.text.strip()
        except Exception as e:
            logger.warning(f"Gemini generation failed: {e}")
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
        short_risks = key_risks[:3]  # type: ignore
        risks_text = "; ".join(short_risks) if short_risks else "No major risks identified"
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
        short_risks = all_risks[:6]  # type: ignore
        risks_text = "\n".join(f"- {r}" for r in short_risks) if short_risks else "- No critical risks"
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
        summary_text = industry_summary[:300] if industry_summary else 'No specific data'  # type: ignore
        prompt = f"""As a credit analyst, write a 2-sentence industry outlook for the {industry} sector in India for 2024-2025.

Research finding: {summary_text}

Be concise and analytical:"""

        enhanced = self.generate(prompt, max_tokens=120)
        return enhanced or ""


# Singleton
llm_service = LLMService()
