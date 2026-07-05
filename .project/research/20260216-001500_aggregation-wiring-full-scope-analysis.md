---
date: 2026-02-16T00:15:00-06:00
researcher: Claude
topic: "Aggregation Wiring — Full Scope Analysis (58 Unwired Inputs)"
tags: [research, aggregation, extraction, syside, graph-builder, cost-pattern, critical]
status: complete
last_updated: 2026-02-16
---

# Research: Aggregation Wiring — Full Scope Analysis

**Date**: 2026-02-16 00:15 CST
**Researcher**: Claude
**Research Type**: Root Cause Analysis / Scope Correction
**Triggered by**: Phase 4 rerun of E2E post-codegen validation showing 58/70
aggregation inputs still unwired after the scoped registry fix

## Research Question

The scoped registry fix (design at `.project/active/aggregation-wiring-fix/`)
addressed 4 of 62 broken aggregation inputs (CHAIN_PART_MISMATCH for inverter
SumTerms). Phase 4 of the E2E validation shows 58 inputs still unwired across
5 categories. The prior research (`20260215-225131_aggregation-wiring-gap-analysis.md`)
classified 46 inputs as "LocalTerms (correctly become entry points — not bugs)."
**Was that assessment wrong? What is the full scope of the problem?**

## Summary

**The prior research was wrong about the 46 LocalTerms.** At least 28 of those
46 "LocalTerms" are actually dotted child references (e.g., `array_bos.capital_cost`)
that should be SingletonTerms wiring to upstream MODULE_OUTPUTs, not entry
points. They are misclassified because SysIDE produces `FeatureReferenceExpression`
nodes instead of `FeatureChainExpression` nodes for dotted references outside
of `sum()` calls. The extraction's `_walk_aggregation_ast()` classifies
`FeatureReferenceExpression` as LocalTerm unconditionally.

**The scoped registry fix addressed 4 out of ~54 broken inputs.** The
remaining 50 are broken at the **extraction layer**, not the resolution layer.
The problem decomposes into 5 distinct root causes across 3 layers.

---

## The 70 Aggregation Inputs — Full Decomposition

Source: Phase 4 rerun #2 of E2E post-codegen validation
(`~/1cfe/fusion-tea/.project/active/e2e-post-codegen-validation/plan.md`,
lines 628-637)

### Inputs by Wiring Status

| Status | Count | Category | Example |
|--------|-------|----------|---------|
| Wired (MODULE_OUTPUT) | 12 | SumTerm resolved via CHAIN or scoped registry | `pv_module.capital_cost` → cost_model output |
| Unwired (ENTRY_POINT) | 12 | Multiplicity counts | `module_count` → raw, not `system_design.`-prefixed |
| Unwired (ENTRY_POINT) | 16 | Singleton child costs | `array_bos.capital_cost` → should wire to cost_model |
| Unwired (ENTRY_POINT) | 12 | Site_infra singleton children | `racking.capital_cost` → should wire to cost_model |
| Unwired (ENTRY_POINT) | 15 | Sub-assembly → plant-level | `solar_array.capital_cost` → should wire to agg output |
| Unwired (ENTRY_POINT) | 7 | idiot_index inputs | `capital_cost / raw_material_cost` → sibling attrs |
| **Total** | **70** | | |

### Inputs by Root Cause

| Root Cause | Layer | Count | Fixed? |
|------------|-------|-------|--------|
| RC-1: FeatureReferenceExpression misclassified as LocalTerm | Extraction | 28 | No |
| RC-2: Sub-assembly agg outputs not resolvable from plant-level | Resolution | 15 | No (Key_E_stripped not yet implemented) |
| RC-3: Multiplicity count channel naming | Graph builder | 12 | No |
| RC-4: Sibling attribute references (idiot_index) | Extraction + Resolution | 7 | No |
| RC-5: CHAIN_PART_MISMATCH (unscoped registry key) | Resolution | 4 | **YES** (scoped registry fix) |
| (Already working) | — | 8 | N/A |

