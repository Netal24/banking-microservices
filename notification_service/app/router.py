import json
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from fastapi import APIRouter, Query
from common.redis_client import get_redis

router = APIRouter(prefix="/notification", tags=["Notification Service"])

@router.get("/inbox/{account_id}")
async def inbox(account_id: int, limit: int = Query(default=20, le=100)):
    redis = await get_redis()
    raw = await redis.lrange(f"notifications:account:{account_id}", 0, limit - 1)
    return [json.loads(r) for r in raw]

@router.get("/fraud-alerts")
async def fraud_alerts(limit: int = Query(default=20, le=100)):
    redis = await get_redis()
    raw = await redis.lrange("notifications:fraud_alerts", 0, limit - 1)
    return [json.loads(r) for r in raw]
