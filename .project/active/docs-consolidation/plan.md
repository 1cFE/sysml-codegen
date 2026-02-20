# Implementation Plan: Architecture Documentation Consolidation

**Status:** Draft
**Created:** 2026-02-20
**Last Updated:** 2026-02-20

## Source Documents
- **Spec:** `.project/active/docs-consolidation/spec.md` ← See here for requirements FR-1 through FR-9, acceptance criteria, deliverables D1-D6

## Implementation Strategy

**Phasing Rationale:**
The 27 design docs are the foundation everything else references. Phase 1 establishes the canonical file layout. Phase 2 captures ADR content before deletion. Phase 3 builds the verification matrix (mechanical extraction). Phase 4 writes the overview last, when all link targets exist.

Phase 1 is split into copy (1a) then edit (1b) so that `git diff` after 1b shows exactly what was changed. Phase 1b is parallelizable — each doc is independent — and should be delegated to subagents.

**Overall Validation Approach:**
- Each phase produces files that can be reviewed via `git diff`
- Cross-link integrity checked after Phase 1b and Phase 4
- No code changes — existing tests remain green throughout

---

## Phase 1a: Copy Design Docs (Exact)

### Goal
Copy all 27 design docs verbatim to `docs/architecture/reference/`. This establishes the target directory and provides a clean baseline for diffing edits in 1b.

### Changes Required

- [ ] Create `docs/architecture/reference/` directory
- [ ] Copy `00-pipeline-overview.md` through `27-typed-registry-refactor.md` (28 files) from `.project/concepts/refactor-design-intent/` to `docs/architecture/reference/`
- [ ] `git add` + commit the exact copies

### Validation

**Automated:**
- [ ] `diff -r` between source and target shows zero differences
- [ ] 28 files exist in `docs/architecture/reference/`

**What We Know Works After This Phase:**
Target directory exists. Every file is an exact copy. Clean git baseline for Phase 1b diffs.

---

## Phase 1b: Clean Up Migrated Docs (Parallelizable)

### Goal
Edit the copied docs in `docs/architecture/reference/` to:
1. Remove references to non-migrating development artifacts (PHASE*_AUDIT files, .project/ paths, IMPLEMENTATION_PLAN references)
2. Apply the two unapplied amendments from IMPLEMENTATION_PLAN.md
3. Strip any session-specific content if found

**Delegation strategy:** Launch one subagent per doc (or per batch of 4-5 docs). Each doc's edits are independent. Subagents receive clear instructions on what to strip and what to preserve.

### What to Strip (per doc)
Based on source analysis, the 27 design docs are already clean of session markers ("DONE (Session N)", "ok (sN)", validation matrices). Edits focus on:

1. **References to non-migrating files** — found in 2 docs:
   - `16-computed-attributes.md:250` — reference to `PHASE2_AUDIT_ACTIONS.md §C3` → replace with inline note about inherited attribute misclassification (the finding itself, not the audit reference)
   - `27-typed-registry-refactor.md` — 6 references to `.project/research/`, `.project/active/`, `IMPLEMENTATION_PLAN.md` → remove or convert to inline notes

2. **Apply unapplied amendment #1** (from IMPLEMENTATION_PLAN.md amendments table line 1273):
   - `05-module-factory.md`: Remove "in the refactored state" qualifier from REQ-MF-01 (it IS the refactored state now)

3. **Apply unapplied amendment #2** (from IMPLEMENTATION_PLAN.md amendments table line 1274):
   - This targets COMPONENT_CHECKLIST.md (C15/C16 purity notes) which is NOT being migrated, so **no action needed in Phase 1b** — note this for Phase 3 verification matrix if relevant

### What to Preserve
- All requirements tables (REQ-* with "Verified by" columns)
- All technical content, code examples, cross-links between docs 00-27
- Related Documents footers (cross-links between numbered docs are relative and still valid within `reference/`)

### Changes Required

**Per-doc subagent instructions template:**
```
Read docs/architecture/reference/{NN}-{name}.md

Strip:
- Any references to PHASE*_AUDIT_ACTIONS.md → replace with inline note preserving the finding
- Any .project/ paths → remove or replace with note about the finding
- Any IMPLEMENTATION_PLAN.md references → remove

Apply amendments if this doc is 05-module-factory.md:
- Remove "in the refactored state" qualifier from REQ-MF-01

Preserve:
- All REQ-* tables and "Verified by" columns
- All technical content and code examples
- All cross-links to other numbered docs (e.g., [01-extraction.md](01-extraction.md))
- Related Documents footers
```

