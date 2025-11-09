from fastapi import APIRouter
from core.redis import get_redis

router = APIRouter()

@router.get("/health/redis")
async def health_redis():
    r = get_redis()
    try:
        ok = r.ping()
        return {"ok": ok}
    except Exception as e:
        return {"ok": False, "error": str(e)}
