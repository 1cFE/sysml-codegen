# Implementation Plan: CONSTRAINT-EXEC Code-Quality Remediation Closure

**Status:** Needs Work — independent audit found unresolved boundary and end-to-end gaps  
**Created:** 2026-07-17  
**Last Updated:** 2026-07-17  
**Dependency Baseline:** `agentic-mbse@82fef099901e219f1e75d784b80b79693727bdac`

## Source Documents

This audit follow-on has no standalone spec or design. The owner approved this source set on
2026-07-17:

- **Remediation requirements:**
  `.project/active/constraint-exec-code-quality-remediation/audit.md`
- **Audit-closure design addendum:**
  `.project/active/constraint-exec-code-quality-remediation/design.md`
- **Cross-repo orientation:** `.project/reports/2026-07-17-1242-status-report.md`
- **Lowering contract and design:**
  `.project/completed/20260713_constraint-lowering/{spec,design}.md`
- **Generation contract and design:**
  `.project/completed/20260713_constraint-generation/{spec,design}.md`
- **Original review:**
  `.project/research/20260713-213722_constraint-exec-pr-code-quality.md`

The backlog rows remain `[AGENT]`; owner approval here authorizes execution but does not change
their provenance grade or make their implementation choices settled.

## Implementation Strategy

**Phasing rationale:** Close the cross-repo profile/compiler seam first because every lowering
test imports the companion contract. Then repair the four local findings independently. Finish
with a combined gate against the exact paired revisions.

**Critical path:** dependency/API compatibility → profile-ADMIT compiler totality → local cures →
combined certification evidence.

**First proof point:** Representative profile-v2 `ADMIT` predicates, including unary plus and
every admitted equality category, compile and execute with the expected three-valued result;
malformed facts remain blocked before compilation.

**Overall validation:** Each phase starts with failing tests, runs its focused tests immediately,
and records results below. Phase 6 reruns the combined gates.

### Audit-Closure Amendment — 2026-07-17

The owner instructed this session to execute the audit handoff, authorizing all independent phases.
The non-real generated-value phase remains parked at the explicit owner checkpoint in
`design.md#key-decisions`.

Critical path for reopened work:

1. Full profile-v2 `ADMIT`/`BLOCK` matrix at compiler and generated-execution boundaries.
2. Inline owner-reference lowering through committed-fixture rendering and execution.
3. Lifetime model invariants across mutation, serialization, filtering, and fingerprinting.
4. Seal digest/path/fingerprint semantics plus artifact I/O normalization.
5. Owner-approved non-real input/default/observation/evidence contract.

Every cure begins with a failing regression. Phases 2 and 4 below remain closed and are not
reworked without new contradictory evidence.

---

## Phase 1: Paired Profile-v2 and API Compatibility

### Goal

Make sysml-codegen compatible with the certified agentic-mbse v2 contract and prove that profile
admission is a total input contract for predicate generation.

### Assumption Under Test

Unary plus can preserve its operand value, and admitted Boolean/string/integer/same-enum equality
can use ordinary equality with unknown reserved for missing/non-finite numeric data. Malformed leaf
facts are rejected by profile preflight and never reach generation.

### Test Stencil

```python
decision = evaluate_profile(facts_for(predicate))
assert decision.eligibility is Eligibility.ADMIT
source, _args = compile_predicate(predicate, "compiled")
compiled = load(source)
assert compiled(**values).actual_value is expected
```

### Changes Required

- [x] Update `ConstraintFacts` test constructors for the non-init wire tag.
- [x] Add paired malformed-snapshot/preflight coverage.
- [x] Add differential profile-ADMIT → compile → execute cases for unary plus and admitted
      equality categories.
- [x] Repin `analysis/constraint_lowering.py` to reviewed profile v2 semantics.
- [x] Extend `generation/predicate_compiler.py` without admitting profile-blocked `!=` or real
      equality.
- [x] Add the missing calc-renderer zero-operand test and preserve explicit direct-API errors.

### Validation

- [x] Run focused profile/compiler/lowering/snapshot/emission tests.
- [x] Run Ruff on touched production and test files.

**What we know afterward:** Every representative v2-admitted predicate compiles and executes;
blocked/malformed shapes do not cross the profile boundary.

