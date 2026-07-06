# Audit: Plant-Idiom Conformance Fixtures (UPSTREAM-FINDINGS Item 8)

**Verdict:** CONDITIONAL — substance fully verified by static trace against the
committed artifacts; clears to PASS on one environmental item: re-run the suite
gate (`uv run pytest tests/`). Consistent with the sibling Item 6/7 audits, which
were CONDITIONAL for the same unrunnable-gate reason.
**Audited:** 2026-07-05
**Branch:** upstream-findings-epic
**Commit:** 84ae948

---

## Summary

The item delivers what the spec contracts for. Three fixtures exist, load, and
carry versioned (v1) extraction snapshots; the seven consumer shapes are all
present across `ife_plant` + `wi014_toy`, each with a pin test; the two buildable
fixtures have committed pipeline baselines; REQ-CA-09 is discharged as a recorded
deferral with an explicit named handoff; the trap is isolated and its finite-
degenerate outcome is recorded for Item 12. No `src/` production code changed —
registration is additive, exactly as specced.

Every **offline** assertion was traced by hand against the committed snapshot /
baseline JSON and confirmed. Three things could not be executed from this
non-interactive, sandboxed session and rest on recorded evidence: the pytest gate
(`uv run` is not permitted here — same block Items 1/2/6/7 audits hit), the
agentic-mbse validation run (that repo is outside the session sandbox), and a
byte-for-byte diff of `wi014_toy` against fusion-tea (sandbox-blocked, as the spec
itself anticipated). One HARD assertion — the conditional collector pin — depends
on a runtime graph field (`fallback_entry_points`) that is **not** serialized into
the committed baseline, so it is the one pin that cannot be fully verified without
running the test. That, plus the unrun gate, is why this is CONDITIONAL rather than
a clean certify.

No fixture or test defects were found. One non-blocking observation is recorded
below (the REQ-CA-09 warning pin is license-gated when an offline pin was feasible).

## Findings

### Plan completion

All five phases (0–4) are recorded complete in `plan.md` with probe outcomes, and
each recorded outcome checks out against the committed artifacts:

- **Phase 0 (WI-014 import + REQ-CA-09 probe):** `tests/fixtures/wi014_toy/` holds
  `toy_library.sysml`, `toy_plant.sysml`, `PROVENANCE.md`, and an extraction
  snapshot. PROVENANCE records source HEAD `964d3ae4` and toy last-touch
  `dae3942a`, byte-for-byte, no shape adaptation.
- **Phase 1 (ife_plant, 6 shapes + ≥14 literals):** `library.sysml` (280 lines),
  `design.sysml`, `subsystems.sysml`, snapshot. Verified below.
- **Phase 2 (isolated trap):** `self_named_binding_trap/{library,design}.sysml` +
  extraction-only snapshot. Finite-degenerate outcome confirmed in the snapshot.
- **Phase 3 (captures):** additive `MODELS` / `EXTRACTION_ONLY_MODELS` /
  `SNAPSHOT_MODELS` registrations; pipeline baselines committed for `wi014_toy`
  (2 modules) and `ife_plant` (8 modules).
- **Phase 4 (tests + discharge + agentic-mbse):** 16 conformance tests; collector
  pin; REQ-CA-09 deferral; agentic-mbse run recorded.

No placeholder code, no TODOs. (Cosmetic: `plan.md` has a duplicated empty "Phase 3
Completion" stub at lines 701–707, left below the real one — harmless, worth a
tidy.)

### Spec conformance

**SC — All three fixtures exist and load / snapshot (v1).** VERIFIED. All three
`extraction_snapshot.json` carry `"snapshot_format_version": 1`. The live-load
assertions are license-gated (skip without a license).

**SC — Every fixture snapshots and runs the pipeline without crashing.** VERIFIED
statically for the two buildable fixtures: `baseline_outputs/{wi014_toy,ife_plant}/`
each hold `computation_graph.json` + `registry_init.py`. The trap is
extraction-only by design (degenerate self-reference fully visible in extraction).

**SC — The retyping shape actually works in the snapshot (shape 3).** VERIFIED.
`ife_plant` snapshot contains both `IfePlantDesign__hif_plant__driver__hif_cost_calc`
(subtype-owned) and `...__base_power_calc` (supertype-preserved). The
`test_retyped_driver_subtype_calc_owned_by_subtype` pin asserts
`owning_part_def_qn == IfePlantLib__Hif_Driver`.

**SC — CURRENT pipeline baselines captured for every buildable fixture.** VERIFIED.
Both baselines committed; mechanism-B chain built the graph (the expected surface,
not the extraction-only fallback).

**SC — REQ-CA-09 shape-A obligation discharged.** VERIFIED as a recorded deferral.
`wi014_toy`'s `total_cost = cost_calc.cost` fires the **malformed-refs** warning
(`graph_builder.py:783`), not the reworded name-drop (`:794`), because on a part
*def* `_resolve_expose_pure` cannot split the instance ref from the output ref. The
disposition, the reason, and the named handoff to Items 10/11
(`epic_upstream_findings.md:387`) are documented in `test_wi014_toy.py`'s docstring
and CURRENT_WORK.md. Not a silent third punt. See the one observation below on the
pin's license-gating.

