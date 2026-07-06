# Release Notes — Item 7: Resolution Matcher Fixes & Warning Reconciliation (SC-8)

**Epic:** UPSTREAM-FINDINGS Item 7 · **Branch:** upstream-findings-epic

## Summary

"Registry unresolved" warnings now mean something. Two matcher bugs that made
healthy models warn are fixed; a genuinely uncovered pipeline input now fails
loudly and precisely (new **V11** diagnostic) instead of generating a pipeline
that `KeyError`s at load; and the benign per-binding / per-collision noise is
demoted to DEBUG with one WARNING summary each.

## What changed

- **Two resolution matcher fixes** (`dependency_backtracker._resolve_to_design_attribute`):
  - **Bug A (REQ-BT-09):** the FORMULA `::`-QN REFERENCE path now per-segment
    sanitizes (`sanitize_qualified_name`), so a quoted-owner QN
    (`Lib::'IFE Driver'::power`) matches the sanitized design-attribute QN.
    Landed as a **six-site lockstep flip** (INV-1 grep clean).
  - **Bug B (REQ-BT-10):** a design attribute owned by a part **def** (empty
    `parent_part`) now matches its binding by a leaf-unique fallback over
    design-part attributes — calc-def I/O excluded (DEV-2 / A1), so a dotted
    calc-output reference stays unresolved and loud rather than cross-wiring.
- **V11 params-coverage check (REQ-GA-08):** a pure collector
  (`collect_uncovered_params`) plus an always-strict generation boundary. Fires
  on a fell-through ∩ valueless ∩ wired entry point (guaranteed runtime
  `KeyError`). The unwired remainder is a WARNING reconciliation summary (M1
  partition).
- **Warning reconciliation (D5):** per-binding Step-4 "Registry unresolved" line
  and per-collision alias line are DEBUG; a single WARNING alias count-summary
  (`OutputRegistry: N alias collision(s) resolved first-wins (M distinct keys)`).
- **README null-key correction (m2):** the JSON template **omits** null-default
  keys (the schema declares them required); the note said they appear awaiting
  values.

## Three-part behavioral review (R1/R2/R3)

### 1. Entry points that reclassified

- **retype_model — 3 EPs, `USAGE_LITERAL` → `DESIGN_ATTRIBUTE`** (via Bug A,
  quoted-owner `::` refs to def-owned design attributes):
  `ife_calc|p` (`RetypeLibrary::'IFE Driver'::power`), and `hif_calc|q`
  (`RetypeLibrary::'HIF Driver'::torque`, two usages). Default-value source
  switches from the unparseable usage-literal (→ `None`) to the design
  attribute's default. *(Computed in Phase 0; confirm at the gate — no committed
  retype_model baseline exists to diff against, see below.)*
- The Phase-0 worksheet's claimed solar_battery dedups (`pack_count`, `p_net_mw`)
  **do not occur** (DEV-1): `pack_count` is a literal binding (never reaches the
  resolver); `p_net_mw` is a `::`-form ref through the exact-match branch where
  sanitize is a no-op. No solar_battery reclassification.

### 2. Keys that collapsed (Step-3 dedup)

- **None in the committed corpus.** The two anchored dedup pairs do not occur
  (above). retype_model's reclassification changes the EPs' *kind and value*, not
  their key identity (the fallback QN and the design-attr QN coincide for these
  def-owned attrs). No params-JSON key set collapses.

### 3. Params-JSON values after

- **retype_model:** `p` → 10.0, `q` → 20.0, `q` → 20.0 (design-attribute
  defaults), replacing the `None` the USAGE_LITERAL fallback carried. *(Gate-confirm.)*
- **No clean-fixture value moved.** solar_battery / chain_spike / attr_expr_probe
  / sample_model params values are unchanged (no reclassification; their
  fell-through EPs were already valued via the deriver merge).
- **No committed baseline churns.** `baseline_outputs/` holds only attr_expr_probe,
  catf_mfe, chain_spike, sample_model, solar_battery — none reclassify.
  retype_model has **no** committed baseline, so there is no baseline file to
  regenerate; the review above is the record of its intended churn.

## V11 corpus surface (genuine pre-existing gaps, now loud)

V11 fires on five fixtures — every one a genuine fell-through ∩ valueless ∩ wired
gap that previously generated a latently-broken pipeline (importable ≠ runnable):

| Fixture | input | tracked to |
|---|---|---|
| catf_mfe | cryo_load.magnet_volume | Items 9-11 (cross-part `tf_coil.volume` EXPOSE) |
| alias_agg_probe | cost_model.base_cost | Item 9 (RedefinitionData → entry-point default) |
| issue22_model | cost_model.base_cost | Item 9 (same class) |
| unresolvable_attr_probe | my_calc.x | dedicated V11 proof fixture |
| chain_override_probe | cost_model.sensitivity | none — A1 keeps the calc-output ref loud by design |

**New suite exceptions:** `{catf_mfe E2E, alias_agg_probe E2E}` — inverted to
assert the V11 abort (pinned, not tolerated). Items 9-11 flip catf_mfe back to
clean; Item 9 flips alias_agg_probe / issue22 back. The other three trip V11 in
the collector (pinned green) but have no E2E generation test.

## Diagnostic

- **V11** added to `modeling-assumptions.md` Validation Rules (first
  generation-boundary rule; V1–V10 are extraction-time).
