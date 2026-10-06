---
id: 0006
title: No late-fill, direct literal actuals are valid, the embedded catalog is the sole schema authority
date: 2026-08-23
owner: Reid W
status: active
amended_by: []
superseded_by: null
provenance: "[OWNER]"
seams: [generation, contracts, teax]
supersedes: null
promoted_to: null
---

## Decision

Three owner decisions from the constraint-execution lifecycle contract ratification (2026-07-19)
that still bind every builder touching generation, contracts, or the TEAx seam:

1. **No public late-fill.** Supported codegen requires a fully representable graph plus ordinary
   declared external typed inputs. No public late-fill, post-build graph mutation, or default
   mutation seam exists.
2. **A direct literal-valued design attribute is a valid constraint actual.** It resolves through
   the same shared producer/exact-QN path as any calculation consumer. Requiring a model-authored
   passthrough calculation is a workaround, not conformance.
3. **Codegen's embedded model-contract catalog is the sole schema authority.** TEAx consumes it
   directly; no parallel reconstructed catalog, materializer, or identity stand-in exists.

## Why

In the owner's words, at ratification (payload preserved in
`.project/concepts/constraint-execution-authoritative-lifecycle-contract.md`, decisions D-1..D-3):

- D-1 `[OWNER-VERBATIM, 2026-07-19]`: "I really don't want to add support for 'public late-fill'
  — that sounds like a great way to allow bugs and enable injecting even more."
- D-2 `[OWNER-VERBATIM, 2026-07-19]`: "100% Option A. I am BLOW AWAY this wasn't already a
  requirement and this is a design gap. That is the whole fucking ethos of the graph-building."
- D-3 `[OWNER-VERBATIM, 2026-07-19]`: "100% Option A. We need to purge this mess."

The shared reasoning: a value that enters the pipeline outside the graph (late-fill), a
model-authored passthrough that exists only to satisfy the toolchain, and a second reconstructed
catalog are all seams where a wrong number can enter without a diagnostic. The graph is the one
place resolution is checked; everything the runtime consumes must come from it or be a declared
external input.

## Invariants established

- The lifecycle requires a fully representable graph; supported codegen exposes no late-fill or
  post-build mutation seam (contract invariant 26).
- A direct literal design-attribute actual reuses the same QN-keyed typed entry point as any
  calculation consumer (contract invariant 21).
- TEAx consumes exactly one catalog: the one codegen embeds and seals.

## Rejected alternatives

- Out of scope: a public post-build completion/mutation seam (D-1 option B) — rejected at
  ratification as a bug-injection channel.
- Out of scope: required model-authored passthrough calculations for literal actuals (D-2
  option B) — rejected; this also superseded the same-day WI-027 D7 passthrough design.
- Out of scope: a TEAx-side reconstructed schema/catalog (D-3 option B) — deleted rather than
  kept in sync.
