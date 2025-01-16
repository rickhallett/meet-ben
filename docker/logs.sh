#!/bin/bash

source ./.env

docker compose -p "$PROJECT_NAME" logs -f --timestamps