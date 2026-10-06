---
id: 0005
title: Exact-identity elaboration replaces string resolution, with no compatibility layer
date: 2026-08-23
owner: Reid W
status: active
amended_by: []
superseded_by: null
provenance: "[AGENT] (ratified by owner, 2026-08-14)"
seams: [extraction, elaboration, snapshot]
supersedes: null
promoted_to: CLAUDE.md
---

## Decision

References resolve against exact node identity — declaration identity and occurrence enumeration —
never by rendered-name or qualified-name string matching. The legacy string-resolution stack was
deleted outright at the 2026-08-14 cutover: no compatibility shim, no feature flag, no parallel
lane. v5 extraction snapshots are refused at load, by name; only v6 instance-graph snapshots are
accepted.

## Why

String matching resolves a name to a feature slot, and feature slots are shared across a whole
redefinition family — so `comp_a::length` and `comp_b::length` can land on one slot and a consumer
silently reads a sibling's value (the measured case computed 14.0 where the model said 6.0;
recorded in product `0002`). Exact identity makes that class of defect inexpressible instead of
individually patched.

The replacement-over-repair shape was decided by the failure of the alternative: the 2026-08
shadow-layer attempt ran an identity manifest beside the legacy resolver, and its artifact-to-
artifact gates could pass with zero runtime behavior change. The owner ratified elaborate-first
replacement over the parallel layer on 2026-08-07 for that reason.

No compatibility layer, because a kept legacy lane is a standing invitation to re-add a "small"
name-matching fallback — and any such fallback reintroduces the entire silent-wrong-binding class.
Deletion was accounted per-row in a closed ledger (`.project/ledger/ledger-4a.json`) with a
replacement test per deleted behavioral responsibility, and the absence is pinned by
`tests/conformance/test_public_authority_switch.py` and
`tests/unit/test_elaboration_import_boundaries.py`.

## Invariants established

- One resolution authority: elaborate, then project; a model that does not elaborate cleanly is
  refused, not accommodated.
- References resolve by node identity and occurrence enumeration; rendered names are display
  artifacts, never resolution keys.
- v5 snapshots are refused by name at load. No migration adapter exists.
- Self-binding is a modeling error, never reinterpreted as an outer reference.

## Rejected alternatives

- Out of scope: a shadow identity layer beside the legacy resolver was built, stopped, and
  archived superseded — its gates could pass without changing runtime behavior.
- Out of scope: a v5→v6 snapshot migration adapter is not provided, because a migrated snapshot
  would carry string-era resolution semantics into the exact route.
- Out of scope: keeping legacy code behind a flag was rejected in the cutover; deletion with a
  per-row replacement ledger was the accepted form.
