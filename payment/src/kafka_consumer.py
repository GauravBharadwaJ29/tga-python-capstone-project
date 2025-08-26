import asyncio
import json
from datetime import datetime
from aiokafka import AIOKafkaConsumer
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from .database import SessionLocal
from .models import Payment, PaymentItem
from .kafka_producer import kafka
from .logger_config import logger
from .config import (
    KAFKA_BOOTSTRAP_SERVERS,
    ORDER_TOPIC,
    PAYMENT_TOPIC,    
    CONSUMER_PAYMENT_GROUP,
    EVENT_PAYMENT_SUCCESSFUL,
    EVENT_PAYMENT_FAILED,
    EVENT_PAYMENT_REFUNDED,
    EVENT_ORDER_CREATED,
    EVENT_ORDER_CANCELLED
)

MAX_ATTEMPTS = 10
RETRY_DELAY = 5  # seconds

class PaymentKafkaConsumer:
    def __init__(self):
        self.consumer = None
        self._connected = False

    async def start(self):
        attempts = 0
        self._connected = False
        while attempts < MAX_ATTEMPTS and not self._connected:
            try:
                self.consumer = AIOKafkaConsumer(
                    ORDER_TOPIC,
                    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                    group_id=CONSUMER_PAYMENT_GROUP,
                    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
                )
                await self.consumer.start()
                # Optionally, perform a healthcheck poll to ensure connectivity
                logger.info("Kafka consumer started successfully")
                self._connected = True
                return
            except Exception as e:
                attempts += 1
                logger.error(f"Kafka consumer connection failed (attempt {attempts}): {e}")
                await asyncio.sleep(RETRY_DELAY)
            finally:
                # If consumer was created but not connected, close it to avoid resource leak
                if self.consumer and not self._connected:
                    logger.warning("Stopping Kafka consumer due to connection failure")
                    await self.consumer.stop()
                    self.consumer = None

        logger.error(f"Failed to connect to Kafka as consumer after {MAX_ATTEMPTS} attempts")
        raise ConnectionError("Could not connect to Kafka as consumer")    

    async def stop(self) -> None:
        if self.consumer:
            await self.consumer.stop()
            self._connected =False
            logger.info("Payment Kafka consumer stopped.")

    async def consume(self) -> None:
        await self.start()
        try:
            async for msg in self.consumer:
                try:
                    event = msg.value
                    event_type = event.get("event")
                    if event_type == EVENT_ORDER_CREATED:
                        await self.handle_order_created(event)
                    elif event_type == EVENT_ORDER_CANCELLED:
                        await self.handle_order_cancelled(event)
                    else:
                        logger.info(f"Event {event_type} and message {event} not handled")  
                except json.JSONDecodeError as e:
                    logger.error(f"JSON decode error: {e}")
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
        finally:
            await self.stop()

    async def handle_order_created(self, event: dict) -> None:
        order = event.get("order", {})
        order_id = order.get("id")
        customer_id = order.get("customer_id")
        amount = order.get("amount")
        payment_method = order.get("payment_method")
        items = order.get("items", [])

        async with SessionLocal() as session:
            try:
                    # Idempotency check: don't double-pay
                result = await session.execute(
                    select(Payment).where(Payment.order_id == order_id)
                )
                existing = result.scalar_one_or_none()
                if existing:
                    logger.info(f"Payment already exists for order: {order_id}")
                    return

                status = "paid"
                transaction_id = f"txn_{order_id}_{int(datetime.utcnow().timestamp())}"

                payment = Payment(
                    order_id=order_id,
                    customer_id=customer_id,
                    amount=amount,
                    payment_method=payment_method,
                    status=status,
                    transaction_id=transaction_id
                )
                session.add(payment)
                await session.flush()

                payment_items = []
                for item in items:
                    payment_item = PaymentItem(
                        payment_id=payment.id,
                        product_id=item["product_id"],
                        quantity=item["quantity"],
                        price=item["price"]
                    )
                    session.add(payment_item)
                    payment_items.append(payment_item)

                await session.commit()
                logger.info(f"Payment processed for order: {order_id}")

                payment_event = {
                    "event": EVENT_PAYMENT_SUCCESSFUL,
                    "order_id": order_id,
                    "customer_id": customer_id,
                    "customer_name": order.get("customer_name"),
                    "customer_contact": order.get("customer_contact"),
                    "delivery_address": order.get("delivery_address"),
                    "amount": amount,
                    "payment_method": payment_method,
                    "transaction_id": transaction_id,
                    "status": status,
                    "items": [
                        {
                            "product_id": pi.product_id,
                            "quantity": pi.quantity,
                            "price": float(pi.price)
                        } for pi in payment_items
                    ]
                }

                await kafka.send_event(payment_event, topic=PAYMENT_TOPIC)
            except Exception as e:
                logger.error(f"Payment processing failed: {e}")
                await session.rollback()
                fail_event = {
                    "event": EVENT_PAYMENT_FAILED,
                    "order_id": order_id,
                    "customer_id": customer_id,
                    "amount": amount,
                    "payment_method": payment_method,
                    "reason": str(e),
                    "status": "failed"
                }
                await kafka.send_event(fail_event, topic=PAYMENT_TOPIC)

    async def handle_order_cancelled(self, event: dict) -> None:
        order_id = event.get("order_id")
        async with SessionLocal() as session:
            try:
                result = await session.execute(
                    select(Payment).where(Payment.order_id == order_id, Payment.status == "paid")
                )
                payment = result.scalar_one_or_none()
                if payment:
                    payment.status = "refunded"
                    await session.commit()
                    logger.info(f"Refund processed for order: {order_id}")
                    refund_event = {
                        "event": EVENT_PAYMENT_REFUNDED,
                        "order_id": order_id,
                        "transaction_id": payment.transaction_id,
                        "status": "refunded"
                    }
                    await kafka.send_event(refund_event, topic=PAYMENT_TOPIC)
                else:
                    logger.info(f"No paid payment found for order: {order_id}")
            except Exception as e:
                logger.error(f"Refund processing failed: {e}")
                await session.rollback()

kafka_consumer = PaymentKafkaConsumer()
