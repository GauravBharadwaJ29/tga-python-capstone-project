from .logger_config import logger
from .config import (
    EVENT_PAYMENT_SUCCESSFUL,   
    EVENT_PAYMENT_FAILED,
    EVENT_ORDER_SHIPPED,
    EVENT_ORDER_DELIVERED,
)

def map_event_to_notification(event: dict) -> dict | None:
    event_type = event.get("event")
    # Helper: get recipient (contact or email)
    recipient = (
        event.get("customer_contact")
        or event.get("customer_email")
        or str(event.get("customer_id", "unknown"))
    )
    items = event.get("items", [])

    if event_type == EVENT_PAYMENT_SUCCESSFUL:
        logger.info(f"Mapping event {event_type} to notification")
        return {
            "to": recipient,
            "subject": f"Payment Successful for Order {event.get('order_id')}",
            "items": items,
            "message": f"Your payment for order {event.get('order_id')} was successful!",
            "type": "email"
        }
    elif event_type == EVENT_PAYMENT_FAILED:
        logger.info(f"Mapping event {event_type} to notification")
        return {
            "to": recipient,
            "subject": f"Payment Failed for Order {event.get('order_id')}",
            "items": items,
            "message": f"Your payment for order {event.get('order_id')} failed. Reason: {event.get('reason', 'Unknown')}",
            "type": "email"
        }
    elif event_type == EVENT_ORDER_SHIPPED:
        logger.info(f"Mapping event {event_type} to notification")
        return {
            "to": recipient,
            "subject": f"Order Shipped: {event.get('order_id')}",
            "items": items,
            "message": f"Your order {event.get('order_id')} has shipped!",
            "type": "email"
        }
    elif event_type == EVENT_ORDER_DELIVERED:
        logger.info(f"Mapping event {event_type} to notification")
        return {
            "to": recipient,
            "subject": f"Order Delivered: {event.get('order_id')}",
            "items": items,
            "message": f"Your order {event.get('order_id')} was delivered!",
            "type": "email"
        }
    else:
        logger.info(f"No notification mapping for event type: {event_type}")
        return None
