# Spec Brief — Lifecycle Item 4: Diagnostic Severity and Modeled-Default Fidelity

**Stage:** spec
**Epic authority:** Item 4 (register row 4) in
`.project/backlog/epic_constraint_execution_lifecycle_remediation.md` — read its CURRENT scope
list (6 points; point 6, the written-reference carry, was absorbed from Item 2 by referral).
Ratified contract + LC spec per the epic's Source Documents.

## Intent

- [INHERITED: ratified contract] Extraction diagnostics become load-bearing: versioned severity
  field, stable code/sink through facts, codecs, validation, and codegen; unclassified
  trust-affecting diagnostics fail closed; both schema-skew directions fail closed.
- [INHERITED] Warning rendering is total (out-of-root included) and warning order is preserved
  before BLOCK; warning preparation can never replace the actionable BLOCK diagnostic (R-8
  family — Item 1 deliberately preserved current bytes for THIS item to change).
- [INHERITED] Explicit signed (`-0.1`) and unit (`[MW]`) modeled defaults survive through typed
  entry points and generated JSON; unsupported default IR fails or stays explicitly unresolved —
  never an invented value.
- [Referred from Item 2, decision 2026-07-20] Carry the written reference for self-named calc
  bindings through extraction facts and the snapshot format, completing SR-A02 convergence on
  real data with no name inference. `tests/fixtures/shared_producer/` +
  `.project/active/constraint-lifecycle-shared-resolution/{spec,design,evidence}.md` (PC-4)
  define the target state; the fixture's PROVENANCE.md documents the exact mechanism gap.
- [OWNER] No LOC metrics anywhere. Qualitative simplicity: consolidate duplicated
  diagnostic/default parsing where one typed representation suffices; delete what the typed
  path obsoletes.

## Inherited residuals this item owns (verify each at HEAD before specifying)

1. Item 1 audit residual: tier-2 disposition asymmetry — a wholly-malformed supplied-value
   target vanishes without a diagnostic (tier 1 flags the same input as non-literal; tier 2
   swallows). See Item 1 `audit.md` residuals.
2. PC-2: SR-R16's stated basis amends to order-dependence (Item 2 design/evidence).
3. Flagged for awareness, scope call is the spec's: param_group=None on LocalTerm mints
   (classification domain — may belong to Item 10 instead; decide and record).

## Coordinated-pair constraints

- agentic-mbse checkout: /home/reid/1cfe/agentic-mbse at pin `515e08bb` (Item 0 set). This item
  MOVES that pin — its schema/version machinery must handle both skew directions fail-closed,
  and the epic requires exact new pin recording. The sysml-codegen candidate chain since the
  pin is entirely additive-certified (Items 1–3).
- Snapshot format: currently v3. The written-reference carry likely needs a snapshot format
  bump — if so, spec it explicitly (version, migration/rejection behavior for v3 snapshots,
  grandfathering interaction with Item 12's fail-closed rule). Do not smuggle it in.
- Delivery stays in the same PR wave: agentic-mbse PR #11 first, codegen PR #9 second.

## Out of scope (firewall)

General constant folding / unit conversion / a diagnostics framework beyond the versioned
contract; Item 5's whole-tree portability; Item 12's grandfathered-snapshot closure (but state
the interaction); reworking Items 1–3 certified seams (extend only).

## Spec shape

Item 1's spec is the rigor template; provenance-graded requirements, exact acceptance
coordinates with RED-first public surface, named deletion targets, cross-repo phasing
(agentic-mbse first), and the new-pin recording obligation.
