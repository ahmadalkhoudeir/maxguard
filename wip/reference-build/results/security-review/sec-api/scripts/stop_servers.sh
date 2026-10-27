#!/bin/sh
S=/tmp/claude-0/-home-user-maxguard/d28fe4b6-2c9f-5cd0-8e7f-d2be65aa4c01/scratchpad
R=$S/agentwork/sec-api/run
for n in A B C D E F H I; do [ -f $R/pid$n ] && kill $(cat $R/pid$n) 2>/dev/null; rm -f $R/pid$n; done
[ -f $R/pidAttacker ] && kill $(cat $R/pidAttacker) 2>/dev/null; rm -f $R/pidAttacker
rm -f $R/token $R/wrongtoken
echo stopped
