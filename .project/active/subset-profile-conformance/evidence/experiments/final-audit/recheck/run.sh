#!/bin/bash
# usage: run.sh <copydir> <label> <patch.py> [codegen pytest targets...]
# Applies patch (python script run with cwd=copydir, which edits files), runs the codegen licensed subset suite
# (and agentic-mbse tests if AGENTIC_TESTS set), records failures, then reverts both repos to HEAD.
COPY=$1; LABEL=$2; PATCH=$3; shift 3
TARGETS=${@:-tests/conformance/subset_profile/}
OUT=/tmp/audit2a-recheck/results/$LABEL.txt
set -a; source /home/reid/src/subset-conformance/agentic-mbse/.env; set +a
cd $COPY && python3 $PATCH > $OUT 2>&1 || { echo "PATCH FAILED" >> $OUT; git -C $COPY/sysml-codegen checkout -q -- . ; git -C $COPY/agentic-mbse checkout -q -- . ; exit 1; }
echo "== diff ==" >> $OUT
git -C $COPY/sysml-codegen diff --stat >> $OUT; git -C $COPY/agentic-mbse diff --stat >> $OUT
git -C $COPY/sysml-codegen status --short --untracked-files=all | grep '^??' >> $OUT
git -C $COPY/agentic-mbse status --short --untracked-files=all | grep '^??' >> $OUT
echo "== codegen pytest ==" >> $OUT
(cd $COPY/sysml-codegen && uv run --extra dev pytest $TARGETS -q -p no:cacheprovider -rfE 2>&1 | grep -E '^(FAILED|ERROR)|passed|failed' | sed 's/ - .*//' ) >> $OUT
if [ -n "$AGENTIC_TESTS" ]; then
  echo "== agentic pytest ==" >> $OUT
  (cd $COPY/agentic-mbse && uv run --all-extras pytest $AGENTIC_TESTS -q -p no:cacheprovider -rfE 2>&1 | grep -E '^(FAILED|ERROR)|passed|failed' | sed 's/ - .*//') >> $OUT
fi
git -C $COPY/sysml-codegen checkout -q -- . ; git -C $COPY/sysml-codegen clean -qfd -e .venv ; git -C $COPY/agentic-mbse checkout -q -- . ; git -C $COPY/agentic-mbse clean -qfd -e .venv -e .env
echo "== reverted ==" >> $OUT
