from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import logging

from app.config import settings
from app.api import documents, financials, risk, research, cam, companies, graph

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="IntelliCredit AI",
    description="AI-powered corporate loan analysis system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(companies.router, prefix="/api/companies", tags=["Companies"])
app.include_router(documents.router, prefix="/api/documents", tags=["Documents"])
app.include_router(financials.router, prefix="/api/financials", tags=["Financials"])
app.include_router(risk.router, prefix="/api/risk", tags=["Risk"])
app.include_router(research.router, prefix="/api/research", tags=["Research"])
app.include_router(cam.router, prefix="/api/cam", tags=["CAM"])
app.include_router(graph.router, prefix="/api/graph", tags=["Graph Risk"])

# Serve uploads as static files
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": "IntelliCredit AI Backend",
        "version": "1.0.0",
    }


@app.get("/", tags=["Health"])
async def root():
    return {
        "message": "IntelliCredit AI API",
        "docs": "/docs",
        "health": "/health",
    }
