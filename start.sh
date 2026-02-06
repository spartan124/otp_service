#!/bin/bash

# 1. Start the Worker in the background (&)
echo " [x] Starting Background Worker..."
python -m app.worker &

# 2. Start the Web API in the foreground
# (Docker keeps running as long as this process is alive)
echo " [x] Starting Web API..."
uvicorn app.main:app --host 0.0.0.0 --port 8000