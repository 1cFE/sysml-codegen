#!/usr/bin/env bash
# SC1's install transcript: design Appendix H1, steps 1-6, as one run.
#
# Usage: run_install.sh CODEGEN_WHEEL AGENTIC_WHEEL
#
# The two wheels come from build_wheels.sh, which writes sources.json beside them. This script
# refuses wheels whose sha256 sources.json does not record, because the transcript must name the
# revisions it installed. It installs both into a fresh venv under /tmp/study-install-<stamp>/,
# runs install-commands and agentic-mbse init there with no checkout on the import path, and
# writes every command, its output and the check of each expected observation to
# ../install-transcript.md. It exits 0 only when every check passes.
set -uo pipefail

here=$(cd "$(dirname "$0")" && pwd)
transcript=$(dirname "$here")/install-transcript.md
CW=$(realpath "$1")
AW=$(realpath "$2")
sources=$(dirname "$CW")/sources.json
if [ ! -f "$sources" ]; then
    echo "run_install.sh: no sources.json beside $CW; build the wheels with build_wheels.sh" >&2
    exit 2
fi
commits=$(python3 - "$sources" "$CW" "$AW" <<'PY'
import hashlib, json, sys
sources = json.load(open(sys.argv[1]))
for key, wheel in (("sysml_codegen", sys.argv[2]), ("agentic_mbse", sys.argv[3])):
    digest = hashlib.sha256(open(wheel, "rb").read()).hexdigest()
    if sources[key]["sha256"] != digest:
        sys.exit(f"run_install.sh: {wheel} has sha256 {digest}; sources.json records "
                 f"{sources[key]['sha256']} for {key}")
print(sources["sysml_codegen"]["commit"], sources["agentic_mbse"]["commit"])
PY
) || exit 2
read -r CODEGEN_COMMIT AGENTIC_COMMIT <<< "$commits"

S=/tmp/study-install-$(date +%Y%m%d-%H%M%S)
V=$S/venv
T=$S/target
mkdir -p "$T"
export S V T CW AW
# Every command runs from the scratch directory with nothing inherited that points at a checkout.
clean=(env -u PYTHONPATH -u SYSML_CODEGEN_PROJECT_ROOT -u VIRTUAL_ENV -u TEAX_SIMKIT_PATH)
failures=0
checks=0

log() { printf '%s\n' "$*" >> "$transcript"; }

# run COMMAND: record the command and its output in the transcript, in a console block.
run() {
    log '```console'
    log "\$ $1"
    (cd "$S" && "${clean[@]}" bash -c "$1") >> "$transcript" 2>&1
    local rc=$?
    [ "$rc" -eq 0 ] || log "(exit $rc)"
    log '```'
    return "$rc"
}

# check OBSERVATION CONDITION: record whether the expected observation holds.
check() {
    checks=$((checks + 1))
    if (cd "$S" && "${clean[@]}" bash -c "$2") > /dev/null 2>&1; then
        log "- PASS: $1"
    else
        log "- **FAIL**: $1 (\`$2\`)"
        failures=$((failures + 1))
    fi
}

: > "$transcript"
log "# SC1 install transcript (design Appendix H1)"
log ""
log "Written by \`evidence/install/run_install.sh\` on $(date -u +%Y-%m-%dT%H:%M:%SZ). Each step lists its commands with their output, then the checks of its expected observations."
log ""
log "- Scratch \`S\` = \`$S\`; venv \`V\` = \`\$S/venv\`; target \`T\` = \`\$S/target\`."
log "- sysml-codegen wheel \`CW\` = \`$CW\`, built from commit \`$CODEGEN_COMMIT\`."
log "- agentic-mbse wheel \`AW\` = \`$AW\`, built from commit \`$AGENTIC_COMMIT\`."
log "- Every command runs from \`\$S\` with \`PYTHONPATH\`, \`SYSML_CODEGEN_PROJECT_ROOT\`, \`VIRTUAL_ENV\` and \`TEAX_SIMKIT_PATH\` unset."
log ""

log "## 1. Build both wheels and install them into a fresh venv"
log ""
run 'cat "$(dirname "$CW")/sources.json"'
run 'unzip -Z1 "$CW" | grep -E "^sysml_codegen/(assets|study/schemas)/"'
check "the sysml-codegen wheel carries the seven shipped files under sysml_codegen/assets/" \
    '[ "$(unzip -Z1 "$CW" | grep -cE "^sysml_codegen/assets/.+[^/]$")" -eq 7 ]'
