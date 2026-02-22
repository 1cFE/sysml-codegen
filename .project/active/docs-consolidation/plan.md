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
Edit the copied docs in `docs/architecture/reference/` to strip ALL development-process artifacts per the spec's D2 requirements. The docs should read as permanent architecture documentation, not development session logs.

**Delegation strategy:** Launch one subagent per batch of 4-5 docs. Each doc's edits are independent.

### What to Strip (per doc)

Per spec D2, strip from every doc:

1. **Audit action references** — any mention of conformance component IDs as provenance:
   - `(C03 conformance, 2026-02-17)`, `(C16 conformance finding (2026-02-17))`, `(X01, 2026-02-19)`
   - `C3 Phase 2 Audit findings`, `C6 probe`, `C5 probe`, `C12 spike`
   - `PHASE2_AUDIT_ACTIONS.md §C3`
   - **Rule**: Strip the provenance label and date. Keep the technical finding.
   - Example: `> **Coverage note (C17 conformance, 2026-02-17)**: solar_battery has zero...` → `> **Note**: solar_battery has zero...`

2. **Implementation plan cross-references**:
   - `.project/active/...`, `.project/research/...` paths
   - `IMPLEMENTATION_PLAN.md` references
   - `revision_backlog.md` references
   - `Deferred Issue #N` numbering → keep the issue content, drop the tracking ID
   - `Phase 7 refactor`, `C05 classifier fix` as future-work references → generalize to "future work"
   - **Rule**: Remove path/tracking-ID. Preserve the technical content inline.

3. **Session-specific markers**:
   - Dates used as provenance: `(2026-02-17)`, `(2026-02-18)`, `(2026-02-19)`
   - `Bug A (20b720e)` commit hash references
   - `added C20`, `Fixed: C20`, `Fixed (C20, 2026-02-18)`
   - Changelog blockquotes (`> **Changelog**: Added 2026-02-17 from...`)
   - **Rule**: Remove entirely, or keep only the technical fact (e.g., "Fixed" without the milestone).

4. **Apply unapplied amendment**:
   - `05-module-factory.md`: Remove "in the refactored state" qualifier from REQ-MF-01

### What to Preserve
- All requirements tables (REQ-* with "Verified by" columns)
- All technical content: bug descriptions, root causes, impacts, workarounds, code examples
- All cross-links between numbered docs (relative paths within `reference/`)
- Related Documents footers
- Known Issues / Known Limitations sections (content, not the tracking metadata)

### Files Requiring Edits (16 of 28)

Source analysis (grep for dates, component IDs, .project/ paths, audit references):

- [x] `01-extraction.md` — 3 findings: C3 data gap note, Deferred Issue #9 ref, C03 coverage note
- [x] `04-input-resolver.md` — 2 findings: C12 spike coverage notes (×2)
- [x] `05-module-factory.md` — 2 findings: C16 conformance note, REQ-MF-01 amendment
- [x] `06-entry-point-classifier.md` — 1 finding: C17 coverage note
- [x] `07-graph-assembly.md` — 1 finding: "added C20, 2026-02-18" in section heading
- [x] `08-generation.md` — 2 findings: X01 date references in REQ-GEN-06 and resolution note
- [x] `09-data-models.md` — 1 finding: C3 footnote
- [x] `11-analysis-backtracker.md` — 4 findings: C11b dispatch section header + date, C6 probe note, C6 cross-scope probe ref
- [x] `16-computed-attributes.md` — 7 findings: C05/C3 notes, Changelog blockquote, PHASE2_AUDIT ref, Deferred Issue #9/#10 labels, Phase 7/C05 future refs
- [x] `18-literal-value-propagation.md` — 1 finding: C16 conformance note
- [x] `19-ast-dispatch-invariant.md` — 3 findings: Bug A commit hash, "Dispatch Site Audit" heading, C07 note
- [x] `21-pipeline-yaml-generation.md` — 3 findings: C20 fix references (×3)
- [x] `22-output-schema-rules.md` — 2 findings: Bug 11 heading with date, C22 conformance ref
- [x] `24-dual-resolution-architecture.md` — 1 finding: X02 date in section heading
- [x] `25-hierarchy-resolver.md` — 1 finding: C06+C5 coverage note
- [x] `27-typed-registry-refactor.md` — 7 findings: .project/ paths (×4), IMPLEMENTATION_PLAN ref, revision_backlog ref, C08→C11 milestone ref

