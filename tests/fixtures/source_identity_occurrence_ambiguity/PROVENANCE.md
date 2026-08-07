# Provenance — contextual-ambiguity fixture (C9 / C10)

Constructed for SOURCE-IDENTITY Item 4 Phase 2, realizing the contract's two BLOCKED ambiguity
keys: a definition-level referent consumed from a context containing two concrete occurrences of
the definition, neither uniquely selected.

- **C9** — `amb_qual_calc`: owner-qualified form `'Amb Sensor'::level` spelling
  (`in value_in = 'Amb Sensor'::reading`). Referent (probed live 2026-08-07):
  `source_identity_occurrence_ambiguity::'Amb Sensor'::reading`, owned by the PartDefinition —
  def-level referent class.
- **C10** — `amb_bare_calc`: bare renamed form, def context. The bare name reaches the def-level
  attribute through `private import 'Amb Sensor'::*` inside `'Amb Bay'` — same referent QN and
  class as C9 (probed identical).
- **Candidate occurrences:** `amb_bay.sensor_a` and `amb_bay.sensor_b` — both inside the
  consumer's context, so contextual projection must return `AMBIGUOUS` with both candidates
  sorted, never a first-pick (D5) and never a global `len == 1` shortcut.
- Value state: definition default only (no overrides), per both cell keys.

Consumers: `tests/conformance/test_source_identity_occurrences.py` (live) and
`tests/unit/test_source_identity.py` (projection outcomes). Outcome per contract:
`AMBIGUITY_DIAGNOSTIC` — `SI_OCCURRENCE_AMBIGUOUS` before any runtime source exists.
