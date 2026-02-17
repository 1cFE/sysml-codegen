# Implementation Plan: New Pipeline Explainer

**Status:** Draft
**Created:** 2026-02-17
**Last Updated:** 2026-02-17

## Source Documents
- **Spec:** `.project/active/new-pipeline-explainer/spec.md`
- **Design:** `.project/active/new-pipeline-explainer/design.md` — See here for component details, data model structure, color palette, layout algorithms
- **Baseline data:** `tests/fixtures/baseline_yaml/solar_battery.yaml` — ground truth for all module names, inputs, outputs, channels
- **SysML fixtures:** `tests/fixtures/solar_battery_model/` — costing.sysml, library.sysml, design.sysml

## Implementation Strategy

**Phasing Rationale:**
Data-first, then infrastructure, then content in narrative order. Every phase produces a viewable HTML file that can be opened in a browser and inspected. The output is a single file (`.project/diagrams/new_pipeline_explainer.html`) — each phase appends to it.

**Key constraint:** This is a documentation artifact. No source code is modified. No unit tests apply. Validation is: data accuracy against baseline YAML, visual inspection in browser, comprehension check.

**Data reconciliation note:** The baseline YAML contains 36 modules (not 35 as stated in the design). During Phase 1, reconcile the count and update MODEL_DATA accordingly. The discrepancy is likely `allocation_model` being counted or not as a standard F1 CalcUsage.

**Overall Validation Approach:**
- Each phase produces a viewable HTML file
- Data accuracy validated against baseline YAML
- Visual inspection in Chrome (primary), Firefox, Safari
- File size tracked after each phase (budget: < 500KB, target: 200-250KB)

---

## Phase 1: Foundation — MODEL_DATA + HTML Skeleton

### Goal
Build the complete `MODEL_DATA` JS object and HTML skeleton. This is the riskiest piece — every subsequent phase renders from this data. If module names, channels, or edges are wrong, everything downstream is wrong. De-risk by validating against the baseline YAML immediately.

### Validation Stencil (Check This First)
```
For every module in baseline YAML solar_battery.yaml:
  ✓ A matching entry exists in MODEL_DATA.modules[] with correct:
    - id (short human-readable ID)
    - fullEQN (matches YAML module key)
    - family (F1/F2/F3 — matches YAML comment prefix)
    - tier (0-6 — consistent with dependency depth)
    - cluster (solar_array/battery_system/site_infra/system)
    - inputs[] (param names + source types match YAML)
    - outputs[] (channel names match YAML)

For every edge implied by YAML input references:
  ✓ A matching entry exists in MODEL_DATA.edges[]
    - from/to module IDs are valid
    - fromOutput/toInput names match

For the traced module (pv_module cost_model):
  ✓ MODEL_DATA.pipelineTrace has complete step-by-step data
    matching design.md#4c through design.md#4l
```

### Changes Required

**See `design.md` for:**
- Full MODEL_DATA structure → `design.md#7-js-data-model-model_data`
- HTML body structure → `design.md#1-file-architecture`
- CSS color palette → `design.md#2e-color-palette`
- Sidebar navigation → `design.md#2c-sidebar-navigation`

**Specific work:**

#### 1. Derive MODULE_DATA from baseline
- [ ] Parse `tests/fixtures/baseline_yaml/solar_battery.yaml` — extract all 36 module names, inputs, outputs, channels
- [ ] Assign short IDs per the convention in `design.md#7` (e.g., `sa_pv_cost_model`, `bs_capital_cost`, `lcoe`)
- [ ] Classify each module: F1 (CalcUsage — no "source:" comment), F2 (computed_attribute comment), F3 (aggregation comment)
- [ ] Assign tiers 0-6 per dependency depth (see `design.md` Research Findings → Dependency tiers)
- [ ] Assign clusters (solar_array, battery_system, site_infra, system)
- [ ] Build edges[] from YAML input channel references (input value matches an output channel → edge)
- [ ] Reconcile 36 vs 35 module count — update design if needed

#### 2. Build pipelineTrace for traced module
- [ ] Step 1 data: CalcDef fields from `library.sysml` PVModuleCostCalc, CalcUsage fields from template in 'PV Module' PartDef
- [ ] Step 2 data: Key_A/B/C for pv_module cost_model outputs (derive from YAML channel names)
- [ ] Step 3.5 data: Before/after bindings (template CHAIN → design LITERAL overrides from `design.sysml`)
- [ ] Step 4 data: Entry point classifications (match YAML input sources: `design_params.` vs `library_params.`)
- [ ] Step 5 data: PipelineModule fields (directly from YAML module entry)

