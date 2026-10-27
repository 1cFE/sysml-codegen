#!/bin/bash
B=${B:-/tmp/claude-1000/leak-investigation/shapes}
cd /tmp/claude-1000/leak-investigation/wt
for d in $B/*/; do n=$(basename $d); rm -rf $d/out
  uv run --env-file /home/reid/src/agentic-mbse/.env python /tmp/claude-1000/leak-investigation/scripts/trace.py generate --models $d/models --output $d/out --package-name leak > $d/trace.txt 2>&1; rc=$?
  echo "=== $n rc=$rc"; grep TRACE $d/trace.txt | sort -u
  [ $rc -ne 0 ] && grep -E "ERROR" $d/trace.txt | head -3
done
