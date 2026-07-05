# Spec: ATTR-EXPR Item 5a -- ADRs and Epic Closure

**Status:** Draft
**Owner:** Reid Westwood
**Created:** 2026-02-09T17:10:36+00:00
**Complexity:** MEDIUM
**Branch:** cost-pattern
**Epic:** ATTR-EXPR (Item 5)

---

## Business Goals

### Why This Matters

The ATTR-EXPR epic introduced 7 architectural decisions (concept doc), a new 5-way classification scheme, a new pipeline step (4.5), backtracker extensions, and graph builder extensions. These decisions exist only in a pre-ADR concept document (`.project/concepts/attr-expr-architectural-decisions.md`), scattered code comments, and spike reports. Without formal ADRs, future developers and agents lack the reasoning behind these choices.

Additionally, the epic's ADRs (001-003) were never carried forward from the `~/fusion_modeling/` monorepo during the repo split. Code comments and CLAUDE.md reference `docs/architecture/ADR-002-...` but no such directory exists in `sysml-codegen`. This is the opportunity to establish the canonical ADR location.

### Success Criteria

- [ ] ADR-001 through ADR-005 exist in `docs/architecture/` within `sysml-codegen`
- [ ] ADR-001 clarification correctly describes computed attribute entry point behavior, citing ADR-004/005
- [ ] ADR-002 amendment clearly distinguishes FORMULA (now permitted) from derived expressions (still prohibited)
- [ ] ADR-004 is self-standing: a new developer can understand computed attribute pipeline integration without reading the concept doc
- [ ] ADR-005 is self-standing: a new developer can understand the classification scheme with concrete examples
- [ ] Modeling guidance includes concrete examples of what works (FORMULA) and what doesn't yet (EXPOSE_COMPUTED)
- [ ] Epic Lessons Learned section filled in
- [ ] Active work items archived to `.project/completed/`
- [ ] Epic status updated to Complete

### Priority

P1 -- final item blocking ATTR-EXPR epic completion. Items 1-4 are all complete with 285 tests passing.

---

## Problem Statement

### Current State

- ADR-001, ADR-002, ADR-003 exist only in `~/fusion_modeling/docs/architecture/` (the pre-split monorepo). `sysml-codegen` has no `docs/architecture/` directory.
- 28+ code references to ADR-002 in `sysml-codegen` point to a path that doesn't exist locally.
- The 7 architectural decisions from ATTR-EXPR are captured in `.project/concepts/attr-expr-architectural-decisions.md` (pre-ADR draft) but not formalized.
- ADR-001's "What is NOT an Input Parameter" table (row: `Expression (not literal) | attr total = a + b | Computed from other params`) is misleading after ATTR-EXPR -- the expression's *inputs* (`a`, `b`) may still be entry points even though the expression result is computed.
- ADR-002 Rule 3 says design attributes "SHALL NOT contain derived expressions referencing other design attributes." After ATTR-EXPR, FORMULA patterns (`attribute area = length * width`) are explicitly permitted and generate pipeline modules.
- 4 active work item directories and 1 concept doc lack archival.
- Epic Lessons Learned section is partially filled.

### Desired Outcome

- Canonical ADR directory in `sysml-codegen` with all 5 ADRs.
- ADR-001 corrected for computed attribute entry points.
- ADR-002 amended for FORMULA pattern exemption.
- ADR-004 and ADR-005 capture the full ATTR-EXPR architectural reasoning.
- Modeling guidance embedded in the ADRs gives clear rules for when to use attribute expressions vs CalcDefs.
- Epic cleanly closed with archived work items.

---

## Scope

### In Scope

1. **Create `docs/architecture/` directory** in `sysml-codegen`

2. **Copy and establish ADR-001, ADR-002, ADR-003** from `~/fusion_modeling/docs/architecture/` as the canonical local source

3. **ADR-001 Clarification: Computed Attribute Entry Points**
   - Update the "What is NOT an Input Parameter" table in the "In Design" section
   - The row `Expression (not literal) | attr total = a + b | Computed from other params` MUST be corrected: the expression result (`total`) is not an entry point, but its inputs (`a`, `b`) MAY be entry points (as DESIGN_ATTRIBUTE type) if they are literal-valued sibling attributes
   - Add a note citing ADR-004 and ADR-005 as the explanation for why: FORMULA computed attributes generate synthetic pipeline modules whose literal inputs become entry points
   - Add a Changelog entry for this clarification