---

## Phase 2: Formal Target Binding and Total Coverage

### Goal

Restore the completed lowering contract: one decision for every definition formal, keyed by
`ActualFact.formal_targets` rather than the actual's local name.

### Assumption Under Test

Definition formals and actual targets carry enough qualified identity to reject zero, multiple,
duplicate, missing, and foreign bindings without changing the intentional modeled-default edge.

### Test Stencil

```python
facts = facts_with_formal("Pkg::C::required", actual_name="alias", targets=[target_qn])
lowered = lower_constraints(facts, ...)
assert lowered[0].inputs[0].formal_name == "required"
```

### Changes Required

- [x] Add renamed-actual, missing-required, zero/multiple-target, duplicate-target, foreign-target,
      and modeled-default tests in `tests/conformance/test_constraint_lowering.py`.
- [x] Build the definition-formal index and bind each formal through exactly one actual or an
      explicitly omitted modeled default in `analysis/constraint_lowering.py`.
- [x] Preserve `MODELED_DEFAULT.default_ir=None` as valid.

### Validation

- [x] Run constraint-lowering and graph-extension suites.
- [x] Run the relevant tests under optimized Python.

**What we know afterward:** Required formals cannot disappear or be renamed by an actual's local
label.

---

## Phase 3: Constraint Model Invariants

### Goal

Make executable and unassessed constraint shapes disjoint and remove generation-time coercion of
missing polarity.

### Assumption Under Test

Existing construction sites already know whether a record is executable; enforcing the full
relationship will expose bugs rather than require a compatibility fallback.

### Test Stencil

```python
with pytest.raises(ValidationError):
    ConcreteConstraint(eligible=True, is_negated=None, ...)
with pytest.raises(ValidationError):
    ConcreteConstraint(eligible=False, predicate_ir=serialized, ...)
```

### Changes Required

- [x] Add negative construction tests for both directions on `ConcreteConstraint` and
      `ConstraintCatalogEntry`.
- [x] Enforce executable payload + polarity for eligible records and absent executable payload for
      unassessed records in `resolution/models.py`.
- [x] Remove `bool(None)` coercion from `generation/modules.py` and fail loudly if an impossible
      catalog record bypasses validation.
- [x] Keep `membership_kind=None` valid where the profile permits it.

### Validation

- [x] Run concrete-model, catalog, module-emission, snapshot, and optimized-mode tests.

**What we know afterward:** Neither model shape can represent a half-executable constraint.

---

## Phase 4: Total Part-Occurrence Ordering

### Goal

Make occurrence ordering independent of set/hash iteration when structural segment/index keys tie.

### Assumption Under Test

Owning-definition identities at each step plus the leaf `part_def_qn` form a stable total key.

### Test Stencil

```python
outputs = [run_probe(seed) for seed in (1, 2, 3, 5, 10, 42)]
assert len(set(outputs)) == 1
assert outputs[0] == expected_cross_root_order
```

### Changes Required

- [x] Add equal-segment/different-root and different-leaf ordering regressions, including multiple
      `PYTHONHASHSEED` subprocesses.
- [x] Extend `_occurrence_sort_key` in `analysis/part_instance_index.py` to a total structural key.

### Validation

- [x] Run part-index unit, conformance, snapshot-round-trip, and optimized-mode tests.

**What we know afterward:** Distinct occurrences never compare equal and ordering is stable across
process hash seeds.

---

## Phase 5: Package Verification Boundary

### Goal

Return explicit verification diagnostics for unreadable or malformed seals and preserve the
canonical emitted verifier exactly.

### Assumption Under Test

Seal loading/schema validation can normalize boundary failures before the existing integrity walk
without weakening tamper, missing-artifact, extra-artifact, name, or runtime checks.

### Test Stencil

```python
result = verify_package(package_dir, "pkg")
assert not result.ok
assert [d.kind for d in result.diagnostics] == [expected_kind]
```

### Changes Required

- [x] Add missing-file, unreadable-file, invalid-JSON, wrong-root-type, and missing/wrong-key tests.
- [x] Define explicit seal-input diagnostic kinds and validate before indexing in
      `contracts/verify.py`.
