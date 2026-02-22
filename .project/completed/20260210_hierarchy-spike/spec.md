# Spec: SysIDE AST Discovery for Hierarchy Patterns

**Status:** Draft
**Owner:** Reid Westwood
**Created:** 2026-02-10T03:30:02Z
**Complexity:** MEDIUM
**Branch:** cost-pattern
**Epic:** COST-PATTERN (Item 1)

---

## Business Goals

### Why This Matters

The COST-PATTERN epic (~8-10 days) targets native support for the Costed Component pattern: PartDefinitions with embedded CalcUsages, `:>>` redefinition chains, parameterized multiplicity, and `sum()` aggregation. Every implementation decision in Items 2-5 depends on how SysIDE represents these constructs in its AST.

The January 2026 research document (`20260109-205122_cost-modeling-codegen-changes.md`) flagged open questions about the `:>>` API, `redefines` representation, and implicit vs explicit redefinition. These remain unanswered. The agentic-mbse package has the syside metamodel types available (`Redefinition`, `Specialization`, `Multiplicity`, `MultiplicityRange`) but hasn't wrapped any of them -- we don't yet know what the raw syside API looks like for these elements.

This spike answers those questions empirically, using the solar_battery model as a probe target. It is a go/no-go gate: if SysIDE lacks critical capabilities, the epic must be re-scoped before investing in implementation.

### Success Criteria

- [ ] All questions in Section "Questions to Answer" answered with concrete AST examples
- [ ] Go/no-go decision made with rationale
- [ ] Any SysIDE gaps documented (no fallback prototypes -- just gap documentation)
- [ ] Report is usable as a direct reference during Items 2-4 implementation

### Priority

P1 -- gates Items 2-5 of COST-PATTERN epic. No implementation should begin until this completes.

---

## Problem Statement

### Current State

- CalcUsages in PartDefinitions are extracted but not instantiated per PartUsage
- `:>>` redefinitions are invisible to codegen
- Multiplicity (`[count]`) is ignored
- `sum()` is classified as UNSUPPORTED/MANUAL_REQUIRED by the expression compiler
- The syside metamodel exposes `Redefinition`, `Specialization`, `Multiplicity` types, but we have no empirical data on their structure or traversability
- The agentic-mbse package (`binding.py`, `expression.py`, `helpers.py`, `syside_adapter.py`) has no hierarchy/redefinition capabilities

### Desired Outcome

A structured report documenting the exact AST attribute names, node types, and traversal code for every pattern in the Costed Component hierarchy. Each finding includes concrete code showing how to access the information, so Items 2-4 can proceed without further AST exploration.

---

## Scope

### In Scope

- Probe the solar_battery model (`tests/fixtures/solar_battery_model/`) via SysIDE
- Document AST structures for all patterns listed in "Questions to Answer"
- Assess whether `agentic-mbse`'s existing modules can be reused or must be extended (for the design phase to act on)
- Document any SysIDE gaps or limitations
- Produce a reusable probe script

### Out of Scope

- Implementation of template detection, redefinition resolution, or multiplicity handling
- Any changes to production code (`src/sysml_codegen/` or `agentic-mbse`)
- Fallback prototyping -- if a gap is found, document it and stop; do not build workarounds
- Testing against CATF model (solar_battery is sufficient for the probe)
- Performance analysis

### Edge Cases & Considerations

- The solar_battery model uses quoted names (`'PV Module'`, `'Costed Component'`) -- verify these work with standard AST attribute access
- Some PartDefs are abstract (`abstract part def 'Costed Component'`) -- verify abstraction doesn't change AST traversal
- The `allocation_model` CalcUsage is inside an assembly PartDef (not a leaf) and has literal bindings (`in child_count = 25.0`) -- verify this doesn't differ from leaf-part embedded CalcUsages
- `default :=` appears on both CalcDef parameters and part attributes -- verify AST representation is identical in both contexts

---

## Requirements

### Questions to Answer

> All questions are derived from the COST-PATTERN epic (Item 1) and the investigation findings below.

#### Q1: Template CalcUsage Ownership

**FR-1**: Determine how SysIDE distinguishes a CalcUsage owned by a PartDefinition (template) from one owned by a PartUsage (concrete). Document the AST path from `cost_model` CalcUsage to its owning `'PV Module'` PartDef. Show the owner chain traversal and which node types appear at each level.