Remaining 12 docs (00, 02, 03, 10, 12, 13, 14, 15, 17, 20, 23, 26): expected clean — subagent confirms.

### Validation

**Automated:**
- [x] Zero matches for: `2026-02-\d{2}` (dates as provenance)
- [x] Zero matches for: `PHASE.*AUDIT`, `.project/`, `IMPLEMENTATION_PLAN`, `revision_backlog`
- [x] Zero matches for: `\bC\d{1,2}\b` used as conformance component labels (C03, C16, X01, etc.)
- [x] Zero matches for: `Deferred Issue #\d+`
- [x] Cross-links between numbered docs still use relative paths
- [x] `git diff` shows edits are surgical (content preserved, only metadata stripped)

**Manual:**
- [x] Spot-check 3 docs: read the Known Issues / coverage notes and confirm they read as permanent docs, not session logs

**What We Know Works After This Phase:**
28 design docs have no syntactic development artifacts (audit labels, dates, .project/ paths, tracking IDs). But the content has NOT been verified for accuracy or architectural tone. Phase 1c does that.

---

## Phase 1c: Content Accuracy & Architectural Tone Review (All 28 Docs)

### Goal
Phase 1b was mechanical find-and-replace. It stripped labels but didn't verify whether the underlying claims are still true, or whether the content belongs in architecture documentation at all. Phase 1c reviews every document independently and ensures each one reads as an **accurate, definitive architectural description** — not a development session log with the dates filed off.

### Why This Phase Exists
Phase 1b left at least two categories of problems:
1. **Stale claims** — Bug 11 (doc 22) says "fix deferred" but commit `4c214d1` already fixed it. The date was stripped, making a false claim look authoritative.
2. **Test-coverage metadata disguised as architecture** — "Coverage note: Strategy B has zero exercise for aggregation scope" is a test-gap observation, not a design decision or known limitation. Stripping the `(C12 spike, 2026-02-17)` label doesn't make it architecture — it just makes it undated test-coverage metadata.

### What Each Doc Review Must Do

For each of the 28 docs, the reviewer must:

1. **Read the document end-to-end** as if you're a developer encountering it for the first time.

2. **Assess each note/blockquote on its value to describing the architecture:**
   - Does this help a developer understand the design, its constraints, or its edge cases? → KEEP (reword if needed to read as architecture, not as a test report).
   - Is this purely about which test fixtures exercise which paths, with no architectural insight? → REMOVE.
   - Does this describe a defensive code path that's unreachable under normal conditions? That IS architecture — it tells a developer not to rely on that path. Keep it, framed as a design observation.
   - Is this about test coverage gaps with no design implication? → REMOVE.
   - Use judgment. The goal is: would a developer benefit from knowing this when working on the code?

3. **Verify every status/state claim against the current codebase:**
   - "Fix deferred" → Is it still deferred? Check git log and code.
   - "Bug: [description]" → Is the bug still present? Check if tests are still xfailed.
   - "Not implemented" / "Deferred" → Still true?
   - "Tracked as xfail in [test]" → Is it still xfailed?
   - Update or remove claims that are no longer accurate.

4. **Verify every factual claim in notes/blockquotes against the codebase:**
   - "Zero exercise / zero coverage for X" → Confirm by checking fixture extraction snapshots, test call sites, or grep for the relevant code path. Do not assume a claim is still true just because it was true when written.
   - "No model contains X" → Verify across all fixture models (`tests/fixtures/*/extraction_snapshot.json`, `.sysml` files).
   - "Strategy X is never triggered" → Trace the code path and confirm the guard condition holds for current data.
   - Claims originally tied to a specific date/audit action are especially suspect — the codebase may have changed since the observation was recorded.
   - If a claim is verified, keep it (reframed as architecture). If falsified, correct or remove it.

