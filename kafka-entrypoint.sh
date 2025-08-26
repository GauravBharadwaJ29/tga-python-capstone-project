#!/bin/bash
set -e

DATA_DIR="/var/lib/kafka/data"
CLUSTER_ID_FILE="$DATA_DIR/cluster.id"

# Generate or reuse CLUSTER_ID
if [ -f "$CLUSTER_ID_FILE" ]; then
  CLUSTER_ID=$(cat "$CLUSTER_ID_FILE")
else
  echo "Generating new Kafka CLUSTER_ID..."
  CLUSTER_ID=$(/usr/bin/kafka-storage.sh random-uuid)
  echo "Generated CLUSTER_ID: $CLUSTER_ID"
  # Save CLUSTER_ID to file for future use

  echo $CLUSTER_ID > "$CLUSTER_ID_FILE"
fi

# Initialize storage if not formatted
if [ ! -f "$DATA_DIR/meta.properties" ]; then
  echo "Formatting Kafka storage with CLUSTER_ID: $CLUSTER_ID"
  /usr/bin/kafka-storage.sh format -t $CLUSTER_ID -c /etc/kafka/kraft/server.properties
  echo "Kafka storage formatted."
fi

# Export CLUSTER_ID for Kafka to use
export KAFKA_CLUSTER_ID=$CLUSTER_ID

# Start Kafka broker
exec /etc/confluent/docker/run
