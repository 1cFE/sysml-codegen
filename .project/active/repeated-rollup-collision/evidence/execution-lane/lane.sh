#!/usr/bin/env bash
# Build and run the TEAx execution lane for one codegen commit (args: <codegen commit> <empty work folder>).
# Adapted from .project/active/subset-profile-screen/evidence/execution-lane/lane.sh: codegen is
# this checkout, agentic-mbse is the committed HEAD of /home/reid/src/agentic-mbse (the editable
# dependency this branch was developed against) instead of e268357f, and the manifest writer is
# the lane_manifest.py beside this script (the old /tmp/subset-2b/tools/ copy is gone).
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
CG=/home/reid/src/sysml-codegen
AGR=/home/reid/src/agentic-mbse
SHA=$(git -C "$CG" rev-parse "$1"); L=$2
AG=$(git -C "$AGR" rev-parse HEAD)
TX=8d877460ac4f6f264561d916e40c1708adb13397
rm -rf "$L"; mkdir -p "$L/artifacts" "$L/codegen" "$L/agentic-src"
git -C "$CG" archive --format=tar "$SHA" > "$L/artifacts/codegen-${SHA:0:8}.tar"
tar -xf "$L/artifacts/codegen-${SHA:0:8}.tar" -C "$L/codegen"
git -C /home/reid/src/teax archive --format=tar "$TX" > "$L/artifacts/teax-8d877460.tar"
git -C "$AGR" archive --format=tar "$AG" | tar -xf - -C "$L/agentic-src"
uv build --wheel --out-dir "$L/artifacts" "$L/agentic-src" > "$L/build.log" 2>&1
uv venv --python 3.12 "$L/venv" > /dev/null 2>&1
uv pip install --python "$L/venv/bin/python" "$L"/artifacts/agentic_mbse-0.1.3-py3-none-any.whl jinja2 pydantic pyyaml pytest pytest-cov jsonschema numpy pandas pyarrow python-dotenv > "$L/install.log" 2>&1
uv pip install --python "$L/venv/bin/python" --no-deps -e "$L/codegen" >> "$L/install.log" 2>&1
(cd "$L/codegen" && git init -q && git add -A && git -c user.name=lane -c user.email=lane@local commit -qm "archive of $SHA")
git clone -q /home/reid/src/teax "$L/teax-clone" && git -C "$L/teax-clone" checkout -q "$TX"
"$L/venv/bin/python" -I "$HERE/lane_manifest.py" "$L" "$SHA" "$AG"
set -a; source "$AGR/.env"; set +a
S="$L/teax-clone/packages/teax-simkit"
cd "$L/codegen"
PYTHONPATH="$L/codegen/src:$S" CODEGEN_EXECUTION_PROVENANCE="$L/provenance.json" TEAX_SIMKIT_PATH="$S" \
  "$L/venv/bin/python" -m pytest tests/execution -m execution -q -p no:cacheprovider -rfEs --junitxml="$L/run.xml" > "$L/run.txt" 2>&1 || true
tail -3 "$L/run.txt"