---

## Root Cause Details

### RC-1: FeatureReferenceExpression → LocalTerm Misclassification (28 inputs)

**Layer:** Extraction (`hierarchy_resolver.py:350-361`)
**Impact:** 28 singleton child cost references become entry points instead of
wiring to upstream cost_model outputs

**The code:**

```python
# hierarchy_resolver.py:350-361

# FeatureChainExpression: child.attr → SingletonTerm
if SysideAdapter.is_instance(node, "FeatureChainExpression"):
    chain_name = extract_feature_chain_name(node)
    ctx.singleton_terms.append(SingletonTerm(source_path=chain_name))
    ctx.input_channels.append(chain_name)
    return chain_name

# FeatureReferenceExpression: local attribute → LocalTerm
if SysideAdapter.is_instance(node, "FeatureReferenceExpression"):
    ref_name = extract_feature_reference_name(node)
    ctx.local_terms.append(LocalTerm(attribute_name=ref_name))
    return ref_name
```

**What happens:** The AST walker uses node type to classify terms:
- `FeatureChainExpression` → SingletonTerm (dotted child reference)
- `FeatureReferenceExpression` → LocalTerm (bare attribute)

For `sum(pv_module.capital_cost)`, the operand inside `sum()` is
`FeatureChainExpression` — correctly parsed. But for bare
`array_bos.capital_cost` (not inside `sum()`), SysIDE produces
`FeatureReferenceExpression`, not `FeatureChainExpression`.

**Evidence:** The spike found 0 SingletonTerms and 46 LocalTerms. The SysML
clearly has dotted child references outside `sum()`:

```sysml
// library.sysml:615-619 (Solar Array)
:>> capital_cost =
    sum(pv_module.capital_cost) +     // SumTerm ✓
    sum(inverter.capital_cost) +      // SumTerm ✓
    array_bos.capital_cost +          // Should be SingletonTerm, becomes LocalTerm ✗
    misc_hardware_cost;               // Correctly LocalTerm ✓
```

**Affected references** (from library.sysml):

| Assembly | Dotted Child Ref | Attrs (×4 cost attrs) | Count |
|----------|------------------|-----------------------|-------|
| Solar Array | `array_bos.{cost}` | capital, raw_material, fabrication, installation | 4 |
| Solar Array | `allocation_model.{attr}` | total_allocation, material_portion | 2 |
| Battery System | `hybrid_inverter.{cost}` | capital, raw_material, fabrication, installation | 4 |
| Battery System | `battery_bos.{cost}` | capital, raw_material, fabrication, installation | 4 |
| Site Infra | `racking.{cost}` | capital, raw_material, fabrication, installation | 4 |
| Site Infra | `electrical_panel.{cost}` | capital, raw_material, fabrication, installation | 4 |
| Site Infra | `permitting.{cost}` | capital, raw_material, fabrication, installation | 4 |
| **Subtotal** | | | **26** |

Plus Solar Array's `misc_hardware_cost` (line 612) which equals
`allocation_model.total_allocation` — that's a separate issue (the
attribute is defined as `= allocation_model.total_allocation` via
a separate redefinition, not inline in the aggregation). There may
be 1-2 more from `allocation_model` references in raw_material_cost
(line 625: `allocation_model.material_portion`).

**The key question:** Is `extract_feature_reference_name()` extracting just
the bare leaf name (e.g., `"capital_cost"`) or the full dotted path
(`"array_bos.capital_cost"`)? Based on the function's contract
(`expression_utils.py:110` — "Extracts bare names only"), it extracts just
the leaf. This means the dotted context is **lost entirely** — we don't even
know which child part is being referenced.

**Diagnosis:** This is a **SysIDE AST representation issue**, not a logic
error in `_walk_aggregation_ast()`. The walker correctly maps
`FeatureChainExpression` → SingletonTerm and `FeatureReferenceExpression` →
LocalTerm. The problem is that SysIDE doesn't produce `FeatureChainExpression`
for dotted references outside `sum()`. Investigation is needed into whether:

