#!/usr/bin/env bash
# Build the sysml-codegen and agentic-mbse wheels the SC1 transcript installs (design H1 step 1).
#
# Usage: build_wheels.sh OUT CODEGEN_REPO AGENTIC_REPO
#
# Each wheel is built from `git archive HEAD` of its repository, never from a working tree, so no
# uncommitted edit reaches it. OUT/sources.json records each repository's commit and its wheel's
# sha256; run_install.sh reads it to record which revisions it installed.
set -euo pipefail
out=$1 codegen=$2 agentic=$3
mkdir -p "$out/src/codegen" "$out/src/agentic"
git -C "$codegen" archive HEAD | tar -x -C "$out/src/codegen"
git -C "$agentic" archive HEAD | tar -x -C "$out/src/agentic"
(cd "$out/src/codegen" && uv build --wheel --out-dir "$out")
(cd "$out/src/agentic" && uv build --wheel --out-dir "$out")
codegen_wheel=$(ls "$out"/sysml_codegen-*.whl)
agentic_wheel=$(ls "$out"/agentic_mbse-*.whl)
cat > "$out/sources.json" <<EOF
{
  "sysml_codegen": {"commit": "$(git -C "$codegen" rev-parse HEAD)", "wheel": "$(basename "$codegen_wheel")", "sha256": "$(sha256sum "$codegen_wheel" | cut -d' ' -f1)"},
  "agentic_mbse": {"commit": "$(git -C "$agentic" rev-parse HEAD)", "wheel": "$(basename "$agentic_wheel")", "sha256": "$(sha256sum "$agentic_wheel" | cut -d' ' -f1)"}
}
EOF
cat "$out/sources.json"
