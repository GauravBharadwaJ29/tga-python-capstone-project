import asyncio
import json
from datetime import datetime, timedelta
from aiokafka import AIOKafkaConsumer
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from .database import SessionLocal
from .config import (
    PAYMENT_TOPIC, ORDER_TOPIC, KAFKA_BOOTSTRAP_SERVERS,
    EVENT_PAYMENT_SUCCESSFUL, EVENT_PAYMENT_FAILED, EVENT_ORDER_CANCELLED,
    EVENT_INVOICE_GENERATED, EVENT_INVOICE_FAILED, EVENT_INVOICE_CANCELLED,
    CONSUMER_BILLING_GROUP
)
from .logger_config import logger
from .kafka_producer import kafka  # Your KafkaProducer instance
from .config import SERVICE_NAME as service_name
from .models import Billing, BillingItem

MAX_ATTEMPTS = 10
RETRY_DELAY = 5  # seconds

class BillingKafkaConsumer:
    def __init__(self):
        self.consumer = None
        self._connected = False

    async def start(self):
        attempts = 0
        self._connected = False
        while attempts < MAX_ATTEMPTS and not self._connected:
            try:
                self.consumer = AIOKafkaConsumer(
                    PAYMENT_TOPIC,
                    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                    group_id=CONSUMER_BILLING_GROUP,
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
 

    async def stop(self):
        if self.consumer:
            await self.consumer.stop()
            self._connected = False
            logger.info("Billing Kafka consumer stopped.")

    async def consume(self):       
        try:
            await self.start()
            logger.debug("consume start")
            async for msg in self.consumer:
                try:
                    event =  msg.value
                    event_type = event.get("event")
                    logger.debug(f"Recieved message: {event}, event_type: {event_type}")
                    if event_type ==  EVENT_PAYMENT_SUCCESSFUL:
                        await self.handle_payment_successful(event)
                    elif event_type ==  EVENT_PAYMENT_FAILED:
                        await self.handle_payment_failed(event)
                    elif event_type ==  EVENT_ORDER_CANCELLED:
                        await self.handle_order_cancelled(event)
                    else:
                        logger.info(f"Event {event_type} and message {event} not handled")                          
                except json.JSONDecodeError as e:
                    logger.error(f"JSON decode error: {e}")
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
        finally:
            await self.stop()

    async def handle_payment_failed(self, event):
        order_id = event.get("order_id")
        amount = event.get("amount")
        customer_id = event.get("customer_id")
        customer_name = event.get("customer_name")
        payment_method = event.get("payment_method")
        async with SessionLocal() as session:
            try:
                bill = Billing(
                    order_id=order_id,
                    customer_id=customer_id,
                    customer_name=customer_name,
                    payment_method=payment_method,
                    amount=amount,
                    status="failed",
                    billing_date=datetime.utcnow()
                )
                session.add(bill)
                await session.commit()
                logger.info(f"Invoice marked as failed for order: {order_id}")
                await kafka.send_event({
                    "event":  EVENT_INVOICE_FAILED,
                    "order_id": order_id,
                    "bill_id": bill.id,
                    "amount": amount,
                    "status": "failed"
                })
            except Exception as e:
                logger.error(f"Error recording failed invoice: {e}")
                await session.rollback()


    async def handle_order_cancelled(self, event):
        order_id = event.get("order_id")
        async with SessionLocal() as session:
            try:
                # Find all non-cancelled bills for this order
                result = await session.execute(
                    select(Billing).where(Billing.order_id == order_id, Billing.status != "cancelled")
                )
                bills = result.scalars().all()
                if bills:
                    for bill in bills:
                        bill.status = "cancelled"
                    await session.commit()
                    logger.info(f"All invoices cancelled for order: {order_id}")
                    # Optionally, emit a cancellation event for each bill
                    for bill in bills:
                        await kafka.send_event({
                            "event":  EVENT_INVOICE_CANCELLED,
                            "order_id": order_id,
                            "bill_id": bill.id,
                            "status": "cancelled"
                        })
                else:
                    logger.info(f"No active invoice to cancel for order: {order_id}")
            except Exception as e:
                logger.error(f"Error cancelling invoice: {e}")
                await session.rollback()

    async def handle_payment_successful(self, event):
        logger.info(f"Received payment_successful event: {event}")
        order_id = event.get("order_id")
        amount = event.get("amount")
        items = event.get("items", [])
        customer_id = event.get("customer_id")
        customer_name = event.get("customer_name")
        payment_method = event.get("payment_method")

        # All DB operations are inside this block
        async with SessionLocal() as session:
            # Example: Check for an existing failed bill
            result = await session.execute(
            select(Billing).where(Billing.order_id == order_id)
            )
            existing = result.scalar_one_or_none()
            if existing:
                logger.info(f"Bill for order {order_id} already exists (id={existing.id}, status={existing.status}), skipping duplicate.")
                return

            try:
                bill = Billing(
                    order_id=order_id,
                    customer_id=customer_id,
                    customer_name=customer_name,
                    payment_method=payment_method,
                    amount=amount,
                    status="paid",
                    billing_date=datetime.utcnow()
                )
                session.add(bill)
                await session.flush()  # To get bill.id

                for item in items:
                    bill_item = BillingItem(
                        billing_id=bill.id,
                        product_id=item["product_id"],
                        quantity=item["quantity"],
                        price=item["price"]
                    )
                    session.add(bill_item)

                await session.commit()
                logger.info(f"Invoice generated for order: {order_id}")

                await kafka.send_event({
                    "event":  EVENT_INVOICE_GENERATED,
                    "order_id": order_id,
                    "bill_id": bill.id,
                    "amount": amount,
                    "status": "paid"
                })
            except SQLAlchemyError as e:
                logger.error(f"Database error: {e}")
                await session.rollback()
                await kafka.send_event({
                    "event":   EVENT_INVOICE_FAILED,
                    "order_id": order_id,
                    "reason": str(e)
                })
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                await session.rollback()
                await kafka.send_event({
                    "event":       EVENT_INVOICE_FAILED,
                    "order_id": order_id,
                    "reason": str(e)
                })
           

kafka_consumer = BillingKafkaConsumer()