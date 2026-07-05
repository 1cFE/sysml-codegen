# Implementation Plan: ATTR-EXPR Item 5a -- ADRs and Epic Closure

**Status:** In Progress
**Created:** 2026-02-09
**Last Updated:** 2026-02-09

## Source Documents

- **Spec:** `.project/active/attr-expr-docs/spec.md`
- **Epic:** `.project/backlog/epic_attribute_expression_capture.md`
- **Concept Doc:** `.project/concepts/attr-expr-architectural-decisions.md` (source material for ADR-004/005)
- **Research:** `.project/research/20260209-165638_attr-expr-documentation-adrs-and-upstream-integration.md`
- **Monorepo ADRs:** `~/fusion_modeling/docs/architecture/ADR-001-...`, `ADR-002-...`, `ADR-003-...`

## Implementation Strategy

**Phasing Rationale:**
Phases follow a strict dependency chain. Phase 1 creates the directory and migrates existing ADRs -- everything depends on this. Phase 2 writes the new ADRs (ADR-005 before ADR-004 since ADR-004 forward-references ADR-005). Phase 3 amends the migrated ADRs, which can only happen after ADR-004/005 exist to be cited. Phase 4 closes the epic, which requires all documentation to be finalized.

**Validation Approach:**
- Each phase verifies file existence and cross-reference consistency
- No automated tests apply (pure documentation, no code changes)
- Final validation: `uv run pytest tests/` confirms no regressions from directory operations

---

## Phase 1: Foundation -- Directory Structure and Monorepo ADR Migration

### Goal

Create `docs/architecture/` in `sysml-codegen` and copy ADR-001, ADR-002, ADR-003 from `~/fusion_modeling/docs/architecture/`. This establishes the canonical local ADR location that code comments and CLAUDE.md already reference.

### Changes Required

#### 1. Create directory
- [x] `mkdir -p docs/architecture/`

#### 2. Copy monorepo ADRs
- [x] Copy `~/fusion_modeling/docs/architecture/ADR-001-input-parameter-definition.md` -> `docs/architecture/ADR-001-input-parameter-definition.md`
- [x] Copy `~/fusion_modeling/docs/architecture/ADR-002-calculation-architecture.md` -> `docs/architecture/ADR-002-calculation-architecture.md`
- [x] Copy `~/fusion_modeling/docs/architecture/ADR-003-signal-identifiers.md` -> `docs/architecture/ADR-003-signal-identifiers.md`

Note: References sections in these ADRs point to monorepo-era paths (`project/research/...`, `docs/codegen/...`). These are historical references and should NOT be updated -- they document the context at time of original authorship.

### Validation

- [x] Verify: `docs/architecture/` contains 3 files
- [x] Verify: Each file matches its monorepo source (byte-identical copy)

**What We Know Works After This Phase:**
The ADR directory exists and contains the 3 canonical pre-existing ADRs, ready for amendment and addition.

---

## Phase 2: New ADRs -- ADR-005 (Classification) then ADR-004 (Pipeline Integration)

### Goal

Draft the two new ADRs that formalize ATTR-EXPR architectural decisions. ADR-005 is written first because ADR-004 references it for classification details.

### Changes Required

#### 1. ADR-005: Computed Attribute Classification
**File:** `docs/architecture/ADR-005-computed-attribute-classification.md` (NEW)

Content sourced from concept doc Sections 3-4, 6-7:
- [x] Status: Accepted, date 2026-02-09
- [x] Context: Phase 2 ATTR-EXPR needs to classify attribute expressions for pipeline treatment. Link to Phase 1 (EXPR-CODEGEN) results.
- [x] Decision section with 3 sub-decisions:
  - [x] **Classification Scheme** (concept doc Decision 2): 5-way enum with definitions table
    - FORMULA: definition, SysML examples (probe: `area = length * width`; solar_battery: `p_net_kw = p_net_mw * 1000.0`), pipeline treatment (synthetic module)
    - EXPOSE_PURE: definition, SysML examples (CATF: `p_alpha_out = alpha_neutron_split.p_alpha`), pipeline treatment (channel alias, no module)
    - EXPOSE_COMPUTED: definition, example (`scaled_area = scale_calc.result * 2.0`), status DEFERRED, UX gap documentation
    - LITERAL: definition, examples, pipeline treatment (existing handling)
    - UNRESOLVABLE: definition, example, pipeline treatment (warning, skip)
  - [x] **EXPOSE Handling** (concept doc Decision 3): PURE = alias with wiring context; COMPUTED = deferred with workaround guidance
  - [x] **Qualified Name Resolution** (concept doc Decision 6): mandatory; include the 19-CATF-misclassification example showing why simple-name matching fails
