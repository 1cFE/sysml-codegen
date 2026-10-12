# SC4 dry run: the target

Set up by `evidence/dry-run/setup_target.sh` on 2026-10-12T19:42:48Z.

- Target: `/tmp/study-dryrun-20261012/target`, a git repository at `8851dabcfe21e720dcd91c139ca94bd019881a50`.
- Venv: `/tmp/study-dryrun-20261012/venv` (`Python 3.12.3`). Source `/tmp/study-dryrun-20261012/env.sh` before starting the agent.
- Cut 3 (the manifest supplied ready-made): not applied.
- `SYSIDE_LICENSE_KEY` is not set: no runbook step needs it, and the brief does not ask for `integrate`.

## Revisions

```json
{
  "sysml_codegen": {"commit": "f44c9916d2230f61a10a2c1e2c9a4bf3c4ce0f36", "wheel": "sysml_codegen-0.1.1-py3-none-any.whl", "sha256": "847269cfd807714db7bea96477019c45de19b42ca12981f172d5c26f55fadc29"},
  "agentic_mbse": {"commit": "db032d69e2f4c051a27c06613e82fb4d0ba046af", "wheel": "agentic_mbse-0.1.3-py3-none-any.whl", "sha256": "04a69b26134523073fc8d06a138cb9ebae8d9309fce61c369822c65fc601e6a8"},
  "teax": {"commit": "8d877460ac4f6f264561d916e40c1708adb13397", "simkit_root": "/home/reid/1cfe/teax/packages/teax-simkit"}
}
```

## install-commands, run with no terminal

```console
$ sysml-codegen install-commands /tmp/study-dryrun-20261012/target --assistant claude < /dev/null
Installed sysml-codegen's study layer in /tmp/study-dryrun-20261012/target
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

## Supplied ready-made

The agent did not write these. Everything else in the target, the record included, comes from following the installed skill. Each piece is a committed file of sysml-codegen `tests/fixtures/study_station/` at `f44c991`, at the same relative path.

- the package, `pkg/station_study/`;
- the models, `models/`, and their snapshot, `station.snapshot.json`;
- the route, `studies/study_route.py` (`execute_baseline` and `run_grid`);
- the oracle, `studies/oracle_entry.py`;
- `.gitignore`, holding `__pycache__/`, so loading the package leaves the tree clean.

## The target's tracked files

```
.agents/skills/run-study/SKILL.md
.agents/skills/run-study/annex-template.md
.agents/skills/run-study/integration-guide.md
.agents/skills/run-study/record-template.md
.agents/skills/run-study/runbook.md
.claude/commands/teax-completion.md
.claude/skills/run-study
.gitignore
.sysml-codegen/install.json
modeling_project/STUDY_POLICY.md
models/station.sysml
pkg/station_study/IMPLEMENTATION_BACKLOG.md
pkg/station_study/__init__.py
pkg/station_study/contracts/generation_manifest.json
pkg/station_study/contracts/model_contract.json
pkg/station_study/contracts/package_contract.json
pkg/station_study/contracts/verify.py
pkg/station_study/handwritten/__init__.py
pkg/station_study/handwritten/pumpstation/__init__.py
pkg/station_study/handwritten/pumpstation/pumpingcost_impl.py
pkg/station_study/handwritten/pumpstation/requiredflow_impl.py
pkg/station_study/inputs/__init__.py
pkg/station_study/inputs/station_params.json
pkg/station_study/modules/__init__.py
pkg/station_study/modules/constraints/__init__.py
pkg/station_study/modules/constraints/constraintreportaggregatormodule.py
pkg/station_study/modules/constraints/predicates.py
pkg/station_study/modules/pumpstation/__init__.py
pkg/station_study/modules/pumpstation/pumpingcost.py
pkg/station_study/modules/pumpstation/requiredflow.py
pkg/station_study/modules/pumpstation/stationpumpfitconstraintmodule.py
pkg/station_study/pipelines/__init__.py
pkg/station_study/pipelines/pipeline.yaml
pkg/station_study/primitives.py
pkg/station_study/schemas/__init__.py
pkg/station_study/schemas/constraint_types.py
pkg/station_study/schemas/station_params.py
pkg/station_study/tests/__init__.py
pkg/station_study/tests/test_implementations_runnable.py
station.snapshot.json
studies/oracle_entry.py
studies/study_route.py
```
