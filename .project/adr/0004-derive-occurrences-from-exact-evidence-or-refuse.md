---
id: 0004
title: Derive occurrences from exact parser evidence or refuse by name
date: 2026-08-23
owner: Reid W
status: active
amended_by: []
superseded_by: null
provenance: "[OWNER]"
seams: [extraction, elaboration]
supersedes: null
promoted_to: null
---

## Decision

Occurrence resolution derives from exact SysIDE evidence — the exact referent Feature, its owning
declaration, the consumer's domain occurrence, and the modeled containment path and multiplicity —
and produces exactly one concrete occurrence, a modeled plural result, or a named refusal. Never
proximity, arrival order, sole-candidate election, first match, class-name substrings, or
qualified-name prefix guessing. Extraction never silently drops or downgrades parser evidence:
warn-and-continue on evidence it cannot classify is itself a defect.

## Why

This is the builder-side mechanism of two owner-verbatim product rules:
`.project/product/0004-product-identity-parse-walk-emit.md` ("use a SysML v2 parser to interpret
the models … any manual fallback or workaround for an unresolved reference is a massive,
disgusting smell") and `.project/product/0003-no-workarounds-for-bad-models.md` ("we do NOT create
workarounds to accept bad models").

A proximity or plausibility rule can name an occurrence the model did not identify, and it does so
silently — the pipeline emits a confident wrong number instead of a diagnostic. The canonical
instance is the July stellarator package (recorded in product `0004`), where dropped bindings left
one physical quantity as several unwired keys and the runner hand-injected values. SysIDE already
supplies exact declaration authority; codegen's only legitimate work is contextual instantiation
from modeled facts. When the modeled context cannot derive the occurrence, the honest outcomes are
two: resolve through the parser, or refuse with a named diagnostic.

Owner class (usage-owned vs definition-owned referent) is one required input to the derivation,
not the whole answer — both classes still refuse when modeled context cannot derive the
occurrence.

## Invariants established

- Every occurrence selection is traceable to exact declaration evidence plus modeled containment;
  no resolution path forks into consumer-specific ladders.
- Unmapped or unclassifiable parser evidence fails by name; it is never warned past.
- A named refusal is a correct product outcome, not a degradation.

## Rejected alternatives

- Out of scope: proximity/arrival-order selection (nearest ancestor, descendant search,
  sole-candidate, first match) is not retained anywhere, because each can silently bind a wrong
  occurrence — the failure mode this decision exists to remove.
- Out of scope: indexed-element expressions (`cells#(2).mass`) are not supported; the decided
  behavior is an honest named refusal rather than a silent wrong answer (item
  stop-reinventing-the-parser, closed 2026-08-19; record in git history).