- [x] Replace string identity with value equality for strict runtime mismatch.
- [x] Update the emitted-verifier fixture/oracle only through the canonical source mechanism and
      prove byte identity.

### Validation

- [x] Run contract/seal/verifier tests and canonical emitted-source identity gate.
- [x] Run stdlib-only import verification.

**What we know afterward:** Advertised verification failures stay inside `VerificationResult`.

---

## Phase 6: Combined Validation and Project Record

### Goal

Validate all five audit findings and paired v2 compatibility against the exact dependency commit.

### Changes Required

- [x] Run the combined focused suites.
- [x] Run targeted tests under `python -O`.
- [x] Run Ruff, formatting checks, targeted mypy, `git diff --check`, and placeholder scans.
- [x] Prove `tests/fixtures` unchanged unless an intentional canonical verifier artifact requires a
      documented update.
- [x] Run the normal/full suite if the environment supports it; label license-dependent evidence
      accurately.
- [x] Update this plan, `audit.md`, and `.project/CURRENT_WORK.md` with exact results and remaining
      unchecked gates.

### Validation

- [ ] All five findings have direct regression coverage.
- [ ] Paired profile/compiler compatibility passes against agentic-mbse `82fef09`.
- [ ] No unresolved failure is hidden by a carried historical result.

**What we know afterward:** The remediation is ready for an independent `$my-audit`; this plan does
not self-certify it.

---

## Phase 7: Inline Owner-Reference Inputs

### Goal

Make inline predicate leaves ordinary generated module inputs so the committed
`constraint_inline` offline fixture renders and executes.

### Assumption Under Test

Inline feature references resolve in the assertion owner's occurrence scope through the existing
strict resolver.

### Changes Required

- [x] Add a regression that reaches committed-fixture rendering and execution, not only graph
      construction.
- [x] Collect unique inline feature-reference leaves and resolve them into
      `ConcreteConstraintInput` records during lowering.
- [x] Replace the empty-input assertion in the existing conformance test with exact wiring checks.

### Validation

- [x] Run inline lowering, rendering, execution, snapshot, and optimized-mode tests.

## Phase 8: Lifetime Constraint-Model Invariants

### Goal

Keep `ConcreteConstraint` and `ConstraintCatalogEntry` valid after construction and at every nested
serialization/filtering/fingerprinting boundary.

### Changes Required

- [x] Add mutation regressions for both eligibility directions and polarity derivation.
- [x] Add nested catalog serialization, eligible filtering, and fingerprint regressions.
- [x] Enable transactional assignment validation and revalidate records at consuming boundaries.

### Validation

- [x] Run model, catalog, graph-extension, emission, snapshot, and optimized-mode tests.

## Phase 9: Verifier Semantic Boundary

### Goal

Reject malformed digests, hostile/non-canonical paths, and self-inconsistent executable
fingerprints without filesystem escape; return diagnostics for artifact walk/read failures.

### Changes Required

- [x] Add stdlib-only regressions for digest syntax, absolute/parent/non-canonical paths,
      fingerprint mismatch, recorded-artifact I/O, and package-walk I/O.
- [x] Validate seal semantics before artifact access and recompute the executable fingerprint.
- [x] Normalize artifact stat/read/walk failures into path-specific fatal diagnostics.
- [x] Preserve canonical emitted-verifier byte identity.

### Validation

- [x] Run verifier, contract, sealing, emitted-source identity, stdlib import, and optimized-mode
      tests.

## Phase 10: Numerical Executable Profile — Dedicated Pipeline Item

### Goal

Align executable admission with the generated package's numerical value model under the dedicated
requirements contract `.project/active/numerical-constraint-profile/spec.md`.

### Changes Required

- [x] Record the selected numerical-profile direction in `design.md` and a dedicated spec.
- [ ] Approve and design `.project/active/numerical-constraint-profile/spec.md`.
- [ ] Replace this placeholder with the approved cross-repository implementation plan.
- [ ] Implement and validate the approved contract, including warning-and-continue behavior for
      valid non-numerical assertions.

### Independent Audit Result — 2026-07-17

The independent audit returned **Needs Work**. Formal-target binding and occurrence ordering are
verified. The reopened work is:

- close the full profile-v2/compiler matrix, including quantity references and generated
  execution;
