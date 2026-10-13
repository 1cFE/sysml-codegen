---
id: 0007
title: Targets install the study layer from sysml-codegen, versioned with the generator whose contracts it reads
date: 2026-10-12
owner: Reid W
status: active
amended_by: []
superseded_by: null
supersedes: null
provenance: "[OWNER] (WRAP-SPLIT epic header, 2026-10-06); package form [AGENT] (design D6)"
surfaces: [study, installer, cli]
checked: 2026-10-12 @ 4dfe275
---

## Promise

A target project gets the study layer from sysml-codegen. `sysml-codegen install-commands` installs the `run-study` skill (runbook, record template, annex template, integration guide) and a study-policy template that it never overwrites. The skill's tools run as `sysml-codegen study indicators|preflight|verify|integrate` from the `sysml_codegen.study` package. They ship in the same distribution as the generator, so the code that reads a generated package's contracts is always the version that wrote them. The shipped text and tools are general: a target declares its own repo gates, environment and locations, and no consumer's names or paths are built in.

This is the "study layer owns exploration and decisions" role that [P-001](0001-design-search-free-variation.md) gives it. [P-004](0004-product-identity-parse-walk-emit.md) defines what the generator is, and does not exclude this layer.

## Authority

- `[OWNER]` WRAP-SPLIT epic header, 2026-10-06: the study layer ships from sysml-codegen, which owns the generated-package contracts the tools read (agentic-mbse `.project/backlog/epic_wrap-split.md:18`). `[OWNER-VERBATIM]` "All these need to be ported and generalized … and installed like everything else" (agentic-mbse `.project/research/20261005-204804_wrap-split-agentic-mbse-fusion-tea.md:18`).
- `[AGENT]` Package form, design D6: one distribution, not a separate package and not files copied into each target, because either would split the contract reader from the generator (`4dfe275:.project/active/study-layer-to-codegen/design.md`).
- ADR-0015 (the project-root anchor), ADR-0016 (installer reuse through `installer/v1`) and ADR-0017 (the one environment read).

## Evidence

- `src/sysml_codegen/study/`, `src/sysml_codegen/cli/install.py`, `src/sysml_codegen/cli/study.py`, `src/sysml_codegen/assets/`; `tests/unit/test_install_commands.py` and the `tests/study/` suite.
- WRAP-SPLIT Item 3 evidence at `4dfe275:.project/active/study-layer-to-codegen/evidence/`: a wheel install into an empty project (25 of 25), a fresh-target dry run, and parity of 28 of 28 cases with fusion-tea's originals. fusion-tea's adoption runbook and kit are in agentic-mbse `.project/completed/20261012_study-layer-to-codegen/`.

## Scope

`install-commands` needs agentic-mbse `d42c8b9` or later (`installer/v1`). teax is an optional dependency, imported only when a tool needs it.
