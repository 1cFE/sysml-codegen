#!/usr/bin/env bash
# Residue and boundary checks, emitted as JSON on stdout.
#
# The greps are deliberately scoped to shipped code and data — `src`, `tests`,
# `scripts`, `docs`, `pyproject.toml`. The recovery's own records under `.project/`
# cite the forensic OIDs on purpose; that is the archive, not an import.

CODEGEN=/home/reid/1cfe/sysml-codegen-item7-rebuild
PY=/home/reid/1cfe/item7-rebuild-venv/bin/python
cd "$CODEGEN" || exit 2
set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a
export PATH=/home/reid/1cfe/item7-rebuild-venv/bin:$PATH

forensic=$(grep -rl "07531e64ed912d6046afce47ef0d958605e6ca08\|ed5b8b02a3064e767799cc6ee58e0119e9bfecba\|item7-forensic" src tests scripts docs pyproject.toml 2>/dev/null | sort)
origin=$(grep -rl "1cfe/sysml-codegen/\|1cfe/agentic-mbse/" src tests scripts docs pyproject.toml 2>/dev/null | sort)
origin_non_v5=$(echo "$origin" | grep -v "extraction_snapshot.json" | grep -v '^$' | sort)

boundary=$($PY -m pytest -q tests/unit/test_elaboration_import_boundaries.py 2>&1 | tail -1)
pins=$($PY -m pytest -q tests/conformance/test_public_authority_switch.py 2>&1 | tail -1)
v6_batch=$($PY -m pytest -q tests/conformance/test_v6_recapture_batch.py 2>&1 | tail -1)
runbook=$($PY -m pytest -q tests/unit/test_runbook_patches.py tests/unit/test_retirement_worklist.py 2>&1 | tail -1)
worklist=$($PY scripts/retirement_worklist.py check 2>&1 | tail -1)

json_list() { printf '['; local first=1; while IFS= read -r line; do [ -z "$line" ] && continue; [ $first -eq 0 ] && printf ','; printf '"%s"' "$line"; first=0; done; printf ']'; }

cat <<EOF
{
  "forensic_references_in_shipped_paths": $(echo "$forensic" | json_list),
  "original_checkout_absolute_paths": {
    "files": $(echo "$origin" | json_list),
    "count": $(echo "$origin" | grep -c . ),
    "outside_the_retiring_v5_snapshots": $(echo "$origin_non_v5" | json_list)
  },
  "import_boundary_tests": "$boundary",
  "single_authority_pins": "$pins",
  "v6_batch_pins": "$v6_batch",
  "runbook_patch_pins": "$runbook",
  "retirement_worklist_check": "$worklist"
}
EOF