- resolve the float-only generated input/evidence design conflict for non-real equality;
- wire inline owner feature references into generated module inputs;
- preserve constraint-model invariants after construction; and
- validate seal fingerprints and artifact paths, and normalize artifact I/O failures.

See `audit.md` for probes, file references, and validation evidence.

---

## Risk Management

- **Equality unknown policy:** Preserve Kleene unknown for missing/non-finite numeric observations.
  Profile-admitted Boolean/string/enum equality compares finite semantic values directly; tests pin
  each category.
- **Dirty cross-repo state:** Baseline commits are now exact. Unrelated untracked paths remain out of
  scope and untouched.
- **Profile/compiler drift:** Differential tests use the installed companion's public profile and IR
  APIs instead of copying its admission matrix into production.
- **Licensed gate:** A missing SysIDE license is reported as unchecked, never converted to a pass.

## Implementation Notes

### Phase 1 Completion

**Completed:** 2026-07-17

**Changes Made:** Repinned profile v2; reconciled the non-init facts tag; compiled unary plus in
both IR renderers; added typed optional-fact guards; implemented admitted `==` for Boolean,
string, integer, and same-enum operands while keeping `!=`/real equality blocked; added paired
profile-ADMIT and malformed-preflight tests.

**Validation:** 111 passed, 5 skipped across the focused compiler, lowering, emission, regression,
and snapshot suites. Ruff passed on all touched production files and the clean touched-test scope.
`tests/unit/test_expression_compiler.py` retains its four documented pre-existing whole-file Ruff
findings; the imports changed here are clean.

**Issues:** The sandboxed uv cache is read-only, so uv-backed checks require the approved external
cache access. No semantic deviation from the approved phase.

### Phase 2 Completion

**Completed:** 2026-07-17

**Changes Made:** Definition-typed lowering now resolves the referenced definition, validates
formal identities, treats each actual's single `formal_targets` QN as authoritative, rejects
ambiguous/duplicate/foreign bindings, and makes exactly one actual-or-explicit-default decision in
definition order for every formal. The actual's local name is diagnostic-only.

**Validation:** 29 passed, 5 skipped in both normal and `python -O` runs across lowering, emission,
and Phase-4 regression tests. Ruff passed after wrapping the two new long lines.

**Issues:** Live fixture legs remain license-skipped; the same binding logic is exercised through
offline production-shaped facts and registry behavior.

### Phase 3 Completion

**Completed:** 2026-07-17

**Changes Made:** Made eligible and unassessed `ConcreteConstraint` payloads disjoint; required
known polarity for eligible records; made catalog executable fields non-null with derived
expectation validation; removed polarity coercion; added a fail-loud mutated-model guard before
predicate compilation. Unassessed records keep source polarity when known but carry no derived
expectation or executable payload. `membership_kind=None` remains legal.

**Validation:** 75 passed, 5 skipped in both normal and `python -O` model/catalog/generation/
lowering/snapshot runs. Ruff passed on the Phase 3 scope.

**Issues:** None.

### Phase 4 Completion

**Completed:** 2026-07-17

**Changes Made:** Extended the established segment/index ordering with owning-definition identities
and the leaf `part_def_qn` as total tie-breakers. Added direct unequal-key tests and a six-seed
subprocess regression that reproduced the pre-fix drift.

**Validation:** 10 passed, 13 license-skipped in both normal and `python -O` part-index/
round-trip runs. Ruff passed on production and test files.

**Issues:** License-dependent live index and occurrence round-trip legs remain skipped.

### Phase 5 Completion

**Completed:** 2026-07-17

**Changes Made:** Added fatal `SEAL_MISSING`, `SEAL_UNREADABLE`, and `SEAL_MALFORMED`
diagnostics; normalized UTF-8/JSON/schema failures before indexing; validated the stdlib seal shape;
and changed strict runtime diagnostic comparison to value equality. Schema-invalid JSON shares the
malformed kind; filesystem absence and other I/O failures remain distinct.

**Validation:** 30 verifier, contract-model, and Step-9 sealing tests passed. The generated verifier
was byte-identical to the canonical source, the verifier remained stdlib-only, and Ruff passed.

**Issues:** None.

### Phase 6 Completion

