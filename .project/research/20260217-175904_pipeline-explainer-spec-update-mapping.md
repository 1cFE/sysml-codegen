---
date: 2026-02-17T17:59:04Z
researcher: Claude
topic: "Pipeline Explainer Spec Update Mapping — Typed Registry Refactor Impact"
tags: [research, pipeline-explainer, typed-registry-refactor, spec-update]
status: addressed
last_updated: 2026-02-17
---

# Research: Pipeline Explainer Spec Update Mapping

**Date**: 2026-02-17 17:59 UTC
**Researcher**: Claude
**Research Type**: Architecture / Design Gap Analysis

## Research Question

Five commits (2aa1fe2, 86cf995, a64c622, cfc4c69, ec1d18d) introduced major design architecture changes — the Typed Registry Refactor (TRR). How must the pipeline explainer spec (`.project/active/new-pipeline-explainer/spec.md`) be updated to match?

## Summary

- The OutputRegistry changed from a **flat `dict[str, str]` with ~12 key formats** to **3 typed registries + 1 membership set** with 5 `NewType` identifier types. This rewrites FR-9 entirely.
- **5 key formats were eliminated** (Key_A, Key_D, Key_E full, Key_F, bare) — proven to have zero resolution hits across 6 models. The spec references all of these in FR-9 and must stop treating them as live.
- Resolution changed from **"try everything in order" cascade** to **type-directed dispatch** based on `BindingType` (CHAIN vs REFERENCE). This rewrites FR-8 (dual resolution) and the strategy chain in FR-8's Path 2.
- FORMULA resolution was narrowed: it uses a **pre-computed attribute map**, NOT the `resolve_input()` strategy chain. The spec's FR-8 Path 2 conflates FORMULA and Aggregation into one path — there are actually **three resolution mechanisms**.
- **Strategy B (SysML QN normalization)** has a 100% failure rate and is marked `REMOVAL_CANDIDATE`. The spec lists it as strategy #3 of 5 — it should be flagged or removed.

## Detailed Findings: Spec Section Impact Map

### FR-1: Narrative Structure — The 7-Step Proof

**Impact: MEDIUM — Table and sub-step naming need updates**

The 7-step table (lines 95-106) references outdated concepts:

| Spec Line | Current Text | Problem | Fix |
|-----------|-------------|---------|-----|
| Step 2 | "Key_A through Key_F populated" | Key_A, Key_D, Key_E full, Key_F, bare are eliminated | Change to "ScopedKey, SysMLQN, CanonicalChannel registries populated" |
| Step 5.5 | "Build OutputRegistry (4-phase)" | Correct concept, but the spec doesn't mention typed registries | Add: "across 3 typed registries (scoped, SysML QN, alias)" |

The sub-steps (3.5, 4.5, 5.5) and ordering constraints are still correct.

### FR-3: ComputationGraph as Single Source of Truth

**Impact: LOW — No changes needed**

The ComputationGraph abstraction boundary is unchanged. If anything, the typed registry refactor strengthens the "single source of truth" claim — generation still consumes only ComputationGraph fields.

### FR-5: Three Module Types and Pure Factories

**Impact: LOW — Factory signatures unchanged**

The three factory types (CalcUsage, FORMULA, Aggregation) and their pure-function signatures are unchanged. The tuple return `(PipelineModule, dict[str, EntryPoint])` is still correct.

One clarification needed: the spec says FORMULA modules use the same `resolve_input()` as Aggregation. Per the STRATEGY.md Session 18 finding and doc 24, FORMULA actually uses a **pre-computed attribute resolution map** — no strategy chain at all. This is an existing spec inaccuracy that pre-dates the TRR but should be corrected.

### FR-7: Aggregation Decomposition

**Impact: LOW — Mostly unchanged**

The three term types (SumTerm, SingletonTerm, LocalTerm) and the aggregation cascade are unchanged. The LocalTerm 3-strategy resolution (sibling aggregation output -> EXPOSE_PURE alias -> entry point fallback) is still correct.

Minor: `_find_literal_redefinition()` still applies. The resolution strategies now use typed registry methods instead of `dict.get()`, but the explainer describes behavior, not implementation — so the narrative is unchanged.

