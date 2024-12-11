#!/bin/bash

# Variables for InfluxDB credentials and database setup
INFLUXDB_URL=""
INFLUXDB_USERNAME=""
INFLUXDB_PASSWORD=""
INFLUXDB_DB_NAME=""

# Create InfluxDB database if it doesn't exist
echo "Creating database '$INFLUXDB_DB_NAME'..."
curl -X POST "$INFLUXDB_URL/query" \
  --data-urlencode "q=CREATE DATABASE $INFLUXDB_DB_NAME" \
  -u "$INFLUXDB_USERNAME:$INFLUXDB_PASSWORD"

# Create a user with the appropriate privileges if it doesn't exist
echo "Creating user '$INFLUXDB_USERNAME' if it doesn't exist..."
curl -X POST "$INFLUXDB_URL/query" \
  --data-urlencode "q=CREATE USER \"$INFLUXDB_USERNAME\" WITH PASSWORD '$INFLUXDB_PASSWORD'" \
  -u "$INFLUXDB_USERNAME:$INFLUXDB_PASSWORD"

# Grant all privileges on the new database to the user
echo "Granting all privileges to user '$INFLUXDB_USERNAME' on database '$INFLUXDB_DB_NAME'..."
curl -X POST "$INFLUXDB_URL/query" \
  --data-urlencode "q=GRANT ALL ON $INFLUXDB_DB_NAME TO \"$INFLUXDB_USERNAME\"" \
  -u "$INFLUXDB_USERNAME:$INFLUXDB_PASSWORD"

# Verify the database and user creation
echo "Verifying database and user setup..."
curl -X GET "$INFLUXDB_URL/query" \
  --data-urlencode "q=SHOW DATABASES" \
  -u "$INFLUXDB_USERNAME:$INFLUXDB_PASSWORD"

curl -X GET "$INFLUXDB_URL/query" \
  --data-urlencode "q=SHOW USERS" \
  -u "$INFLUXDB_USERNAME:$INFLUXDB_PASSWORD"

echo "InfluxDB setup completed successfully!"
