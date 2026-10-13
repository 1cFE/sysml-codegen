---
id: 0017
title: Study location settings are the one environment read reachable from the CLI
date: 2026-10-12
owner: Reid W
status: active
amended_by: []
superseded_by: null
provenance: "[AGENT] (design DD20, approved for planning by the orchestrator, 2026-10-12)"
seams: [study, cli, conformance]
supersedes: null
promoted_to: null
---

## Decision

Among the modules reachable from `sysml_codegen.cli`, exactly one reads the process environment: `sysml_codegen.study.roots`. It reads study location settings only: `SYSML_CODEGEN_PROJECT_ROOT`, `TEAX_SIMKIT_PATH`, and the copy of the environment `integrate` hands its producers. The conformance pin `test_no_cli_flag_or_environment_variable_selects_a_route` names it as its one allowance, and `test_the_study_package_reads_the_environment_only_in_roots` holds every other study module to none.

## Why

- The pin exists so that no environment variable can select a generation implementation. Study location settings do not touch generation authority; they say where a project and teax are.
- One named reader keeps the allowance auditable. The pin greps source text, comments included, so a second reader anywhere in the study package or the CLI fails a test.
- The ported tools read the environment in two places, `integrate`'s seam environment and `read_coverage`'s teax root. Both were lines the closed list already edited, so moving them into `roots` cost no extra byte change.

## Invariants established

- Only `sysml_codegen.study.roots` reads the environment among the modules reachable from `sysml_codegen.cli` (design I13).

## Rejected alternatives

- Hiding the read behind an `importlib` string was rejected: it hides the read from the pin instead of justifying it.
- Scoping the pin to the generation construction closure was rejected: a wider change to a pin the study layer does not own.
