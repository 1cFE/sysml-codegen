---
id: 0010
title: Coverage truth and headline semantics
date: 2026-08-23
owner: Reid W
status: active
amended_by: []
superseded_by: null
provenance: "[AGENT] (ratified by owner, 2026-08-12)"
seams: [generation, teax, reporting]
supersedes: null
promoted_to: null
---

## Decision

A constraint report's headline precedence is violation → indeterminate → full satisfaction →
partial coverage → not assessed. Full satisfaction is a **coverage claim**: every applicable
asserted gate was assessed and passed. The partial-coverage state carries the case where an
applicable asserted gate exists and went unassessed. Filed 2026-08-12 under CONSTRAINT-SEMANTICS
Item 1; agent-proposed, owner-ratified — challengeable by re-deriving against the reasoning below,
not by asking the owner.

## Why

A headline that cannot distinguish "checked and passed" from "not checked" is not evidence. Before
this decision, two rules made the headline unreliable: a plain `constraint` was cataloged but
never executed, and the headline claimed satisfaction whenever *any* assessed result passed — so a
model could read fully satisfied while every gate the modeler wrote went unassessed. The change
makes the claim honest at the cost of one additional state, and the study layer keeps a design
point at the boundary rather than accepting it on a coverage gap.

The prior contract text this supersedes: lifecycle invariant 33's precedence
"violation, then indeterminate, then all satisfied, then not assessed" and companion LC-E11's
"else any assessed result → `all_satisfied`".

## Scope

This entry governs the headline vocabulary's **meaning**. The definitions live in the lifecycle
contract's "Headline states and coverage truth" subsection
(`.project/concepts/constraint-execution-authoritative-lifecycle-contract.md`), the one authority
for both repositories' vocabularies. The concrete token spellings and code landed 2026-08-13
(CONSTRAINT-SEMANTICS Item 3): the five report tokens are `violation`, `indeterminate`,
`full_satisfaction`, `partial_coverage`, `not_assessed`
(`src/sysml_codegen/templates/constraint_types.py.jinja2`), each mapping to exactly one runtime token in TEAx's
`CANONICAL_HEADLINE`; the coverage account beside the headline is derived by
`src/sysml_codegen/generation/coverage.py::coverage_account`. `all_satisfied` was **renamed rather than redefined**,
so a stale reader refuses by name instead of misreading the strengthened claim.

Consequences were filed into the lifecycle contract: invariants 1, 9, 28, 32, 33, 46/46a, 48, new
61, Appendix B/C cells; companions LC-E05/E06/E10/E11/E12 and LC-G07.

## Re-homing note

This entry re-homes `docs/architecture/modeling-assumptions.md` §9 (ADR-009), triaged
builder-facing on 2026-08-21 — it binds report token spellings, generation templates, TEAx's
`CANONICAL_HEADLINE`, and the normalization seam, not the model author. §9 is now a pointer to
this entry; the citation form `docs/architecture/modeling-assumptions.md ADR-009` continues to
resolve there. Product `0001`'s Authority block cites this decision; the product promise built on
it is `.project/product/0005-full-satisfaction-requires-full-assessment.md`.

## Invariants established

- Full satisfaction requires `unassessed_gate_count == 0` and `assessed_gate_count > 0`.
- A headline state never conflates absence of assessment with success.