#### 3. Build resolution and entry point examples
- [ ] Dual resolution examples from `design.md#5c` — backtrackerPath + resolveInputPath for 2-3 bindings
- [ ] Registry examples from `design.md#4j` — Key formats with concrete values
- [ ] Entry point groups from YAML (design_params, library_params, system_design)

#### 4. HTML skeleton
- [ ] Create `.project/diagrams/new_pipeline_explainer.html`
- [ ] Write `<style>` block with full color palette from `design.md#2e`
- [ ] Write `<body>` with sidebar nav from `design.md#2c` + empty section containers for all 4 acts
- [ ] Write `<script>` block with MODEL_DATA constant + empty class stubs
- [ ] Verify file opens in browser with working sidebar navigation

### Validation

- [ ] Open in Chrome — sidebar renders, sections scroll, no JS errors in console
- [ ] Spot-check 5 modules: compare MODEL_DATA entry against baseline YAML line-by-line
- [ ] Verify edge count: every non-entry-point input in YAML should produce an edge
- [ ] Verify pipelineTrace.step5_module matches YAML entry for pv_module cost_model exactly
- [ ] Check file size (target: ~40-50KB at this stage — mostly MODEL_DATA + skeleton)

**What We Know Works After This Phase:**
Data is accurate. File opens. Navigation works. Everything else can render from this data with confidence.

---

## Phase 2: Infrastructure + Act 1 (Hierarchy + Big Question)

### Goal
Build shared JS infrastructure (ZoomPanController, rendering utilities) and the first visual content (Act 1 hierarchy diagram + Big Question animation). This proves the rendering approach works before building the more complex sections.

### Validation Stencil
```
Hierarchy diagram:
  ✓ Solar Battery Plant contains 3 subsystem rectangles side-by-side
  ✓ Each subsystem contains correct component rectangles
  ✓ Multiplicity badges show ×20 (PV Module), ×4 (Inverter), ×8 (Battery Pack)
  ✓ cost_model boxes visible inside components
  ✓ Aggregation formulas visible at assembly level
  ✓ Zoom: mouse wheel zooms in/out (range 0.3×–5×)
  ✓ Pan: click-drag moves the viewport
  ✓ Keyboard: +/- zoom, arrows pan, 0 reset

Big Question animation:
  ✓ "Show me the path to LCOE" button triggers trace
  ✓ Highlight propagates backward: LCOE → ann_financial → plant capital → subsystems → leaves
  ✓ Non-upstream elements dim to 15% opacity
  ✓ Animation completes in ~4 seconds (7 steps × ~600ms)
```

### Changes Required

**See `design.md` for:**
- ZoomPanController → `design.md#2a`
- Shared utilities → `design.md#2b`
- Hierarchy diagram layout → `design.md#3a`
- Big Question animation → `design.md#3b`
- Narrative callout integration → `design.md#3a` (positioned overlays with connector lines)

**Specific work:**

#### 1. ZoomPanController class
- [ ] Implement class per `design.md#2a` — viewBox manipulation, mouse wheel, click-drag, keyboard
- [ ] Test on empty SVG container before attaching to hierarchy

#### 2. Shared utilities
- [ ] `renderModuleNode()` — rounded rect with family color, label, optional ports
- [ ] `traceUpstream()` — BFS backward through MODEL_DATA.edges
- [ ] `highlightElements()` / `dimElements()` — SVG element manipulation by data-id
- [ ] `renderDataPanel()` — HTML panel showing model fields with values (for Act 2)
- [ ] `renderStepConnector()` — arrow between step panels (for Act 2)

#### 3. HierarchyRenderer
- [ ] Render nested rectangles from MODEL_DATA.hierarchy
- [ ] Component boxes with design values, cost_model sub-boxes
- [ ] Multiplicity badges (×N stack visual)
- [ ] Aggregation formula text at assembly level
- [ ] Narrative callout overlays with connector lines (scroll-driven reveal via IntersectionObserver)
- [ ] Attach ZoomPanController

#### 4. Big Question animation
- [ ] "Show me the path to LCOE" button
- [ ] CSS @keyframes for pulse + glow
- [ ] JS setTimeout sequencing (~600ms per step) using `traceUpstream()` from LCOE
- [ ] `highlightElements()` + `dimElements()` on completion
- [ ] Closing callout text

