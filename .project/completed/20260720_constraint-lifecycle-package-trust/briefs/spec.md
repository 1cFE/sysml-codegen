# Spec Brief — Lifecycle Item 7: Trusted Package Bootstrap and Seal Provenance

**Stage:** spec
**Epic authority:** Item 7 (register rows 8–9) in
`.project/backlog/epic_constraint_execution_lifecycle_remediation.md`; ratified contract rows
8–9; adversarial-review package-trust lane.

## Intent

- [INHERITED: ratified contract] No untrusted package code runs before verification: move
  verification trust to runtime-owned code, or authenticate package-local verifier bytes
  before execution. The threat model to spec against: an unconditional-success verifier inside
  a package must be rejected BEFORE any package code executes.
- Verifier/runtime-contract versions: single-source them, or define an explicit fail-closed
  compatibility table — both skew directions.
- A generation manifest distinguishing codegen-produced, preserved-handwritten, and runtime
  artifacts; a re-seal must not be able to classify an arbitrary foreign file as
  codegen-produced (laundering rejection).
- Preserve the CERTIFIED stdlib-only symlink/path policy (superseded-epic Item 6 — inherited,
  do not re-audit; extend only where rows 8–9 name new work).
- [OWNER] No LOC metrics; qualitative simplicity — consolidate duplicated verifier/version
  machinery WITHOUT merging the deliberately-distinct seal and verify walkers (that boundary
  is a named do-not-collapse invariant).

## Current facts to ground in (verify at HEAD)

- Chain: sysml-codegen through Item 6 (`f917787`), agentic-mbse `4c18d61`, TEAx `d545701f` +
  local `db23719`.
- Item 4's `_upstream_pins` single-sourcing is precedent for the version machinery.
- The certified seal→verify symlink matrix (constraint-wave Item 6) is inherited evidence —
  its regression tests must stay green, its scope not reopened.
- Read the actual sealing/verification code before writing requirements: where the verifier
  bytes live, what executes when a package loads, what the current re-seal path accepts.

## Out of scope (firewall)

A second catalog schema authority (Item 8's D-3 territory); re-auditing the certified symlink
matrix; TEAx evidence-durability work (Item 11).

## Spec shape

Item 1's rigor template: provenance-graded requirements, threat-model-driven acceptance
coordinates (the unconditional-success-verifier attack, the foreign-file re-seal attack, both
skew directions), RED-first public surface, named deletion/consolidation targets, cross-repo
phasing if TEAx-side work is genuinely required (verify whether it is — the epic lists TEAx,
but ground it).
