# Provenance

New fixture for CONSTRAINT-EXEC Item 5 (design.md D6, Appendix B). Adapted from the
orchestrator's B1 probe skeleton (`.project/active/constraint-lowering/probe_b1_channels.py`,
which itself proved the shared-producer-channel finding, `b1-probe-evidence.md`).

**Deviation from the design's Appendix B prose, surfaced here (capture-fidelity law 4):**
Appendix B describes the assertion as living in `Container` ("`Container { part cell :
Cell [3]; assert constraint <bound>(cell.power_calc.p) }`"). Placed there, the assertion's
`owning_definition` walk (`constraint_extraction.py:_owning_definition`) resolves to
`Container`, which is itself a *singleton* under `Design` — `occurrences_of(Container)`
would yield exactly one occurrence, not three. That does not exercise the multi-instance
semantics the fixture exists to pin (3 IDs / 3 catalog entries / 3 constraint modules with
a recorded shared producer binding, B1-settled).

This model instead nests the assertion inside `Cell` itself, self-scoped (`power_calc.p`,
a sibling feature reference, not `cell.power_calc.p`). `Cell`'s owning-definition walk
resolves to `Cell`; `occurrences_of(Cell)` returns three occurrences (matching the B1
probe's proven `MultiChan__Cell` result); each occurrence resolves its own `power_calc.p`
in its own occurrence scope, misses the occurrence-indexed `ScopedKey`, and falls through
to the shared de-indexed producer channel — the exact B1-settled behavior. The semantic
point Appendix B is pinning (three concrete constraints, three channels, one shared
producer binding, recorded per entry) is preserved; only the literal nesting differs from
the prose sketch.
