# Design: New Pipeline Explainer

**Status:** Draft
**Owner:** Reid Westwood
**Created:** 2026-02-17 02:15 UTC
**Complexity:** HIGH
**Branch:** cost-pattern-refactor
**Commit:** 59b29b0

---

## Overview

A single self-contained HTML file (~200-300KB) that traces the LCOE computation through the refactored 7-step pipeline, depicting the intended architecture as if it already exists. Serves two purposes: validate the refactor design by forcing it through a concrete example, and teach the architecture to new engineers. Vanilla HTML + inline SVG + vanilla JS, zero external dependencies.

## Related Artifacts

- **Spec:** `.project/active/new-pipeline-explainer/spec.md`
- **Prior design (old spec):** `.project/active/interactive-pipeline-explainer/design.md`
- **Design intent:** `.project/concepts/refactor-design-intent/` (27 documents)
- **Research:** `.project/research/20260216-120000_interactive-html-diagram-frameworks.md`
- **Existing HTML (superseded):** `.project/diagrams/08_block_diagrams.html`
- **Solar battery fixtures:** `tests/fixtures/solar_battery_model/` (3 .sysml files)

---

## Research Findings

### Visual Framework Decision

Research (`.project/research/20260216-120000_...`) evaluated 6 approaches. Vanilla HTML+SVG+JS was recommended (Claude's strongest generation mode, zero deps, maximum layout control). ELK.js was the runner-up for complex DAGs but adds ~300KB. The prior design solved this by implementing a **tier-slot grid layout algorithm** in vanilla JS — algorithmic positioning without external libraries. This approach is carried forward.

### Existing HTML Analysis

The current `08_block_diagrams.html` (137KB) uses static inline SVG with hand-coded coordinates, hover/click tooltips only, no zoom/pan, 1D vertical layout. All 9 diagrams are vertical chains of boxes. The prior design for the old spec (`interactive-pipeline-explainer/design.md`, 55KB) solved every one of these problems with:

- **ZoomPanController** class (viewBox-based zoom/pan with keyboard support)
- **Tier-slot grid layout** for the DAG (algorithmic, not manual coordinates)
- **Narrative callout overlays** (positioned inside diagram containers with connector lines, scroll-driven reveal)
- **Progressive disclosure** (collapsed clusters, detail levels)
- **Shared utilities** (`renderModuleNode()`, `traceUpstream()`, `highlightElements()`, `dimElements()`)

All of this infrastructure is reusable for the new design. The changes are in **narrative structure** (4 acts instead of 3) and **new visualization types** (pipeline step waterfall, dual resolution side-by-side, factory diagrams).

### Solar Battery Model Data (from test fixtures)

**Part hierarchy** (3 levels, 13 PartDefs):
```
Solar Battery Plant
├── Solar Array
│   ├── PV Module [×20]         → cost_model: PVModuleCostCalc
│   ├── String Inverter [×4]    → cost_model: InverterCostCalc
│   ├── Array BOS               → cost_model: ArrayBOSCostCalc
│   └── allocation_model: AllocationCostCalc
├── Battery System
│   ├── Battery Pack [×8]       → cost_model: BatteryPackCostCalc
│   ├── Hybrid Inverter         → cost_model: HybridInverterCostCalc
│   └── Battery BOS             → cost_model: BatteryBOSCostCalc
└── Site Infrastructure
    ├── Racking & Mounting       → cost_model: RackingCostCalc
    ├── Electrical Panel         → cost_model: ElectricalPanelCostCalc
    └── Permitting & Interconnect→ cost_model: PermittingCostCalc
```

**Module family breakdown**: 14 F1 (CalcUsage) + 1 F2 (Computed Attribute: `p_net_kw`) + 20 F3 (Aggregation: 5 cost attrs × 4 assemblies) = **35 modules**.

**Dependency tiers** (0-6): Tier 0 = leaf F1 modules, Tier 1 = F2, Tier 2-3 = subsystem F3, Tier 4-5 = plant F3 + system calcs, Tier 6 = LCOE.

### Data Models (post-refactor)

Documented fully in the explore agent output. Key models for the explainer:

| Layer | Model | Key Fields |
|-------|-------|------------|
| Extraction | `CalculationDefinitionData` | name, qualified_name, input_attributes, output_attributes, output_expression_asts |
| Extraction | `CalcUsageData` | instance_name, calc_def_name, bindings (list[BindingInfo]), is_template, qualified_name |
| Extraction | `HierarchyExtractionResult` | redefinitions, design_overrides, multiplicities, aggregation_expressions, usage_type_map |
| Extraction | `AggregationExpressionData` | sum_terms, singleton_terms, local_terms, transformed_expression |
| Analysis | `BacktrackingResult` | required_usages, binding_resolutions (dict[str, BindingResolution]), entry_points |
| Core | `OutputRegistry` | _scoped (dict[ScopedKey, CanonicalChannel]), _sysml_qn (dict[SysMLQN, CanonicalChannel]), _alias (dict[ScopedKey, CanonicalChannel]), _canonical (set[CanonicalChannel]), scoped_lookup(), sysml_qn_lookup(), alias_lookup(), register_scoped(), register_sysml_qn(), register_alias() |
| Core | `BindingResolution` | resolution_type (ENTRY_POINT\|MODULE_OUTPUT), qualified_name, source_path |
| Resolution | `ComputationGraph` | modules (list[PipelineModule]), entry_point_groups (list[ParameterGroup]), execution_order |
| Resolution | `PipelineModule` | name, module_type, inputs (list[ModuleInput]), outputs (list[ModuleOutput]), compilability, is_computed_attribute, is_aggregation |
| Resolution | `ModuleInput` → `InputSource` | source_type ("entry_point"\|"module_output"), producer_channel, param_group, qualified_name |
| Resolution | `EntryPoint` | qualified_name, entry_type (DESIGN_ATTRIBUTE\|LIBRARY_DEFAULT\|USAGE_LITERAL), default_value |

---

## Proposed Design

### 1. File Architecture

```
┌──────────────────────────────────────────────────────────┐
│ <style>  (~12KB)                                         │
│   CSS variables, layout, diagram styles,                 │
│   animations, step indicators, responsive rules          │
├──────────────────────────────────────────────────────────┤
│ <body>  (~40KB HTML)                                     │
│   ┌─── Sidebar Navigation (fixed, 240px)                │
│   ├─── Glossary Overlay (hidden by default)              │
│   └─── Main Content (scrollable)                         │
│        ├── Hero: "How sysml-codegen works"               │
│        ├── Act 1: Meet the Solar Plant                   │
│        │    ├── <div id="hierarchy-diagram">             │
│        │    └── <div id="big-question-anim">             │
│        ├── Act 2: The Pipeline (7 steps)                 │
│        │    ├── <div id="pipeline-overview">             │
│        │    ├── <div id="step-1-extract">                │
│        │    ├── <div id="step-2-registry">               │
│        │    ├── <div id="step-3-trace">                  │
│        │    ├── <div id="step-35-hierarchy">             │
│        │    ├── <div id="step-4-classify">               │
│        │    ├── <div id="step-45-computed">              │
│        │    ├── <div id="step-5-modules">                │
│        │    ├── <div id="step-55-registry-build">        │
│        │    ├── <div id="step-6-sort">                   │
│        │    └── <div id="step-7-render">                 │
│        ├── Act 3: Why The Hard Parts Work                │
│        │    ├── <div id="template-demo">                 │
│        │    ├── <div id="aggregation-demo">              │
│        │    └── <div id="dual-resolution-demo">          │
│        └── Act 4: The Full Graph                         │
│             ├── <div id="dag-diagram">                   │
│             └── <div id="generated-code">                │
├──────────────────────────────────────────────────────────┤
│ <script>  (~80KB JS)                                     │
│   ┌─── MODEL_DATA  (~25KB)                               │
│   │    Hierarchy, pipeline step data, modules, edges,    │
│   │    binding examples, registry examples, factory      │
│   │    examples, entry point examples                    │
│   ├─── Shared Utilities (~3KB)                           │
│   │    renderModuleNode(), traceUpstream(),              │
│   │    highlightElements(), dimElements(),               │
│   │    renderDataPanel(), renderStepConnector()          │
│   ├─── ZoomPanController (~3KB)                          │
│   ├─── NavigationController (~2KB)                       │
│   ├─── GlossaryController (~2KB)                         │
│   ├─── HierarchyRenderer (~8KB)                          │
│   ├─── PipelineStepRenderer (~15KB)                      │
│   ├─── TemplateExpansionDemo (~6KB)                      │
│   ├─── AggregationDemo (~6KB)                            │
│   ├─── DualResolutionDemo (~8KB)                         │
│   ├─── DAGRenderer (~10KB)                               │
│   └─── init() (~1KB)                                     │
└──────────────────────────────────────────────────────────┘
```

**Estimated total**: ~200-250KB (well under 500KB budget). Larger than the prior design (~150KB) because Act 2's seven pipeline steps add significant content.

**JS organization**: Sequential class declarations with block-comment separators (`// ═══ DATA ═══`, etc.). No modules, no bundler. Each class reads from `MODEL_DATA` and manipulates the DOM. Classes communicate through DOM events only — no cross-class method calls.

### 2. Shared Infrastructure

#### 2a. ZoomPanController

Carried forward from prior design. Reusable class for any SVG-containing `<div>`:

- **Zoom**: Mouse wheel → scale SVG `viewBox`. Anchored to cursor position. Range 0.3×–5×.
- **Pan**: Click-drag on non-interactive elements → translate viewBox origin.
- **Keyboard**: `+`/`-` zoom, arrows pan, `0` reset.
- **Minimap** (on DAG only): Small inset SVG showing full graph with viewport rectangle.

```js
class ZoomPanController {
  constructor(containerEl, svgEl, options = {}) { /* ... */ }
  // State: viewBox {x, y, w, h}, scale
  // Methods: zoomTo(scale, cx, cy), panBy(dx, dy), reset(), fitAll()
}
```

Attached to: hierarchy diagram (Act 1), DAG diagram (Act 4). Smaller demos use CSS overflow-auto.

#### 2b. Shared Rendering Utilities

```js
// Render a pipeline module node. Reused by hierarchy (cost_model boxes),
// aggregation demo (tier boxes), DAG (all 35 modules).
function renderModuleNode(svgParent, { id, shortName, family, x, y, collapsed, inputs, outputs })
  → SVGGElement

// BFS backward through MODEL_DATA.edges. Returns upstream module IDs + edge indices.
// Reused by Act 1 "big question" animation AND Act 4 trace mode.
function traceUpstream(startModuleId, edges)
  → { moduleIds: Set<string>, edgeIndices: Set<number> }

// Highlight/dim SVG elements by data-id attribute.
function highlightElements(svgRoot, ids, highlightColor)
function dimElements(svgRoot, keepIds)

// NEW: Render a data panel showing a Pydantic model with concrete field values.
// Used by every pipeline step in Act 2.
function renderDataPanel(container, { title, modelName, fields, highlightFields })
  → HTMLDivElement

// NEW: Render an arrow connector between two step panels with a label.
function renderStepConnector(container, { fromEl, toEl, label })
  → SVGLineElement
```

#### 2c. Sidebar Navigation

Fixed left sidebar (240px). Updated structure for 4 acts:

```html
<nav id="sidebar">
  <div class="nav-title">sysml-codegen pipeline</div>

  <a href="#act1" class="nav-act">1. Meet the Solar Plant</a>
  <a href="#act1-hierarchy" class="nav-sub">The Part Hierarchy</a>
  <a href="#act1-question" class="nav-sub">The Big Question</a>

  <a href="#act2" class="nav-act">2. The Pipeline</a>
  <a href="#step-1" class="nav-step">Step 1: Extract</a>
  <a href="#step-2" class="nav-step">Step 2: Build Registry</a>
  <a href="#step-3" class="nav-step">Step 3: Trace Dependencies</a>
  <a href="#step-35" class="nav-step">Step 3.5: Hierarchy</a>
  <a href="#step-4" class="nav-step">Step 4: Classify Entries</a>
  <a href="#step-45" class="nav-step">Step 4.5: Computed Attrs</a>
  <a href="#step-5" class="nav-step">Step 5: Build Modules</a>
  <a href="#step-55" class="nav-step">Step 5.5: Build Registry</a>
  <a href="#step-6" class="nav-step">Step 6: Sort + Validate</a>
  <a href="#step-7" class="nav-step">Step 7: Render</a>

  <a href="#act3" class="nav-act">3. Why The Hard Parts Work</a>
  <a href="#act3-template" class="nav-sub">Template Instantiation</a>
  <a href="#act3-aggregation" class="nav-sub">Aggregation Decomposition</a>
  <a href="#act3-resolution" class="nav-sub">Dual Resolution</a>

  <a href="#act4" class="nav-act">4. The Full Graph</a>
  <a href="#act4-dag" class="nav-sub">Computation Graph</a>
  <a href="#act4-code" class="nav-sub">Generated Code</a>

  <button id="glossary-btn">SysML Glossary</button>
</nav>
```

The `.nav-step` items use a small step-number badge (colored circle with step number). Current step highlights via `IntersectionObserver`.

#### 2d. Glossary Overlay

Carried forward from prior design. Slide-in right panel (400px), 8 SysML concepts with visual examples from the solar battery model:

| Term | Example | Visual |
|------|---------|--------|
| PartDefinition | `part def 'PV Module'` | Blueprint icon (dotted border) |
| PartUsage | `part pv_module : 'PV Module' [20]` | Solid box in container |
| CalcDefinition | `calc def PVModuleCostCalc` | f(x)=y icon |
| CalcUsage | `calc cost_model : PVModuleCostCalc` | Function wired into part |
| Binding | `in wattage = wattage` | Arrow from attr to param |
| `:>>` Redefinition | `:>> capital_cost = cost_model.total_cost` | Equals + redirect arrow |
| Multiplicity `[N]` | `part pv_module [module_count]` | Stacked boxes |
| `sum()` Aggregation | `sum(pv_module.capital_cost)` | Sigma over stack |

#### 2e. Color Palette

Carried forward + new pipeline-step colors:

```css
:root {
  /* Module families (consistent across ALL diagrams) */
  --f1-bg: #DBEAFE; --f1-border: #2563EB; --f1-text: #1E40AF;  /* Blue — CalcUsage */
  --f2-bg: #EDE9FE; --f2-border: #7C3AED; --f2-text: #5B21B6;  /* Purple — Computed Attr */
  --f3-bg: #FFEDD5; --f3-border: #EA580C; --f3-text: #9A3412;  /* Orange — Aggregation */

  /* Part hierarchy levels */
  --plant-bg: #F0FDF4; --plant-border: #16A34A;
  --subsys-bg: #FEF9C3; --subsys-border: #CA8A04;
  --comp-bg: #F1F5F9; --comp-border: #64748B;

  /* Entry point types */
  --ep-design: #FDE68A;    /* Amber — DESIGN_ATTRIBUTE */
  --ep-library: #E0E7FF;   /* Indigo — LIBRARY_DEFAULT */
  --ep-literal: #FEE2E2;   /* Rose — USAGE_LITERAL */

  /* Pipeline step indicators */
  --step-extract: #059669;    /* Emerald */
  --step-registry: #0891B2;   /* Cyan */
  --step-trace: #4F46E5;      /* Indigo */
  --step-classify: #7C3AED;   /* Violet */
  --step-modules: #DB2777;    /* Pink */
  --step-sort: #EA580C;       /* Orange */
  --step-render: #16A34A;     /* Green */

  /* Resolution paths */
  --path-backtracker: #2563EB;  /* Blue */
  --path-formula: #7C3AED;      /* Purple — FORMULA attribute map */
  --path-resolve-input: #EA580C; /* Orange — Aggregation resolve_input() */

  /* Structural */
  --edge-color: #94A3B8;
  --edge-highlight: #2563EB;
  --dim-opacity: 0.15;
  --canvas-bg: #F8FAFC;
}
```

### 3. Act 1: "Meet the Solar Plant"

Carried forward from prior design with minimal changes.

#### 3a. Hierarchy Diagram

2D nested rectangles showing containment. SVG canvas ~2400×1600px with ZoomPanController.

```
┌──────────────── Solar Battery Plant ──────────────────────────────────┐
│                                                                        │
│  ┌── Solar Array ──────────┐  ┌── Battery System ──┐  ┌── Site ──┐   │
│  │ ┌─PV Module─┐ ×20      │  │ ┌─Battery Pack─┐×8 │  │ ┌─Rack─┐ │   │
│  │ │ watt:400  │           │  │ │ cap:5kWh    │    │  │ │      │ │   │
│  │ │ ┌cost_mod┘│           │  │ │ ┌cost_model┘│    │  │ │┌c_m┘ │ │   │
│  │ └──────────┘            │  │ └─────────────┘    │  │ └──────┘ │   │
│  │ ┌─Inverter──┐ ×4       │  │ ┌─Hybrid Inv──┐    │  │ ┌─Panel┐ │   │
│  │ │ ┌cost_mod┘│           │  │ │ ┌cost_model┘│    │  │ │┌c_m┘ │ │   │
│  │ └──────────┘            │  │ └─────────────┘    │  │ └──────┘ │   │
│  │ ┌─Array BOS─┐           │  │ ┌─Battery BOS─┐    │  │ ┌─Perm─┐ │   │
│  │ │ ┌cost_mod┘│           │  │ │ ┌cost_model┘│    │  │ │┌c_m┘ │ │   │
│  │ └──────────┘            │  │ └─────────────┘    │  │ └──────┘ │   │
│  │ Σ capital_cost = ...    │  │ Σ capital_cost=... │  │ Σ cap=...│   │
│  └─────────────────────────┘  └────────────────────┘  └──────────┘   │
│                                                                        │
│  Σ capital_cost = solar_array + battery_system + site_infra           │
│  ┌─ System Calcs ────────────────────────────────────────────┐       │
│  │ energy_prod → ann_om → ann_financial → LCOE ← ann_fuel   │       │
│  └───────────────────────────────────────────────────────────┘       │
└────────────────────────────────────────────────────────────────────────┘
```

Features: multiplicity badges (×N stacked visual), hover to highlight component + cost model, aggregation formulas shown in muted font at assembly level.

Narrative callouts positioned inside the diagram container with connector lines to relevant elements. Scroll-driven reveal via `IntersectionObserver`.

#### 3b. "The Big Question" Animation

"Show me the path to LCOE" button triggers animated trace-back:

1. LCOE pulses → traces to `annualized_financial` → to `plant.capital_cost`
2. `plant.capital_cost` → three subsystem aggregations
3. Each subsystem → leaf `cost_model` modules
4. All highlighted; rest dims to 15%

Uses shared `traceUpstream()` + `highlightElements()` + `dimElements()`. CSS `@keyframes` + JS `setTimeout` sequencing, ~600ms per step.

Callout after animation: "To compute LCOE, the system needs to execute 35 modules in the right order. Here's the 7-step pipeline that makes it happen."

### 4. Act 2: "The Pipeline" — 7-Step Proof

This is the new centerpiece. Each pipeline step gets its own section showing concrete data from the LCOE computation.

#### 4a. Pipeline Overview Diagram

A horizontal strip showing the 7 steps as connected boxes (not the detail — just the map):

```
┌──────┐   ┌──────┐   ┌──────┐   ┌──────┐   ┌──────┐   ┌──────┐   ┌──────┐
│  1   │──→│  2   │──→│  3   │──→│  4   │──→│  5   │──→│  6   │──→│  7   │
│Extract│   │Regis.│   │Trace │   │Class.│   │Build │   │Sort  │   │Render│
└──────┘   └──────┘   └──────┘   └──────┘   └──────┘   └──────┘   └──────┘
     ↓           ↓          ↓          ↓          ↓          ↓          ↓
  CalcDef    Output    Backtrack   Entry     Pipeline   Computation  Generated
  CalcUsage  Registry  Result     Points    Modules    Graph        Code
  PartDef
```

Sub-steps (3.5, 4.5, 5.5) shown as smaller boxes below their parent step, with connector arrows showing the ordering constraints.

Each step box is **clickable** — scrolls to the detailed section for that step. Current step highlights in the sidebar. The strip remains visible as a sticky header while scrolling through Act 2 sections.

**Ordering constraint callouts**: Three red "MUST precede" annotations on the overview:
- "3.5 → 4: Virtual binding rewrite must happen before entry point classification (bindings are mutated in place)"
- "4.5 → 5: FORMULA removal from design attrs prevents false entry points"
- "5.5 → 6: Backtracker needs the OutputRegistry for resolution"

#### 4b. Pipeline Step Layout Template

Every pipeline step section uses the same layout pattern:

```
┌─ Step N: [Name] ─────────────────────────────────────────────────────┐
│                                                                       │
│  [1-2 sentence plain-English explanation of what this step does]     │
│                                                                       │
│  ┌─ Input ──────────────────┐     ┌─ Output ─────────────────────┐  │
│  │ ModelName                 │     │ ModelName                     │  │
│  │ ─────────────────────     │ ──→ │ ─────────────────────         │  │
│  │ field_1: value            │     │ field_1: value                │  │
│  │ field_2: value            │     │ field_2: value                │  │
│  │ field_3: [expand...]      │     │ field_3: [expand...]          │  │
│  └───────────────────────────┘     └───────────────────────────────┘  │
│                                                                       │
│  [Why this step exists — 1-2 sentences]                              │
│                                                                       │
└───────────────────────────────────────────────────────────────────────┘
```

The "Input" and "Output" panels are rendered by `renderDataPanel()`. Fields show concrete values from the solar battery example. Array/object fields are collapsible (click to expand). Highlighted fields draw attention to the key transformation.

**Trace module**: To make the pipeline concrete, we trace **one module** (PV Module `cost_model`) through ALL 7 steps. This module is highlighted in amber wherever it appears in the data panels. The reader follows one piece of data from SysML source to generated code.

Additionally, each step briefly notes what happens to the ~35 other modules at that step (e.g., "The same extraction happens for all 14 CalcDefs and their usages").

#### 4c. Step 1: Extract

**Explanation**: "Parse .sysml files into structured data models. Each CalcDef becomes a `CalculationDefinitionData`; each calc usage becomes a `CalcUsageData` with binding info."

**Input panel**: Three .sysml file names with line counts.

**Output panel (traced module)**:

```
CalculationDefinitionData
───────────────────────────
name: "PVModuleCostCalc"
qualified_name: "SolarBatteryLibrary::PVModuleCostCalc"
input_attributes: [
  {name: "wattage", python_type: "float"},
  {name: "efficiency", python_type: "float"},
  {name: "cost_per_watt", python_type: "float", default: 1.07},
  ...
]
output_attributes: [
  {name: "material_cost", python_type: "float"},
  {name: "total_cost", python_type: "float"},
  ...
]

CalcUsageData (template)
───────────────────────────
instance_name: "cost_model"
calc_def_name: "PVModuleCostCalc"
is_template: true ← lives in PartDef, not design
owning_part_def_qn: "SolarBatteryLibrary::'PV Module'"
bindings: [
  {param: "wattage", source: "wattage", type: CHAIN},
  {param: "efficiency", source: "efficiency", type: CHAIN},
  {param: "cost_per_watt", source: (unbound), type: UNBOUND},
]
```

**Why this step exists**: "The raw SysML model is an AST. Extraction produces typed, validated data models that downstream steps can consume without touching the parser."

**Also extracted** (collapsed expandable): Summary showing 14 CalcDefs, 14 CalcUsages (5 system-level direct + 9 template), 13 PartDefs.

#### 4d. Step 2: Build Registry (OutputRegistry overview — detailed build in Step 5.5)

**Explanation**: "Catalog every output channel name into three typed registries so that later steps can look up where a value comes from. The `OutputRegistry` uses typed identifiers — `ScopedKey`, `SysMLQN`, and `CanonicalChannel` — to prevent key-format confusion."

**Output panel**: The OutputRegistry conceptual structure, showing typed registry entries for the traced module:

```
OutputRegistry (partial — PV Module cost_model only)
─────────────────────────────────────────────
_scoped registry (ScopedKey → CanonicalChannel):
  "solar_battery_plant.solar_array.pv_module.cost_model.total_cost"
  → "...pv_module__cost_model__total_cost"

_canonical set (membership):
  "...pv_module__cost_model__total_cost" ✓

(SysML QN and alias registries populated in later phases)
```

**Why this step exists**: "Bindings in SysML use scope-relative names (`cost_model.total_cost`). But multiple parts can have a `cost_model` — the typed registry only registers hierarchy-scoped `ScopedKey` entries, making ambiguity impossible by construction."

**Scope problem callout**: Visual showing that unscoped names like `cost_model.total_cost` are not registered at all — ambiguity is prevented by construction. Across 6 models and 150 bindings, unscoped keys had zero resolution hits while causing 10+ collisions. `ScopedKey` (hierarchy-qualified, e.g., `solar_battery_plant.solar_array.pv_module.cost_model.total_cost`) is unique by SysML ownership semantics.

Note: "Step 2 registers into the scoped registry and `_canonical` set. The alias registry is populated in Step 5.5 (Phases 2–4) after all module types are known."

#### 4e. Step 3: Trace Dependencies (Backtracker DFS)

**Explanation**: "Starting from LCOE, trace backward through bindings to find every module needed. At each binding, decide: is this an upstream module (recurse) or an external input (stop)?"

**Visual**: A DFS tree diagram showing the backtracker's traversal:

```
LCOE
├── annualized_financial ──────→ (recurse: found in registry)
│   ├── total_capex = capital_cost ──→ plant.capital_cost (F3)
│   │   ├── solar_array.capital_cost ──→ (F3, recurse)
│   │   │   ├── pv_module.cost_model ──→ (F1, recurse)
│   │   │   │   ├── wattage ──→ STOP: entry point (DESIGN_ATTRIBUTE)
│   │   │   │   ├── efficiency ──→ STOP: entry point (DESIGN_ATTRIBUTE)
│   │   │   │   └── cost_per_watt ──→ STOP: entry point (LIBRARY_DEFAULT)
│   │   │   └── ...
│   │   └── ...
│   ├── discount_rate ──→ STOP: entry point (not in registry)
│   └── plant_lifetime ──→ STOP: entry point
├── energy_production ──→ (recurse)
└── ...
```

The DFS tree is color-coded: blue for "recurse" decisions, amber for "stop — entry point" decisions. The traced module (`pv_module.cost_model`) is highlighted.

**Output panel**:

```
BacktrackingResult
──────────────────
required_usages: [14 CalcUsageData in topological order]
binding_resolutions: {
  "...pv_module__cost_model|wattage":
    BindingResolution(ENTRY_POINT, qn="...wattage")
  "...pv_module__cost_model|efficiency":
    BindingResolution(ENTRY_POINT, qn="...efficiency")
  "...annualized_financial|total_capex":
    BindingResolution(MODULE_OUTPUT, channel="...capital_cost__capital_cost")
  ... (N more)
}
entry_points: {"...wattage", "...efficiency", "...cost_per_watt", ...}
```

**Why this step exists**: "You can't build the pipeline without knowing which modules are needed and how they're wired. The backtracker's DFS discovers both simultaneously — resolution is embedded in traversal because the resolution result determines whether to recurse."

#### 4f. Step 3.5: Hierarchy + Virtual Binding Rewrite

**Explanation**: "Template calc usages carry generic bindings. The virtual binding rewrite scopes them to the design instance and overwrites bindings with concrete design values."

**Visual**: Before/after of the traced module's bindings. This is a compact version of Act 3a's full treatment.

```
BEFORE (template binding):              AFTER (virtual copy):
  in wattage = wattage (CHAIN)     →      in wattage = 400.0 (LITERAL)
  in efficiency = efficiency (CHAIN) →    in efficiency = 0.21 (LITERAL)
  in cost_per_watt = (UNBOUND)     →      in cost_per_watt = (UNBOUND) — unchanged
```

**Ordering constraint callout** (red): "This MUST happen before Step 4. If you classify entry points before rewriting bindings, `wattage` would be classified as LIBRARY_DEFAULT (unbound in the template) instead of DESIGN_ATTRIBUTE (literal 400.0 from the design)."

Also shows: `HierarchyExtractionResult` with multiplicities (`pv_module[20]`), aggregation expressions, and redefinition data. These are used by Step 5 (module factories).

#### 4g. Step 4: Classify Entry Points

**Explanation**: "Every unresolved parameter becomes an entry point — a value the user provides via JSON input. Classification determines the type and default value."

**Visual**: A classification decision tree for three examples:

```
Parameter: pv_module__cost_model__wattage
  ├─ Has design attribute literal? YES (400.0 from :>> wattage = 400.0)
  └─ → DESIGN_ATTRIBUTE, default=400.0

Parameter: pv_module__cost_model__cost_per_watt
  ├─ Has design attribute literal? NO
  ├─ Has calc def default? YES (1.07)
  └─ → LIBRARY_DEFAULT, default=1.07

Parameter: (hypothetical usage literal example)
  ├─ Has design attribute? NO
  ├─ Has calc def default? NO
  ├─ Has literal in usage binding? YES
  └─ → USAGE_LITERAL
```

**Precedence rule callout**: "DESIGN_ATTRIBUTE > LIBRARY_DEFAULT > USAGE_LITERAL. Design intent always wins."

**Output panel**: List of `EntryPoint` instances with types color-coded (amber=DESIGN, indigo=LIBRARY, rose=LITERAL).

#### 4h. Step 4.5: Computed Attributes

**Explanation**: "Some PartDef attributes have inline expressions (like `p_net_kw = p_net_mw * 1000`). If all references are sibling attributes, this becomes a FORMULA — a synthetic pipeline module. These must be identified and removed from design attributes before module building."

**Visual**: Shows `p_net_kw` being classified as FORMULA:

```
Attribute: p_net_kw on Solar Battery Plant
Expression: p_net_mw * 1000
References: [p_net_mw] — all siblings ✓
Classification: FORMULA → generates synthetic F2 module

Side effect: p_net_kw removed from design_attributes
  (prevents it from being falsely classified as a DESIGN_ATTRIBUTE entry point)
```

**Ordering constraint callout** (red): "This MUST happen before Step 5. If `p_net_kw` stays in design_attributes, the module factory would create a DESIGN_ATTRIBUTE entry point for it, when it should actually come from the F2 FORMULA module's output."

#### 4i. Step 5: Build Modules — Three Pure Factories

**Explanation**: "Each pipeline module is built by a pure factory function. The factory takes extraction-layer data, resolves inputs, and returns a `(PipelineModule, dict[str, EntryPoint])` tuple. No side effects, no mutation of shared state."

This is the factory visualization — the core implementation pattern the spec demands (FR-5).

**Three-column layout** showing one factory call of each type:

```
┌─ CalcUsage Factory ───────────────────────────────────────────────────┐
│                                                                        │
│  INPUT:                                                                │
│  CalcUsageData(instance_name="cost_model", ...)                       │
│  + CalculationDefinitionData(name="PVModuleCostCalc", ...)            │
│  + binding_resolutions from Step 3                                     │
│                                                                        │
│  PURE FUNCTION (no side effects):                                      │
│  build_calc_usage_module(usage, calc_def, binding_resolutions, ...)    │
│      │                                                                 │
│      ▼                                                                 │
│  RETURNS TUPLE:                                                        │
│  ┌─ PipelineModule ─────────────────────────┐                         │
│  │ name: "...pv_module__cost_model"          │                         │
│  │ module_type: "PVModuleCostCalcModule"     │                         │
│  │ is_computed_attribute: false               │                         │
│  │ is_aggregation: false                      │                         │
│  │ inputs: [                                  │                         │
│  │   ModuleInput("wattage",                   │                         │
│  │     source: InputSource(                   │                         │
│  │       type: "entry_point",                 │                         │
│  │       param_group: "design_params",        │                         │
│  │       qn: "...wattage")),                  │                         │
│  │   ModuleInput("cost_per_watt",             │                         │
│  │     source: InputSource(                   │                         │
│  │       type: "entry_point",                 │                         │
│  │       param_group: "library_params",       │                         │
│  │       qn: "...cost_per_watt")),            │                         │
│  │   ...                                      │                         │
│  │ ]                                           │                         │
│  │ outputs: [                                  │                         │
│  │   ModuleOutput("root", "float",            │                         │
│  │     channel: "...cost_model__total_cost")   │                         │
│  │ ]                                           │                         │
│  └─────────────────────────────────────────────┘                       │
│  ┌─ dict[str, EntryPoint] ──────────────────┐                         │
│  │ "...wattage": EntryPoint(DESIGN_ATTR, 400.0)                       │
│  │ "...cost_per_watt": EntryPoint(LIBRARY_DEFAULT, 1.07)              │
│  └──────────────────────────────────────────┘                          │
└────────────────────────────────────────────────────────────────────────┘
```

Similar panels for FORMULA factory (`build_formula_module`) and Aggregation factory (`build_aggregation_module`), each with a concrete example and return tuple.

**Key callout**: "Every factory returns a tuple. Entry points are collected as a separate return value — not mutated as a side effect on shared state. This means each factory can be tested in isolation with no mocks."

#### 4j. Step 5.5: Build OutputRegistry (4-Phase Protocol)

**Explanation**: "Now that all module types are known, the full OutputRegistry is built in 4 phases. Each phase adds a different kind of alias."

**Visual**: The registry growing phase by phase (same approach as prior design's Act 2c, but positioned here in the pipeline sequence). Interactive table with rows appearing per phase:

| Phase | Registry | Key Type | Example Key | Points To |
|-------|----------|----------|-------------|-----------|
| 1a | `_scoped` | `ScopedKey` | `solar_battery_plant.solar_array.pv_module.cost_model.total_cost` | `...pv_module__cost_model__total_cost` |
| 1a | `_canonical` | `CanonicalChannel` | `...pv_module__cost_model__total_cost` | (membership set) |
| 1b | `_scoped` | `ScopedKey` | `solar_battery_plant.solar_array.capital_cost` | `...solar_array__capital_cost__capital_cost` |
| 1c | `_sysml_qn` | `SysMLQN` | `SolarBatteryLibrary::Solar_Battery_Plant::p_net_kw` | `...p_net_kw__p_net_kw` |
| 2 | `_alias` | `ScopedKey` | `pv_module.capital_cost` (CHAIN) | `...pv_module__cost_model__total_cost` |
| 3 | `_alias` | `ScopedKey` | *(none in this model — EXPOSE_PURE)* | — |
| 4 | `_alias` | `ScopedKey` | *(none in this model — transitive)* | — |

Phases 3 and 4 are shown as labeled empty rows: "No EXPOSE_PURE/transitive aliases in this model — these come from computed attribute passthroughs and multi-hop :>> chains."

Note about phase ordering enforcement: Phases 2–4 register into the `_alias` registry. The `register_alias()` API enforces that the target `CanonicalChannel` must already exist in `_canonical` — rejecting out-of-order registration attempts.

**Ordering constraint callout** (red): "This MUST happen before Step 6. The backtracker (CalcUsage resolution) uses this registry. Aggregation factory resolution (via `resolve_input()`) and FORMULA attribute map resolution also use it."

#### 4k. Step 6: Sort + Validate

**Explanation**: "Topologically sort all modules (Kahn's algorithm, O(V+E)). Validate that every `producer_channel` in every `InputSource` resolves to a declared `ModuleOutput.channel_name`."

**Visual**: A small animation showing Kahn's algorithm processing:

1. Start: identify modules with no incoming edges (Tier 0 leaf cost_models)
2. Remove them, decrement edge counts
3. Newly zero-count modules enter the queue (Tier 1, 2, ...)
4. Final order emerges

The traced module (`pv_module__cost_model`) gets `execution_order: 0` (it has no upstream module dependencies).

**Validation callout**: "If any `producer_channel` doesn't match a declared output, the design has a bug. This is the pipeline's compile-time error — catch wiring problems before any code runs."

**Output panel**: The `ComputationGraph` — the final product:

```
ComputationGraph
─────────────────
modules: [35 PipelineModules in execution order]
entry_point_groups: [
  ParameterGroup("design_params", [...12 EntryPoints...]),
  ParameterGroup("library_params", [...8 EntryPoints...]),
]
execution_order: ["...pv_module__cost_model", "...inv_cost_model", ..., "...lcoe"]
```

**ComputationGraph as boundary callout** (the single source of truth visualization from FR-3):

```
 Steps 1-6                          Step 7
┌──────────────────┐   ┌─────────────────────────────┐
│ Extract          │   │ Generate                     │
│ Analyze    ─────►│   │                              │
│ Resolve          │   │ ┌── pipeline.yaml ──────┐   │
│                  │   │ │ reads ComputationGraph │   │
│ Produces:        │   │ └───────────────────────┘   │
│ ComputationGraph │──►│ ┌── modules.py ─────────┐   │
│                  │   │ │ reads ComputationGraph │   │
│ Nothing else     │   │ └───────────────────────┘   │
│ crosses this     │   │ ┌── entry_point.py ─────┐   │
│ boundary.        │   │ │ reads ComputationGraph │   │
│                  │   │ └───────────────────────┘   │
└──────────────────┘   └─────────────────────────────┘

"Generation consumes ONLY the ComputationGraph.
 No back-references to extraction models."
```

#### 4l. Step 7: Render (Generated Output Traceability)

**Explanation**: "Jinja2 templates render the ComputationGraph into Python, YAML, and JSON. Every generated line traces back to a ComputationGraph field."

**Three code panels** with traced annotations (same as prior design's §7c, but with explicit field traceability per FR-11):

**Pipeline YAML** (traced module):
```yaml
# PipelineModule.name → YAML key
solarbatterydesign__solar_battery_plant__solar_array__pv_module__cost_model:
  # PipelineModule.module_type → module_type field
  module_type: solarbatterylibrary.PVModuleCostCalcModule
  inputs:
    # ModuleInput.param_name → input key
    # InputSource.source_type=entry_point → reads from JSON
    wattage: { source: design_params, field: ...wattage }
    cost_per_watt: { source: library_params, field: ...cost_per_watt }
  outputs:
    # ModuleOutput.channel_name → output channel
    total_cost: { channel: ...pv_module__cost_model__total_cost }
```

Each annotation (right-aligned, in muted gray) shows which `ComputationGraph` → `PipelineModule` → field produced that line.

**JSON input** (traced module's entry points):
```json
// ParameterGroup.json_filename → file name
// design_params.json:
{
  // EntryPoint.qualified_name → JSON key
  // EntryPoint.default_value → default value
  "...pv_module__cost_model__wattage": 400.0,
  "...pv_module__cost_model__efficiency": 0.21
}
```

Each panel has a "Click to highlight this module in the graph" link (scrolls to Act 4 DAG and triggers trace mode).

### 5. Act 3: "Why The Hard Parts Work"

Three deep-dive sections, each proving a specific claim about the refactored design.

#### 5a. Template Instantiation (Virtual Binding Rewrite)

Carried forward from prior design's §4, updated to match refactored terminology.

**3-panel horizontal layout** with step-synced callouts:

Panel 1 ("The Recipe"): `PVModuleCostCalc` inside `'PV Module'` PartDef, dotted border (blueprint). Shows template bindings (`in wattage = wattage` as CHAIN).

Panel 2 ("The Design"): Design instance `solar_battery_plant > solar_array > pv_module : 'PV Module' [20]` with `:>> wattage = 400.0` highlighted in amber.

Panel 3 ("The Virtual Copy"): Animated transition showing:
- Qualified name building up segment by segment
- Three mutation cases:
  - LITERAL override: `wattage` binding → strikethrough → `400.0` (amber)
  - CHAIN override: (if applicable in this example)
  - No match: `cost_per_watt` stays UNBOUND (becomes LIBRARY_DEFAULT entry point)

Stepper control (Step 1/2/3) or Play button.

#### 5b. Aggregation Decomposition

Carried forward from prior design's §5, updated with SumTerm/SingletonTerm/LocalTerm terminology.

**4-tier vertical stack** (bottom to top):

```
TIER 4:    LCOE
TIER 3:    Plant capital_cost = SA + BS + SI
TIER 2:    SA capital_cost = Σ(pv×20) + Σ(inv×4) + bos + misc
TIER 1:    [PV cost] [Inv cost] [BOS cost] ...
```

**Step 1**: Color-coded SysML expression:
- `sum(pv_module.capital_cost)` → **SumTerm** (red)
- `array_bos.capital_cost` → **SingletonTerm** (blue)
- `misc_hardware_cost` → **LocalTerm** (green)

**Step 2**: Animate SumTerm → parametric multiply:
- `sum(pv_module.capital_cost)` → `pv_module_capital_cost × module_count`
- Visual: `sum(...)` fades, multiply icon appears
- Badge: "module_count = 20 → becomes an entry point in JSON"

**Step 3**: Show LocalTerm resolution (3 strategies):
- Strategy 1: Sibling aggregation output? → No
- Strategy 2: EXPOSE_PURE alias? → No
- Strategy 3: Entry point fallback → Yes, creates DESIGN_ATTRIBUTE entry point

If a literal `:>>` redefinition exists, show literal value propagation instead.

**Step 4**: Cascade rollup from leaf → subsystem → plant → LCOE.

**Interactive slider**: `module_count` (1-50, default 20). Shows multiplier changing.

#### 5c. Dual Resolution Architecture

This is the most important "prove it works" section. **NEW — not in the prior design.**

**Layout**: Three-panel comparison (or 2-panel with FORMULA as a distinct callout between them):

```
┌──────────────────────────┐  ┌───────────────────────────┐  ┌───────────────────────────────┐
│ MECHANISM 1: Backtracker │  │ MECHANISM 2: Attribute Map│  │ MECHANISM 3: resolve_input()  │
│ (CalcUsage modules)      │  │ (FORMULA modules)         │  │ (Aggregation modules)         │
│                          │  │                           │  │                               │
│ Context: DFS traversal.  │  │ Context: Pre-computed     │  │ Context: Post-DFS factory.    │
│ Type-directed dispatch:  │  │ during computed attribute  │  │ Uses strategy chain.          │
│ CHAIN → scoped registry  │  │ analysis (Step 4.5).      │  │                               │
│ REFERENCE → SysML QN reg │  │ No runtime strategy chain │  │ AGG_STRATEGIES order:         │
│                          │  │ — answer already known.   │  │ A: ScopedRegistryLookup       │
│ Reference:               │  │                           │  │ C: ChainRedefinitionFollow    │
│ "capital_cost" on        │  │ Reference:                │  │ D: DesignAttributeLookup      │
│ annualized_financial     │  │ "p_net_mw" on p_net_kw    │  │                               │
│                          │  │                           │  │ Reference:                    │
│ ┌── Type dispatch ─────┐│  │ ┌── Attribute map ──────┐ │  │ "capital_cost" as agg input   │
│ │ CHAIN binding (no ::) ││  │ │ p_net_mw → scoped     │ │  │                               │
│ │ → scoped registry     ││  │ │ registry lookup       │ │  │ ┌── Strategy A: Scoped ────┐ │
│ │ → ScopedKey lookup    ││  │ │ → pre-computed match  │ │  │ │ ScopedRegistryLookup     │ │
│ │ → MATCH: plant agg    ││  │ └───────────────────────┘ │  │ │ → ScopedKey lookup       │ │
│ └───────────────────────┘│  │                           │  │ │ → MATCH: plant agg       │ │
│                          │  │ Output:                   │  │ └──────────────────────────┘ │
│ Output:                  │  │ InputSource(module_output) │  │                               │
│ BindingResolution(       │  │                           │  │ Output:                       │
│   MODULE_OUTPUT,         │  │                           │  │ InputSource(module_output)    │
│   channel: "...")        │  │                           │  │                               │
│                          │  │                           │  │                               │
│ ════════════════════════ │  │ ═════════════════════════ │  │ ═════════════════════════════ │
│ SAME CHANNEL.            │  │ SAME CHANNEL.             │  │ SAME CHANNEL.                 │
│ (BindingResolution)      │  │ (InputSource)             │  │ (InputSource)                 │
└──────────────────────────┘  └───────────────────────────┘  └───────────────────────────────┘
```

**Below the panels**: Explanation of why they can't merge:

"The **backtracker** resolves during DFS traversal — it needs the resolution result to decide whether to recurse deeper or stop. You can't separate 'what to resolve' from 'what to traverse next.' **FORMULA** inputs are resolved during computed attribute analysis (Step 4.5), before module building begins — there's no strategy chain to run because the answer is already known from the attribute map. **Aggregation** modules use a standalone strategy chain (`resolve_input()`) because their references span scopes. All three mechanisms query the same typed registries (scoped, SysML QN, alias), ensuring consistency (REQ-DRA-04)."

**Strategy chain detail** (for Mechanism 3 — Aggregation only):

```
resolve_input(ref, ctx, strategies) → InputSource
───────────────────────────────────
AGG_STRATEGIES order:
  A: ScopedRegistryLookup      ──→ ScopedKey (hierarchy-scoped, queries scoped + alias registries)
  C: ChainRedefinitionFollow   ──→ :>> chains, cycle-safe
  D: DesignAttributeLookup     ──→ bare name match against design attrs
```

ChainRedefinitionFollow is promoted to position C (was D in earlier designs) because aggregation inputs almost always resolve through `:>>` redefinition chains.

Each strategy box is clickable — expands to show a concrete example of when that strategy fires and what happens.

**Self-reference guard callout**: "All mechanisms include a guard that prevents wiring a module to its own output. Without this, aggregation modules that produce `capital_cost` and consume `capital_cost` (from children) would create a cycle."

**Interactive element**: Dropdown to select different references and see which mechanism/strategy resolves them. Examples:
1. `total_capex = capital_cost` → Strategy A (scoped) → MODULE_OUTPUT
2. `discount_rate = discount_rate` → All strategies miss → ENTRY_POINT

### 6. Act 4: "The Full Graph"

#### 6a. DAG Diagram

Carried forward from prior design's §7, with updated module data.

**Layout**: Left-to-right flow, tier-slot grid algorithm:
- 7 tiers (0-6) determine x-position
- Modules sorted by cluster (solar_array, battery_system, site_infra, system) within tier
- Grid spacing: `TIER_WIDTH=400px`, `SLOT_HEIGHT=60px`, `CLUSTER_GAP=40px`
- Positions computed in JS, not manual coordinates

**SVG canvas**: ~3500×2000px. ZoomPanController with minimap.

**Node rendering**:
- Collapsed (default): 160×40px, short name, family color fill
- Expanded (on click): 280×(40 + 20×max(inputs,outputs)), input/output ports visible
  - Input ports labeled with source: "EP" badge (entry point) or upstream module short name
  - Output ports labeled with channel short name

**Color coding**: F1=blue, F2=purple, F3=orange (consistent with all other diagrams).

**Cluster grouping**: Subsystem clusters have light background rectangles with dashed borders.

**Progressive disclosure**:
- Initial: All clusters collapsed → ~8 elements
- Click cluster → expand to see internal modules
- "Expand All" / "Collapse All" in sticky overlay bar

**Trace mode**: Click module → "Trace" button → BFS backward → upstream highlighted, rest dims to 15%. Uses shared `traceUpstream()`. Default on first load: LCOE trace pre-activated.

**Module detail panel**: When a module is expanded/selected, shows all fields from `PipelineModule`:
- inputs (with InputSource details)
- outputs (with channel_name)
- compilability
- factory type (CalcUsage / FORMULA / Aggregation)
- execution_order position

This satisfies FR-3 (fully expanded PipelineModule with concrete values).

#### 6b. Generated Code Samples

Three panels with traceability annotations linking each line back to ComputationGraph fields. Each panel has "Click to highlight in graph" link.

Carried forward from prior design's §7c with added field-level traceability annotations.

### 7. JS Data Model (MODEL_DATA)

The prior design's MODEL_DATA structure is expanded significantly:

```js
const MODEL_DATA = {

  // ──── Part Hierarchy (Act 1) ────
  hierarchy: {
    name: "Solar Battery Plant",
    type: "plant",
    children: [
      {
        name: "Solar Array",
        type: "subsystem",
        children: [
          {
            name: "PV Module",
            type: "component",
            multiplicity: { count: 20, attr: "module_count" },
            designValues: { wattage: 400.0, efficiency: 0.21 },
            calcUsage: {
              name: "cost_model",
              calcDef: "PVModuleCostCalc",
              inputs: ["wattage", "efficiency", "cost_per_watt", "fab_factor", "install_factor"],
              outputs: ["material_cost", "fab_cost", "install_cost", "total_cost", "idiot_index"]
            }
          },
          // ... inverter, array_bos
        ],
        aggregations: [{
          attribute: "capital_cost",
          expression: "sum(pv_module.capital_cost) + sum(inverter.capital_cost) + array_bos.capital_cost + misc_hardware_cost",
          sumTerms: [
            { part: "pv_module", attr: "capital_cost", multAttr: "module_count", count: 20 },
            { part: "inverter", attr: "capital_cost", multAttr: "inverter_count", count: 4 }
          ],
          singletonTerms: [{ path: "array_bos.capital_cost" }],
          localTerms: [{ attr: "misc_hardware_cost" }]
        }]
      },
      // ... battery_system, site_infra
    ],
    systemCalcs: [/* ... */]
  },

  // ──── Pipeline Step Data (Act 2) ────
  // Concrete values at each step for the traced module (pv_module cost_model)
  pipelineTrace: {
    step1_extract: {
      calcDef: {
        name: "PVModuleCostCalc",
        qualified_name: "SolarBatteryLibrary::PVModuleCostCalc",
        inputs: [
          { name: "wattage", python_type: "float", default: null },
          { name: "efficiency", python_type: "float", default: null },
          { name: "cost_per_watt", python_type: "float", default: 1.07 },
          // ...
        ],
        outputs: [
          { name: "material_cost", python_type: "float" },
          { name: "total_cost", python_type: "float" },
          // ...
        ]
      },
      calcUsage: {
        instance_name: "cost_model",
        calc_def_name: "PVModuleCostCalc",
        is_template: true,
        owning_part_def_qn: "SolarBatteryLibrary::'PV Module'",
        bindings: [
          { param: "wattage", source_path: "wattage", binding_type: "CHAIN" },
          { param: "efficiency", source_path: "efficiency", binding_type: "CHAIN" },
          { param: "cost_per_watt", source_path: null, binding_type: "UNBOUND" }
        ]
      }
    },
    step2_registry: {
      tracedKeys: [
        { format: "ScopedKey", key: "solar_battery_plant.solar_array.pv_module.cost_model.total_cost", canonical: "...pv_module__cost_model__total_cost", registry: "_scoped" },
        { format: "CanonicalChannel", key: "...pv_module__cost_model__total_cost", canonical: "(membership in _canonical set)", registry: "_canonical" }
      ],
      scopeAmbiguity: {
        unscopedKey: "cost_model.total_cost",
        registered: false,
        explanation: "Not registered at all — 9 components have a cost_model, so unscoped keys are ambiguous. Prevented by construction: only ScopedKey (hierarchy-qualified) is registered."
      }
    },
    step35_rewrite: {
      before: [
        { param: "wattage", binding_type: "CHAIN", source_path: "wattage" },
        { param: "efficiency", binding_type: "CHAIN", source_path: "efficiency" },
        { param: "cost_per_watt", binding_type: "UNBOUND", source_path: null }
      ],
      after: [
        { param: "wattage", binding_type: "LITERAL", literal_value: 400.0, mutation: "LITERAL_OVERRIDE" },
        { param: "efficiency", binding_type: "LITERAL", literal_value: 0.21, mutation: "LITERAL_OVERRIDE" },
        { param: "cost_per_watt", binding_type: "UNBOUND", source_path: null, mutation: "NONE" }
      ]
    },
    step4_classify: [
      { qn: "...wattage", type: "DESIGN_ATTRIBUTE", default: 400.0, reason: "design literal" },
      { qn: "...efficiency", type: "DESIGN_ATTRIBUTE", default: 0.21, reason: "design literal" },
      { qn: "...cost_per_watt", type: "LIBRARY_DEFAULT", default: 1.07, reason: "calc def default" }
    ],
    step5_module: {
      name: "solarbatterydesign__solar_battery_plant__solar_array__pv_module__cost_model",
      module_type: "solarbatterylibrary.PVModuleCostCalcModule",
      family: "F1",
      is_computed_attribute: false,
      is_aggregation: false,
      compilability: "FULLY_COMPILABLE",
      inputs: [
        { param: "wattage", source_type: "entry_point", param_group: "design_params", qn: "...wattage" },
        { param: "efficiency", source_type: "entry_point", param_group: "design_params", qn: "...efficiency" },
        { param: "cost_per_watt", source_type: "entry_point", param_group: "library_params", qn: "...cost_per_watt" }
      ],
      outputs: [
        { field_name: "root", channel: "...pv_module__cost_model__total_cost" }
      ],
      entryPoints: {
        "...wattage": { type: "DESIGN_ATTRIBUTE", default: 400.0 },
        "...cost_per_watt": { type: "LIBRARY_DEFAULT", default: 1.07 }
      }
    }
  },

  // ──── Pipeline Modules (Act 4 DAG) ────
  modules: [
    {
      id: "sa_pv_cost_model",
      shortName: "PV Module Cost",
      fullEQN: "solarbatterydesign__solar_battery_plant__solar_array__pv_module__cost_model",
      family: "F1",
      cluster: "solar_array",
      tier: 0,
      compilability: "FULLY_COMPILABLE",
      inputs: [
        { name: "wattage", source: "entry_point", group: "design", value: 400.0 },
        { name: "efficiency", source: "entry_point", group: "design", value: 0.21 },
        { name: "cost_per_watt", source: "entry_point", group: "library", value: 1.07 }
      ],
      outputs: [
        { name: "total_cost", channel: "...pv_module__cost_model__total_cost" }
      ]
    },
    // ... all 35 modules
  ],

  // ──── Dependency Edges (Act 4 DAG) ────
  edges: [
    { from: "sa_pv_cost_model", fromOutput: "total_cost",
      to: "sa_capital_cost", toInput: "pv_module_capital_cost" },
    // ... all edges
  ],

  // ──── Dual Resolution Examples (Act 3c) ────
  resolutionExamples: [
    {
      label: "total_capex = capital_cost",
      reference: "capital_cost",
      consumer: "annualized_financial",
      backtrackerPath: {
        scope: "solar_battery_plant",
        dispatchType: "CHAIN",
        scopedKey: "solar_battery_plant.capital_cost",
        registryQueried: "_scoped",
        result: "MODULE_OUTPUT",
        channel: "...capital_cost__capital_cost"
      },
      resolveInputPath: {
        strategies: [
          { name: "A: ScopedRegistryLookup", key: "solar_battery_plant.capital_cost", result: "HIT" }
          // C, D not reached
        ],
        result: "module_output",
        channel: "...capital_cost__capital_cost"
      }
    },
    {
      label: "discount_rate = discount_rate",
      reference: "discount_rate",
      consumer: "annualized_financial",
      backtrackerPath: {
        scope: "solar_battery_plant",
        dispatchType: "CHAIN",
        scopedKey: "solar_battery_plant.discount_rate",
        registryQueried: "_scoped",
        result: "ENTRY_POINT",
        channel: null
      },
      resolveInputPath: {
        strategies: [
          { name: "A: ScopedRegistryLookup", key: "solar_battery_plant.discount_rate", result: "MISS" },
          { name: "C: ChainRedefinitionFollow", result: "MISS" },
          { name: "D: DesignAttributeLookup", key: "discount_rate", result: "HIT" }
        ],
        result: "entry_point",
        channel: null
      }
    }
  ],

  // ──── Binding Resolution Examples (Act 2 Step 5.5) ────
  registryExamples: [
    {
      label: "total_capex = capital_cost (:: normalization path)",
      sourcePath: "SolarBatteryLibrary::'Solar Battery Plant'::capital_cost",
      steps: [
        { action: "Direct lookup", key: "SolarBatteryLibrary::'Solar Battery Plant'::capital_cost", result: "miss" },
        { action: "Normalize '::'", key: "solar_battery_plant.capital_cost", result: "hit", phase: "Phase 1b" }
      ],
      resolvedChannel: "...capital_cost__capital_cost",
      resolvedModule: "plant_capital_cost",
      resolutionType: "MODULE_OUTPUT"
    },
    // 2-3 more examples
  ],

  // ──── Entry Point Groups (Act 2 Step 4, Act 4) ────
  entryPointGroups: [
    {
      name: "design_params",
      className: "DesignParams",
      parameters: [
        { qn: "...wattage", simpleName: "wattage", type: "DESIGN_ATTRIBUTE", default: 400.0 },
        { qn: "...efficiency", simpleName: "efficiency", type: "DESIGN_ATTRIBUTE", default: 0.21 },
        // ...
      ]
    },
    {
      name: "library_params",
      className: "LibraryParams",
      parameters: [
        { qn: "...cost_per_watt", simpleName: "cost_per_watt", type: "LIBRARY_DEFAULT", default: 1.07 },
        // ...
      ]
    }
  ]
};
```

The full 35-module list, all edges, and complete entry point data will be derived from running the current pipeline on the solar battery fixtures during implementation. The data is structured to match the refactored model field names even though the current code uses slightly different internal representations.

---

## Potential Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| **File size exceeds 300KB** | Slow load | Keep SVG procedural (generated from data). The 25KB MODEL_DATA is the main cost; rendering code is compact. Budget: 200-250KB. |
| **Act 2 is too long** | Reader loses attention scrolling through 10 pipeline steps | Progressive disclosure: overview strip stays sticky, steps start collapsed (1-sentence summary visible), expand on click. Reader can skip to Act 3/4. |
| **Refactored data models don't match current output** | MODEL_DATA field names don't match reality | Derive concrete values from running current pipeline. Structure data to match refactored model names. Document any gaps as "design validation findings." |
| **Dual resolution proof is abstract** | Reader can't follow the side-by-side | Use the same concrete reference in both paths. Highlight the identical result at the bottom. The interactive dropdown lets users try multiple references. |
| **SVG rendering performance with 35 modules** | Janky zoom/pan | `will-change: transform` on SVG container. Simplify edges at low zoom. Debounce wheel events. Collapsed clusters reduce DOM nodes. |
| **Cross-browser SVG differences** | Layout breaks in Safari | Use standard SVG 1.1 only. Use viewBox for zoom (not CSS transforms on SVG internals). Test in 3 browsers. |
| **Design intent docs contain unstated assumptions** | Explainer reveals gaps while building concrete data | This is a feature — document findings in a "Design Validation Findings" section at the end of the HTML. The explainer serves as a proof-of-concept for the refactor design. |

---

## Integration Strategy

- **Standalone documentation artifact** — no changes to source code
- File path: `.project/diagrams/new_pipeline_explainer.html`
- Supersedes: `.project/diagrams/08_block_diagrams.html` and the old explainer spec/design
- References the refactored design intent docs (`.project/concepts/refactor-design-intent/`)
- Can be committed to the repo, opened by anyone with a browser
- Serves as the primary onboarding artifact and design validation artifact

---

## Validation Approach

### Data Accuracy
1. Run the current pipeline on solar battery fixtures: `uv run sysml-codegen generate --models tests/fixtures/solar_battery_model --output /tmp/solar_battery_test --package-name solar_battery`
2. Compare every module name, input, output, and edge in the HTML against the generated baseline YAML
3. Verify entry point classifications match
4. Verify registry key formats match

### Design Validation
5. While building concrete data for each pipeline step, document any case where the refactored design intent is ambiguous or contradictory — these are the "design validation findings" the spec demands (Success Criterion 3)
6. Verify the dual resolution proof: for at least one reference, confirm both paths produce identical wiring

### Comprehension
7. Have someone unfamiliar with the codebase answer the 5 comprehension test questions from the spec's acceptance criteria

### Browser & Quality
8. Open in Chrome, Firefox, Safari — verify zoom/pan, animations, layout
9. Verify file size < 500KB
10. Open with network disabled — verify self-containment

### Success Criteria (from spec)
- [ ] Reader answers "What are the 7 pipeline steps?" after Act 2 overview
- [ ] Reader answers "Why two resolution paths?" after Act 3c
- [ ] Reader answers "How does sum() become a multiply?" after Act 3b
- [ ] Reader answers "What is a ScopedKey?" after Step 2 / Step 5.5
- [ ] Reader answers "What guarantees generation doesn't need extraction data?" after Step 6

---

## Implementation Order

Each step produces a viewable HTML file:

1. **Skeleton + navigation**: HTML structure, CSS layout, 4-act sidebar, sticky pipeline overview strip. Empty section containers.
2. **Data model**: Full MODEL_DATA object — all 35 modules, edges, pipeline trace data, resolution examples. Validated against baseline.
3. **Shared utilities**: renderModuleNode(), traceUpstream(), highlight/dim, renderDataPanel(), renderStepConnector().
4. **ZoomPanController**: Reusable class, tested on empty SVG.
5. **Act 1**: Hierarchy diagram + "Big Question" animation.
6. **Act 2 overview**: Pipeline overview strip with step boxes and ordering constraint annotations.
7. **Act 2 steps 1-7**: Pipeline step sections with data panels, traced module, callouts. One section at a time.
8. **Act 3a**: Template instantiation demo (3-panel, stepper).
9. **Act 3b**: Aggregation decomposition demo (4-tier, slider).
10. **Act 3c**: Dual resolution demo (side-by-side, strategy chain, interactive dropdown).
11. **Act 4**: DAG diagram with tier-slot grid layout, clusters, trace mode, minimap.
12. **Act 4 code samples**: Generated code panels with traceability annotations.
13. **Glossary overlay**: 8 terms with visual examples.
14. **Polish**: Responsive tweaks, animation timing, color consistency, keyboard navigation.

---

**Next Step:** After approval → `/_my_plan` to break implementation into ordered tasks, then `/_my_implement` for each task.
