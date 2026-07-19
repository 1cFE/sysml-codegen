# Design Review: Runtime Evaluation Contract — Exceptional Arithmetic and Predicate Naming

**Design:** `.project/active/gap-runtime-contract/design.md`
**Spec:** `.project/active/gap-runtime-contract/spec.md`
**Spec Review:** `.project/active/gap-runtime-contract/spec-review.md`
**Epic Item:** `.project/backlog/epic_gap_close.md`, GAP-CLOSE Item 1
**Review File:** `.project/active/gap-runtime-contract/design-review.md`
**Date:** 2026-07-18

---

## Fundamental Assessment

**Sound, with validation-contract revisions required.** Rejecting collisions through one exact
raw-key-to-emitted-name mapping is the right-sized design. Running that validator before output
mutation and again at the direct compilation boundary is justified: the first call preserves an
existing package, while the second protects library callers. No new class, module, allocation
scheme, or renderer interface is needed (`design.md:82-91,107-140,206-227`).

The F1 treatment is also correctly scoped. Generated arithmetic already uses Python `/` and `**`
before `_cmp` sees an operand (`src/sysml_codegen/generation/predicate_compiler.py:120-135,170-189`),
and the wrapper calls the predicate before constructing `ConstraintEvaluation`
(`src/sysml_codegen/templates/constraint_module.py.jinja2:32-44`). Characterization plus the
approved docstring clarification is honest sysml-codegen work. Evaluator normalization remains an
external TEAx P0 because only the serial executor holds both `module_key` and the escaping exception
(`../teax/packages/teax-simkit/simkit/core/pipeline_executor.py:181-197`), while both evaluators
currently normalize only the later top-level exception without module identity
(`../teax/packages/teax-simkit/simkit/evaluation/evaluator.py:112-123,185-199`).

The design should not proceed unchanged, however. Its proposed historical evidence cannot be run
literally at the pinned baseline because the new tests do not exist there. Its CLI preservation
assertion is weaker than the invariant it claims. Its two-worktree and two-generated-package gates
do not yet prevent source-selection or import-cache leakage. These are evidence-design defects, not
reasons to replace the core approach.

---

## Dimensional Review

### 1. Spec Compliance

**Assessment: Concerns**

The behavioral design matches the approved spec:

- Reject-on-collision is one of the spec's allowed F2 outcomes and preserves collision-free names
  and imports (`spec.md`, Success Criteria 7 and 10; `design.md:109-128`).
- F1 remains characterization of already-correct codegen behavior, with explicit non-closure until
  `[GAP-CLOSE-F1-TEAX-NORMALIZATION]` passes (`design.md:14-17,181-185,297-311,331-341`). This
  faithfully carries the resolution in `spec-review.md`, L2-1.
- The three verified collision classes remain separate regressions. The design does not narrow the
  spec back to the original hyphen probe (`design.md:158-166,284-295`).
- The route-parity and before/after axes remain separate, as required by the approved spec
  (`design.md:313-329`).

The evidence plan does not yet make the spec's pre-fix evidence criterion reproducible. The design
says to enter an isolated worktree at `6db321225a5c8568db0287b67ed1d04c03079cc2` and “run each new
collision test” and each new F1 characterization (`design.md:291-306`). Those test files and test
cases do not exist at that revision. A command against a clean baseline worktree will therefore
select nothing or fail during collection, which is an unrelated setup failure expressly forbidden
by the spec. The design must require either:

1. a recorded test-only patch applied unchanged to both revisions, with its hash and the fact that
   it contains no production changes; or
2. a durable standalone probe that imports the production code from the selected revision, with the
   probe content/hash and exact command recorded.

The F2 baseline must then fail for the intended reason (`DID NOT RAISE` plus the later-body overwrite
observation), while the same F1 overlay/probe must pass as characterization. This is a major gap in
D5, not an implementation detail.

Capture fidelity is otherwise good. The owner-originated F1 policy remains distinct from the
agent-grade collision policy and evidence controls. The design does not promote the F2
`[INFERRED]` requirement into an owner-settled item; it selects one permitted mechanism in D1. The
owner ruling, exact baseline revision, and three collision-class referents are all carried at their
original force.

**Recommendation:** Amend D5 and the validation sections with one reproducible historical-test
mechanism before planning.

### 2. Pattern Consistency

**Assessment: Pass**

The design follows established codebase patterns. The current output-path collision preflight runs
after live/snapshot context construction and before clearing or setup
(`src/sysml_codegen/cli/__init__.py:949-983`). The current predicate compiler already has a fail-loud
same-IR invariant at its compile-once seam
(`src/sysml_codegen/generation/constraint_catalog.py:146-180`). One validator reused at those two
boundaries is consistent with both patterns.

