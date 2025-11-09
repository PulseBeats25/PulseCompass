"""
Rate Limiting Middleware
"""
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, Response
from starlette.status import HTTP_429_TOO_MANY_REQUESTS

# Create limiter instance
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])


def get_limiter():
    return limiter


# Custom rate limit exceeded handler
async def custom_rate_limit_handler(request: Request, exc: RateLimitExceeded) -> Response:
    return Response(
        content='{"detail":"Rate limit exceeded. Please try again later."}',
        status_code=HTTP_429_TOO_MANY_REQUESTS,
        headers={"Content-Type": "application/json"}
    )
