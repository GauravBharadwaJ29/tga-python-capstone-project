from src.event_mapper import map_event_to_notification

def test_payment_successful():
    event = {
        "event": "payment_successful",
        "customer_id": "user@example.com",
        "order_id": "123"
    }
    notif = map_event_to_notification(event)
    assert notif["recipient"] == "user@example.com"
    assert "successful" in notif["message"]
    assert notif["type"] == "email"

def test_unknown_event():
    event = {"event": "random_event"}
    assert map_event_to_notification(event) is None