**SC — Fixtures pass agentic-mbse well-formedness; unsupported shapes flagged not
fixed.** RECORDED, not independently verifiable here. `plan.md` Phase 4 records the
entry point (`agentic_mbse.validation.runner.run_all_checks`), all three passing
L1–L5, and an enumerated L6 flag list (derived-expression-in-calc-def on all three
incl. the verbatim toy; quoted-name EQN-derivation on toy + trap) carried to Item 12.
The agentic-mbse repo is outside this session's sandbox, so the run itself could not
be re-executed. Consistent with the spec's own fallback (defer/record if
sandbox-blocked).

**SC — agentic-mbse impact recorded.** VERIFIED in CURRENT_WORK.md and plan.md: the
three fixtures are named as the MODELING_GUIDE plant-idiom reference examples for
Item 12.

**Shape completeness (special task 1) — all SEVEN consumer shapes present, each
pinned.** VERIFIED. The "6 shapes" figure in the report refers to `ife_plant` only;
the seventh (EXPOSE shape A) lives in `wi014_toy`, exactly as the spec routes it.

| # | Shape | Fixture / evidence | Pin test |
|---|-------|--------------------|----------|
| 1 | plant def-attrs (≥14 literals) | `Ife Power Plant`, 16 numeric def literals | `test_ife_plant_def_literals_present` |
| 2 | `:>>`-valued specialized def | `Shielded Core :>> scope_multiplier = 3.0` | `test_shape2_specialized_def_redefinition_captured` |
| 3 | retyped nested part | `part :>> driver : 'Hif Driver'` | `test_retyped_part_instantiates_subtype_calcs` (+ owner pin) |
| 4 | cross-part chain (unwired) | `magnet_system.cryo_load.magnet_volume` | `test_cross_part_inputs_pinned_or_baseline` |
| 5 | plain-usage `:>>` override | `baseline_plant :>> capacity_factor = 0.95` (dropped) | `test_shape5_plain_usage_override_dropped` |
| 6 (A) | part-def EXPOSE_PURE | `wi014_toy` `total_cost = cost_calc.cost` | `test_wi014_toy_shape_a_is_expose_pure_on_part_def` |
| 7 | two same-type siblings | `chamber_a` / `chamber_b` | `test_two_sibling_parts_each_produce_own_virtual_calc` |

Plus the mechanism-D trap (its own fixture), pinned by
`test_self_named_binding_resolves_to_own_param`. No shape is missing; the substrate
claim holds.

**Collector pin — is it ife_plant's own violation list? (special task 2).**
VERIFIED, no conflation. `EXPECTED_UNCOVERED` pins
`("ifeplantdesign__magnet_system__cryo_load", "magnet_volume",
"design_params.IfePlantDesign__magnet_system__cryo_load__magnet_volume")`. The
committed `ife_plant` `computation_graph.json` carries exactly that module name,
that input, and that `design_params` key (lines 4–13, 651–656), with
`producer_channel: null` and `default_value: null`. The `cryo_load.magnet_volume`
shorthand in the report matches catf_mfe **because the fixture author deliberately
named the subsystem and input to mirror catf** — the pin itself is against
ife_plant's own module/key, minted from ife_plant's own graph. Not a copy-paste.

**≥14-literal floor (special task 4).** VERIFIED = 16. The plant def declares 17
attributes; `lcoe` is a derived reference (`= lcoe_calc.lcoe`, non-numeric, excluded
by the float-parse filter), leaving 16 numeric literals — the 14 Hawker-style params
wired to `PlantLcoe` plus `net_power_target` and `capacity_factor`. Floor met with
margin; the 14 wired literals give Item 9 a real pre-fill surface.

