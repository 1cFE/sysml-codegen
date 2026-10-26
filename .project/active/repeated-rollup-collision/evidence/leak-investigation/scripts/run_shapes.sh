#!/bin/bash
B=/tmp/claude-1000/leak-investigation/shapes
cd /home/reid/src/sysml-codegen
for d in $B/*/; do n=$(basename $d); rm -rf $d/out
  uv run --env-file /home/reid/src/agentic-mbse/.env sysml-codegen generate --models $d/models --output $d/out --package-name leak > $d/gen.txt 2>&1; rc=$?
  echo "=== $n rc=$rc"; cat $d/out/inputs/*.json 2>/dev/null | tr -d '\n ' ; echo
  [ $rc -ne 0 ] && grep -iE "error|refus" $d/gen.txt | head -3
done