Keeping the mapping helper in the existing generation module is also proportionate. The production
mapping already lives inline there (`src/sysml_codegen/generation/modules.py:124-131`), and the CLI
already imports the predicate compiler/render helpers directly from that module
(`src/sysml_codegen/cli/__init__.py:340-362`). No new package-level export or naming subsystem is
needed.

### 3. Abstraction Quality

**Assessment: Pass**

The proposed abstractions earn their existence: one pure emitted-name function removes duplicate
normalization logic, and one pure validator makes timing independently testable. The design leaves
the compile map and renderer contract intact (`design.md:206-210,270-275`). Removing either helper
would force the CLI and compiler seam to duplicate the lossy mapping or collision grouping.

The validator should accept the smallest useful input, such as distinct raw definition keys or a
catalog projected immediately to those keys. It should not become a general naming registry. The
current design stays within that boundary.

### 4. Duplication Avoidance

**Assessment: Pass**

Calling one validator twice duplicates enforcement, not logic. That duplication is intentional and
protects two different entry surfaces. The design explicitly rejects independent normalization at
the two call sites (`design.md:116-121,258-263`).

### 5. Data Structure Clarity

**Assessment: Pass**

The data flow is explicit: distinct raw definition keys are grouped by their final emitted function
name, identical raw keys are deduplicated, groups and keys are sorted, and the first complete
collision group is reported (`design.md:122-128,142-166,168-179`). This preserves the catalog's
compile-once identity, which is exactly `usage_qualified_name`
(`src/sysml_codegen/generation/constraint_catalog.py:46-54`).

The diagnostic contains the emitted name and every raw key in the selected group. Because each
required regression isolates one collision class, it deterministically names both raw keys for
case-lowering, underscore-run collapse, and quoted hyphen.

### 6. Route Safety

**Assessment: Concerns**

The production placement is correct. Today `compile_shared_predicates` is called during module
generation, after output clearing/setup, `primitives.py`, and schemas
(`src/sysml_codegen/cli/__init__.py:977-997` and `:349-362`). Moving the first check beside the
existing preflights makes both live and snapshot routes reject before package mutation. The direct
compile-seam recheck occurs before `compile_predicate`, protecting non-CLI callers
(`src/sysml_codegen/generation/modules.py:117-131`).

The proposed CLI test proves too little. A surviving sentinel (`design.md:194-195,215-216,290`) can
show that overwrite clearing did not remove that file, but it does not prove that no new directory,
file, or changed byte appeared beside it. The design's invariant is stronger: “before overwrite
clearing or any output write.” The test must snapshot the complete target tree before generation and
assert that the relative path set and every file byte are identical afterward. It should use
`overwrite=True` so the most destructive route is exercised. An additional empty/nonexistent-target
case should assert that rejection does not create the output root at all.

**Recommendation:** Strengthen I4's gate from sentinel survival to complete before/after tree
identity, plus no output-root creation when the target did not exist.

### 7. Bets & Decisions Integrity

**Assessment: Concerns**

B2 is a genuine, load-bearing bet: every definition rendered into the shared module must come from
the catalog being validated (`design.md:99-101`). The present production flow supports it because
`compile_shared_predicates` iterates `catalog.concrete_entries` and the renderer consumes only that
map (`src/sysml_codegen/generation/modules.py:117-153`).

B1 and B3 are not bets about uncertain reality. B1 is the policy choice already made in D1; B3 is
the owner-settled F1 rule. Duplicating them as bets blurs what evidence could falsify versus what a
decision controls. Keep D1 and state B3 as a governing requirement/invariant. Leave B2 as the real
bet.

Two hidden bets need to be surfaced:

- **Historical source selection:** an isolated worktree command will execute that worktree's source.
  This is false if the environment still resolves the main editable install. The evidence must
  record the imported `sysml_codegen.__file__` or use an explicit worktree-local install/Python path,
  and hash the identical model/snapshot input used at both revisions.
- **Two-route execution isolation:** executing live- and snapshot-generated packages with the same
  package name in one Python process can reuse `sys.modules` entries from the first package. That
  can make the second route's finite/non-finite assertions test the first route again. Run each
  generated package in a separate subprocess, or define complete module-cache eviction.

**Recommendation:** Add these as explicit validation assumptions with gates. Remove B1/B3 from the
bet register or relabel them as decision/owner requirement.

### 8. Reader Comprehension

