#!/bin/bash
# start.sh <build> <data> <port> [seed]  -> starts serve.py in the background, prints the PID
W=/tmp/claude-0/-home-user-maxguard/d28fe4b6-2c9f-5cd0-8e7f-d2be65aa4c01/scratchpad/agentwork/final-review
PY=/tmp/claude-0/-home-user-maxguard/d28fe4b6-2c9f-5cd0-8e7f-d2be65aa4c01/scratchpad/ref/.venv/bin/python
export TMPDIR=$W/tmp PYTHONDONTWRITEBYTECODE=1
mkdir -p $W/tmp $W/logs
nohup $PY $W/scripts/serve.py $1 $2 $3 ${4:-basic} > $W/logs/server-$3.log 2>&1 &
pid=$!
for i in $(seq 1 120); do curl -s -o /dev/null http://127.0.0.1:$3/ && break; sleep 0.5; done
echo $pid