**Completed:** 2026-07-17

**Validation:** Combined sysml-codegen remediation suite: **189 passed, 18 skipped**. Optimized
remediation suite: **138 passed, 18 skipped**; the changed calc-renderer cases also passed
separately under optimized Python (**2 passed, 49 deselected**). Exact paired companion suite at
`agentic-mbse@82fef09`: **92 passed**. Touched-file Ruff and format checks, `git diff --check`, and
the production placeholder scan passed. `tests/fixtures` is unchanged.

The unlicensed full suite collected 2,430 tests and completed with **2,107 passed, 197 skipped,
7 deselected, 23 failed, and 96 errors**. The remaining failures and setup errors are the existing
license-dependent group. Two constraint-graph fixture failures exposed by the first full run were
corrected and their test file then passed (**8 passed**).

**Remaining non-green gates:** Project-wide mypy completed with **127 errors in 29 files**. This is
not comparable to the carried baseline because the configured import surface includes
`/tmp/agentic-mbse-head` and missing optional stubs. A pre-existing load-bearing assertion also
remains in calc compilability classification: the broad expression-compiler suite fails under
`python -O` at `test_unknown_in_results_raises_assertion`. It is outside these five audit findings
and is recorded here so the optimized-mode limitation is not hidden.

### Audit-Closure Independent Phases — 2026-07-17

**Profile/compiler:** Quantity feature references now participate in numeric compilation, while
integer exponentiation derives as real at the equality boundary. The paired matrix covers every
admitted arithmetic and ordering operator, non-real equality categories, quantity references,
units, connectives, and malformed preflight. The exact companion profile suite passed **113 tests**.

**Inline wiring:** Inline predicate leaves are collected in predicate order and resolved through
the existing strict owner-scope ladder. The committed offline snapshot now produces module input
`value`, renders successfully, and executed under the documented agentic-mbse/TEAx environment
with the expected satisfied verdict (**1 passed**).

**Lifetime invariants:** `ConcreteConstraint` and `ConstraintCatalogEntry` validate assignments
transactionally, so a rejected cross-field mutation leaves the previous valid value intact.
Catalog assembly revalidates each full record before eligibility filtering and fingerprinting.

**Verifier:** Seal loading now validates lowercase SHA-256 syntax and canonical package-relative
POSIX paths. Verification recomputes the executable fingerprint, rejects symlink escapes, and
returns fatal path-specific diagnostics for artifact resolve/stat/read and package-walk failures.

**Focused validation:** The combined independent-remediation selection passed **149 tests with 13
license skips** in both normal and optimized Python. Targeted mypy passed on all five touched
production files. Touched-file Ruff and format checks passed. The typed generated-value contract
remains the only owner-decision-dependent phase.

### Phase 7 Inherited-Inline Regression Correction — 2026-07-18

**R4 pre-existence proof:** The licensed inherited-constraint oracle was run with the numerical
profile Phase 3 lowering hunks reversed and agentic-mbse loaded from the pre-v3 companion commit
`82fef099901e219f1e75d784b80b79693727bdac`. It reproduced the same unresolved `reading`
failure. The defect therefore predates numerical-profile v3 and belongs to D2/Phase 7.

**Finding:** The production resolver was not mis-scoping the inherited leaf. A direct probe with
production-equivalent `extract_design_attributes(model)` resolved all nine concrete occurrences,
including subtype, retyped, multi-level, and fixed-multiplicity paths, to the modeled base
attribute `InstanceIndexProbe__ConstrainedLeaf__reading`. The regression test had passed
`design_attrs={}`, leaving the strict resolver no modeled source and making its failure correct.

**Cure:** Commit `096c29f` corrects the family regression. It supplies the production extraction
input and asserts the exact nine owner-instance paths and input resolution for every record. The
existing committed `constraint_inline` live/offline coverage remains the non-inherited pin. No
production resolver change was made because the family probe proved its behavior correct.

**Validation:** The inherited family and non-inherited live/offline pins passed **4 tests**. The
first licensed full-suite run over the remediation worktree passed **2433 tests, 23 skipped, 8
deselected**. The execution-only inline pin is not part of that default suite and still requires
the documented TEAx-capable environment; the plain codegen venv lacks `pandas`.
