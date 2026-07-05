# Design: Baseline Repair & Silent-Failure Diagnostics

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-07-05
**Complexity:** LOW (hardening; ~0.5–1 day)
**Branch:** upstream-findings-epic (HEAD `2601b55`)
**Epic:** UPSTREAM-FINDINGS — Item 1

---

## Overview

Repair the one red baseline (recurrence-proof, by sorting the graph at its source) and turn
three silent/opaque failures into V-rule-style diagnostics — without changing what valid models
generate.

## Related Artifacts

- **Spec (contract):** `.project/active/baseline-diagnostics/spec.md`
- **Spec review:** `.project/active/baseline-diagnostics/spec-review.md`
- **Epic:** `.project/backlog/epic_upstream_findings.md` (Item 1 + R1/R2/R3)
- **Research:** `.project/research/20260705_upstream-findings-deep-research.md` (SC-1/2/7)
- **Contract doc:** `docs/architecture/modeling-assumptions.md` (V-rules; gains a constraints section)
- **Required Reading:** fusion-tea findings register (outside sandbox; covered by the research report)

---

## Research Findings

All four code sites in the spec were confirmed at HEAD. Two findings **change where two of the
fixes must live** — both inside the authority the spec's Open Questions delegated to design.

**Confirmed as spec states:**

- **Baseline sort site.** `graph_builder.py:362-366` constructs `ComputationGraph` with
  `entry_point_groups=param_groups`. `param_groups` is built in discovery order; sorting it by
  `group.name` immediately before construction is the true source (line 364 is correct). The
  downstream `qn_to_group` build (`graph_builder.py:343`) and the YAML renderer
  (`generation/pipeline.py:66-87`) both iterate the list order-independently, so the sort is safe.
- **Zero-output crash.** `templates/teax_module.py.jinja2:118,122` index `output_attributes[0]`
  in the single-output branch → `IndexError` on zero outputs. No guard exists upstream.
- **EXPOSE_PURE warnings.** `_resolve_expose_pure` (`graph_builder.py:648-689`) has two distinct
  warnings — malformed-refs (672-675) and key-not-found (683-687) — plus the Phase-3 registration
  warning (`output_registry_builder.py:182-186`). Only the last two are the name-drop path.
- **No existing calc def extracts zero outputs** (checked all `extraction_snapshot.json`), and no
  baseline calc def carries a constraint on the *part-def* path — so both new hard checks are
  no-ops for the current green corpus.

**Finding 1 — the constraint drop is on the calc-def path, not the part-def stub.**
The spec names `_extract_part_definition` (`extractor.py:106`, `constraints = []`) as the drop
site. But `extract_part_definitions()` is **called nowhere on the live generation path**
(`pipeline_builder.py` only calls `extract_calculation_definitions()` at line 482). Meanwhile
`catf_mfe`'s dozens of constraints all live **inside calc defs** (e.g. `ThermalCycleEfficiency`,
`TorusMinorRadius` in `library/physics/*.sysml`), and `_extract_calculation_definition` skips them
silently — its member loop `continue`s on anything that is not an `AttributeUsage`
(`extractor.py:151-153`), and `CalculationDefinitionData` has no constraints field at all. So the
diagnostic that funds the `catf_mfe` success criterion **must detect ConstraintUsage members in
the calc-def path**. The part-def stub stays as-is (off the live path; harmless).

**Finding 2 — which EXPOSE_PURE warning a shape-A fixture fires is unverified.** The research says
shape A trips the key-not-found warning via a simple-name-vs-EQN mismatch. But by the code,
`ca.references[].name` are simple names (`cost_calc`) and `calc_usage_names` holds backtracker
instance EQNs (`graph_builder.py:193`); if the simple name is not in that set, `instance_name`
stays `None` and the **malformed-refs** warning (672) fires instead — the one the spec says to
leave unchanged. Which path fires cannot be settled by reading; it needs a live probe of the
shape-A fixture. This is the item's single de-risk-first task (see Handoff).

**Diagnostic convention.** The codebase has no `ExtractionError` class and does not implement the
V1–V6 strings literally — V-rules are documented in `modeling-assumptions.md` but hard checks are
raised as plain `raise ValueError(f"…")` with a descriptive message (e.g.
`parameter_groups.py:309`, `graph_builder.py:777`). WARN/INFO use the stdlib `logger` already
present in each module (`extractor.py:27`). No warning/error *codes* convention exists. New
diagnostics follow this: `ValueError` for hard fails, `logger.warning/info` for soft ones, V-rule
prose shape (what happened · where · what to do).

