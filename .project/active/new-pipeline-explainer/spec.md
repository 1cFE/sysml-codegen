# Spec: New Pipeline Explainer

**Status:** Draft
**Owner:** Reid Westwood
**Created:** 2026-02-17 02:08 UTC
**Complexity:** HIGH
**Branch:** cost-pattern-refactor
**Supersedes:** `.project/active/interactive-pipeline-explainer/spec.md`

---

## Business Goals

### Why This Matters

The refactor design intent (`.project/concepts/refactor-design-intent/`, 26 documents, 168 requirements) describes a clean pipeline architecture. But architecture documents are not proof. They describe what should happen — they don't demonstrate that the pieces actually compose into a working whole.

This explainer serves two purposes:

1. **Validation artifact**: Force the refactored design through a concrete end-to-end example (LCOE computation for a solar battery plant). Every step of the 7-step pipeline must be shown transforming real data. If a step can't be explained clearly with concrete inputs and outputs, the design has a gap.

2. **Onboarding artifact**: A new engineer opens the HTML, spends 20 minutes, and understands what the pipeline does, why each step exists, and how the pieces compose. Not what the code looks like — what it *means*.

The old explainer spec was written against the old architecture. That architecture had three independent resolution implementations, shared mutable state, generation reaching past the ComputationGraph into extraction models, and orchestration hiding in `generation/initialization.py`. Explaining a broken design produces a broken explanation. This spec starts fresh against the intended design.

### Success Criteria

- [ ] A software engineer unfamiliar with the codebase can trace the LCOE value from SysML source to generated pipeline output, naming every intermediate data structure it passes through
- [ ] The three "hard parts" (template instantiation, aggregation decomposition, dual resolution) are each explained with concrete before/after examples, not abstract descriptions
- [ ] The explanation surfaces at least one design gap, ambiguity, or unstated assumption in the refactor design intent — or provides evidence that none exist
- [ ] Every PipelineModule in the LCOE computation graph can be clicked to show: its inputs (with source type and producer), its outputs (with channel names), and its factory type
- [ ] The dual resolution architecture is shown with parallel traces through both paths, demonstrating they produce equivalent wiring for the same reference

### Priority

High. This should be built before or in parallel with the refactor implementation. The explainer is a forcing function — building it against the design intent will expose gaps before code is written.

---

## Problem Statement

### Current State

The refactor design intent exists as 26 prose documents with requirements tables. These are thorough but linear — they describe each component in isolation. No single artifact demonstrates that the components compose correctly end-to-end. The existing `08_block_diagrams.html` explains a design that is being thrown away.

### Desired Outcome

A single self-contained HTML file that traces the LCOE computation through the refactored 7-step pipeline, showing the concrete data transformations at each step. The explainer is structured as a proof: given this SysML input, here is what each step produces, here is why each step is necessary, and here is the generated output at the end.

---

## Scope

### In Scope

- Single self-contained HTML file (vanilla HTML + inline SVG + vanilla JS, no external dependencies)
- End-to-end narrative following the LCOE computation through all 7 pipeline steps
- Concrete data examples at each step (not pseudocode — actual model instances with real field values from the solar battery example)
- Interactive computation graph DAG with module drill-down
- Visualizations of the three hard parts: template instantiation, aggregation decomposition, dual resolution
- Implementation pattern visualization: pure factory functions, strategy chain, OutputRegistry key formats
- Brief expandable SysML glossary grounded in the solar battery example
- Large zoomable/pannable diagrams

### Out of Scope

- Explaining the current (pre-refactor) architecture or the refactor migration path
- Source code file paths, line numbers, or function signatures as explanatory content
- Exhaustive data model field listings (belongs in API docs)
- Expression compiler internals beyond "SysML expressions become Python code with a compilability verdict"
- Print-friendly layout
- Every edge case and classification category — this is proof-of-concept, not reference manual

### Edge Cases & Considerations

- The solar battery model has ~35 pipeline modules — the full computation graph needs collapse/expand by subsystem
- The design intent documents may contain unstated assumptions that only surface when forced through a concrete example — this is a feature, not a bug
- The explainer depicts the refactored design AS IF complete, before implementation begins — it must be self-consistent with the design intent docs even where the code doesn't exist yet

---

## Requirements

### FR-1: Narrative Structure — The 7-Step Proof

The narrative MUST follow the LCOE computation through the refactored pipeline's 7 steps. Each step MUST show:

- **Input**: What data structure enters this step (with concrete values from the solar battery example)
- **Transformation**: What the step does to the data and why this step exists
- **Output**: What data structure leaves this step (with concrete values)
- **Composition proof**: How this step's output becomes the next step's input

