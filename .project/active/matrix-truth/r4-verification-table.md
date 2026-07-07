# R4 Verification Table — Item 7 (REQ/Matrix Reconciliation)

**Produced:** 2026-07-06 (Phase 9). **Protocol:** R4 (epic names Item 7 a verification-table producer).
Each finding → the probe/evidence that decided it → verdict (CONFIRMED / NOT-REPRODUCED / RECLASSIFIED).

## F4 — Input Resolver family pins unwired code

| Finding | Probe / evidence | Verdict |
|---------|------------------|---------|
| `resolve_input`/`AGG_STRATEGIES` has zero production callers | grep of `src/` (only `input_resolver.py` self-refs) | **CONFIRMED** |
| Module channel-resolution matches the live path | probe (i) extended parity, `probe_i_run_log.txt` — 0 kills over plant_values/plant_value_shapes/spec_chain_twolevel (1 MO + 5 EP checks), now committed as `TestResolveInputParityExtended` | **CONFIRMED no-kill** |
| Strategy D dedup churns consumer-depended keys | probe (ii), `probe_ii_run_log.txt` — 0 key churn on catf_mfe + solar_battery; trigger never co-occurs with a fall-through EP | **NOT-REPRODUCED** (→ delete Strategy D, filed) |
| Live path drifted from the module since COST-PATTERN birth | probe (iii), `probe_iii_module_drift.md` — `_resolve_aggregation_input_channel` byte-identical since `d6c725f`; zero post-birth live fixes | **NOT-REPRODUCED** (no drift) |
| A naive `resolve_input` drop-in is baseline-safe | probe (iv), `probe_iv_ep_key_divergence.md` — leaf-only fallback EP collides with an existing output channel in solar_battery's baseline; part-usage disambiguator dropped | **CONFIRMED divergence** (→ cutover is a refactor, split out) |
| **Verdict** | LAND-with-split. Rows/docs reframed to "parity-validated, not-yet-wired"; cutover filed `[ITEM7-F4-CUTOVER]` | **RECLASSIFIED** (PASS-pins-dead-code → capability-pinned) |

## F2 — Registry contract text contradicts the code

| Finding | Probe / evidence | Verdict |
|---------|------------------|---------|
| `instance_attr_to_channel` dict bypasses the typed-registry contract | read `output_registry_builder.py:164-189` — dict feeds only guarded `register_alias`; registers nothing itself (B3) | **NOT-REPRODUCED** (→ fix text, not code) |
| REQ-OR-05/06/08 + doc-10 text falsely say Key_A/Key_F unregistered | code: Phase 1a `register_alias(Key_A)`, Phase 1c `register_scoped(Key_F)` | **CONFIRMED** (→ reframed to actual registrations) |
| REQ-ORCH-04's `min(phase1)<min(alias)` is vacuous | Phase-1a interleaves scoped/alias in one loop | **CONFIRMED** (→ replaced with presence assertion) |
| Presence assertion actually fails on a phase-order regression | **red-mutation gate**: swap Phase-1a `register_scoped`/`register_alias` order → guard warns "phase ordering violation", aliases dropped → test **RED**; revert → **GREEN**; src reverted clean | **CONFIRMED** |
| Two docstrings misstate their own bodies (`test_output_registry.py`, `test_orchestrator.py`) | read both | **CONFIRMED** (→ fixed) |

## Divergent-PASS rows (D7 list)

| Finding | Evidence | Verdict |
|---------|----------|---------|
| REQ-EXT-09 part-usage-owner leg missing | `test_extractor.py:888-934` (Item 4) present, anti-pattern-free | **NOT-REPRODUCED** (DONE) — PASS honest |
| REQ-PGD-08 cited file doesn't cover the claim | `test_matcher_fixes_item7.py` exists in `tests/unit/` and pins backtracker propagation | **NOT-REPRODUCED** — PASS honest |
| CA-05, PY-01/03/05, GEN-02, SR-07, DM-06/07, GA-07 pin less than text | read each cited test | **CONFIRMED** (→ text reframed to what the test checks, INV-B) |

## Counts & sweep

| Finding | Evidence | Verdict |
|---------|----------|---------|
| Summary 252/240/12 miscounts (PGD-06 PENDING counted as PASS) | row-by-row recount | **CONFIRMED** → regenerated to 253 = 249 PASS + 4 UNTESTED (DM-08, PGD-06, RES-05, RES-08) + 0 PENDING |
| Footer "33 test files" wrong | recount → **57 distinct cited** (41 conformance + 16 unit/integration); definition stated beside the number | **CONFIRMED** |
| ~175 PASS rows never deep-read | Phase-8 leashed sweep (delegated deep-read of ~167 qualifying rows) surfaced SR-03 (6-case), EXT-07, EXT-14 (reframed in-matrix) + ~30 pins-narrower findings — all PASS-but-narrower, no correctness lies | **CONFIRMED** → findings filed `[ITEM7-MATRIX-SWEEP-RESIDUE]`; unswept residue named there with count |

## Filings produced by Item 7

- `[ITEM7-F4-CUTOVER]` — executable aggregation-rewire follow-on (comparand M3, EP-key M4, Strategy D delete).
- `[ITEM7-MATRIX-TEST-GAPS]` — 3 rows with no honest pinning test (DM-08, RES-05, RES-08).
- `[ITEM7-CLASSIFIER-FIX]` — inherited-attr EXPOSE_COMPUTED misclassification behind the loud xfail.
- `[ITEM7-MATRIX-SWEEP-RESIDUE]` — the deep-read sweep findings + unswept residue.
- Retired: `DOCS-SCRUB-F2`, `DOCS-SCRUB-F4`, `[ITEM7-PGD06]`.
