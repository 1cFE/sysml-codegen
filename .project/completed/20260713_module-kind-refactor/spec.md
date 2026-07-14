# Spec: `module_kind` and the Generation-Seam Refactor (Item 6)

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-07-12
**Complexity:** MEDIUM–HIGH (mechanical per-site logic, but ~40 files touched: ~8 src sites, 22 test files, 9 baselines, plus comparison harnesses)
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
- [x] `PipelineModule` carries a single `module_kind` enum with five members (calculation, formula,
  aggregation, constraint, report_aggregator); the two Boolean flags no longer exist anywhere.
- [ ] The four seams S4 named dispatch on `module_kind`. A `PipelineModule` with
  `module_kind == constraint` (or `report_aggregator`) reaching any of them **fails loud** — never
  takes the calc path, never skips — guarded by unit tests in this item, exercised for real in Item 7.
- [x] Every current flag consumer is migrated — `src/` **and** `tests/` (the four seams, the other
  src consumers, 22 test files, and the baseline-comparison harnesses). A repo-wide grep for
  `is_computed_attribute` and `is_aggregation` returns zero hits.
- [ ] The committed `computation_graph.json` baselines are regenerated to carry `module_kind`
  instead of the flags, and round-trip through `ComputationGraph.model_validate_json`
  (`tests/conformance/test_baselines.py:43`).
- [ ] mypy clean, Ruff clean, full suite green.

## Known Requirements

### The enum and the field

- **[INHERITED]** `PipelineModule` gains a real `module_kind` (values: calculation, formula,
  aggregation, constraint, report_aggregator) replacing the accreted Boolean flags. Source: concept
  `PipelineModule` paragraph ("Concrete Lowering", line 98); epic Item 6 scope 1.
- **[HARD]** The three existing kinds map one-to-one from today's flags at the three
  `PipelineModule(...)` construction sites in `graph_builder.py`, so existing behavior is preserved
  exactly:
  - computed-attribute site (`graph_builder.py:1175`, sets `is_computed_attribute=True` at line
    1183) → `formula`
  - aggregation site (`graph_builder.py:1578`, sets `is_aggregation=True` at line 1586) →
    `aggregation`
  - calc-usage site (`graph_builder.py:1783`, sets neither flag) → `calculation`
- **[HARD]** The collapse to one enum is total and lossless. The two-flag space has four cells,
  and the fourth — `is_computed_attribute=True AND is_aggregation=True` — has defined-but-inconsistent
  behavior in today's seams (`modules.py:40-42` gives computed precedence; other seams differ). It is
  safe to drop because **no construction site ever sets both flags**: the three sites above set
  computed-only, aggregation-only, and neither, respectively. The ambiguous cell is unreachable, so
  three enum members cover every constructible module.
- **[INHERITED]** The enum defines `constraint` and `report_aggregator` now, even though nothing
  constructs them until Item 7. The success criterion "a constraint-kind module reaching any seam no
  longer mis-renders as a calc" is only testable if the value exists to construct a test module.
  Source: epic Item 6 success criterion 2.
- **[HARD]** A `PipelineModule` whose `module_kind` is `constraint` or `report_aggregator` reaching
  any of the four calc-shaped seams in this item **fails loud** — it raises an explicit,
  identity-bearing error, never a skip and never a calc render. This is forced by the concept's
  owner-ratified Design Principle 5, "Silence Is Never an Outcome" (concept lines 64-66): a modeled
  limit must never quietly disappear, and a constraint module skipped or mis-rendered as a calc is
  exactly the silent outcome that principle forbids — it is the S4 bug this item exists to kill. The
  seams have no correct emission for these kinds until Item 7 wires it; until then, loud failure is
  the only acceptable behavior. The error's exact form and message are design-open (see Open
  Questions); that it must raise rather than skip or stub is not.

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

### Every other flag consumer — src

- **[HARD]** Migration is not limited to the four seams. Every remaining `src/` reader of the two
  flags moves to `module_kind`:
  - Pipeline-YAML source labeling (`generation/pipeline.py:128-134`).
  - Conformance test generator, which skips formula/aggregation modules
    (`generation/test_gen.py:47`).
  - The three graph-builder construction sites set `module_kind` instead of the flags
    (`graph_builder.py:1175,1578,1783`).

