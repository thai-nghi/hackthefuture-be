#!/bin/sh
alembic -x db_url="postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}/${POSTGRES_DB}" upgrade head

uvicorn main:app --host 0.0.0.0 --port 8000