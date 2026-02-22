# Update Plan: Pipeline Explainer HTML

**Activity:** Apply the 17 deltas from `update-list.md` to the actual HTML file (`.project/diagrams/new_pipeline_explainer.html`, 5189 lines).

**Input:** `update-list.md` (17 updates across 3 priority tiers), plus the now-updated `design.md` as the authoritative spec.

**Branch:** `cost-pattern-refactor` (current)

**Key decision (from design.md Phase 0):** Show `_resolve_aggregation_input_channel()` as the actual running mechanism, not `resolve_input()`. Add footnote acknowledging `resolve_input()` as tested-but-unwired.

---

## Phase 1: MODEL_DATA Updates (JS)

**Goal:** Update the `MODEL_DATA` object in `<script>` to reflect all new fields. This is the data layer — everything downstream renders from it.

### Task 1.1: Add metadata fields to `modules[]` entries

Each module object in `MODEL_DATA.modules` currently has: `id`, `shortName`, `family`, `fullEQN`, `moduleType`, `cluster`, `tier`, `inputs`, `outputs`. Add:

- `calcDefName` (string) — source CalcDef name
- `docComment` (string|null) — documentation string
- `sourceFile` (string|null) — path to .sysml file
- `sourceLine` (number|null) — line number in source
- `compilability` (string) — `"FULLY_COMPILABLE"` | `"PARTIALLY_COMPILABLE"` | `"MANUAL_REQUIRED"`

Also add to each input entry: `description` (string|null), `defaultValue` (number|string|null).
Also add to each output entry: `description` (string|null), `unit` (string|null).

**Scope:** Only populate the traced module (PVModuleCostCalc) and a few representative modules with real values. Others get null placeholders.

### Task 1.2: Add `pipelineTrace.step65_compile` object

Add new step data after `step6_sort` (or equivalent). Structure from update-list.md §7c:

```js
step65_compile: {
  tracedModule: {
    calcDef: "PVModuleCostCalc",
    verdict: "FULLY_COMPILABLE",
    compiledExpression: "wattage * cost_per_watt * (1 + fab_factor) * (1 + install_factor)",
    outputExpressions: [
      { name: "material_cost", expression: "wattage * cost_per_watt" },
      { name: "total_cost", expression: "material_cost * (1 + fab_factor) * (1 + install_factor)" }
    ]
  },
  summary: {
    fullyCompilable: 12,
    partiallyCompilable: 2,
    manualRequired: 0,
    unknown: 21
  }
}
```

### Task 1.3: Expand `pipelineTrace.step5_module` with new fields

Add to the traced module's Step 5 data: `calc_def_name`, `calc_def_qualified_name`, `doc_comment`, `source_file`, `source_line`, `auto_impl_context`. Add `description`/`default_value` to inputs, `description`/`unit` to outputs.

### Task 1.4: Update dual resolution example data

If `MODEL_DATA` contains resolution example data referencing `resolve_input()` or named strategies (A, C, D), update to reference `_resolve_aggregation_input_channel()` and chain-trace steps instead.

**Success criteria:**
- [x] `MODEL_DATA.modules[0]` has `calcDefName`, `compilability` fields
- [x] `pipelineTrace.step65_compile` exists with traced module + summary
- [x] `pipelineTrace.step5_module` has expanded metadata fields
- [x] No JS references to `resolve_input()` as the running mechanism

