# Notification Bridge Service

Consumes NOTIFICATION_TOPIC from Kafka and POSTs notifications to the notification service REST API.

## Usage

- Configure `.env` and `logging_config.yaml`
- Add to docker-compose as a service (depends_on: kafka, notification)
- Adjust `event_mapper.py` for your event types and payloads

## Testing

