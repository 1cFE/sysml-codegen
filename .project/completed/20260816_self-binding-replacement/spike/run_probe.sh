#!/usr/bin/env bash
# SPIKE THROWAWAY — run the shipped codegen CLI over each scratch fixture.
# Usage: ./run_probe.sh [fixture_name ...]   (default: all)
set -u
cd /home/reid/1cfe/sysml-codegen
set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a
if [ -z "${SYSIDE_LICENSE_KEY:-}" ]; then echo "FATAL: no license key"; exit 1; fi
echo "license key loaded (len ${#SYSIDE_LICENSE_KEY})"

SPIKE=.project/active/self-binding-replacement/spike
FIXTURES=${*:-$(ls "$SPIKE/fixtures")}

for f in $FIXTURES; do
  out="$SPIKE/out/$f"
  rm -rf "$out"; mkdir -p "$out"
  echo "=================== FIXTURE: $f"
  uv run sysml-codegen generate \
      --models "$SPIKE/fixtures/$f" \
      --output "$out" \
      --package-name spike_pkg \
      --overwrite > "$SPIKE/out/$f.log" 2>&1
  echo "exit=$?"
  tail -40 "$SPIKE/out/$f.log"
done
