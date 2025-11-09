"""
PulseCompass API - Refactored Main Application
Clean, modular FastAPI application with proper separation of concerns
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from dotenv import load_dotenv
import uvicorn

# Import routers
from routers import upload, portfolio, companies, analysis
from routers import health, jobs, metrics, websocket, ranking
from routers import integrity_advanced as integrity
try:
    from routers import validation
    VALIDATION_AVAILABLE = True
except ImportError:
    VALIDATION_AVAILABLE = False
    print("⚠️ Validation router not available - install yfinance")
from middleware.rate_limit import limiter, custom_rate_limit_handler
from slowapi.errors import RateLimitExceeded
from core.logging_config import setup_logging
from core.monitoring import init_sentry

# Load environment variables
load_dotenv()

# Setup logging
setup_logging()

# Initialize monitoring
init_sentry()

# Create FastAPI app
app = FastAPI(
    title="PulseCompass API",
    description="Advanced Stock Market Analysis Backend - Refactored Architecture",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, custom_rate_limit_handler)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js dev server
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers under /api/v1
app.include_router(health.router, prefix="/api/v1")
app.include_router(jobs.router, prefix="/api/v1")
app.include_router(metrics.router, prefix="/api/v1")
app.include_router(websocket.router, prefix="/api/v1")
app.include_router(upload.router, prefix="/api/v1")
app.include_router(portfolio.router, prefix="/api/v1")
app.include_router(companies.router, prefix="/api/v1")
app.include_router(analysis.router, prefix="/api/v1")
app.include_router(integrity.router, prefix="/api/v1")
app.include_router(ranking.router, prefix="/api/v1")

# Include validation router if available
if VALIDATION_AVAILABLE:
    app.include_router(validation.router, prefix="/api/v1")

# Legacy compatibility: mount unversioned routes (temporary)
app.include_router(upload.router, tags=["upload-legacy"])
app.include_router(portfolio.router, tags=["portfolio-legacy"])
app.include_router(companies.router, tags=["companies-legacy"])
app.include_router(analysis.router, tags=["analysis-legacy"])


@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "message": "PulseCompass API is running",
        "version": "2.0.0",
        "status": "healthy",
        "architecture": "refactored",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    from services.ollama_service import OllamaService
    from database.supabase_client import SupabaseClient
    
    ollama_service = OllamaService()
    db_client = SupabaseClient()
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "2.0.0",
        "services": {
            "ollama": await ollama_service.health_check(),
            "database": await db_client.health_check()
        }
    }


@app.get("/api/info")
async def api_info():
    """Get API information and available endpoints"""
    return {
        "title": "PulseCompass API",
        "version": "2.0.0",
        "description": "Advanced Stock Market Analysis Backend",
        "endpoints": {
            "upload": {
                "pdf": "POST /api/v1/upload/pdf",
                "excel": "POST /api/v1/upload/excel",
                "test": "POST /api/v1/upload/test"
            },
            "analysis": {
                "company": "GET /api/v1/company/{company_id}/analysis",
                "query": "POST /api/v1/company/query"
            },
            "portfolio": {
                "default": "GET /api/v1/portfolio",
                "user": "GET /api/v1/portfolio/{user_id}",
                "watchlist": "GET /api/v1/portfolio/watchlist/{user_id}"
            },
            "companies": {
                "watchlist": "GET /api/v1/companies/watchlist",
                "create": "POST /api/v1/companies"
            }
        },
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        }
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
