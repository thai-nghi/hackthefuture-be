#!/bin/bash

# Load environment variables from the .dev.env file
# Ensure the file exists before sourcing
ENV_FILE=".dev.env"

if [ -f "$ENV_FILE" ]; then
  # Load the environment variables
  export $(grep -v '^#' $ENV_FILE)
  export PGPASSWORD=$POSGRES_PASSWORD

  CONTAINER_NAME="postgres-htf"        # Change this to postgres container name
  SQL_SCRIPT_PATH="countries.sql"

  cat $SQL_SCRIPT_PATH | docker exec -i $CONTAINER_NAME psql -U $POSTGRES_USER -d $POSTGRES_DB -f /dev/stdin

  if [ $? -eq 0 ]; then
    echo "SQL script executed successfully."
  else
    echo "Error executing SQL script."
  fi
else
  echo "$ENV_FILE not found. Please make sure the file exists."
fi
