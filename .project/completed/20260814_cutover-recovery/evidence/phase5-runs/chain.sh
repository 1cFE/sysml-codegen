#!/usr/bin/env bash
# Three consecutive complete runs of the candidate battery.
D=/home/reid/1cfe/sysml-codegen-item7-rebuild/.project/active/cutover-recovery/evidence/phase5-runs
for r in run1 run2 run3; do
  "$D/run_candidate_battery.sh" "$r" > "$D/$r.console" 2>&1
done
echo "CHAIN COMPLETE"
