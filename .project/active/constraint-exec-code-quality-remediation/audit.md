---
date: 2026-07-17
auditor: Codex
topic: "Independent audit of CONSTRAINT-EXEC code-quality remediation"
status: needs-work
branch: constraint-exec-epic
commit: c2967f0
---

# Independent Audit: CONSTRAINT-EXEC Code-Quality Remediation

**Verdict:** Needs Work
**Audited:** 2026-07-17
**Branch:** `constraint-exec-epic`
**Commit:** `c2967f0`

## Verdict

**Needs Work.** The four remediation commits are real and their focused tests pass. They close
most of the minimum merge bar from the 2026-07-13 research. They do not close the whole review,
and two defects violate completed feature contracts:

1. Lowering does not bind actuals through `ActualFact.formal_targets` or prove total formal
   coverage. A required formal with no actual and no modeled default is silently omitted.
2. The executable profile admits expressions that the predicate compiler rejects. Proven integer
   equality is the clearest case. Malformed or unary arithmetic shapes expose the same missing
   profile/compiler contract.

The new model validators also enforce only one direction of the eligibility invariant. Two further
quality defects were found at adjacent boundaries: occurrence ordering is nondeterministic when its
sort key ties, and package verification lets missing or malformed seals escape its result API.

All unresolved findings are filed in `.project/backlog/BACKLOG.md`. The existing
`[CONSTRAINT-ARCH-UNIFY]` and `[EXIT-PIN-SEAM]` rows remain valid.

## Audit Basis

There is no standalone remediation spec, design, or plan. This audit therefore uses:

- the minimum merge bar and recommendations in
  `.project/research/20260713-213722_constraint-exec-pr-code-quality.md`;
- the completed constraint-lowering contract, especially strict per-formal resolution at
  `.project/completed/20260713_constraint-lowering/spec.md:143-175`;
- the completed generation contract, especially profile-before-compiler behavior at
  `.project/completed/20260713_constraint-generation/spec.md:99-112`;
- the executable-profile contract and implementation from clean companion commit `9e24c93`.

The audited sysml-codegen commit is `c2967f0`. The sibling agentic-mbse worktree contains unrelated
in-progress changes, so cross-repo probes used a clean export of committed `9e24c93` at
`/tmp/agentic-mbse-head`.

## Research-Finding Closure

| Minimum merge-bar item | Result | Evidence |
|---|---|---|
| Impossible-state validators and rejection tests | **Partial** | Resolution-tag fields are enforced. Eligible constraints require predicate IR and an evaluation channel. Polarity and the reverse ineligible relationship remain unenforced. |
| Resolver conflict and precedence tests | **Met** | Six two-rung conflict cases pin the current ordered ladder in `tests/unit/test_constraint_resolver.py`. |
| Adversarial path tests | **Met as characterization** | Brackets, empty segments, and chain/source-name behavior are pinned. Invalid paths remain representable and belong to `[CONSTRAINT-ARCH-UNIFY]`. |
| Malformed arity and unary tests for both IR renderers | **Partial** | Both renderers reject unary `+` instead of changing its sign. Predicate arity and identifier guards are covered. The calc renderer's existing zero-operand guard still lacks a test, and profile/compiler shape parity is not enforced. |
| Explicit errors in place of load-bearing asserts | **Met** | Version, same-IR, capture, eligibility, and most-specific-type failures survive optimized Python. Remaining asserts examined are guarded narrowing assertions, not the only runtime check. |
| Owned architectural follow-up | **Met** | `[CONSTRAINT-ARCH-UNIFY]` explicitly covers typed paths, one resolver, one part index, shared live/offline phases, and graph assembly. `[EXIT-PIN-SEAM]` covers the dormant exit-selection branch. |

## Unresolved Findings

### P1: Formal binding and coverage do not implement the completed lowering contract

The completed spec defines one decision for every definition formal: match an actual through
`ActualFact.formal_targets`; otherwise use an explicitly omitted modeled default; otherwise raise a
generation error (`constraint-lowering/spec.md:150-164`).

Current lowering instead builds `actual_by_target` from `actual.name`
(`src/sysml_codegen/analysis/constraint_lowering.py:610-615`). It never reads
`ActualFact.formal_targets`, even though that field is the extracted formal identity. It then emits
inputs only for the actual-name dictionary and `usage.omitted_default_formals` (`:619-639`). It never
compares those bindings with the referenced definition's full formal set.

Two construction probes confirm the consequences:

- an admitted definition-typed constraint with a required, non-defaulted formal and no actual
  lowered successfully with `inputs=[]` instead of raising;
- an actual named `alias` whose `formal_targets` contains `Pkg::C::required` produced an input for
  `alias`, not for the targeted formal.

This can generate a predicate whose required argument is absent or misnamed. Filed as
`[CONSTRAINT-FORMAL-COVERAGE]`.

### P1: The executable profile is not a total contract for the compiler

The generation contract says the profile gate precedes compilation and the compiler consumes what
the profile admitted (`constraint-generation/spec.md:107-112`). The companion v1 profile admits
same-category Boolean, string, integer, and same-enumeration equality
(`agentic-mbse@9e24c93:src/agentic_mbse/sysml/executable_profile.py:179-213`). Its arithmetic walk
also admits every `+`, `-`, `*`, `/`, `**`, or `^` node without checking arity (`:347-377`).

The predicate compiler rejects every `==` and `!=`
(`src/sysml_codegen/generation/predicate_compiler.py:140-146`). It also rejects unary `+` and
zero-operand arithmetic (`:120-130`). Probes against the clean companion commit produced:

