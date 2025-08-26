#!/bin/bash
set -e
DB=psmarket

# Create DB if not exists
if ! docker compose exec -T postgres psql -U postgres -tAc "SELECT 1 FROM pg_database WHERE datname = '$DB';" | grep -q 1; then
  echo "Creating database $DB..."
  docker compose exec -T postgres psql -U postgres -c "CREATE DATABASE $DB;"
else
  echo "Database $DB already exists."
fi

# Create tables (idempotent)
echo "Creating tables in $DB..."
docker compose exec -T postgres psql -U postgres -d $DB -f /docker-entrypoint-initdb.d/init-postgres-multidb.sql
echo "Done."
