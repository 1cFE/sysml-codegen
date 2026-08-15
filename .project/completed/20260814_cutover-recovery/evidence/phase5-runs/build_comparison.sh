#!/usr/bin/env bash
# Build the REVISE step-7a three-run comparison from the committed run artifacts.
D=/home/reid/1cfe/sysml-codegen-item7-rebuild/.project/active/cutover-recovery/evidence/phase5-runs
/home/reid/1cfe/item7-rebuild-venv/bin/python "$D/compare_revise_runs.py" > "$D/revise-runs/comparison.md"
rc=$?
echo "comparator exit=$rc"
cat "$D/revise-runs/comparison.md"
exit $rc