### Validation

- [ ] Open in Chrome — hierarchy diagram renders with correct nesting
- [ ] Zoom in to PV Module — verify wattage: 400, efficiency: 0.21 visible
- [ ] Zoom out — verify all 3 subsystems visible side-by-side
- [ ] Click-drag pan works smoothly
- [ ] Click "Show me the path to LCOE" — animation plays through all tiers
- [ ] After animation: LCOE and all upstream highlighted, rest dimmed
- [ ] Test in Firefox — no rendering differences
- [ ] Check file size (target: ~80-100KB)

**What We Know Works After This Phase:**
SVG rendering, zoom/pan, animation, narrative callouts, and shared utilities all proven. The visual foundation is solid.

---

## Phase 3: Act 2 — The 7-Step Pipeline Proof

### Goal
Build the pipeline overview strip and all 10 step sections (Steps 1, 2, 3, 3.5, 4, 4.5, 5, 5.5, 6, 7). This is the centerpiece — the "prove the refactored design works" arc. Each step shows concrete Input→Transformation→Output for the traced module (PV Module cost_model).

This is the primary design validation exercise. If any step can't be concretely explained with real data, we've found a design gap.

### Validation Stencil
```
Pipeline overview strip:
  ✓ 7 step boxes visible in horizontal strip
  ✓ Sub-steps (3.5, 4.5, 5.5) shown below parent steps
  ✓ 3 ordering constraint annotations visible (red "MUST precede" callouts)
  ✓ Strip stays sticky while scrolling through Act 2

Per step section (repeat for all 10):
  ✓ Plain-English explanation visible at top
  ✓ Input panel shows correct model name + concrete field values
  ✓ Output panel shows correct model name + concrete field values
  ✓ Traced module (pv_module cost_model) highlighted in amber
  ✓ "Why this step exists" explanation present

Step-specific checks:
  ✓ Step 2: Scope ambiguity visual shows Key_A matches 9 modules, Key_C is unique
  ✓ Step 3: DFS tree shows recurse vs stop decisions
  ✓ Step 3.5: Before/after bindings match pipelineTrace.step35_rewrite
  ✓ Step 5: Three-column factory layout, each shows input → pure function → (PipelineModule, dict)
  ✓ Step 5.5: Registry table grows across 4 phases
  ✓ Step 6: ComputationGraph boundary diagram shows generation consuming ONLY the graph
```

### Changes Required

**See `design.md` for:**
- Pipeline overview strip → `design.md#4a`
- Step layout template → `design.md#4b`
- Step 1 through Step 7 details → `design.md#4c` through `design.md#4l`
- ComputationGraph boundary diagram → `design.md#4k`

**Specific work:**

#### 1. PipelineStepRenderer class
- [ ] Implement step section template (explanation + input panel + output panel + "why" callout)
- [ ] Use `renderDataPanel()` for input/output panels
- [ ] Collapsible fields (click to expand arrays/objects)
- [ ] Amber highlighting on traced module fields

#### 2. Pipeline overview strip
- [ ] Horizontal strip with 7 step boxes + sub-step boxes
- [ ] Step-number badges with per-step colors from `design.md#2e`
- [ ] 3 red ordering constraint annotations
- [ ] CSS `position: sticky` behavior
- [ ] Click step box → scroll to detailed section

#### 3. Step sections (all 10)
- [ ] Step 1: Extract — CalcDef + CalcUsage panels from pipelineTrace.step1_extract
- [ ] Step 2: Build Registry — Key_A/B/C table + scope ambiguity visual
- [ ] Step 3: Trace Dependencies — DFS tree diagram (SVG, color-coded recurse/stop)
- [ ] Step 3.5: Hierarchy — Before/after binding panels + red ordering constraint callout
- [ ] Step 4: Classify Entry Points — Decision tree for 3 example parameters
- [ ] Step 4.5: Computed Attributes — FORMULA classification + red ordering constraint callout
- [ ] Step 5: Build Modules — Three-column factory layout (CalcUsage / FORMULA / Aggregation)
- [ ] Step 5.5: Build OutputRegistry — Progressive table (phases 1a→1b→1c→2→3→4)
- [ ] Step 6: Sort + Validate — Kahn's algorithm animation + ComputationGraph boundary diagram
- [ ] Step 7: Render — Three code panels with field-level traceability annotations

