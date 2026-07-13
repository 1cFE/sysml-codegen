# Design: `module_kind` and the Generation-Seam Refactor (Item 6)

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-07-12
**Branch:** constraint-exec-epic
**Commit:** 9a4fac4

---

## Overview

Replace the two accreted Boolean flags on `PipelineModule` (`is_computed_attribute`,
`is_aggregation`) with a single `module_kind` enum, and make the four calc-shaped generation
seams dispatch on it. Pure refactor: byte-identical output for the three existing kinds, plus a
loud refusal when a not-yet-wired kind (constraint, report_aggregator) reaches a seam. Clears the
path for Item 7's constraint emission.

## Related Artifacts

- **Spec:** `.project/active/module-kind-refactor/spec.md` (review-revised, orchestrator-accepted)
- **Spec review:** `.project/active/module-kind-refactor/spec-review.md`
- **S4 seam findings:** `.project/active/spike-vertical-slice-constraint-execution/findings.md`
- **Epic:** `.project/backlog/epic_constraint_execution.md` (Item 6, lines 270-297)
- **Concept:** `.project/concepts/constraint-execution-and-design-space-studies-claude.md`
  (`PipelineModule` paragraph line 98; Appendix B S4 seam findings)
- **Required Reading:** concept `PipelineModule` + Appendix B; S4 findings; memory
  *byte-identity captured_at churn* (gate mechanics).

## Research Findings

The whole surface is confirmed and concrete. Two Boolean flags live at
`resolution/models.py:181-182`, default `False`. Their construction and every read:

- **Three construction sites** in `graph_builder.py`, mutually exclusive, never both set:
  - `:1175` (formula) sets `is_computed_attribute=True` at `:1183`.
  - `:1578` (aggregation) sets `is_aggregation=True` at `:1586`.
  - `:1783` (calc-usage) sets neither.
- **Four calc-shaped seams**, each an `if computed … elif agg … else (calc)` chain:
  1. `cli/__init__.py:150-222` — `_get_python_path`, `_raw_source_name`, `_check_duplicate_output_paths`.
  2. `generation/registry.py:220-281` — split-by-flag into three lists, class naming + dedup per kind.
  3. `generation/modules.py:32-45` — `_get_module_sysml_qn` (module wrapper QN derivation).
  4. `generation/stencils.py:34-47` — its own `_get_module_sysml_qn`; auto-impl counting `:200-216`.
- **Two more src readers:** pipeline-YAML source labeling `pipeline.py:127-134`; conformance
  test-gen skip `test_gen.py:47`.
- **str-Enum serialization verified:** in the committed baselines, `Compilability` renders as
  `"compilability": "fully_compilable"` and `EntryPointType` as `"entry_type": "design_attribute"`
  — a `str`-valued `Enum` serializes as its `.value` and round-trips through
  `model_validate_json` with no config. The flags render as `"is_computed_attribute": false`,
  `"is_aggregation": false`. This settles the enum-representation and serialization questions.
- **Pydantic gotcha:** `PipelineModule` has no `model_config`, so Pydantic v2's default
  `extra='ignore'` applies. After the flags are deleted, a test still passing
  `is_computed_attribute=…` as a kwarg is **silently dropped**, not an error. Construction won't
  loud-fail on a missed site — the repo-wide grep gate is the real completeness backstop.
- **The "float-specialized wrapper":** `modules.py:102-154` builds every output channel as a
  primitive `Float` (`teax_module.py.jinja2`); there is no per-output type field. This is the
  assumption Item 7's structured (`ConstraintEvaluation`) output must break.
- **Migration surface:** grep confirms the spec's count — 8 src files, 22 test `.py` files, 9
  committed `computation_graph.json` baselines.

## Core Concept

Today the answer to "what kind of module is this?" is *computed* at every seam by reading two
Booleans and inferring — with "calculation" as the silent `else`. Three real kinds are encoded in
a two-flag space, and one of that space's four cells is meaningless. The fix is to make the kind an
**explicit, named property of the module**, set once at construction, and turn every seam's
inference into a lookup.

