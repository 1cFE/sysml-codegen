# SC1 install transcript (design Appendix H1)

Written by `evidence/install/run_install.sh` on 2026-10-12T19:42:20Z. Each step lists its commands with their output, then the checks of its expected observations.

- Scratch `S` = `/tmp/study-install-20261012-124220`; venv `V` = `$S/venv`; target `T` = `$S/target`.
- sysml-codegen wheel `CW` = `/tmp/claude-1000/-home-reid-1cfe-agentic-mbse/8552c715-dee4-4a8a-8421-4029b4d8f180/scratchpad/o1/sysml_codegen-0.1.1-py3-none-any.whl`, built from commit `f44c9916d2230f61a10a2c1e2c9a4bf3c4ce0f36`.
- agentic-mbse wheel `AW` = `/tmp/claude-1000/-home-reid-1cfe-agentic-mbse/8552c715-dee4-4a8a-8421-4029b4d8f180/scratchpad/o1/agentic_mbse-0.1.3-py3-none-any.whl`, built from commit `db032d69e2f4c051a27c06613e82fb4d0ba046af`.
- Every command runs from `$S` with `PYTHONPATH`, `SYSML_CODEGEN_PROJECT_ROOT`, `VIRTUAL_ENV` and `TEAX_SIMKIT_PATH` unset.

## 1. Build both wheels and install them into a fresh venv

```console
$ cat "$(dirname "$CW")/sources.json"
{
  "sysml_codegen": {"commit": "f44c9916d2230f61a10a2c1e2c9a4bf3c4ce0f36", "wheel": "sysml_codegen-0.1.1-py3-none-any.whl", "sha256": "847269cfd807714db7bea96477019c45de19b42ca12981f172d5c26f55fadc29"},
  "agentic_mbse": {"commit": "db032d69e2f4c051a27c06613e82fb4d0ba046af", "wheel": "agentic_mbse-0.1.3-py3-none-any.whl", "sha256": "04a69b26134523073fc8d06a138cb9ebae8d9309fce61c369822c65fc601e6a8"}
}
```
```console
$ unzip -Z1 "$CW" | grep -E "^sysml_codegen/(assets|study/schemas)/"
sysml_codegen/assets/commands/teax-completion.md
sysml_codegen/assets/project_templates/STUDY_POLICY.md.template
sysml_codegen/assets/skills/run-study/SKILL.md
sysml_codegen/assets/skills/run-study/annex-template.md
sysml_codegen/assets/skills/run-study/integration-guide.md
sysml_codegen/assets/skills/run-study/record-template.md
sysml_codegen/assets/skills/run-study/runbook.md
sysml_codegen/study/schemas/axis_declaration.v1.schema.json
sysml_codegen/study/schemas/baseline_result.v1.schema.json
sysml_codegen/study/schemas/indicators.v1.schema.json
sysml_codegen/study/schemas/package_identity.v1.schema.json
sysml_codegen/study/schemas/preflight_results.v1.schema.json
sysml_codegen/study/schemas/study_package_manifest.v1.schema.json
sysml_codegen/study/schemas/verification_summary.v1.schema.json
```
- PASS: the sysml-codegen wheel carries the seven shipped files under sysml_codegen/assets/
- PASS: the sysml-codegen wheel carries the seven schemas under sysml_codegen/study/schemas/
```console
$ uv venv "$V" --python 3.12 -q
```
```console
$ uv pip install --python "$V/bin/python" -q "$CW" "$AW"
```

## 2. What is installed, and from where