#### 4. Design validation findings
- [ ] While building each step, note any case where the design intent docs are ambiguous or contradictory
- [ ] Document findings inline as HTML comments or in a "Design Validation Findings" section at the bottom

### Validation

- [ ] Open in Chrome — all 10 step sections render with data panels
- [ ] Pipeline overview strip stays sticky during scroll
- [ ] Click Step 5 in overview → smooth-scrolls to Step 5 section
- [ ] Step 3 DFS tree: verify LCOE → annualized_financial → plant capital_cost path is shown
- [ ] Step 5 three-column layout: verify each factory column shows correct input model and return tuple
- [ ] Step 6 ComputationGraph boundary: verify "generation consumes ONLY the graph" is visually clear
- [ ] Step 7 YAML snippet: compare against baseline YAML for annualized_financial module — must match
- [ ] Expand/collapse works on data panel array fields
- [ ] Check file size (target: ~150-180KB)

**What We Know Works After This Phase:**
The 7-step pipeline can be concretely explained end-to-end with real data. Any design gaps have surfaced. The ComputationGraph boundary is proven. Pure factory pattern is visualized.

---

## Phase 4: Act 3 — The Hard Parts (Proof Sections)

### Goal
Build the three interactive proof sections: template instantiation, aggregation decomposition, and dual resolution. These are the most interactive parts — steppers, sliders, animated transitions, side-by-side comparisons.

### Validation Stencil
```
Template instantiation (Act 3a):
  ✓ 3-panel layout: Recipe / Design / Virtual Copy
  ✓ Step 1: Recipe panel shows template bindings (CHAIN)
  ✓ Step 2: Design panel shows :>> overrides (amber)
  ✓ Step 3: Virtual copy shows rewritten bindings with strikethrough
  ✓ Stepper or Play button advances through steps
  ✓ Step callout text syncs with active step

Aggregation decomposition (Act 3b):
  ✓ 4-tier vertical stack renders (leaf → subsystem → plant → LCOE)
  ✓ Step 1: Color-coded expression (SumTerm red, SingletonTerm blue, LocalTerm green)
  ✓ Step 2: sum() → parametric multiply animation
  ✓ Step 3: LocalTerm 3-strategy resolution shown
  ✓ Step 4: Cascade rollup visualized
  ✓ module_count slider works (1-50, updates multiplier display)

Dual resolution (Act 3c):
  ✓ Side-by-side layout: Backtracker (left) vs resolve_input() (right)
  ✓ Both paths trace "capital_cost" and arrive at same channel
  ✓ Strategy chain shows 5 strategies (C, A, B, D, E) with concrete examples
  ✓ AGG_STRATEGIES reordering (D promoted) is shown
  ✓ Self-reference guard callout present
  ✓ Dropdown with 2-3 example references — selecting one replays the trace
  ✓ "Why they can't merge" explanation below the side-by-side
```

### Changes Required

**See `design.md` for:**
- Template instantiation → `design.md#5a`
- Aggregation decomposition → `design.md#5b`
- Dual resolution → `design.md#5c`

**Specific work:**

#### 1. TemplateExpansionDemo class
- [ ] 3-panel horizontal layout (HTML + inline SVG for binding arrows)
- [ ] Stepper control (Step 1/2/3 buttons + Play)
- [ ] Step-synced callout column (left side, cross-fade on step change)
- [ ] Step 3: strikethrough animation on rewritten bindings, amber highlight on new values

#### 2. AggregationDemo class
- [ ] 4-tier vertical stack (SVG, uses `renderModuleNode()` for tier boxes)
- [ ] Step 1: Color-coded SysML expression (SumTerm/SingletonTerm/LocalTerm)
- [ ] Step 2: sum() → multiply animation (text fade + multiply icon appear)
- [ ] Step 3: LocalTerm 3-strategy resolution (sequential check with ✓/✗ results)
- [ ] Step 4: Cascade animation (highlight flows bottom to top)
- [ ] module_count slider (HTML range input, updates display on change)

#### 3. DualResolutionDemo class
- [ ] Side-by-side container (flexbox, two equal-width panels)
- [ ] Left panel: Backtracker path — scope + scoped key + result
- [ ] Right panel: Strategy chain — 5 strategy boxes, each expandable on click
- [ ] AGG_STRATEGIES variant shown as reordered chain
- [ ] Bottom section: "SAME CHANNEL. SAME WIRING. DIFFERENT DATA TYPE." equivalence proof
- [ ] "Why they can't merge" explanation paragraph
- [ ] Self-reference guard callout
- [ ] Dropdown selector with 2-3 resolution examples from MODEL_DATA.resolutionExamples
- [ ] Selecting a new example rerenders both panels

