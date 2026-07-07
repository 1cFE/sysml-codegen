# Run Report: fusion-tea Acceptance & Workaround Retirement (PIPELINE-TRUTH Item 3)

**Date:** 2026-07-06
**This repo:** sysml-codegen `pipeline-truth-epic` — commits `36d3394`, `c44d7bb`, `5946f7c`
**fusion-tea repo:** branch `chore/retire-pipeline-truth-workarounds` (off `epic/pipeline-derisk-demo`) — commits `5a889ac5`, `2286e5aa`
**License:** live in this session — all live legs actually ran (not skipped).

The epic's real-world proof is assembled and runs end-to-end from generated artifacts alone:
zero bridges, zero hand-plumbing, single pass. Every acceptance number below is a real
execution result, and every perturbed/hand-computed target was derived independently of the
executor.

---

## SC-A — end state assembled, zero offenders both states

| State | What | Result |
|---|---|---|
| (i) instance present | committed in-repo v2 snapshot `tests/fixtures/fusion_tea` | `generate` emits full package, **zero V11 offenders** (`test_fusion_tea_snapshot_zero_offenders`, green) |
| (ii) instance deleted | fusion-tea models with `hif_driver_instance` removed, re-captured v2 snapshot | `generate` → 6 modules (was 7), **zero V11 offenders**, Meier channels re-anchored to `hif_plant_pkg__hif_plant__driver__meier_cost__*`, zero `hif_driver_instance` |

State (ii) verified two ways: live `--models` generate and `--from-snapshot` on the
re-captured `ife_workaround_free.snapshot.json` — both zero-offender, both canonical channels.

## SC-B — run-C reproduces + proven consumed

Through `run_pipeline` on the generated package (in-repo, license-free) AND the real teax
executor (`run_anchors.py`, fusion-tea):

| Anchor | Value (exact) | Target | Result |
|---|---|---|---|
| C — full pipeline lcoe | `270.1211779380445` | `270.1211779380445` | bit-exact, rel 1e-6 |
| C — Meier gamma | `68.247088` | hand-math (hif_economics) | OK |
| C — Meier capital $B | `3.30388687` / `3.303886865568384` | hand-math | OK |
| C — Meier COE c/kWh | `4.73540355` | hand-math | OK |
| C — f_recirc | `0.07222302470027446` | `1/(0.35·80·1.15·0.43)` | OK |
| A — module-level | in-repo: gamma `68.247088`, cost_billions `0.9749584`; fusion-tea: lcoe `252.29996307` | hand/oracle | OK |
| B — module-level | in-repo: f_recirc `0.07222302470027446`; fusion-tea: lcoe `68.69020165` | hand/oracle | OK |

**Perturbed-key proof (consumed, not baked-default):** move the emitted lcoe gain key
`hif_plant_pkg__hif_plant__lcoe_calc__gain` 80 → 100.

- Hand-computed target (independent, from `ife_lcoe.sysml:53-125` arithmetic with gamma
  68.247088 unaffected by gain): **`216.55528392479388`**.
- Executor (in-repo `run_pipeline` with `inputs=` override): `216.55528392479388` — bit-exact.
- Executor (fusion-tea real teax, emitted JSON edited in place then restored):
  `216.55528392` — matches oracle.

The perturbation moves lcoe alone: `gain` is emitted **per-consumer** (`lcoe_calc__gain`,
`recirc_calc__gain`), not collapsed by source QN — it is a plant DESIGN_ATTRIBUTE bound into
each calc usage, unlike the cross-part `driver__efficiency` which does collapse to one key.

## SC-C — every workaround deleted (operative surface, all greps ZERO)

| # | Workaround | Action | Grep (models + `exploration/ife_e2e/*.py`) |
|---|---|---|---|
| R-1 | `sanitize_names.py` | file deleted | `sanitize_names` → **0** |
| R-2 | `part hif_driver_instance` | deleted both model copies; Meier channels re-anchored | `hif_driver_instance` → **0** |
| R-3 | two-pass gamma feedback | deleted from `run_anchors.py` | `two.pass\|second pass\|gamma feedback` → **0** |
| R-4 | hand-written input JSONs | `run_anchors.py` reads emitted `generated/inputs/` | (reads INPUTS_DIR; no pre-run writes) |
| R-5 | bridge in harness | none in canonical `run_anchors.py` | `bridged` → **0** |
| R-6 | six `out attribute` | **KEPT** (see Phase 3 notes: non-workaround optional style, genuine outputs, matches fixture) | n/a — decision logged |

**Kept by design:** teax OutputRouter/WriteHandler (T-1/T-2); `sweep_ife.py`'s ηG>10 viability
check (harness-side until the constraint-execution epic). `sweep_ife.py` needed no re-anchor —
it calls the generated impls directly and never used the instance channel path.