### Phase 1 Completion
**Completed:** 2026-02-22
**Changes Made:**
- Added `calcDefName`, `docComment`, `sourceFile`, `sourceLine`, `compilability` to 5 representative modules (sa_pv_cost, p_net_kw, sa_cap_cost, ann_fin, lcoe)
- Added `description`/`defaultValue` to inputs and `description`/`unit` to outputs on same 5 modules
- Added `step65_compile` object with traced module compilation data (5 output expressions) and summary counts
- Expanded `step5_module` with `calc_def_name`, `calc_def_qualified_name`, `doc_comment`, `source_file`, `source_line`, `auto_impl_context` (with execution_steps and output_expressions)
- Added `description`/`default_value` to step5_module inputs and `description`/`unit` to outputs
- Replaced `resolveInputPath` with `aggChainPath` in both resolution examples, using chain-trace steps instead of named strategies
- Updated `DualResolutionDemo.renderPanels()` to read `aggChainPath` and render chain-trace steps
- Updated Mechanism 3 panel title/description to reference `_resolve_aggregation_input_channel()`
- Updated "Why they can't merge" text for Aggregation mechanism
- Updated AGG_STRATEGIES callout to describe chain resolution order

**Deviations from Plan:**
- Added metadata to 5 modules (not all 36) — renderer handles undefined gracefully, others show no metadata in detail panels
- Two `resolve_input()` references remain in Step 5.5 renderer HTML text (lines 3927, 4004) — deferred to Phase 3/5 as these are renderer text, not MODEL_DATA

---

## Phase 2: HTML Structure — Add Step 6.5

**Goal:** Add the Step 6.5 section to the HTML body and sidebar nav.

### Task 2.1: Add Step 6.5 to sidebar navigation

Insert after the Step 6 nav link (line ~1257):

```html
<a href="#step-65" class="nav-step"><span class="step-badge" style="background:var(--step-sort)">6.5</span> Compile</a>
```

### Task 2.2: Add Step 6.5 section div

Insert a new `<div id="step-65" class="step-section">` between `#step-6` and `#step-7` (between lines ~1417 and ~1422). Follow the existing step-section layout:

```html
<div id="step-65" class="step-section">
  <h3><span class="step-badge" style="background:var(--step-sort)">6.5</span> Compile Expressions</h3>
  <p class="step-explanation">Compile CalcDef expressions to Python. Each CalcDef's output expressions are parsed into an AST and compiled. The compilation verdict (FULLY_COMPILABLE, PARTIALLY_COMPILABLE, MANUAL_REQUIRED) determines whether the module gets auto-generated implementation or a handwritten stencil.</p>
  <div class="step-panels">
    <div class="data-panel" id="step-65-input"></div>
    <div class="step-arrow">→</div>
    <div class="data-panel" id="step-65-output"></div>
  </div>
  <div class="step-callout">Without compilation, every module needs a handwritten implementation file. Compilation makes the pipeline self-sufficient for straightforward calculations — the generated code is complete, not just wiring.</div>
</div>
```

### Task 2.3: Update pipeline overview strip

If there's a pipeline overview diagram (the strip showing all steps), add Step 6.5 box. Check `PipelineStepRenderer` for how the overview strip is built — it may read step data from MODEL_DATA and auto-render, or it may be hardcoded HTML.

**Success criteria:**
- [x] Step 6.5 appears in sidebar between Step 6 and Step 7
- [x] `#step-65` section exists in the HTML with input/output panels
- [x] Pipeline overview strip shows 4 sub-steps (3.5, 4.5, 5.5, 6.5)

### Phase 2 Completion
**Completed:** 2026-02-22
**Changes Made:**
- Added `<a href="#step-65">` nav link between Step 6 and Step 7 in sidebar (line 1258)
- Added `<div id="step-65" class="step-section">` between `#step-6` and `#step-7` with explanation text, `step-io-layout` with input/output data panels, and callout
- Added `{ n: '6.5', name: 'Compile Expressions', href: '#step-65' }` to `subs` array in `renderOverviewStrip()`
- NavigationController auto-discovers the new section via `querySelectorAll('#sidebar a[href]')` — no JS changes needed