- profile `ADMIT` for integer equality, then `PredicateCompileError: equality blocked in profile v1`;
- profile `ADMIT` for unary `+` in operand position, then
  `PredicateCompileError: unsupported unary operator: '+'`.

Rejecting unary `+` fixed the silent sign inversion, but it did not make the upstream and downstream
contracts agree. The remedy needs an explicit operator-shape contract and a differential test that
every profile-admitted IR compiles. It also needs to implement the admitted equality categories or
change the profile contract deliberately. Filed as `[PROFILE-COMPILER-PARITY]`.

### P2: Eligibility invariants remain one-way

`ConcreteConstraint` now requires predicate IR and an evaluation channel when `eligible=True`, and
it derives `expected_value` from a non-null polarity
(`src/sysml_codegen/resolution/models.py:347-369`). It still accepts:

- `eligible=True`, `is_negated=None`, and `expected_value=None`;
- `eligible=False` with executable predicate/evaluation payload populated.

`ConstraintCatalogEntry` describes an eligible assertion but independently permits null predicate,
polarity, and expected value (`resolution/models.py:385-401`). Generation later uses
`bool(entry.is_negated)`, turning an invalid `None` polarity into `False`
(`src/sysml_codegen/generation/modules.py:119-127`). This is exactly the kind of defaulted guess the
lowering contract forbids at its boundary. Filed as `[CONSTRAINT-MODEL-INVARIANTS]`.

### P2: Occurrence ordering has an incomplete tie-breaker

`_occurrence_sort_key` returns only feature names and occurrence indices
(`src/sysml_codegen/analysis/part_instance_index.py:221-235`). It omits owning-definition identity
and the occurrence's own part-definition identity. Distinct occurrences can therefore compare equal.
They are collected in a set before sorting (`:309-313`), so equal-key order follows hash iteration.

A two-occurrence probe with identical segment names and indices but different owning definitions
returned `A, B` under hash seeds `1` and `42`, and `B, A` under seeds `2`, `3`, `4`, `5`, and `10`.
That violates the method's deterministic-order contract. Filed as `[PART-INDEX-TIEBREAK]`.

### P2: Package verification does not normalize its input boundary

`verify_package` advertises a `VerificationResult`, but reads and indexes the seal before validating
it (`src/sysml_codegen/contracts/verify.py:100-151`). A missing seal raises `FileNotFoundError`,
malformed JSON raises `JSONDecodeError`, and absent keys raise `KeyError`. The strict runtime check
also compares diagnostic strings with `is` rather than `==` (`:178-180`). This was already identified
in the source research (`constraint-exec-pr-code-quality.md:390-393`) but was neither remediated nor
previously backlogged. Filed as `[CONTRACT-VERIFY-BOUNDARY]`.

## Code-Integrity Assessment

- The remediation does not contain placeholders, empty implementations, catch-all exception
  suppression, or fixture rewrites.
- The explicit-error conversion was checked under `python -O`; the targeted optimized suite passed.
- The touched production files pass Ruff. The whole touched-test-file check reports five existing
  violations in `test_expression_compiler.py`; blame and the pre-remediation file show they predate
  these commits, so they are not filed as remediation defects.
- Complexity remains concentrated at the boundaries named in the research. The remediation also
  pushed `_compile_numeric` over Ruff's C901 threshold. That is included in the shared IR validation
  work rather than filed as a separate mechanical split.
- The four remediation commits do not change `tests/fixtures`.

## Validation Record

| Check | Result |
|---|---|
| Focused remediation tests: concrete models, resolver, calc renderer, predicate compiler | **113 passed** |
| Optimized-mode boundary tests: concrete model, constraint emission/lowering, graph extension, snapshot v3, occurrence round trip | **44 passed, 7 skipped** |
| Ruff on touched production files | **Passed** |
| Ruff complexity scan on the research hotspots | **16 findings**; architectural items remain open, including predicate `_compile_numeric` at C901 13 |
| Fixture diff across the four remediation commits | **Empty** |
| Full suite without a SysIDE license | **2071 passed, 197 skipped, 23 failed, 96 errors, 7 deselected**; failures/errors entered through missing-license setup, so this run cannot replace the recorded licensed result |
| Licensed full suite | **Not rerun**; `CURRENT_WORK.md` records the remediation-time result as 2364 passed / 23 skipped |
| Mypy baseline | **Not independently reproduced**; the clean companion export changes mypy's import-analysis surface, while the sibling editable worktree has unrelated changes |

## Backlog Disposition

- P1: `[CONSTRAINT-FORMAL-COVERAGE]`
- P1: `[PROFILE-COMPILER-PARITY]`
- P2: `[CONSTRAINT-MODEL-INVARIANTS]`
- P2: `[PART-INDEX-TIEBREAK]`
- P2: `[CONTRACT-VERIFY-BOUNDARY]`
- Existing P1: `[CONSTRAINT-ARCH-UNIFY]`, amended with the missing differential/edge
  characterization gates
- Existing P3: `[EXIT-PIN-SEAM]`

Certification remains blocked until the two P1 items are fixed and validated against the clean
companion profile contract. The P2 items are quality/correctness work that should remain visible even
if merge sequencing treats them separately.

## Certification

The focused remediation behavior, optimized-mode failures, production lint, fixture preservation,
and cited adversarial construction probes were checked. No completed spec or plan checkbox was
changed because the audit found contract gaps after those work items had been archived.

**Not checked:** a licensed full-suite run, live SysIDE corpus execution, generated-package runtime
execution, performance, and unrelated uncommitted agentic-mbse work. The historical licensed result
and mypy baseline were not treated as independently reproduced evidence.
