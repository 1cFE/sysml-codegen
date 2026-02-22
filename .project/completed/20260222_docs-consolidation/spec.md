# Spec: Architecture Documentation Consolidation

**Status:** Draft
**Owner:** Reid Westwood
**Created:** 2026-02-20 16:29 UTC
**Complexity:** MEDIUM
**Branch:** cost-pattern-refactor

---

## Business Goals

### Why This Matters
The implemented design is documented across 40+ files in `.project/concepts/refactor-design-intent/` -- a development artifact with session logs, audit actions, spike notes, and validation reports. The official docs (`docs/architecture/`) contain 8 ADRs, 3 of which have stale file paths. A developer (or future Claude session) trying to understand the system must navigate the concept folder, which was never intended as permanent documentation.

### Success Criteria
- [ ] A developer can read `docs/` and understand every pipeline component, requirement, and invariant without touching `.project/concepts/`
- [ ] Every REQ-* tag is traceable from requirement definition to test file in a single lookup
- [ ] SysML modeling assumptions are explicitly documented as a design prerequisite
- [ ] The concept folder is clearly marked as archived/historical

### Priority
Post-refactor documentation consolidation. No code changes. Blocks nothing, but high value for maintainability and onboarding.

---

## Problem Statement

### Current State
- **27 validated design docs** (00-27) in `.project/concepts/refactor-design-intent/` with 169+ REQ-* requirements, cross-links, and source-code-verified accuracy
- **COMPONENT_CHECKLIST.md** with 29 components (C01-C27, X01-X02), acceptance criteria, and test file mappings
- **IMPLEMENTATION_PLAN.md** (1319 lines) with phase structure, test count tracking, and design doc amendments
- **8 ADR files** in `docs/architecture/` -- 3 stale (ADR-001/002/003), 5 current (ADR-004-008)
- **762 conformance tests** across 34 files covering ~130 unique REQ-* tags
- No consolidated architecture overview or reading guide

### Desired Outcome
`docs/architecture/` becomes the single authoritative source for the implemented design, with:
- A top-level architecture overview with reading guide
- All 27 design docs migrated (session noise stripped)
- A modeling assumptions document (prerequisite SysML conventions)
- A compact verification matrix (REQ -> test file)
- ADR files removed (content subsumed)

---

## Scope

### In Scope

**D1. Architecture Overview & Reading Guide** (NEW)
- Single consolidated document summarizing all pipeline layers
- Links to each detail doc by layer
- Data flow diagram (extraction -> analysis -> core -> resolution -> generation)
- Key architectural principles (ComputationGraph as single source of truth, typed registries, dual resolution architecture)
- Reading order guidance for newcomers

**D2. Migrate 27 Design Docs** (MOVE + CLEANUP)
- Move docs 00-27 from `.project/concepts/refactor-design-intent/` to `docs/architecture/reference/`
- Strip from each doc:
  - Session-specific markers ("DONE (Session 7)", "ok (s18)")
  - Validation status tables (the "ok | ok | ok | ok" matrices)
  - Implementation plan cross-references ("Detailed plan: `.project/active/...`")
  - Session log entries
  - Audit action references
- Preserve:
  - Requirements tables (REQ-* with "Verified by" columns)
  - Related Documents footers (update paths to new locations)
  - All technical content, cross-links, code examples
- Update internal cross-links to reflect new file locations

**D3. Modeling Assumptions Document** (NEW)
- Extract from ADR-001, ADR-002, ADR-006, ADR-007:
  - SysML library/design separation convention (calc defs in library/, values in design)
  - Expression type taxonomy (calc def formula, static expression, binding reference, dynamic expression = error)
  - Static evaluator supported operators
  - EXPOSE pattern conventions
  - Template instantiation convention (CalcUsages in PartDefs)
  - Uniform-array assumption for aggregation
  - "Compute once, look up thereafter" principle
- Frame as **prerequisites/assumptions** the codegen pipeline depends on
- NOT a design doc -- a statement of what the SysML models MUST look like

**D4. Verification Matrix** (NEW)
- Single document: `docs/architecture/verification-matrix.md`
- One row per REQ-* tag (~170 rows)
- Columns: REQ ID | Requirement (short text) | Component | Test File | Status
- Status: PASS, XFAIL (with reason), or UNTESTED
- Grouped by REQ family (alphabetical: AS, AST, BASE, BT, CA, ...)
- Source data: COMPONENT_CHECKLIST.md + conformance test catalog

**D5. Remove ADR Files**
- Delete all 8 ADR files from `docs/architecture/`
- Unique ADR content (modeling conventions, alternatives analysis) already captured in D3

