# Spec: Production Elaborator + Projection (ELABORATE-FIRST Item 4)

**Date**: 2026-08-07 · **Branch**: `source-identity-epic` · **Status**: Implementation complete; independent Item-5 re-audit pending
**Spike basis**: `.project/active/elaborator-spike/findings.md` (assumption confirmed, owner GO)

## The Point

**[INHERITED: SOURCE-IDENTITY mission, owner grade]** One semantic source occurrence becomes
exactly one runtime source across all calculation, constraint, and aggregation consumers. This
item specifies the front end that makes that true by construction: elaborate the model into an
instance graph, then project the graph into the existing `ComputationGraph`.

## Requirements

- **[NEED] R1 — One elaboration pass.** At load time (licensed), the pipeline produces an
  instance graph: part/attribute/calc/constraint occurrence nodes with stable IDs, every
  redefinition applied innermost-wins, every binding referent resolved to a node ID. No later
  stage re-resolves a reference from a string.
- **[NEED] R2 — Identity by construction.** A modeled value is one attribute node. Consumers
  hold edges to nodes. The projection emits one public input per externally suppliable consumed
  node and one producer channel per computed node output. No mechanism may mint a
  consumer-local input for a bound modeled reference.
- **[INHERITED: contract D-3/SRC-01] R3 — Self-binding fails.** `in R = R`, where the referent
  and bound formal denote the same exact semantic declaration, is a hard elaboration error carrying
  `SI_SELF_BINDING` and every offending binding. Never reinterpreted. Indexed (`#(i)`) and general
  expression sources fail with their contract codes. R9 pins the required equality representation.
- **[INHERITED: contract, ratified 2026-08-05] R4 — Distinct occurrences, distinct sources.**
  Equal inherited defaults on distinct concrete occurrences remain distinct sources unless the
  model explicitly shares them; one independently overridable default per concrete calculation
  usage (C23). The elaborator's per-occurrence nodes implement this directly.
- **[NEED] R5 — Projection lands on the verified seam.** The projection produces the full
  in-memory `ComputationGraph` the generation layer consumes: modules (calculation, FORMULA,
  aggregation, constraint, report-aggregator), entry-point groups, execution order,
  `output_aliases`, attached `constraint_catalog`. Generation code is not modified.
  `fallback_entry_points` is retired (nothing falls through); the V11 coverage check remains as
  an invariant assertion.
- **[NEED] R6 — Dual-run capable.** Until the Item-6 cutover, the elaborator front end runs
  behind an internal parallel entry point (never a shipped flag) so old-vs-new
  `ComputationGraph`s can be diffed per fixture. Item 5 owns the harness and breadth;
  this item must not preclude it.
- **[HARD] R7 — Acceptance authority.** The Item-3 contract's 29-cell matrix is the behavior
  authority. This spec restates none of it.
- **[NEED] R8 — Deletion is in scope of the design.** The design names the mechanisms this
  front end supersedes (the deletion ledger); Item 6 executes it. New code that duplicates a
  ledger row's responsibility without deleting it is out of contract.
- **[INFERRED] (ratified by owner 2026-08-08) R9 — Exact parser identity is the semantic
  contract.** Between model load and the resolved instance graph, every supported semantic
  declaration is represented by its exact parser declaration ID; every concrete instantiation is
  represented by a structured occurrence ID derived from exact containment declaration IDs and
  multiplicity indices; and consumer edges target typed node/output-port IDs. The parser adapter
  exposes exact element IDs and resolved referent, chain, typing, and redefinition endpoints before
  evidence is flattened. Names, qualified names, owner/name pairs, rendered occurrence paths,
  sanitized spellings, source locations, current values, and enumeration order may not participate
  in semantic equality, lookup, slot formation, occurrence selection, or edge selection.
  Self-binding compares the referent and bound formal declaration IDs. Redefinition families key
  from their endpoint declaration IDs, never a relationship-object ID. A required exact identity
  that is missing, unstable across the supported capture boundary, or ambiguous fails closed with a
  named diagnostic. Strings may exist as diagnostic/projection metadata or as a canonical wire
  encoding of an already-defined typed ID; no stage may use them to resolve semantic identity again.

## Non-Goals

- Snapshot format change and corpus recapture (Item 6, atomic with cutover).
- Removing any legacy mechanism now (Item 6; old front end stays authoritative until then).
- Cross-repo `agentic-mbse` validator changes and modeling guidance (Item 7).
- Non-finite multiplicity support (expand-finite or block-loud stands).

## Related Artifacts

- Epic: `.project/backlog/epic_elaborate_first_architecture.md`
- Governing contract:
  `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md:287-368`
- Architecture research:
  `.project/research/20260807-145336_elaborate-first-instance-graph-architecture.md`
- Identity probe record:
  `.project/research/20260808-103243_syside-identity-and-redefinition-probe-record.md`
- Design: `.project/active/elaborator-design/design.md`
- Design review: `.project/active/elaborator-design/design-review.md`
- Product-lens ledger: `.project/active/elaborator-design/product-lens.md`