### FR-8: Dual Resolution Architecture — MAJOR REWRITE

**Impact: CRITICAL — This section is substantially wrong**

FR-8 is the most affected section. Five areas need rewriting:

#### 8a. Path count: Two paths → Three mechanisms

The spec says:

> Path 1: Backtracker (CalcUsage modules)
> Path 2: resolve_input() (FORMULA + Aggregation modules)

The design now specifies **three** resolution mechanisms (REQ-RES-02):

| Mechanism | Module Types | When |
|-----------|-------------|------|
| `_resolve_binding_via_registry()` in backtracker | CalcUsage | During DFS traversal |
| Pre-computed attribute resolution map | FORMULA | After DFS, during module building |
| `resolve_input()` with strategy chain | Aggregation SumTerm/SingletonTerm | After DFS, during module building |

(Plus a 4th for LocalTerm: factory-specific 3-strategy cascade)

FORMULA modules do NOT use `resolve_input()`. They use a map pre-built from computed attribute analysis. This is a structural difference, not an implementation detail — FORMULA inputs are resolved before any strategy chain runs.

#### 8b. Backtracker resolution: cascade → type-directed dispatch

The spec says (FR-8, Path 1):

> MUST show the DFS traversal: backtracker encounters a binding, resolves it

The backtracker's resolution is now **type-directed dispatch** based on the binding's `source_path` format:

- **CHAIN bindings** (no `::` in source_path): scoped registry (`ScopedKey`) → alias registry → design attr → fallback
- **REFERENCE bindings** (`::` in source_path): SysML QN registry (`SysMLQN`) → normalized scoped → design attr → fallback

This dispatch replaces the old "try Steps 0, 1, 1b, 2 against one flat dict" cascade. The explainer should show the **dispatch decision** (is this CHAIN or REFERENCE?) as the first resolution step, then the typed lookup.

#### 8c. Strategy chain: 5 strategies → 4 strategies (Strategy B flagged)

The spec lists 5 strategies in order (lines 198-204):

| Position | Strategy | Status |
|----------|----------|--------|
| C | ScopedRegistryLookup | **Active** — now uses typed `ScopedKey` lookup |
| A | DirectRegistryLookup (Key_A) | **ELIMINATED** — Key_A is dead; this strategy was rewritten to use scoped lookup |
| B | SysmlQnNormalization | **REMOVAL_CANDIDATE** — 0% success rate across 94 bindings, 3 models |
| D | ChainRedefinitionFollow | **Active** — unchanged |
| E | DesignAttributeLookup | **Active** — unchanged |

The strategy chain for `resolve_input()` (Aggregation only) is now effectively 4 strategies:

| Position | Strategy | Typed Registry Used |
|----------|----------|-------------------|
| A | ScopedRegistryLookup | `scoped_lookup(ScopedKey)` then `alias_lookup(ScopedKey)` |
| B | SysMLQNLookup | `sysml_qn_lookup(SysMLQN)` (if `::` in ref) |
| C | ChainRedefinitionFollow | follows `:>>` chains, cycle-safe |
| D | DesignAttributeLookup | bare name match against design attrs |

`AGG_STRATEGIES` reorders to `[A, C, B, D]` (ChainRedefinitionFollow promoted to position 2).

Note: The old "Strategy A = DirectRegistryLookup (Key_A)" is gone. The new "Strategy A = ScopedRegistryLookup" is a different thing — it queries the typed scoped registry, not the flat index. The spec's labeling needs to be updated to avoid confusion.

#### 8d. Output models: same semantic, different types

The two resolution paths produce different output types that the explainer should distinguish:

- Backtracker → `BindingResolution` (with `resolution_type: MODULE_OUTPUT | ENTRY_POINT`)
- `resolve_input()` → `InputSource` (with `source_type: module_output | entry_point`)

Same binary answer, different types. The consistency guarantee (REQ-DRA-04) ensures they produce the same wiring for the same reference.

#### 8e. Composition proof: typed registries guarantee consistency

The spec says:

> MUST pick one concrete reference that both paths could resolve
> MUST show both paths arriving at the same InputSource / wiring decision

