#!/bin/sh
# Start three throwaway MaxGuard servers from the alpha build, all on 127.0.0.1.
#  A :18731 create_app, ingest OFF (no token), 1 MiB upload limit
#  B :18732 create_app, ingest ON (runtime token), 1 MiB upload limit
#  C :18733 create_ingest_app (runtime token), 1 MiB upload limit
set -eu
S=/tmp/claude-0/-home-user-maxguard/d28fe4b6-2c9f-5cd0-8e7f-d2be65aa4c01/scratchpad
W=$S/agentwork/sec-api
R=$W/run
PY=$S/ref/.venv/bin/python
mkdir -p $R/logs
umask 077
# throwaway token, made at run time, deleted by stop_servers.sh
[ -f $R/token ] || $PY -c "import secrets; print(secrets.token_urlsafe(32))" > $R/token
TOKEN=$(cat $R/token)
start() { # name port factory extra-env...
  name=$1; port=$2; factory=$3; shift 3
  mkdir -p $R/data$name $R/tmp$name
  ( cd $W/alpha && env -i PATH=/usr/bin:/bin HOME=$R PYTHONDONTWRITEBYTECODE=1 \
      MAXGUARD_DATA_DIR=$R/data$name TMPDIR=$R/tmp$name MAXGUARD_MAX_UPLOAD_MB=1 \
      MAXGUARD_OFFLINE=1 OLLAMA_HOST=http://127.0.0.1:9 "$@" \
      setsid nohup $PY -m uvicorn maxguard.api.app:$factory --factory \
      --host 127.0.0.1 --port $port > $R/logs/$name.log 2>&1 & echo $! > $R/pid$name )
}
start A 18731 create_app
start B 18732 create_app MAXGUARD_INGEST_TOKEN=$TOKEN
start C 18733 create_ingest_app MAXGUARD_INGEST_TOKEN=$TOKEN
sleep 3
for p in 18731 18732 18733; do printf '%s ' $p; curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:$p/api/alerts; done
