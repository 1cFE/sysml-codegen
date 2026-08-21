---
id: 0003
title: Cite decisions by register path
date: 2026-08-21
owner: Reid W
status: active
amended_by: []
superseded_by: null
provenance: "[AGENT] (ratified by owner, 2026-08-21)"
seams: [decision-registers, documentation]
supersedes: null
promoted_to: CLAUDE.md
---

## Decision

Cite a decision by its register path and id, never by a bare number. Use forms such as
`docs/architecture/modeling-assumptions.md ADR-009` for an input-authoring decision and
`.project/adr/0003-cite-decisions-by-register-path.md` for a system-builder decision.

## Why

Both registers allocate numbers, and their human-readable forms can be confused in prose. The path
states which audience-bound register supplies the authority and gives the reader a direct lookup
route without changing either register's established numbering scheme.

## Invariants established

- Every decision citation identifies its register as well as its id.
- Existing `ADR-0NN` ids and script-allocated `NNNN` ids keep their native forms.

## Rejected alternatives

- A new prefix such as `DR-0001` was rejected because the script and filesystem would still use
  `0001`, leaving prose and storage with different identifiers.