```console
$ uv pip show --python "$V/bin/python" agentic-mbse sysml-codegen
Using Python 3.12.11 environment at: venv
Name: agentic-mbse
Version: 0.1.3
Location: /tmp/study-install-20261012-124220/venv/lib/python3.12/site-packages
Requires: img2table, pydantic, pymupdf, pymupdf4llm, python-dotenv, pyyaml, syside
Required-by: sysml-codegen
---
Name: sysml-codegen
Version: 0.1.1
Location: /tmp/study-install-20261012-124220/venv/lib/python3.12/site-packages
Requires: agentic-mbse, jinja2, pydantic, pyyaml
Required-by:
```
```console
$ cat "$V"/lib/python3*/site-packages/agentic_mbse-*.dist-info/direct_url.json; echo; cat "$V"/lib/python3*/site-packages/sysml_codegen-*.dist-info/direct_url.json; echo
{"url":"file:///tmp/claude-1000/-home-reid-1cfe-agentic-mbse/8552c715-dee4-4a8a-8421-4029b4d8f180/scratchpad/o1/agentic_mbse-0.1.3-py3-none-any.whl","archive_info":{}}
{"url":"file:///tmp/claude-1000/-home-reid-1cfe-agentic-mbse/8552c715-dee4-4a8a-8421-4029b4d8f180/scratchpad/o1/sysml_codegen-0.1.1-py3-none-any.whl","archive_info":{}}
```
```console
$ cd / && "$V/bin/python" -c "import sysml_codegen, agentic_mbse; from agentic_mbse.cli.installation import INSTALLER_API_VERSION; print(sysml_codegen.__file__); print(agentic_mbse.__file__); print(INSTALLER_API_VERSION)" | tee "$S/imports.txt"
/tmp/study-install-20261012-124220/venv/lib/python3.12/site-packages/sysml_codegen/__init__.py
/tmp/study-install-20261012-124220/venv/lib/python3.12/site-packages/agentic_mbse/__init__.py
installer/v1
```
- PASS: both packages import from the scratch venv
- PASS: both are wheel installs, not editable ones
- PASS: no import path entry lies outside the interpreter and the venv
- PASS: the installed agentic-mbse carries the installer API installer/v1

The agentic-mbse installed is revision `db032d69e2f4c051a27c06613e82fb4d0ba046af` (from `sources.json`, whose wheel digest matched). A wheel install records no VCS revision in `direct_url.json`, so the build commit is the revision.

## 3. List, then install with no terminal

```console
$ "$V/bin/sysml-codegen" install-commands "$T" --list | tee "$S/list.txt"
Skills, for Claude Code and Codex (.agents/skills/, linked from .claude/skills/):
  - run-study (workflow): Run a parameter study against a generated model package, or read a finished study's record and synthesize it. Use when asked to sweep, search, or explore a design space; to test how an objective or a constraint responds to a parameter; to find where a feasible region ends; or to pick up someone else's finished study and say what it found. Triggers: "run a study", "sweep R and a", "design search", "explore the design space", "how sensitive is the objective to", "where does the constraint bind", "find the feasible region", "study whatever you can find in this package", "what did this study find", "synthesize this study", "pick up the results in a studies directory", "administer this record", any request to sweep a model or interpret a study record.
Claude commands (.claude/commands/):
  - teax-completion
Project documents, created once and then the project's own:
  - modeling_project/STUDY_POLICY.md (from STUDY_POLICY.md.template)
```
- PASS: --list names the run-study skill as a workflow
- PASS: --list names the teax-completion command
- PASS: --list names the policy template's project document
- PASS: --list writes nothing into the target
```console
$ "$V/bin/sysml-codegen" install-commands "$T" < /dev/null
Installed sysml-codegen's study layer in /tmp/study-install-20261012-124220/target
Symlinked (1):
  @ .claude/skills/run-study
Created (7):
  + .agents/skills/run-study/SKILL.md
  + .agents/skills/run-study/annex-template.md
  + .agents/skills/run-study/integration-guide.md
  + .agents/skills/run-study/record-template.md
  + .agents/skills/run-study/runbook.md
  + .claude/commands/teax-completion.md
  + modeling_project/STUDY_POLICY.md
```

## 4. The target's files and the manifest

