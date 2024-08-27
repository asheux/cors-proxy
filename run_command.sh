#!/bin/bash

# docker-compose run -p 5000:5000 app "$@"
docker compose -f docker-compose.dev.yml run -p 5000:5000 app "$@"
