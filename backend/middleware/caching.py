"""
Redis Caching Middleware and Decorators
"""
import json
import hashlib
from functools import wraps
from typing import Optional, Callable
from core.redis import get_redis


def cache_key(prefix: str, *args, **kwargs) -> str:
    """Generate cache key from function arguments"""
    key_data = f"{prefix}:{str(args)}:{str(sorted(kwargs.items()))}"
    return f"cache:{hashlib.md5(key_data.encode()).hexdigest()}"


def cached(prefix: str, ttl: int = 300):
    """
    Decorator to cache function results in Redis.
    
    Args:
        prefix: Cache key prefix
        ttl: Time to live in seconds (default 5 minutes)
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            key = cache_key(prefix, *args, **kwargs)
            redis_client = get_redis()
            
            # Try to get from cache
            cached_value = redis_client.get(key)
            if cached_value:
                return json.loads(cached_value)
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Store in cache
            redis_client.setex(key, ttl, json.dumps(result))
            
            return result
        return wrapper
    return decorator


def invalidate_cache(prefix: str, *args, **kwargs):
    """Invalidate specific cache entry"""
    key = cache_key(prefix, *args, **kwargs)
    redis_client = get_redis()
    redis_client.delete(key)


def invalidate_cache_pattern(pattern: str):
    """Invalidate all cache entries matching pattern"""
    redis_client = get_redis()
    keys = redis_client.keys(f"cache:{pattern}*")
    if keys:
        redis_client.delete(*keys)