5. **Verify Known Issues sections are still known issues:**
   - Each Known Issue must still be an actual open issue.
   - If fixed → remove or convert to a "Resolution" note.
   - If still open → keep, but ensure description matches current code behavior.

6. **Ensure the document reads as definitive architecture:**
   - Would a new team member reading this understand the design?
   - Is there hedging language that should be assertive? ("may produce", "is expected to" → state what it does)
   - Are there "future work" references to things that already happened?

### Files to Review (All 28)

Every doc in `docs/architecture/reference/` gets a full review. Group by expected effort:

- [x] `00-pipeline-overview.md`
- [x] `01-extraction.md`
- [x] `02-orchestration.md`
- [x] `03-resolution-overview.md`
- [x] `04-input-resolver.md`
- [x] `05-module-factory.md`
- [x] `06-entry-point-classifier.md`
- [x] `07-graph-assembly.md`
- [x] `08-generation.md`
- [x] `09-data-models.md`
- [x] `10-output-registry.md`
- [x] `11-analysis-backtracker.md`
- [x] `12-virtual-binding-rewrite.md`
- [x] `13-aggregation-scoping.md`
- [x] `14-expression-compiler.md`
- [x] `15-naming-conventions.md`
- [x] `16-computed-attributes.md`
- [x] `17-parameter-group-deriver.md`
- [x] `18-literal-value-propagation.md`
- [x] `19-ast-dispatch-invariant.md`
- [x] `20-module-registry-generation.md`
- [x] `21-pipeline-yaml-generation.md`
- [x] `22-output-schema-rules.md`
- [x] `23-smart-regen-preservation.md`
- [x] `24-dual-resolution-architecture.md`
- [x] `25-hierarchy-resolver.md`
- [x] `26-pipeline-module-migration.md`
- [x] `27-typed-registry-refactor.md`

### Delegation Strategy

Launch subagents per batch, but each subagent MUST have codebase access to verify claims. Each subagent:
- Reads the doc
- For every status/coverage/bug claim, checks the current code or tests
- Edits the doc to remove or correct stale content
- Reports what was changed and why

### Validation

**Automated:**
- [x] No remaining "Coverage note" blockquotes in any doc
- [x] No "xfail" references that point to tests that are no longer xfailed
- [x] No "deferred" or "not implemented" claims for things that have been implemented

**Manual:**
- [ ] Read 3 high-effort docs end-to-end and confirm they read as definitive architecture descriptions
- [ ] Confirm Bug 11 section in doc 22 reflects the fix

**What We Know Works After This Phase:**
Every document is accurate as of the current codebase state. No stale bug reports, no test-coverage metadata, no false "deferred" claims. Each doc reads as a definitive architectural description that a new developer can trust.

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

- [x] Read all 8 ADR files fully to identify unique content
- [x] Write `docs/architecture/modeling-assumptions.md` synthesizing the above
- [x] Verify all unique ADR content is captured (alternatives analysis, context sections with novel info)
- [x] Delete 8 files: `docs/architecture/ADR-001-input-parameter-definition.md` through `ADR-008-output-registry.md`
- [x] Check no remaining files in `docs/architecture/` reference ADR files by name

### Validation

**Automated:**
- [x] `ls docs/architecture/ADR-*` returns empty
- [x] `grep -r 'ADR-00' docs/architecture/` — no broken references

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
| Mechanical cleanup leaves stale/false claims | 1c | Phase 1b only stripped syntax (labels, dates, paths). Phase 1c verifies every factual claim against the codebase. Each note assessed individually for architectural value. |
| ADR content missed during D3 synthesis | 2 | Read all 8 ADRs fully before writing. Cross-check unique sections (Context, Alternatives Considered). |
| REQ tag mismatch between docs and tests | 3 | ~5 REQ tags in docs but not tests (expected — some are design-only). Mark as UNTESTED with note. |
| Overview too long or too short | 4 | Target ~200 lines. Link to detail docs rather than duplicating content. |

