#!/bin/bash
set -e

# Install necessary utilities for health checks if missing
if ! command -v pg_isready &> /dev/null
then
    echo "pg_isready could not be found, installing postgresql-client ..."
    sudo apt-get update && sudo apt-get install -y postgresql-client
fi

if ! command -v nc &> /dev/null
then
    echo "nc (netcat) could not be found, installing netcat ..."
    sudo apt-get update && sudo apt-get install -y netcat
fi

echo "Waiting for PostgreSQL to be ready at postgres:5432"
until pg_isready -h postgres -p 5432; do
  echo "Waiting for postgres..."
  sleep 2
done

echo "Waiting for MongoDB to be ready at mongo:27017"
until nc -z mongo 27017; do
  echo "Waiting for mongo..."
  sleep 2
done

echo "Waiting for Redis to be ready at redis:6379"
until nc -z redis 6379; do
  echo "Waiting for redis..."
  sleep 2
done

echo "Waiting for Kafka to be ready at kafka:9092"
until nc -z kafka 9092; do
  echo "Waiting for kafka..."
  sleep 2
done

echo "All services are up!"

