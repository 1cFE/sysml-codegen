# Spec Brief — Lifecycle Item 9: Multi-Entry Candidate Bridge

**Stage:** spec (TEAx-owned item; artifacts live here for register continuity, deliverable
work in /home/reid/1cfe/teax)
**Epic authority:** Item 9 (register row 11) in
`.project/backlog/epic_constraint_execution_lifecycle_remediation.md`; contract row 11;
backlog row CE-F2 (absorbed here).

## Intent

- [INHERITED: ratified contract] Stock TEAx's bridge constructs complete typed mappings for
  ZERO, ONE, or MANY generated entry channels without a consumer wrapper: baseline typed
  models for every entry channel, overrides for selected fields only.
- Validate missing/extra/malformed/wrong-typed channel mappings BEFORE evaluation.
- Ordinary declared design inputs are never treated as missing graph producers.
- DELETE fusion's MultiChannelEvaluator and every single-entry assumption duplicated across
  config, definition, and bridge layers.
- [OWNER] No LOC metrics; deletion over shims.

## Fresh ground truth from Item 8 (use it — this is why register order matters)

- Item 8's IFE regeneration changed the entry-channel decomposition (4 groups → 3;
  hif_driver_params gone) and left fusion's run_viability_study.py MultiChannelEvaluator
  STALE against the real package — the live counterexample this item's zero/one/many
  requirement exists to fix. Ground the spec in that exact package
  (fusion-tea/exploration/ife_e2e/generated at 667136fa+).
- TEAx now consumes the embedded catalog directly (load_model_contract seam,
  ACCEPTED_CATALOG_SCHEMA_VERSIONS) — the bridge work builds on that seam.
- Chain: codegen 19b74ac(+), teax a5594e1(+audit-note commits), fusion-tea 667136fa(+).

## Out of scope (firewall)

Model-derived late fill or graph mutation; constraint-free report semantics (Item 11);
stellarator producer representation (Item 10).

## Spec shape

Provenance-graded requirements; acceptance coordinates for zero/one/many including the REAL
IFE three-group package as the "many" case and a constraint-free package as "zero"; RED-first;
the single-entry-assumption inventory across TEAx config/definition/bridge layers (find them
all, file:line); fusion MultiChannelEvaluator deletion gated on the study running green
through the stock bridge.
