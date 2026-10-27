#!/bin/bash
# Run one check script for one build with a time limit; output to results/<name>-<key>.txt
# Usage: run_one.sh <script.js> <buildKey> <seconds>
W=/tmp/claude-0/-home-user-maxguard/d28fe4b6-2c9f-5cd0-8e7f-d2be65aa4c01/scratchpad/agentwork/final-browser
cd $W/scripts
export TMPDIR=$W/tmp
name=$(basename $1 .js)
timeout ${3:-300} node $1 $2 > $W/results/$name-$2.txt 2>&1
echo "exit=$?" >> $W/results/$name-$2.txt
