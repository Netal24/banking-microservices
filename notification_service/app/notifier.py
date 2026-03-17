import logging, json
from datetime import datetime
logger = logging.getLogger("notification_service")

async def send_email_simulation(to, subject, body):
    logger.info(f"[EMAIL] To:{to} | Subject:{subject} | {body}")

async def send_sms_simulation(phone, message):
    logger.info(f"[SMS] To:{phone} | {message}")

async def store_notification(redis, key, payload):
    entry = {**payload, "sent_at": datetime.utcnow().isoformat()}
    await redis.lpush(key, json.dumps(entry))
    await redis.ltrim(key, 0, 999)