- [x] Classification summary table: classification | generates module? | exists in models? | modeling practice change?
- [x] Why MIXED was dropped: zero occurrences across 540 attributes; EXPOSE_PURE/EXPOSE_COMPUTED more precise
- [x] EXPOSE-within-FORMULA interaction: resolution map strategy for FORMULA inputs that reference EXPOSE aliases
- [x] Consequences (positive/negative)
- [x] Examples section with concrete SysML and compiled output
- [x] References: concept doc, spike reports, ADR-004
- [x] Changelog entry

#### 2. ADR-004: Computed Attribute Pipeline Integration
**File:** `docs/architecture/ADR-004-computed-attribute-pipeline-integration.md` (NEW)

Content sourced from concept doc Sections 2, 5, 8 and Sections 9-10:
- [x] Status: Accepted, date 2026-02-09
- [x] Context: Phase 2 needs to integrate computed attributes into the extraction-resolution-generation pipeline. Link Phase 1 results, ATTR-EXPR spike findings.
- [x] Decision section with 4 sub-decisions:
  - [x] **Integration Architecture** (concept doc Decision 1): Option C (direct graph integration). Include options-considered table (A/B/C/D) with pros/cons. Rationale: FORMULA/EXPOSE need different treatment; provenance matters; graph builder extension is moderate.
  - [x] **Pipeline Placement** (concept doc Decision 4): Step 4.5. Include updated pipeline flow diagram (Steps 1-8). Explain why Step 4.5 (needs design attrs from Step 4, feeds Step 5/6/7). Document Step 4/4.5 overlap resolution (FORMULA removed from design_attributes before Step 5).
  - [x] **Module Naming** (concept doc Decision 5): `{part_name}__{attr_name}` per ADR-003. Include examples table. Output channel: `{module_name}__{attr_name}` (PQN). Note member-name collision assumption.
  - [x] **Backtracker Awareness** (concept doc Decision 7): backtracker receives `list[ComputedAttributeData]`, builds lookup dict. Resolution rules: FORMULA -> MODULE_OUTPUT from synthetic module; EXPOSE_PURE -> follow alias; fallthrough to existing logic. Include solar_battery `p_net_kw` -> `annualized_om` example.
- [x] Chain handling section: compiler treats computed attr refs identically to literal refs; chain resolution is topological ordering in graph builder. Not a decision -- a finding that simplifies implementation.
- [x] Provenance: `PipelineModule.is_computed_attribute` flag; `# source: computed_attribute` in YAML
- [x] Consequences (positive/negative)
- [x] Examples: probe fixture chain (area -> cost -> cost_density), solar_battery p_net_kw
- [x] References: concept doc, spike reports, ADR-003, ADR-005
- [x] Changelog entry

### Validation

- [x] Verify: ADR-005 is self-standing -- read it without concept doc and confirm all decisions are clear with examples
- [x] Verify: ADR-004 is self-standing -- read it without concept doc and confirm all decisions are clear with examples
- [x] Verify: ADR-004 -> ADR-005 cross-reference points to correct document
- [x] Verify: ADR-005 -> ADR-004 cross-reference points to correct document
- [x] Verify: Both follow existing ADR format (Status, Context, Decision, Consequences, References, Changelog)

**What We Know Works After This Phase:**
All 5 ADRs exist. The two new ADRs capture the full ATTR-EXPR architectural reasoning as self-standing documents. Cross-references between ADR-004 and ADR-005 are consistent.

---

## Phase 3: Amendments -- ADR-001 Clarification and ADR-002 Amendment

### Goal

