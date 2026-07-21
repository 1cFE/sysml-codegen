# Spec Brief — Lifecycle Item 8: Canonical Embedded Catalog and Store Transition

**Stage:** spec
**Epic authority:** Item 8 (register row 10) in
`.project/backlog/epic_constraint_execution_lifecycle_remediation.md`; owner decision D-3 in
the ratified contract (settled: codegen's embedded catalog is the SOLE schema authority).

## Intent

- [INHERITED: owner decision D-3 — settled, do not relitigate] Codegen's embedded
  model-contract catalog is the only schema authority. TEAx consumes it directly. Alternate
  schemas, fixtures, stand-ins, materializers, and reconstruction code are DELETED.
- Catalog additions (the one recognized additive class): the admitted per-usage record and the
  five TEAx-consumed fields per eligible concrete entry — source form, usage short name/QN,
  real `owner_qn`, `definition_qn`, entry-level definition-to-usage join. Spec them against
  the REAL current catalog shape at HEAD (Items 1–5 changed it — inventory first).
- TEAx config/query/CLI/fixtures consume real codegen model contracts; the stand-in
  catalog-byte hash becomes real semantic/catalog/executable identity.
- Store migration: equivalence proof OR archived lineage + new store — never silent rebind.
- Catalog/schema skew fails closed before semantic use.
- [OWNER] No LOC metrics. This item is the epic's largest deletion: the named alternate system
  (TEAx alternate catalog schema, fusion materializer, hand-authored schema fixture, stand-in
  fingerprint, QN splitting, predicate-text search, hardcoded source form, semantic
  reconstruction) must be gone, not shimmed.

## Ground truth to establish first (both/all repos)

- Chain: codegen through Item 7 (`280a2bd` + evidence edits), agentic-mbse `4c18d61`, TEAx
  `98a6d07`. Fusion consumer at `../fusion-tea-stellarator-mbse-demo` (bceaf40a + uncommitted
  Gate B filing — do not disturb).
- Inventory the CURRENT embedded catalog schema (post Items 1–5: occurrence transcript,
  exclusion records, written-qualifier era) and the CURRENT TEAx alternate-schema surface —
  find every consumer of the alternate system before specifying its deletion.
- Item 7's trust machinery (manifest, hash anchor) is landed — identity work here must
  compose with it, not duplicate it.
- Backlog rows CE-F1 (absorbed here) — read their recorded scope.

## Out of scope (firewall)

A differently-shaped standalone catalog export (any later export must be mechanically
identical to the embedded schema); Items 9/11 TEAx bridge/evidence work (but name the seams
they'll consume); fusion stellarator modeling (Item 10).

## Spec shape

Item 1 rigor: provenance-graded requirements, acceptance coordinates (catalog coverage
totality across definition/usage/concrete occurrence/exclusion/result; skew both directions;
store migration/archival), RED-first public surface, the complete deletion inventory with
file:line grounding, cross-repo phasing.
