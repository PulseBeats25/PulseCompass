import os
from functools import lru_cache
from redis import Redis
from dotenv import load_dotenv

# Load environment from backend/.env when imported (works for worker too)
load_dotenv()

@lru_cache(maxsize=1)
def get_redis() -> Redis:
    url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    # Important: RQ expects binary-safe Redis (no response decoding)
    return Redis.from_url(url)