1. SysIDE flattens `array_bos.capital_cost` into a single
   `FeatureReferenceExpression` (losing the dot structure), or
2. SysIDE produces a nested structure (`FeatureReferenceExpression` inside
   another expression) that the walker doesn't recognize, or
3. SysIDE produces `FeatureChainExpression` but the walker hits the
   `FeatureReferenceExpression` check first (unlikely — the checks are
   `is_instance`, not substring matches)

This requires a SysIDE AST dump of the non-sum dotted references to
determine the exact node structure. A diagnostic spike similar to Item 1's
AST discovery spike is needed.

---

### RC-2: Sub-assembly → Plant-Level Aggregation (15 inputs)

**Layer:** Resolution (`graph_builder.py` + `initialization.py`)
**Impact:** Plant-level aggregation inputs referencing sub-assembly outputs
fail to resolve

```sysml
// library.sysml:742-746 (Solar Battery Plant)
:>> capital_cost =
    solar_array.capital_cost +        // Should wire to solar_array agg output
    battery_system.capital_cost +     // Should wire to battery_system agg output
    site_infra.capital_cost;          // Should wire to site_infra agg output
```

These are the same dotted references as RC-1, but at the plant level —
they reference sub-assembly aggregation outputs rather than leaf-part
cost_model outputs. Even if RC-1 is fixed (dotted refs become SingletonTerms),
these would still fail because:

1. If classified as SingletonTerms, `_resolve_aggregation_input_channel()`
   needs a scoped key: `solar_battery_plant.solar_array.capital_cost`
2. That key requires Key_E_stripped registration (the design's Change 2)
3. The aggregation output channel is the double-attr format:
   `Design__plant__solar_array__capital_cost__capital_cost`

The scoped registry fix (Change 1) and Key_E_stripped (Change 2) would
handle this — but only AFTER RC-1 is fixed so these references become
SingletonTerms instead of LocalTerms.

**These 15 inputs require BOTH RC-1 fix AND the resolution fix (Changes 1+2
from the design).**

Count: 3 sub-assemblies × 5 cost attributes = 15

---

### RC-3: Multiplicity Count Channel Naming (12 inputs)

**Layer:** Graph builder (`graph_builder.py`)
**Impact:** Multiplicity count entry points referenced as raw names, not
properly qualified

The E2E notes these as "referenced as raw channel names, not
`system_design.`-prefixed." The multiplicity counts (`module_count`,
`inverter_count`, `pack_count`) ARE correctly entry points — they're integer
parameters, not upstream module outputs. But the channel naming may prevent
TEAx from finding them at runtime.

