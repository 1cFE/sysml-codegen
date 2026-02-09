---
date: 2026-02-09T16:56:38-06:00
researcher: Claude
topic: "ATTR-EXPR Item 5: Documentation, ADRs, and Upstream Integration Points"
tags: [research, attr-expr, documentation, adr, agentic-mbse, integration]
status: complete
last_updated: 2026-02-09
---

# Research: ATTR-EXPR Item 5 -- Documentation, ADRs, and Upstream Integration Points

**Date**: 2026-02-09T16:56:38-06:00
**Researcher**: Claude
**Research Type**: Architecture / Integration / Documentation

## Research Question

For ATTR-EXPR Item 5 (Documentation -- ADRs and Epic Closure):

1. Where do the architectural decision records (ADRs) live? Were they carried forward from the `~/fusion-modeling` monorepo during migration?
2. What places in the `agentic-mbse` pipeline need adjustment for the computed attribute expression feature?
3. What is the complete scope of documentation and code changes needed for Item 5?

## Summary

- **ADRs live in the original monorepo** at `~/fusion_modeling/docs/architecture/` (ADR-001, ADR-002, ADR-003). They were **NOT carried forward** to `sysml-codegen` or `agentic-mbse` as standalone files. Only ADR-002 was partially migrated as a pattern reference in `agentic-mbse/docs/patterns/adr002-calculations.md`.
- **The `agentic-mbse` validation layer has a critical conflict**: `adr002.py:check_static_expressions()` treats FORMULA computed attributes (`attribute area = length * width`) as V2 violations. This is the single highest-priority upstream change.
- **13 pattern docs** exist in the installed `agentic_mbse_data` package. Two need updates: `adr002-calculations.md` and `expose-pattern.md`.
- **8 modeling agent commands** exist in `~/agentic-mbse/claude/commands/`. Three need updates for computed attribute guidance.
- **2 project templates** need updates: `MODELING_GUIDE.md.template` and `MODELING_PROCESS.md.template`.
- **`fusion-tea` requires zero changes** -- it's a pure consumer of codegen output.

## Detailed Findings

### 1. ADR Location and Migration Status

#### Original ADRs (Canonical Source)

All three ADRs exist in the original monorepo:

| ADR | Path | Status | Date |
|-----|------|--------|------|
| ADR-001 | `~/fusion_modeling/docs/architecture/ADR-001-input-parameter-definition.md` | Accepted | 2025-12-08 |
| ADR-002 | `~/fusion_modeling/docs/architecture/ADR-002-calculation-architecture.md` | Implemented | 2025-12-28 |
| ADR-003 | `~/fusion_modeling/docs/architecture/ADR-003-signal-identifiers.md` | Accepted | 2025-12-23 |

#### Migration Status: NOT Carried Forward

The migration from `~/fusion-modeling` monorepo to the three separate repos (`agentic-mbse`, `sysml-codegen`, `fusion-tea`) **did not carry the ADR files forward**:

- **`sysml-codegen`**: No `docs/` directory at all. No ADR files. ADRs are referenced in CLAUDE.md, concept docs, and code comments (28+ references to ADR-002 alone), but the actual documents don't exist in this repo.
- **`agentic-mbse`**: One partial derivative exists: `docs/patterns/adr002-calculations.md` is a pattern guide implementing ADR-002, not the ADR itself. It's also published as package data in `agentic_mbse_data/docs/patterns/`.
- **`fusion-tea`**: Has its own architectural decisions (`AD-001` through `AD-005` in `modeling_project/ARCHITECTURE.md`) but these are fusion-specific modeling decisions, not cross-cutting pipeline ADRs.

#### Implications for Item 5

The epic's deliverables reference `docs/architecture/ADR-004-...` and `docs/architecture/ADR-005-...` as paths within `sysml-codegen`. Since no `docs/architecture/` directory exists, **Item 5 must either**:
1. Create `docs/architecture/` in `sysml-codegen` and place ADR-004/005 there (along with copies of ADR-001/002/003 for completeness), OR
2. Place ADRs in `.project/concepts/` (where the pre-ADR concept doc already lives), OR
3. Place ADRs back in the monorepo and reference from both repos

