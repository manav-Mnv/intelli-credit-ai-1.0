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

## 💻 Detailed Quick Start (Local Windows)

Follow this step-by-step guide to run the complete IntelliCredit AI system locally on your Windows machine without WSL. 

**Prerequisites:** Ensure you have installed [Python 3.11+](https://www.python.org/downloads/), [Node.js](https://nodejs.org/), and [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/).

### Step 1: Open Docker Desktop
- Search for **Docker Desktop** in your Windows Start Menu and open it.
- **Wait** until the Docker icon in your system tray turns green, or it says "Engine running" in the Docker Desktop UI. This is strictly required before proceeding so Redis and Neo4j can launch!

### Step 2: Open a PowerShell Terminal & Clone the Code
- Open your Windows Start Menu, type `powershell`, and run Windows PowerShell.
- Run the following commands to download the project and enter its folder:
```powershell
git clone https://github.com/manav-Mnv/intelli-credit-ai-1.0.git
cd intelli-credit-ai-1.0
```

### Step 3: Run the Installer Script
- While still in the PowerShell terminal, run the setup script:
```powershell
.\install.ps1
```
- *What this does:* It automatically installs all Python packages for the backend, installs all NPM packages for the frontend, trains your local machine learning model, and creates a template `backend\.env` file for you.

### Step 4: Add Your Credentials
- Open the `backend\.env` file in Notepad or your code editor.
- Fill in your actual API keys (e.g., Supabase, Gemini). **Save and close the file**.

### Step 5: Start the Databases (Redis & Neo4j)
- In the same PowerShell window (ensure you are still exactly inside the main project folder), run the start script:
```powershell
.\start.ps1
```
- Keep this terminal open. It ensures your Docker containers for Redis and Neo4j are spun up. 

### Step 6: Run the Backend (FastAPI)
- Open a **BRAND NEW** Windows PowerShell terminal window.
- Make sure you are inside the main project folder, then navigate to the backend folder and start the API server:
```powershell
cd backend
uvicorn app.main:app --reload --port 8000
```
- *Minimize this terminal and leave it running in the background.*

### Step 7: Run the Frontend (Next.js)
- Open a **THIRD** Windows PowerShell terminal window.
- Make sure you are inside the main project folder, then navigate to the frontend folder and start the web app:
```powershell
cd frontend
npm run dev
```
- *Minimize this terminal and leave it running in the background.*

### Step 8: View the Application
Everything is now running! Open your web browser (Chrome, Edge, etc.) and visit:
- 🌐 **Main Dashboard:**   [http://localhost:3000](http://localhost:3000)
- 📚 **Backend API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
- 🗄️  **Neo4j Database:**   [http://localhost:7474](http://localhost:7474)

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



