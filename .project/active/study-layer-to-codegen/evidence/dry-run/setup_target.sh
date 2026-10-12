#!/usr/bin/env bash
# SC4 dry run, step 1 (design Appendix H2): the scratch target the study agent works in.
#
# Usage: setup_target.sh [--with-manifest] SCRATCH CODEGEN_REPO AGENTIC_REPO TEAX_CHECKOUT
#
# --with-manifest is cut 3: the fixture's studies/manifest.json is copied in too, so the agent
# does not write the manifest.
#
# What it does, in order:
# 1. Builds SCRATCH/venv with ../parity/make_venv.sh: both wheels from `git archive HEAD`,
#    installed non-editable on /usr/bin/python3.12, with teax's simkit importable from
#    TEAX_CHECKOUT/packages/teax-simkit. SCRATCH/wheels/sources.json records the commits.
# 2. `git init SCRATCH/target`, then `sysml-codegen install-commands target --assistant claude`
#    with no terminal, from the venv.
# 3. Copies the fixture's ready-made pieces from CODEGEN_REPO's HEAD, keeping their layout under
#    tests/fixtures/study_station/: models/, station.snapshot.json, pkg/station_study/,
#    studies/study_route.py and studies/oracle_entry.py (and studies/manifest.json under cut 3).
#    It writes a .gitignore holding __pycache__/, because loading the package writes bytecode
#    beside it and preflight's clean gate would then see a dirty tree. Then it commits.
# 4. Writes SCRATCH/env.sh, which the agent's shell sources: the venv first on PATH,
#    TEAX_SIMKIT_PATH, and nothing that names a project root or an import path.
# 5. Writes SCRATCH/setup.md: the revisions, the install output, and the pieces supplied
#    ready-made, for the evidence.
set -euo pipefail

with_manifest=false
if [ "${1:-}" = --with-manifest ]; then
    with_manifest=true
    shift
fi
if [ $# -ne 4 ]; then
    echo "usage: setup_target.sh [--with-manifest] SCRATCH CODEGEN_REPO AGENTIC_REPO TEAX_CHECKOUT" >&2
    exit 2
fi
scratch=$1 codegen=$(realpath "$2") agentic=$(realpath "$3") teax=$(realpath "$4")
here=$(cd "$(dirname "$0")" && pwd)
target=$scratch/target
venv=$scratch/venv
simkit=$teax/packages/teax-simkit
if [ -e "$target" ]; then
    echo "setup_target.sh: $target already exists; use a fresh scratch directory" >&2
    exit 2
fi

bash "$here/../parity/make_venv.sh" "$scratch" "$codegen" "$agentic" "$teax"

git init -q "$target"
install_output=$(cd "$scratch" && env -u PYTHONPATH -u SYSML_CODEGEN_PROJECT_ROOT \
    "$venv/bin/sysml-codegen" install-commands "$target" --assistant claude < /dev/null)

fixture=tests/fixtures/study_station
pieces=(models station.snapshot.json pkg/station_study studies/study_route.py studies/oracle_entry.py)
if $with_manifest; then
    pieces+=(studies/manifest.json)
fi
git -C "$codegen" archive HEAD -- "${pieces[@]/#/$fixture/}" | tar -x -C "$target" --strip-components=3
printf '__pycache__/\n' > "$target/.gitignore"
git -C "$target" add -A
git -C "$target" -c user.name="SC4 dry run" -c user.email=dry-run@example.invalid \
    commit -q -m "Target for the SC4 dry run: the study layer installed, the fixture's ready-made pieces"

cat > "$scratch/env.sh" <<EOF
# Source this in the shell that runs the study agent in $target.
export PATH="$venv/bin:\$PATH"
export TEAX_SIMKIT_PATH="$simkit"
unset PYTHONPATH SYSML_CODEGEN_PROJECT_ROOT VIRTUAL_ENV
EOF

{
    echo "# SC4 dry run: the target"
    echo
    echo "Set up by \`evidence/dry-run/setup_target.sh\` on $(date -u +%Y-%m-%dT%H:%M:%SZ)."
    echo
    echo "- Target: \`$target\`, a git repository at \`$(git -C "$target" rev-parse HEAD)\`."
    echo "- Venv: \`$venv\` (\`$("$venv/bin/python" -V 2>&1)\`). Source \`$scratch/env.sh\` before starting the agent."
    echo "- Cut 3 (the manifest supplied ready-made): $($with_manifest && echo applied || echo "not applied")."
    echo "- \`SYSIDE_LICENSE_KEY\` is not set: no runbook step needs it, and the brief does not ask for \`integrate\`."
    echo
    echo "## Revisions"
    echo
    echo '```json'
    cat "$scratch/wheels/sources.json"
    echo '```'
    echo
    echo "## install-commands, run with no terminal"
    echo
    echo '```console'
    echo "\$ sysml-codegen install-commands $target --assistant claude < /dev/null"
    echo "$install_output"
    echo '```'
    echo
    echo "## Supplied ready-made"
    echo
    echo "The agent did not write these. Everything else in the target, the record included, comes from following the installed skill. Each piece is a committed file of sysml-codegen \`$fixture/\` at \`$(git -C "$codegen" rev-parse --short HEAD)\`, at the same relative path."
    echo
    echo "- the package, \`pkg/station_study/\`;"
    echo "- the models, \`models/\`, and their snapshot, \`station.snapshot.json\`;"
    echo "- the route, \`studies/study_route.py\` (\`execute_baseline\` and \`run_grid\`);"
    echo "- the oracle, \`studies/oracle_entry.py\`;"
    if $with_manifest; then
        echo "- the manifest, \`studies/manifest.json\` (cut 3);"
    fi
    echo "- \`.gitignore\`, holding \`__pycache__/\`, so loading the package leaves the tree clean."
    echo
    echo "## The target's tracked files"
    echo
    echo '```'
    git -C "$target" ls-files
    echo '```'
} > "$scratch/setup.md"
echo "setup_target.sh: target ready at $target; read $scratch/setup.md, then source $scratch/env.sh"
