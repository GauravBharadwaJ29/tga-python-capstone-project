import asyncio
import json
from aiokafka import AIOKafkaProducer
from .config import (
    KAFKA_BOOTSTRAP_SERVERS, PAYMENT_TOPIC, 
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
                await self.producer.send_and_wait(
                    "healthcheck_topic",
                    {"healthcheck": True, "service": self.service_name}
                )                           
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
                if self.producer and not self._connected:
                    logger.warning("Stopping Kafka producer due to connection failure")
                    await self.producer.stop()
                    self.producer = None   
        logger.error("Failed to connect to Kafka after 10 attempts")
        raise ConnectionError("Could not connect to Kafka")                                    

    async def stop(self):
        if self.producer:
            await self.producer.stop()
            self._connected = False



    async def send_event(self, event: dict, topic: str = None):
        topic = topic or PAYMENT_TOPIC

        # Defensive type check
        if not isinstance(event, dict):
            logger.error(
                "send_event expects a dict, not bytes or string",
                extra={
                    "topic": topic,
                    "event_type": type(event).__name__,
                    "event_repr": repr(event)
                }
            )
            raise ValueError("send_event expects a dict, not bytes or string")

        # Log the outgoing event in detail before sending
        logger.info(
            f"Preparing to send event to Kafka | topic={topic} event_type={event.get('event')} order_id={event.get('order_id')} payload={event}"
        )

        if not self.producer or not self._connected:
            logger.info("Producer not connected, attempting to start", extra={"topic": topic})
            await self.start()
        try:
            await self.producer.send_and_wait(topic, event)
            logger.info(
                "Event sent to topic",
                extra={
                    "topic": topic,
                    "event_type": event.get("event"),
                    "order_id": event.get("order_id"),
                    "payload": event
                }
            )
        except Exception as e:
            logger.error(
                "Failed to send event to topic",
                extra={
                    "topic": topic,
                    "event_type": event.get("event"),
                    "order_id": event.get("order_id"),
                    "payload": event,
                    "error": str(e),
                    "error_type": type(e).__name__
                }
            )
            raise RuntimeError(ErrorMessages.KAFKA_EVENT_FAILED.format(str(e)))
        
kafka = KafkaProducer()
