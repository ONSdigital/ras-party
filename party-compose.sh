#!/bin/bash

###
# Creates ras-party and db containers and populates the database with test data
###
docker compose -f docker-compose.yml down
docker compose -f docker-compose.yml up -d
sleep 10
docker cp scripts/install_test_data.sql postgres:/install_test_data.sql
sleep 10
docker exec postgres psql -U postgres -d postgres -f install_test_data.sql