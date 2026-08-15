# Audit: Lifecycle Item 12 — Legacy Snapshot and Tracking Identity Closure

**Verdict:** Certify
**Audited:** 2026-07-20
**Branch:** constraint-exec-epic
**Commit:** 7526665

---

## Summary

All six spec+design coordinates are delivered and independently reproduced — not
trusted from the evidence. The product path now fails closed on `grandfathered_off`
at the generate command, before preflight, output, or seal; the fail-open it closes
is real (I reconstructed the silent drop: a grandfathered snapshot carrying 1 usage
rebuilds to 0 catalog entries with an "assertions are NOT generated" warning). The
capture-time opt-out and the dead `tracking_key` field are deleted, the from-snapshot
mode misreport is fixed, and the two test interactions are resolved honestly without
weakening coverage. Full licensed suite 3115 passed / 0 failed, `-rs` clean, mypy 72
(unchanged), ruff clean, tree byte-identical.

## Findings

### Plan completion

All five phases of the phased plan verified complete against the diff:

- **D4 (mode honesty)** — `snapshot_context.py:94` threads
  `constraint_lowering_mode=snap["constraint_lowering_mode"]` into the from-snapshot
  `PipelineContext`. Verified the `constraint_multi_instance` fixture is `applied`
  on disk, so RED-6 exercises a real applied→applied path (not a tautology).
- **D1 (gate)** — `snapshot/__init__.py:51-79` adds `GrandfatheredSnapshotError` +
  `assert_snapshot_certifiable`; `cli/__init__.py:994` calls it right after context
  build and `:1077-1079` logs it as a clean `False` return.
- **D2 (capture deletion)** — `capture.py` drops the `lower_constraints_enabled`
  param; `scripts/capture_extraction_snapshots.py` drops the empty `GRANDFATHERED`
  set and its conditional arg. The extraction-only path (`:239`) still hardcodes
  `CONSTRAINT_LOWERING_MODE_GRANDFATHERED_OFF`, so the 7 probes stay honest.
- **D3 (`tracking_key` deletion)** — field + docstring gone from `resolution/models.py`;
  round-trip test deleted; contract non-goals amended.
- **Bullet 5 (verify not rebuild)** — confirmed no resume/query/lineage surface added;
  the five edits touch only the gate, mode threading, capture opt-out, and the field.

No placeholder code, TODOs, or partial implementations.

### Spec conformance

Every success criterion reproduced independently:

- **Fails closed with a contextual error, before any output** — verified. The gate
  at `cli:994` precedes `_preflight_constraint_names` (`:1005`), output clear
  (`:1029`), and seal (`:1069`). `test_grandfathered_snapshot_writes_no_sealed_package`
  confirms no `package_contract.json` is written. Error names "lowering" and "recapture".
- **Provably cannot seal** — verified. No code path from a `grandfathered_off` context
  to `_seal_package`; the raise short-circuits `run_codegen` to `False`. I ran the
  generate command on a crafted grandfathered snapshot: returns `False`, no output tree.
- **Probes remain loadable for inspection** — verified. All 7 probes pass
  `test_grandfathered_probe_still_loads_for_inspection` via both inspection entry
  points, and each reports `grandfathered_off` truthfully. The gate lives on the
  generate command, not the shared read-path helper, so inspection is untouched.
- **Full-pipeline model can no longer be captured grandfathered** — verified. The
  `lower_constraints_enabled` parameter is gone from `capture_snapshot` (not
  defaulted); `capture_snapshot` always builds with lowering applied.
- **`tracking_key` does not exist; no correlation claimed** — verified. Zero
  occurrences in `src/`, zero in real `docs/`; the only `tests/` hits are the RED-5
  deletion assertion itself. The two amended contract lines read as decision records
  ("Resolved (Item 12): `tracking_key` was removed … so no cross-version correlation
  is claimed"), not as instructions to future agents (capture-fidelity Law 3 clean).
- **From-snapshot context reports the real mode** — verified (RED-6 green; applied
  fixture confirmed applied on disk).
- **Full suite green, no re-capture, no format bump** — verified below.

Non-goals respected: mode not deleted, extraction-only path kept, live inert-build
flag (D5) untouched, no format bump.

### Design conformance

Implementation follows the design exactly. D1's gate is at the generate command as
`[HARD]` required (not in `seal_package`, which is pure over the directory, and not
in the shared `build_pipeline_context_from_snapshot` helper, which inspection tests
legitimately run on grandfathered probes). The rejected load-time branch was not
taken — probes still load. The inspection warn at `graph_rebuild.py` stays (D2's two
honest boundaries). D4 supplies the gate signal from the context rather than a second
snapshot load, as designed.

### Code integrity

No slop or failure-honesty issues. `assert_snapshot_certifiable` is a single-purpose
guard with a readable signature. The new `except GrandfatheredSnapshotError` is a
narrow, specific catch that maps to the existing fail-fast `return False` idiom — not
a broad `except Exception`. This is the inverse of a silent fallback: it *replaces* a
silent fail-open (warn-and-drop-and-seal) with a hard fail-closed. The two test
interactions were resolved without weakening: the V11 gap test
(`test_uncovered_params.py:187`) still runs end-to-end through `run_codegen` and still
asserts the `False` return + logged V11 line — the applied-copy flip is guarded by an
assertion that the probe carries zero usages, so the flip is provably immaterial. The
parity test simply drops a now-redundant `=True` kwarg; behavior identical.

---

## Certification

**Checked and reproduced:**
- Mode-misreport fix: applied fixture reports `applied`; 7 probes report
  `grandfathered_off`. Confirmed the fixture's on-disk mode independently.
- The gate: reconstructed the pre-gate silent drop (1 usage → 0 catalog entries,
  drop warning); confirmed `run_codegen` now returns `False` with no `package_contract.json`;
  gate ordering precedes preflight/output/seal in source.
- Capture opt-out deletion: `lower_constraints_enabled` absent from
  `capture_snapshot` signature (gone, not defaulted); extraction-only path still
  produces `grandfathered_off`.
- `tracking_key`: zero `src/` occurrences; contract non-goals read as decision records.
- Two interactions: parity intent preserved; V11 test still end-to-end via `run_codegen`.
- Batteries at 7526665: `uv run pytest tests/` licensed = **3115 passed, 47 skipped,
  0 failed**, `-rs` clean (no `requires_license` skips); mypy **72** (identical count,
  all pre-existing); ruff clean on all changed files; git tree clean → 7 probe
  snapshots byte-identical; no format bump.
- Closure test file green: 13/13.

Marked: all seven success criteria in `spec-design.md` were already `[x]`; each is
verified as genuinely met. CURRENT_WORK updated to certified. Epic item 12 checkbox
marked below.

**Not checked:** teax-side execution (this item touches no teax surface); the real
RED-state of each of the six tests on the pre-change tree was not reconstructed
individually — instead the one load-bearing fail-open (D1's silent drop) was
reproduced directly, and the current tree's green state plus the crafted-fixture
mechanics were verified. The claim "Items 1–11 surfaces untouched" is verified only
indirectly (full suite green + diff scoped to the six listed files); no per-item
behavioral re-audit of Items 1–11 was performed.
