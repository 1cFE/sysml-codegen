---
id: 0019
title: agentic-mbse keeps no second occurrence reader; ADR 0012's exclusive ownership stands
date: 2026-10-22
owner: Reid Westwood
status: active
amended_by: []
superseded_by: null
provenance: "[AGENT] (ratified by owner, 2026-10-21)"
seams: [elaboration, agentic-mbse]
supersedes: 0018
promoted_to: null
---

## Decision

ADR 0018 is superseded. agentic-mbse no longer has an occurrence reader: its `occurrence_extraction.py`, the subset profile it served and the parity test that held it to codegen are deleted. ADR 0012's invariant that codegen alone owns the raw parser reads for declaration discrimination, slot construction and multiplicity applies again unamended.

## Why

On 2026-10-21 the owner approved retiring agentic-mbse's copy of the generator's refusal rules (agentic-mbse ADR 0004, which supersedes its ADR 0001; design and reasoning in `.project/research/2026-10-21-generator-check-architecture-review/`). The generator is now the only authority on whether a model generates, and modellers get its answer from `sysml-codegen check`. ADR 0018 existed only so that copy could make the same occurrence reads; with the copy gone there is no second reader to hold in parity. ADR 0018 was merged to main on 2026-10-22 (PR #21) after the retirement was implemented on unmerged branches, so this entry records that it no longer describes the code.

## Invariants established

- Only codegen reads declaration discrimination, slot construction and multiplicity from the parser. No agentic-mbse module repeats these reads.
