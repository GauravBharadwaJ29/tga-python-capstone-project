import asyncio
from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaConnectionError
from .config import KAFKA_BOOTSTRAP_SERVERS, BILLING_TOPIC, SERVICE_NAME as SERVICE_NAME
from .logger_config import logger
import json

MAX_ATTEMPTS = 10
RETRY_DELAY = 5  # seconds
class KafkaProducer:
    def __init__(self):
        self.producer = None
        self._connected = False
        self.service_name = SERVICE_NAME  
        # self._start_lock = asyncio.Lock()  # Lock to serialize start calls      

    async def start(self):
        # async with self._start_lock:  # Serialize start calls
            # if self._connected:
            #     logger.info("Kafka producer already connected")
            #     return
                
        logger.info("Starting Kafka producer...")
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
            except KafkaConnectionError as e:
                logger.warning(f"Kafka connection attempt {attempts+1}/{MAX_ATTEMPTS} failed: {str(e)}")
                attempts += 1
                await asyncio.sleep(RETRY_DELAY)
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
            logger.info("Kafka producer stopped successfully")

    async def send_event(self, event: dict):
        """Send an event to the Kafka billing topic."""
        logger.debug(f"Sending event to Kafka: {event}")
        if not self._connected:
            await self.start()
        try:
            if not isinstance(event, dict):
                raise ValueError("send_event expects a dict, not bytes or string")               
            await self.producer.send_and_wait(BILLING_TOPIC, event)
            logger.debug(f"Event sent to topic {BILLING_TOPIC}")
        except Exception as e:
            logger.error(f"Failed to send event: {str(e)}")
            # Optionally, reset connection state to force reconnect on next send
            self._connected = False
            self.producer = None
            raise RuntimeError(f"Kafka event sending failed: {str(e)}")

kafka = KafkaProducer()