```console
$ cd "$T" && find . \( -type f -o -type l \) | sort | tee "$S/files.txt"
./.agents/skills/run-study/annex-template.md
./.agents/skills/run-study/integration-guide.md
./.agents/skills/run-study/record-template.md
./.agents/skills/run-study/runbook.md
./.agents/skills/run-study/SKILL.md
./.claude/commands/teax-completion.md
./.claude/skills/run-study
./modeling_project/STUDY_POLICY.md
./.sysml-codegen/install.json
```
```console
$ readlink "$T/.claude/skills/run-study"
../../.agents/skills/run-study
```
```console
$ cat "$T/.sysml-codegen/install.json"
{
  "version": 2,
  "files": {
    ".agents/skills/run-study/SKILL.md": "1707a04eaae854d49ac0ad62f3916a644797372998e27caefaa38b557d471b75",
    ".agents/skills/run-study/annex-template.md": "767d753d9294798873cad7a3cdf06a7e590ae2b745d39d85c4a604c9040aa6ee",
    ".agents/skills/run-study/integration-guide.md": "0ab76bd045b0724492f61b1686fa14cde37721159f914a4f00610e37b3452a19",
    ".agents/skills/run-study/record-template.md": "3d7da51c93fb10c0bf45614d36fa1f0fb0fdef9b0d763af38650308bb58b23dd",
    ".agents/skills/run-study/runbook.md": "a323f85af9b10f324f82940670abaa6cb15a5c4c00f8228d86cd8b6acb2efdc7",
    ".claude/skills/run-study": "link:../../.agents/skills/run-study",
    ".claude/commands/teax-completion.md": "fec3b4fabe91e98e7705323e7e07b796b17f651d09d6762a9d9e9bfa0dddd2c6"
  }
}
```
- PASS: the target holds the five skill files, the Claude link, teax-completion.md, STUDY_POLICY.md and the manifest, and nothing else
- PASS: the Claude skill is a relative link to the shared folder
- PASS: the installed skill files are the package's own bytes
- PASS: teax-completion.md and STUDY_POLICY.md are the package's own bytes
- PASS: the manifest records the seven managed entries, and not the policy
- PASS: agentic-mbse's manifest was not written

## 5. An edited runbook is kept on a re-run, and replaced under --force

```console
$ printf "\nA local edit.\n" >> "$T/.agents/skills/run-study/runbook.md"
```
```console
$ "$V/bin/sysml-codegen" install-commands "$T" < /dev/null | tee "$S/rerun.txt"
Preserved .agents/skills/run-study/runbook.md: it was edited after sysml-codegen installed it; re-run interactively or with --force to replace it
Preserved modeling_project/STUDY_POLICY.md: it is this project's document; --force replaces it
Installed sysml-codegen's study layer in /tmp/study-install-20261012-124220/target
Symlinked (1):
  @ .claude/skills/run-study
Updated, rewritten with the shipped bytes (5):
  ~ .agents/skills/run-study/SKILL.md
  ~ .agents/skills/run-study/annex-template.md
  ~ .agents/skills/run-study/integration-guide.md
  ~ .agents/skills/run-study/record-template.md
  ~ .claude/commands/teax-completion.md
Skipped, kept as they are (2):
  . .agents/skills/run-study/runbook.md
  . modeling_project/STUDY_POLICY.md
```
- PASS: the re-run says it preserved the edited runbook
- PASS: the edit is still there
- PASS: the re-run kept the policy as the project's document
```console
$ "$V/bin/sysml-codegen" install-commands "$T" --force < /dev/null
Installed sysml-codegen's study layer in /tmp/study-install-20261012-124220/target
Symlinked (1):
  @ .claude/skills/run-study
Updated, rewritten with the shipped bytes (7):
  ~ .agents/skills/run-study/SKILL.md
  ~ .agents/skills/run-study/annex-template.md
  ~ .agents/skills/run-study/integration-guide.md
  ~ .agents/skills/run-study/record-template.md
  ~ .agents/skills/run-study/runbook.md
  ~ .claude/commands/teax-completion.md
  ~ modeling_project/STUDY_POLICY.md
```
- PASS: --force put the shipped runbook back

## 6. agentic-mbse init leaves the study layer intact, and a re-install leaves init's files