check "the sysml-codegen wheel carries the seven schemas under sysml_codegen/study/schemas/" \
    '[ "$(unzip -Z1 "$CW" | grep -cE "^sysml_codegen/study/schemas/.+\.schema\.json$")" -eq 7 ]'
run 'uv venv "$V" --python 3.12 -q'
run 'uv pip install --python "$V/bin/python" -q "$CW" "$AW"'
log ""

log "## 2. What is installed, and from where"
log ""
run 'uv pip show --python "$V/bin/python" agentic-mbse sysml-codegen'
run 'cat "$V"/lib/python3*/site-packages/agentic_mbse-*.dist-info/direct_url.json; echo; cat "$V"/lib/python3*/site-packages/sysml_codegen-*.dist-info/direct_url.json; echo'
run 'cd / && "$V/bin/python" -c "import sysml_codegen, agentic_mbse; from agentic_mbse.cli.installation import INSTALLER_API_VERSION; print(sysml_codegen.__file__); print(agentic_mbse.__file__); print(INSTALLER_API_VERSION)" | tee "$S/imports.txt"'
check "both packages import from the scratch venv" \
    '[ "$(grep -c "^$V/" "$S/imports.txt")" -eq 2 ]'
check "both are wheel installs, not editable ones" \
    'for f in "$V"/lib/python3*/site-packages/{agentic_mbse,sysml_codegen}-*.dist-info/direct_url.json; do grep -q "\"archive_info\"" "$f" && ! grep -q "\"editable\": *true" "$f" || exit 1; done'
check "no import path entry lies outside the interpreter and the venv" \
    'cd / && "$V/bin/python" -c "import sys; bad = [p for p in sys.path if p and not p.startswith((sys.prefix, sys.base_prefix))]; print(bad); sys.exit(1 if bad else 0)"'
check "the installed agentic-mbse carries the installer API installer/v1" \
    '[ "$(tail -1 "$S/imports.txt")" = installer/v1 ]'
log ""
log "The agentic-mbse installed is revision \`$AGENTIC_COMMIT\` (from \`sources.json\`, whose wheel digest matched). A wheel install records no VCS revision in \`direct_url.json\`, so the build commit is the revision."
log ""

log "## 3. List, then install with no terminal"
log ""
run '"$V/bin/sysml-codegen" install-commands "$T" --list | tee "$S/list.txt"'
check "--list names the run-study skill as a workflow" 'grep -q "run-study (workflow)" "$S/list.txt"'
check "--list names the teax-completion command" 'grep -q "teax-completion" "$S/list.txt"'
check "--list names the policy template's project document" \
    'grep -q "modeling_project/STUDY_POLICY.md (from STUDY_POLICY.md.template)" "$S/list.txt"'
check "--list writes nothing into the target" '[ -z "$(ls -A "$T")" ]'
run '"$V/bin/sysml-codegen" install-commands "$T" < /dev/null'
log ""

log "## 4. The target's files and the manifest"
log ""
run 'cd "$T" && find . \( -type f -o -type l \) | sort | tee "$S/files.txt"'
run 'readlink "$T/.claude/skills/run-study"'
run 'cat "$T/.sysml-codegen/install.json"'
cat > "$S/expected-files.txt" <<'EOF'
./.agents/skills/run-study/SKILL.md
./.agents/skills/run-study/annex-template.md
./.agents/skills/run-study/integration-guide.md
./.agents/skills/run-study/record-template.md
./.agents/skills/run-study/runbook.md
./.claude/commands/teax-completion.md
./.claude/skills/run-study
./.sysml-codegen/install.json
./modeling_project/STUDY_POLICY.md
EOF
assets=$(cd / && "$V/bin/python" -c "import sysml_codegen, os; print(os.path.join(os.path.dirname(sysml_codegen.__file__), 'assets'))")
export ASSETS=$assets
check "the target holds the five skill files, the Claude link, teax-completion.md, STUDY_POLICY.md and the manifest, and nothing else" \
    'diff <(LC_ALL=C sort "$S/expected-files.txt") <(LC_ALL=C sort "$S/files.txt")'
check "the Claude skill is a relative link to the shared folder" \
    '[ "$(readlink "$T/.claude/skills/run-study")" = ../../.agents/skills/run-study ]'
