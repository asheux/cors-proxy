#!/bin/bash

docker-compose run -p 5000:5000 flask "$@"