**Historical references left intact (scope note):** `work/` (report, WI-015 findings, evidence,
snapshots), `.project/reports|research`, and demo docs still name the workarounds as historical
record — not rewritten (they document the workaround when it existed; not this item's to falsify).

## SC-D — SNAP-19 parity parametrized + fusion-tea leg

- `test_live_vs_snapshot_byte_identical` parametrized over 6 shape-bearing fixtures
  (solar_battery_model, retype_model, quoted_owner_formula, alias_agg_probe, ife_plant,
  plant_values) — all green with license. Full-tree diff = channel identity (comment pins why).
- `test_fusion_tea_live_vs_snapshot` (new) — vendored whole-plant fixture byte-identical live
  vs snapshot — green.
- **R1 mis-wire probe:** repointing ife_plant's snapshot channel source failed the gate; reverted.

---

## Recorded constraint-drop report (spec fact 2 — expected output, not a surprise)

`generate` on the fusion-tea models emits, every run:

```
Constraint drop report: scanned 1 ConstraintUsage (incl. subtypes), reported 1 droppable
  (1 assert, 0 require/plain), excluded 0 requirement/satisfy.
Constraint 'viability' on part def 'IFE_Power_Plant' is not executable and was dropped
  (constraints are not compiled to pipeline modules; see modeling-assumptions.md).
WARNING: Dropped 1 constraint usage(s) across the model ...
```

The Item-4 fix makes the `assert constraint viability` drop loud and true. Executing the
constraint stays deferred (ηG>10 remains harness-side in `sweep_ife.py`).

## Deviations from plan (surfaced, not massaged)

1. **Runner multi-output completion (in-repo, `tests/runtime/pipeline_runner.py`).** fusion_tea
   is the first *multi-output* package run through `run_pipeline`; the twolevel fixture was
   single-output only. Two faithful stub/token completions were needed to run it at all — a
   `simkit.config.schema.MultiOutput` surface and recognizing bare multi-output channel sources.
   The generated YAML wiring was already correct (the report proved anchor C via the teax
   executor); only the in-repo runner's classifier was single-output-only. **Not** a resolution
   patch — no `src/` touched. Flagged for audit.
2. **Anchors A/B definition.** In-repo A/B are the meier_cost and recirc modules in isolation;
   fusion-tea A/B are the lcoe calc at the Hawker/Realistic points (reproducing the documented
   $252.30 / $68.69). Both are legitimate "module-level own-semantics" checks; the report's
   historical dollar anchors are reproduced by the fusion-tea harness.
3. **R-6 kept, not reverted** (rationale above).
4. **Scope of retirement greps** to the operative surface (rationale above).

## Coordination actions (report §"Coordination actions" — discharged)

1. `sanitize_names.py` deleted; WI-015 repro step 2 is dead. ✔
2. `part hif_driver_instance` deleted; Meier channels re-anchored in `run_anchors.py`. ✔
   (`sweep_ife.py` needed no change — never used the instance path.)
3. Six `out attribute` → **kept** (verified-safe optional style; not reverted). ✔ (logged)
4. `run_anchors.py` simplified: two-pass + hand-input-writing dropped, T-1/T-2 router kept,
   single-pass anchors + perturbation. ✔
5. `sweep_ife.py` ηG>10 kept; no constraint warning expected until AssertConstraintUsage work. ✔
6. v2 snapshot captured (`ife_workaround_free.snapshot.json`) — decouples future inspection
   from the license. ✔

## Item-9 / Item-10 / R2

- **Item-9 impact (verification matrix / release notes):** Item 3 adds SC-A (both offender
  states), SC-B (270.12 + perturbation consumed), SC-C (retirement greps zero), SC-D (6-fixture
  parity + fusion_tea leg). New in-repo tests: `test_fusion_tea_acceptance.py` (4),
  `test_fusion_tea_live_vs_snapshot`, SNAP-19 parametrized (6). Suite 2056 → 2066 passed.
  One flagged deviation for the audit: the runner multi-output completion.
- **Item-10 impact (close-out):** fusion-tea PR to open from
  `chore/retire-pipeline-truth-workarounds` per their norm; this repo's tests are on
  `pipeline-truth-epic`. No new close-out touchpoints beyond the PR.
- **R2 (agentic-mbse lockstep): none new.** This item changes no executable SysML subset and no
  auditor behavior — it consumes landed mechanisms and retires workarounds. Recorded explicitly.

## This repo — gate status (no regression)

- Suite: **2066 passed, 4 skipped, 5 xfailed** (was 2056 / 4 / 5).
- ruff `src/`: **17** (unchanged). mypy `src/`: **104** (unchanged). Changed files (all `tests/`)
  ruff-clean.