This is still correct and now MORE demonstrable — both paths query the same typed registries (scoped, SysML QN, alias), just through different APIs. The typed registry is the shared truth that ensures consistency.

### FR-9: OutputRegistry and Key Formats — MAJOR REWRITE

**Impact: CRITICAL — Almost entirely rewritten**

#### 9a. Registry data structure

The spec says (line 216):

> MUST show it as a flat `dict[str, str]` mapping alias → canonical channel

Replace with:

> MUST show it as three typed registries + one membership set:
> - `_scoped: dict[ScopedKey, CanonicalChannel]` — hierarchy-qualified lookups
> - `_sysml_qn: dict[SysMLQN, CanonicalChannel]` — `Package::Element` format lookups
> - `_alias: dict[ScopedKey, CanonicalChannel]` — CHAIN/EXPOSE_PURE/transitive aliases
> - `_canonical: set[CanonicalChannel]` — membership check for phase ordering

#### 9b. 4-phase build protocol

The spec's 4-phase description (lines 218-223) needs updating:

| Phase | Spec Currently Says | What It Should Say |
|-------|-------------------|-------------------|
| Phase 1a | "Key_A (`cost_model.total_cost`), Key_B (`BatteryPackCostCalc.total_cost`), Key_C (`plant.battery_system.battery_pack.cost_model.total_cost`)" | Register into **scoped** registry via `ScopedKey` (the old Key_C) + register `CanonicalChannel` into `_canonical` set. Key_A and Key_B are NOT registered. |
| Phase 1b | "Aggregation outputs → Key_D, Key_E, stripped variants" | Register into **scoped** registry via `ScopedKey` (the old Key_E_stripped). Key_D is NOT registered. |
| Phase 1c | "FORMULA outputs → Key_F, bare, SysML QN" | Register into **SysML QN** registry. Key_F and bare are NOT registered. |
| Phase 2 | "CHAIN aliases (`:>>` redefinition chains)" | Register into **alias** registry. Target must exist in `_canonical` (enforced by API). |
| Phase 3 | "EXPOSE_PURE aliases" | Register into **alias** registry. |
| Phase 4 | "Transitive design attribute aliases" | Register into **alias** registry. |

#### 9c. The scope problem narrative

The spec says (line 224):

> MUST show the scope problem: two parts containing identically-named `cost_model` usages — Key_A is ambiguous, Key_C disambiguates

The narrative is now stronger: Key_A is not just ambiguous — **it is not registered at all**. The scope problem is solved by only registering scoped keys (`ScopedKey`), making ambiguity impossible by construction. The explainer should show:

1. Why bare instance names (`cost_model.total_cost`) are ambiguous (two parts can have the same usage name)
2. Why the old design registered them anyway (Key_A) — and the empirical proof they had zero hits
3. Why `ScopedKey` (hierarchy-qualified, design prefix stripped) is unique by SysML ownership semantics
4. The typed registry ensures you can't accidentally query with the wrong key format

#### 9d. Interactive registry explorer

The spec says (line 225):

> SHOULD be interactive: let the user select a reference and see which key format matches

Update to: let the user select a reference and see **which typed registry is queried** (based on CHAIN vs REFERENCE dispatch) and **what ScopedKey or SysMLQN is constructed**.

### FR-10: Entry Point Classification

**Impact: LOW — Minor path description update**

The spec says (lines 237-238):

> Path 1: Backtracker → `_classify_entry_points()` (3-strategy, full binding context)
> Path 2: Factory fallback → hardcoded `DESIGN_ATTRIBUTE` (FORMULA/Aggregation factories lack binding context)

This is still correct. The typed registry refactor doesn't change entry point classification — it changes how resolution decides "this is an entry point" but not how entry points are typed after creation.

### Narrative Outline (Acts 1-4)

**Impact: MEDIUM — Act 2 and Act 3 need updates**

#### Act 2, Step 2 (Build Registry)

> Show Key_A/B/C for `pv_module_cost_model.total_cost`. Show why Key_C exists (scope disambiguation).

Update to: Show the three typed registries being populated. Show `ScopedKey` construction (the old Key_C) for the scoped registry. Show why typed registries exist: prevent the ambiguity that Key_A (unscoped) allowed.

