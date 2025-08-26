import asyncio
from aiokafka import AIOKafkaProducer
from .config import (
    KAFKA_BOOTSTRAP_SERVERS, PRODUCT_TOPIC, 
    KAFKA_RETRY_COUNT, KAFKA_RETRY_DELAY,
    ErrorMessages, SERVICE_NAME as service_name
)
from .logger_config import logger
import json

class KafkaProducer:
    def __init__(self):
        self.producer = None
        self._connected = False
        self.service_name = service_name

    async def start(self):
        for attempt in range(KAFKA_RETRY_COUNT):
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
                logger.warning(
                    f"Kafka not ready, retrying in {KAFKA_RETRY_DELAY} seconds... "
                    f"({attempt+1}/{KAFKA_RETRY_COUNT}): {str(e)}"
                )
                await asyncio.sleep(KAFKA_RETRY_DELAY)
            finally:
                # If producer was created but not connected, close it to avoid resource leak
                if self.producer and not self._connected:
                    logger.warning("Stopping Kafka producer due to connection failure")
                    await self.producer.stop()
                    self.producer = None                 
        logger.error(ErrorMessages.KAFKA_CONNECTION_FAILED.format(KAFKA_RETRY_COUNT))
        raise RuntimeError(ErrorMessages.KAFKA_CONNECTION_FAILED.format(KAFKA_RETRY_COUNT))

    async def stop(self):
        if self.producer:
            await self.producer.stop()

    async def send_event(self, event: dict):
        try:
            if not self.producer:
                await self.start()
            # # Always send as JSON string
            if not isinstance(event, dict):
                raise ValueError("send_event expects a dict, not bytes or string")                   
            await self.producer.send_and_wait(PRODUCT_TOPIC, event)
            logger.debug(f"Event sent to topic {PRODUCT_TOPIC}")
        except Exception as e:
            logger.error(f"Failed to send event: {str(e)}")
            raise RuntimeError(f"Failed to send event to Kafka: {str(e)}")

kafka = KafkaProducer()