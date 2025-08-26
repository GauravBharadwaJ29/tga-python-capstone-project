import aioredis
from .config import REDIS_URL, QUEUE_NAME
from .logger_config import logger

class RedisQueue:
    def __init__(self):
        self.redis = None

    async def connect(self):
        try:
            self.redis = await aioredis.from_url(REDIS_URL, decode_responses=True)
            logger.info("Successfully connected to Redis")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {str(e)}")
            raise

    async def enqueue(self, notification: dict):
        try:
            await self.redis.rpush(QUEUE_NAME, str(notification))
            logger.debug(f"Notification enqueued successfully")
        except Exception as e:
            logger.error(f"Failed to enqueue notification: {str(e)}")
            raise

    async def dequeue(self):
        return await self.redis.lpop(QUEUE_NAME)  # Use config constant
    

queue = RedisQueue()    
