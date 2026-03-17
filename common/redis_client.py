import redis.asyncio as aioredis
from .config import settings

_redis = None

async def get_redis():
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(
            str(settings.REDIS_DSN),
            decode_responses=True,
            encoding="utf-8",
        )
    return _redis
