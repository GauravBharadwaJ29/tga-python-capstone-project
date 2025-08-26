import asyncio
from aiokafka import AIOKafkaProducer
from .config import KAFKA_BOOTSTRAP_SERVERS, INVENTORY_TOPIC,SERVICE_NAME as service_name, ORDER_TOPIC
from .logger_config import logger
import json

MAX_ATTEMPTS = 10
RETRY_DELAY = 5  # seconds

class KafkaProducer:
    def __init__(self):
        self.producer = None
        self._connected = False
        self.service_name = service_name

    async def start(self):
        attempts = 0
        while attempts < MAX_ATTEMPTS and not self._connected: 
            try:
                self.producer = AIOKafkaProducer(
                    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                    value_serializer=lambda v: json.dumps(v).encode("utf-8")
                )
                await self.producer.start()
                await self.producer.send_and_wait("healthcheck_topic", {"healthcheck": True, "service": self.service_name})
                self._connected = True
                logger.info("Kafka producer started successfully")                
                return
            except Exception as e:
                attempts += 1
                logger.error(f"Kafka connection failed (attempt {attempts}): {e}")
                await asyncio.sleep(RETRY_DELAY)
            finally:
                # If producer was created but not connected, close it to avoid resource leak
                if self.producer and not self._connected:
                    logger.warning("Stopping Kafka producer due to connection failure")
                    await self.producer.stop()
                    self.producer = None                   
                
                
        logger.error("Failed to connect to Kafka after 10 attempts")
        raise ConnectionError("Could not connect to Kafka")

    async def stop(self):
        if self.producer:
            await self.producer.stop()

    async def send_event(self, event: dict):
        if not self.producer:
            await self.start()
        # # Always send as JSON string
        logger.debug(f"Before isinstance check : About to send event to Kafka: type={type(event)}, value={event!r}, topic=INVENTORY_TOPIC")
        if not isinstance(event, dict):
            raise ValueError("send_event expects a dict, not bytes or string")   
        logger.debug(f"About to send event to Kafka: type={type(event)}, value={event!r}, topic=INVENTORY_TOPIC")                 
        await self.producer.send_and_wait(INVENTORY_TOPIC, event)

kafka = KafkaProducer()