### Validation

- [ ] Template demo: advance through all 3 steps, verify binding rewrite matches pipelineTrace.step35_rewrite
- [ ] Aggregation demo: verify SumTerm for pv_module shows count=20 and multAttr=module_count
- [ ] Aggregation slider: drag to 1, verify display updates; drag to 50, verify
- [ ] Dual resolution: verify "capital_cost" trace — both panels show same canonical channel
- [ ] Dual resolution: select "discount_rate" from dropdown — both panels show ENTRY_POINT result
- [ ] Strategy chain: click Strategy D (ChainRedefinitionFollow) — expansion shows concrete example
- [ ] Check file size (target: ~200-230KB)

**What We Know Works After This Phase:**
The three hardest concepts are concretely proven with interactive visualizations. Template instantiation, aggregation decomposition, and dual resolution all demonstrated with real data. The interactive elements (steppers, sliders, dropdowns) work.

---

## Phase 5: Act 4 + Glossary + Polish

### Goal
Build the computation graph DAG (the biggest rendering challenge), generated code samples with traceability, glossary overlay, and final polish. This completes the artifact.

### Validation Stencil
```
DAG diagram:
  ✓ All 36 modules rendered (verify count in JS console: MODEL_DATA.modules.length)
  ✓ No module overlaps at default zoom
  ✓ Modules color-coded: F1 blue, F2 purple, F3 orange
  ✓ Clusters have dashed background rectangles with labels
  ✓ Edges render with arrowheads, no egregious crossings
  ✓ Click module → expanded view shows inputs/outputs/factory type
  ✓ Trace mode: click LCOE → all upstream highlights, rest dims
  ✓ Progressive disclosure: initial view shows ~8 collapsed clusters
  ✓ "Expand All" shows full graph
  ✓ Zoom/pan works (ZoomPanController)
  ✓ Minimap shows viewport position

Generated code samples:
  ✓ Pipeline YAML snippet matches baseline YAML for annualized_financial
  ✓ JSON input snippet shows correct entry points with defaults
  ✓ "Click to highlight in graph" links scroll to DAG and trigger trace

Glossary:
  ✓ Glossary button in sidebar opens right-side panel
  ✓ All 8 terms present with visual examples
  ✓ Clicking dotted-underline term in narrative opens glossary to that term
  ✓ Glossary closeable (X button or click outside)

Final checks:
  ✓ File opens with network disabled (self-contained)
  ✓ File size < 500KB (target: 200-250KB)
  ✓ No JS errors in console (Chrome, Firefox, Safari)
  ✓ Sidebar navigation highlights correct section on scroll
  ✓ Keyboard navigation: +/- zoom, arrows pan on focused diagram
  ✓ All narrative callouts have connector lines to diagram elements
```

### Changes Required

**See `design.md` for:**
- DAG diagram → `design.md#6a`
- Tier-slot grid layout algorithm → `design.md#6a` (tier × TIER_WIDTH, slot × SLOT_HEIGHT + clusterOffset)
- Generated code samples → `design.md#6b`
- Glossary → `design.md#2d`

**Specific work:**

#### 1. DAGRenderer class
- [ ] Tier-slot grid layout: compute {x, y} for each module from tier + cluster sort
- [ ] Collapsed node rendering (160×40px, short name, family color)
- [ ] Expanded node rendering (280×variable, input/output ports)
- [ ] Edge rendering: cubic Bezier or Manhattan segments with arrowheads
- [ ] Cluster background rectangles (dashed border, label)
- [ ] Collapse/expand clusters (click cluster → toggle internal modules)
- [ ] "Expand All" / "Collapse All" buttons in sticky overlay bar
- [ ] Trace mode: click module → traceUpstream() → highlight/dim
- [ ] Pre-activate LCOE trace on first load
- [ ] Minimap (small inset SVG with viewport rectangle)
- [ ] Attach ZoomPanController

#### 2. Generated code samples
- [ ] Pipeline YAML panel (annualized_financial) with traceability annotations
- [ ] Module wrapper panel (skeleton) with traceability annotations
- [ ] JSON input panel (design_params excerpt) with traceability annotations
- [ ] "Click to highlight in graph" links → scroll to DAG + trigger trace mode

