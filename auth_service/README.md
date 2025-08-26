# API Gateway

## Overview
- FastAPI service acting as a reverse proxy for all microservices.
- Enforces API key security (header: `x-api-key`).
- Health check endpoint.
- (Commented) Rate limiting middleware for future use.

## Endpoints

| Method | Endpoint         | Description                |
|--------|------------------|---------------------------|
| GET    | /health          | Health check              |
| *      | /products*       | Proxy to Product Catalog  |
| *      | /inventory*      | Proxy to Inventory        |
| *      | /orders*         | Proxy to Order            |
| *      | /payments*       | Proxy to Payment          |
| *      | /bills*          | Proxy to Billing          |
| *      | /deliveries*     | Proxy to Delivery         |
| *      | /notify*         | Proxy to Notification     |
| *      | /stores*         | Proxy to Store Onboarding |

## Setup
