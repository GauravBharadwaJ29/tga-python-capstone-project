#!/bin/bash
set -e

# Install required utilities
apt-get update && apt-get install -y postgresql-client netcat-openbsd

# Function to check service availability
wait_for_service() {
  local host=$1
  local port=$2
  local service=$3
  local max_attempts=30
  local attempt=1

  echo "Waiting for $service at $host:$port..."
  while [ $attempt -le $max_attempts ]; do
    if nc -z $host $port; then
      echo "$service is ready!"
      return 0
    fi
    echo "Attempt $attempt/$max_attempts: $service not ready. Retrying in 2 seconds..."
    sleep 2
    attempt=$((attempt + 1))
  done
  echo "Error: $service failed to become ready in time."
  exit 1
}

# Check services
wait_for_service localhost 5432 PostgreSQL
wait_for_service localhost 27017 MongoDB
wait_for_service localhost 6379 Redis
wait_for_service localhost 2181 Zookeeper
wait_for_service localhost 9092 Kafka

echo "All services are up and running!"