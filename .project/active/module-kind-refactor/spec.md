# Spec: `module_kind` and the Generation-Seam Refactor (Item 6)

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-07-12
**Complexity:** MEDIUM
**Branch:** constraint-exec-epic

---

## Problem

Generation today asks "what kind of module is this?" by reading two accreted Boolean flags
on `PipelineModule` — `is_computed_attribute` and `is_aggregation` (`resolution/models.py:181-182`).
Every generation seam that behaves differently per kind re-derives the answer from those flags,
usually as an `if is_computed_attribute … elif is_aggregation … else (calc)` chain. Three module
kinds are encoded implicitly in a two-flag space, and the "calculation" kind is the silent `else`.

The constraint-execution epic needs a fourth and fifth kind (constraint, report aggregator). The
S4 spike proved the concrete cost of the current shape: four calc-shaped generation seams assume a
module is a calculation and had to be bypassed by test-only emitters to render a constraint module
at all (concept Appendix B, S4 seam findings). A constraint module reaching any of these seams
mis-renders as a calc — wrong Python path, wrong class name, a calc wrapper and stencil it should
never get. Adding a third Boolean flag would deepen the same tangle.

This item replaces the flags with a real `module_kind` enum and makes the four seams dispatch on it,
byte-identically for the three existing kinds. It is a **pure refactor**: it clears the path for
Item 7 (constraint-kind emission) without mixing refactor risk into new-emission risk. Byte-identity
for existing kinds is the entire acceptance gate.

## Success Criteria

- [ ] The entire existing fixture corpus regenerates **byte-identically** (timestamps excepted) with
  the Boolean flags gone. "Fixture corpus" here is the generated package artifacts — modules,
  stencils, schemas, pipeline YAML, registry `__init__.py`, JSON templates — for every model under
  `tests/`. This is the core gate.
- [ ] `PipelineModule` carries a single `module_kind` enum with five members (calculation, formula,
  aggregation, constraint, report_aggregator); the two Boolean flags no longer exist anywhere.
- [ ] The four seams S4 named dispatch on `module_kind`. A `PipelineModule` with
  `module_kind == constraint` (or `report_aggregator`) reaching any of them no longer takes the calc
  path — guarded by unit tests in this item, exercised for real in Item 7.
- [ ] Every current flag consumer (not only the four seams) is migrated; no reader of
  `is_computed_attribute` or `is_aggregation` remains.
- [ ] The committed `computation_graph.json` baselines are regenerated to carry `module_kind`
  instead of the flags, and round-trip through `ComputationGraph.model_validate_json`
  (`tests/conformance/test_baselines.py:43`).
- [ ] mypy clean, Ruff clean, full suite green.

## Known Requirements

### The enum and the field

- **[INHERITED]** `PipelineModule` gains a real `module_kind` (values: calculation, formula,
  aggregation, constraint, report_aggregator) replacing the accreted Boolean flags. Source: concept
  `PipelineModule` paragraph ("Concrete Lowering", line 98); epic Item 6 scope 1.
- **[HARD]** The three existing kinds map one-to-one from today's flags at the three construction
  sites, so existing behavior is preserved exactly:
  - `is_computed_attribute=True` → `formula` (`graph_builder.py:1183`)
  - `is_aggregation=True` → `aggregation` (`graph_builder.py:1586`)
  - neither flag → `calculation` (`graph_builder.py:1783`)
- **[INHERITED]** The enum defines `constraint` and `report_aggregator` now, even though nothing
  constructs them until Item 7. The success criterion "a constraint-kind module reaching any seam no
  longer mis-renders as a calc" is only testable if the value exists to construct a test module.
  Source: epic Item 6 success criterion 2.

### The four seams

- **[HARD]** Each of these four seams currently branches on the flags and must instead dispatch on
  `module_kind`, preserving byte-identical output for calculation/formula/aggregation:
  1. **Python path + duplicate-path check** — `_get_python_path` and `_raw_source_name` /
     `_check_duplicate_output_paths` (`cli/__init__.py:150-222`). Both assume the calc-def-QN shape
     for the `else` branch.
  2. **Registry class naming and dedup** — `generate_registry` splits modules by flag, names classes
     and deduplicates per kind (`generation/registry.py:220-269+`).
  3. **Module wrapper rendering** — `_generate_modules` via `_get_module_sysml_qn`
     (`generation/modules.py:32-45`) and its float-specialized template.
  4. **Stencil rendering** — `_generate_stencils` via its own `_get_module_sysml_qn`
     (`generation/stencils.py:34-47`) and the auto-impl counting (`stencils.py:200-216`).

### Every other flag consumer

