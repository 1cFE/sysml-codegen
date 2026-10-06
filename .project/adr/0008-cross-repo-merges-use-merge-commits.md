---
id: 0008
title: Cross-repo merges use explicit merge commits, never squash or rebase
date: 2026-08-23
owner: Reid W
status: active
amended_by: []
superseded_by: null
provenance: "[AGENT] (ratified by owner, 2026-08-20)"
seams: [git-workflow, fusion-tea]
supersedes: null
promoted_to: null
---

## Decision

Merges to `main` in this repository (and its companions agentic-mbse and fusion-tea) use explicit
merge commits. Never squash, never rebase.

## Why

fusion-tea pins the exact sysml-codegen commit SHA and wheel hash its provenance evidence was
sealed against. A squash or rebase merge replaces the merged commits with new SHAs, making the
pinned commit unreachable from `main` — which forces a repin and regeneration of provenance
evidence for work that did not change. An explicit merge commit keeps every pinned SHA reachable.

This was applied at the 2026-08-20 stop-reinventing-the-parser shipment: all three repositories
merged with explicit merge commits in dependency order, and fusion-tea's provenance suite passed
against the sealed wheels with no repin.

## Invariants established

- Any commit another repository pins by SHA remains reachable from `main` after every merge.

## Rejected alternatives

- Out of scope: squash merges for a "clean history" — the clean history costs cross-repo pin
  validity, which is load-bearing here and cosmetic there.
