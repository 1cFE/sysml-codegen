---
id: 0011
title: Parser declarations, concrete occurrences, and typed graph projection
date: 2026-10-12
owner: Reid W
status: active
amended_by: []
superseded_by: null
provenance: "[INHERITED: exact-identity research and design cited below]"
seams: [extraction, elaboration, projection, snapshot]
supersedes: null
promoted_to: null
---

## Decision

SysIDE supplies effective child declarations and exact referent/redefinition endpoints; codegen expands their concrete parent and finite-index contexts. Serializable declaration identity must be reload-stable, and feature slots follow authored and implied redefinition endpoint IDs rather than relationship-object IDs. Exact calculation/formal/output/constraint payloads and structured expression IR attach to typed graph nodes; projection orders their dependencies and renders names without reconstructing semantics from output strings.

## Why

A declaration is shared by many modeled occurrences. Confusing those identities can merge independent values, split one shared source, or bind a consumer to a sibling. Session-local object/relationship IDs also break replay, while filtering implied redefinitions disconnects ordinary calculation bindings from their formal slots. Keeping resolved ancestry, payload identity, and IR in the instance graph prevents downstream renderers from inventing a second semantic account.

[OWNER] The August 7 report records the owner's premise that snapshots are a serialization choice, not an architectural constraint. This is a report-recorded paraphrase, not a verbatim quote or a new compatibility promise. The original authority is `aa35f06fb6b3bacfd42c7763a07a4ee4fdaafa57:.project/research/20260807-145336_elaborate-first-instance-graph-architecture.md`, Research question.

## Sources and bounds

This supplements `.project/adr/0005-exact-identity-elaboration-replaces-string-resolution.md`; the detailed mechanisms were agent findings/design choices, not newly owner-originated rulings. Sources: `aa35f06fb6b3bacfd42c7763a07a4ee4fdaafa57:.project/research/20260808-103243_syside-identity-and-redefinition-probe-record.md`, Probes 1–3; `aa35f06fb6b3bacfd42c7763a07a4ee4fdaafa57:.project/research/20260809-153245_item6-identity-completion-and-cutover-census.md`, exact payload and projection findings. The UUIDv5/null-QN admission boundary is an explicit supported-parser boundary, not a universal promise about every future parser version.

Implementation: `src/sysml_codegen/elaboration/identity.py`, `occurrence.py`, `elaborate.py`, `graph.py`, and `project.py`. Kept controls: `tests/conformance/test_elaboration_identity_foundation.py`, `test_elaboration_payload_identity.py`, `test_elaboration_projection_one_way.py`, and `tests/unit/test_elaboration_import_boundaries.py`. Full lifecycle certification remains bounded by `.project/reference/source-identity-reconciliation.md`.
