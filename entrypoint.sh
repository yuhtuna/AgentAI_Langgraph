#!/bin/sh
set -e
if [ -z "$PORT" ]; then
  PORT=8080
fi
# Try to run with gunicorn if available, else python
if grep -q "gunicorn" requirements.txt; then
    exec gunicorn --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 120 main:app
else
    exec python main.py
fi
