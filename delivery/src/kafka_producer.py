import asyncio
import json
from typing import Any, Dict
from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaConnectionError, KafkaTimeoutError
from .config import KAFKA_BOOTSTRAP_SERVERS, DELIVERY_TOPIC, SERVICE_NAME
from .logger_config import logger
from .exceptions import KafkaProducerError

MAX_ATTEMPTS = 10
RETRY_DELAY = 5  # seconds

class KafkaProducer:
    def __init__(self, max_retries: int = MAX_ATTEMPTS, retry_delay: int = RETRY_DELAY):
        self.producer = None
        self._connected = False
        self.service_name = SERVICE_NAME

    async def start(self) -> None:
        attempts = 0
        while attempts < MAX_ATTEMPTS and not self._connected:
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
                logger.info("Kafka producer started successfully", extra={"attempt": attempts + 1})
                return
            except KafkaConnectionError as e:
                logger.warning(
                    "Kafka connection attempt failed",
                    extra={"attempt": attempts, "max_retries": MAX_ATTEMPTS, "error": str(e)}
                )
                attempts += 1
                logger.error(f"Kafka connection failed (attempt {attempts}): {e}")
                await asyncio.sleep(RETRY_DELAY)
            except Exception as e:
                attempts += 1
                logger.error(
                    "Unexpected error during Kafka producer startup",
                    extra={"error": str(e), "error_type": type(e).__name__}
                )
                await asyncio.sleep(RETRY_DELAY)
            finally:
                if self.producer and not self._connected:
                    logger.warning("Stopping Kafka producer due to connection failure")
                    await self.producer.stop()
                    self.producer = None
        logger.error("Failed to connect to Kafka after 10 attempts")
        raise ConnectionError("Could not connect to Kafka")

    async def stop(self) -> None:
        if self.producer:
            try:
                await self.producer.stop()
                self._connected = False
                logger.info("Kafka producer stopped successfully")
            except Exception as e:
                logger.error(
                    "Error stopping Kafka producer",
                    extra={"error": str(e), "error_type": type(e).__name__}
                )
                raise KafkaProducerError("Failed to stop Kafka producer") from e

import json
from typing import Dict, Any

async def send_event(self, event: Dict[str, Any], topic: str = None) -> None:
    topic = topic or DELIVERY_TOPIC

    # Defensive type check
    if not isinstance(event, dict):
        logger.error(
            "send_event called with non-dict event",
            extra={"topic": topic, "event_type": type(event), "event": repr(event)}
        )
        raise ValueError("send_event expects a dict, not bytes or string")

    # Log the outgoing message in detail
    logger.info(
        f"Preparing to send event to Kafka topic='{topic}'",
        extra={
            "topic": topic,
            "event_type": event.get("event"),
            "delivery_id": event.get("delivery_id"),
            "event_payload": event,
            "event_payload_json": json.dumps(event, ensure_ascii=False)
        }
    )

    if not self.producer or not self._connected:
        logger.info("Producer not connected, attempting to start", extra={"topic": topic})
        await self.start()
    try:
        await self.producer.send_and_wait(topic, event)
        logger.info(
            f"Event sent successfully to Kafka topic='{topic}'",
            extra={
                "topic": topic,
                "event_type": event.get("event"),
                "delivery_id": event.get("delivery_id"),
                "event_payload": event
            }
        )
    except KafkaTimeoutError as e:
        logger.error(
            f"Timeout sending event to Kafka topic='{topic}'",
            extra={"topic": topic, "event": event, "error": str(e)}
        )
        raise KafkaProducerError("Timeout sending event to Kafka") from e
    except Exception as e:
        logger.error(
            f"Failed to send event to Kafka topic='{topic}'",
            extra={"topic": topic, "event": event, "error": str(e), "error_type": type(e).__name__}
        )
        raise KafkaProducerError("Failed to send event to Kafka") from e

    @property
    def is_connected(self) -> bool:
        return self._connected

kafka = KafkaProducer()
