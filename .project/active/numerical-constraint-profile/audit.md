# Audit: Numerical Constraint Executable Profile

**Verdict:** Certify
**Audited:** 2026-07-18
**Branch:** constraint-exec-epic
**Commit:** aaa579e (codegen working tree, uncommitted item changes); companion agentic-mbse v3 at `05cde35`

---

## Summary

The item delivers the three-way outcome rule as specified: v3-admitted numerical claims compile
and execute, malformed numerical claims halt generation naming the fix, and non-numerical
statements warn in both tools, are cataloged, and never block. I reran the load-bearing gates in
both repos rather than trusting the plan's claims — the constraint-focused codegen suite (73 +
62 + 28 tests) and the companion profile/consumer suite (119 + 11 tests) are green, the
eligible⇔exclusion invariant is unrepresentable under construction probes, and the frozen golden
is untouched. The parent-remediation booking for the mid-implementation licensed-suite failure is
genuine and honestly recorded (it was a test defect, not a resolver defect). No blocking findings.

## Findings

### Plan completion

All five phases verified against code, not just their Implementation Notes.

- **Phase 1 (profile v3 core, companion):** `PROFILE_SEMANTIC_VERSION = "executable-profile/v3"`
  (`executable_profile.py:55`); `Eligibility.NON_NUMERICAL` (`:98`); force axis on the diagnostic
  (`:111`); containment computed in the single walk with `xor`/`implies` recursion (`:606-620`)
  and force-folding (`:731-735`). The v3 answer-key tests pass (`test_executable_profile_v3.py`,
  5 tests + matrix).
- **Phase 2 (L4/L6, companion):** L6 malformed→ERROR and non-numerical→one-WARNING-per-statement,
  L4 executable-share includes non_numerical — tests present and green
  (`test_item12_checks.py:122,133`; `test_level4_reconciliation.py:55`). Exact companion commit
  `05cde35` exists.
- **Phase 3 (codegen re-pin):** v3 pin + RuntimeError guard (`constraint_lowering.py:747-751`);
  halt rendering appends `diag.message` (`:763`); compiler defensively rejects `==`/`!=`
  (`predicate_compiler.py:163-167,173-174`).
- **Phase 4 (exclusion payload + catalog):** `ConstraintExclusion` tagged payload + eligible⇔
  exclusion validator (`models.py:311-318,376-413`); `excluded_records` projection sorted by
  `constraint_id` (`constraint_catalog.py:121-131`); all three routes totalized in `_exclusion_for`
  (`constraint_lowering.py:479-491`).
- **Phase 5 (end-to-end + gates):** one warning per NON_NUMERICAL usage (`constraint_lowering.py:
  779-786`); the two new fixtures exist; live/snapshot parity compares full graph and catalog
  values (`test_constraint_non_numerical.py:64-72`).

### Spec conformance

- **SC 1 (totality: admitted compiles/executes; equality never reaches compiler):** Verified.
  `tests/execution/test_constraint_execution.py` passes end-to-end (admitted assertion executes,
  satisfied/violated verdicts, margins). Equality is structurally barred from ADMIT (every `==`/`!=`
  appends a diagnostic in `_walk_comparison`, so it can never reach the zero-diagnostic ADMIT path),
  and the compiler rejects it defensively as a second gate (`predicate_compiler.py:163`).
- **SC 2 (admitted matrix):** Verified. Profile matrix + arithmetic suites green
  (`test_executable_profile_matrix.py`, `test_executable_profile_arithmetic.py`).
- **SC 3 (split equality outcomes):** Verified in code and answer key. `classify_equality`
  (`executable_profile.py:197-226`) routes boolean/string/enum → `warn_non_numerical_equality`
  (warn), real/quantity → `block_real_equality_requires_tolerance`, integer →
  `block_integer_equality_unpreservable`; both error messages name the two-inequality-band /
  float-path rewrite (`:495-504`). `!=` follows the same bucketing (`:492,621`).
- **SC 4 (one source-specific warning per non-numerical statement in BOTH tools, codegen
  continues):** Verified. Codegen: one `logger.warning` per NON_NUMERICAL usage with identity +
  location + reasons (`constraint_lowering.py:779-786`); the fixture test asserts exactly one
  warning naming statement + `model.sysml:` line + reason. agentic-mbse: L6 emits
  `L6_CONSTRAINT_NON_NUMERICAL` WARNING per statement (`test_item12_checks.py:133-158`).
- **SC 5 (catalog excluded_records + eligible⇔exclusion validator):** Verified by construction
  probe (see Code integrity) and catalog projection code. Excluded records carry kind + ordered
  reasons + location.
- **SC 6 (distinguishable failure vs out-of-scope):** Verified. BLOCK (error force, halts) vs
  NON_NUMERICAL (warn) vs UNASSESSED vs unsupported-owner are distinct outcomes/exclusion kinds.
