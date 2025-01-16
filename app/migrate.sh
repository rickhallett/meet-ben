#!/bin/bash

source ./.env

docker exec -it "$PROJECT_NAME"_api bash -c "alembic upgrade head"