# IntelliCredit AI 🏦

> **Transmuting raw financial data into sharp, automated credit intelligence.**

IntelliCredit AI is a high-performance, containerized platform designed for modern corporate underwriting. It processes multi-page financial documents (PDF, XLSX, DOCX) through a sophisticated 4-layer risk engine to generate comprehensive Credit Appraisal Memos (CAM).

---

## 🚀 Hackathon Highlights

- **4-Layer Risk Convergence**: Orchestrates Rule-Based Ratios (45%), XGBoost ML Models (25%), NLP Sentiment Analysis (20%), and Sector Risk Assessment (10%).
- **Autonomous Research Agents**: Custom LangChain agents for specialized Litigation, News, Industry Trend, and Knowledge Graph (Neo4j) research.
- **Explainable AI (XAI)**: Native SHAP integration to provide transparent justifications for credit decisions, moving beyond "black-box" models.
- **Enterprise-Ready Pipeline**: Full document ingestion pipeline (OCR, table extraction) backed by a robust RAG system (ChromaDB).

---

## 🛠️ Tech Stack

| Component | Technology |
|:--- |:--- |
| **Frontend** | Next.js 14 (App Router), TypeScript, Tailwind CSS, Recharts |
| **Backend** | FastAPI, Python 3.11, Celery + Redis |
| **Databases** | Supabase (PostgreSQL), ChromaDB (Vector), Neo4j (Graph) |
| **AI/ML** | XGBoost + SHAP, Gemini LLM, LangChain, FinBERT |
| **Document Proc** | PyMuPDF, Camelot, Tesseract OCR |
| **DevOps** | Docker, Docker Compose |

---

## 📥 Quick Start (Dockerized)

Ensure you have [Docker](https://www.docker.com/) installed and running.

```bash
# 1. Clone & Setup
git clone https://github.com/manav-Mnv/intelli-credit-ai-1.0.git
cd intelli-credit-ai-1.0
cp .env.example .env

# 2. Launch Stack
docker-compose up --build -d

# 3. Access Dashboard
# Head to http://localhost:3000 to see the interface
```

*Note: Edit `.env` with your own credentials if you're not using the default emulator settings.*

---

## 🏗️ System Architecture

1.  **Ingestion Engine**: Extracts structured tables and text from heterogeneous financial documents.
2.  **Intelligence Engines**: Runs parallel calculations for 10+ financial ratios (DSCR, TOL/TNW, etc.).
3.  **Risk Synergy**: Fuses numeric analysis with qualitative sentiment and external research.
4.  **Final Recommendation**: Generates a standardized CAM report with a definitive Approve/Conditional/Reject decision.

---

## 📁 Repository Map

```text
├── backend/          # FastAPI gateway & Celery workers
├── frontend/         # Next.js 14 dashboard
├── ml/               # Training notebooks & model weights
├── webpage/          # Showcase/Architecture landing pages
└── docker-compose.yml # Full ecosystem orchestration
```

---

## 📝 License

Built for the Hackathon. Distributed under the MIT License.



