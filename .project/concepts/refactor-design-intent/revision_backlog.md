# Revision Backlog: Design Intent vs Research Learnings

**Date**: 2026-02-17
**Source**: Cross-reference of [research/20260217-030000_mistakes-and-learnings-since-a6310a4b.md](../../research/20260217-030000_mistakes-and-learnings-since-a6310a4b.md) against design intent docs 00-26, COMPONENT_CHECKLIST.md, and IMPLEMENTATION_PLAN.md.
**Purpose**: Identify gaps where research lessons are documented but not structurally prevented in the refactored design.

---

## Status Legend

- `OPEN` — not yet addressed
- `IN PROGRESS` — partially addressed
- `DONE` — resolved

---

## RB-01: No CanonicalName type in data models (DONE 2026-02-17)

**Priority**: Critical
**Research lesson**: L1 — "Define a canonical name type and use it everywhere"
**Bug prevention**: Eliminates 8 of 19 bugs (42%) — Bugs 2, 6, 9, 11, 12, 13, 16, 19
[Research 1.L1, p.36-41; 2.Category A, p.132-144; 4.Smell 1, p.200-206]

**Gap**: The research's highest-impact recommendation was to introduce a typed wrapper so the type checker catches name-format mismatches at compile time. Doc 15 thoroughly documents 5+ name formats and their conventions (REQ-NC-01 through REQ-NC-07). Doc 09 defines all name fields as plain `str`. The *conventions* are clear, but there is no *type-level enforcement*. A downstream implementer can still pass a SysML QN (`Package::Element`) where an EQN (`Package__Element`) is expected — mypy won't catch it.

The research explicitly states: *"Introduce a `CanonicalName` type. Raw SysML names convert at the extraction boundary. All downstream indexes, lookups, and registrations use only canonical form."* [Research 1.L1, p.40-41]

**Affected docs**: 09-data-models.md, 15-naming-conventions.md
**Affected components**: C01 (Data Models), C02 (Naming Conventions)

**Recommended action**: Add `NewType` wrappers to Doc 09 / C01:

```python
from typing import NewType
SysMLQN = NewType('SysMLQN', str)        # "Package::Element"
EQN = NewType('EQN', str)                # "Package__Element"
PQN = NewType('PQN', str)                # "EQN__param"
RegistryKey = NewType('RegistryKey', str) # dotted format, no "::"
```

Update field types: `CalculationDefinitionData.qualified_name` -> `SysMLQN`, `CalcUsageData.qualified_name` -> `EQN`, `ModuleOutput.channel_name` -> `PQN`, `OutputRegistry._index` keys -> `RegistryKey`. Add REQ-DM-08 requiring typed name fields. Update Doc 15 to reference the types.

**Effort**: Medium (data model changes propagate to tests)

---

## RB-02: No shared dispatch_ast_node() function (OPEN)

**Priority**: Critical
**Research lesson**: L6 — "AST type dispatch must be ordered by specificity, enforced structurally"
**Bug prevention**: Eliminates 3 of 19 bugs (16%) — Bugs 8, 10, 18; plus 28 misclassified aggregation terms
[Research 1.L6, p.81-88; 2.Category C, p.161-169]

**Gap**: Doc 19 documents the FCE-before-OE invariant with 7 requirements, an audit of all 8 dispatch sites, and a concrete before/after example. But enforcement relies on comments at each site and grep-based audits (REQ-AST-02: *"Every dispatch site checking both FCE and OE SHALL include a comment"*).

The research explicitly recommended structural prevention: *"Extract a shared `dispatch_ast_node()` with mandatory type-priority ordering. No if/elif chains on `is_instance()` at individual call sites."* [Research 1.L6, p.87-88]

The current design has 8+ independent dispatch sites (Doc 19, lines 62-97) that must independently maintain correct ordering. A new dispatch site added by a future contributor has no structural guard — only a convention.

**Affected docs**: 19-ast-dispatch-invariant.md
**Affected components**: C07 (AST Dispatch Invariant)

**Recommended action**: Add a `dispatch_ast_node()` specification to Doc 19:

```python
def dispatch_ast_node(
    node: Any,
    handlers: dict[str, Callable[[Any], T]],
) -> T | None:
    """Dispatch in canonical order: FCE, OE, FRE, IE, Literal.
    Ordering is hardcoded here — callers cannot override it."""
```

All 8 sites refactor to call this shared function. Add REQ-AST-08: *"All dispatch sites SHALL use `dispatch_ast_node()`, not inline `is_instance()` chains."* Add as a C07 acceptance criterion and Phase 1.7 deliverable.

**Effort**: Low (specification only; implementation is a small extraction)

---

## RB-03: Strategy B retained despite 100% failure rate (DONE 2026-02-17)

