#!/bin/bash
set -e

# Install required utilities
apt-get update && apt-get install -y postgresql-client netcat-openbsd kafkacat

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

# Function to check Kafka specifically
# Function to check Kafka specifically
wait_for_kafka() {
  local host=$1
  local port=$2
  local max_attempts=40  # Increased from 30 to 40
  local attempt=1

  echo "Waiting for Kafka at $host:$port..."
  while [ $attempt -le $max_attempts ]; do
    # Use kafkacat to list brokers, which checks if Kafka is truly ready
    if kafkacat -b $host:$port -L 2>/dev/null; then
      echo "Kafka is ready!"
      return 0
    fi
    echo "Attempt $attempt/$max_attempts: Kafka not ready. Retrying in 2 seconds..."
    sleep 2
    attempt=$((attempt + 1))
  done
  echo "Error: Kafka failed to become ready in time."
  exit 1
}


# Function to check PostgreSQL specifically
wait_for_postgres() {
  local host=$1
  local port=$2
  local max_attempts=30
  local attempt=1

  echo "Waiting for PostgreSQL at $host:$port..."
  while [ $attempt -le $max_attempts ]; do
    if pg_isready -h $host -p $port -U postgres; then
      echo "PostgreSQL is ready!"
      return 0
    fi
    echo "Attempt $attempt/$max_attempts: PostgreSQL not ready. Retrying in 2 seconds..."
    sleep 2
    attempt=$((attempt + 1))
  done
  echo "Error: PostgreSQL failed to become ready in time."
  exit 1
}

# Check services
wait_for_postgres localhost 5432 PostgreSQL
wait_for_service localhost 27017 MongoDB
wait_for_service localhost 6379 Redis

echo "Waiting a moment for services to begin starting..."
sleep 10
wait_for_kafka localhost 9092 Kafka

echo "All services are up and running!"