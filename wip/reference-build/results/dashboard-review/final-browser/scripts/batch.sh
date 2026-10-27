#!/bin/bash
# Run "script.js:buildKey:seconds" items one after another; write results/<batchname>.done at the end.
# Usage: batch.sh <batchname> item...
W=/tmp/claude-0/-home-user-maxguard/d28fe4b6-2c9f-5cd0-8e7f-d2be65aa4c01/scratchpad/agentwork/final-browser
name=$1; shift
echo $$ > $W/results/$name.pid
for item in "$@"; do
  IFS=: read script key secs <<< "$item"
  $W/scripts/run_one.sh $script $key $secs
done
echo done > $W/results/$name.done
