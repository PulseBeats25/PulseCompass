"""
Companies Router - Handles company-related operations
"""
from fastapi import APIRouter, HTTPException
from typing import Optional
from database.supabase_client import SupabaseClient

router = APIRouter(prefix="/companies", tags=["companies"])

# Initialize database client
db_client = SupabaseClient()


@router.get("/watchlist")
async def get_default_watchlist():
    """Get default watchlist (no user authentication)"""
    try:
        # Return mock watchlist data for now
        return []
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("")
async def create_company(name: str, ticker: str, sector: Optional[str] = None):
    """Create a new company"""
    try:
        company_id = await db_client.create_company(name, ticker, sector)
        return {"company_id": company_id, "message": "Company created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
