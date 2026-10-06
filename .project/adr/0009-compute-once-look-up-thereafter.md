---
id: 0009
title: Compute identifiers once, look up thereafter
date: 2026-08-23
owner: Reid W
status: active
amended_by: []
superseded_by: null
provenance: "[INHERITED: docs/architecture/modeling-assumptions.md §7 (ADR-007)]"
seams: [extraction, elaboration, generation]
supersedes: null
promoted_to: null
---

## Decision

Identifiers are computed once, at the front of the pipeline, and looked up thereafter. Downstream
code never re-derives or reconstructs an identifier. Resolutions are stored in a single
authoritative mapping, not re-derived at the point of use.

The naming convention uses `__` (double underscore) as the hierarchy separator throughout:
element names `Package__Part__Element`, parameter names `Package__Part__Element__param`, module
names the element name lowercased.

## Why

Two derivations of the same identifier are two chances to disagree, and they disagree silently: a
re-derived name that differs by one sanitization or separator rule produces a dangling channel or
a wrong wire, not an error at the derivation site. A lookup cannot diverge from its source. This
is the identifier-level form of the pipeline's general rule that semantics are settled once
(today: at elaboration/projection) and everything downstream renders what was settled.

## Re-homing note

This entry re-homes `docs/architecture/modeling-assumptions.md` §7 (ADR-007), triaged
builder-facing on 2026-08-21 — it binds the builder implementing identifier creation and reuse,
not the model author. §7 is now a pointer to this entry; the citation form
`docs/architecture/modeling-assumptions.md ADR-007` continues to resolve there. The original
section recorded no provenance; the decision is inherited as filed, and the Why above is this
entry's reconstruction rather than a recorded original.

## Invariants established

- One authoritative identifier mapping; downstream phases look up, never reconstruct.
- `__` is the hierarchy separator in every generated identifier (see also CLAUDE.md's ADR-003
  naming-convention summary; identifier taxonomy in
  `docs/architecture/reference/15-naming-conventions.md`).
