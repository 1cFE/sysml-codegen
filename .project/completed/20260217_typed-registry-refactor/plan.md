# Component: Typed Registry Refactor — Design Intent Document (TRR-1 / C27)

**Status**: DONE
**Created**: 2026-02-17
**Last updated**: 2026-02-17
**Updated by**: Planning agent (TRR-1 plan)

## Source Documents

- **Checklist entry**: `COMPONENT_CHECKLIST.md` — C27
- **Design intent**: `27-typed-registry-refactor.md` (this IS the deliverable)
- **Requirements**: FR-1 through FR-6, NFR-1 through NFR-3
- **Depends on**: Key_A fallback spike (`.project/research/20260217-060000_key-a-fallback-spike.md`) — COMPLETE
- **Spec**: `.project/active/typed-registry-refactor/spec.md` — COMPLETE

---

## 1. Assessment

### What This Component Does

TRR-1 creates the new design intent document `27-typed-registry-refactor.md`. This is the
authoritative specification for: (a) 5 typed identifier wrappers replacing bare `str`, (b)
3 typed registries replacing the flat `dict[str, str]`, (c) elimination of 5 ambiguous key
formats, and (d) type-directed resolution dispatch. It is a docs-only deliverable — no
production code changes.

### Current State

- **Exists?** Yes — `27-typed-registry-refactor.md` is written and committed (240 lines).
- **Needs extraction/refactoring?** No. The document is complete.
- **Current test coverage**: N/A (design intent doc, not code).
- **IMPLEMENTATION_PLAN status**: Checkbox unchecked but Design Doc Amendments table says "Applied? Yes (TRR-1)".
- **All 7 downstream docs (TRR-2 through TRR-8)** have already been amended to reference doc 27
  and use its terminology. The amendments table confirms all 7 are applied.

### Design Consistency Check

- [x] All acceptance criteria from COMPONENT_CHECKLIST are testable (by document inspection)
- [x] AC are consistent with the requirements in the design intent doc (FR-1 through FR-6, NFR-1 through NFR-3)
- [x] No contradictions with other component specs
- [x] Input/output interfaces match what upstream/downstream components expect
- [x] Any ambiguities or gaps identified and resolved (documented below)

**Issues found during review:**

1. **NewType vs `.from_xxx()` constructors (minor doc gap).**
   Doc 27 says all types are `NewType` wrappers (NFR-1, zero runtime cost) but also
   specifies constructors like `ScopedKey.from_eqn()`, `CanonicalChannel.from_eqn()`, and
   `EQN.from_sysml_qn()`. Python's `NewType` creates a simple callable — you cannot add
   methods to it. The `.from_xxx()` notation is a documentation convenience for "there
   exists a validated factory function." The implementation will need either:
   (a) standalone factory functions (`make_scoped_key(eqn, attr) -> ScopedKey`), or
   (b) thin wrapper classes with `__slots__` (contradicts pure NewType but preserves NFR-1
   if properly benchmarked).

   **Resolution**: This is an implementation-time decision, not a design doc bug. Doc 27
   correctly specifies the intent (typed construction with validation). The exact Python
   pattern is deferred to the C08 implementation plan. No doc change needed.

2. **PQN and CanonicalChannel share the same string format.**
   Both use `__` separator and represent `{EQN}__{param}`. CanonicalChannel is specifically
   "PQN of an output" — a semantic distinction, not a format distinction. This is intentional:
   entry point QNs are PQNs, output channel names are CanonicalChannels. mypy distinguishes
   them even though the string format is identical.

   **Resolution**: No issue. The type distinction is the point of NewType — same format,
   different semantic meaning, caught by type checker.

3. **Step 1b (SysML QN normalization) is absent from doc 27's dispatch table.**
   The current production code has a Step 1b that converts `::` to dotted and retries in the
   scoped registry. Doc 27's REFERENCE path has Step 2 ("normalized scoped lookup") which
   serves the same purpose. Doc 11 (backtracker) also documents this as "Step 2: Normalized
   scoped lookup." The numbering is different but the behavior is consistent.

   **Resolution**: Consistent. Doc 27 and doc 11 agree on the behavior. The old Step 1b
   numbering is from the pre-TRR cascade; the new Step 2 numbering is from the typed
   dispatch. No conflict.