check "the installed skill files are the package's own bytes" \
    'diff -r "$ASSETS/skills/run-study" "$T/.agents/skills/run-study"'
check "teax-completion.md and STUDY_POLICY.md are the package's own bytes" \
    'cmp "$ASSETS/commands/teax-completion.md" "$T/.claude/commands/teax-completion.md" && cmp "$ASSETS/project_templates/STUDY_POLICY.md.template" "$T/modeling_project/STUDY_POLICY.md"'
check "the manifest records the seven managed entries, and not the policy" \
    'python3 -c "import json, sys; f = json.load(open(sys.argv[1]))[\"files\"]; sys.exit(0 if len(f) == 7 and not any(\"STUDY_POLICY\" in k for k in f) else 1)" "$T/.sysml-codegen/install.json"'
check "agentic-mbse's manifest was not written" '[ ! -e "$T/.agentic-mbse" ]'
log ""

log "## 5. An edited runbook is kept on a re-run, and replaced under --force"
log ""
run 'printf "\nA local edit.\n" >> "$T/.agents/skills/run-study/runbook.md"'
run '"$V/bin/sysml-codegen" install-commands "$T" < /dev/null | tee "$S/rerun.txt"'
check "the re-run says it preserved the edited runbook" \
    'grep -qF "Preserved .agents/skills/run-study/runbook.md: it was edited after sysml-codegen installed it" "$S/rerun.txt"'
check "the edit is still there" '[ "$(tail -1 "$T/.agents/skills/run-study/runbook.md")" = "A local edit." ]'
check "the re-run kept the policy as the project's document" \
    'grep -qF "Preserved modeling_project/STUDY_POLICY.md: it is this project'"'"'s document" "$S/rerun.txt"'
run '"$V/bin/sysml-codegen" install-commands "$T" --force < /dev/null'
check "--force put the shipped runbook back" 'cmp "$ASSETS/skills/run-study/runbook.md" "$T/.agents/skills/run-study/runbook.md"'
log ""

log "## 6. agentic-mbse init leaves the study layer intact, and a re-install leaves init's files"
log ""
snapshot_ours='cd "$T" && sha256sum .agents/skills/run-study/* .claude/commands/teax-completion.md modeling_project/STUDY_POLICY.md .sysml-codegen/install.json && readlink .claude/skills/run-study'
run "$snapshot_ours > \"\$S/ours-before.txt\" && cat \"\$S/ours-before.txt\""
run '"$V/bin/agentic-mbse" init "$T" < /dev/null | tee "$S/init.txt"'
run "$snapshot_ours > \"\$S/ours-after.txt\""
check "init changed none of the study layer's files, its link or its manifest" 'cmp "$S/ours-before.txt" "$S/ours-after.txt"'
check "init's output names nothing of the study layer" \
    '! grep -E "run-study|teax-completion|STUDY_POLICY|\.sysml-codegen" "$S/init.txt"'
run 'python3 -c "import json, sys; [print(name, sorted(json.load(open(name))[\"files\"])) for name in sys.argv[1:]]" "$T/.sysml-codegen/install.json" "$T/.agentic-mbse/install.json"'
check "agentic-mbse's manifest names none of the study layer's files" \
    'python3 -c "import json, sys; f = json.load(open(sys.argv[1]))[\"files\"]; sys.exit(1 if [k for k in f if \"run-study\" in k or \"teax-completion\" in k or \"STUDY_POLICY\" in k] else 0)" "$T/.agentic-mbse/install.json"'
run 'sha256sum "$T/.agentic-mbse/install.json" > "$S/theirs-before.txt"; "$V/bin/sysml-codegen" install-commands "$T" < /dev/null | tee "$S/after-init.txt"'
check "a re-install after init keeps back only the project's policy" \
    'grep -qF "Skipped, kept as they are (1):" "$S/after-init.txt" && grep -qF "  . modeling_project/STUDY_POLICY.md" "$S/after-init.txt"'
check "a re-install after init leaves agentic-mbse's manifest as init wrote it" \
    'sha256sum -c --quiet "$S/theirs-before.txt"'
log ""

log "## Result"
log ""
log "$checks checks, $failures failed. agentic-mbse revision installed: \`$AGENTIC_COMMIT\`; sysml-codegen revision installed: \`$CODEGEN_COMMIT\`."
echo "run_install.sh: $checks checks, $failures failed; transcript at $transcript"
[ "$failures" -eq 0 ]