```console
$ cd "$T" && sha256sum .agents/skills/run-study/* .claude/commands/teax-completion.md modeling_project/STUDY_POLICY.md .sysml-codegen/install.json && readlink .claude/skills/run-study > "$S/ours-before.txt" && cat "$S/ours-before.txt"
767d753d9294798873cad7a3cdf06a7e590ae2b745d39d85c4a604c9040aa6ee  .agents/skills/run-study/annex-template.md
0ab76bd045b0724492f61b1686fa14cde37721159f914a4f00610e37b3452a19  .agents/skills/run-study/integration-guide.md
3d7da51c93fb10c0bf45614d36fa1f0fb0fdef9b0d763af38650308bb58b23dd  .agents/skills/run-study/record-template.md
a323f85af9b10f324f82940670abaa6cb15a5c4c00f8228d86cd8b6acb2efdc7  .agents/skills/run-study/runbook.md
1707a04eaae854d49ac0ad62f3916a644797372998e27caefaa38b557d471b75  .agents/skills/run-study/SKILL.md
fec3b4fabe91e98e7705323e7e07b796b17f651d09d6762a9d9e9bfa0dddd2c6  .claude/commands/teax-completion.md
d8d4d83e438230fabf6cdd6fd51f83f390f1049ea7e9db0b3de342845895248b  modeling_project/STUDY_POLICY.md
9cc1310661c399927e83dc00b5c55f3802b93183c7051961bd51927e99a91e35  .sysml-codegen/install.json
../../.agents/skills/run-study
```
```console
$ "$V/bin/agentic-mbse" init "$T" < /dev/null | tee "$S/init.txt"

Initialized MBSE project in /tmp/study-install-20261012-124220/target

Symlinked (27):
  @ .claude/skills/analyze-models
  @ .claude/skills/audit-models
  @ .claude/skills/backlog
  @ .claude/skills/design-model
  @ .claude/skills/epic-decomposition
  @ .claude/skills/formalize-intent
  @ .claude/skills/implement-model
  @ .claude/skills/manage-sources
  @ .claude/skills/model-validation
  @ .claude/skills/narrate-goal
  @ .claude/skills/onboard
  @ .claude/skills/orchestrate-modeling
  @ .claude/skills/pdf-analysis
  @ .claude/skills/plan-model
  @ .claude/skills/project-structure
  @ .claude/skills/python-debugger
  @ .claude/skills/quick-model
  @ .claude/skills/record-learning
  @ .claude/skills/requirements-tracking
  @ .claude/skills/research
  @ .claude/skills/review-model
  @ .claude/skills/run-goal
  @ .claude/skills/source-traceability
  @ .claude/skills/spec-model
  @ .claude/skills/status
  @ .claude/skills/sysml-conventions
  @ .claude/skills/toolkit-awareness

Created (72):
  + .gitignore
  + knowledge/SOURCE_INDEX.md
  + .agents/skills/analyze-models/SKILL.md
  + .agents/skills/audit-models/SKILL.md
  + .agents/skills/backlog/SKILL.md
  + .agents/skills/design-model/SKILL.md
  + .agents/skills/epic-decomposition/SKILL.md
  + .agents/skills/formalize-intent/SKILL.md
  + .agents/skills/implement-model/SKILL.md
  + .agents/skills/manage-sources/SKILL.md
  + .agents/skills/model-validation/SKILL.md
  + .agents/skills/narrate-goal/SKILL.md
  + .agents/skills/onboard/SKILL.md
  + .agents/skills/orchestrate-modeling/SKILL.md
  + .agents/skills/pdf-analysis/SKILL.md
  + .agents/skills/pdf-analysis/references/extraction-details.md
  + .agents/skills/pdf-analysis/scripts/extract_page.py
  + .agents/skills/plan-model/SKILL.md
  + .agents/skills/project-structure/SKILL.md
  + .agents/skills/python-debugger/SKILL.md
  + .agents/skills/python-debugger/references/debugging_internals.md
  + .agents/skills/python-debugger/scripts/claude_debugger.py
  + .agents/skills/quick-model/SKILL.md
  + .agents/skills/record-learning/SKILL.md
  + .agents/skills/requirements-tracking/SKILL.md
  + .agents/skills/research/SKILL.md
  + .agents/skills/review-model/SKILL.md
  + .agents/skills/run-goal/SKILL.md
  + .agents/skills/source-traceability/SKILL.md
  + .agents/skills/spec-model/SKILL.md
  + .agents/skills/status/SKILL.md
  + .agents/skills/sysml-conventions/SKILL.md
  + .agents/skills/sysml-conventions/references/stencils.md
  + .agents/skills/toolkit-awareness/SKILL.md
  + .agents/skills/toolkit-awareness/references/python-environment.md
  + .agentic-mbse/claude.md
  + CLAUDE.md
  + .claude/agents/kerml-expert.md
  + .claude/agents/python-debugger.md
  + .claude/agents/syside-expert.md
  + .claude/agents/sysml-expert.md
  + .claude/agents/sysmlv2-validator.md
  + .agentic-mbse/codex.md
  + AGENTS.md
  + .codex/agents/kerml-expert.toml
  + .codex/agents/python-debugger.toml
  + .codex/agents/syside-expert.toml
  + .codex/agents/sysml-expert.toml
  + .codex/agents/sysmlv2-validator.toml
  + .codex/config.toml
  + .claude/hooks/ruff-format.sh
  + README.md
  + modeling_project/OVERVIEW.md
  + work/BACKLOG.md
  + work/learnings/RAW_LEARNINGS.md
  + knowledge/KNOWLEDGE.md
  + modeling_project/ARCHITECTURE.md
  + modeling_project/REQUIREMENTS.md
  + modeling_project/VALIDATION_MATRIX.md
  + tests/models/test_example.py
  + tests/conftest.py
  + data/traceability_matrix.csv
  + modeling_project/MODELING_GUIDE.md
  + modeling_project/MODELING_PROCESS.md
  + work/EPIC_GUIDE.md
  + work/backlog/epic_template.md
  + work/orchestration/GOAL_RUNBOOK.md
  + work/orchestration/goal-templates/goal.md
  + work/orchestration/goal-templates/trail.md
  + work/orchestration/goal-templates/learnings.md
  + tests/orchestration/test_narrative_links.py
  + .claude/settings.json (3 permissions)

Next steps:
  1. Run /onboard in Claude or $onboard in Codex to configure your project
  2. Or manually edit knowledge/SOURCE_INDEX.md and start with the design-model skill
```
```console
$ cd "$T" && sha256sum .agents/skills/run-study/* .claude/commands/teax-completion.md modeling_project/STUDY_POLICY.md .sysml-codegen/install.json && readlink .claude/skills/run-study > "$S/ours-after.txt"
767d753d9294798873cad7a3cdf06a7e590ae2b745d39d85c4a604c9040aa6ee  .agents/skills/run-study/annex-template.md
0ab76bd045b0724492f61b1686fa14cde37721159f914a4f00610e37b3452a19  .agents/skills/run-study/integration-guide.md
3d7da51c93fb10c0bf45614d36fa1f0fb0fdef9b0d763af38650308bb58b23dd  .agents/skills/run-study/record-template.md
a323f85af9b10f324f82940670abaa6cb15a5c4c00f8228d86cd8b6acb2efdc7  .agents/skills/run-study/runbook.md
1707a04eaae854d49ac0ad62f3916a644797372998e27caefaa38b557d471b75  .agents/skills/run-study/SKILL.md
fec3b4fabe91e98e7705323e7e07b796b17f651d09d6762a9d9e9bfa0dddd2c6  .claude/commands/teax-completion.md
d8d4d83e438230fabf6cdd6fd51f83f390f1049ea7e9db0b3de342845895248b  modeling_project/STUDY_POLICY.md
9cc1310661c399927e83dc00b5c55f3802b93183c7051961bd51927e99a91e35  .sysml-codegen/install.json
```
- PASS: init changed none of the study layer's files, its link or its manifest
- PASS: init's output names nothing of the study layer
```console
$ python3 -c "import json, sys; [print(name, sorted(json.load(open(name))[\"files\"])) for name in sys.argv[1:]]" "$T/.sysml-codegen/install.json" "$T/.agentic-mbse/install.json"
/tmp/study-install-20261012-124220/target/.sysml-codegen/install.json ['.agents/skills/run-study/SKILL.md', '.agents/skills/run-study/annex-template.md', '.agents/skills/run-study/integration-guide.md', '.agents/skills/run-study/record-template.md', '.agents/skills/run-study/runbook.md', '.claude/commands/teax-completion.md', '.claude/skills/run-study']
/tmp/study-install-20261012-124220/target/.agentic-mbse/install.json ['.agentic-mbse/claude.md', '.agentic-mbse/codex.md', '.agents/skills/analyze-models/SKILL.md', '.agents/skills/audit-models/SKILL.md', '.agents/skills/backlog/SKILL.md', '.agents/skills/design-model/SKILL.md', '.agents/skills/epic-decomposition/SKILL.md', '.agents/skills/formalize-intent/SKILL.md', '.agents/skills/implement-model/SKILL.md', '.agents/skills/manage-sources/SKILL.md', '.agents/skills/model-validation/SKILL.md', '.agents/skills/narrate-goal/SKILL.md', '.agents/skills/onboard/SKILL.md', '.agents/skills/orchestrate-modeling/SKILL.md', '.agents/skills/pdf-analysis/SKILL.md', '.agents/skills/pdf-analysis/references/extraction-details.md', '.agents/skills/pdf-analysis/scripts/extract_page.py', '.agents/skills/plan-model/SKILL.md', '.agents/skills/project-structure/SKILL.md', '.agents/skills/python-debugger/SKILL.md', '.agents/skills/python-debugger/references/debugging_internals.md', '.agents/skills/python-debugger/scripts/claude_debugger.py', '.agents/skills/quick-model/SKILL.md', '.agents/skills/record-learning/SKILL.md', '.agents/skills/requirements-tracking/SKILL.md', '.agents/skills/research/SKILL.md', '.agents/skills/review-model/SKILL.md', '.agents/skills/run-goal/SKILL.md', '.agents/skills/source-traceability/SKILL.md', '.agents/skills/spec-model/SKILL.md', '.agents/skills/status/SKILL.md', '.agents/skills/sysml-conventions/SKILL.md', '.agents/skills/sysml-conventions/references/stencils.md', '.agents/skills/toolkit-awareness/SKILL.md', '.agents/skills/toolkit-awareness/references/python-environment.md', '.claude/agents/kerml-expert.md', '.claude/agents/python-debugger.md', '.claude/agents/syside-expert.md', '.claude/agents/sysml-expert.md', '.claude/agents/sysmlv2-validator.md', '.claude/hooks/ruff-format.sh', '.claude/skills/analyze-models', '.claude/skills/audit-models', '.claude/skills/backlog', '.claude/skills/design-model', '.claude/skills/epic-decomposition', '.claude/skills/formalize-intent', '.claude/skills/implement-model', '.claude/skills/manage-sources', '.claude/skills/model-validation', '.claude/skills/narrate-goal', '.claude/skills/onboard', '.claude/skills/orchestrate-modeling', '.claude/skills/pdf-analysis', '.claude/skills/plan-model', '.claude/skills/project-structure', '.claude/skills/python-debugger', '.claude/skills/quick-model', '.claude/skills/record-learning', '.claude/skills/requirements-tracking', '.claude/skills/research', '.claude/skills/review-model', '.claude/skills/run-goal', '.claude/skills/source-traceability', '.claude/skills/spec-model', '.claude/skills/status', '.claude/skills/sysml-conventions', '.claude/skills/toolkit-awareness', '.codex/agents/kerml-expert.toml', '.codex/agents/python-debugger.toml', '.codex/agents/syside-expert.toml', '.codex/agents/sysml-expert.toml', '.codex/agents/sysmlv2-validator.toml', 'AGENTS.md', 'CLAUDE.md', 'modeling_project/MODELING_GUIDE.md', 'modeling_project/MODELING_PROCESS.md', 'tests/orchestration/test_narrative_links.py', 'work/EPIC_GUIDE.md', 'work/backlog/epic_template.md', 'work/orchestration/GOAL_RUNBOOK.md', 'work/orchestration/goal-templates/goal.md', 'work/orchestration/goal-templates/learnings.md', 'work/orchestration/goal-templates/trail.md']
```
- PASS: agentic-mbse's manifest names none of the study layer's files
```console
$ sha256sum "$T/.agentic-mbse/install.json" > "$S/theirs-before.txt"; "$V/bin/sysml-codegen" install-commands "$T" < /dev/null | tee "$S/after-init.txt"
Preserved modeling_project/STUDY_POLICY.md: it is this project's document; --force replaces it
Installed sysml-codegen's study layer in /tmp/study-install-20261012-124220/target
Symlinked (1):
  @ .claude/skills/run-study
Updated, rewritten with the shipped bytes (6):
  ~ .agents/skills/run-study/SKILL.md
  ~ .agents/skills/run-study/annex-template.md
  ~ .agents/skills/run-study/integration-guide.md
  ~ .agents/skills/run-study/record-template.md
  ~ .agents/skills/run-study/runbook.md
  ~ .claude/commands/teax-completion.md
Skipped, kept as they are (1):
  . modeling_project/STUDY_POLICY.md
```
- PASS: a re-install after init keeps back only the project's policy
- PASS: a re-install after init leaves agentic-mbse's manifest as init wrote it

## Result

25 checks, 0 failed. agentic-mbse revision installed: `db032d69e2f4c051a27c06613e82fb4d0ba046af`; sysml-codegen revision installed: `f44c9916d2230f61a10a2c1e2c9a4bf3c4ce0f36`.