### Risks & Unknowns

None. The document is written, the spec is complete, and all downstream TRR steps (TRR-2
through TRR-8) have already been applied. The only remaining work is formal validation.

---

## 2. Spike

**Decision**: SKIP
**Rationale**: The Key_A fallback spike (`.project/research/20260217-060000_key-a-fallback-spike.md`)
already answers every question doc 27 is built on. The spike proved:
- Zero Key_A hits across 6 models
- 12 Step 1 hits are EXPOSE_PURE (10) + SysML QN (2), not Key_A
- 5 key formats are dead weight (Key_D, Key_E full, Key_F, bare, Key_A)
- REQ-BT-08 as written would break 12 correct resolutions

Doc 27 is the direct codification of these findings. No additional spike needed.

---

## 3. Test Plan

**Test file**: N/A — TRR-1 is a design document, not code.
**Validation method**: Document inspection against acceptance criteria.

### Validation Cases

Every requirement (FR-1 through FR-6, NFR-1 through NFR-3) and every AC from the
COMPONENT_CHECKLIST must be verified by inspecting the document content.

| AC | Requirement | Where in doc 27 | Verified? |
|----|-------------|-----------------|-----------|
| 5 typed identifiers defined | FR-1 | §Typed Identifier Types — table with all 5 types, formats, separators, examples, invariants | Yes |
| 3 typed registries defined | FR-2 | §Typed Registries — table with Scoped, SysML QN, Alias; API table with 6 methods | Yes |
| 5 eliminated keys with evidence | FR-3 | §Eliminated Keys — table with Key_A, Key_D, Key_E full, Key_F, bare; hit counts and reasons | Yes |
| Type-directed dispatch table | FR-4 | §Type-Directed Resolution Dispatch — CHAIN (4 steps) and REFERENCE (4 steps) paths | Yes |
| Constructor invariants | FR-5 | §Constructor Invariants — table with 5 types, from methods, validates, rejects columns | Yes |
| Uniqueness guarantee | FR-6 | §Uniqueness Guarantee — 3-row table: scoped=unique, SysML QN=unique, alias=first-wins | Yes |
| NewType zero cost | NFR-1 | §NFR Notes — code snippet, "zero runtime cost" explanation | Yes |
| mypy --strict | NFR-2 | §NFR Notes — "pass `mypy --strict` without `type: ignore`" | Yes |
| Incremental adoption | NFR-3 | §NFR Notes — 4-stage plan | Yes |
| Evidence citations | — | §Evidence Base — 7-row table citing spike research | Yes |
| Cross-references to 7 docs | — | §Cross-References — 7-row table: 03, 04, 09, 10, 11, 15, 24 | Yes |

### Cross-Consistency Checks

These verify doc 27 is consistent with the 7 amended downstream docs:

