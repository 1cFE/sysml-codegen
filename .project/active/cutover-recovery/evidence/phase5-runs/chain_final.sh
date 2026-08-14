#!/usr/bin/env bash
# Three consecutive complete runs of the narrow-correction step-7 battery.
D=/home/reid/1cfe/sysml-codegen-item7-rebuild/.project/active/cutover-recovery/evidence/phase5-runs
mkdir -p "$D/final-runs"
for r in run1 run2 run3; do
  bash "$D/run_final_battery.sh" "$r" > "$D/final-runs/$r.console" 2>&1
done
echo "CHAIN COMPLETE"