Specific files needing edits (from source analysis):
- [ ] `reference/05-module-factory.md` — apply REQ-MF-01 amendment
- [ ] `reference/16-computed-attributes.md` — replace audit reference with inline note
- [ ] `reference/27-typed-registry-refactor.md` — clean 6 .project/ and IMPLEMENTATION_PLAN references

All other 25 docs: verify clean (no edits expected, but subagent should confirm).

### Validation

**Automated:**
- [ ] `git diff docs/architecture/reference/` shows only the expected edits (not wholesale rewrites)
- [ ] No remaining references to `PHASE*_AUDIT`, `.project/active/`, `.project/research/` in any migrated doc
- [ ] Cross-links between numbered docs still use relative paths (e.g., `(01-extraction.md)`)

**Manual:**
- [ ] Review `git diff` — edits should be minimal and surgical

**What We Know Works After This Phase:**
27 design docs are clean, self-contained within `reference/`, and have no dangling references to development artifacts.

---

## Phase 2: Modeling Assumptions Document (D3) + ADR Removal (D5)

### Goal
Synthesize `docs/architecture/modeling-assumptions.md` from ADR-001/002/006/007 content, then delete all 8 ADR files. Grouping creation + deletion ensures no content is lost.

### Content Outline for `modeling-assumptions.md`

Extract and reorganize from ADRs (see spec D3 for full list):

1. **SysML Library/Design Separation** (ADR-001, ADR-002)
   - Calc defs live in `library/`, values in `design/`
   - Core principle: input parameter = literal in design file user may override

2. **Expression Type Taxonomy** (ADR-002)
   - Calc def formula, static expression, binding reference, dynamic expression = error
   - Evaluation strategy per type

3. **Static Evaluator Supported Operators** (ADR-002)

4. **EXPOSE Pattern Conventions** (ADR-002)

5. **Template Instantiation Convention** (ADR-006)
   - CalcUsages in PartDefs are templates
   - Virtual CalcUsage generation per (template, PartUsage) pair

6. **Uniform-Array Assumption for Aggregation** (ADR-007)
   - Parametric multiply strategy: `sum(child.attr)` → `count * child.attr`
   - Multiplicity counts become Integer entry points

7. **"Compute Once, Look Up Thereafter" Principle** (ADR-001)

Frame as **prerequisites** — what the SysML models MUST look like for the pipeline to work correctly.

### Changes Required

- [ ] Read all 8 ADR files fully to identify unique content
- [ ] Write `docs/architecture/modeling-assumptions.md` synthesizing the above
- [ ] Verify all unique ADR content is captured (alternatives analysis, context sections with novel info)
- [ ] Delete 8 files: `docs/architecture/ADR-001-input-parameter-definition.md` through `ADR-008-output-registry.md`
- [ ] Check no remaining files in `docs/architecture/` reference ADR files by name

### Validation

**Automated:**
- [ ] `ls docs/architecture/ADR-*` returns empty
- [ ] `grep -r 'ADR-00' docs/architecture/` — no broken references (or all are in historical context within modeling-assumptions.md)

**Manual:**
- [ ] `modeling-assumptions.md` reads standalone as a modeling guide
- [ ] Spot-check: key decisions from each ADR are captured

**What We Know Works After This Phase:**
ADR content is consolidated into a single prerequisites document. No orphaned ADR files.

---

## Phase 3: Verification Matrix (D4)

### Goal
Build `docs/architecture/verification-matrix.md` mapping every REQ-* tag (~197 unique) to its test file, component, and status.

### Approach

This is largely mechanical extraction:
1. Extract REQ tags from design docs (source: `docs/architecture/reference/*.md`)
2. Extract REQ tags from conformance tests (source: `tests/conformance/*.py`)
3. Cross-reference with COMPONENT_CHECKLIST.md for component mapping
4. Mark status: PASS (test exists + passes), XFAIL (test exists + xfail), UNTESTED (no test found)

