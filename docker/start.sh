#!/bin/bash

source ./.env

docker_network="$PROJECT_NAME"_network

if docker network ls --filter name=$docker_network --format '{{.Name}}' | grep -w $docker_network > /dev/null; then
    echo "Network '$docker_network' exists"
else
    echo "Creating docker network '$docker_network'"
    docker network create $docker_network
fi

docker compose -p "$PROJECT_NAME" up --build -d