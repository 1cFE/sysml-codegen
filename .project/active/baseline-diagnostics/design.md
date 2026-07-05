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

**Finding 1 — constraints drop from BOTH calc defs and part defs; the spec's part-def stub is the
wrong site for the fix.** The spec names `_extract_part_definition` (`extractor.py:106`,
`constraints = []`) as the drop site, but that method is **called nowhere on the live generation
path** — so a diagnostic added there never fires. `catf_mfe`'s constraints live in two owner
kinds, both reached on the live path:

- **Calc-def-owned** (most of them — e.g. `ThermalCycleEfficiency`, `TorusMinorRadius`): dropped
  silently by `_extract_calculation_definition`, whose member loop `continue`s on anything that is
  not an `AttributeUsage` (`extractor.py:151-153`); `CalculationDefinitionData` has no constraints
  field at all.
- **Part-def-owned** (e.g. `RadiusConsistency` in `part def 'Radial Build Layer'`,
  `radial_build.sysml:55`): part-def *elements* are visited on the live path by
  `_extract_and_filter_computed_attributes` (`pipeline_builder.py:115`, iterating
  `PartDefinition` + `PartUsage`), but only for computed attributes — their `ConstraintUsage`
  members are ignored, and again dropped silently.

So an honest "no silent constraint drops" summary must count constraints across **both owner
kinds** (and part usages), not just one path. The design uses a single dedicated detection pass
(see D2) so the summary count is the true model-wide total. The part-def stub at `extractor.py:106`
stays as-is (off the live path; harmless).

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

- **B1.** `catf_mfe`'s constraint usages are reachable as `ConstraintUsage` members of their owner
  elements (calc defs and part defs) during model traversal (same `owned_members` idiom that yields
  `AttributeUsage`). *If false → the summary WARN never fires against `catf_mfe` and SC-1 has no
  real-fixture test.*
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
- **D2.** Detect dropped constraints in one dedicated pass over the loaded model — a single method
  `SysMLDataExtractor.report_dropped_constraints()` that finds every `ConstraintUsage` (across
  calc-def, part-def, and part-usage owners), logs one INFO per constraint, and emits one summary
  WARN with the model-wide total. Called once from orchestration after load
  (`pipeline_builder.py`, near the calc-def extraction step). *Rejected: detecting inline inside
  `_extract_calculation_definition` only — misses part-def-owned constraints (M1;
  `radial_build.sysml:55`), so the summary would under-count and the drop would stay partly silent.
  Rejected: threading a shared counter across `_extract_calculation_definition` and the
  part-def loop in `pipeline_builder.py:115` — those are different modules; a dedicated pass is one
  collector by construction and keeps the diagnostic off the extraction return path. Rejected:
  scoping the message down to "calc-def constraints" — SC-1's intent is no silent drops, period.*
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
       consumed by 5 sites (see Implementation Notes) → all serialization deterministic
       ⇒ re-capture solar_battery: YAML + computation_graph.json + registry_init.py (C1)

pipeline_builder (after load)
  └─ extractor.report_dropped_constraints()  ── dedicated pass over the model (D2)
        ├─ for each ConstraintUsage (calc-def / part-def / part-usage owners):
        │     logger.info per constraint
        └─ logger.warning(summary) with model-wide total

extractor._extract_calculation_definition
  └─ if not output_attributes: raise ValueError (V-rule) ──► fail-fast (D3)