**Deviations from Plan:**
- Used `step-io-layout` + `step-io-arrow` classes (existing patterns) instead of `step-panels` + `step-arrow` (plan suggestion) for consistency with other step sections
- Used `.callout` class instead of `.step-callout` (which doesn't exist) — matches existing CSS

---

## Phase 3: JS Renderers — Step 6.5 + Updated Panels

**Goal:** Wire the new Step 6.5 data into the rendering pipeline and update existing renderers for new fields.

### Task 3.1: Add Step 6.5 rendering to PipelineStepRenderer

Add rendering logic for `#step-65-input` and `#step-65-output` panels. Input panel shows `CalculationDefinitionData` with `output_expression_asts`. Output panel shows `CalcDefCompilationResult` with verdict, compiled expression, and per-output expressions. Follow the pattern used by adjacent steps.

### Task 3.2: Update DAGRenderer module detail panel

`DAGRenderer._selectModule()` (line ~4882) builds the detail panel HTML. Add new fields:

- `calcDefName` — show below module type
- `docComment` — show if non-null, as a dim text block
- `sourceFile:sourceLine` — show as a source location reference
- `compilability` — show as a small badge (green/yellow/red by verdict)
- Input `description` and `defaultValue` — show alongside each input
- Output `description` and `unit` — show alongside each output

### Task 3.3: Update Step 5 rendering — factory pure returns

If Step 5's explanation text says the factory "will return" or uses aspirational language, change to confirmed: "the factory returns `(module, entry_points)` — verified by conformance tests". Add note that CalcUsage factory always returns `(module, {})`.

### Task 3.4: Update Step 5.5 rendering — Phase 1 sub-phases

If Step 5.5 shows the registry build phases as a table, split Phase 1 into:
- Phase 1a: CalcUsage outputs → `register_scoped(ScopedKey, CanonicalChannel)`
- Phase 1b: Aggregation outputs → `register_scoped(ScopedKey, CanonicalChannel)`
- Phase 1c: FORMULA outputs → `register_sysml_qn(SysMLQN, CanonicalChannel)`

### Task 3.5: Update Step 7 rendering — `_from_graph()` + auto-impl

Add to Step 7 explanation:
1. Note `_from_graph()` generator variants (pure-graph generators that require only ComputationGraph)
2. Auto-implementation dispatch: if `module.auto_impl_context` is populated → generate implementation directly, otherwise → generate stub stencil

**Success criteria:**
- [x] Step 6.5 input/output panels render with compilation data
- [x] Module detail panel shows metadata fields when clicking a DAG node
- [x] Step 5 uses confirmed language, not aspirational
- [x] Step 7 mentions `_from_graph()` variants and auto-impl dispatch

### Phase 3 Completion
**Completed:** 2026-02-22
**Changes Made:**
- Added `renderStep65()` method to PipelineStepRenderer with input/output panels showing CalculationDefinitionData → CalcDefCompilationResult, compilation summary stats with color-coded badges, and callout
- Added `.compile-stat` CSS class for summary stat boxes
- Updated `_selectModule()` in DAGRenderer to show: `calcDefName`, `docComment` (italic dim), `sourceFile:sourceLine`, `compilability` (color-coded badge), input `description`/`defaultValue`, output `description`/`unit`
- Updated Step 5 explanation: added "verified by conformance tests" and note about CalcUsage factory returning `(module, {})`
- Added two `<details>` sections to Step 7: `_from_graph()` generator variants (4 functions listed) and auto-implementation dispatch logic
- Strengthened ComputationGraph boundary callout in Step 6 with AST analysis test enforcement note

**Deviations from Plan:**
- Task 3.4 (Phase 1 sub-phases in Step 5.5) was already implemented in Phase 1 — the table already shows 1a/1b/1c. No changes needed.

---

## Phase 4: Act 3 — Dual Resolution Updates

**Goal:** Update the DualResolutionDemo to show the actual resolution mechanism.

### Task 4.1: Update Mechanism 3 panel content

The DualResolutionDemo (line ~1445, rendered by `DualResolutionDemo` class) currently shows three panels. Update Mechanism 3 from `resolve_input()` + named strategies to `_resolve_aggregation_input_channel()` + chain tracing:

Resolution chain to show:
1. Parse "part_usage.attribute" from symbolic ref
2. Find CHAIN :>> redefinition on child PartDef
3. Follow chain to CalcUsage output → build channel name
4. Fall back to OutputRegistry scoped/alias lookup
5. Cycle detection via visited set

Plus LocalTerm resolution (separate, inside factory):
1. Sibling aggregation output → channel match
2. EXPOSE_PURE alias → alias registry lookup
3. Entry point fallback → DESIGN_ATTRIBUTE

### Task 4.2: Add framing note

Add introductory text to Act 3c: "The architecture describes two resolution *paths* (DFS-integrated vs. post-DFS). Within the post-DFS path, FORMULA and Aggregation use distinct *mechanisms*."

### Task 4.3: Add footnote about `resolve_input()`

Add a footnote or collapsed detail: "`resolve_input()` with `AGG_STRATEGIES` exists in `input_resolver.py` and is conformance-tested, but not yet wired into the graph builder."

### Task 4.4: Update interactive resolution examples

If the demo has interactive dropdowns or trace-through examples that reference named strategies, update to trace through chain resolution steps instead.

### Task 4.5: Update CSS variable

Rename `--path-resolve-input` → `--path-agg-chain` in CSS and all JS references.

**Success criteria:**
- [x] Mechanism 3 panel shows `_resolve_aggregation_input_channel()`, not `resolve_input()`
- [x] Footnote acknowledges `resolve_input()` as planned but not wired
- [x] No references to `AGG_STRATEGIES` as the running mechanism
- [x] CSS variable renamed

### Phase 4 Completion
**Completed:** 2026-02-22
**Changes Made:**
- Added 2-path vs 3-mechanism framing note as a left-bordered paragraph in DualResolutionDemo intro (explains architecture overview groups FORMULA + Aggregation as "Path 2" while the explainer separates all three)
- Added visible `<details>` footnote acknowledging `resolve_input()` with AGG_STRATEGIES as conformance-tested but not wired into graph builder
- Renamed CSS variable `--path-resolve-input` → `--path-agg-chain` (line 38)
- Fixed `resolve_input()` text in F3 factory input panel → `_resolve_aggregation_input_channel()`
- Fixed `resolve_input()` text in Step 5.5 ordering constraint callout → `_resolve_aggregation_input_channel()`

**Deviations from Plan:**
- Tasks 4.1 (Mechanism 3 panel) and 4.4 (interactive examples) were already completed during Phase 1 — MODEL_DATA and DualResolutionDemo were updated together. No additional changes needed.
- `--path-resolve-input` CSS variable was only declared, never used via `var()` — rename was trivial.

---

## Phase 5: Cross-Cutting Polish

**Goal:** REQ ID annotations, callout updates, and consistency pass.

### Task 5.1: Add REQ IDs to callout boxes

Add REQ ID references to HTML callout elements. Highest-value placements:
- Ordering constraints (Steps 3.5→4, 4.5→5, 5.5→6): REQ-ORCH-02, REQ-ORCH-03, REQ-ORCH-04
- ComputationGraph boundary (Step 6→7 transition): REQ-PIPE-07 + "enforced by AST analysis test"
- Dual resolution consistency: REQ-DRA-04
- Self-reference guard (Step 6): REQ-GA-04, REQ-IR-03
- Factory purity (Step 5): REQ-MF-01

Format: small `<span class="req-badge">REQ-XX-NN</span>` inline, styled as subtle monospace tags.

### Task 5.2: Add CSS for REQ badges

```css
.req-badge {
  font-family: monospace;
  font-size: 0.65rem;
  color: #64748B;
  background: #F1F5F9;
  padding: 0.1rem 0.3rem;
  border-radius: 3px;
  margin-left: 0.3rem;
}
```

### Task 5.3: Strengthen ComputationGraph boundary callout

The boundary callout between Steps 6 and 7 currently describes it as a design principle. Update to note it's enforced by test (REQ-PIPE-07): "An AST analysis test verifies that `generation/` imports zero classes from `extraction/` or `analysis/`."

### Task 5.4: Update stale text references

Scan all HTML text content for:
- `resolve_input()` used as if it's the running mechanism (OK in footnotes)
- `AGG_STRATEGIES` used as if it's the running mechanism
- Aspirational language ("will return", "the factory should")
- Any references to old paths (`resolution/identifier_types.py`, `generation/initialization.py`)

**Success criteria:**
- [x] At least 6 REQ IDs appear as badges in callout elements
- [x] REQ badge CSS exists
- [x] ComputationGraph boundary callout references test enforcement
- [x] No stale aspirational language or old code paths in text content

### Phase 5 Completion
**Completed:** 2026-02-22
**Changes Made:**
- Added `.req-badge` CSS class (monospace, 0.65rem, slate background, 3px radius)
- Added 9 REQ badges across 8 callout locations:
  - REQ-ORCH-02 (Step 3.5→4 ordering constraint)
  - REQ-ORCH-03 (Step 4.5→5 ordering constraint)
  - REQ-MF-01 (Step 5 factory purity)
  - REQ-ORCH-04 (Step 5.5→6 ordering constraint)
  - REQ-PIPE-07 (ComputationGraph boundary, AST test enforcement)
  - REQ-GA-07 (topological sort), REQ-GA-03 (channel validation)
  - REQ-GA-04 + REQ-IR-03 (self-reference guard in DualResolutionDemo)
  - REQ-DRA-04 (dual resolution consistency)
- Stale text scan confirmed clean: no aspirational language, no old code paths, no `resolve_input()` as running mechanism

**Deviations from Plan:**
- Task 5.3 (ComputationGraph boundary strengthening) was already completed in Phase 3 — line 4124 already had "Enforced by AST analysis test" text. Added REQ-PIPE-07 badge alongside it.
- Added REQ-GA-03 (channel validation) in addition to planned badges — it was a natural fit alongside REQ-GA-07.

---

## Execution Summary

| Phase | Tasks | Dependency | Scope |
|-------|-------|-----------|-------|
| 1 | 4 | None | Medium — JS data updates |
| 2 | 3 | None | Small — HTML structure |
| 3 | 5 | Phases 1, 2 | Large — renderer logic |
| 4 | 5 | Phase 1 | Medium — DualResolutionDemo rewrite |
| 5 | 4 | Phases 1-4 | Small — cross-cutting polish |

**Phases 1+2 can run in parallel** (data vs. HTML structure, no overlap).
**Phases 3+4 can run in parallel** (Act 2 renderers vs. Act 3 demo, independent sections). Both depend on Phase 1 (MODEL_DATA).
**Phase 5 runs last** (cross-cutting).

```
Phase 1 (MODEL_DATA) ──┬──→ Phase 3 (renderers) ──┬──→ Phase 5 (polish)
                        │                           │
Phase 2 (HTML struct) ──┤                           │
                        │                           │
                        └──→ Phase 4 (Act 3 demo) ──┘
```

---

## Completion Criteria (whole activity)

- [x] Step 6.5 exists in sidebar nav, HTML body, pipeline overview, and renders data
- [x] MODEL_DATA includes all new PipelineModule metadata fields and step65_compile
- [x] Module detail panel (DAG click) shows calcDefName, compilability, docComment, source location, input/output descriptions+units
- [x] DualResolutionDemo Mechanism 3 shows `_resolve_aggregation_input_channel()` with chain-trace steps
- [x] Footnote acknowledges `resolve_input()` as tested-but-unwired
- [x] At least 6 REQ IDs appear as inline badges (9 badges across 8 locations)
- [x] No aspirational language — only confirmed state
- [x] CSS variable `--path-resolve-input` → `--path-agg-chain`
- [ ] HTML opens in browser and all interactive features still work
