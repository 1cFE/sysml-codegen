# Provenance

[AGENT] Supplementary Item 1 fixture, authored 2026-07-19 during audit remediation.

Delivers the `A → B → A` indirect-containment variant that approved
`design.md:598` specifies for OD-A05 but that the Phase 0 `cycle/` fixture did not
model — it carries only the self-cycle (`part recursive : Node`). Added as a NEW
directory rather than by editing `cycle/`, because the Phase 0 overlay bytes are the
RED/GREEN anchor and must not change.

`A` contains `b : B`, `B` contains `a : A`, and `A` carries the assertion. Querying
`A`'s occurrences therefore closes the cycle through `B`, yielding
`cycle_path == (A, B, A)` with the closing edge `(A, "b", B)` per the design's
`(owning_definition_qn, feature_name, target_definition_qn)` field definition.

Not covered here: the design's declaration-reversed variants (proven at unit level in
`tests/unit/test_part_instance_index.py`) and the `b"sentinel\n"` output-target
byte-preservation observation, which remains unproven and is disclosed as such in
evidence.md.