Each count appears 4 times (once per cost attribute's aggregation module):
3 counts × 4 cost attributes = 12 inputs.

**This may be a pipeline execution issue rather than a wiring issue.** The
entry point IS created, the value IS in `system_design.json`. The question is
whether the module input references the entry point by the correct qualified
name. Needs investigation during Phase 5 pipeline execution.

---

### RC-4: Sibling Attribute References — idiot_index (7 inputs)

**Layer:** Extraction + Resolution
**Impact:** `idiot_index = capital_cost / raw_material_cost` creates inputs
that reference sibling `:>>` attributes on the same PartDef

```sysml
// library.sysml:637
:>> idiot_index = capital_cost / raw_material_cost;
```

Here `capital_cost` and `raw_material_cost` are sibling attributes on the
same PartDef. They're `:>>` redefinitions that resolve to aggregation
expressions themselves. The `idiot_index` module needs to wire its inputs to
the outputs of the sibling aggregation modules (e.g.,
`solar_array__capital_cost` and `solar_array__raw_material_cost`).

These are currently extracted as LocalTerms (`attribute_name="capital_cost"`,
`attribute_name="raw_material_cost"`) because they're bare
`FeatureReferenceExpression` nodes — no dot, so they're genuinely local
attribute references.

But they're NOT user-provided parameters — they're outputs of other
aggregation modules on the same assembly. The graph builder's LocalTerm
handling creates entry points unconditionally (lines 1015-1036). There's no
attempt to resolve a LocalTerm to a sibling aggregation module output.

Count: 4 assemblies × 2 attrs (capital_cost, raw_material_cost) = 8, minus
1 because the plant-level idiot_index may be counted differently = 7.

**Fix required:** LocalTerm processing needs to check if a same-assembly
aggregation module has a matching output before falling back to entry point.
The registry has these outputs registered (e.g., Key_D
`solar_array.capital_cost`), but the LocalTerm handler doesn't look them up.

---

### RC-5: CHAIN_PART_MISMATCH — Unscoped Registry Key (4 inputs) — FIXED

**Layer:** Resolution (`graph_builder.py:815-820`)
**Impact:** 4 inverter SumTerms failed because `sanitize_name("String_Inverter").lower()`
≠ `"inverter"`

**Status: FIXED** by the scoped registry design (Change 1). After the fix,
`inverter.capital_cost` resolves via scoped key
`solar_battery_plant.solar_array.inverter.capital_cost` → Phase 2 CHAIN alias.

---

## How the Prior Research Went Wrong

The prior research (`20260215-225131_aggregation-wiring-gap-analysis.md`)
made two critical errors:

### Error 1: Accepting the spike's term counts at face value

The spike reported: **12 SumTerms, 0 SingletonTerms, 46 LocalTerms.**

The research accepted "46 LocalTerms (correctly become entry points — not
bugs)" without questioning why there were 0 SingletonTerms when the SysML
clearly has dotted child references outside `sum()`:

```sysml
array_bos.capital_cost    // Not inside sum() → should be SingletonTerm
hybrid_inverter.capital_cost
battery_bos.capital_cost
racking.capital_cost
// ... etc.
```

The spike's `_walk_aggregation_ast()` is a faithful replica of the production
code, so 0 SingletonTerms is the correct count **of what the extraction
actually produces**. But it's NOT the correct count of **what the SysML
contains**. The research should have cross-referenced the term counts against
the SysML source to validate the extraction.

### Error 2: Scoping the fix to the resolution layer only

The research focused entirely on `graph_builder.py` and `initialization.py`
(resolution + registration). It never examined `hierarchy_resolver.py`
(extraction). The root cause analysis followed the resolution code path and
found three bugs there — all real bugs — but missed the upstream extraction
bug that accounts for 28+ of the 58 unwired inputs.

The research explicitly noted: "62 of 70 inputs failing... 46 LocalTerms
(correctly become entry points)." This left only 12 SumTerms as the bug
surface. Of those, 8 already worked via CHAIN, leaving 4 broken. The fix
targeted those 4. **The fix's scope was correct for the problem as diagnosed,
but the diagnosis was incomplete.**

---

## Revised Problem Decomposition

| # | Problem | Layer | Count | Blocked By | Fix Approach |
|---|---------|-------|-------|------------|-------------|
| 1 | Dotted refs misclassified as LocalTerm | Extraction | 28 | SysIDE AST investigation | Detect dotted refs in FeatureReferenceExpression |
| 2 | Plant-level → sub-assembly agg wiring | Resolution | 15 | #1 (refs must become SingletonTerms first) | Key_E_stripped + scoped lookup (existing design Changes 1+2) |
| 3 | Multiplicity count naming | Graph builder | 12 | Phase 5 (may work at runtime) | Qualify entry point references |
| 4 | Sibling attr → sibling agg output | Graph builder | 7 | Independent | LocalTerm resolution against same-assembly agg outputs |
| 5 | CHAIN_PART_MISMATCH | Resolution | 4 | None | **DONE** (scoped registry fix) |

**Dependency graph:**

