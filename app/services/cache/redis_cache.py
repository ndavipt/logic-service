import json
from typing import Any, Optional
import redis
from datetime import timedelta
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# Create a Redis connection with error handling
try:
    redis_client = redis.from_url(settings.REDIS_URL)
    # Test connection
    redis_client.ping()
    logger.info("Connected to Redis successfully")
except redis.ConnectionError:
    logger.warning("Could not connect to Redis. Running without cache.")
    redis_client = None
except Exception as e:
    logger.warning(f"Redis initialization error: {e}. Running without cache.")
    redis_client = None

def get_cache(key: str) -> Optional[Any]:
    """
    Get a value from the cache.
    """
    if redis_client is None:
        return None
    
    try:
        value = redis_client.get(key)
        if value:
            return json.loads(value)
    except Exception as e:
        logger.warning(f"Cache get error: {e}")
    
    return None

def set_cache(key: str, value: Any, expire_seconds: int = 3600) -> None:
    """
    Set a value in the cache with an expiration time.
    """
    if redis_client is None:
        return
    
    try:
        redis_client.setex(
            key,
            timedelta(seconds=expire_seconds),
            json.dumps(value)
        )
    except Exception as e:
        logger.warning(f"Cache set error: {e}")

def delete_cache(key: str) -> None:
    """
    Delete a value from the cache.
    """
    if redis_client is None:
        return
    
    try:
        redis_client.delete(key)
    except Exception as e:
        logger.warning(f"Cache delete error: {e}")

def clear_cache_pattern(pattern: str) -> None:
    """
    Clear all cache keys matching a pattern.
    """
    if redis_client is None:
        return
    
    try:
        for key in redis_client.scan_iter(pattern):
            redis_client.delete(key)
    except Exception as e:
        logger.warning(f"Cache clear pattern error: {e}")