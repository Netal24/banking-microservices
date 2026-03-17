import json, asyncio, logging
import aio_pika
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from common.rabbit import get_rabbit_connection, publish_event
from .rules import FraudContext, evaluate

logger = logging.getLogger("fraud_service")

async def handle(message: aio_pika.IncomingMessage):
    async with message.process(requeue=False):
        try:
            p = json.loads(message.body)
            ctx = FraudContext(
                transaction_id=p.get("transaction_id", 0),
                source_account_id=p.get("source_account_id", 0),
                destination_account_id=p.get("destination_account_id", 0),
                amount_cents=p.get("amount_cents", 0),
                currency=p.get("currency", "INR"),
                transaction_type=p.get("transaction_type", "transfer"),
                user_id=p.get("user_id"),
            )
            alerts = evaluate(ctx)
            if alerts:
                logger.warning(f"FRAUD txn={ctx.transaction_id} alerts={alerts}")
                await publish_event("fraud", "fraud.alert", {"transaction_id": ctx.transaction_id, "source_account_id": ctx.source_account_id, "amount_cents": ctx.amount_cents, "currency": ctx.currency, "alerts": alerts, "user_id": ctx.user_id})
        except Exception as e:
            logger.error(f"Error: {e}", exc_info=True)

async def start_consumer():
    conn = await get_rabbit_connection()
    channel = await conn.channel()
    await channel.set_qos(prefetch_count=10)
    exchange = await channel.declare_exchange("transactions", aio_pika.ExchangeType.FANOUT, durable=True)
    queue = await channel.declare_queue("fraud_detection_queue", durable=True)
    await queue.bind(exchange)
    await queue.consume(handle)
    logger.info("Fraud consumer ready")