| Check | Doc | Finding |
|-------|-----|---------|
| Doc 09 uses all 5 NewType wrappers | 09-data-models.md | Yes — §Name Type Wrappers has all 5 with code snippet and field assignment table |
| Doc 09 OutputRegistry uses 3 typed dicts | 09-data-models.md | Yes — §Core Models describes `_scoped`, `_sysml_qn`, `_alias` dicts + `_canonical` set |
| Doc 10 REQ-OR-02 specifies typed lookups | 10-output-registry.md | Yes — "Each typed registry SHALL have its own exact-match lookup method" |
| Doc 10 REQ-OR-05 eliminates dead keys | 10-output-registry.md | Yes — Phase 1 tables have only Key_B, Key_C, Key_E_stripped, SysML QN |
| Doc 10 REQ-OR-08 eliminates Key_A entirely | 10-output-registry.md | Yes — "Key_A SHALL NOT be registered" |
| Doc 11 REQ-BT-08 uses type-directed dispatch | 11-analysis-backtracker.md | Yes — CHAIN/REFERENCE paths documented; no Key_A refs |
| Doc 11 no UnscopedResolutionError | 11-analysis-backtracker.md | Yes — grep confirms zero occurrences |
| Doc 15 REQ-NC-07 corrected | 15-naming-conventions.md | Yes — "SysML QN registry uses `SysMLQN` (`::` format) in its own typed registry" |
| Doc 15 no dead key rows | 15-naming-conventions.md | Yes — Phase 1 tables have only Key_B, Key_C, Key_E_stripped, SysML QN |
| Doc 04 strategies use typed registries | 04-input-resolver.md | Yes — Strategy A uses `scoped_lookup(ScopedKey)`, B uses `sysml_qn_lookup(SysMLQN)` |
| Doc 04 no Key_A refs | 04-input-resolver.md | Yes — Key_A not mentioned in strategies |
| Doc 24 REQ-DRA-03 typed registries | 24-dual-resolution-architecture.md | Yes — "No untyped `dict.get()`" |
| Doc 24 strategy table accurate | 24-dual-resolution-architecture.md | Yes — typed methods in overlap table |
| Doc 03 REQ-RES-07 uses ScopedKey/SysMLQN | 03-resolution-overview.md | Yes — Scope Problem section uses typed registries |
| Doc 03 no UnscopedResolutionError | 03-resolution-overview.md | Yes — not mentioned |

### Test Infrastructure Needed

None — validation is by document inspection.

### Gate: Ready for BUILD

N/A — there is no build phase. The document already exists. Proceed directly to VALIDATE.

---

## 4. Build Plan

### Files to Modify

None. The document `27-typed-registry-refactor.md` is already written and complete.
All 7 downstream docs (TRR-2 through TRR-8) have already been amended.

### Files to Create

None.

### Implementation Notes

TRR-1 is the only TRR step that creates a new document. The remaining 7 steps (TRR-2
through TRR-8) amend existing docs. All 8 steps have already been executed per the Design
Doc Amendments table in IMPLEMENTATION_PLAN.md. The work remaining is:

1. Formally validate doc 27 against all 9 C27 ACs (§3 above).
2. Run the validation criteria from IMPLEMENTATION_PLAN.md §Phase TRR (grep checks).
3. Update IMPLEMENTATION_PLAN.md: check the TRR-1 checkbox.
4. Update COMPONENT_CHECKLIST.md: check the C27 ACs.

### Gate: Ready for VALIDATE

- [x] Document exists with all required sections
- [x] All 7 downstream docs amended
- [x] No contradictions found in cross-consistency review

---

## 5. Validation

### C27 Acceptance Criteria

- [x] All 5 typed identifier types defined: SysMLQN, EQN, PQN, CanonicalChannel, ScopedKey
      — §Typed Identifier Types table (lines 30-37)
- [x] All 3 typed registries defined: Scoped, SysML QN, Alias
      — §Typed Registries table (lines 79-83) + API table (lines 86-94)
- [x] All 5 eliminated key formats documented with zero-hit evidence: Key_A, Key_D, Key_E full, Key_F, bare
      — §Eliminated Keys table (lines 107-113)
- [x] Type-directed dispatch table present: CHAIN -> scoped/alias, REFERENCE -> SysML QN/scoped
      — §Type-Directed Resolution Dispatch (lines 118-156)
- [x] Constructor invariants documented: ScopedKey rejects `::`, SysMLQN rejects `__`
      — §Constructor Invariants table (lines 56-62) + Typed Identifier Types table constructor invariant column
- [x] Uniqueness guarantee: scoped/SysML QN unique by construction, alias retains first-wins
      — §Uniqueness Guarantee table (lines 160-164)
- [x] NFR notes: NewType for zero runtime cost, mypy --strict, incremental adoption
      — §NFR Notes (lines 173-196)
- [x] Evidence base: citations from spike research
      — §Evidence Base table (lines 202-213) citing spike research file