4. **ADR-002 Amendment: FORMULA Pattern Exemption**
   - Add an "Amendment" section at the bottom of ADR-002 (do not rewrite the existing text)
   - Rule 3 amendment: design attributes MAY contain arithmetic expressions referencing only sibling attributes on the same part (FORMULA pattern per ADR-005 classification)
   - Rule 5 (implied by Rule 3): simple formulas no longer require a CalcDef
   - Conditions: all feature references MUST resolve to sibling attributes (same owner); no FeatureChainExpression nodes (no calc output refs, no cross-part refs); supported operators: `+`, `-`, `*`, `/`
   - Pipeline treatment: FORMULA expressions generate synthetic pipeline modules with auto-implemented code (see ADR-004)
   - Update the Expression Taxonomy table: split "Derived expression" into "FORMULA expression" (PASS) and "Derived expression" (FAIL -- calc output refs)
   - Document the known UX gap: EXPOSE_COMPUTED (`attribute x = calc.output * factor`) is NOT yet supported; workaround is to create a CalcDef (Phase 1 auto-implements it)
   - Modeling guidance: "Attribute expressions can reference sibling attributes on the same part. To reference a calc output, use the EXPOSE pattern (pure alias, no arithmetic) or create a CalcDef."
   - When to use CalcDefs vs attribute expressions: reusable or complex logic -> CalcDef; one-off simple formula on a single part -> attribute expression
   - Add a Changelog entry
   - Reference ADR-004 and ADR-005

5. **ADR-004: Computed Attribute Pipeline Integration** (new)
   - Follows existing ADR format: Status, Context, Decision, Consequences, Examples, References, Changelog
   - Captures from the concept doc:
     - Decision 1: Option C (direct graph integration, not synthetic CalcDef/CalcUsage). Include the options-considered table.
     - Decision 4: Step 4.5 pipeline placement (after design attributes, before parameter groups). Include the updated pipeline flow diagram.
     - Decision 5: Module naming `{part_name}__{attr_name}` per ADR-003. Include examples table.
     - Decision 7: Backtracker MUST consume computed attributes for binding resolution. Include the solar_battery `p_net_kw` -> `annualized_om` example.
   - Step 4/4.5 overlap resolution: FORMULA attributes removed from design_attributes dict before ParameterGroupDeriver
   - Chain handling: compiler treats computed attribute refs identically to literal attribute refs; chain resolution is purely topological ordering in the graph builder
   - Provenance: `PipelineModule.is_computed_attribute = True` flag; `# source: computed_attribute` in YAML
   - References concept doc and spike findings for empirical grounding

6. **ADR-005: Computed Attribute Classification** (new)
   - Follows existing ADR format
   - Captures from the concept doc:
     - Decision 2: 5-way classification (FORMULA, EXPOSE_PURE, EXPOSE_COMPUTED, LITERAL, UNRESOLVABLE)
     - Decision 3: EXPOSE handling (PURE = alias providing wiring context, COMPUTED = deferred)
     - Decision 6: Qualified name resolution mandatory (19 CATF misclassifications without it)
   - Classification table with: definition, SysML examples from probe fixture and real models, pipeline treatment, generates module?
   - Why MIXED was dropped (zero occurrences; EXPOSE_PURE/EXPOSE_COMPUTED is more precise)
   - EXPOSE_COMPUTED deferral rationale and UX gap documentation
   - EXPOSE-within-FORMULA interaction: how FORMULA module inputs resolve through EXPOSE aliases

7. **Epic Closure**
   - Fill in Lessons Learned section on the epic doc (`epic_attribute_expression_capture.md`)
   - Update epic status to Complete
   - Update BACKLOG.md: move ATTR-EXPR to Completed section
   - Archive `.project/active/attr-expr-spike/` -> `.project/completed/attr-expr-spike/`
   - Archive `.project/active/attr-expr-extraction/` -> `.project/completed/attr-expr-extraction/`
   - Archive `.project/active/attr-expr-pipeline/` -> `.project/completed/attr-expr-pipeline/`
   - Archive `.project/active/attr-expr-e2e/` -> `.project/completed/attr-expr-e2e/`
   - Archive `.project/active/attr-expr-docs/` -> `.project/completed/attr-expr-docs/` (this item itself)

### Out of Scope

- **`agentic-mbse` upstream changes** -- `adr002.py` V2 FORMULA exemption, pattern doc updates (`adr002-calculations.md`, `expose-pattern.md`), agent command updates, `MODELING_GUIDE.md.template` updates. These are a separate work item in the `agentic-mbse` repo.
- **CLAUDE.md updates** -- deferred until PR review per epic
- **Phase 3 planning** -- explicitly deferred
- **`fusion-tea` changes** -- research confirmed zero needed
- **External documentation** -- no README, no API docs
- **Code changes** -- this is pure documentation; no source code modifications

### Edge Cases & Considerations

