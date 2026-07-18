---
date: 2026-07-17
auditor: Codex (independent audit)
topic: constraint-exec-code-quality-remediation
status: needs-work
branch: constraint-exec-epic
commit: "036ec39 + uncommitted remediation"
dependency_baseline: agentic-mbse@82fef099901e219f1e75d784b80b79693727bdac
---

# Audit: CONSTRAINT-EXEC Code-Quality Remediation

## Verdict

**Needs Work.** The formal-target binding and total occurrence-ordering cures meet their
contracts. The implementation does not yet establish profile/compiler totality, generated-package
support for newly admitted value categories, lifetime model invariants, or the complete package
verification boundary. A committed inline-constraint fixture also exposes a generation failure
that the current “end-to-end” test does not reach.

This audit replaces the pre-remediation assessment for the current worktree. It does not change
the archived lowering or generation specifications; the conflict identified below requires an
explicit design decision before those contracts can be certified together.

## Audit Basis

This follow-on has no standalone specification or design. The owner approved the following source
set as its governing contract on 2026-07-17:

- `.project/active/constraint-exec-code-quality-remediation/plan.md`
- `.project/completed/20260713_constraint-lowering/spec.md`
- `.project/completed/20260713_constraint-lowering/design.md`
- `.project/completed/20260713_constraint-generation/spec.md`
- `.project/completed/20260713_constraint-generation/design.md`
- `.project/research/20260713-213722_constraint-exec-pr-code-quality.md`
- the public executable-profile v2 behavior at the pinned companion commit
  `agentic-mbse@82fef099901e219f1e75d784b80b79693727bdac`

The audit inspected the uncommitted diff from `036ec39`, traced the completed contracts into code,
ran focused tests in normal and optimized Python, and used direct construction and offline-fixture
probes where the existing tests did not exercise a claimed invariant.

## Finding Disposition

| Original finding | Result | Evidence |
|---|---|---|
| Formal target binding and coverage | **Met** | Definition formals are matched by exact target identity; foreign, duplicate, missing, and defaulted cases are covered. |
| Profile/compiler parity | **Not met** | Profile-admitted quantity ordering and arithmetic still fail compilation; new non-real equality coverage stops before generated modules. |
| Constraint model invariants | **Partly met** | Construction rejects the documented impossible shapes, but ordinary assignment recreates and serializes them. |
| Part-occurrence ordering | **Met** | The key includes segment, owning-definition, index, and leaf-definition identity; unequal occurrences do not tie. |
| Package verification boundary | **Partly met** | Seal load and broad schema failures are normalized, but semantic consistency, path containment, and artifact I/O are not. |

## Findings

### 1. Profile `ADMIT` is still not a total contract for predicate compilation — Important, P1

The pinned companion profile admits same-unit quantity ordering and arithmetic. The compiler accepts
only `real` and `integer` feature references in numeric positions, so the admitted predicate fails
after the profile boundary (`src/sysml_codegen/generation/predicate_compiler.py:151`). Direct probes
against the exact companion commit reproduced the mismatch for quantity feature references,
including `a <= b`, `length <= 2[m]`, unary `+length <= 2[m]`, and `length / length <= 2`.

The new differential test covers five representative literal-only cases and requires the compiled
argument list to be empty (`tests/conformance/test_constraint_lowering.py:303`). It therefore does
not test the feature-reference and generated-module surfaces where the incompatibility occurs.
There is also a derivation mismatch for exponentiation: the compiler classifies integer
exponentiation as integer for equality (`src/sysml_codegen/generation/predicate_compiler.py:176`),
while profile v2 derives it as real and blocks real equality.

**Required closure:** reconcile every profile-v2 admitted operator/category combination with the
compiler, including references and units, then replace representative parity cases with a
matrix-driven profile-`ADMIT` → compile → generated execution gate. The compiler must also reject
every profile-blocked shape.

### 2. Newly admitted non-real equality has no valid generated-package data path — Important, P1

The predicate compiler can compare Boolean, string, integer, and synthetic enum literals, but the
rest of generation remains float-only:

- modeled defaults are converted through `float(...)`
  (`src/sysml_codegen/analysis/constraint_lowering.py:882`);
- every graph input is declared as `float`
  (`src/sysml_codegen/analysis/constraint_lowering.py:950`);
- generated observations and run signatures coerce values to float
  (`src/sysml_codegen/generation/modules.py:184`);
- generated schemas declare float fields and `dict[str, float]` evidence
  (`src/sysml_codegen/templates/constraint_module.py.jinja2:15` and
  `src/sysml_codegen/templates/constraint_types.py.jinja2:13`).

This makes string and enum inputs unusable, changes Boolean evidence into `1.0`/`0.0`, and loses
large-integer precision. The enum regression uses a synthetic `LiteralNode`; production enum
members arrive as feature references and are collected as runtime arguments
(`src/sysml_codegen/generation/predicate_compiler.py:258`).

This exposes a premise conflict. The completed generation design fixes the input and evidence
shape around floats, while the pinned executable profile now admits equality over other semantic
categories. The audit cannot silently choose which contract wins.

**Required closure:** amend the generation contract/design to define typed inputs, defaults,
observations, and enum constants, or narrow profile admission before compilation. Park dependent
certification until the owner chooses that contract direction.

### 3. Inline owner-reference constraints lower but cannot generate — Important, P1