- [x] Cross-references to all 7 amended docs (03, 04, 09, 10, 11, 15, 24)
      — §Cross-References table (lines 218-228)

### IMPLEMENTATION_PLAN Validation Criteria (Phase TRR)

The following grep-based validation criteria apply after ALL TRR steps. Since TRR-2
through TRR-8 are also applied, these can be checked now:

1. `grep -r "Key_A" *.md` → zero hits outside doc 27 rationale and `_intermediate_` files
2. `grep -r "dict\[str, str\]" *.md` → zero hits describing OutputRegistry
3. `grep -r "UnscopedResolutionError" *.md` → zero hits outside `_intermediate_` files
4. `grep -r "resolve()" *.md` → zero hits describing OutputRegistry single-method API
5. All REQ cross-references consistent between definition and citation docs
6. `ScopedKey`, `CanonicalChannel`, `SysMLQN` used consistently across docs 03, 04, 09, 10, 11, 15, 24, 27
7. No orphan requirement references

### Baseline Impact

None — this is a design intent document, not production code.

---

## 6. Learnings

### Findings

1. **The document and all downstream amendments are already complete.** The Design Doc
   Amendments table in IMPLEMENTATION_PLAN.md confirms all 8 TRR steps are applied.
   The unchecked TRR-1 checkbox is a bookkeeping gap, not a work gap.

2. **NewType `.from_xxx()` notation is a doc convention.** Python's NewType doesn't
   support methods. The constructors documented in doc 27 (e.g., `ScopedKey.from_eqn()`)
   will need to be implemented as standalone factory functions or thin classes at C08 time.
   This is an implementation detail, not a design inconsistency.

3. **PQN and CanonicalChannel are semantically distinct but format-identical.** This is
   correct and intentional — NewType distinguishes them for mypy even though the string
   format is the same.

### Design Doc Updates Needed

| Doc | What to update | Why |
|-----|---------------|-----|
| None | — | Doc 27 is complete as written |

### Cross-Component Impact

| Component | Impact | Action needed |
|-----------|--------|---------------|
| C08 (Output Registry) | Must implement typed registries per doc 27 spec | C08 plan references doc 27 |
| C11 (Backtracker) | Must implement type-directed dispatch per doc 27 FR-4 | C11 plan references doc 27 |
| C12 (Input Resolver) | Strategies must use typed registry methods per doc 27 | C12 plan references doc 27 |
| C01 (Data Models) | AC7-AC10 added for typed identifier wrappers | Already in COMPONENT_CHECKLIST |

### Deviations from Plan

None expected — the document is already written and validated.

---

## 7. Commit

**Branch**: `cost-pattern-refactor` (current branch)
**Commit convention**: One commit per TRR step or batch

- [x] All validation checks above are green
- [x] Grep-based validation criteria run (Phase 2 audit, 2026-02-17)
- [x] IMPLEMENTATION_PLAN.md: TRR-1 checkbox checked
- [x] COMPONENT_CHECKLIST.md: C27 ACs checked
- [x] Committed as part of Phase 2 batch commit (C08 + C09 + C10 + TRR + audit)
- [x] Committed successfully *(2026-02-17)*

---

## Progress Log

### Session: 2026-02-17 — Planning and validation
**Phase**: PLAN + VALIDATE (combined — document already exists)
**Work done**:
- Read all source documents: IMPLEMENTATION_PLAN, COMPONENT_CHECKLIST, component-loop template, spec, spike research
- Read doc 27 and all 7 amended downstream docs (03, 04, 09, 10, 11, 15, 24)
- Completed design consistency review: no contradictions, no gaps, all interfaces match
- Verified all 9 C27 ACs by document inspection
- Verified cross-consistency with all 7 amended docs
- Identified 1 minor doc convention (NewType vs .from_xxx()) — resolved as implementation-time decision
**Stopped at**: Plan complete. Ready for grep-based validation and checkbox updates.
**Next step**: Run grep validation criteria, update checkboxes in IMPLEMENTATION_PLAN and COMPONENT_CHECKLIST, commit.
**Blockers**: None