Update the migrated ADRs with ATTR-EXPR changes. ADR-001 gets a clarification for computed attribute entry points. ADR-002 gets a FORMULA pattern exemption amendment with modeling guidance.

### Changes Required

#### 1. ADR-001 Clarification
**File:** `docs/architecture/ADR-001-input-parameter-definition.md` (MODIFY)

Per spec FR-2:
- [x] Update "What is NOT an Input Parameter" / "In Design" table:
  - Current row: `Expression (not literal) | attr total = a + b | Computed from other params`
  - Updated: Clarify that while the expression result (`total`) is NOT an entry point, its inputs (`a`, `b`) MAY be DESIGN_ATTRIBUTE entry points if they are literal-valued sibling attributes on the same part
  - Add note: "See ADR-004 (Computed Attribute Pipeline Integration) and ADR-005 (Computed Attribute Classification) for details on how FORMULA computed attributes generate synthetic pipeline modules whose literal inputs become entry points."
- [x] Add Changelog entry: `2026-02-09 | Clarification: Computed attribute expression inputs may be entry points (see ADR-004, ADR-005)`

#### 2. ADR-002 Amendment
**File:** `docs/architecture/ADR-002-calculation-architecture.md` (MODIFY)

Per spec FR-3. Append an Amendment section at the bottom (do NOT rewrite existing text):

- [x] **Amendment header**: `## Amendment: FORMULA Computed Attributes (2026-02-09)`
- [x] **Context**: ATTR-EXPR epic (Phase 2) adds attribute-level expression support
- [x] **Rule 3 Amendment**: Design attributes MAY contain arithmetic expressions referencing only sibling attributes on the same part (FORMULA pattern per ADR-005)
  - Conditions: all refs MUST resolve to siblings (same owner); no FeatureChainExpression (no calc output refs, no cross-part); supported operators: `+`, `-`, `*`, `/`
  - Pipeline treatment: generates synthetic pipeline module with auto-implemented code (see ADR-004)
- [x] **Updated Expression Taxonomy table**: Split the "Derived expression" row:
  - `FORMULA expression` | `designs/` attribute | >=1 (sibling attrs only) | PASS | `= length * width`
  - `Derived expression` | `designs/` attribute | >=1 (calc output refs) | FAIL | `= calc.output * 0.95`
- [x] **Known UX Gap**: EXPOSE_COMPUTED (`attribute x = calc.output * factor`) is NOT supported yet. Workaround: create a CalcDef (Phase 1 auto-implements it). See ADR-005 for classification details.
- [x] **Modeling Guidance**:
  - "Attribute expressions can reference sibling attributes on the same part. To reference a calc output, use the EXPOSE pattern (pure alias, no arithmetic) or create a CalcDef."
  - When to use CalcDef: reusable, complex, multi-part, or references calc outputs
  - When to use attribute expression: one-off, simple formula, same-part sibling refs only
  - Examples of what works (FORMULA) and what doesn't (EXPOSE_COMPUTED)
- [x] **References**: ADR-004, ADR-005
- [x] **Changelog entry**: `2026-02-09 | Amendment: FORMULA computed attributes permitted (Rule 3 relaxation). See ADR-004 for pipeline integration, ADR-005 for classification scheme.`

### Validation