The 7 steps, with sub-steps where orchestration ordering matters:

| Step | Name | Produces |
|------|------|----------|
| 1 | Extract | `CalculationDefinitionData`, `CalcUsageData`, `PartDefinitionData` |
| 2 | Build Registry | `OutputRegistry` (Key_A through Key_F populated) |
| 3 | Trace Dependencies | `BacktrackingResult` (binding resolutions, required usages) |
| 3.5 | Hierarchy + Virtual Binding Rewrite | `HierarchyExtractionResult`, mutated `CalcUsageData` bindings |
| 4 | Classify Entry Points | `EntryPoint` instances typed as DESIGN_ATTRIBUTE / LIBRARY_DEFAULT / USAGE_LITERAL |
| 4.5 | Computed Attributes | `ComputedAttributeData`, FORMULA removal from design attrs |
| 5 | Build Modules | `PipelineModule` instances from 3 factory types |
| 5.5 | Build OutputRegistry (4-phase) | Fully populated `OutputRegistry` |
| 6 | Sort + Validate | Topologically ordered `ComputationGraph` |
| 7 | Render | Generated Python, YAML, JSON |

The narrative MUST make the ordering constraints visible — why Step 3.5 must precede Step 4, why Step 4.5 must precede Step 5, why Step 5.5 must precede Step 6.

### FR-2: The Solar Plant Hierarchy Diagram

The SysML part hierarchy MUST be rendered as a 2D spatial nested layout:

- MUST use nested rectangles showing containment (plant > subsystems > components)
- MUST show calc usages inside their owning parts (e.g., `cost_model` inside `pv_module`)
- MUST show multiplicity visually (e.g., `pv_module [20]` as a stack or badge)
- MUST be zoomable and pannable
- SHOULD arrange subsystems spatially (solar array left, battery center, site infrastructure right)

### FR-3: The ComputationGraph as Single Source of Truth

The ComputationGraph MUST be presented as the central artifact of the pipeline — the pivot point between resolution (steps 1-6) and generation (step 7):

- MUST show the `ComputationGraph` Pydantic model structure: `modules`, `entry_point_groups`, `execution_order`
- MUST demonstrate visually that generation consumes ONLY the ComputationGraph — no back-references to extraction models
- MUST show one `PipelineModule` fully expanded with its `ModuleInput` list (each with `InputSource`), `ModuleOutput` list (each with `channel_name`), and flags (`is_computed_attribute`, `is_aggregation`, `compilability`)
- SHOULD contrast this with the problem it solves: "previously, generators reached past the graph into raw extraction data"

### FR-4: The Computation Graph DAG

The full computation graph MUST be rendered as an interactive 2D DAG:

- MUST use spatial layout — modules that can execute in parallel at the same vertical level
- MUST color-code the three module types: CalcUsage (e.g., blue), FORMULA/Computed Attribute (e.g., purple), Aggregation (e.g., orange)
- MUST show data flow edges with directional arrows from producer to consumer
- MUST support click-to-expand on each module to reveal inputs, outputs, factory type, and compilability
- MUST support trace mode: click an output module (e.g., LCOE) and highlight all upstream dependencies, dimming unrelated modules
- MUST be pannable and zoomable — ~35 modules MUST NOT be shrunk to fit one viewport
- SHOULD group modules by subsystem (Solar Array cluster, Battery System cluster, etc.)
- SHOULD show a minimap for viewport orientation

### FR-5: Three Module Types and Pure Factories

The three module types MUST be explained with concrete examples from the LCOE computation:

| Type | Example | Factory signature |
|------|---------|------------------|
| CalcUsage | `pv_module_cost_model` | `build_calc_usage_module(usage, calc_def, binding_resolutions, ...) -> (PipelineModule, dict[str, EntryPoint])` |
| FORMULA | `battery_pack__energy_capacity` | `build_formula_module(computed_attr, registry, ...) -> (PipelineModule, dict[str, EntryPoint])` |
| Aggregation | `solar_array__capital_cost` | `build_aggregation_module(scoped_agg, registry, ...) -> (PipelineModule, dict[str, EntryPoint])` |

For each type, the explainer MUST show:

