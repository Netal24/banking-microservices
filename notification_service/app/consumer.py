import json, logging
import aio_pika
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from common.rabbit import get_rabbit_connection
from common.redis_client import get_redis
from .notifier import send_email_simulation, send_sms_simulation, store_notification

logger = logging.getLogger("notification_service")

async def handle_txn(message: aio_pika.IncomingMessage):
    async with message.process(requeue=False):
        try:
            d = json.loads(message.body)
            txn_id = d.get("transaction_id")
            amount = d.get("amount_cents", 0) / 100.0
            currency = d.get("currency", "INR")
            txn_type = d.get("transaction_type", "transfer")
            await send_email_simulation("user@example.com", f"Transaction #{txn_id} Successful", f"{txn_type} of {currency} {amount:,.2f} completed")
            await send_sms_simulation("+91-XXXXXXXXXX", f"{currency} {amount:,.2f} {txn_type} done. Ref:{txn_id}")
            redis = await get_redis()
            acct_key = d.get("source_account_id", d.get("destination_account_id", "unknown"))
            await store_notification(redis, f"notifications:account:{acct_key}", {"type": "transaction_success", **d})
        except Exception as e:
            logger.error(f"Error: {e}", exc_info=True)

async def handle_fraud(message: aio_pika.IncomingMessage):
    async with message.process(requeue=False):
        try:
            d = json.loads(message.body)
            txn_id = d.get("transaction_id")
            alerts = "; ".join(d.get("alerts", []))
            amount = d.get("amount_cents", 0) / 100.0
            currency = d.get("currency", "INR")
            await send_email_simulation("security@bank.com", f"FRAUD ALERT txn #{txn_id}", f"Amount:{currency} {amount:,.2f} | Alerts:{alerts}")
            await send_sms_simulation("+91-SECURITY", f"FRAUD txn #{txn_id}: {alerts[:80]}")
            redis = await get_redis()
            await store_notification(redis, "notifications:fraud_alerts", {"type": "fraud_alert", **d})
        except Exception as e:
            logger.error(f"Error: {e}", exc_info=True)

async def start_consumers():
    conn = await get_rabbit_connection()
    channel = await conn.channel()
    await channel.set_qos(prefetch_count=10)
    txn_ex = await channel.declare_exchange("transactions", aio_pika.ExchangeType.FANOUT, durable=True)
    fraud_ex = await channel.declare_exchange("fraud", aio_pika.ExchangeType.FANOUT, durable=True)
    txn_q = await channel.declare_queue("notification_txn_queue", durable=True)
    fraud_q = await channel.declare_queue("notification_fraud_queue", durable=True)
    await txn_q.bind(txn_ex)
    await fraud_q.bind(fraud_ex)
    await txn_q.consume(handle_txn)
    await fraud_q.consume(handle_fraud)
    logger.info("Notification consumers ready")
