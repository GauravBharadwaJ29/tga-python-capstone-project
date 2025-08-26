import asyncio
import json
from .logger_config import logger
import httpx
from aiokafka import AIOKafkaConsumer
from .config import (
    KAFKA_BOOTSTRAP_SERVERS,    
    NOTIFICATION_API_URL,
    CONSUMER_BRIDGE_GROUP,
    BILLING_TOPIC,   
    PAYMENT_TOPIC,   
    ORDER_TOPIC,     
    DELIVERY_TOPIC,  
    INVENTORY_TOPIC, 
    PRODUCT_TOPIC,   
    STORE_TOPIC     
)
from .event_mapper import map_event_to_notification

MAX_ATTEMPTS = 10
RETRY_DELAY = 5  # seconds

class NotificationBridge:
    def __init__(self):
        self.consumer = None
        self._connected = False

    async def start(self):
        attempts = 0
        self._connected = False
        while attempts < MAX_ATTEMPTS and not self._connected:
            try:
                self.consumer = AIOKafkaConsumer(
                                                    BILLING_TOPIC,   
                                                    PAYMENT_TOPIC,   
                                                    ORDER_TOPIC,     
                                                    DELIVERY_TOPIC,  
                                                    INVENTORY_TOPIC, 
                                                    PRODUCT_TOPIC,   
                                                    STORE_TOPIC,
                                                    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                                                    group_id=CONSUMER_BRIDGE_GROUP,
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
            logger.info("Notification Bridge Kafka consumer stopped.")

    async def run(self):
        await self.start()
        try:
            async for msg in self.consumer:
                try:
                    event = msg.value
                    logger.info(f"Received event: {event}")
                    notification_payload = map_event_to_notification(event)
                    if notification_payload:
                        async with httpx.AsyncClient() as client:
                            resp = await client.post(NOTIFICATION_API_URL, json=notification_payload)
                            if resp.status_code in (200, 201, 202):
                                logger.info(f"Notification sent: {notification_payload}")
                            else:
                                logger.error(f"Failed to send notification: {resp.status_code} {resp.text}")
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
        finally:
            await self.stop()