Test targets:
- `PV Module.cost_model` (leaf PartDef, template)
- `Solar Array.allocation_model` (assembly PartDef, template)
- `solar_battery_plant.energy_production` (design PartUsage, concrete)

#### Q2: `:>>` Redefinition AST Representation

**FR-2**: Document how `:>>` redefinitions appear in the AST. There are at least 4 distinct `:>>` patterns in the model:

| Pattern | Example | Expected AST Structure |
|---------|---------|----------------------|
| Enum literal | `:>> cas_category = CASCategory::CAS220101` | Redefinition + enum reference |
| EXPOSE (calc output) | `:>> capital_cost = cost_model.total_cost` | Redefinition + FeatureChainExpression |
| Aggregation formula | `:>> capital_cost = sum(pv_module.capital_cost) + ...` | Redefinition + OperatorExpression + InvocationExpression |
| FORMULA (sibling refs) | `:>> idiot_index = capital_cost / raw_material_cost` | Redefinition + OperatorExpression |

For each: document the node type wrapping the `:>>`, the `.redefined_feature` link back to `'Costed Component'`, and the expression node on the RHS.

#### Q3: `part redefines` vs Plain `part`

**FR-3**: Determine how `part redefines solar_array : 'Solar Array' { ... }` (design.sysml:25) differs from `part solar_array : 'Solar Array'` (library.sysml:738) in the AST. Is there an explicit `ownedRedefinition` link? Does the `redefines` keyword produce a different node type?

#### Q4: Deep-Path `:>>` Resolution

**FR-4**: Document how `:>> pv_module.wattage = 400.0` (design.sysml:26) appears in the AST. Specifically:
- Is `pv_module.wattage` a `FeatureChainExpression`, a dotted qualified name, or something else?
- Can we resolve `pv_module` to the PartUsage on `Solar Array`, then `.wattage` to the attribute on `PV Module`?
- Show the full traversal chain from design to leaf attribute

#### Q5: Multiplicity Representation

**FR-5**: Document how `part pv_module : 'PV Module' [module_count]` (library.sysml:602) encodes multiplicity. Specifically:
- Is multiplicity on the PartUsage element? What attribute name?
- Is `module_count` a reference to the sibling attribute (`attribute module_count : Integer default := 20`)?
- Can we resolve the multiplicity to a literal value via the default?
- How does syside's `Multiplicity` / `MultiplicityRange` relate to what's on the PartUsage?

#### Q6: `sum()` InvocationExpression Structure

**FR-6**: Document how `sum(pv_module.capital_cost)` (library.sysml:616) appears in the expression AST. Specifically:
- Is it an `InvocationExpression`? What is the function reference?
- What are the operands? Is `pv_module.capital_cost` a `FeatureChainExpression` inside the invocation?
- Can we distinguish `sum(array_part.attr)` from hypothetical `sqrt(x)` structurally?
- How does `NumericalFunctions::sum` resolve in the AST?

#### Q7: Specialization Chain Traversal

**FR-7**: Demonstrate end-to-end traversal from `solar_battery_plant` (design) through the full hierarchy:
```
solar_battery_plant → 'Solar Battery Plant' → solar_array → 'Solar Array' → pv_module → 'PV Module' → cost_model → PVModuleCostCalc
```
At each link, document: the attribute used (`.type`, `.ownedSpecialization`, `.general`, etc.), the node types, and whether it's traversable programmatically.

#### Q8: New Attribute vs Redefined Attribute Distinction

**FR-8** [FROM INVESTIGATION]: Document the AST difference between:
- `attribute misc_hardware_cost : Real = allocation_model.total_allocation;` (library.sysml:612) -- a **new** attribute with a formula RHS
- `:>> capital_cost = sum(pv_module.capital_cost) + ...;` (library.sysml:615) -- a **redefined** inherited attribute

Both are inside the same PartDef (`Solar Array`). The spike MUST determine whether these produce different AST node types or relationships.

#### Q9: `default :=` Representation

**FR-9** [FROM INVESTIGATION]: Document how `default :=` is represented in the AST in both contexts:
- CalcDef parameter: `in attribute cost_per_watt : Real default := 1.07` (library.sysml:39)
- Part attribute: `attribute module_count : Integer default := 20` (library.sysml:598)

