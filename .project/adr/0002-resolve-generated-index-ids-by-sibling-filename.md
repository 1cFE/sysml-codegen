---
id: 0002
title: Resolve generated index ids by sibling filename
date: 2026-08-21
owner: Reid W
status: active
amended_by: []
superseded_by: null
provenance: "[AGENT] (ratified by owner, 2026-08-21)"
seams: [product-ledger, project-workflow]
supersedes: null
promoted_to: .project/product/README.md
---

## Decision

Treat a generated register index as a discovery surface keyed by id. Every indexed four-digit id
must resolve to exactly one sibling `<id>-*.md` entry, and a conformance test enforces that naming
rule instead of adding links to the generated index.

## Why

The register generator owns the index format and intentionally emits compact rows. Forking it to
add repo-local links or provenance would recreate the tooling drift this migration removed. The
naming rule is mechanically stronger: it fails on both a missing entry and an ambiguous duplicate,
while the entry remains the authority surface for provenance and full content.

## Invariants established

- One index id resolves to one and only one sibling entry.
- `INDEX.md` remains entirely generated; durable explanatory prose lives in the register README.

## Rejected alternatives

- A local `regen_index` fork was rejected because it would make this repo maintain a divergent
  output format.