**Priority**: Medium
**Research lesson**: L10 — "Kill dead code paths identified by probes"
**Empirical finding**: #5 — "SYSML_QN normalization fails 100% of exercised cases"
[Research 1.L10, p.121-126; 3.Assumption #3, p.190; 5.Finding #5, p.247]

**Gap**: The research found that `::` -> `__` string replacement normalization fails 100% of exercised cases across all tested models and recommended: *"If a spike proves code can't execute, remove it immediately. Don't keep 'defensive' code for hypothetical scenarios."* [Research 1.L10, p.125-126]

Yet the design retains this as an active resolution strategy:
- Doc 24: "Stage 1b: SysML QN normalization" in the backtracker cascade (line 64)
- Doc 24: "Strategy B: SysmlQnNormalization" in AGG_STRATEGIES (line 106)
- Doc 04: Strategy B listed in the ordered chain (REQ-IR-05)

No rationale is documented for keeping a strategy with a proven 0% success rate.

**Affected docs**: 04-input-resolver.md, 24-dual-resolution-architecture.md
**Affected components**: C11 (DependencyBacktracker), C12 (Input Resolver)

**Recommended action**: Either (a) add an explicit note to Docs 04 and 24 explaining why Strategy B is retained despite 0% success rate (e.g., known future model patterns that would exercise it), or (b) mark Strategy B for removal and add it to the Phase 7.4 dead code removal checklist. The current state contradicts L10 without explanation.

**Effort**: Low

---

## RB-04: Empirical findings lack a permanent home (DONE 2026-02-17)

**Priority**: Medium
**Research lesson**: All of Section 5 — "Empirical Data Points That Must Not Be Forgotten"
[Research 5, p.239-254]

**Gap**: The research cataloged 12 hard-won empirical findings from spikes and labeled them *"findings that the refactored design must preserve."* Some are anchored in design docs:

| Finding | Anchored in |
|---------|-------------|
| #2 Key_C is load-bearing | Doc 15, Section 7 |
| #10 FCE is subtype of OE | Doc 19, Section 1 |
| #11 segments[-2] for REFERENCE | Doc 11 |
| #7 :>> creates ReferenceUsage | Doc 25 |

Others have no anchor in the design:

| Finding | Not anchored |
|---------|-------------|
| #1 Zero bare-name references (94 bindings, 3 models) | No doc says "skip bare-name handling" |
| #5 SYSML_QN normalization fails 100% | See RB-03; contradicted by design |
| #8 cached_upper_bound is N+1 (exclusive) | Only in research |
| #9 24% of CHAIN RHS values are string literals | Only in research |
| #4 Virtual CalcUsage outputs consumed only through aggregation | Only in research |
| #6 instance_path includes design prefix as first segment | Implicit in Doc 15 Key_C derivation |
| #12 EXPOSE_PURE on PartDefs must be filtered | Implicit in Doc 16 but not a stated requirement |

**Affected docs**: STRATEGY.md or new file
**Affected components**: Cross-cutting

**Recommended action**: Add a "Design Invariants from Empirical Data" section to STRATEGY.md (or a standalone `INVARIANTS.md`). For each of the 12 findings: state the invariant, cite the spike that proved it, and cross-reference the design doc that enforces it (or flag as unanchored). This ensures institutional memory survives across sessions.

**Effort**: Low

---

## RB-05: Phase 7 structural refactoring underspecified (DONE 2026-02-17)

**Priority**: Medium
**Research lesson**: Section 6 — "Hotspot Files"
[Research 6, p.258-271; 4.Smell 2, p.209-214; 4.Smell 4, p.227-230]

**Gap**: Phase 7 of the implementation plan contains the actual structural changes that address the research's architecture smells (god module decomposition, orchestration extraction, naming consolidation, dead code removal). But each item is a single bullet with "Run full test suite" as the only acceptance criterion.

The research identifies these as the *highest-priority* refactor targets — 5 files modified 7-10 times each, with 27% rework rate [Research 6, p.272]. The god module `graph_builder.py` alone has 1282 lines, 13 functions, and 3 module construction paths [Research 4.Smell 4, p.227-229].

**Affected docs**: IMPLEMENTATION_PLAN.md
**Affected components**: Phase 7 items

**Recommended action**: Expand Phase 7 items with explicit acceptance criteria:

- **7.1** (orchestration extraction): AC should specify which functions move, verify `generation/initialization.py` drops below a target line count, verify no circular imports between `orchestration/` and `generation/`.
- **7.3** (naming consolidation): AC should verify single import path for all naming functions, no duplicate `identifier_types` modules.
- **7.4** (dead code removal): Enumerate the research-identified dead paths as an explicit checklist:
  - [ ] Bare-name handling in `resolve()` [Research 5.#1]
  - [ ] SYSML_QN normalization [Research 5.#5]
  - [ ] Virtual binding rewrite for bare names [Research 5.#1]
  - [ ] Step 3.6 alias enrichment heuristic [Research 1.L10, p.123]
  - [ ] Bare-name registration keys [Research 1.L10, p.124]

**Effort**: Low

---

## RB-06: Open issues not tracked in implementation plan (DONE 2026-02-17)

**Priority**: Medium
**Research lesson**: Section 7 — "Open Issues Carried Forward"
[Research 7, p.277-289]

**Gap**: The research lists 8 open issues. The implementation plan does not reference them. Some are clearly out-of-scope, but the decision is implicit — a future implementer won't know whether they were intentionally deferred or overlooked.

| # | Issue | In-scope? |
|---|-------|-----------|
| 1 | 16 of 20 aggregation impls produce invalid Python (`.()` syntax) | Partially — relates to C04 expression compiler |
| 2 | EXPOSE_COMPUTED pattern deferred | Out of scope (acknowledged in Doc 16) |
| 3 | agentic-mbse V2 validation rejects valid FORMULA patterns | Out of scope (upstream) |
| 4 | 28+ ADR references point to nonexistent documents | In scope (documentation) |
| 5 | Two BindingInfo classes un-consolidated | In scope — research "should-have" #12 |
| 6 | Three expression reconstruction implementations | In scope — research "should-have" #11 |
| 7 | Deeply-nested cross-scope REFERENCE resolution | Out of scope (not observed) |
| 8 | `sum()` is the only recognized aggregation function | Out of scope (feature request) |

**Affected docs**: IMPLEMENTATION_PLAN.md

**Recommended action**: Add a "Deferred Issues" section to IMPLEMENTATION_PLAN.md listing all 8 with explicit in-scope/deferred classification. For issues #5 and #6, decide whether to add components (e.g., a Phase 7 consolidation item) or defer with documented rationale. For issue #1, note the relationship to C04 and whether the conformance tests should cover this.

**Effort**: Low

---

## RB-07: PartDef vs PartUsage distinction not type-enforced (OPEN)

**Priority**: Low
**Research lesson**: L7 — "Distinguish PartDef-level from PartUsage-level processing at every stage"
[Research 1.L7, p.91-98; 3.Assumption #8, p.195]

**Gap**: The research says: *"Every extraction and registration function must explicitly handle or filter PartDef-level data. The type system should make this distinction visible."* [Research 1.L7, p.97-98]

The design handles this narratively: Doc 13 REQ-AS-08 warns on zero instances, Doc 16 restricts EXPOSE_PURE to PartUsage-level, Doc 25 documents template detection. But the data models use plain `str` for both PartDef-scoped names and instance-scoped names. The bug pattern (registering PartDef-level attributes in instance-scoped indexes) was made *independently three times* [Research 1.L7, p.94-96] — narrative rules didn't prevent it.

**Affected docs**: 09-data-models.md
**Affected components**: C01 (Data Models)

**Recommended action**: If RB-01 is adopted, extend the `NewType` approach:

```python
PartDefQN = NewType('PartDefQN', str)      # template-scoped
InstanceEQN = NewType('InstanceEQN', str)  # instance-scoped
```

Apply to `AggregationExpressionData.owning_part_qn` (PartDefQN), `ScopedAggregationData.instance_path` (InstanceEQN), `RedefinitionData.owning_part_qn` (PartDefQN). This makes the scope distinction visible at type-check time.

**Effort**: Medium (same propagation cost as RB-01; can be done together)

---

## Summary

| ID | Title | Priority | Lesson | Bugs Prevented | Effort | Status |
|----|-------|----------|--------|----------------|--------|--------|
| RB-01 | CanonicalName type wrappers | Critical | L1 | 8 (42%) | Medium | **DONE** |
| RB-02 | Shared dispatch_ast_node() | Critical | L6 | 3 (16%) + 28 misclassified | Low | OPEN |
| RB-03 | Strategy B retention rationale | Medium | L10 | Dead code clarity | Low | **DONE** |
| RB-04 | Empirical invariants permanent home | Medium | All | Institutional memory | Low | **DONE** |
| RB-05 | Phase 7 acceptance criteria | Medium | L3, L10 | Refactor safety | Low | **DONE** |
| RB-06 | Open issues tracking | Medium | Sec 7 | Scope clarity | Low | **DONE** |
| RB-07 | PartDef vs PartUsage types | Low | L7 | 3+ design issues | Medium | OPEN |

### Already well-addressed by design (no action needed)

These research lessons are structurally covered and require no revision:

- **L2** (spike-before-design): Implementation plan Phase 0 + "no mocks" ground rule
- **L3** (single module factory): REQ-MF-01 pure data transformer for all 3 types; X01 tracks type mapping consolidation
- **L4** (late-binding entry points): Factories return `(PipelineModule, dict[str, EntryPoint])`; param_groups rebuilt after all modules [Research 1.L4, p.62-69]
- **L5** (OutputRegistry for all resolution): Docs 10, 24 thoroughly address this [Research 1.L5, p.72-78]
- **L8** (test with real model outputs): Ground Rule #1 "no mock testing" [Research 1.L8, p.103-109]
- **L9** (self-contained design): 27 docs, 169 requirements, 18 quality-pass sessions [Research 1.L9, p.111-118]