Inline predicates have no named formals or actuals, so lowering creates no module inputs
(`src/sysml_codegen/analysis/constraint_lowering.py:762`). The committed `constraint_inline`
snapshot nevertheless contains a predicate leaf named `value`. An offline build of that fixture
produces compiled arguments `['value']` and module inputs `[]`; rendering then raises the intended
leaf/input reconciliation error (`src/sysml_codegen/generation/modules.py:176`).

The lowering test explicitly blesses the empty input list
(`tests/conformance/test_constraint_lowering.py:111`). The test named “end to end” stops after graph
construction and never renders or executes the module
(`tests/conformance/test_constraint_pipeline_threading.py:105`). This misses the completed
lowering spec's inline-source success criterion and generation design's leaf/input reconciliation
requirement.

**Required closure:** define and implement how owner feature references in inline predicates become
module inputs, then make the committed offline fixture pass package rendering and execution.

### 4. Model invariants can be bypassed after construction — Important, P2

The new validators correctly reject impossible values during construction
(`src/sysml_codegen/resolution/models.py:345` and
`src/sysml_codegen/resolution/models.py:424`). The models are mutable and do not validate
assignment. A valid eligible `ConcreteConstraint` can therefore be changed to `eligible=False`
while retaining its predicate, inputs, expected value, and channel; `model_dump` serializes that
state. Catalog assembly and graph extension then silently filter the record out
(`src/sysml_codegen/generation/constraint_catalog.py:76` and
`src/sysml_codegen/analysis/constraint_lowering.py:946`). A catalog entry's polarity and expected
value can likewise be mutated out of agreement and serialized.

The added mutation regression covers a downstream `is_negated=None` guard only. It does not prove
that either model shape remains valid for its lifetime.

**Required closure:** make the models immutable or assignment-validating, or revalidate the full
nested shape at every serialization and consumption boundary. Add mutation tests for both
eligibility directions, polarity derivation, nested catalog serialization, silent filtering, and
fingerprint generation.

### 5. Package verification accepts self-inconsistent seals and paths outside the package — Important, P2

Seal validation checks broad JSON types but not semantic forms
(`src/sysml_codegen/contracts/verify.py:113`). A seal with an arbitrary
`executable_fingerprint` verifies successfully because verification never recomputes the declared
fingerprint from its recorded artifact hashes. Artifact keys are joined directly to the package
directory (`src/sysml_codegen/contracts/verify.py:179`), so `../outside` and absolute paths can
read and validate files outside the package root. This contradicts the package contract's
relative-path coverage and derived-fingerprint rules.

Recorded artifact reads are also unguarded (`src/sysml_codegen/contracts/verify.py:190`). An
unreadable artifact raises `PermissionError` instead of returning a `VerificationResult`, even
though the seal itself now has normalized I/O diagnostics.

**Required closure:** reject absolute, parent-traversing, and non-canonical artifact keys; validate
digest syntax; recompute and compare the executable fingerprint; and normalize artifact walk/read
errors into path-specific fatal diagnostics. Cover each case with stdlib-only tests.

## Conformance Assessment

### Plan

Phases 2 and 4 are complete. Phases 1, 3, and 5 implemented useful partial cures but do not meet
their stated goals. Phase 6's mechanical commands ran, but its three certification assertions are
not true under the probes above. The affected plan checkboxes are reopened.

### Lowering specification and design

Strict formal coverage, target-based binding, modeled-default handling, and stable occurrence
ordering conform. Inline owner-reference wiring does not. No archived checkbox is changed because
the completed artifact is historical and the current conflict belongs in this active remediation.

### Generation specification and design

The profile-before-compiler boundary is present, but the compiler does not consume all `ADMIT`
results. The generated input/evidence design does not represent the expanded non-real equality
domain. This is a contract conflict, not a local compiler-only defect.

### Code integrity

The changed production files contain no placeholder implementations, new broad exception
swallowing, dead compatibility shims, or new load-bearing assertions. Ruff, formatting, fixture
preservation, and diff checks are clean. The defects above are boundary and end-to-end coverage
gaps rather than draft-code artifacts.

## Independent Validation

| Check | Result |
|---|---|
| Changed remediation tests, normal mode | **174 passed, 5 skipped, 7 deselected** |
| Focused profile/lowering/compiler tests | **116 passed, 5 skipped** |
| Focused model/order/verifier tests | **47 passed** |
| Changed remediation tests, `python -O` | **173 passed, 5 skipped; 1 pre-existing assertion-dependent failure** |
| Companion profile core tests at exact `82fef09` | **90 passed** |
| Touched-file Ruff and format | **Passed** |
| `git diff --check` | **Passed** |
| Fixture diff and production placeholder scan | **Clean** |
| Targeted mypy | **Non-green; imported project surface remains above baseline** |

The audit did not reproduce the implementation report's exact 189-test combined command or
92-test companion command, but broader and overlapping focused selections were run. Direct probes
were necessary because all selected tests passed while the profile, inline-generation, mutation,
and verifier-boundary failures remained reproducible.

## Not Checked

- Licensed SysIDE/live-model legs and live-vs-snapshot parity.
- Paid or slow corpus cases.
- The complete 2,107-pass unlicensed suite was not rerun during this independent pass.
- Performance and resource-usage regressions.
- A project-wide mypy baseline; current targeted runs import a known non-green project surface.
- Unrelated untracked `.claude/projects/` content.

## Certification Record

- Verdict: **Needs Work**.
- Reopened incomplete checkboxes in the active plan only.
- Updated `.project/CURRENT_WORK.md` to point at this audit and its blockers.
- Updated the existing backlog findings with the narrower remaining work and added the newly
  exposed inline-wiring issue.
- Left archived spec, design, epic, and closure checkboxes unchanged.