- **[HARD]** Migration is not limited to the four seams. Every remaining reader of the two flags
  moves to `module_kind`:
  - Pipeline-YAML source labeling (`generation/pipeline.py:128-134`).
  - Conformance test generator, which skips formula/aggregation modules
    (`generation/test_gen.py:47`).
  - The three graph-builder construction sites set `module_kind` instead of the flags
    (`graph_builder.py:1175,1578,1783`).
  A repo-wide grep for `is_computed_attribute` and `is_aggregation` must return zero hits at the end.

### Structured output schema identity

- **[INHERITED]** Structured output schema identity becomes graph data, retiring the
  float-specialized wrapper assumption for structured modules. Source: concept line 98; epic Item 6
  scope 1. Bounded by byte-identity: for the three existing (float) kinds the rendered output must be
  identical, so whatever graph field or dispatch is introduced must reproduce today's float wrapper
  exactly for them. The field exists so Item 7's constraint / report-aggregator modules can declare a
  non-float structured output schema without a new seam; it is *exercised for real* in Item 7, only
  *introduced and proven float-identical* here. (See Open Questions on how far to build this now.)

### Serialization

- **[HARD]** `module_kind` is a `ComputationGraph` / `PipelineModule` field, not an extraction-snapshot
  field. It must serialize and deserialize on the graph — the committed `computation_graph.json`
  baselines are `ComputationGraph.model_validate_json` fixtures
  (`tests/conformance/test_baselines.py:43-48`) and will change from `is_aggregation`/
  `is_computed_attribute` keys to a `module_kind` key. Regenerating those baselines is an intentional,
  reviewable fixture update — it is **not** a byte-identity violation of the generated package (a
  separate artifact set). Verified: the `extraction_snapshot.json` fixtures carry neither flag
  (`grep` returns zero), so this refactor does not touch extraction-snapshot content.

## Non-Goals

- Emitting constraint-kind or report-aggregator modules — Item 7. This item only makes a
  constraint-kind module *not* mis-render as a calc; it does not render one correctly.
- Any behavior change for existing kinds. The byte-identity gate is the whole point.
- Bumping the extraction-snapshot format version. Out of scope here because `module_kind` is a
  graph field, not a snapshot field — this refactor is **decoupled from Item 8's snapshot v3 work**
  (see Open Questions for the surfaced finding). The epic's Item 6 scope 3 phrase "coordinated with
  Item 8's version bump if sequenced together" is satisfied by: they are not sequenced together on
  the data, so no coordination is required.
- Compiling predicate IR, the Kleene runtime, catalog persistence, or the aggregator's exact schema —
  all Item 7.

## Open Questions / Deferred to design

- **What a constraint/report-aggregator kind does at each seam in *this* item.** Item 7 wires real
  emission; here the requirement is only "no calc mis-render." Each seam could, for an
  Item-7-only kind, raise a clear `NotImplementedError`-style guard, skip the module, or route to a
  stub. Recommendation: an explicit guard that fails loudly (silence has bitten this project
  repeatedly — concept Design Principle 5), so an Item-7 kind reaching a not-yet-wired seam is a
  named error, not a silent calc render. Deferred to design to choose the exact form and message.
- **How far to build "structured output schema identity as graph data" now.** Two readings of the
  epic scope: (a) land only the graph field plus the dispatch that reads it, populated to reproduce
  float behavior for existing kinds, leaving the non-float rendering to Item 7; or (b) build the full
  structured-schema rendering path now, unused. Recommendation: (a) — minimal graph data + a
  float-identical read path keeps this a pure refactor and hands Item 7 a clean field to populate.
  Deferred to design.
- **Enum representation choice** — `str`-valued `Enum` vs. `Literal` union vs. plain `Enum` — and the
  exact serialized string values (the concept spells `report_aggregator`). Pydantic serialization and
  the `computation_graph.json` round-trip must both stay clean. Mechanism; deferred to design.
- **Byte-identity verification mechanics for the run.** The gate is a per-fixture regenerate +
  timestamp-only-diff check + revert (memory: byte-identity captured_at churn; brief required-reading
  3). Which harness runs it (existing conformance baseline tests vs. a dedicated regen script) is a
  plan-stage detail.

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_constraint_execution.md` (Item 6, lines 270-297)
- **Concept:** `.project/concepts/constraint-execution-and-design-space-studies-claude.md`
  (`PipelineModule` paragraph, line 98; Appendix B S4 seam findings, line 297)
- **Required Reading:**
  - Concept `PipelineModule` paragraph + Appendix B S4 seam findings.
  - `.project/active/spike-vertical-slice-constraint-execution/findings.md` — the four calc-shaped
    seams the test-only emitters bypassed ("Seam findings for spec/design").
  - Memory: byte-identity captured_at churn (gate mechanics).
- **Design:** `.project/active/module-kind-refactor/design.md` (to be created)

---

**Next Steps:** After approval, proceed to `/_my_design`.
