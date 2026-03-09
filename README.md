# IntelliCredit AI 🏦

> AI-powered corporate loan analysis system. Upload financial documents → get risk scores and loan recommendations in minutes.

## Quick Start

```bash
# 1. Clone & configure
cp .env.example .env
# Edit .env with your Supabase credentials

# 2. Run everything with Docker
docker compose up --build

# 3. Open the dashboard
open http://localhost:3000
```

## Manual Setup (No Docker)

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

## System Flow

```
Upload Documents → Extract Financial Data → Calculate Ratios
→ ML Risk Score → Research Agents → AI Decision → CAM Report
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14, Tailwind CSS, Recharts |
| Backend | FastAPI, Python 3.10+ |
| Task Queue | Celery + Redis |
| ML/AI | XGBoost, FinBERT (keyword NLP), LangChain |
| Vector DB | ChromaDB |
| Graph DB | Neo4j |
| Main DB | Supabase (PostgreSQL) |
| Infra | Docker, Docker Compose |

## API Docs

Once backend is running: http://localhost:8000/docs

## Project Structure

```
intelli-credit-ai-1/
├── backend/          # FastAPI + Celery workers
│   ├── app/
│   │   ├── api/      # REST endpoints
│   │   ├── services/ # Business logic engines
│   │   ├── agents/   # Research agents
│   │   └── tasks/    # Celery tasks
│   └── requirements.txt
├── frontend/         # Next.js dashboard
├── ml/               # ML models
└── docker-compose.yml
```
