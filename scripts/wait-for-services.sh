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
    if nc -z -w 1 $host $port; then
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

# Function to check Kafka specifically with multiple approaches
wait_for_kafka() {
  local host=$1
  local port=$2
  local max_attempts=60  # Increased to 60 attempts (2 minutes)
  local attempt=1

  echo "Waiting for Kafka at $host:$port..."
  
  # First, wait for the port to be open
  while [ $attempt -le $max_attempts ]; do
    if nc -z -w 1 $host $port; then
      echo "Kafka port is open, checking if fully ready..."
      break
    fi
    echo "Kafka port not open yet. Attempt $attempt/$max_attempts. Retrying in 3 seconds..."
    sleep 3
    attempt=$((attempt + 1))
  done
  
  # Reset attempt counter for the readiness check
  attempt=1
  
  # Now check if Kafka is fully ready
  while [ $attempt -le $max_attempts ]; do
    # Try multiple approaches to check Kafka readiness
    if kafkacat -b $host:$port -L 2>/dev/null; then
      echo "Kafka is fully ready!"
      return 0
    fi
    
    # Alternative check: try to create a topic
    if echo "test-topic" | kafkacat -b $host:$port -t test-topic -C -e -o beginning 2>/dev/null; then
      echo "Kafka is fully ready!"
      return 0
    fi
    
    echo "Kafka not fully ready yet. Attempt $attempt/$max_attempts. Retrying in 5 seconds..."
    sleep 5
    attempt=$((attempt + 1))
  done
  
  echo "Error: Kafka failed to become ready in time."
  echo "Debug info:"
  echo "Kafka container status:"
  docker ps -a | grep kafka || true
  echo "Kafka logs (last 20 lines):"
  docker logs $(docker ps -a | grep kafka | awk '{print $1}') | tail -20 2>/dev/null || echo "Could not get Kafka logs"
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
    if pg_isready -h $host -p $port -U postgres -q; then
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

echo "Waiting a moment for Kafka to begin starting..."
sleep 20  # Increased initial wait for Kafka

wait_for_kafka localhost 9092 Kafka

echo "All services are up and running!"