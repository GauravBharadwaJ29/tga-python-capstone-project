# Order Service

## Overview
- FastAPI service for managing customer orders.
- PostgreSQL for data storage.
- Publishes order events to Kafka.
- Health check endpoint.

## Endpoints

| Method | Endpoint                | Description             |
|--------|------------------------|-------------------------|
| GET    | /health                | Health check            |
| POST   | /orders                | Create order            |
| GET    | /orders                | List all orders         |
| GET    | /orders/{id}           | Get order by ID         |
| PUT    | /orders/{id}           | Update order status     |
| DELETE | /orders/{id}           | Delete order            |
