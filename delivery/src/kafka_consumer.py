import os
import json
from .logger_config import logger
import asyncio
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from sqlalchemy import select
from sqlalchemy.orm import Session
from .kafka_producer import kafka

from .database import SessionLocal
from .models import Delivery, DeliveryStatus
from .config import (
              KAFKA_BOOTSTRAP_SERVERS, ORDER_TOPIC, PAYMENT_TOPIC, 
              CONSUMER_DELIVERY_GROUP,EVENT_PAYMENT_SUCCESSFUL,
              EVENT_ORDER_CANCELLED, EVENT_ORDER_DELETED, EVENT_PAYMENT_REFUNDED,
              EVENT_DELIVERY_CREATED, EVENT_DELIVERY_CANCELLED
          )

MAX_ATTEMPTS = 10
RETRY_DELAY = 5  # seconds

class DeliveryKafkaConsumer:
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
                                    PAYMENT_TOPIC,
                                    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                                    group_id=CONSUMER_DELIVERY_GROUP,
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
        await self.consumer.stop()
        self._connected = False
        # await self.producer.stop()
        logger.info("DeliveryKafkaConsumer stopped")

    async def consume(self):
        await self.start()
        try:
            async for msg in self.consumer:
                event = msg.value
                logger.info(f"Received event: {event}")
                await self.handle_event(event)
        except Exception as e:
            logger.exception(f"Error in consumer loop: {e}")
        finally:
            await self.stop()

    async def handle_event(self, event):
        event_type = event.get("event")
        order_id = event.get("order_id")
        customer_id = event.get("customer_id")
        delivery_address = event.get("delivery_address")
        items = event.get("items", [])

        async with SessionLocal() as db:
            try:
                if event_type == EVENT_PAYMENT_SUCCESSFUL:
                    result = await db.execute(select(Delivery).where(Delivery.order_id == order_id))
                    delivery = result.scalars().first()
                    if not delivery:
                        delivery = Delivery(
                            order_id=order_id,
                            customer_id=customer_id,
                            delivery_address=delivery_address,
                            status=DeliveryStatus.PENDING,
                        )
                        db.add(delivery)
                        await db.commit()
                        logger.info(f"Created delivery for order {order_id}")
                        await self.emit_notification(delivery, EVENT_DELIVERY_CREATED)
                    else:
                        logger.info(f"Delivery already exists for order {order_id}, skipping creation.")

                elif event_type in (EVENT_ORDER_CANCELLED, EVENT_ORDER_DELETED, EVENT_PAYMENT_REFUNDED):
                    result = await db.execute(select(Delivery).where(Delivery.order_id == order_id))
                    delivery = result.scalars().first()
                    if delivery and delivery.status not in (DeliveryStatus.CANCELLED, DeliveryStatus.DELIVERED):
                        delivery.status = DeliveryStatus.CANCELLED
                        await db.commit()
                        logger.info(f"Cancelled delivery for order {order_id}")
                        await self.emit_notification(delivery, EVENT_DELIVERY_CANCELLED)
                    else:
                        logger.info(f"No active delivery to cancel for order {order_id}")

                else:
                    logger.info(f"Ignoring event type: {event_type}")

            except Exception as e:
                logger.exception(f"Error handling event {event_type} for order {order_id}: {e}")


    async def emit_notification(self, delivery, event_type):
        # TODO: Implement notification logic here
        pass

kafka_consumer = DeliveryKafkaConsumer()