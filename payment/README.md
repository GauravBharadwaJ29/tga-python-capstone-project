# Payment Service

## Overview
- FastAPI service for processing payments (dummy logic).
- PostgreSQL for data storage.
- Publishes payment events to Kafka.
- Health check endpoint.

## Endpoints

| Method | Endpoint                | Description             |
|--------|------------------------|-------------------------|
| GET    | /health                | Health check            |
| POST   | /payments              | Process payment         |
| GET    | /payments              | List all payments       |
| GET    | /payments/{id}         | Get payment by ID       |
| PUT    | /payments/{id}         | Update payment          |
| DELETE | /payments/{id}         | Delete payment          |

## Setup
