import json
import aio_pika
from .config import settings

_connection = None

async def get_rabbit_connection():
    global _connection
    if _connection is None or _connection.is_closed:
        _connection = await aio_pika.connect_robust(str(settings.RABBIT_DSN))
    return _connection

async def publish_event(exchange_name: str, routing_key: str, payload: dict):
    conn = await get_rabbit_connection()
    async with conn.channel() as channel:
        exchange = await channel.declare_exchange(
            exchange_name, aio_pika.ExchangeType.FANOUT, durable=True
        )
        await exchange.publish(
            aio_pika.Message(
                body=json.dumps(payload).encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            ),
            routing_key=routing_key,
        )
