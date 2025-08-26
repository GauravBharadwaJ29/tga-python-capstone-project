from fastapi import APIRouter, status
from .models import NotificationIn
from .redis_queue import queue
from .mongo_log import log_notification_meta
from .utils import custom_error
from datetime import datetime
from .logger_config import logger  # Use shared logger instance

router = APIRouter()
# queue = RedisQueue()


@router.get("/health", tags=["Health"])
async def health_check():
    try:
        # Check Redis connection
        await queue.redis.ping()
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return custom_error("Service unhealthy", 503)


@router.post("/notify", status_code=status.HTTP_202_ACCEPTED)
async def send_notification(notification: NotificationIn):
    try:
        await queue.enqueue(notification.dict())
        meta = {
            "to": notification.to,
            "subject": notification.subject,
            "sent_at": datetime.utcnow(),
            "status": "queued"
        }
        await log_notification_meta(meta)
        
        # Replace print statements with logger
        for item in notification.items:
            logger.debug(f"Processing item: {item.product_id}, Qty: {item.quantity}, Price: {item.price}")
        logger.info(f"Email queued for {notification.to} with subject '{notification.subject}'")
        
        return {"message": "Notification queued"}
    except Exception as e:
        logger.error(f"Failed to process notification: {str(e)}")
        return custom_error("Failed to process notification", 500)
    





