#!/bin/sh
# usage: start_server.sh <build folder> <port> <data folder> [OLLAMA_HOST]
# Starts the dashboard exactly as AHM-02 step 7 says, from the build folder,
# with the project venv first on PATH and the data folder inside my work folder.
BUILD="$1"; PORT="$2"; DATA="$3"; OLL="${4:-}"
VENV=/tmp/claude-0/-home-user-maxguard/d28fe4b6-2c9f-5cd0-8e7f-d2be65aa4c01/scratchpad/ref/.venv/bin
cd "$BUILD" || exit 1
export PATH="$VENV:$PATH" PYTHONDONTWRITEBYTECODE=1 MAXGUARD_DATA_DIR="$DATA"
if [ -n "$OLL" ]; then export OLLAMA_HOST="$OLL"; fi
exec uvicorn maxguard.api.app:create_app --factory --host 127.0.0.1 --port "$PORT"