- The input data that feeds the factory (extraction-layer model)
- The pure function call with no side effects (returns tuple, doesn't mutate)
- The resulting `PipelineModule` with concrete inputs/outputs
- The entry points collected as a separate return value

The "pure factory" pattern MUST be explicitly called out: no shared mutable state, no entry point mutation as a side effect, each factory independently testable.

### FR-6: Template Instantiation and Virtual Binding Rewrite

Template expansion MUST be explained through a concrete before/after:

- MUST show the "before": a `cost_model` CalcUsage inside the `'PV Module'` PartDefinition with generic bindings (e.g., `in wattage = wattage` referencing template-level attribute)
- MUST show the design instance: `solar_battery_plant > solar_array > pv_module : 'PV Module'`
- MUST show the virtual binding rewrite (Step 3.5): three mutation cases
  - LITERAL override: binding becomes `binding_type=LITERAL, literal_value=400.0` (from `:>> pv_module.wattage = 400.0`)
  - CHAIN override: `source_path` replaced with design-instance-scoped path
  - No match: binding unchanged
- MUST show the "after": virtual CalcUsage with fully qualified name scoped to the design instance path, bindings rewritten
- SHOULD use animation or before/after toggle

### FR-7: Aggregation Decomposition

Aggregation MUST be explained through Solar Array's `capital_cost`:

- MUST show the SysML expression: `capital_cost = sum(pv_module.capital_cost) + sum(inverter.capital_cost) + array_bos.capital_cost + misc_hardware_cost`
- MUST show decomposition into three term types:
  - **SumTerm**: `sum(pv_module.capital_cost)` where `pv_module[20]` → `pv_module_capital_cost * module_count` (parametric multiply using `mult_lookup`)
  - **SingletonTerm**: `array_bos.capital_cost` — direct reference to single-instance child
  - **LocalTerm**: `misc_hardware_cost` — same-PartDef attribute, resolved via 3 strategies (sibling aggregation output → EXPOSE_PURE alias → entry point fallback)
- MUST show how each term becomes a `ModuleInput` with a resolved `InputSource`
- MUST show the cascade: leaf components → subsystem aggregations → plant total → `annualized_financial.total_capex` → LCOE
- SHOULD show literal value propagation: when an aggregation input can't wire to upstream, `_find_literal_redefinition()` checks `:>>` defaults before creating an entry point

### FR-8: Dual Resolution Architecture

This is the most important "prove it works" section. The refactored design has two resolution paths that MUST stay separate (doc 24). The explainer MUST demonstrate why and show they compose correctly:

**Path 1: Backtracker (CalcUsage modules)**
- MUST show the DFS traversal: backtracker encounters a binding, resolves it to decide "recurse deeper" vs "stop — this is an entry point"
- MUST show why resolution is embedded in traversal: you can't separate "what to resolve" from "what to traverse next"
- MUST show the output: `BindingResolution` objects in `BacktrackingResult.binding_resolutions`

**Path 2: resolve_input() (FORMULA + Aggregation modules)**
- MUST show the strategy chain: `resolve_input(ref, ctx, strategies) -> InputSource`
- MUST show the 5 strategies in order with concrete examples:
  - C: ScopedRegistryLookup (Key_C — hierarchy-scoped, unique)
  - A: DirectRegistryLookup (Key_A — unscoped, potentially ambiguous)
  - B: SysmlQnNormalization (`Package::Part::attr` → dotted)
  - D: ChainRedefinitionFollow (`:>>` chains, cycle-safe)
  - E: DesignAttributeLookup (bare name match)
- MUST show that `AGG_STRATEGIES` reorders to promote D before A/B (because aggregation inputs almost always resolve through `:>>` chains)
- MUST show the self-reference guard: prevents wiring a module to its own output

**Composition proof:**
- MUST pick one concrete reference that both paths could resolve (e.g., a binding that appears in a CalcUsage AND would also appear if the same calc were a FORMULA)
- MUST show both paths arriving at the same `InputSource` / wiring decision
- MUST explain why this equivalence is required (REQ-DRA-04) and how it's tested

### FR-9: The OutputRegistry and Key Formats

The OutputRegistry MUST be shown as the namespace that makes resolution work:

- MUST show it as a flat `dict[str, str]` mapping alias → canonical channel
- MUST show the 4-phase build protocol with concrete examples from LCOE:
  - Phase 1a: CalcUsage outputs → Key_A (`cost_model.total_cost`), Key_B (`BatteryPackCostCalc.total_cost`), Key_C (`plant.battery_system.battery_pack.cost_model.total_cost`)
  - Phase 1b: Aggregation outputs → Key_D, Key_E, stripped variants
  - Phase 1c: FORMULA outputs → Key_F, bare, SysML QN
  - Phase 2: CHAIN aliases (`:>>` redefinition chains)
  - Phase 3: EXPOSE_PURE aliases (computed attribute passthrough)
  - Phase 4: Transitive design attribute aliases
- MUST show the scope problem: two parts containing identically-named `cost_model` usages — Key_A is ambiguous, Key_C disambiguates
- SHOULD be interactive: let the user select a reference and see which key format matches

### FR-10: Entry Point Classification

Entry points MUST be shown as the pipeline's external inputs:

- MUST show the three types (ADR-001) with concrete examples:
  - `DESIGN_ATTRIBUTE`: `pv_module.wattage = 400.0` (from PartDef literal)
  - `LIBRARY_DEFAULT`: `discount_rate` with default `0.08` (from calc def)
  - `USAGE_LITERAL`: `in unit_cost = 4.50` (hardcoded in usage binding)
- MUST show classification precedence: `DESIGN_ATTRIBUTE` > `LIBRARY_DEFAULT` > `USAGE_LITERAL`
- MUST show the two creation paths:
  - Path 1: Backtracker → `_classify_entry_points()` (3-strategy, full binding context)
  - Path 2: Factory fallback → hardcoded `DESIGN_ATTRIBUTE` (FORMULA/Aggregation factories lack binding context)
- MUST show how entry points are organized into `ParameterGroup` objects, each mapping to one JSON input file

### FR-11: Generated Output Traceability

The final section MUST connect the ComputationGraph back to generated artifacts:

- MUST show a sample pipeline YAML snippet and trace each line back to the `PipelineModule` that produced it
- MUST show a module wrapper and trace its inputs/outputs back to `ModuleInput`/`ModuleOutput`
- MUST show a JSON input schema and trace its fields back to `EntryPoint` instances in a `ParameterGroup`
- MUST show that generation consumes only `ComputationGraph` fields — the "single source of truth" claim is proven by showing no other data source is needed

### FR-12: SysML Visual Glossary

An expandable glossary MUST be available:

- MUST cover: PartDefinition, PartUsage, CalcDefinition, CalcUsage, binding (`in param = source`), `:>>` redefinition, multiplicity `[N]`, `sum()` aggregation
- MUST use visual examples from the solar battery model
- MUST be accessible from any point in the narrative (floating button or sidebar)
- MUST NOT be a prerequisite — the narrative itself SHOULD be understandable without opening the glossary

### FR-13: Navigation and Interactivity

- MUST have zoom/pan controls on all large diagrams (mouse wheel zoom, click-drag pan)
- MUST have a persistent navigation element showing narrative position and the current pipeline step
- MUST support smooth scrolling between sections
- MUST support keyboard navigation (arrows to pan, +/- to zoom)
- MUST be a single self-contained HTML file with no external dependencies
- SHOULD have a minimap on the computation graph DAG

### FR-14: Progressive Disclosure

- MUST start with the plant hierarchy (~15 elements), not the full 35-module graph
- MUST use expand/collapse to manage complexity
- SHOULD support detail levels: Level 1 = plant overview (5 elements), Level 2 = subsystem internals (~15), Level 3 = full graph (~35)
- Each pipeline step section SHOULD start with a 1-sentence summary before expanding into detail

### FR-15: Plain-English Explanations

- MUST explain every concept in plain English BEFORE showing technical detail
- MUST NOT use function signatures, field listings, or file paths as explanations
- MUST ground every explanation in the solar battery example
- SHOULD use analogies where helpful
- Explanatory text MUST be integrated with visuals, not separated into prose below static images

---

## Acceptance Criteria

### Design Validation

- [ ] Every step of the 7-step pipeline is shown with concrete input/output data from the LCOE example
- [ ] The ordering constraints (3.5→4, 4.5→5, 5.5→6) are visually explained with "what breaks if you skip this" examples
- [ ] The dual resolution architecture is demonstrated with a parallel trace showing both paths reach the same wiring
- [ ] The ComputationGraph is shown to be sufficient for generation — no data from upstream steps leaks past it
- [ ] At least one `PipelineModule` is fully expanded showing all `ModuleInput` sources and `ModuleOutput` channels with real values
- [ ] The three module factory types are each shown with input → pure function → output, demonstrating no side effects
- [ ] Aggregation decomposition (SumTerm / SingletonTerm / LocalTerm) is shown with the Solar Array `capital_cost` expression mapped term-by-term to `ModuleInput` instances

### Comprehension Test

- [ ] A reader can answer: "What are the 7 pipeline steps and what does each produce?" after the pipeline overview
- [ ] A reader can answer: "Why are there two resolution paths and why can't they be merged?" after the dual resolution section
- [ ] A reader can answer: "How does `sum(pv_module.capital_cost)` become a parametric multiply?" after the aggregation section
- [ ] A reader can answer: "What is Key_C and why does it exist?" after the OutputRegistry section
- [ ] A reader can answer: "What guarantees that generation doesn't need extraction data?" after the ComputationGraph section

### Core Functionality

- [ ] Single self-contained HTML file opens in any modern browser with no dependencies
- [ ] Narrative follows LCOE computation end-to-end from SysML model to generated pipeline
- [ ] Solar plant hierarchy rendered as 2D spatial nested layout
- [ ] Computation graph rendered as pannable/zoomable 2D DAG with color-coded module types
- [ ] All three hard parts (template instantiation, aggregation decomposition, dual resolution) have interactive visualizations
- [ ] SysML glossary available as expandable overlay
- [ ] All diagrams support zoom (mouse wheel) and pan (click-drag)
- [ ] Progressive disclosure: initial view shows ~5-15 elements; full detail via drill-down

### Quality

- [ ] No external CDN or library dependencies
- [ ] File size SHOULD be under 500KB
- [ ] Works in Chrome, Firefox, Safari (latest)
- [ ] Self-consistent with the 26 design intent documents — no contradictions

---

## Narrative Outline

### Act 1: "Meet the Solar Plant" (the world)

> *You're an engineer who designed a solar battery plant in SysML. Here's what that looks like.*

- Interactive 2D hierarchy diagram: plant > 3 subsystems > 9 components
- Calc usages visible inside their owning parts
- The question: "What's the Levelized Cost of Electricity?"
- Visual trace from LCOE down the dependency chain

### Act 2: "The Pipeline" (the machine)

> *Here's the machine that turns your SysML model into a runnable computation. Seven steps, each with a clear input and output.*

Walk through each step with the LCOE data:

**Step 1 — Extract**: SysML files → `CalculationDefinitionData` + `CalcUsageData`. Show one calc def and one usage with concrete fields.

**Step 2 — Build Registry**: Catalog all module outputs into the `OutputRegistry`. Show Key_A/B/C for `pv_module_cost_model.total_cost`. Show why Key_C exists (scope disambiguation).

**Step 3 — Trace Dependencies**: Backtracker DFS from LCOE. Show the traversal tree. Show one binding resolution decision: "this resolves to an upstream module (recurse)" vs "this has no producer (entry point, stop)."

**Step 3.5 — Hierarchy + Virtual Binding Rewrite**: Show template `cost_model` inside `'PV Module'` PartDef. Show the design instance. Animate the binding rewrite (three mutation cases). Show why this MUST happen before Step 4.

**Step 4 — Classify Entry Points**: Show the three types with concrete examples. Show precedence.

**Step 4.5 — Computed Attributes**: Show a FORMULA being identified and removed from design attrs. Show why this MUST happen before Step 5 (prevents false entry points).

**Step 5 — Build Modules**: Show one factory call of each type. Emphasize pure function → `(PipelineModule, dict[str, EntryPoint])`.

**Step 5.5 — Build OutputRegistry (4-phase)**: Show the registry growing across 4 phases. Show the scope problem and Key_C resolution.

**Step 6 — Sort + Validate**: Show Kahn's algorithm producing execution order. Show validation: every `producer_channel` resolves to a declared output.

**Step 7 — Render**: Show generated YAML, module wrapper, JSON schema. Trace each back to the ComputationGraph.

### Act 3: "Why The Hard Parts Work" (the proof)

> *Three things make this non-trivial. Here's each one, end to end, with concrete data.*

**3a: Template Instantiation** — Before/after of virtual binding rewrite. "The recipe vs. the kitchen" — but now showing the actual data mutation.

**3b: Aggregation Decomposition** — Solar Array `capital_cost` decomposed term-by-term. SumTerm → parametric multiply. LocalTerm → 3-strategy resolution. Cascade to plant total.

**3c: Dual Resolution** — Side-by-side: Backtracker path (DFS + binding context) vs `resolve_input()` (strategy chain). Same reference, same answer. Why they can't merge (resolution is embedded in traversal for CalcUsage).

### Act 4: "The Full Graph" (the result)

> *After all that, here's the complete computation graph for LCOE.*

- Interactive DAG with ~35 modules, color-coded by type
- Click any module → inputs/outputs/factory type/compilability
- Trace mode: click LCOE → all upstream lights up
- Entry point groups shown as JSON input panels feeding into the graph
- "This is the single source of truth. Generation reads nothing else."

---

## Related Artifacts

- **Design Intent:** `.project/concepts/refactor-design-intent/` (26 documents)
- **Supersedes:** `.project/active/interactive-pipeline-explainer/spec.md`
- **Research:** `.project/research/20260216-120000_interactive-html-diagram-frameworks.md`
- **Design:** `.project/active/new-pipeline-explainer/design.md` (to be created)

---

**Next Steps:** After approval, proceed to `/_my_design`