**Recommendation**: Create `docs/architecture/` in `sysml-codegen`. This is where CLAUDE.md and code comments expect them to be. Copy ADR-001/002/003 from the monorepo as the canonical migration, then add ADR-004/005 and the ADR-002 amendment.

---

### 2. `agentic-mbse` Pipeline: Complete Integration Point Inventory

#### 2.1 CRITICAL: Validation Layer (`~/agentic-mbse/src/agentic_mbse/validation/`)

**`adr002.py` -- V2 Dynamic Expression Check (lines 418-510)**

This is the **highest-priority upstream change**. The `check_static_expressions()` function currently flags ALL design attributes with feature references (except EXPOSE) as V2_DYNAMIC_EXPRESSION violations:

```python
# Current logic (adr002.py:480-505):
refs = extract_feature_refs(expr)
if len(refs) == 0:
    continue  # TRUE STATIC → OK
if _is_expose_pattern(attr, expr, calc_outputs):
    continue  # EXPOSE → OK
# Everything else → V2 VIOLATION  ← THIS IS THE PROBLEM
```

After ATTR-EXPR, `attribute area = length * width` is a **valid FORMULA pattern**, not a violation. The V2 check needs a third exemption path that recognizes FORMULA computed attributes.

**Specific change needed**: Add a FORMULA classification check between the EXPOSE check and the violation:

```python
# Proposed logic:
if _is_expose_pattern(attr, expr, calc_outputs):
    continue  # EXPOSE → OK
if _is_formula_pattern(attr, expr):    # ← NEW
    continue  # FORMULA → OK (per ADR-002 Amendment)
# Remaining → V2 VIOLATION
```

The `_is_formula_pattern()` check would verify: all feature refs in the expression resolve to sibling attributes on the same part (no calc output refs, no cross-part refs). This mirrors the classification logic in `sysml-codegen/extraction/computed_attribute_extractor.py`.

**File**: `~/agentic-mbse/src/agentic_mbse/validation/adr002.py:418-510`
**Impact**: Without this change, the validation pyramid will flag valid FORMULA patterns as errors, contradicting the ADR-002 amendment.

**`adr002.py` -- V4 Unsupported Operator Check (lines 80-148)**

Currently checks operators in design attribute expressions. After ATTR-EXPR, this check should also apply to computed attribute expressions, but it already does -- it checks ALL design file attributes with expressions. No change needed, but verify that FORMULA patterns use only supported operators (they do -- `+`, `-`, `*`, `/` are all supported; `^` was added to `SUPPORTED_OPERATORS` on line 25).

**`level8_codegen.py` -- Codegen Readiness (lines 1-565)**

Currently validates qualified names, calc def structure, binding formats, and design attr completeness. Consider adding:
- Check that computed attributes with FORMULA classification have compilable expressions
- Check that computed attribute module names would be valid (no collisions with CalcUsage module names)

**Priority**: Low. These checks would be nice-to-have but aren't blocking. The codegen pipeline itself validates these during execution.

**`level2_structure.py`**: May need to understand computed attributes for completeness checks. Priority: Low.

**`types.py` -- ValidationCode enum (line 66-94)**

Consider adding a new validation code for computed attribute issues:
```python
V2_COMPUTED_ATTR_UNRESOLVABLE = "V2_COMPUTED_ATTR_UNRESOLVABLE"
```
**Priority**: Low. Only needed if adr002.py begins classifying computed attributes beyond FORMULA/EXPOSE.

#### 2.2 Pattern Documentation (`~/agentic-mbse/docs/patterns/` → installed as `agentic_mbse_data`)

13 pattern docs are distributed with the `agentic_mbse_data` package. Two need updates:

**`adr002-calculations.md`** -- The installed pattern guide currently says:

> | **Derived expression** | `designs/` attribute | ≥1 (design attr) | **FAIL** | `= radius * 2.0` |

This must be updated to reflect the ADR-002 amendment:

> | **FORMULA expression** | `designs/` attribute | ≥1 (sibling attrs only) | **PASS** | `= length * width` |
> | **Derived expression** | `designs/` attribute | ≥1 (calc output refs) | **FAIL** | `= calc.output * 0.95` |