- **ADR format consistency**: ADR-004 and ADR-005 MUST follow the same structure as ADR-001/002/003 (Status, Context, Decision, Consequences, References, Changelog). The monorepo ADRs vary slightly in subsection structure but share the same top-level pattern.
- **Cross-references**: ADR-004 references ADR-003 (naming) and ADR-005 (classification). ADR-005 references ADR-004 (pipeline treatment). ADR-002 amendment references both. ADR-001 clarification cites ADR-004/005. These cross-references MUST be consistent.
- **Monorepo ADR copies**: When copying ADR-001/002/003 from `~/fusion_modeling/`, the file paths in their References sections point to monorepo locations (`project/research/...`, `docs/codegen/...`). These SHOULD be noted as historical references from the pre-split monorepo, not updated to point at `sysml-codegen` paths.
- **Concept doc status**: The concept doc (`.project/concepts/attr-expr-architectural-decisions.md`) SHOULD have its status updated from "Draft (pre-ADR)" to "Superseded by ADR-004/005" with a pointer to the new ADRs.

---

## Requirements

### Functional Requirements

> Requirements below are from user's request unless marked [INFERRED] or [FROM INVESTIGATION]

1. **FR-1**: Create `docs/architecture/` directory in `sysml-codegen` and copy ADR-001, ADR-002, ADR-003 from `~/fusion_modeling/docs/architecture/`

2. **FR-2**: Clarify ADR-001's "What is NOT an Input Parameter" table to correctly describe that a computed attribute expression's inputs MAY be entry points, citing ADR-004 and ADR-005 as explanation

3. **FR-3**: Amend ADR-002 with FORMULA pattern exemption for Rule 3, including the updated expression taxonomy, conditions, UX gap documentation, and modeling guidance

4. **FR-4**: Draft ADR-004 capturing computed attribute pipeline integration decisions (Option C, Step 4.5, module naming, backtracker awareness, chain handling)

5. **FR-5**: Draft ADR-005 capturing computed attribute classification scheme (5-way, EXPOSE strategy, qualified name resolution, MIXED elimination)

6. **FR-6**: ADR-004 and ADR-005 MUST be self-standing -- a reader can understand the decisions without reading the concept doc or spike reports

7. **FR-7**: [INFERRED] All ADRs MUST reference the concept doc and spike findings as empirical grounding (per epic Item 5 description)

8. **FR-8**: Fill in epic Lessons Learned section, update epic status to Complete, update BACKLOG.md

9. **FR-9**: Archive all `.project/active/attr-expr-*` directories to `.project/completed/`

10. **FR-10**: [INFERRED] Update concept doc status from "Draft (pre-ADR)" to "Superseded by ADR-004/005"

---

## Acceptance Criteria

### Core Functionality

- [ ] `docs/architecture/` directory exists with ADR-001 through ADR-005
- [ ] ADR-001 clarification: "Expression (not literal)" row updated with correct computed attribute entry point behavior; cites ADR-004/005
- [ ] ADR-002 amendment: FORMULA pattern exemption with conditions, taxonomy update, UX gap, modeling guidance; references ADR-004/005
- [ ] ADR-004: self-standing document covering Option C, Step 4.5, module naming, backtracker awareness, chain handling, with examples
- [ ] ADR-005: self-standing document covering 5-way classification with definitions, SysML examples, pipeline treatment per classification, qualified name resolution rationale
- [ ] All 5 ADRs have consistent cross-references (no broken or incorrect citations)
- [ ] Modeling guidance appears in ADR-002 amendment: what works (FORMULA), what doesn't (EXPOSE_COMPUTED), when to use CalcDef vs attribute expression

### Epic Closure

- [ ] Epic Lessons Learned populated with findings from Items 1-4
- [ ] Epic status: Complete
- [ ] BACKLOG.md: ATTR-EXPR in Completed section with summary
- [ ] `.project/active/attr-expr-spike/` archived to `.project/completed/`
- [ ] `.project/active/attr-expr-extraction/` archived to `.project/completed/`
- [ ] `.project/active/attr-expr-pipeline/` archived to `.project/completed/`
- [ ] `.project/active/attr-expr-e2e/` archived to `.project/completed/`
- [ ] `.project/active/attr-expr-docs/` archived to `.project/completed/`
- [ ] Concept doc status updated to "Superseded by ADR-004/005"

### Quality & Integration

- [ ] Existing tests continue to pass (no code changes, but verify nothing breaks from directory moves)
- [ ] ADR format matches existing ADR-001/002/003 structure

---

## Related Artifacts

- **Research:** `.project/research/20260209-165638_attr-expr-documentation-adrs-and-upstream-integration.md`
- **Concept Doc:** `.project/concepts/attr-expr-architectural-decisions.md` (source material for ADR-004/005)
- **Spike Reports:** `.project/active/attr-expr-spike/report.md`, `.project/active/attr-expr-spike/findings_v2.md`
- **E2E Report:** `.project/active/attr-expr-e2e/report.md`
- **Epic:** `.project/backlog/epic_attribute_expression_capture.md`
- **Monorepo ADRs:** `~/fusion_modeling/docs/architecture/ADR-001-...`, `ADR-002-...`, `ADR-003-...`
- **Design:** `.project/active/attr-expr-docs/design.md` (to be created)

---

**Next Steps:** After approval, proceed to `/_my_design`
