import asyncio
import json
from aiokafka import AIOKafkaConsumer
from sqlalchemy.exc import SQLAlchemyError
from .database import SessionLocal
from .config import (KAFKA_BOOTSTRAP_SERVERS, INVENTORY_TOPIC, EVENT_ORDER_FAILED, 
                     EVENT_PAYMENT_FAILED, EVENT_PAYMENT_SUCCESSFUL,
                     EVENT_ORDER_FAILED_NOTIFICATION,
                     PAYMENT_TOPIC, ORDER_TOPIC)
from .logger_config import logger
from .kafka_producer import kafka  # Your KafkaProducer instance
from .models import Order
from .config import CONSUMER_ORDER_GROUP
from sqlalchemy import select


MAX_ATTEMPTS = 10
RETRY_DELAY = 5  # seconds

class OrderKafkaConsumer:
    def __init__(self):
        self.consumer = None
        self._connected = False

    async def start(self):
        attempts = 0
        self._connected = False
        while attempts < MAX_ATTEMPTS and not self._connected:
            try:
                self.consumer = AIOKafkaConsumer(
                        INVENTORY_TOPIC,
                        PAYMENT_TOPIC,
                        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                        group_id=CONSUMER_ORDER_GROUP,
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
            self._connected =False
            logger.info("Order Kafka consumer stopped.")

    async def consume(self):
        await self.start()
        try:
            async for msg in self.consumer:
                try:
                    raw_value = msg.value
                    logger.debug(f"Raw Kafka message value: {raw_value!r}")
                    if not raw_value:
                        logger.error("Received empty message from Kafka")
                        continue
                    # Handle both bytes and str
                    if isinstance(raw_value, bytes):
                        raw_value = raw_value.decode('utf-8')
                    event = raw_value      

                    event_type = event.get("event")
                    if event_type == EVENT_ORDER_FAILED:
                        await self.handle_order_failed(event)
                    elif event_type == EVENT_PAYMENT_FAILED:
                        await self.handle_payment_failed(event)
                    elif event_type == EVENT_PAYMENT_SUCCESSFUL:
                        await self.handle_payment_successful(event)    
                    else:
                        logger.info(f"Event: {event_type} is not hanlded")                        
                except json.JSONDecodeError as e:
                    logger.error(f"JSON decode error: {e}")
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
        finally:
            await self.stop()    

    async def handle_order_failed(self, event):
        order_id = event.get("order_id")
        reason = event.get("reason", "Unknown")
        customer_id = event.get("customer_id")
        async with SessionLocal() as session:
            try:
                result = await session.execute(select(Order).where(Order.id == order_id))
                order = result.scalars().first()
                if order:
                    order.status = "FAILED"
                    order.failure_reason = reason
                    await session.commit()
                    logger.info(f"Order {order_id} marked as FAILED due to: {reason}")
                    notification_event = {
                        "event": EVENT_ORDER_FAILED_NOTIFICATION,
                        "order_id": order_id,
                        "customer_id": customer_id,
                        "message": f"Your order {order_id} failed: {reason}"
                    }
                    await kafka.send_event(notification_event, topic=ORDER_TOPIC)
                else:
                    logger.warning(f"Order {order_id} not found for failure handling.")
            except SQLAlchemyError as e:
                logger.error(f"Database error while handling order_failed: {e}")
                await session.rollback()

    async def handle_payment_failed(self, event):
        order_id = event.get("order_id")
        reason = event.get("reason", "Unknown")
        customer_id = event.get("customer_id")
        async with SessionLocal() as session:
            try:
                result = await session.execute(select(Order).where(Order.id == order_id))
                order = result.scalars().first()
                if order:
                    order.status = "PAYMENT_FAILED"
                    order.failure_reason = reason
                    await session.commit()
                    logger.info(f"Order {order_id} marked as PAYMENT_FAILED due to: {reason}")
                    notification_event = {
                        "event": EVENT_ORDER_FAILED_NOTIFICATION,
                        "order_id": order_id,
                        "customer_id": customer_id,
                        "message": f"Your payment for order {order_id} failed: {reason}"
                    }
                    await kafka.send_event(notification_event, topic=ORDER_TOPIC)
                else:
                    logger.warning(f"Order {order_id} not found for payment failure handling.")
            except SQLAlchemyError as e:
                logger.error(f"Database error while handling payment_failed: {e}")
                await session.rollback()

    async def handle_payment_successful(self, event):
        order_id = event.get("order_id")
        async with SessionLocal() as session:
            try:
                result = await session.execute(select(Order).where(Order.id == order_id))
                order = result.scalars().first()
                if order:
                    order.status = "PAID"   # or whatever your paid status is
                    await session.commit()
                    logger.info(f"Order {order_id} marked as PAID after successful payment.")
                else:
                    logger.warning(f"Order {order_id} not found for payment_successful handling.")
            except SQLAlchemyError as e:
                logger.error(f"Database error while handling payment_successful: {e}")
                await session.rollback()


kafka_consumer = OrderKafkaConsumer()