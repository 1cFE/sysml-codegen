#!/usr/bin/env bash
# Phase 5 candidate battery — one complete run.
#
#   ./run_candidate_battery.sh <run-label>
#
# Writes every step's stdout/stderr and exit code under phase5-runs/<run-label>/.
# It never stops on a failing step: a divergence is a finding to record, and the
# rest of the run still has to be measured.
#
# Environment discipline (plan.md, "Environment Setup"):
#   - the licensed key comes from the companion checkout's .env
#   - the interpreter is the one task-specific acceptance venv
#   - the three import paths are asserted first and the run aborts if any of them
#     resolves outside the two *-item7-rebuild worktrees and the pinned TEAx.

RUN="${1:?usage: run_candidate_battery.sh <run-label>}"
CODEGEN=/home/reid/1cfe/sysml-codegen-item7-rebuild
MBSE=/home/reid/1cfe/agentic-mbse-item7-rebuild
TEAX=/home/reid/1cfe/teax
OUT="$CODEGEN/.project/active/cutover-recovery/evidence/phase5-runs/$RUN"
PY=/home/reid/1cfe/item7-rebuild-venv/bin/python

set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a
# The acceptance venv's bin goes on PATH: several agentic-mbse tests shell out to a
# bare `python`, and without this they fail with FileNotFoundError on a host whose
# PATH has only `python3`. That is a harness property, not a candidate property —
# measured once, run0-harness-defect/, before this line existed.
export PATH=/home/reid/1cfe/item7-rebuild-venv/bin:$PATH
mkdir -p "$OUT"
: > "$OUT/status.tsv"

step() {   # step <name> <workdir> <command...>
  local name="$1" dir="$2"; shift 2
  local start end rc
  start=$(date +%s)
  ( cd "$dir" && "$@" ) > "$OUT/$name.log" 2>&1
  rc=$?
  end=$(date +%s)
  printf '%s\t%s\t%s\n' "$name" "$rc" "$((end - start))" >> "$OUT/status.tsv"
  echo "[$RUN] $name rc=$rc $((end - start))s"
}

# --- 0. environment assertion (hard gate) ------------------------------------
$PY - > "$OUT/env.json" 2>&1 <<'PYEOF'
import json, os, sys
import agentic_mbse, jinja2, simkit, syside, sysml_codegen
import importlib.metadata as md

paths = {
    "sysml_codegen": sysml_codegen.__file__,
    "agentic_mbse": agentic_mbse.__file__,
    "simkit": simkit.__file__,
    "jinja2": jinja2.__file__,
    "syside": syside.__file__,
}
allowed = (
    "/home/reid/1cfe/sysml-codegen-item7-rebuild/",
    "/home/reid/1cfe/agentic-mbse-item7-rebuild/",
    "/home/reid/1cfe/teax/",
    "/home/reid/1cfe/item7-rebuild-venv/",
)
bad = [k for k, v in paths.items() if not v.startswith(allowed)]
versions = {}
for dist in ("syside", "syside-producer", "jinja2", "pydantic", "pytest", "ruff", "mypy"):
    try:
        versions[dist] = md.version(dist)
    except Exception:
        versions[dist] = None
print(json.dumps({
    "python": sys.version.split()[0],
    "executable": sys.executable,
    "resolved_import_paths": paths,
    "import_path_gate": "FAIL " + ",".join(bad) if bad else "PASS",
    "license_key_present": bool(os.environ.get("SYSIDE_LICENSE_KEY")),
    "versions": versions,
}, indent=2))
sys.exit(1 if bad else 0)
PYEOF
if [ $? -ne 0 ]; then echo "ENVIRONMENT GATE FAILED — see $OUT/env.json"; exit 2; fi
printf 'env_gate\t0\t0\n' >> "$OUT/status.tsv"

# --- 1. the two full suites ---------------------------------------------------
step suite_codegen   "$CODEGEN" $PY -m pytest -q
step suite_agentic   "$MBSE"    $PY -m pytest -q
step execution_lane  "$CODEGEN" $PY -m pytest tests/execution -m execution -q

# --- 2. corpus: the ledger test, and the driver's own multisets ---------------
step corpus_tests    "$CODEGEN" $PY -m pytest -q -k corpus
step corpus_driver   "$CODEGEN" $PY scripts/run_elaboration_corpus.py

# --- 3. the PROPOSED v6 batch, re-verified live against replay ----------------
step batch_verify    "$CODEGEN" $PY scripts/capture_v6_batch.py --verify
( cd "$CODEGEN" && git status --porcelain ) > "$OUT/batch_verify_worktree.txt" 2>&1
( cd "$CODEGEN" && git diff --stat ) >> "$OUT/batch_verify_worktree.txt" 2>&1
( cd "$CODEGEN" && git diff -U0 -- tests/fixtures \
    | grep -E '^[+-]' | grep -v '^[+-][+-]' | grep -vE '"captured_at"|"sha256"' ) \
    > "$OUT/batch_verify_nontimestamp_diff.txt" 2>&1
( cd "$CODEGEN" && git checkout -- tests/fixtures ) >> "$OUT/batch_verify_worktree.txt" 2>&1
step batch_check     "$CODEGEN" $PY scripts/capture_v6_batch.py --check

# --- 4. quality gates ---------------------------------------------------------
step ruff_src        "$CODEGEN" $PY -m ruff check src
step ruff_all        "$CODEGEN" $PY -m ruff check src tests scripts
step mypy_src        "$CODEGEN" $PY -m mypy src

# --- 5. the ledger checkers and the proof tripwire -----------------------------
step ledger_paths    "$CODEGEN" $PY scripts/check_ledger_4a.py paths
step ledger_surface  "$CODEGEN" $PY scripts/check_ledger_4a.py surface
step ledger_groups   "$CODEGEN" $PY scripts/check_ledger_4a.py groups
step proof_integrity "$CODEGEN" $PY scripts/check_proof_integrity.py
step doc_distinct    "$CODEGEN" $PY scripts/check_doc_distinctness.py

# --- 6. residue and boundary ---------------------------------------------------
step diff_check_cg   "$CODEGEN" git diff --check
step diff_check_mb   "$MBSE"    git diff --check
step status_cg       "$CODEGEN" git status --short --branch
step status_mb       "$MBSE"    git status --short --branch
step status_teax     "$TEAX"    git status --short --branch

echo "=== $RUN complete ==="
cat "$OUT/status.tsv"