The "Invalid Pattern: Derived Expression" section (lines 65-101) shows `attribute area = length * width` as a **violation** that must be refactored to a calc def. After ATTR-EXPR, this is a valid pattern. The document needs an amendment section.

The Decision Flow (lines 202-217) needs a new branch for FORMULA:

```
+-- YES: Is it just referencing sibling attributes (FORMULA)?
    |
    +-- YES: Computed attribute -> OK (generates pipeline module)
    |
    +-- NO: Derived expression -> EXTRACT TO CALC DEF
```

**File**: Source at `~/agentic-mbse/docs/patterns/adr002-calculations.md`; installed at `.venv/lib/python3.12/site-packages/agentic_mbse_data/docs/patterns/adr002-calculations.md`

**`expose-pattern.md`** -- This doc is accurate but incomplete after ATTR-EXPR. It should add a section distinguishing:
- **EXPOSE_PURE** (existing pattern, no change): `attribute x = calc.output`
- **FORMULA** (new pattern): `attribute x = a * b` (not an EXPOSE; it's a computed attribute)
- **EXPOSE_COMPUTED** (deferred): `attribute x = calc.output * 2.0`

This prevents modelers from conflating FORMULA with EXPOSE.

**File**: Source at `~/agentic-mbse/docs/patterns/expose-pattern.md`; installed at `.venv/lib/python3.12/site-packages/agentic_mbse_data/docs/patterns/expose-pattern.md`

#### 2.3 Modeling Agent Commands (`~/agentic-mbse/claude/commands/`)

8 agent commands guide the modeling workflow. Three need updates:

**`implement-model.md`** (highest priority)
- Currently instructs modelers to follow ADR-002 for expression handling
- Needs examples of when to use `attribute x = a * b` (FORMULA) vs CalcDef
- Should document that FORMULA patterns generate pipeline modules automatically
- **Lines to update**: Stage 1 references MODELING_GUIDE, which will be updated separately

**`design-model.md`** (medium priority)
- Instructs the design agent to analyze component interfaces
- Should add guidance for recognizing when FORMULA patterns (attribute expressions with sibling refs) are more appropriate than CalcDefs
- Decision criteria: one-off simple formula → attribute expression; reusable/complex → CalcDef

**`audit-models.md`** (low priority)
- Could add a check for computed attributes with unresolvable references
- Not blocking; audit focuses on parameter accuracy, not expression analysis

**`onboard.md`** (low priority)
- Could mention that computed attributes reduce CalcDef overhead for simple formulas

#### 2.4 Project Templates (`~/agentic-mbse/project_templates/`)

**`MODELING_GUIDE.md.template`** (lines 72-78)
- Decision tree currently says: "A CALCULATION formula? → Calc def in library/ (per ADR-002)"
- Needs amendment: "A SIMPLE FORMULA on sibling attributes? → Attribute expression (per ADR-002 amendment) OR Calc def in library/"
- Should add a "Computed Attributes" section with examples of FORMULA, EXPOSE_PURE, and the EXPOSE_COMPUTED limitation

**`MODELING_PROCESS.md.template`**
- The 3-phase design workflow could mention computed attributes as a modeling option
- Low priority; the workflow itself doesn't change

#### 2.5 Shared Data Models (`~/agentic-mbse/src/agentic_mbse/sysml/`)

**No changes needed.** The shared types (`BindingType`, `ExpressionRef`, `BindingInfo`, etc.) in `types.py` and the expression utilities in `expression.py` (`extract_feature_refs()`, `extract_operators()`, etc.) are CalcDef-agnostic and already support everything needed for computed attribute analysis.

#### 2.6 SysIDE Adapter (`~/agentic-mbse/src/agentic_mbse/sysml/syside_adapter.py`)

**No changes needed.** The adapter is a generic wrapper that handles all SysML element types including `AttributeUsage` and `feature_value_expression`.

#### 2.7 CLI (`~/agentic-mbse/src/agentic_mbse/cli/`)

**No changes needed.** The CLI runs validation which will be updated separately.

---

### 3. `fusion-tea` Pipeline

**No changes needed.** Fusion-tea is a pure consumer of sysml-codegen output. Computed attribute synthetic modules are standard `PipelineModule` instances that generate standard TEAx module wrappers, auto-implementations, and pipeline YAML entries. The TEAx runtime (`execute_pipeline()`, `PipelineValidator`, `create_registry()`) handles any registered module type generically.

The solar_battery model at `~/1cfe/fusion-tea/models/tests/solar_battery/design.sysml:60` has the flagship computed attribute (`p_net_kw = p_net_mw * 1000.0`) that Item 4 validated E2E. The generated output will include the synthetic module automatically.

---

### 4. ADR Content Analysis

#### ADR-002: What Needs Amending

The canonical ADR-002 (`~/fusion_modeling/docs/architecture/ADR-002-calculation-architecture.md`) has these sections that conflict with ATTR-EXPR:

**Rule 3 (lines 114-139)**: "Design attributes contain values, not computations"
- Currently: "Design attributes SHALL NOT contain: Derived expressions (referencing other design attributes)"
- Amendment: FORMULA patterns (arithmetic on sibling attributes of the same part) are now permitted. They generate synthetic pipeline modules automatically.

**Expression Taxonomy (lines 152-159)**:
- Currently: "Derived expression" (≥1 design attr ref) → FAIL
- Amendment: Split into FORMULA (sibling refs only → PASS) vs derived (calc output refs → FAIL)

**Decision Flow (lines 202-217)**:
- Currently: "Does it reference design attributes? YES → Derived expression → EXTRACT TO CALC DEF"
- Amendment: Add FORMULA branch before the "EXTRACT" conclusion

**Static Evaluator Section (lines 206-248)**:
- Currently: describes static evaluation (all operands resolve to literals) as the only way to handle design expressions
- Amendment: FORMULA expressions are NOT statically evaluated; they generate pipeline modules that execute at runtime

**Validation Rule V2 (lines 362-369)**:
- Currently: "V2: Static eval failure → 'Expression cannot be statically evaluated'"
- Amendment: V2 only fires for non-FORMULA, non-EXPOSE patterns. FORMULA is a valid new category.

#### ADR-004: Computed Attribute Pipeline Integration (New)

Content sourced from `.project/concepts/attr-expr-architectural-decisions.md`:
- Decision 1: Option C (direct graph integration, not synthetic CalcDef/CalcUsage)
- Decision 4: Step 4.5 pipeline placement
- Decision 5: Module naming `{part_name}__{attr_name}` per ADR-003
- Decision 7: Backtracker consumes computed attributes for binding resolution

#### ADR-005: Computed Attribute Classification (New)

Content sourced from `.project/concepts/attr-expr-architectural-decisions.md`:
- Decision 2: 5-way classification (FORMULA, EXPOSE_PURE, EXPOSE_COMPUTED, LITERAL, UNRESOLVABLE)
- Decision 3: EXPOSE handling (PURE = alias, COMPUTED = deferred)
- Decision 6: Qualified name resolution mandatory in classification

---

### 5. sysml-codegen Internal Documentation

The epic's deliverables also include:
- Updating `CLAUDE.md` to reference new ADRs and describe computed attribute pipeline step
- Archiving `.project/active/attr-expr-*` to `.project/completed/`
- Filling in Lessons Learned section in the epic doc

## Code References

### `agentic-mbse` (upstream changes needed)

- `~/agentic-mbse/src/agentic_mbse/validation/adr002.py:418-510` -- V2 check needs FORMULA exemption
- `~/agentic-mbse/src/agentic_mbse/validation/adr002.py:25` -- SUPPORTED_OPERATORS (already includes `^`)
- `~/agentic-mbse/src/agentic_mbse/validation/adr002.py:297-391` -- `_is_expose_pattern()` (model for `_is_formula_pattern()`)
- `~/agentic-mbse/src/agentic_mbse/validation/level8_codegen.py:442-565` -- codegen readiness (optional enhancement)
- `~/agentic-mbse/src/agentic_mbse/sysml/types.py:66-94` -- ValidationCode enum (optional new code)
- `~/agentic-mbse/docs/patterns/adr002-calculations.md:42-44` -- expression taxonomy needs FORMULA row
- `~/agentic-mbse/docs/patterns/adr002-calculations.md:65-101` -- "Invalid Pattern" section needs amendment
- `~/agentic-mbse/docs/patterns/adr002-calculations.md:202-217` -- decision flow needs FORMULA branch
- `~/agentic-mbse/docs/patterns/expose-pattern.md:1-288` -- needs FORMULA vs EXPOSE distinction
- `~/agentic-mbse/claude/commands/implement-model.md:1-50` -- needs FORMULA guidance
- `~/agentic-mbse/claude/commands/design-model.md:1-50` -- needs FORMULA recognition
- `~/agentic-mbse/project_templates/MODELING_GUIDE.md.template:72-78` -- decision tree needs FORMULA branch

### ADRs (canonical source)

- `~/fusion_modeling/docs/architecture/ADR-001-input-parameter-definition.md` -- reference only, no changes
- `~/fusion_modeling/docs/architecture/ADR-002-calculation-architecture.md` -- AMENDMENT needed (Rule 3, taxonomy, V2)
- `~/fusion_modeling/docs/architecture/ADR-003-signal-identifiers.md` -- reference only, no changes

### `sysml-codegen` (internal, already implemented)

- `src/sysml_codegen/extraction/computed_attribute_extractor.py` -- extraction module (Item 2)
- `src/sysml_codegen/extraction/data_models.py` -- ComputedAttributeData model (Item 2)
- `src/sysml_codegen/analysis/dependency_backtracker.py` -- computed attr awareness (Item 3)
- `src/sysml_codegen/resolution/graph_builder.py` -- FORMULA module generation (Item 3)
- `src/sysml_codegen/generation/initialization.py` -- Step 4.5 integration (Item 3)
- `.project/concepts/attr-expr-architectural-decisions.md` -- pre-ADR concept doc (source for ADR-004/005)

## Architecture Insights

### ADR Evolution Path

```
~/fusion_modeling/docs/architecture/  (original, canonical)
    ├── ADR-001  →  referenced in sysml-codegen code and CLAUDE.md
    ├── ADR-002  →  partially migrated as agentic-mbse pattern doc
    │                amended by ATTR-EXPR (Rule 3, V2 check)
    └── ADR-003  →  referenced in sysml-codegen code and CLAUDE.md

~/1cfe/sysml-codegen/docs/architecture/  (TO BE CREATED by Item 5)
    ├── ADR-001  (copied from monorepo, establishes canonical local source)
    ├── ADR-002  (copied + amended for FORMULA pattern)
    ├── ADR-003  (copied from monorepo)
    ├── ADR-004  (NEW: computed attribute pipeline integration)
    └── ADR-005  (NEW: computed attribute classification)
```

### Validation Pyramid Impact

```
Level 1 (Syntax):     No change
Level 2 (Structure):  adr002.py V2 check needs FORMULA exemption  ← CRITICAL
Level 3 (Dataflow):   No change
Level 4 (Constraints): No change
Level 5 (Semantic):   No change
Level 6 (Trace):      No change
Level 7 (Arch):       No change
Level 8 (Codegen):    Optional: computed attr structure validation
```

### Pattern Doc Impact

```
adr002-calculations.md:  AMENDMENT (expression taxonomy, decision flow, invalid→valid)
expose-pattern.md:       ADDITION (FORMULA vs EXPOSE distinction)
common-mistakes.md:      Optional: "Using CalcDef when attribute expression suffices"
Other 10 docs:           No change
```

## Feasibility Assessment

Item 5 as scoped in the epic is **fully feasible** within the estimated 0.5-1 day. The scope breaks down as:

| Task | Effort | Blocking? |
|------|--------|-----------|
| Create `docs/architecture/` directory structure | 15 min | No |
| Draft ADR-004 (from concept doc content) | 1-2 hr | No |
| Draft ADR-005 (from concept doc content) | 1-2 hr | No |
| Draft ADR-002 amendment | 30 min | No |
| Copy ADR-001/002/003 from monorepo | 15 min | No |
| Update CLAUDE.md | 15 min | No |
| Fill epic Lessons Learned | 15 min | No |
| Archive active items | 15 min | No |

**However**, the upstream `agentic-mbse` changes are **not scoped in Item 5** but are **critical for feature completeness**:

| Upstream Task | Effort | Blocking? |
|--------------|--------|-----------|
| Fix `adr002.py` V2 check (FORMULA exemption) | 2-4 hr | **YES** -- validation rejects valid patterns |
| Update `adr002-calculations.md` pattern doc | 1 hr | Yes -- modeler guidance is wrong |
| Update `expose-pattern.md` | 30 min | No -- informational |
| Update agent commands (3 files) | 1-2 hr | No -- convenience |
| Update MODELING_GUIDE template | 30 min | No -- new projects only |

## Recommendations

### 1. Split Item 5 Into Two Sub-Items

**Item 5a: sysml-codegen ADRs and Epic Closure** (0.5-1 day)
- Create `docs/architecture/` with ADR-001 through ADR-005
- ADR-002 amendment
- Update CLAUDE.md
- Epic closure (Lessons Learned, archive)

**Item 5b: agentic-mbse Upstream Integration** (0.5-1 day, separate PR)
- Fix `adr002.py` V2 check with FORMULA exemption
- Update pattern docs (`adr002-calculations.md`, `expose-pattern.md`)
- Update agent commands and MODELING_GUIDE template
- Bump `agentic-mbse` version and re-install

### 2. ADR-002 Amendment Strategy

Rather than modifying the existing ADR-002 text extensively, use an **Amendment section** at the bottom:

```markdown
## Amendment: FORMULA Computed Attributes (2026-02-09)

### Context
ATTR-EXPR epic (Phase 2) adds support for attribute-level expressions
that reference sibling attributes on the same part.

### Rule 3 Amendment
Design attributes MAY contain arithmetic expressions that reference
only sibling attributes on the same part (FORMULA pattern).

### Conditions
- All feature references must resolve to sibling attributes (same owner)
- No FeatureChainExpression nodes (no calc output refs)
- Supported operators: +, -, *, /

### Pipeline Treatment
FORMULA expressions generate synthetic pipeline modules with
auto-implemented code. See ADR-004 for pipeline integration details.
```

### 3. FORMULA Validation Logic

For the `adr002.py` fix, the `_is_formula_pattern()` function should mirror the classification logic already proven in `sysml-codegen/extraction/computed_attribute_extractor.py`:

```python
def _is_formula_pattern(attr, expr, calc_def_qualified_names):
    """Check if expression is a FORMULA computed attribute (sibling refs only)."""
    refs = extract_feature_refs(expr)
    if len(refs) == 0:
        return False  # No refs = literal, not FORMULA

    for ref in refs:
        # If any ref points to a calc output → not FORMULA
        if _is_calc_output_reference(ref, calc_def_qualified_names):
            return False
        # If any ref is from a different document → not sibling
        if ref.document_path and ref.document_path != attr_document_path:
            return False

    return True  # All refs are sibling design attributes
```

### 4. Don't Update fusion-tea

Confirm: zero changes needed for `fusion-tea`. The computed attribute feature is fully contained within the codegen pipeline.

## Open Questions

1. **Where should the canonical ADRs live going forward?** The monorepo still exists but the repos have diverged. Should ADR-001/002/003 live in `sysml-codegen` (primary consumer), `agentic-mbse` (shared library), or both? **Recommendation**: `sysml-codegen/docs/architecture/` as the primary location, since ADRs describe codegen pipeline architecture.

2. **Should the `agentic-mbse` V2 fix be a blocking prerequisite for the sysml-codegen PR?** If the validation pipeline runs against models with FORMULA patterns, it will produce false errors. **Recommendation**: Yes, fix `adr002.py` first or simultaneously.

3. **Should Item 5 update the `agentic_mbse_data` installed package?** Pattern docs in the installed package are stale after changes to source docs. This requires a version bump and re-install of `agentic-mbse`. **Recommendation**: Yes, as part of Item 5b.

4. **Should ADR-001 be amended for computed attribute entry points?** FORMULA module inputs that are literal sibling attributes become DESIGN_ATTRIBUTE entry points -- this is already correct per ADR-001 Type 2. No amendment needed. However, ADR-001's "What is NOT an Input Parameter" table (line 85) says `Expression (not literal) | attr total = a + b | Computed from other params` -- this should be updated to note that the expression's inputs (a, b) may still be entry points even though the expression result is not.
