#!/bin/bash

set -e

echo "Waiting for Postgres..."
until docker exec $(docker-compose ps -q postgres) pg_isready > /dev/null 2>&1; do
  echo "Waiting for Postgres to be ready..."
  sleep 3
done

echo "Waiting for MongoDB..."
until docker exec $(docker-compose ps -q mongo) mongo --eval "db.adminCommand('ping')" > /dev/null 2>&1; do
  echo "Waiting for MongoDB to be ready..."
  sleep 3
done

echo "Waiting for Kafka..."
until nc -z localhost 9092; do
  echo "Waiting for Kafka to be ready..."
  sleep 3
done

# Add waits for any other critical services similarly

echo "All services are healthy and ready!"
