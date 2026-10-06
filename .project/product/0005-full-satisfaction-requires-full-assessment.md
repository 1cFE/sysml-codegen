---
id: 0005
title: A package never reports full satisfaction while authored gates went unassessed
date: 2026-08-23
owner: Reid W
status: active
amended_by: []
superseded_by: null
supersedes: null
provenance: "[AGENT] (ratified by owner, 2026-08-13)"
surfaces: [generation, reporting, teax]
checked: 2026-08-23 @ f0a7b0a
---

# P-005 — A package never reports full satisfaction while authored gates went unassessed

**Grade:** `[AGENT] (ratified by owner, 2026-08-13)` — an agent-originated promise built on
owner-ratified decisions. Challenge it by re-deriving against the reasoning in
`.project/adr/0010-coverage-truth-and-headline-semantics.md`, not by asking the owner.
**Serves:** [P-001](0001-design-search-free-variation.md) — a design search that cannot tell
"passed" from "nobody checked" cannot assess viability.

## The promise

Every authored constraint usage gets exactly one recorded disposition — `eligible`, `excluded`,
or `non_reaching`, each with a reason — before occurrence expansion; nothing a modeler wrote is
silently absent from the record. The report headline claims `full_satisfaction` only when every
applicable asserted gate was assessed and passed; an unassessed applicable gate yields
`partial_coverage`, a named state, never silence. A constraint-bearing model can therefore never
be mistaken for a constraint-free one.

## Authority

- `.project/adr/0010-coverage-truth-and-headline-semantics.md` — the decision record
  (`[AGENT] (ratified by owner, 2026-08-12)`), including why `all_satisfied` was renamed rather
  than redefined.
- `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md`, "Headline states
  and coverage truth" and invariant 1 as amended 2026-08-14 (`[INHERITED]`) — every authored
  constraint has a visible disposition.
- Filing note: the delivering items (CONSTRAINT-SEMANTICS Items 2–3, closed 2026-08-13) recorded
  at close that no ledger entry had been minted for this promise, deliberately — an entry without
  located authority would have been a provenance failure. This entry closes that recorded gap by
  resting on the ratified decision record above, and its grade claims ratified-agent authority,
  nothing more.

## Evidence

- `src/sysml_codegen/generation/coverage.py::coverage_account` — the one-directional account from the sealed
  catalog; `src/sysml_codegen/templates/constraint_types.py.jinja2` — the five headline tokens.
- `tests/unit/test_coverage_account.py`, `tests/unit/test_report_precedence.py`,
  `tests/unit/test_coverage_ledger_agreement.py`, `tests/conformance/test_coverage_preflight.py`.