#### 3. GlossaryController class
- [ ] Right-side slide-in panel (400px)
- [ ] 8 term entries per `design.md#2d` — term, definition, SysML snippet, inline SVG visual
- [ ] Open on sidebar button click or dotted-underline term click
- [ ] Scroll to specific term when opened from narrative link
- [ ] Close on X button or outside click

#### 4. Polish pass
- [ ] Consistent callout positioning across all acts
- [ ] Animation timing review (nothing too fast or too slow)
- [ ] Color consistency check (every F1 is blue, every F2 is purple, every F3 is orange, everywhere)
- [ ] Responsive: sidebar collapses on narrow viewport
- [ ] Print media query: hide sidebar and interactive controls
- [ ] Add "Design Validation Findings" section at bottom (from Phase 3 notes)

### Validation

- [ ] DAG: count rendered modules in browser dev tools — must be 36
- [ ] DAG: screenshot at default zoom — verify no overlaps, clusters distinct
- [ ] DAG: click LCOE → verify trace highlights all upstream (should be ~30+ modules)
- [ ] DAG: collapse all → verify ~8 elements visible (3 subsystem clusters + 5 system calcs)
- [ ] Code samples: compare YAML panel against baseline YAML for annualized_financial — exact match
- [ ] Glossary: click "PartDefinition" term in Act 1 narrative → glossary opens to PartDefinition entry
- [ ] Self-containment: disconnect network, reload → everything renders
- [ ] File size: `ls -la .project/diagrams/new_pipeline_explainer.html` < 500KB
- [ ] Chrome: full scroll-through, all interactions work
- [ ] Firefox: full scroll-through, no rendering differences
- [ ] Safari: full scroll-through, zoom/pan works
- [ ] Comprehension: can you answer these 5 questions from the spec after reading?
  1. "What are the 7 pipeline steps and what does each produce?"
  2. "Why are there two resolution paths and why can't they be merged?"
  3. "How does sum(pv_module.capital_cost) become a parametric multiply?"
  4. "What is Key_C and why does it exist?"
  5. "What guarantees that generation doesn't need extraction data?"

**What We Know Works After This Phase:**
Everything. The artifact is complete, self-contained, accurate, and comprehensible. All spec acceptance criteria can be checked.

---

## Environment Setup

**See CLAUDE.md for full environment rules.**

This artifact requires no build tools. The output is a single `.html` file opened directly in a browser. No `uv`, `pytest`, or `mypy` involved.

For data derivation, the baseline YAML at `tests/fixtures/baseline_yaml/solar_battery.yaml` is the ground truth. The SysML source at `tests/fixtures/solar_battery_model/` provides the raw model values (design overrides, library defaults, expressions).

---

## Risk Management

**See `design.md#potential-risks` for detailed risk analysis.**

**Phase-Specific Mitigations:**
- **Phase 1**: Data accuracy is the biggest risk. Mitigated by line-by-line spot-checks against baseline YAML. Build a checklist of all 36 module IDs before writing any rendering code.
- **Phase 3**: Act 2 length could overwhelm. Mitigated by progressive disclosure — steps start collapsed with 1-sentence summaries, expand on click. Pipeline overview strip provides orientation.
- **Phase 4**: Dual resolution is the most novel visualization. Mitigated by reusing the registry trace pattern from Step 5.5 (already validated in Phase 3). The side-by-side is a layout change, not a new rendering primitive.
- **Phase 5**: DAG with 36 modules may have edge-crossing issues. Mitigated by Manhattan-style routing with sweep-based overlap avoidance. If edge crossings are bad, fall back to simple curved Bezier paths (less precise but visually cleaner at scale).

---

## Implementation Notes

_TO BE FILLED DURING IMPLEMENTATION_

### Phase 1 Completion
**Completed:**
**Actual Changes:**
**Issues:**
**Deviations:**

### Phase 2 Completion
**Completed:**
**Actual Changes:**
**Issues:**
**Deviations:**

### Phase 3 Completion
**Completed:**
**Actual Changes:**
**Issues:**
**Deviations:**
**Design Validation Findings:**

### Phase 4 Completion
**Completed:**
**Actual Changes:**
**Issues:**
**Deviations:**

### Phase 5 Completion
**Completed:**
**Actual Changes:**
**Issues:**
**Deviations:**

---

**Status**: Draft → In Progress → Complete
