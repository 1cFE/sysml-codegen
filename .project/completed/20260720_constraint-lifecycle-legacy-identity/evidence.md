# Evidence — Lifecycle Item 12: Legacy Snapshot and Tracking Identity Closure

**Implemented:** 2026-07-20 · **Branch:** constraint-exec-epic
**Spec+design:** `spec-design.md` (all four decisions ratified on the evidence)

RED-first across the six coordinates. Every RED test was confirmed failing on the
pre-change tree before the fix landed; the full licensed battery is green after.

## What changed (5 source edits + 1 doc correction)

| Phase | Decision | Change |
|---|---|---|
| 1 | D4 | `orchestration/snapshot_context.py` — thread `snap["constraint_lowering_mode"]` into the from-snapshot `PipelineContext`, replacing the defaulted `grandfathered_off`. Fixes the latent misreport and supplies the gate signal. |
| 2 | D1 | `snapshot/__init__.py` — add `GrandfatheredSnapshotError` + `assert_snapshot_certifiable(mode, path)`. `cli/__init__.py` — call the guard in `run_codegen`'s from-snapshot branch (after ctx build, before preflight/output/seal) and add an explicit `except` clause logging the contextual error. |
| 3 | D2 | `snapshot/capture.py` — delete the `lower_constraints_enabled` param; capture is always `applied`. `scripts/capture_extraction_snapshots.py` — delete the empty `GRANDFATHERED` set and its conditional. |
| 4 | D3 | `resolution/models.py` — delete the `tracking_key` field + docstring. `tests/unit/test_concrete_constraint_model.py` — delete the round-trip test (validate_assignment stays covered by the polarity-mutation test). Contract non-goal lines amended to a decision record. |

## RED-first coordinates (test file: `tests/conformance/test_legacy_snapshot_closure.py`)

- **RED-6 (D4)** `test_from_snapshot_context_reports_real_lowering_mode` — an applied
  snapshot's context reports `applied`, not the old defaulted `grandfathered_off`.
  *Red before:* returned `grandfathered_off`.
- **RED-1 (D1)** `test_generate_from_grandfathered_snapshot_fails_closed` +
  `test_grandfathered_gate_raises_contextual_error` — a crafted `grandfathered_off`
  snapshot **carrying constraint usages** (the exact silent-drop case) is refused;
  the error names "recapture" and "lowering". *Red before:* `run_codegen` warned,
  dropped the usage, and sealed (returned `True`). The pre-change warn log
  confirmed the drop: *"carries 1 constraint assertion(s) — these assertions are
  NOT generated."*
- **RED-2 (D1)** `test_grandfathered_snapshot_writes_no_sealed_package` — no
  `contracts/package_contract.json` is written (the gate precedes output creation).
  *Red before:* a sealed package was produced.
- **RED-3 (D1/D2 fence)** `test_grandfathered_probe_still_loads_for_inspection` —
  all 7 grandfathered probes still load via `build_full_graph_from_snapshot` and
  `build_pipeline_context_from_snapshot`. Green before and after (over-gating fence).
- **RED-4 (D2)** `test_capture_snapshot_has_no_lowering_optout` — `capture_snapshot`
  has no `lower_constraints_enabled` parameter. *Red before:* the param existed.
- **RED-5 (D3)** `test_tracking_key_field_is_deleted` — `tracking_key` is not in
  `ConcreteConstraint.model_fields`. *Red before:* the field was present.

## Gate is unconditional on `grandfathered_off` (owner ruling)

Ratification: *"a certifying-package attempt from a grandfathered probe must fail at
the gate, not later."* All 7 probes carry 0 usages, so the gate rejects a
grandfathered snapshot regardless of usage count — provenance-based fail-closed, not
drop-count-based. Inspection loads are unaffected because the gate lives on the
`generate` command path, not in the shared read-path helper.

## Interactions found and resolved (not silently absorbed)

Two tests broke on the first full run — both expected consequences of the change,
resolved honestly:

1. **`test_snapshot_constraint_parity.py`** (5 cases) passed
   `lower_constraints_enabled=True` to `capture_snapshot` — now the only behavior.
   Dropped the redundant kwarg; intent preserved (they want lowering applied).
2. **`test_uncovered_params.py::test_seeded_strict_generation_aborts_on_v11_gap`**
   generated from `chain_override_probe` (grandfathered) to reach V11 end-to-end.
   The gate now fires first. Fix: present the same snapshot as `applied` in a tmp
   copy — immaterial for a zero-usage probe (no lowering runs either way) — so the
   gate passes and the V11 boundary is still exercised end-to-end through
   `run_codegen`. The un-flipped grandfathered form failing at the gate is covered
   by the closure test. The D5-retained `build_pipeline_context(lower_constraints_enabled=...)`
   flag was untouched — no other test needed changing.

## Verification bullet 5 (verify, not rebuild)

This change adds **no** resume/query/lineage surface: the five edits touch only the
generate gate, the mode threading, the capture opt-out, and the `tracking_key`
field. Item 8's store gate is untouched.

## Byte-identity + format

- **No snapshot re-capture.** `git status` shows no fixture snapshot modified; the 7
  probes stay byte-identical (inspection-only).
- **No format bump.** `tracking_key` never reached a serialized surface
  (`ConcreteConstraint` is not serialized into snapshots; absent from the catalog),
  so deleting it needs no version change. `grandfathered_off` remains a legal mode.

## Full battery

- `uv run pytest tests/` (licensed): **3115 passed, 47 skipped, 17 deselected, 0 failed**.
  The 47 skips are pre-existing data/scenario skips (no golden / no scenario / no
  baseline) — no `requires_license` skips (license active), so `-rs` is clean.
- `uv run ruff check` on all changed files: clean.
- `uv run mypy src/`: 72 errors, identical with and without the change (all
  pre-existing repo noise) — **zero new type errors**.