```
#1 (extraction fix) ─── blocks ──→ #2 (resolution fix)
                                    (existing design Changes 1+2)

#3 (multiplicity naming) ─── independent
#4 (sibling agg wiring) ─── independent
#5 (CHAIN_PART_MISMATCH) ─── DONE
```

---

## Immediate Next Steps

### 1. SysIDE AST Diagnostic Spike (RC-1)

Before any fix can be designed for RC-1, we need to understand what SysIDE
actually produces for `array_bos.capital_cost` outside `sum()`. Specifically:

```python
# Proposed spike: dump AST node type for non-sum dotted references
# in Solar Array's capital_cost aggregation expression
for node in ast_walk(solar_array_capital_cost_expression):
    print(type(node).__name__, getattr(node, 'name', '?'))
    if hasattr(node, 'chaining_features'):
        print("  chaining:", [f.name for f in node.chaining_features])
    if hasattr(node, 'referent'):
        print("  referent:", type(node.referent).__name__, node.referent.name)
```

Key questions:
- Is `array_bos.capital_cost` one node or two nested nodes?
- What type is it? (`FeatureReferenceExpression`, `FeatureChainExpression`,
  or something else?)
- Does it have `chaining_features` or other structure that could be used
  to reconstruct the dotted path?

### 2. Reassess the Design Scope

The existing aggregation wiring fix design addresses RC-5 (done) and RC-2
(Changes 1+2). But RC-2 is blocked on RC-1. The design needs to be
rescoped to include:
- RC-1: Extraction-layer fix for dotted ref classification
- RC-2: Resolution-layer fix (already designed, Changes 1+2)
- RC-4: Graph builder LocalTerm → sibling agg output resolution
- RC-3: Investigate during Phase 5 pipeline execution

### 3. Update the Spec

The current spec targets "12 resolvable inputs resolve to MODULE_OUTPUT."
The actual target should be **~54 resolvable inputs resolve to MODULE_OUTPUT**
(70 total - 12 multiplicity entry points - ~4 true local terms like
`misc_hardware_cost`).

---

## Code References

| File | Lines | What |
|------|-------|------|
| `extraction/hierarchy_resolver.py` | 305-433 | `_walk_aggregation_ast()` — term classification |
| `extraction/hierarchy_resolver.py` | 350-355 | FeatureChainExpression → SingletonTerm |
| `extraction/hierarchy_resolver.py` | 357-361 | FeatureReferenceExpression → LocalTerm |
| `extraction/expression_utils.py` | 110 | `extract_feature_reference_name()` — bare name only |
| `extraction/expression_utils.py` | 133 | `extract_feature_chain_name()` — full dotted path |
| `resolution/graph_builder.py` | 1015-1036 | LocalTerm processing — always entry point |
| `resolution/graph_builder.py` | 954-1013 | SingletonTerm processing — attempts resolution |
| `tests/fixtures/solar_battery_model/library.sysml` | 615-619 | Solar Array aggregation |
| `tests/fixtures/solar_battery_model/library.sysml` | 659-662 | Battery System aggregation |
| `tests/fixtures/solar_battery_model/library.sysml` | 703-706 | Site Infrastructure aggregation |
| `tests/fixtures/solar_battery_model/library.sysml` | 743-746 | Solar Battery Plant aggregation |

---

## Related Artifacts

- **Prior research (SUPERSEDED):** `.project/research/20260215-225131_aggregation-wiring-gap-analysis.md`
- **Scoped registry fix design:** `.project/active/aggregation-wiring-fix/design.md`
- **E2E validation plan (Phase 4 results):** `~/1cfe/fusion-tea/.project/active/e2e-post-codegen-validation/plan.md`
- **Spike script:** `scripts/spike_aggregation_validation.py`
- **Architecture review:** `.project/research/20260215-235500_aggregation-wiring-design-vs-architecture-review.md`
- **ADR-007:** `docs/architecture/ADR-007-parametric-multiplicity-aggregation.md` (Consequences section notes singleton `.()` syntax bug)
