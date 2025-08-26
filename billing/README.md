# Billing Service

## Overview
- FastAPI service for generating and managing bills.
- PostgreSQL for data storage.
- Publishes billing events to Kafka.
- Health check endpoint.

## Endpoints

| Method | Endpoint                | Description             |
|--------|------------------------|-------------------------|
| GET    | /health                | Health check            |
| POST   | /bills                 | Generate bill           |
| GET    | /bills                 | List all bills          |
| GET    | /bills/{id}            | Get bill by ID          |
| PUT    | /bills/{id}            | Update bill status      |
| DELETE | /bills/{id}            | Delete bill             |

## Setup