**D6. Archive Concept Folder**
- Add `ARCHIVED.md` to `.project/concepts/refactor-design-intent/` stating:
  - "This folder contains development artifacts from the Feb 2026 refactor"
  - "Canonical documentation is now in `docs/architecture/`"
  - "Preserved for historical reference only"

### Out of Scope
- Writing new tests or new requirements
- Changing any code
- Rewriting the concept docs from scratch (migration, not recreation)
- Documenting cross-cutting concerns not yet covered (error handling, 270-combination matrix)
- Updating CLAUDE.md (separate task after docs are settled)

### Edge Cases & Considerations
- **Cross-link integrity**: The 27 docs have extensive internal cross-links (`[03-resolution-overview](03-resolution-overview.md)`). After moving to `docs/architecture/reference/`, all relative links must be updated.
- **Known issues in design docs**: Two unapplied amendments remain in IMPLEMENTATION_PLAN.md (doc 05 REQ-MF-01 qualifier, COMPONENT_CHECKLIST C15/C16 purity notes). These SHOULD be applied during migration.
- **Deferred issues**: 10 deferred issues documented in IMPLEMENTATION_PLAN.md should be mentioned in the architecture overview as known limitations.

---

## Requirements

### Functional Requirements

> Requirements below are from user's request unless marked [INFERRED].

1. **FR-1**: The architecture overview SHALL provide a single-page summary of all pipeline layers with links to detail docs
2. **FR-2**: All 27 design docs SHALL be migrated to `docs/architecture/reference/` with session-specific content stripped
3. **FR-3**: A modeling assumptions document SHALL capture SysML conventions that the pipeline depends on, extracted from ADR-001, ADR-002, ADR-006, and ADR-007
4. **FR-4**: A verification matrix SHALL map every REQ-* tag to its test file in a compact table (~170 rows)
5. **FR-5**: All 8 ADR files SHALL be removed from `docs/architecture/`
6. **FR-6**: The concept folder SHALL be marked as archived with a pointer to the new canonical location
7. **FR-7**: [INFERRED] Internal cross-links between migrated docs SHALL be updated to reflect new file locations
8. **FR-8**: [INFERRED] The two unapplied design doc amendments (REQ-MF-01 qualifier, C15/C16 purity notes) SHALL be applied during migration
9. **FR-9**: [INFERRED] Known deferred issues SHALL be listed in the architecture overview

---

## Acceptance Criteria

### Core Functionality
- [ ] `docs/architecture/` contains: `overview.md`, `modeling-assumptions.md`, `verification-matrix.md`, and `reference/` with 27 docs
- [ ] No ADR files remain in `docs/architecture/`
- [ ] Every REQ-* tag from the design docs appears in the verification matrix
- [ ] Every cross-link in migrated docs resolves correctly (no broken references)
- [ ] Concept folder has `ARCHIVED.md` pointing to new location

### Quality & Integration
- [ ] Existing tests continue to pass (no code changes in this spec)
- [ ] `docs/architecture/overview.md` can be read standalone as an architecture summary
- [ ] `docs/architecture/modeling-assumptions.md` can be read standalone as a modeling guide
- [ ] No session logs, audit actions, or validation matrices remain in migrated docs

---

## Deliverables Summary

| # | Deliverable | Type | Source |
|---|-------------|------|--------|
| D1 | `docs/architecture/overview.md` | NEW | Synthesized from docs 00, 02, 03, 09 |
| D2 | `docs/architecture/reference/00-pipeline-overview.md` through `27-typed-registry-refactor.md` | MOVE+CLEANUP | 27 concept docs |
| D3 | `docs/architecture/modeling-assumptions.md` | NEW | ADR-001, 002, 006, 007 |
| D4 | `docs/architecture/verification-matrix.md` | NEW | COMPONENT_CHECKLIST + test catalog |
| D5 | Remove `docs/architecture/ADR-*.md` (8 files) | DELETE | - |
| D6 | `.project/concepts/refactor-design-intent/ARCHIVED.md` | NEW | - |

---

## Related Artifacts

- **Source material**: `.project/concepts/refactor-design-intent/` (27 docs + strategy + checklist + plan)
- **Current official docs**: `docs/architecture/ADR-*.md` (8 files, to be removed)
- **Test catalog**: `tests/conformance/` (34 files, 762 tests, ~130 REQ-* tags)
- **Design**: `.project/active/docs-consolidation/design.md` (to be created)

---

**Next Steps:** After approval, proceed to `/_my_design`
