# Provenance — contextual-ambiguity fixture (C9 / C10)

Constructed for SOURCE-IDENTITY Item 4 Phase 2. The later F-4 owner ruling splits its two
definition-level references by authored form.

- **C9** — `amb_qual_calc`: owner-qualified form `'Amb Sensor'::level` spelling
  (`in value_in = 'Amb Sensor'::reading`). Referent (probed live 2026-08-07):
  `source_identity_occurrence_ambiguity::'Amb Sensor'::reading`, owned by the PartDefinition —
  def-level referent class. Neither occurrence is on the consumer lineage, so the current
  expected outcome is `SI_OCCURRENCE_MISSING`; descendants are not counted or selected.
- **C10** — `amb_bare_calc`: bare renamed form, def context. The bare name reaches the def-level
  attribute through `private import 'Amb Sensor'::*` inside `'Amb Bay'` — same referent QN and
  class as C9 (probed identical).
- **Candidate occurrences for C10:** `amb_bay.sensor_a` and `amb_bay.sensor_b` — the bare form's
  contextual projection returns `SI_OCCURRENCE_AMBIGUOUS`, never a first-pick (D5).
- Value state: definition default only (no overrides), per both cell keys.

Kept consumers: `tests/conformance/test_elaboration_contract_matrix.py` and
`tests/conformance/test_elaboration_fail_closed.py`.