- [x] Verify: ADR-001 clarification is accurate -- computed attr inputs are entry points, expression result is not
- [x] Verify: ADR-001 cites ADR-004 and ADR-005 correctly
- [x] Verify: ADR-002 amendment does NOT rewrite existing text -- only appends (confirmed via diff: first 559 lines identical to monorepo source)
- [x] Verify: Updated taxonomy table is consistent with ADR-005 classification definitions
- [x] Verify: Modeling guidance has concrete examples of FORMULA (works) and EXPOSE_COMPUTED (doesn't)
- [x] Verify: All cross-references (ADR-001->004/005, ADR-002->004/005) point to correct files
- [x] Verify: Changelog entries added to both files

**What We Know Works After This Phase:**
All 5 ADRs are complete and internally consistent. The full cross-reference graph is correct (001->004/005, 002->004/005, 004<->005, 004->003). Modeling guidance is clear and actionable.

---

## Phase 4: Epic Closure -- Lessons Learned, Status Updates, Archival

### Goal

Close out the ATTR-EXPR epic with lessons learned, status updates, backlog update, concept doc update, and archival of all active work items.

### Changes Required

#### 1. Epic Lessons Learned
**File:** `.project/backlog/epic_attribute_expression_capture.md` (MODIFY)

- [x] Fill in "What Went Well" section:
  - Spike de-risked the entire epic (already noted)
  - Purpose-built probe fixture with 14 FORMULA + 3 chain + 4 EXPOSE patterns provided comprehensive coverage
  - Phase 1 expression compiler reused with zero changes (as predicted)
  - Option C (direct graph integration) was cleaner than original Option A recommendation
  - Test suite grew from 167 (Phase 1 baseline) to 285 with zero regressions
  - Chain handling was a non-issue (biggest simplification)
  - Hardening pass in Item 3 caught edge cases before E2E validation
- [x] Fill in "What Could Improve" section:
  - Concept doc was drafted late in Item 1; would have been clearer to formalize architectural decisions before starting Item 2
  - ADR migration from monorepo was deferred too long -- should have been done during repo split
- [x] Fill in remaining "Surprises" entries:
  - EXPOSE_PURE backtracker transitive resolution already worked (zero code needed for CalcUsage->EXPOSE bindings)
  - Step 4/4.5 overlap was a real risk -- removing FORMULA from design_attributes was essential
  - Module naming collision between CalcUsage and AttributeUsage names is prevented by SysML namespace rules (assumption held)

#### 2. Epic Status Update
**File:** `.project/backlog/epic_attribute_expression_capture.md` (MODIFY)

- [x] Change `**Status**: Active (Items 1-4 complete, Item 5 ready)` to `**Status**: Complete`
- [x] Update Item 5 status from `Not Started` to `Complete`
- [x] Update "Last Updated" date
- [x] Update "Next Action" line to indicate epic is closed

#### 3. BACKLOG.md Update
**File:** `.project/backlog/BACKLOG.md` (MODIFY)

- [x] Move ATTR-EXPR from "P1 - High Priority" to "Completed" table
- [x] Add completion date, duration, and summary notes
- [x] Update checkboxes to reflect Item 5 completion
- [x] Update "Last Updated" date

#### 4. Concept Doc Status
**File:** `.project/concepts/attr-expr-architectural-decisions.md` (MODIFY)

- [x] Change `**Status**: Draft (pre-ADR)` to `**Status**: Superseded by ADR-004 and ADR-005`
- [x] Add note at top: "The architectural decisions in this document have been formalized as ADR-004 (Computed Attribute Pipeline Integration) and ADR-005 (Computed Attribute Classification) in `docs/architecture/`."

#### 5. Archive Active Work Items
- [x] `git mv .project/active/attr-expr-spike/ .project/completed/20260209_attr-expr-spike/`
- [x] `git mv .project/active/attr-expr-extraction/ .project/completed/20260209_attr-expr-extraction/`
- [x] `git mv .project/active/attr-expr-pipeline/ .project/completed/20260209_attr-expr-pipeline/`
- [x] `git mv .project/active/attr-expr-e2e/ .project/completed/20260209_attr-expr-e2e/`
- [x] `git mv .project/active/attr-expr-docs/ .project/completed/20260209_attr-expr-docs/`

### Validation

- [x] Verify: Epic doc Lessons Learned has substantive entries for all 3 sections
- [x] Verify: Epic status is "Complete" with all items marked complete
- [x] Verify: BACKLOG.md shows ATTR-EXPR in Completed section
- [x] Verify: Concept doc status is "Superseded by ADR-004 and ADR-005"
- [x] Verify: No `attr-expr-*` directories remain in `.project/active/`
- [x] Verify: All 5 directories exist in `.project/completed/` (with 20260209 timestamp prefix)

**Final validation:**
- [x] `uv run pytest tests/` -- all 285 tests still pass (no regressions from file moves)

**What We Know Works After This Phase:**
Epic is cleanly closed. All documentation is finalized. Active work items archived. Backlog reflects completion.

---

## Risk Management

| Risk | Mitigation |
|------|-----------|
| Cross-reference inconsistency between 5 ADRs | Write ADR-005 first (no forward refs), then ADR-004 (refs ADR-005 only), then amendments (ref both). Verify all links in Phase 3 validation. |
| ADR-004 becomes bloated with 4 decisions | Keep options-considered tables compact. Reference concept doc for extended rationale ("See concept doc Section 2 for detailed analysis"). |
| Monorepo ADR references are confusing | Add a note in the copied ADRs: "References below point to the original fusion_modeling monorepo paths from the time of authorship." |
| Archive moves break something | Run full test suite after Phase 4. `.project/` is not imported by code -- moves are safe. |

---

## Implementation Notes

*TO BE FILLED DURING IMPLEMENTATION*

### Phase 1 Completion
**Completed:** 2026-02-09
**Actual Changes:**
- Created `docs/architecture/` directory
- Copied ADR-001, ADR-002, ADR-003 from `~/fusion_modeling/docs/architecture/` (byte-identical, verified with `diff`)

**Issues:** None
**Deviations:** None

### Phase 2 Completion
**Completed:** 2026-02-09
**Actual Changes:**
- Created `docs/architecture/ADR-005-computed-attribute-classification.md` (18.2 KB) with 3 decisions: classification scheme, EXPOSE handling, qualified name resolution. Includes all 5 classification definitions with SysML examples, classification summary table, MIXED elimination rationale, EXPOSE-within-FORMULA interaction, and 3 concrete examples.
- Created `docs/architecture/ADR-004-computed-attribute-pipeline-integration.md` (17.3 KB) with 4 decisions: Option C integration, Step 4.5 placement, module naming, backtracker awareness. Includes options-considered table, pipeline flow diagram, chain handling non-decision, and 3 concrete examples with YAML output.
- Both ADRs follow existing format (Status, Context, Decision, Consequences, Examples, References, Changelog).
- Cross-references verified: ADR-004 references ADR-005 in context and references sections; ADR-005 references ADR-004 in references section.

**Issues:** None
**Deviations:** None -- ADR-005 written first as planned (ADR-004 forward-references it).

### Phase 3 Completion
**Completed:** 2026-02-09
**Actual Changes:**
- Modified `docs/architecture/ADR-001-input-parameter-definition.md`: Updated "Expression (not literal)" row in "What is NOT an Input Parameter" table to clarify that expression inputs MAY be entry points. Added changelog entry citing ADR-004/005.
- Modified `docs/architecture/ADR-002-calculation-architecture.md`: Appended "Amendment: FORMULA Computed Attributes (2026-02-09)" section with Rule 3 amendment, updated expression taxonomy table (FORMULA vs Derived split), known UX gap (EXPOSE_COMPUTED), modeling guidance with examples of what works and what doesn't, workaround for EXPOSE_COMPUTED. Added ADR-004/005 to References. Added changelog entry.
- Verified original ADR-002 text (first 559 lines) unchanged via diff against monorepo source.

**Issues:** None
**Deviations:** None

### Phase 4 Completion
**Completed:** 2026-02-09
**Actual Changes:**
- Filled epic Lessons Learned with 7 "What Went Well", 2 "What Could Improve", 6 "Surprises" entries
- Updated epic status from "Active (Items 1-4 complete, Item 5 ready)" to "Complete"; Item 5 status to "Complete"; "Next Action" to "Epic complete"
- Updated BACKLOG.md: moved ATTR-EXPR to Completed table with date, duration, summary; added EXPOSE_COMPUTED to Ideas/Future
- Updated concept doc status to "Superseded by ADR-004 and ADR-005" with pointer note
- Updated `.project/completed/CHANGELOG.md` with ATTR-EXPR epic entry and retrospective EXPR-CODEGEN entry
- Archived all 5 active work items to `.project/completed/` with `20260209_` timestamp prefix using `git mv` (preserves git history)
- Ran full test suite: 285 passed, 0 failures

**Issues:** None
**Deviations:**
- Used `git mv` instead of plain `mv` (user instruction, preserves git history)
- Added `20260209_` timestamp prefix to archived directories (per `/_my_project_manage close` convention)
- Plan originally listed plain `mv` without timestamps; adjusted to follow project conventions

---

**Status**: Complete