`PipelineModule` gains `module_kind: ModuleKind`, a `str`-valued enum with five members:
`calculation`, `formula`, `aggregation`, `constraint`, `report_aggregator`. The three
construction sites set it directly (formula / aggregation / calculation), one-to-one with today's
flags. Each of the four seams — plus the two other readers — rewrites its flag chain as a
dispatch on `module_kind` whose calculation/formula/aggregation arms reproduce today's branches
**verbatim**, so the generated package is byte-identical. The two new kinds have no correct
rendering until Item 7; reaching a seam with one **raises** rather than falling into the calc
`else`. That refusal is the whole reason the refactor exists — it converts the S4 silent
mis-render into a loud, identity-bearing failure (concept Design Principle 5, "Silence Is Never an
Outcome").

The design is deliberately mechanical. Every seam's before/after shape is spelled out below so a
sonnet implement session executes it without judgment calls. The only new behavior is the raise;
everything else is a rename of "read two flags" to "read one enum."

**Composes with existing pieces.** The enum sits beside the codebase's eight existing
`str`-Enums (`EntryPointType`, `Compilability`, …) — same pattern, same serialization. The
fail-loud raise reuses `CodeGenerationError` (already the generation layer's fail-fast type, e.g.
`cli/__init__.py:203`). No new mechanism is introduced.

## Key Bets

- **B1.** The three construction sites are mutually exclusive and cover every constructible
  module — no site sets both flags, none sets neither-and-means-a-fourth-thing. *If false → the
  flag→kind map is lossy, and some existing module silently changes kind, breaking byte-identity.*
  (Verified at `:1183`/`:1586`/`:1783`; spec [HARD] lines 65-70.)
- **B2.** Every per-kind branch at the four seams is reproducible by an enum arm that returns the
  identical value today's flag branch returns — the flags carry *only* kind, no hidden state.
  *If false → a seam's output shifts for an existing kind and byte-identity fails.*
- **B3.** No generated artifact and no non-timestamp field of the serialized graph depends on the
  literal JSON key names `is_computed_attribute` / `is_aggregation` beyond the baseline fixtures
  and their comparison harnesses (which move in lockstep). *If false → some consumer breaks on the
  key rename outside the migrated set.* (Grep-bounded: the only JSON hits are the 9 baselines.)

## Key Decisions

- **D1. `str`-valued `Enum` named `ModuleKind`.** Values: `"calculation"`, `"formula"`,
  `"aggregation"`, `"constraint"`, `"report_aggregator"` (underscore form from epic scope line
  279, per spec L1-4). *Rejected: `Literal` union* (no namespace for the guard/dispatch to
  reference, inconsistent with the eight existing enums). *Rejected: plain `Enum`* (serializes by
  name or needs `use_enum_values`, either of which changes the JSON string and breaks the clean
  round-trip verified above).
- **D2. Field placement replaces the flags in declaration order.** `module_kind` occupies the
  lines the two flags held (`models.py:181-182`), so the serialized-JSON diff is a localized
  two-keys-out / one-key-in replace at the same position, not a field-order reshuffle across every
  baseline. *Rejected: append at end of model* (spreads the baseline diff and reads as unrelated
  churn to the implement-stage reviewer). No default — the field is required, forcing every
  construction site to state the kind (a missing site becomes a Pydantic error, not a silent calc).
- **D3. Per-seam dispatch, shared error constructor.** Each seam maps `module_kind` to its own
  existing branch locally (the QN shapes genuinely differ per seam); the refusal calls one shared
  `unrenderable_module_kind_error(module, seam_name)` that returns a `CodeGenerationError` with
  uniform identity. *Rejected: one central dispatcher* (the seams don't share a return shape —
  forcing them through one function invents an abstraction that fits none). *Rejected: per-seam
  bespoke raise messages* (message drift; identity content diverges seam to seam).
- **D4. Fail-loud via `CodeGenerationError`, message carries name + kind + seam.** *Rejected:
  `NotImplementedError`* (reads as "not built" rather than "modeled limit refused"; the generation
  layer already standardizes on `CodeGenerationError` for fail-fast). *Rejected: a field validator
  on `module_kind`* (the value is legal on the graph — Item 7 constructs it; it is only
  unrenderable at these four seams, so the guard belongs at the seam, not on the type).
- **D5. Structured-output-schema carrier: add `output_schema_type: str | None = None` now,
  read by nothing in Item 6.** Satisfies the spec [INHERITED] requirement (schema identity as
  graph data) at its minimal, provably float-identical reading: the field defaults to `None`
  ("the float wrapper"), no construction site sets it, and the module template is untouched — so
  every existing kind renders byte-identically. Item 7 populates it at its constraint construction
  site and adds the template dispatch that reads it. *Rejected: build the structured render path
  now, unused* (dead code, and it can't be proven correct with no constructor exercising it — spec
  Open-Question reading (b), explicitly not recommended). *Rejected: omit the field entirely and
  defer to Item 7* (would re-open the PipelineModule schema and re-churn every baseline a second
  time in Item 7; front-loading it here folds that change into this item's already-planned baseline
  regen). *Cost recorded:* this adds `"output_schema_type": null` to every module in every
  baseline — see the baseline-diff spec below so the implement-stage diff review stays mechanical.

## Architecture

**Data model (`resolution/models.py`).** New `ModuleKind(str, Enum)` above `PipelineModule`.
`PipelineModule` loses both flags, gains `module_kind: ModuleKind` (required, at the same
position) and `output_schema_type: str | None = None` (after it). Nothing else on the model moves.

**Construction (`graph_builder.py`).** The three sites set `module_kind=` in place of the flag
they set today:

| site | today | after |
|---|---|---|
| `:1175` formula | `is_computed_attribute=True` | `module_kind=ModuleKind.FORMULA` |
| `:1578` aggregation | `is_aggregation=True` | `module_kind=ModuleKind.AGGREGATION` |
| `:1783` calc-usage | *(neither)* | `module_kind=ModuleKind.CALCULATION` |

**Dispatch (the four seams + two readers).** Each flag chain becomes a `module_kind` dispatch.
The sites are **not all the same shape** — three are genuine `if/elif/else` three-arm chains, one
is a two-arm helper, and three are a ternary / guard-`continue` / `or`-guard. **The per-site
before/after below is the authority; do not apply a blanket rule.** For the genuine three-arm
chains only, the rekey is mechanical: `is_computed_attribute` branch → `FORMULA` arm;
`is_aggregation` branch → `AGGREGATION` arm; `else` → `CALCULATION` arm (body unchanged);
`CONSTRAINT | REPORT_AGGREGATOR` raises via the shared constructor. The two-arm and
non-`if/elif/else` sites each get their exact shape spelled out — a two-arm helper that gives
`AGGREGATION` its own arm, or a ternary that tries to raise inline, would break existing kinds.

- **Seam 1a — `_get_python_path` (`cli/__init__.py:150-161`), three-arm.** A real
  computed/agg/else chain. The three arms keep their exact QN-derivation bodies, rekeyed:
  `FORMULA` → the `::calc_def_name` form, `AGGREGATION` → the `name.replace("__","::")` form,
  `CALCULATION` → `calc_def_qualified_name`. `CONSTRAINT`/`REPORT_AGGREGATOR` raise.
- **Seam 1b — `_raw_source_name` (`cli/__init__.py:164-174`), two-arm — NOT three.** Today:
  `if is_computed_attribute: return "{qn}::{name}"` then a **shared** fall-through
  `return calc_def_qualified_name or name` that serves **both aggregation and calculation** (there
  is no `is_aggregation` branch here). After: `FORMULA` arm → `{qn}::{name}`; **`AGGREGATION` joins
  `CALCULATION`** in the `calc_def_qualified_name or name` arm; only
  `CONSTRAINT`/`REPORT_AGGREGATOR` raise. Do **not** give `AGGREGATION` its own arm and do **not**
  route it to the raise — this helper runs for *every* module in `_check_duplicate_output_paths`
  (`cli/__init__.py:200,214`), so either mistake breaks every aggregation module.
- **`_check_duplicate_output_paths` (`cli/__init__.py:177-222`)** needs no logic change — it calls
  the two helpers above, which now raise for unrenderable kinds (so a constraint module in the
  module list fails the pre-clear check loudly, which is correct).
- **Seam 2 — `generate_registry` (`registry.py:220-281`).** Today it partitions
  `graph.modules` into three lists by flag (`:221-226`). After: partition by `module_kind ==
  CALCULATION / FORMULA / AGGREGATION`; each list's naming+dedup body is unchanged. Add a guard
  pass: any module whose kind is `CONSTRAINT`/`REPORT_AGGREGATOR` raises before the split (none
  reach here until Item 7).
- **Seam 3 — `_get_module_sysml_qn` (`modules.py:32-45`).** Same three-arm rekey; two new kinds
  raise. The float-wrapper body (`modules.py:102-154`) is untouched (D5).
- **Seam 4 — `_get_module_sysml_qn` (`stencils.py:34-47`) + auto-impl counting
  (`stencils.py:200-216`).** QN helper rekeyed identically. The counting loop's
  `if is_computed_attribute … if is_aggregation …` becomes `if module_kind == FORMULA … elif ==
  AGGREGATION …`; two new kinds raise (the loop is where a constraint module would otherwise be
  silently skipped).
- **Reader — pipeline source label (`pipeline.py:127-134`), a ternary — site-specific.** A ternary
  cannot raise inline, so this is not the three-arm rekey. Keep the two existing labels
  byte-identical (`AGGREGATION` → "source: aggregation …", `FORMULA` → "source: computed_attribute
  …", `CALCULATION` → `module.module_type`), rekeyed to `module_kind`, and hoist an explicit guard
  above the ternary that raises for `CONSTRAINT`/`REPORT_AGGREGATOR` (do not try to add a fourth
  ternary arm).
- **Reader — test-gen skip (`test_gen.py:47`), an `or`-guard — site-specific.** `if
  is_computed_attribute or is_aggregation: continue` → `if module_kind in (FORMULA, AGGREGATION):
  continue`, with a raise for `CONSTRAINT`/`REPORT_AGGREGATOR` (they must not silently fall through
  into the calc-conformance emitter). Seam 4's auto-impl counter (`stencils.py:208-220`) is the
  same guard-`continue` shape, handled in its own bullet above.

**Test suite + baselines (lockstep).** Factory kwargs `is_computed_attribute=`/`is_aggregation=`
→ `module_kind=`; assertions `assert m.is_aggregation is True` → `assert m.module_kind ==
ModuleKind.AGGREGATION`; `test_data_models.py:578-591` asserts the field list **in order**, so the
swap must place `module_kind` + `output_schema_type` **at the flags' position** (after
`compiled_expression`, before `auto_impl_context`) — do not append them at the end of the
inventory. The two comparison harnesses
(`test_pipeline_e2e.py:86-90`, `test_graph_assembly.py:563-567`) read `bm["is_computed_attribute"]`
/`bm["is_aggregation"]` out of the baseline JSON — these move to `bm["module_kind"]` **in the same
change** as the baseline regeneration.

## Required Invariants

- **INV-1 (byte-identity).** For every model under `tests/`, the generated package (modules,
  stencils, schemas, pipeline YAML, registry `__init__.py`, JSON templates) is byte-identical
  before and after, timestamps excepted. The core gate.
- **INV-2 (total lossless map).** Every constructed `PipelineModule` has exactly one
  `module_kind`, and it equals the kind its flags encoded today. No module changes kind.
- **INV-3 (no silent fall-through).** No seam or reader routes a `CONSTRAINT` /
  `REPORT_AGGREGATOR` module to a calc path or skips it — each **seam entry point** raises. The
  registry seam is the one that fails *open* (partition-by-equality omits an unmatched kind), so it
  needs an explicit guard-pass *and* a seam-entry test; a helper-level test cannot protect it. See
  Validation Approach. (Locked here; exercised for real in Item 7.)
- **INV-4 (zero-hit gate).** After migration, `grep -rn 'is_computed_attribute\|is_aggregation'`
  over `src/` and `tests/` returns zero hits.
- **INV-5 (clean serialization round-trip).** Regenerated baselines carry `module_kind` (+
  `output_schema_type`) and round-trip through `ComputationGraph.model_validate_json`
  (`test_baselines.py:43`).

## Baseline-diff spec (the intentional, reviewable diff)

`tests/fixtures/baseline_outputs/` has **10** directories, but only **9** carry the flags:
`sample_model/computation_graph.json` has `"modules": []` (zero modules, no flag keys) and
regenerates byte-identically. Expect the diff to touch 9 of 10 baseline JSONs — `sample_model`
unchanged is correct, not a missed file. Per module object in each of the 9 flag-carrying
`computation_graph.json` files:

- **Removed:** `"is_computed_attribute": <bool>,` and `"is_aggregation": <bool>,`.
- **Added at the same position:** `"module_kind": "<value>",` where value is `"formula"` if the
  module was computed, `"aggregation"` if aggregation, else `"calculation"`.
- **Added (after module_kind's block, from D5):** `"output_schema_type": null`.

No other key changes. The diff is a uniform two-out / two-in replace on every module; anything
else in a regenerated baseline is a bug, not an intended change.

## Component Overview

- **`ModuleKind`** (`resolution/models.py`, new) — the five-member `str`-Enum. Single source of
  truth for module kind.
- **`unrenderable_module_kind_error(module, seam_name) -> CodeGenerationError`** (new, in
  `generation/`) — builds the uniform fail-loud exception carrying module name, kind value, and
  seam name. Called from every seam's unrenderable arm. Note: `CodeGenerationError` is **defined in
  `orchestration/pipeline_context.py:48`** and re-exported via `generation/__init__.py`; the helper
  *imports* it (don't hunt for the class definition under `generation/`).
- **The six rewritten dispatch sites** (four seams + two readers) — each a local `module_kind`
  branch replacing a flag chain, bodies unchanged for existing kinds.
- **`output_schema_type` field** — inert carrier for Item 7 (D5).

## Non-Goals

- Emitting or correctly rendering constraint / report-aggregator modules — Item 7. This item only
  makes them *not* mis-render, by refusing.
- Any behavior change for existing kinds (the byte-identity gate).
- Building the structured-output render path (D5 rejected reading (b)).
- Bumping the extraction-snapshot format version — `module_kind` is a graph field, not a snapshot
  field; decoupled from Item 8 (spec Serialization; verified in spec review L1-1).

## Implementation Notes

- **Pydantic `extra='ignore'` (gotcha).** Removing the flags does **not** make stale test kwargs
  raise — they're silently dropped. Do not rely on construction errors to find missed test sites;
  the INV-4 grep is the completeness check. Run it before declaring the migration done.
- **Migration order (never a mixed state a test run can't interpret):** (1) model — add enum +
  field, remove flags; (2) three construction sites; (3) six dispatch sites + the shared error
  helper; (4) test files + baselines + comparison harnesses in one lockstep move; then run the
  gates. Between (1) and (4) the tree does not pass — that's expected; the item is green only at
  the end. Do not interleave baseline regen with harness edits (spec: one move).
- **Shared error message form** (identity per D4), e.g.:
  `f"Module {module.name!r} (module_kind={module.module_kind.value!r}) reached the {seam_name} "
  f"seam, which has no rendering for this kind yet (wired in Item 7). Refusing rather than "
  f"mis-rendering it as a calculation."`
- **Do not add a default to `module_kind`** — required field, so a forgotten construction site is
  a loud Pydantic error (D2).

## Potential Risks

- **A missed dispatch site renders wrong silently.** Mitigation: the INV-4 grep is exhaustive over
  src+tests; the byte-identity gate catches any behavior shift for existing kinds; the six sites
  are enumerated above with file:line.
- **Baseline diff carries an unintended change.** Mitigation: the baseline-diff spec above is
  exact; the implement-stage review rejects any baseline hunk that isn't the specified two-out /
  two-in-plus-null replace.
- **`output_schema_type` drifts from "inert."** Mitigation: no Item-6 code reads it; a grep for
  `output_schema_type` in `src/` should hit only the field declaration until Item 7.

## Integration Strategy

Drop-in replacement for the flags. Nothing downstream of generation changes shape; the snapshot
rebuild path (`snapshot/graph_rebuild.py:158`) reconstructs the graph via
`build_computation_graph`, so `module_kind` is re-derived at rebuild, never read from a serialized
snapshot field (spec review L1-1). Item 7 extends `ModuleKind`'s two spare members and
`output_schema_type` with zero PipelineModule schema change.

## Validation Approach

- **Primary gate (INV-1):** regenerate each fixture's package, timestamp-only diff, revert (the
  *byte-identity captured_at churn* protocol). Which harness runs it is a plan detail; the existing
  conformance baseline suite (`test_pipeline_e2e`, `test_graph_assembly`, `test_baselines`) already
  regenerates + compares and is the recommended vehicle.
- **INV-3 unit tests (new) — must call the seam ENTRY POINT, not the inner helper.** Construct a
  `ComputationGraph` containing a `PipelineModule(module_kind=CONSTRAINT, …)` and assert that each
  **module-iterating seam function** raises `CodeGenerationError` with the kind and seam in the
  message: `generate_registry`, `_check_duplicate_output_paths`, `_generate_modules`,
  `_generate_stencils`, the pipeline-YAML builder, and the test-gen builder. **Do not test the
  inner QN helpers** (`_get_module_sysml_qn`, `_get_python_path`): they would pass even if the seam
  that drives them silently filters the constraint module out.
  *Why the entry point specifically:* the registry seam **fails open**. It partitions
  `graph.modules` by `module_kind ==` equality (`registry.py:221-226`), so a kind matching no list
  is simply *omitted* — dropped with no raise and no diff, the exact silent outcome this item
  exists to kill. Its guard-pass (raise for `CONSTRAINT`/`REPORT_AGGREGATOR` before the split) is
  the only thing preventing that, and a guard can be forgotten or later regressed. Only a
  seam-entry test — `generate_registry(graph_with_constraint)` raises — catches a dropped guard; a
  helper-level test cannot. This is the test that makes the fail-loud contract real.
- **INV-4:** the repo-wide grep, run as the final gate.
- **INV-5:** the regenerated baselines round-trip through `model_validate_json` (existing
  `test_baselines.py`).
- **Full suite green, mypy clean, Ruff clean** (spec Success Criteria).

## Next-Stage Handoff

- **Fixed:** the enum members and values (D1); required-field placement replacing the flags (D2);
  per-seam dispatch + shared error constructor (D3/D4); `output_schema_type` inert-and-defaulted
  (D5); the six dispatch sites and three construction sites (file:line above); the baseline-diff
  spec; migration order.
- **Open (plan-stage):** which harness command runs the byte-identity gate; exact test-file edit
  list (22 files — mechanical, enumerable by the INV-4 grep); the effort estimate (spec flags the
  epic's 7h as understated ~3× by the test surface — reprice at plan).
- **De-risk first:** run the INV-1 byte-identity gate on one fixture immediately after the six
  dispatch rewrites land, before touching test files — it proves B2/B3 (the flags carried only
  kind) on real output before the large test-migration edit commits.

---
Next Step: After approval → `/_my_plan`.

ARTIFACT: .project/active/module-kind-refactor/design.md
