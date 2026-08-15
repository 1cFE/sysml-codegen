#!/usr/bin/env bash
# Three consecutive complete runs of the REVISE step-7a battery.
D=/home/reid/1cfe/sysml-codegen-item7-rebuild/.project/active/cutover-recovery/evidence/phase5-runs
mkdir -p "$D/revise-runs"
for r in run1 run2 run3; do
  bash "$D/run_revise_battery.sh" "$r" > "$D/revise-runs/$r.console" 2>&1
done
echo "CHAIN COMPLETE"
