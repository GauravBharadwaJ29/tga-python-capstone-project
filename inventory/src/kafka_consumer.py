import asyncio
import json
from aiokafka import AIOKafkaConsumer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from .models import Inventory
from .database import SessionLocal
from .config import ORDER_TOPIC, KAFKA_BOOTSTRAP_SERVERS, CONSUMER_INVENTORY_GROUP
from .logger_config import logger  # Ensure logger is imported
from .kafka_producer import kafka  # Ensure kafka_producer is imported
from .config import EVENT_ORDER_FAILED, EVENT_ORDER_CREATED, EVENT_PAYMENT_SUCCESSFUL

MAX_ATTEMPTS = 10
RETRY_DELAY = 5  # seconds

class KafkaConsumer:
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
                                group_id=CONSUMER_INVENTORY_GROUP,
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
            logger.info("Kafka consumer stopped.")
    async def consume(self):
        await self.start()
        try:
            async for msg in self.consumer:
                try:
                    logger.info(
                        f"Received message from topic='{msg.topic}', partition={msg.partition}, offset={msg.offset}, "
                        f"key={msg.key}, value(raw)={msg.value!r}"
                    )
                    # event = json.loads(msg.value)
                    event = msg.value
                    logger.debug(f"Parsed event from topic '{msg.topic}': {event}")

                    event_type = event.get("event")
                    if event_type == EVENT_ORDER_CREATED:
                        await self.handle_order_created(event)

                    elif event_type in {EVENT_PAYMENT_SUCCESSFUL, EVENT_ORDER_FAILED}:
                        # These are valid but not handled by this service
                        logger.info(f"Ignored event type: {event_type} from topic '{msg.topic}'")
                    else:
                        # Unknown event type
                        logger.warning(f"Unknown event type: {event_type} from topic '{msg.topic}' - event: {event}")
                except json.JSONDecodeError as e:
                    logger.error(
                        f"JSON decode error on topic '{msg.topic}' at offset {msg.offset}: {e}. Raw value: {msg.value!r}"
                    )
                except Exception as e:
                    logger.error(
                        f"Error processing message from topic '{msg.topic}' at offset {msg.offset}: {e}. Raw value: {msg.value!r}"
                    )
        finally:
            await self.stop()

    async def handle_order_created(self, event):
        items = event.get("order", {}).get("items", [])
        order_id = event.get("order", {}).get("id")
        store_id = event.get("order", {}).get("store_id")
        async with SessionLocal() as session:
            try:
                # First, check all items for sufficient inventory
                for item in items:
                    product_id = item.get("product_id")
                    quantity = item.get("quantity")
                    # store_id = item.get("store_id")

                    if not product_id or not isinstance(quantity, int):
                        logger.warning(f"Invalid item data: {item}")
                        await session.rollback()
                        await kafka.send_event({
                            "event": EVENT_ORDER_FAILED,
                            "order_id": order_id,
                            "reason": f"Invalid item data: {item}"
                        })
                        return

                    result = await session.execute(
                        select(Inventory).where(Inventory.product_id == product_id, Inventory.store_id == store_id)
                    )
                    inventory = result.scalar_one_or_none()

                    if not inventory or inventory.quantity < quantity:
                        logger.warning(f"Insufficient stock for product_id: {product_id}")
                        await session.rollback()
                        await kafka.send_event({
                            "event": EVENT_ORDER_FAILED,
                            "order_id": order_id,
                            "reason": f"Insufficient stock for product_id: {product_id}"
                        })
                        return

                # If all items have sufficient stock, decrement inventory
                for item in items:
                    product_id = item.get("product_id")
                    quantity = item.get("quantity")
                    # store_id = item.get("store_id")
                    result = await session.execute(
                        select(Inventory).where(Inventory.product_id == product_id, Inventory.store_id == store_id)
                    )
                    inventory = result.scalar_one_or_none()
                    inventory.quantity -= quantity

                await session.commit()
                logger.info(f"Inventory updated for order: {order_id}")
            except SQLAlchemyError as e:
                logger.error(f"Database error: {e}")
                await session.rollback()
                await kafka.send_event({
                    "event": EVENT_ORDER_FAILED,
                    "order_id": order_id,
                    "reason": str(e)
                })
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                await session.rollback()
                await kafka.send_event({
                    "event": EVENT_ORDER_FAILED,
                    "order_id": order_id,
                    "reason": str(e)
                })

kafka_consumer = KafkaConsumer()