---

## Core Concept

Four small, independent changes, each routed to the site that already owns the concern:

1. **Determinism at the source.** Sort `param_groups` by `group.name` once, where the graph is
   built — so every consumer of `entry_point_groups` (YAML today, Item 2's snapshot rebuild
   tomorrow) inherits a stable order. Then re-capture the one baseline whose order actually shifts.
2. **Make each silent drop speak, at the site that drops it.** Constraints are dropped in the
   calc-def extractor → count and log there. Zero outputs slip past extraction into Jinja → hard-fail
   at extraction. EXPOSE_PURE name-drops warn with bare text → reword the two name-drop warnings.

No new module, class, or abstraction. Each change is a few lines at an existing site plus a
fixture and a conformance test. The unifying principle is R1's "compute/detect once, at the
source" — the same reason the sort goes in the graph, not the template.

## Key Bets

- **B1.** `catf_mfe`'s constraint usages are reachable as `ConstraintUsage` members of the calc-def
  element during extraction (same `owned_members` loop that today yields `AttributeUsage`).
  *If false → the summary WARN never fires against `catf_mfe` and SC-1 has no real-fixture test.*
- **B2.** A minimal shape-A EXPOSE_PURE fixture fires one of the two reworded name-drop warnings
  (683 or Phase-3), not only the malformed-refs one. *If false → REQ-CA-09's real-fixture test is
  unfundable in Item 1 and defers to Item 8 (recorded fallback).*
- **B3.** Sorting `param_groups` by name is a semantic no-op: entry-group order never affects
  execution, only serialization. *If false → re-capturing solar_battery would change meaning, not
  just ordering, and the "no behavioral change" success criterion breaks.*

## Key Decisions