---

## Implementation Notes

### Phase 1a Completion
**Completed:** 2026-02-20 (commit 49c2fde)
**Actual Changes:** Copied 28 files from `.project/concepts/refactor-design-intent/` to `docs/architecture/reference/`
**Issues:** None

### Phase 1b Completion
**Status:** NOT APPLIED — plan was pre-filled but work was reverted.
**What happened:** Commit 66d2411 cleaned 3 docs; commit c77eff7 reverted it. The full 16-doc cleanup was never committed. All 28 docs still contain audit artifacts as of Phase 1c start.
**Resolution:** Phase 1b work is being performed as part of Phase 1c (combined pass: strip artifacts + content accuracy review). This is more efficient — each doc is read end-to-end once for both mechanical stripping and content assessment.

### Phase 1c Completion (includes Phase 1b work)
**Started:** 2026-02-20
**Approach:** Combined 1b+1c in single pass per doc batch. Each doc gets: (1) mechanical artifact stripping, (2) content accuracy verification against codebase, (3) architectural tone assessment. Batches of ~5 docs with user approval checkpoint between each.

**Batch 1 (docs 00–04):** Complete.
- Doc 00: Updated package structure (orchestration/ now exists), removed stale "does not yet exist" note
- Doc 01: Stripped C3/C03 audit refs, reframed PartDefinitionData limitation as "Known limitation", removed Deferred Issue #9 label
- Doc 02: Updated initialization.py → orchestration/pipeline_builder.py, changed future tense to present
- Doc 03: No edits needed — clean, accurate
- Doc 04: Stripped C12 audit refs from Strategy B and D notes; verified both claims against codebase

**Batch 2 (docs 05–09):** Complete.
- Doc 05: Applied REQ-MF-01 amendment (removed "in the refactored state"), stripped C16 audit ref
- Doc 06: Stripped C17 audit ref, generalized namespace mismatch note from solar_battery-specific
- Doc 07: Stripped "(added C20, 2026-02-18)" from section heading
- Doc 08: Stripped X01 audit ref, corrected REQ-GEN-06 description (type_mapping.py used by 2 generators, not all 5)
- Doc 09: Stripped C3/Deferred Issue #9 from UNRESOLVABLE footnote, updated PipelineContext location

**Batch 3 (docs 10–14):** Complete.
- Doc 10: Updated `build_output_registry()` location from initialization.py to orchestration/output_registry_builder.py
- Doc 11: Stripped C11b/C6 audit refs, removed "See C6 deep cross-scope probe findings" dangling ref, removed entire "Compat-Only Resolution Migration" section (23 lines of implementation history, not architecture)
- Doc 12: Updated `_rewrite_virtual_bindings()` location to orchestration/pipeline_builder.py
- Doc 13: Updated 4 stale initialization.py file refs + Key Source Files table to orchestration/ paths
- Doc 14: No edits needed — clean, accurate

