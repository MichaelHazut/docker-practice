#!/bin/bash

if [ "$#" -ne 1 ]; then
    echo "Usage: ./scale_service.sh <up|down>"
    exit 1
fi

command=$1

if [ "$command" = "up" ]; then
    docker-compose up -d --scale web=5
elif [ "$command" = "down" ]; then
    docker-compose up -d --scale web=3
else
    echo "Invalid command. Use 'up' to scale to 5 replicas or 'down' to scale to 3 replicas."
    exit 1
fi