### Test-suite migration — in scope

- **[AGENT]** (orchestrator decision, 2026-07-12) The test suite is **in scope for this item**, not
  follow-on. The point of the item is that the flags are gone; leaving test files reading them would
  be a half-migration and would leave the zero-hit gate (below) red. The migration surface is:
  - **22 test `.py` files** that read `is_computed_attribute` / `is_aggregation` — factory helpers
    that pass the flags as kwargs (`tests/unit/test_aggregation_generation.py:68-81`), assertions on
    module kind (`tests/unit/test_graph_builder_aggregation.py:482`), and the model-field inventory
    test that lists both flag names as expected fields (`tests/conformance/test_data_models.py:584-585`).
  - **The baseline-comparison harnesses**, which read the flag keys back out of the baseline JSON and
    compare (`tests/conformance/test_pipeline_e2e.py:86-90`;
    `tests/conformance/test_graph_assembly.py:563-567`). These must move to `module_kind` in
    **lockstep** with the baseline regeneration below — regenerating the JSON to a `module_kind` key
    without editing these harnesses breaks them, and vice versa. Treat the baseline change and the
    harness change as one move.
  - **9 committed `computation_graph.json` baseline fixtures** (`tests/fixtures/baseline_outputs/*/`),
    regenerated to carry `module_kind` instead of the flag keys.
- **[HARD]** The zero-hit gate is **repo-wide**: after migration, a grep for `is_computed_attribute`
  and `is_aggregation` across `src/` **and** `tests/` returns zero hits.

**Effort note.** This roughly triples the touched-file surface the epic's 7h execute estimate
assumed (~8 src sites → ~8 src + 22 test files + 9 baselines + the harness edits). The logic per site
is mechanical, but the file count is the real cost. Design and plan should size against the full
surface, not the src slice; the epic estimate is understated and should be revised at plan time.

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
  `is_computed_attribute` keys to a `module_kind` key. This baseline change is coupled to the
  comparison-harness edits named under "Test-suite migration" — the two are one move, not an isolated
  fixture bump. It is **not** a byte-identity violation of the generated package (a separate artifact
  set). Verified: the `extraction_snapshot.json` fixtures carry neither flag (`grep` returns zero),
  so this refactor does not touch extraction-snapshot content.

## Non-Goals

- Emitting constraint-kind or report-aggregator modules — Item 7. This item only makes a
  constraint-kind module *not* mis-render as a calc; it does not render one correctly.
- Any behavior change for existing kinds. The byte-identity gate is the whole point.
- Bumping the extraction-snapshot format version. Out of scope here because `module_kind` is a
  graph field, not a snapshot field — this refactor is **decoupled from Item 8's snapshot v3 work**
  (see the Serialization requirement; verified in spec review L1-1). The epic's Item 6 scope 3 phrase
  "coordinated with Item 8's version bump if sequenced together" is satisfied by: they are not
  sequenced together on the data, so no coordination is required.
- Compiling predicate IR, the Kleene runtime, catalog persistence, or the aggregator's exact schema —
  all Item 7.

## Open Questions / Deferred to design

- **The form and message of the fail-loud guard.** *That* a constraint/report-aggregator kind
  reaching a not-yet-wired seam must fail loud is pinned as [HARD] above (skip and stub are off the
  table). Design chooses the mechanism: one central guard vs. a per-seam raise, the exception type,
  and what identity the message carries (module name, kind, seam). Deferred to design.
- **How far to build "structured output schema identity as graph data" now.** Two readings of the
  epic scope: (a) land only the graph field plus the dispatch that reads it, populated to reproduce
  float behavior for existing kinds, leaving the non-float rendering to Item 7; or (b) build the full
  structured-schema rendering path now, unused. Recommendation: (a) — minimal graph data + a
  float-identical read path keeps this a pure refactor and hands Item 7 a clean field to populate.
  Deferred to design.
- **Enum representation choice** — `str`-valued `Enum` vs. `Literal` union vs. plain `Enum`. The
  canonical serialized string values come from the **epic** scope (line 279), which spells
  `report_aggregator` with an underscore; the concept prose (line 98) writes it as two words
  ("report aggregator"), so the underscore form is the one to adopt. Pydantic serialization and the
  `computation_graph.json` round-trip must both stay clean. Mechanism; deferred to design.
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
