#!/bin/bash
R=/tmp/claude-0/-home-user-maxguard/d28fe4b6-2c9f-5cd0-8e7f-d2be65aa4c01/scratchpad/agentwork/r3-browser
cd $R/scripts
echo "### c3a (bfcache off)"; timeout 400 node c3a_back.js fixed-03 orig-03 fixed-06
echo "### c3a (bfcache on)"; timeout 400 node c3a_back.js bfcache fixed-03 orig-03 fixed-06
echo "### c3b"; timeout 400 node c3b_bfcache.js fixed-03 orig-03 fixed-06
echo "### c3c"; timeout 600 node c3c_stream502.js fixed-03 orig-03
echo "### c3d"; timeout 400 node c3d_midswap.js fixed-03 orig-03 fixed-06
echo "### done $(date)"