graph_builder._resolve_expose_pure  (key-not-found branch) ──► reworded WARN (D4)
output_registry_builder  (Phase-3 branch) ──────────────────► reworded WARN (D4)
```

Data flow is otherwise unchanged. The constraint pass reads only `self.model`; it holds no state
and nothing downstream reads its result — it is purely diagnostic.

## Required Invariants

- **I1.** `entry_point_groups` is sorted by `group.name` in every `ComputationGraph`. Testable:
  assert the list equals its name-sorted copy for every baseline.
- **I2 (per-model, not per-file).** All baseline artifacts for the three other models (chain_spike,
  attr_expr_probe, sample_model) and every extraction snapshot are byte-identical after the change.
  **solar_battery is re-captured across three files** — `baseline_yaml/solar_battery.yaml`,
  `baseline_outputs/solar_battery/computation_graph.json`, and
  `baseline_outputs/solar_battery/registry_init.py` — all ordering-only diffs (C1). The success
  criterion "no baseline changes beyond solar_battery" is read **per model**: solar_battery's files
  may change (reviewed, ordering-only); no other model's may. This is the hard "no behavioral
  change" gate.
- **I3.** A calc def with zero output attributes never reaches generation — it raises at
  extraction. Testable on the zero-output fixture.
- **I4.** Generating `catf_mfe` emits exactly **one** constraint summary WARN, and the number of
  per-constraint INFO lines equals the number of `ConstraintUsage` members the test independently
  counts from the loaded model — asserted structurally, never against a hardcoded N. No
  per-constraint WARN.

## Component Overview

- **Sort (D1)** — `resolution/graph_builder.py`, ~1 line before line 364. `param_groups` reassigned
  to `sorted(param_groups, key=lambda g: g.name)`.
- **Constraint diagnostic (D2)** — a new `report_dropped_constraints()` method on
  `SysMLDataExtractor` (`extraction/extractor.py`) that scans the loaded model for every
  `ConstraintUsage`, INFO-logs each by `owner.name` + constraint name, and WARN-summarizes the
  total; invoked once from `orchestration/pipeline_builder.py` after `load_models()`.
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
    `"Constraint '{constraint_name}' on {owner_kind} '{owner_name}' is not executable and was dropped (constraints are not compiled to pipeline modules; see modeling-assumptions.md)."` (`owner_kind` = "calc def" | "part def" | "part usage")
  - **Constraint summary (D2), `logger.warning`:**
    `"Dropped {n} constraint usage(s) across the model; constraint predicates are not executable and do not appear in generated output. See the 'Constraints are not executable' section of modeling-assumptions.md."`
  - **EXPOSE key-not-found (D4), reworded `logger.warning`:**
    `"EXPOSE_PURE %s: derived-attribute name is dropped from generated output — no alias is emitted. Its value was expected on canonical channel '%s', which is not registered (name-form mismatch; part-def shape-A resolution is Item 10/11)."` (`ca.name`, `catalog_key`)
  - **EXPOSE Phase-3 (D4), reworded `logger.warning`:**
    `"Phase 3: EXPOSE_PURE alias '%s' is dropped from generated output — canonical channel '%s' is not in the registry, so no named alias is emitted."` (`scoped_key`, `alias.canonical_name`)
- **Constraint detection mechanism.** Prefer `self.adapter.elements_of_type(self.model,
  "ConstraintUsage")` if it enumerates every constraint usage in the model (owner reachable via the
  node's owner attribute) — one call, honest total. If it does not recurse into calc-def/part-def
  bodies, fall back to scanning `owned_members` of each `CalculationDefinition`, `PartDefinition`,
  and `PartUsage` element for `is_instance(member, "ConstraintUsage")` (the existing member-loop
  idiom). Confirm the exact SysIDE metaclass string and the enumeration behavior with the same
  one-line probe used for SC-7. Either way it is one collector, model-wide.
- **Sort stability.** `group.name` is unique per design file (one group per file), so the sort is
  total and stable. Do not sort module inputs, modules, or exit points — scope creep would churn
  the other baselines (spec review L3-2).
- **`entry_point_groups` consumers (why C1's re-capture set is what it is).** The sorted list feeds
  five sites, and the sort makes all of them deterministic in one place — this is D1's whole point:
  1. pipeline YAML entry points — `generation/pipeline.py:56` (`_build_entry_points`);
  2. **registry `group_names` order** — `generation/registry.py:185` → `registry_init.py`;
  3. Pydantic schema file generation — `generation/entry_point.py:238`;
  4. JSON input file generation — `generation/entry_point.py:293`;
  5. the CLI driver that calls 3 & 4 — `cli/__init__.py:372-383`.
  Consumers 1 and 2 are what change solar_battery's `pipeline.yaml` and `registry_init.py`; the
  list itself changes `computation_graph.json`. Schema/JSON file *contents* are per-group and
  order-independent, but their generation order is now stable too.
- **Baseline re-capture (C1).** Two scripts, both live-license (valid to 2026-08-06, in window;
  never hand-edit, R3): `scripts/capture_baseline_yaml.py` regenerates the four
  `baseline_yaml/*.yaml`; `scripts/capture_pipeline_baselines.py` regenerates
  `baseline_outputs/<model>/{computation_graph.json,registry_init.py}`. Commit **only** the three
  solar_battery diffs; the other three models must show no change across either script — that is
  I2's guard. `test_computation_graph_identical` (`test_factory_purity.py:509`) compares the graph
  dict exactly with no ordering normalization, which is why the graph JSON must be re-captured, not
  just the YAML.

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
| REQ-BASE-05 | solar_battery YAML + graph + registry re-captured via scripts (ordering-only) | `test_baselines.py`, `test_factory_purity.py`, `test_gen_pipeline_yaml.py` | solar_battery_model |
| REQ-BASE-06 | `entry_point_groups` name-sorted in every graph (I1) | `test_graph_assembly.py` | all baselines |
| REQ-EXT-08 | zero-output calc def raises at extraction (I3) | `test_extractor.py` | `zero_output_calc` (new) |
| REQ-EXT-09 | dropped constraints (calc-def + part-def) → 1 summary WARN + structural INFO count (I4) | `test_extractor.py` (caplog) | catf_mfe_model |
| REQ-CA-09 | EXPOSE_PURE name-drop warning reworded | `test_computed_attributes.py` (caplog) | `expose_pure_shape_a` (new) |

- **Full suite green** on the branch after re-capture (top success criterion) — includes
  `test_factory_purity.py::test_computation_graph_identical`, which fails until solar_battery's
  `computation_graph.json` is re-captured.
- **I2 byte-identical guard (per model)**: after both capture scripts run, only the three
  solar_battery files change; the other three models' YAML, `computation_graph.json`,
  `registry_init.py`, and all extraction snapshots are byte-identical. Verify via `git diff --stat`
  on the re-capture commit — it should touch solar_battery paths only.
- **Constraint test (REQ-EXT-09)** asserts structurally: load `catf_mfe`, independently count
  `ConstraintUsage` nodes, then assert exactly one summary WARN and that INFO count equals that
  number — covering both a calc-def-owned and a part-def-owned constraint. No hardcoded N.
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

**Fixed** (do not relitigate): D1 sort site and scope; D2 single dedicated constraint pass covering
calc-def **and** part-def (and part-usage) owners; D3 fail-fast at extraction; D4 two-warning
rewording; D5 sequential REQ numbers; the dead-code deletion; the per-model baseline guard
(solar_battery re-captured across YAML + `computation_graph.json` + `registry_init.py`; no other
model changes).

**Open** for the plan/implementer: the exact SysIDE metaclass string for constraint usages and
whether `elements_of_type` enumerates them model-wide vs. the owned_members fallback (one probe,
shared with SC-7); the precise line for the zero-output guard within the return-building block;
final fixture file contents.

**Risky:** B2 (above) is the only thing that can shrink scope. Everything else is mechanical and
guarded by I2's byte-identical assertion.

---

## Design-Review Resolutions (round 1)

- **C1 (critical) — resolved.** The graph-level sort changes solar_battery's
  `computation_graph.json` and `registry_init.py` (via `entry_point_groups` and the derived
  `group_names` order), and `test_computation_graph_identical` (`test_factory_purity.py:509`)
  compares the graph dict exactly. Re-capture set is now solar_battery's YAML **+ graph JSON +
  registry** via both `capture_baseline_yaml.py` and `capture_pipeline_baselines.py` (all
  ordering-only, reviewed). Success criterion reinterpreted **per model** (I2, Implementation
  Notes, validation matrix).
- **M1 (major) — resolved.** Constraint detection extended to part-def-owned constraints
  (`radial_build.sysml:55`, visited on the live path at `pipeline_builder.py:115`). D2 redesigned as
  a single dedicated model-wide pass with one collector across calc-def, part-def, and part-usage
  owners; detection-only; message not scoped down (Finding 1, D2, B1, Architecture, Component
  Overview, wording).
- **Minor — I4's N.** Test now asserts structurally (independently counted `ConstraintUsage`
  total), not a magic number (I4, validation).
- **Minor — consumer enumeration.** All five `entry_point_groups` consumers listed with file:line
  (Implementation Notes), which also grounds C1's re-capture set.

Next Step: After approval → `/_my_plan` (several fixtures + a probe + doc updates make a short plan
worthwhile over going straight to `/_my_implement`).