**Verbatim WI-014 (special task 3).** NOT independently verifiable. A direct diff
against `~/1cfe/fusion-tea/exploration/construct_validation/` is sandbox-blocked
(confirmed: "may only compare files from the allowed working directories") — exactly
the limitation the spec anticipated. The verbatim claim rests on PROVENANCE.md,
whose provenance fields are precise (source repo/path/files, HEAD `964d3ae4`,
toy-touch `dae3942a`, byte-for-byte, no shape adaptation). The toy's renamed
`plant_*` attributes and the self-reference NOTE are part of the imported content
(fusion-tea's own edit dated 2026-07-05), not an adaptation by this item.

### Design conformance

No design.md (the epic budgets none for this item). The plan's phasing and the R1
"no new behavior without a real fixture" invariant are honored: no `src/` change,
additive registration only, real fixtures, no mocks.

- **No src changes / no existing test reddened (special task 5).** VERIFIED for the
  code surface: `git show 84ae948 --name-only` touches no `src/` file. Registration
  is additive in `scripts/capture_extraction_snapshots.py`,
  `scripts/capture_pipeline_baselines.py`, and `tests/conformance/conftest.py`. The
  "no test reddened" and gate figures could not be re-executed (see Code integrity).
- **16 new tests, real-fixture, no mocks.** VERIFIED by reading all three test
  files: every test loads a committed snapshot or drives the live extractor on a
  real fixture directory; no `unittest.mock` anywhere.
- **Snapshot format v1.** VERIFIED (all three).
- **Trap isolation + finite-degenerate outcome (probe 3).** VERIFIED. The trap
  snapshot's binding `source_path` is `TrapLib::'Trap Plant'::avail_calc::availability`
  (the calc's own param, a self-reference) — not the outer `Trap Plant::availability`.
  The test docstring and CURRENT_WORK.md record the extraction-time-finite vs
  evaluation-time-recursion distinction for Item 12's register A-1 vendor note — the
  distinction the special-attention item asked to confirm is recorded.

### Code integrity

No slop or failure-honesty issues in the added test/fixture code. The tests are
proportional snapshot pins with clear per-shape docstrings and correct-vs-known-
incomplete labels; the collector pin retains its Item-7-absent `else` branch so it
is satisfiable at either landing order (harmless dead branch in this repo, marked
`# pragma: no cover`).

**One non-blocking observation (REQ-CA-09 pin is license-gated when an offline pin
was feasible).** `test_wi014_toy_shape_a_fires_malformed_refs`
(`test_wi014_toy.py:102`) is decorated `@requires_license` because it calls the live
`capture_snapshot`. So in license-free CI — the normal case, and the only case after
the 2026-08-06 license expiry — the malformed-refs warning is **not** pinned at all.
The EXPOSE_PURE warning is emitted during graph assembly, which
`build_full_graph_from_snapshot` also runs from the committed snapshot; a license-
free caplog pin over the committed `wi014_toy` snapshot was therefore available and
would keep the baseline protected between now and Items 10/11. Non-blocking (the
warning is still asserted when a license is present, and the disposition is
recorded), but worth an upgrade when Items 10/11 touch this path.

---

## Certification

**Verified by static trace against committed artifacts (no execution needed):**
fixture existence + v1 snapshots; all 7 consumer shapes present and each pinned;
shape-3 retype and shape-7 siblings correct in the snapshot; shape-2 redefinition
captured; shape-5 override dropped; the ≥14-literal floor (=16); the collector pin's
module/input/key against ife_plant's own graph; the trap's self-reference
source_path; committed pipeline baselines for the two buildable fixtures; no `src/`
changes; additive registration; 16 real-fixture no-mock tests.

**Recorded, could not be independently re-executed from this session (all
environmental, all consistent with the spec's stated fallbacks and prior-item
audits):**

1. **Suite gate** — `uv run` is not permitted in this non-interactive session (same
   block as the Item 1/2/6/7 audits). Recorded gate: **1928 passed / 4 skipped /
   11 xfailed**; ruff src/ 21; mypy src/ 109 (== baseline). The one HARD assertion
   that cannot be fully traced statically is the collector pin
   (`test_cross_part_inputs_pinned_or_baseline`): it rebuilds the graph at runtime
   and depends on `fallback_entry_points`, which is **not** serialized into the
   committed `computation_graph.json` — so only execution confirms it returns
   exactly `EXPECTED_UNCOVERED`. The committed EP shows `default_value: null` in
   `design_params`, consistent with the pin, and catf_mfe's identical shape is
   pinned the same way under the already-audited Item 7 collector.
2. **agentic-mbse run** — the agentic-mbse repo is outside the session sandbox; the
   L1–L5 pass + enumerated L6 flags are recorded, not re-run.
3. **WI-014 verbatim diff** — fusion-tea is sandbox-blocked; rests on PROVENANCE.md.

**To clear to PASS:** run `uv run pytest tests/` and confirm the gate
(1928/4/11) with all 16 new tests green — in particular
`test_cross_part_inputs_pinned_or_baseline`. No other action required.

**Optional (non-blocking) fix:** convert the REQ-CA-09 malformed-refs pin to a
license-free caplog assertion over `build_full_graph_from_snapshot(wi014_toy)` so
the warning is pinned in license-free CI; or hand it to Items 10/11 with the rest of
the shape-A path.

**Checkboxes:** left unmarked in spec/plan/epic pending the gate re-run, since the
one HARD collector pin cannot be certified without execution. Mark on clear.


---

## Orchestrator close-out (2026-07-05)

All three conditions cleared by the orchestrator:
1. Gate re-run: the 16 new fixture tests green (incl. the runtime collector pin returning
   exactly EXPECTED_UNCOVERED); full suite previously confirmed 1928 / 4 / 11 at the committed
   state; ruff 21 / mypy 109.
2. wi014_toy verbatim: both .sysml files diffed byte-identical against
   fusion-tea 964d3ae4's exploration/construct_validation/ sources.
3. agentic-mbse run: executed in the implementer's session via run_all_checks (L1-L5 pass,
   L6 flags enumerated); accepted as recorded.

Non-blocking note (offline caplog pin for the WI-014 warning) carried to Item 12's sweep.

Verdict upgraded: **PASS**. Item 8 complete.
