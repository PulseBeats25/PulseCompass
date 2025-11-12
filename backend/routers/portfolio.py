"""
Portfolio Router - Handles portfolio and watchlist operations
"""
from fastapi import APIRouter, HTTPException
from database.supabase_client import SupabaseClient

router = APIRouter(prefix="/portfolio", tags=["portfolio"])


@router.get("")
async def get_default_portfolio():
    """Get default portfolio (no user authentication)"""
    try:
        # Return mock portfolio data for now
        return {
            "totalValue": 125000,
            "dayChange": 1250,
            "dayChangePercent": 1.01,
            "positions": 5,
            "alerts": 2
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}")
async def get_portfolio(user_id: str):
    """Get user's portfolio"""
    try:
        db_client = SupabaseClient()
        portfolio = await db_client.get_user_portfolio(user_id)
        return portfolio
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/watchlist/{user_id}")
async def get_watchlist(user_id: str):
    """Get user's watchlist"""
    try:
        db_client = SupabaseClient()
        watchlist = await db_client.get_user_watchlist(user_id)
        return watchlist
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