- **SC 7 (admitted fixtures retain verdicts + live/snapshot parity):** Verified. Snapshot parity
  and migration-mapping suites green; the parity test compares full `computation_graph` and
  `constraint_catalog` `model_dump` values (I5, value-level not just counts).
- **SC 8 (version boundary + exact companion):** Verified. Both repos pin
  `executable-profile/v3`; codegen has a runtime RuntimeError guard on any other version; companion
  commit `05cde35` exists and is recorded in the plan's Phase-2/5 notes per D3(c).

Non-goals respected: no typing of the generated data path, no tolerance semantics invented, no
non-numerical execution, no concept-shape source-record rework.

### Design conformance

Implementation follows the design.

- **D1/D2/D9:** Fourth `NON_NUMERICAL` value; containment via error-dominates-warn in the single
  walk; `xor`/`implies` recurse; `!=` walks operands and buckets like `==`. Traced `(x>0) and flag`
  → BLOCK, `(x>0) xor (y>0)` → BLOCK, `flag xor other` → NON_NUMERICAL through the walk;
  matches D2's stated consequences.
- **D3/I6 (single gate):** One behavior pin in shared `lower_constraints`; loader keeps only its
  schema pins. Runtime v3 assert present and verified.
- **D5:** Halt rendering appends the actionable message; malformed fixture test pins the rewrite
  guidance text (M1 resolution landed).
- **D6/M5:** One tagged validated exclusion payload; catalog projects it; unsupported-owner route
  totalized (M5 resolution landed).
- **D8:** Frozen `golden.json` is git-clean — v3 answer key lives in tests.
- **D10/M6:** `_render_location` fallback to `<no location>`; locations render when present.

### Code integrity

No slop or failure-honesty issues found in the item's production changes.

- **Construction probes (eligible⇔exclusion invariant, SC 5 / I2):** eligible=True + exclusion →
  rejected; eligible=False + no exclusion → rejected; clearing exclusion by assignment on an
  ineligible record → rejected (validate_assignment). The contradictory record is unrepresentable.
- The `_exclusion_for` helper (`constraint_lowering.py:479-491`) is a clean total projection over
  the three causes, not a policy-in-utility smell — the dispatch is exhaustive and the reason
  ordering follows walk order deterministically.
- No broad `except Exception`, no back-compat shim, no silent invariant fallback introduced.
  `collect_bare_actual_demand`'s `except (NonFiniteCardinalityError, CodeGenerationError): continue`
  is pre-existing and correctly scoped (read-only probe; the real failure re-raises in
  `lower_constraints`).
- Placeholder scan clean (the single "placeholder" grep hit is a docstring naming Item 5's design
  scheme, not placeholder code).

---

## Certification

Independently reran and verified in this pass:

- Codegen constraint suite: `test_constraint_lowering.py`, `test_constraint_non_numerical.py`,
  `test_concrete_constraint_model.py` (73 passed); `test_constraint_execution.py`,
  `test_snapshot_constraint_parity.py`, `test_constraint_migration_mapping.py`,
  `test_snapshot_v3_gate.py`, `test_predicate_compiler.py` (62 passed);
  `test_constraint_graph_extension.py`, `test_constraint_emission.py`,
  `test_constraint_pipeline_threading.py` (28 passed). License loaded via the documented env.
- Companion suite: profile v3 + matrix + arithmetic + hygiene (119 passed); L4/L6 v3 consumer
  tests (11 passed).
- Construction probes for the eligible⇔exclusion invariant (3/3).
- Runtime version-pin guard presence; both repos agree on `executable-profile/v3`.
- Frozen `golden.json` clean; sample_model snapshot diff is timestamp + retired `dropped_constraints`
  field only (non-constraint fixture, not a v3 flip); two new fixtures present.
- Parent-remediation booking: cure commit `096c29f` (test correction) reproduced green; R4
  pre-existence ledger entry is genuine and honestly attributes the fix to the parent item.

**Not checked (recorded by the implementer, not independently reproduced here):**

- The full licensed sysml-codegen suite (plan claims 2450 passed) and the full companion suite at
  the `05cde35` archive (plan claims 1491 passed). I ran the constraint/profile/validation subsets,
  not the whole corpora.
- mypy, ruff/format, and `python -O` runs (plan claims all pass) — not rerun.
- The R4 pre-existence proof itself (reversing Phase-3 hunks against the pre-v3 companion at
  `82fef09`) — I verified the cure test passes at HEAD and that the ledger records the proof, but
  did not re-execute the reversal experiment.
- Broad corpus byte-identity beyond the tracked git status (I inspected the one tracked fixture
  diff; I did not regenerate the full corpus to confirm no untracked drift).
- The uncommitted state: the item's changes are unstaged in the working tree; this audit certifies
  the working-tree code, not a committed revision.