**Assessment: Pass**

The design leads with the mental model: emitted predicate names form a finite namespace that must be
unique before output mutation (`design.md:82-91`). The exact mapping, validation flow, F1 boundary,
and external dependency are each stated before implementation details. A reader can follow the
system without decoding coined labels.

One wording correction is needed but does not block comprehension. “The same exception object
class/message leaves the wrapper” (`design.md:302-304`) reads as though object identity is required.
The approved sysml-codegen contract requires unchanged class and message; causal object retention is
the external TEAx contract. Say “the same exception class and message leave the wrapper unchanged”
unless object identity is intentionally added and a capture mechanism is specified.

---

## Exact Correctness Findings

### Normalization equivalence

**Verified.** The design's five-step contract is equivalent to production. Production emits
`constraint_pred_` plus `sanitize_qualified_name(key).lower()`
(`src/sysml_codegen/generation/modules.py:124-131`). `sanitize_qualified_name` splits on `::`, applies
`sanitize_name` once per segment, and joins with `__`
(`../agentic-mbse/src/agentic_mbse/sysml/qualified_names.py:83-90`). `sanitize_name` strips end quote
characters, replaces spaces and non-ASCII identifier characters, collapses underscore runs, strips
edge underscores, repairs empty/digit-leading segments, and avoids keywords (`:20-37`).

The stated pairs therefore converge exactly:

| Class | Raw keys | Emitted name |
|---|---|---|
| Case-lowering | `Pkg::Foo`, `Pkg::foo` | `constraint_pred_pkg__foo` |
| Underscore-run | `Pkg::foo__bar`, `Pkg::foo_bar` | `constraint_pred_pkg__foo_bar` |
| Quoted hyphen | `Pkg::'Foo-Bar'`, `Pkg::Foo_Bar` | `constraint_pred_pkg__foo_bar` |

The implementation must call this canonical helper from the compile loop as well as the validator;
tests should assert the helper output for all three pairs so later sanitizer drift cannot split
validation from emission.

### Detection before writes

**Design placement verified; test strength insufficient.** The proposed preflight location is before
the first package mutation on both routes. The direct-call invariant is also before predicate
compilation. Revise the preservation test as described in Dimension 6 so evidence matches I4.

### Deterministic diagnostics

**Verified.** Sorting emitted groups and raw keys before choosing the complete first group makes the
message permutation-independent and names both keys for each isolated required class
(`design.md:122-128,187-197,284-290`). Exact-message assertions should include `repr` escaping.

### Collision-free bytes

**Mechanism verified; gate needs execution isolation.** Refactoring the existing expression into a
helper does not alter insertion order, compile-map shape, function source, or wrapper imports
(`src/sysml_codegen/generation/modules.py:117-153,174-205`). The only direct generated-source change
should be the approved one-line wrapper docstring. Package contracts/seals may change transitively
because they hash changed wrapper bytes, exactly as the approved spec permits. The before/after gate
must reject any other file difference and must prove each worktree executed its own source.

### F1 characterization and dependency

**Verified.** The design does not pretend to fix codegen arithmetic. It pins the existing raw Python
raise and acknowledges that the current template is already substantively narrow
(`design.md:62-80,129-140,297-311`). Generated constraint module keys are
`constraint_id.lower()` (`src/sysml_codegen/analysis/constraint_lowering.py:1105-1121`) and become
the pipeline instance name unchanged (`src/sysml_codegen/generation/pipeline.py:122-149`). Attaching
that identity to the exception remains TEAx work. The evidence and handoff must continue to say F1
is open until the external P0 passes.

### RED and byte-gate feasibility

**Feasible after revision.** Public-boundary F2 tests can be overlaid onto the old revision and fail
with `DID NOT RAISE`, while an execution probe demonstrates the shared name and later-body overwrite.
F1 tests on the same overlay should pass at the old revision and stay outside the RED table. Existing
full-tree comparison code is suitable (`tests/conformance/test_snapshot_generation.py:33-43`), and
the live/snapshot matrix already includes constraint-bearing fixtures such as `plant_values`
(`tests/conformance/test_snapshot_generation.py:179-221`). The design should name the selected
fixture and assert before running the expensive gates that its two generated trees contain the
shared predicates module and at least one constraint wrapper. Execute each generated package in an
isolated subprocess for finite/non-finite behavior.

---

## Issues by Severity

### Critical

- None.

### Major

- **M1 — Historical tests are not reproducible as written.** New tests cannot be run directly from a
  clean pre-fix worktree. Require a hashed test-only overlay or durable standalone probe, and prove
  the selected revision's production source was imported. — Spec Compliance; Bets & Decisions
