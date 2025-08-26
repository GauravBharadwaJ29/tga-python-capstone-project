import asyncio
from aiokafka import AIOKafkaProducer
from .config import KAFKA_BOOTSTRAP_SERVERS, ORDER_TOPIC, ErrorMessages, SERVICE_NAME as service_name
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
                logger.info("Healthcheck sent successfully")
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
            self._connected = False
            logger.info("Kafka producer stopped")

    async def send_event(self, event: dict, topic: str = ORDER_TOPIC):
        if not self._connected:
            await self.start()
        try:
            # # Always send as JSON string
            if not isinstance(event, dict):
                raise ValueError("send_event expects a dict, not bytes or string")              
            await self.producer.send_and_wait(topic, event)
            logger.debug(f"Event sent to topic {topic}")
        except Exception as e:
            logger.error(f"Failed to send event: {str(e)}")
            raise RuntimeError(ErrorMessages.KAFKA_EVENT_FAILED.format(str(e)))

# Create Kafka producer instance
kafka = KafkaProducer()
