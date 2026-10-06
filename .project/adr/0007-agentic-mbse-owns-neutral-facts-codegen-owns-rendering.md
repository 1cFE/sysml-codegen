---
id: 0007
title: agentic-mbse owns neutral SysML facts; sysml-codegen owns rendering and assembly
date: 2026-08-23
owner: Reid W
status: active
amended_by: []
superseded_by: null
provenance: "[AGENT] (ratified by owner, 2026-07-10)"
seams: [agentic-mbse, extraction]
supersedes: null
promoted_to: CLAUDE.md
---

## Decision

agentic-mbse owns neutral SysML facts: AST walking, expression reconstruction, decomposition into
typed terms, literal/operator facts, and their diagnostics — anything true of the model regardless
of what consumes it. sysml-codegen owns everything Python- and pipeline-shaped: expression
rendering, codegen identifiers, channel names, entry points, and pipeline assembly. The dependency
is strictly one-way: sysml-codegen imports agentic-mbse, never the reverse.

## Why

Before the split (PUSH-DOWN, 2026-07), reusable AST-walking lived inside codegen's resolvers, so
agentic-mbse could not validate against the same SysML facts codegen relied on without duplicating
the logic or creating a reverse dependency — and duplicated fact-derivation is two chances to
disagree about what the model says. Putting the neutral facts in the shared layer gives every
consumer one answer; keeping rendering in codegen keeps SysML semantics out of reach of
codegen-specific naming and Python concerns.

A lesson worth keeping from the move itself: the independent epic audit found two undocumented
behavioral deviations introduced during the "behavior-preserving" relocation (a widened fallback
gate, and fallback branches that matched only a test mock). Both were reverted to the original
bodies. A boundary move is byte-faithful or it is a behavior change to be reviewed as one.

## Invariants established

- A fact about the model (what it declares, decomposes to, or means) is computed in agentic-mbse;
  a fact about the output (how it renders, what it is named) is computed in sysml-codegen.
- Dependency direction: sysml-codegen → agentic-mbse only.

## Rejected alternatives

- Out of scope: duplicating the decomposition logic in both repos — two derivations of the same
  model fact can silently diverge.
- Out of scope: a reverse dependency (agentic-mbse importing codegen containers) — the neutral
  layer must stay consumable by non-codegen tools.
