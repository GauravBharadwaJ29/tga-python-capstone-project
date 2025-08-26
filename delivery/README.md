# Delivery Service

## Overview
- FastAPI service for managing delivery assignments and status (dummy logic).
- PostgreSQL for data storage.
- Publishes delivery events to Kafka.
- Health check endpoint.

## Endpoints

| Method | Endpoint                | Description             |
|--------|------------------------|-------------------------|
| GET    | /health                | Health check            |
| POST   | /deliveries            | Assign delivery         |
| GET    | /deliveries            | List all deliveries     |
| GET    | /deliveries/{id}       | Get delivery by ID      |
| PUT    | /deliveries/{id}       | Update delivery status  |
| DELETE | /deliveries/{id}       | Delete delivery         |

## Setup