- **M2 — The pre-write gate does not prove the no-partial-artifact invariant.** Sentinel survival is
  weaker than full target-tree identity and no output-root creation. — Route Safety
- **M3 — Route and two-revision gates can be falsely green through environment leakage.** Name and
  shape-check the constraint-bearing fixture, force each worktree to execute its own source, hash the
  common input, and isolate live/snapshot package execution in separate processes. — Route Safety;
  Bets & Decisions

### Minor

- **m1 — The bet register duplicates decisions and settled policy.** B1 belongs only in D1; B3 is an
  owner requirement/invariant. B2 is the genuine reality claim. — Bets & Decisions Integrity
- **m2 — Exception wording implies object identity.** Require unchanged class/message at the codegen
  boundary unless identity is deliberately specified and testable. — Reader Comprehension

---

## Recommendations

1. Define one reproducible baseline-evidence mechanism: a hashed test-only overlay applied unchanged
   to baseline and post-fix worktrees, or a hashed standalone probe. Record the imported source path,
   revision, command, environment, input hash, and defect-specific result.
2. Replace the CLI sentinel assertion with complete output-tree identity under `overwrite=True`, and
   add a no-target-created assertion for a previously absent output path.
3. Name the route/byte fixture, assert it emits shared predicates and wrappers, run generated-package
   behavior in isolated subprocesses, and prove each isolated worktree uses its own code.
4. Keep the exact canonical mapping and deterministic complete-group diagnostic unchanged.
5. Retain the external TEAx P0 as unresolved and do not label sysml-codegen characterization as F1
   closure or RED evidence.
6. Clean up the bet register and exception-identity wording before handing the design to planning.

---

## Resolutions

*Recorded by the design agent, 2026-07-18. These dispositions accept the review's validation
findings without changing their agent provenance. No owner-originated requirement or decision was
added.*

- **M1 — Resolved.** D5 and Validation Approach now require one durable, hashed test-only overlay
  copied unchanged into detached baseline and candidate worktrees. The overlay uses only production
  seams available at the pinned revision. Appendix A gives exact commands and expected results:
  each baseline F2 node exits 1 with `DID NOT RAISE CodeGenerationError`; the old later-body impact
  probe passes; the unchanged F1 group passes as characterization. Collection/import failures are
  explicitly invalid evidence.
- **M2 — Resolved.** I4 and the no-partial-artifact validation now cover the real `run_codegen` API
  with `overwrite=True` in two states. An absent target must remain absent. A pre-populated nested
  tree must retain the exact relative path set, path kinds, symlink targets, and every regular-file
  byte. Sentinel-only evidence was removed.
- **M3 — Resolved.** Historical and candidate commands use detached `/tmp` worktrees, a shared
  hashed fixture copy, an allowlisted production patch, explicit worktree-first `PYTHONPATH`,
  disabled user-site and bytecode writes, and fresh interpreter processes. The overlay asserts the
  imported codegen paths and revision before behavior. Live- and snapshot-generated packages run in
  separate subprocesses whose hashed runner asserts both generated-package and codegen source paths,
  preventing editable-install and `sys.modules` contamination.
- **m1 — Resolved.** The bet register now contains only the load-bearing catalog-completeness claim.
  Reject-on-collision remains D1. Python's native value/raise boundary remains the owner-governed F1
  requirement and I7, not a falsifiable bet.
- **m2 — Resolved.** F1 wrapper wording now requires the same exception class and message to leave
  unchanged. It does not require Python object identity; causal object retention remains part of the
  external TEAx contract.

## Re-Review: 2026-07-18

**Scope:** Narrow check of the revised design against M1–M3 and m1–m2, plus confirmation that the
patch did not weaken the accepted collision or F1 decisions.

**Result:** The five findings are resolved. The historical evidence is now runnable at the pinned
revision because the test-only overlay is a saved input rather than assumed baseline content. Source
selection and candidate identity are asserted inside fresh processes. The pre-write test now proves
the complete no-mutation claim for absent and populated targets. Route behavior cannot reuse a
same-named package from another route. Reject-on-collision, pre-write detection, deterministic
complete-group diagnostics, all three collision classes, codegen-only F1 characterization, and the
external TEAx P0 remain unchanged.

**New blocking issues introduced:** None found.

---

**Overall:** Approve
**Next Steps:** Proceed to `my-plan`. The plan must preserve the hashed-overlay protocol, both
full-tree no-write cases, source-path/revision assertions, and fresh-process route execution.
