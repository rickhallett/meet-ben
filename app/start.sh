#!/bin/sh

# Uncomment next line to automatically apply Alembic database migrations
# alembic upgrade head

exec uvicorn main:app --host 0.0.0.0 --port 8080 --reload