- **D1.** Sort `param_groups` by `group.name` in `graph_builder` immediately before
  `ComputationGraph(...)` (line 364), scoped to that list only. *Rejected: sorting in
  `generation/pipeline.py:66` (spec's original cite) — leaves the graph itself discovery-ordered,
  so Item 2's snapshot rebuild stays non-deterministic; contradicts "fix at the source."*
- **D2.** Detect dropped constraints in `_extract_calculation_definition` (live path); emit
  per-constraint INFO inline and one summary WARN after the loop in
  `extract_calculation_definitions()`. *Rejected: detecting in `_extract_part_definition` per the
  spec's literal cite — that method is off the live generation path, so the diagnostic would never
  fire against `catf_mfe`. Rejected: an orchestration-time summary — needs cross-method plumbing
  for no gain, since all live constraints are calc-def-owned.*
- **D3.** Zero-output check raises `ValueError` right after `output_attributes` is populated, before
  the `CalculationDefinitionData(...)` return (`extractor.py:~214`); fail on the first offender.
  *Rejected: collect-all-then-report — "fail-fast" is the spec's word and the crash it replaces is
  already fatal.*
- **D4.** Rewording is text-only on the two name-drop warnings (`graph_builder.py:683-687`,
  `output_registry_builder.py:182-186`); the malformed-refs warning (672-675) is untouched.
  *Rejected: rewording all three — the malformed-refs case is a different failure.*
- **D5.** Number new REQs sequentially per family: **REQ-BASE-05/06, REQ-EXT-08 (zero-output),
  REQ-EXT-09 (constraint drop), REQ-CA-09 (EXPOSE wording)**. *Rejected: the spec's proposed
  30-band (REQ-EXT-30/31, REQ-CA-30) — the matrix numbers every family sequentially (EXT tops out
  at 07, CA at 08, BASE at 04); a 30-jump is an unexplained gap. BASE-05/06 match the spec already.*

## Architecture

Four independent edits, no shared state beyond one per-extractor counter:

```
graph_builder.build_computation_graph
  └─ sort param_groups by name ───────────────► deterministic entry_point_groups (D1)

extractor.extract_calculation_definitions        (loop)
  └─ _extract_calculation_definition
        ├─ count ConstraintUsage members ──────► logger.info per constraint (D2)
        │     accumulate → self._dropped_constraint_count
        └─ if not output_attributes: raise ValueError (V-rule) ──► fail-fast (D3)
  └─ after loop: if count: logger.warning(summary) (D2)

graph_builder._resolve_expose_pure  (key-not-found branch) ──► reworded WARN (D4)
output_registry_builder  (Phase-3 branch) ──────────────────► reworded WARN (D4)
```

Data flow is otherwise unchanged. The constraint counter is a private `int` initialized in
`SysMLDataExtractor.__init__` and reset per extraction run; nothing downstream reads it.

## Required Invariants

- **I1.** `entry_point_groups` is sorted by `group.name` in every `ComputationGraph`. Testable:
  assert the list equals its name-sorted copy for every baseline.
- **I2.** The three currently-green YAML baselines (chain_spike, attr_expr_probe, sample_model) and
  all extraction snapshots are byte-identical after the change. Only `solar_battery.yaml` is
  re-captured. This is the hard "no behavioral change" gate.
- **I3.** A calc def with zero output attributes never reaches generation — it raises at
  extraction. Testable on the zero-output fixture.
- **I4.** Generating `catf_mfe` emits exactly one constraint summary WARN plus N INFO lines
  (N = constraint count), and no per-constraint WARN.

## Component Overview

- **Sort (D1)** — `resolution/graph_builder.py`, ~1 line before line 364. `param_groups` reassigned
  to `sorted(param_groups, key=lambda g: g.name)`.
- **Constraint diagnostic (D2)** — `extraction/extractor.py`. A counter field + a member-type branch
  in `_extract_calculation_definition` that INFO-logs each `ConstraintUsage` by name and increments
  the counter; a summary WARN after the loop in `extract_calculation_definitions()`.
- **Zero-output fail-fast (D3)** — `extraction/extractor.py`, guard before the calc-def return.
- **EXPOSE wording (D4)** — two `logger.warning` string edits, no logic change.
- **Fixtures** — `tests/fixtures/zero_output_calc/` (minimal, funds D3) and
  `tests/fixtures/expose_pure_shape_a/` (minimal, funds D4). Modeled on `chain_spike_model`'s
  library/design split.
- **Docs** — `modeling-assumptions.md` gains a "constraints are not executable" section and a V7
  row (zero-output) in the Validation Rules table; reference docs `01-extraction.md` (EXT-08/09)
  and `16-computed-attributes.md` (CA-09) get rows; `verification-matrix.md` gains five rows.
- **Dead-code deletion (D2/spec)** — remove `extraction/constraints.py` and
  `templates/constraint_validator.py.jinja2`; keep `constraint_extractor.py`.

## Non-Goals

- Constraint execution, return-style/bare-`in` extraction (Item 3), alias surfacing (Item 11),
  warning the silent shape-B EXPOSE drop (Item 11) — all deferred per spec.
- Any change to `_extract_part_definition` beyond leaving its stub. It is off the live path;
  wiring it in is not in scope.
- Deleting `constraint_extractor.py` or the `PartDefinitionData.constraints` field.

## Implementation Notes

- **Diagnostic wording (V-rule shape: what · where · what to do).** Final strings:
  - **Zero-output (D3), `ValueError`:**
    `"Calc def '{name}' extracted with zero output attributes. A pipeline module needs at least one output channel. Likely cause: return-style ('return y : Real = expr') or bare 'in' parameters, which are not yet extracted (Item 3); anonymous 'return' is unsupported. Declare an 'out attribute'."`
  - **Constraint per-item (D2), `logger.info`:**
    `"Constraint '{constraint_name}' on calc def '{calc_def_name}' is not executable and was dropped (constraints are not compiled to pipeline modules; see modeling-assumptions.md)."`
  - **Constraint summary (D2), `logger.warning`:**
    `"Dropped {n} constraint usage(s) across the model; constraint predicates are not executable and do not appear in generated output. See the 'Constraints are not executable' section of modeling-assumptions.md."`
  - **EXPOSE key-not-found (D4), reworded `logger.warning`:**
    `"EXPOSE_PURE %s: derived-attribute name is dropped from generated output — no alias is emitted. Its value was expected on canonical channel '%s', which is not registered (name-form mismatch; part-def shape-A resolution is Item 10/11)."` (`ca.name`, `catalog_key`)
  - **EXPOSE Phase-3 (D4), reworded `logger.warning`:**
    `"Phase 3: EXPOSE_PURE alias '%s' is dropped from generated output — canonical channel '%s' is not in the registry, so no named alias is emitted."` (`scoped_key`, `alias.canonical_name`)
- **Constraint metaclass string.** Detect via `self.adapter.is_instance(member, "ConstraintUsage")`.
  Confirm the exact SysIDE type name with a one-line probe before wiring (the member loop already
  uses `is_instance` with metaclass strings). If inline `constraint` bodies surface as a different
  metaclass, adjust the string only.
- **Sort stability.** `group.name` is unique per design file (one group per file), so the sort is
  total and stable. Do not sort module inputs, modules, or exit points — scope creep would churn
  the other baselines (spec review L3-2).
- **Counter reset.** Initialize `self._dropped_constraint_count = 0` in `__init__`; the summary
  reads it after the calc-def loop. No global state.
- **Baseline re-capture.** `uv run python scripts/capture_baseline_yaml.py` regenerates all four;
  commit only the `solar_battery.yaml` diff (the other three must show no change — that is I2's
  guard). Requires the live syside license (valid to 2026-08-06, in window). Never hand-edit (R3).

## Potential Risks

- **B2 (EXPOSE fixture)** is the real risk. Mitigation: probe first (Handoff). If the shape-A
  fixture fires only the malformed-refs warning, invoke the spec's recorded fallback — defer
  REQ-CA-09's real-fixture test to Item 8's WI-014 toy, keep the wording change (it is correct
  regardless), and note the deferral in the verification matrix. Do **not** reword the
  malformed-refs warning to force a test to pass.
- **Constraint metaclass mismatch (B1)** — cheap to check with the same probe; adjust the string.
- **Sort churns another baseline (B3 false)** — contradicts the spec review's verified no-op for
  the three green baselines; I2's byte-identical assertion catches it immediately if it happens.

## Integration Strategy

Additive hardening on top of the frozen refactor. No ComputationGraph schema change (the sort
reorders an existing field's contents). No new dependencies. The dead-code deletion is verified
unimported (spec D2). Everything composes with existing extraction, resolution, and generation —
each edit is local to one function.

## Validation Approach

Real-fixture conformance tests, no mocks (R1). Verification-matrix rows:

| REQ | Behavior | Test | Fixture |
|-----|----------|------|---------|
| REQ-BASE-05 | solar_battery YAML re-captured via script | `test_baselines.py` / `test_gen_pipeline_yaml.py` | solar_battery_model |
| REQ-BASE-06 | `entry_point_groups` name-sorted in every graph (I1) | `test_graph_assembly.py` | all baselines |
| REQ-EXT-08 | zero-output calc def raises at extraction (I3) | `test_extractor.py` | `zero_output_calc` (new) |
| REQ-EXT-09 | dropped constraints → 1 summary WARN + N INFO (I4) | `test_extractor.py` (caplog) | catf_mfe_model |
| REQ-CA-09 | EXPOSE_PURE name-drop warning reworded | `test_computed_attributes.py` (caplog) | `expose_pure_shape_a` (new) |

- **Full suite green** on the branch after re-capture (top success criterion).
- **I2 byte-identical guard**: the three green YAML baselines + all extraction snapshots unchanged;
  assert in the baseline test that only solar_battery differs.
- **Fixtures** — `zero_output_calc`: one calc def with an `in` attribute and **no** `out attribute`
  (e.g. a body-only or empty calc def), instantiated once; must load and trigger D3 without Item 3.
  `expose_pure_shape_a`: a library part def owning a calc usage plus an EXPOSE attribute
  (`attribute total_cost : Real = cost_calc.total_cost;`), instantiated by a separate design part —
  the "toy" shape. Capture extraction snapshots for both via
  `scripts/capture_extraction_snapshots.py`.
- **Manual**: run generation on `catf_mfe` and eyeball the one summary WARN + INFO lines; confirm no
  per-constraint WARN noise.

## Next-Stage Handoff

**De-risk first (before any other SC-7 work):** write the `expose_pure_shape_a` fixture and run a
throwaway probe through `build_pipeline_context` to observe which `_resolve_expose_pure` warning
fires. Branch on the result:
- Fires 683 (key-not-found) or Phase-3 → proceed; that fixture funds REQ-CA-09.
- Fires only 672 (malformed-refs) → invoke the fallback: keep the wording edits, defer REQ-CA-09's
  real-fixture test to Item 8, record it in the matrix. Do not touch the malformed-refs warning.

**Fixed** (do not relitigate): D1 sort site and scope; D2 calc-def detection path; D3 fail-fast at
extraction; D4 two-warning rewording; D5 sequential REQ numbers; the dead-code deletion; the
byte-identical baseline guard (only solar_battery re-captured).

**Open** for the plan/implementer: the exact SysIDE metaclass string for inline constraints
(probe); the precise line for the zero-output guard within the return-building block; final fixture
file contents.

**Risky:** B2 (above) is the only thing that can shrink scope. Everything else is mechanical and
guarded by I2's byte-identical assertion.

---

Next Step: After approval → `/_my_plan` (several fixtures + a probe + doc updates make a short plan
worthwhile over going straight to `/_my_implement`).
