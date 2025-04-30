#!/bin/bash

# Define the base URL for the Flask API
BASE_URL="http://localhost:5000/api"

# Flag to control whether to echo JSON output
ECHO_JSON=false

# Parse command-line arguments
while [ "$#" -gt 0 ]; do
  case $1 in
    --echo-json) ECHO_JSON=true ;;
    *) echo "Unknown parameter passed: $1"; exit 1 ;;
  esac
  shift
done


###############################################
#
# Health checks
#
###############################################

# Function to check the health of the service
check_health() {
  echo "Checking health status..."
  curl -s -X GET "$BASE_URL/health" | grep -q '"status": "success"'
  if [ $? -eq 0 ]; then
    echo "Service is healthy."
  else
    echo "Health check failed."
    exit 1
  fi
}

# Function to check the database connection
check_db() {
  echo "Checking database connection..."
  curl -s -X GET "$BASE_URL/db-check" | grep -q '"status": "success"'
  if [ $? -eq 0 ]; then
    echo "Database connection is healthy."
  else
    echo "Database check failed."
    exit 1
  fi
}

##########################################################
#
# Boxer Management
#
##########################################################

create_boxer() {
    name=$1
    weight=$2
    height=$3
    reach=$4
    age=$5

    echo "Adding boxer ($name) to the gym..."
    curl -s -X POST "$BASE_URL/add-boxer" -H "Content-Type: application/json" \
    -d "{\"name\":\"$name\", \"weight\":$weight, \"height\":$height, \"reach\":$reach, \"age\":$age}" | grep -q '"status": "success"'

    if [ $? -eq 0 ]; then
    echo "Boxer added successfully."
  else
    echo "Failed to add boxer."
    exit 1
  fi
}

delete_boxer_by_id() {
    boxer_id=$1

    echo "Deleting boxer by ID ($boxer_id)..."
    response=$(curl -s -X DELETE "$BASE_URL/delete-boxer/$boxer_id")
    if echo "$response" | grep -q '"status": "success"'; then
        echo "Boxer deleted successfully by ID ($boxer_id)."
    else
        echo "Failed to delete boxer by ID ($boxer_id)."
        exit 1
    fi
}

get_boxer_by_id() {
    boxer_id=$1

    echo "Getting boxer by ID ($boxer_id)..."
    response=$(curl -s -X GET "$BASE_URL/get-boxer-by-id/$boxer_id")
    if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxer retrieved successfully by ID ($boxer_id)."
    if [ "$ECHO_JSON" = true ]; then
      echo "Get boxer by ID JSON (ID $boxer_id):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get boxer by ID ($boxer_id)."
    exit 1
  fi
}

get_boxer_by_name() {
    boxer_name=$1

    echo "Getting boxer by name ($boxer_name)..."
    response=$(curl -s -X GET "$BASE_URL/get-boxer-by-name/$boxer_name")
    if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxer retrieved successfully by name ($boxer_name)."
    if [ "$ECHO_JSON" = true ]; then
      echo "Get Boxer by name JSON (ID $boxer_name):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get boxer by name ($boxer_name)."
    exit 1
  fi
}

############################################################
#
# Ring
#
############################################################

fight_boxers() {
  echo "Triggering a simulated fight between the boxers..."
  response=$(curl -s -X GET "$BASE_URL/fight")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxers have fought successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Fight result JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Fight failed. Response:"
    echo "$response" | jq .
    exit 1
  fi
}

clear_boxers() {
    echo "Clearing boxers..."
    response=$(curl -s -X POST "$BASE_URL/clear-boxers")

    if echo "$response" | grep -q '"status": "success"'; then
        echo "Boxers cleared successfully."
    else
        echo "Failed to clear boxers."
        exit 1
    fi
}

enter_ring() {
    name=$1
    
    echo "Adding boxer to ring: $name..."
    response=$(curl -s -X POST "$BASE_URL/enter-ring" \
    -H "Content-Type: application/json" \
    -d "{\"name\":\"$name\"}")

    if echo "$response" | grep -q '"status": "success"'; then
        echo "Boxer added to ring successfully."
        if [ "$ECHO_JSON" = true ]; then
            echo "Enter Ring JSON:"
            echo "$response" | jq .
    fi
  else
    echo "Failed to add boxer to ring."
    exit 1
  fi
}

get_boxers() {
    echo "Retrieving all boxers from ring..."
    response=$(curl -s -X GET "$BASE_URL/get-boxers")

    if echo "$response" | grep -q '"status": "success"'; then
        echo "All boxers retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
        echo "Get Boxers JSON:"
        echo "$response" | jq .
        fi
    else
        echo "Failed to retrieve all boxers from ring."
        exit 1
    fi
}

############################################################
#
# Leaderboard
#
############################################################

get_leaderboard() {
    sort_by=$1

    echo "Retrieving leaderboard sorted by '$sort_by'..."
    response=$(curl -s -X GET "$BASE_URL/leaderboard?sort=$sort_by")

    if echo "$response" | grep -q '"status": "success"'; then
        echo "Leaderboard retrieved successfully."
        if [ "$ECHO_JSON" = true ]; then
            echo "Leaderboard JSON:"
        echo "$response" | jq .
        fi
    else
        echo "Failed to retrieve leaderboard (sort_by: $sort_by)."
        exit 1
  fi
}

# Initialize the database
sqlite3 db/boxing.db < sql/init_db.sql

# Health checks
check_health
check_db

# Create songs
create_boxer "Mike Tyson" 150 70 10 26
create_boxer "Clay Thompson" 160 77 11 31
create_boxer "Michael Miller" 145 50 9 19
create_boxer "John Smith" 130 55 13 30
create_boxer "Gabe Kim" 219 80 12 35

delete_boxer_by_id 4

get_boxer_by_id 2
get_boxer_by_name "Mike Tyson"

enter_ring "Clay Thompson"
enter_ring "John Smith"

get_boxers
fight_boxers

get_leaderboard "wins"
get_leaderboard "win_pct"

clear_boxers
delete_boxer_by_id 1
delete_boxer_by_id 2

echo "All tests passed successfully!"




