# Store Onboarding Service

## Overview
- FastAPI service for registering and managing stores.
- PostgreSQL for data storage.
- Publishes store events to Kafka.
- Health check endpoint.

## Endpoints

| Method | Endpoint                | Description             |
|--------|------------------------|-------------------------|
| GET    | /health                | Health check            |
| POST   | /stores                | Onboard store           |
| GET    | /stores                | List all stores         |
| GET    | /stores/{id}           | Get store by ID         |
| PUT    | /stores/{id}           | Update store            |
| DELETE | /stores/{id}           | Delete store            |

## Setup