#### Act 2, Step 5.5 (Build OutputRegistry 4-phase)

> Show the registry growing across 4 phases. Show the scope problem and Key_C resolution.

Update to: Show the three registries growing across 4 phases. Show phase ordering enforcement (alias registration rejects unknown canonical channels). Show `ScopedKey` as the load-bearing resolution key.

#### Act 3c (Dual Resolution)

> Side-by-side: Backtracker path (DFS + binding context) vs `resolve_input()` (strategy chain).

Update to: Three-way comparison:
1. Backtracker (DFS + type-directed dispatch on CHAIN/REFERENCE)
2. FORMULA (pre-computed attribute map — no runtime strategy chain)
3. Aggregation (`resolve_input()` with reordered `AGG_STRATEGIES`)

Show why they can't merge (backtracker resolution is embedded in DFS traversal; FORMULA resolution is pre-computed; aggregation needs a strategy chain because its references span scopes).

## New Concepts the Explainer Must Introduce

### 1. Typed Identifiers (5 NewType wrappers)

The explainer should introduce the type system early (Act 2, Step 1 or Step 2) with a conversion boundary diagram:

```
SysML Model → SysMLQN (Package::Element)
                  ↓ extraction boundary
              EQN (Package__Element)
                  ↓ extend with param
              PQN (Package__Element__param)
                  ↓ used as
              CanonicalChannel (PQN of output — registry value)
              ScopedKey (dotted hierarchy — registry key)
```

### 2. Type-Directed Dispatch

The CHAIN vs REFERENCE dispatch decision is a new concept that replaces the old "try everything" cascade. The explainer should show:

- How binding `source_path` is classified (contains `::` → REFERENCE, else → CHAIN)
- Each dispatch path queries a **different registry** as its first step
- This prevents cross-format confusion (a scoped key can never accidentally match a SysML QN)

### 3. Phase Ordering Enforcement

The `register_alias()` API enforces that alias targets must already exist in `_canonical`. This is a new concept: the registry **rejects** out-of-order registration attempts. The explainer should show a Phase 2 alias that successfully registers (because its Phase 1a target exists) and explain what would happen if phases were reordered.

## Empirical Data the Explainer Can Cite

The research spikes provide concrete numbers for the "why" narrative:

| Claim | Evidence |
|-------|----------|
| Key_A has zero resolution hits | 0/150 across 6 models (Key_A fallback spike) |
| Key_A has real collisions | 10+ in `catf_mfe` (pump_load.pump_power maps to 2 producers) |
| Strategy B (SysML QN normalization) fails 100% | 0/94 exercised bindings across 3 models |
| ScopedKey (Key_C) is load-bearing | 27/27 backtracker scoped resolutions, 41/41 Phase 2 CHAIN aliases |
| 42% of historical bugs were naming/resolution failures | 8 of 19 bugs across 37 commits |
| Typed identifiers prevent the #1 bug category | Catches format mismatches at mypy time |

## Spec Sections Requiring NO Changes

These sections are unaffected by the TRR:

- **FR-2**: Solar Plant Hierarchy Diagram — pure visualization, no resolution concepts
- **FR-3**: ComputationGraph as Single Source of Truth — abstraction boundary unchanged
- **FR-4**: Computation Graph DAG — visualization layer, module types unchanged
- **FR-6**: Template Instantiation and Virtual Binding Rewrite — Step 3.5 is upstream of resolution
- **FR-11**: Generated Output Traceability — ComputationGraph → generation is unchanged
- **FR-12**: SysML Visual Glossary — SysML concepts unchanged
- **FR-13**: Navigation and Interactivity — pure UX
- **FR-14**: Progressive Disclosure — pure UX
- **FR-15**: Plain-English Explanations — style guide

## Recommendations

### Priority 1: Rewrite FR-9 (OutputRegistry)

This is the most visible change. The entire section must switch from "flat dict with 12 key formats" to "3 typed registries with 3 key types." The 4-phase protocol description must be updated to show which registry each phase populates.

### Priority 2: Rewrite FR-8 (Dual Resolution)