### Data Sources
- **REQ definitions**: 197 unique REQ tags across 27 design docs
- **REQ coverage**: 192 unique REQ tags exercised in 37 conformance test files
- **Component mapping**: COMPONENT_CHECKLIST.md C01-C27, X01-X02

### Changes Required

- [ ] Script or manual extraction of REQ→test file mapping
- [ ] Write `docs/architecture/verification-matrix.md` with table grouped by REQ family
- [ ] Columns: REQ ID | Requirement (short text) | Component | Test File | Status

### Validation

**Automated:**
- [ ] Every REQ-* tag from `docs/architecture/reference/*.md` appears in the matrix
- [ ] Every test file referenced in the matrix exists

**Manual:**
- [ ] Spot-check 10 rows: REQ text matches source doc, test file has matching test

**What We Know Works After This Phase:**
Single-lookup traceability from any REQ-* tag to its test file.

---

## Phase 4: Architecture Overview (D1) + Archive Marker (D6)

### Goal
Write `docs/architecture/overview.md` as the single-page architecture summary with reading guide. Add `ARCHIVED.md` to the concept folder.

### Content Outline for `overview.md`

1. **What sysml-codegen does** — 2-3 sentence summary
2. **Data flow diagram** — the 7-step pipeline (text-based, from doc 00)
3. **Key architectural principles**:
   - ComputationGraph as single source of truth
   - Typed registries (ScopedKey, SysMLQN, CanonicalChannel)
   - Dual resolution architecture (3 paths)
   - Test-first with real data (no mocks)
4. **Reading guide** — recommended order for newcomers:
   - Start: `overview.md` (this doc)
   - Prerequisites: `modeling-assumptions.md`
   - Pipeline walkthrough: docs 00, 01, 11, 03, 06, 05, 07, 08
   - Deep dives: remaining docs by topic
5. **Component index** — compact table linking component ID → doc → package
6. **Known limitations** — 10 deferred issues from IMPLEMENTATION_PLAN.md (FR-9)
7. **Verification** — pointer to `verification-matrix.md`

### Changes Required

- [ ] Write `docs/architecture/overview.md`
- [ ] Write `.project/concepts/refactor-design-intent/ARCHIVED.md` with:
  - "This folder contains development artifacts from the Feb 2026 refactor"
  - "Canonical documentation is now in `docs/architecture/`"
  - "Preserved for historical reference only"
- [ ] Verify all links in overview.md resolve to existing files

### Validation

**Automated:**
- [ ] All markdown links in `overview.md` point to files that exist
- [ ] `docs/architecture/` contains: `overview.md`, `modeling-assumptions.md`, `verification-matrix.md`, `reference/` (28 files)
- [ ] No ADR files remain
- [ ] Existing tests still pass (`uv run pytest tests/`)

**Manual:**
- [ ] `overview.md` reads standalone — a developer unfamiliar with the project can follow it
- [ ] `ARCHIVED.md` exists in concept folder

**What We Know Works After This Phase:**
All acceptance criteria from spec are met. `docs/architecture/` is the single authoritative source.

---

## Risk Management

| Risk | Phase | Mitigation |
|------|-------|------------|
| Cross-link breakage after migration | 1a/1b | Docs 00-27 use relative links to each other — all go to same directory, links preserved. Only 2 docs reference non-migrating files. |
| Session noise heavier than expected | 1b | Source analysis shows 27 design docs are already clean. Subagents confirm per-doc. |
| ADR content missed during D3 synthesis | 2 | Read all 8 ADRs fully before writing. Cross-check unique sections (Context, Alternatives Considered). |
| REQ tag mismatch between docs and tests | 3 | ~5 REQ tags in docs but not tests (expected — some are design-only). Mark as UNTESTED with note. |
| Overview too long or too short | 4 | Target ~200 lines. Link to detail docs rather than duplicating content. |

---

## Implementation Notes

### Phase 1a Completion
**Completed:**
**Actual Changes:**
**Issues:**

### Phase 1b Completion
**Completed:**
**Actual Changes:**
**Issues:**

### Phase 2 Completion
**Completed:**
**Actual Changes:**
**Issues:**

### Phase 3 Completion
**Completed:**
**Actual Changes:**
**Issues:**

### Phase 4 Completion
**Completed:**
**Actual Changes:**
**Issues:**

---

**Status**: Draft → In Progress → Complete