**Batch 4 (docs 15–19):** Complete.
- Doc 15: Fixed `ScopedKey.from_eqn()` → `make_scoped_key()` (NewType has no methods). All naming claims verified.
- Doc 16: Stripped 7 artifacts (C05/C3 notes, changelog blockquote, PHASE2_AUDIT, Deferred Issue #9/#10 labels, Phase 7/C05 future refs). Fixed stale line number, updated initialization.py → pipeline_builder.py.
- Doc 17: Fixed stale initialization.py path → pipeline_builder.py, fixed cross-ref (classify() called from graph assembly, not module factory), deduplicated Related Docs.
- Doc 18: Stripped C16 conformance label. Replaced 7 brittle line-number refs with structural references. Fixed stale initialization.py → pipeline_builder.py.
- Doc 19: Stripped 3 artifacts (commit hash ×4, "Dispatch Site Audit" heading, C07 note). Removed audit tracking columns from tables. Fixed wrong function name → `_extract_single_redefinition`.

**Batch 5 (docs 20–24):** Complete.
- Doc 20: Reframed "Bug 8" section → "Design Constraints". Stripped Bug 8a/8b labels. Fixed 3 wrong file paths (resolution/ → core/). Updated code examples to match actual @dataclass(frozen=True) structure.
- Doc 21: Stripped 3 C20 references. Updated 4 stale line numbers. Fixed stale field name `graph.parameter_groups` → `graph.entry_point_groups`.
- Doc 22: Stripped Bug 11 date + C22 conformance ref. **Updated Bug 11 from "deferred" to "Fix applied"** (commit 4c214d1). Fixed 2 wrong function names, corrected type default behavior.
- Doc 23: No artifacts. 7 accuracy fixes: wrong function parameter type (CalcDef → PipelineModule), wrong stub upgrade condition, nonexistent functions in REQ-SR-06, stale line numbers.
- Doc 24: Stripped 2 artifacts (X02 label + date). Removed 3 brittle line numbers. Fixed BindingInfo file location.

**Batch 6 (docs 25–27):** Complete.
- Doc 25: Stripped spike Q5 provenance ref + C06/C5 coverage note → architectural "Edge case" note. All 16 line numbers verified accurate.
- Doc 26: No artifacts. **Major rewrite**: migration is fully completed, not planned. Reframed from forward-looking to completed state. Fixed field name qualified_name → calc_def_qualified_name.
- Doc 27: Stripped all 7 expected artifacts (.project/ ×4, IMPL_PLAN, backlog, C08→C11). Removed entire stale `_compat` bridge section. Rewrote constructor table (NewType has no .from_*() methods). Added missing CHAIN dispatch Step 1b. Fixed REFERENCE dispatch oversimplification.

**Completed:** 2026-02-21
**Actual Changes:** All 28 docs reviewed. 25 of 28 edited (docs 03, 14 were clean in prior batches). Combined artifact stripping + content accuracy verification in single pass per doc.
**Issues:** None. All validation checks pass: zero matches for dates, .project/ paths, conformance labels, Deferred Issue IDs, Coverage notes, initialization.py refs.

### Phase 2 Completion
**Completed:** 2026-02-22
**Actual Changes:**
- Created `docs/architecture/modeling-assumptions.md` (7 sections + validation rules + related docs)
  - Section 1: Library/Design Separation (from ADR-001, ADR-002)
  - Section 2: Input Parameter Classification (3 types, value types, units, grouping — from ADR-001)
  - Section 3: Design Attribute Expression Rules (taxonomy, FORMULA, EXPOSE, operators — from ADR-002)
  - Section 4: Aggregation via Redefinition (from ADR-002 hierarchy amendment, ADR-007)
  - Section 5: Template Instantiation Convention (from ADR-006)
  - Section 6: Uniform-Array Assumption for Aggregation (from ADR-007)
  - Section 7: Compute Once, Look Up Thereafter (from ADR-003)
- Deleted 8 ADR files via `git rm`
- Updated 7 ADR references across 3 reference docs:
  - `reference/15-naming-conventions.md`: Removed "ADR-003, ADR-008" from authoritative sources line, removed "ADR-003 Phase 7" from binding_resolutions description
  - `reference/05-module-factory.md`: Removed "ADR-003 VIOLATION" from error message description
  - `reference/00-pipeline-overview.md`: Replaced 4 ADR references with direct terminology (e.g., "ADR-001 types" → "entry point types")

**Content disposition for ADR-003/004/005/008:**
ADR-003 (signal identifiers), ADR-004 (computed attribute pipeline integration), ADR-005 (computed attribute classification), and ADR-008 (output registry) contain pipeline architecture details already documented in the reference docs (docs 10, 14, 15, 16, 27). No unique modeling assumptions needed capture — these are implementation decisions, not SysML model prerequisites.

**Issues:** None

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