Are they identical in AST representation? Can we uniformly extract the default value?

#### Q10: Binding to Inherited/Redefined Attribute

**FR-10** [FROM INVESTIGATION]: Document how `in total_capex = capital_cost` (design.sysml:85) resolves in the AST. Here, `capital_cost` refers to the top-level plant's `:>> capital_cost`, which is itself an aggregation result. Does the AST resolve this reference to the redefined attribute, or does it point to the abstract `Costed Component.capital_cost`?

### Non-Functional Requirements

- **NFR-1**: Probe script MUST load the solar_battery model via the same `SysideAdapter` path that codegen uses (not a separate SysIDE instance)
- **NFR-2**: Report MUST include concrete Python code snippets (not pseudocode) showing attribute access for each finding
- **NFR-3**: Report MUST note which syside metamodel types are available vs which are actually populated on the solar_battery model elements

### agentic-mbse Reuse Assessment

**FR-11**: The report SHOULD include a section assessing what `agentic-mbse` already provides and what needs to be added for Phase 3. Specifically review:
- `syside_adapter.py` -- type map has `PartDefinition`, `PartUsage`, `FeatureTyping`; does NOT have `Redefinition`, `Specialization`, `Multiplicity`
- `binding.py` -- `classify_binding()` and `extract_bindings()` handle CHAIN, REFERENCE, LITERAL, EXPRESSION but no redefinition awareness
- `expression.py` -- `extract_feature_refs()`, `traverse_expression()` work but don't handle `InvocationExpression`
- `helpers.py` -- `get_parent_part_name()` gets immediate parent only; no full chain traversal
- `types.py` -- `BindingInfo`, `ExpressionRef` exist; no hierarchy/redefinition data models

The design phase (Item 2) SHOULD reuse existing agentic-mbse capabilities where possible and propose extensions where needed.

---

## Acceptance Criteria

### Core Functionality

- [ ] Q1-Q10 each answered with concrete AST examples from the solar_battery model
- [ ] Each answer includes Python code showing exact attribute access (e.g., `elem.ownedRedefinition[0].redefinedFeature.name`)
- [ ] agentic-mbse reuse assessment completed (FR-11)
- [ ] Go/no-go decision documented with rationale

### Probe Script

- [ ] `scripts/spike_hierarchy_ast.py` exists and runs successfully
- [ ] Script loads solar_battery model via SysideAdapter
- [ ] Script produces structured output for all 10 questions
- [ ] Script handles graceful failures (missing attributes logged, not crashed)

### Report Quality

- [ ] Report documents exact attribute names for each traversal pattern
- [ ] Any SysIDE gaps documented with clear description of what's missing
- [ ] No fallback prototypes or workarounds included -- gaps are documented only
- [ ] Findings are organized by question number for easy reference during Items 2-4

### Regression Safety

- [ ] No production code modified
- [ ] All existing tests continue to pass (this is research only)

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_costed_component_pattern.md` (COST-PATTERN, Item 1)
- **Research (strategy):** `.project/research/20260202-180000_expression-compilation-and-inline-math-strategy.md`
- **Research (gap analysis):** `.project/research/20260109-205122_cost-modeling-codegen-changes.md`
- **Model fixture:** `tests/fixtures/solar_battery_model/` (library.sysml, costing.sysml, design.sysml)
- **agentic-mbse package:** `~/agentic-mbse/src/agentic_mbse/sysml/` (syside_adapter.py, binding.py, expression.py, helpers.py, types.py)
- **syside metamodel docs:** `~/agentic-mbse/docs/syside/api/metamodel/KerML/` (Redefinition.md, Specialization.md, Multiplicity.md)
- **Design:** `.project/active/hierarchy-spike/design.md` (to be created -- N/A for research spike)
- **Phase 1 epic:** `.project/backlog/epic_expression_aware_codegen.md` (EXPR-CODEGEN, complete)
- **Phase 2 epic:** `.project/backlog/epic_attribute_expression_capture.md` (ATTR-EXPR, complete)

---

**Next Steps:** This is a research spike. After report completion, proceed directly to Item 2 spec (`/_my_spec item 2`). The spike report feeds into the design phase of Items 2-4.
