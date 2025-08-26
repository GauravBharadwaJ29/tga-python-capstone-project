# Notification Service

## Overview
- FastAPI service for queuing email notifications (dummy logic).
- Redis for queueing.
- MongoDB for logging notification metadata (no message content).
- Health check endpoint.

## Endpoints

| Method | Endpoint   | Description             |
|--------|------------|------------------------|
| GET    | /health    | Health check           |
| POST   | /notify    | Queue notification     |

## Setup
