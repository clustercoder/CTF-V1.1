#!/bin/sh
set -e

# wait until Postgres is ready
until pg_isready -h db -U postgres; do
  echo "Waiting for Postgres..."
  sleep 2
done

# Run seed and start app
python seed.py
exec gunicorn app:app --bind 0.0.0.0:8000
