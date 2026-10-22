---
id: 0008
title: check gives generate's answer without writing, and a refused generate writes nothing
date: 2026-10-22
owner: Reid Westwood
status: active
amended_by: []
superseded_by: null
supersedes: null
provenance: "[AGENT] (ratified by owner, 2026-10-21)"
surfaces: [cli, generation]
checked: 2026-10-22 @ d7366431
---

## Promise

`sysml-codegen check --models <dir>` tells a modeller whether `generate` would build the model, and it gets that answer by running the generator's own load and checking steps, then stopping before anything is written. Exit 0: `generate` would build it. Exit 1: `generate` would refuse it, with the same reason. Exit 2: usage error. A refused `generate` leaves its output folder exactly as it found it.

This is the only generation answer modellers get: agentic-mbse keeps no copy of the generator's rules and its workflow runs this command (agentic-mbse ADR 0004, P-0004).

## Authority

- `[OWNER-ratified 2026-10-20]` The generator's route alone decides refused or builds (`d7366431f425459053a46d764d5a327fda4c2f07:.project/active/subset-profile-screen/briefs/align.md` Q1); epic Item 2b success criterion "check and generate fail at the same preparation seam without mutating a sentinel destination" (agentic-mbse `.project/backlog/epic_executable-subset-contract.md`).
- `[AGENT] (ratified by owner, 2026-10-21)` `check` reports only the generator's answer: `.project/research/2026-10-21-generator-check-architecture-review/`; ADR 0019.
- Design D1-D4 (one route: `load_source` → `prepare` → `emit_package`; every model refusal inside `prepare`): `d7366431f425459053a46d764d5a327fda4c2f07:.project/active/subset-profile-screen/design.md`.

## Evidence

- `src/sysml_codegen/cli/prepare.py` (read-only), `cli/emit.py` (writes), `cli/destination.py`.
- `tests/conformance/refusal_cases/test_check_matches_stored_answers.py` (246 cases: `check` exit equals the stored generator outcome), `tests/conformance/test_check_command.py`, `tests/conformance/test_check_snapshots.py`, `tests/conformance/test_refusal_before_first_write.py`, `tests/conformance/refusal_cases/test_emit_reachability.py`.