Split Path 2 into two: FORMULA (attribute map) and Aggregation (`resolve_input()`). Add type-directed dispatch (CHAIN vs REFERENCE) to Path 1. Update the strategy chain to remove dead strategies and show typed registry queries.

### Priority 3: Update FR-1 table

Replace "Key_A through Key_F" with typed registry names. Small change, high visibility.

### Priority 4: Add typed identifiers section

Either as a new FR or as an expansion of FR-9, introduce the 5 NewType wrappers and the conversion boundary. This is fundamental to understanding why the new architecture prevents bugs.

### Priority 5: Update narrative outline (Acts 2-3)

Align the narrative walkthrough with the updated FRs. The concrete examples should show `ScopedKey` construction, typed dispatch decisions, and alias phase ordering.

### What NOT to Change

Do not expand the scope of the explainer to cover the TRR migration path, the `_compat` bridge, or implementation details of typed constructors. The explainer depicts the refactored design "as if complete" — it should show the final state, not the transition.

## Open Questions

1. **Should Strategy B appear in the explainer at all?** It's marked `REMOVAL_CANDIDATE` with 0% hit rate. Including it adds complexity with no explanatory value. But if it's not yet removed from the design docs, the explainer should be consistent.

2. **How deeply should typed identifiers be explained?** They're `NewType` wrappers (zero runtime cost), which is an implementation detail. The explainer's audience cares about "there are 3 key formats, each in its own registry" — not `NewType` mechanics.

3. **Should the explainer cite the empirical data?** The Key_A spike numbers make a compelling "why" narrative ("we proved that 5 of 12 key formats had zero hits"). This would strengthen the explanation but adds a historical dimension the spec currently avoids.

## Cross-References

- **Pipeline Explainer Spec**: `.project/active/new-pipeline-explainer/spec.md`
- **TRR Design Doc**: `.project/concepts/refactor-design-intent/27-typed-registry-refactor.md`
- **TRR Active Spec**: `.project/active/typed-registry-refactor/spec.md`
- **Key_A Fallback Spike**: `.project/research/20260217-060000_key-a-fallback-spike.md`
- **Mistakes and Learnings**: `.project/research/20260217-030000_mistakes-and-learnings-since-a6310a4b.md`
- **Phase 0/1/TRR Verification**: `.project/research/20260217-080000_phase-0-1-trr-verification.md`
- **Design Intent Docs Modified**: 03, 04, 09, 10, 11, 15, 24, 27 (8 of 27)

## Implementation Status

All priority recommendations from this research have been addressed. Changes applied to: spec.md, design.md, plan.md, new_pipeline_explainer.html.

| Priority | Recommendation | Status | Notes |
|----------|---------------|--------|-------|
| P1 | Rewrite FR-9 (OutputRegistry) | **Done** | Spec: flat dict → 3 typed registries. HTML: MODEL_DATA, renderStep2(), renderStep55() all updated. |
| P2 | Rewrite FR-8 (Dual Resolution) | **Done** | Spec: 2 paths → 3 mechanisms. HTML: DualResolutionDemo rewritten with 3-panel layout, type-directed dispatch, FORMULA attribute map panel. |
| P3 | Update FR-1 table | **Done** | "Key_A through Key_F" → "3 typed registries: scoped, SysML QN, alias" |
| P4 | Add typed identifiers | **Done** | Integrated into FR-9 (ScopedKey, SysMLQN, CanonicalChannel introduced). HTML Step 2 expandable section explains all three. |
| P5 | Update narrative outline | **Done** | Acts 2 and 3c updated in spec. HTML renderers updated accordingly. |

### Open Questions Resolved

1. **Strategy B (SysmlQnNormalization)**: Omitted entirely from explainer. 0% hit rate, marked REMOVAL_CANDIDATE — no value showing dead code.
2. **Typed identifiers depth**: Explained as "3 key formats, each in its own registry" with names (ScopedKey, SysMLQN, CanonicalChannel). NewType mechanics omitted.
3. **Empirical data**: Yes, included. Brief callout in Step 2 scope visual: "0/150 Key_A hits across 6 models; 10+ collisions in catf_mfe."
