# Design: Runtime Evaluation Contract — Exceptional Arithmetic and Predicate Naming

**Status:** Implemented — sysml-codegen leg; external TEAx P0 open
**Owner:** Reid W
**Created:** 2026-07-18 13:38 PDT
**Branch:** `constraint-exec-epic`
**Commit:** `6db321225a5c8568db0287b67ed1d04c03079cc2`
**Epic:** GAP-CLOSE — Item 1

---

## Overview

This item makes generated predicate naming fail safely when distinct SysML definition keys would
become one Python function. It also pins sysml-codegen's existing exceptional-arithmetic boundary
with characterization tests and narrows one generated docstring. End-to-end F1 normalization
remains blocked on the separate P0 TEAx dependency `[GAP-CLOSE-F1-TEAX-NORMALIZATION]`.

## Related Artifacts

- Approved-after-revision spec: `.project/active/gap-runtime-contract/spec.md`
- Spec review: `.project/active/gap-runtime-contract/spec-review.md`
- Epic Item 1: `.project/backlog/epic_gap_close.md`
- Gap review: `.project/research/20260718-123558_constraint-expression-final-gap-review.md`
- Independent verification and owner F1 ruling:
  `.project/research/20260718_gap-review-verification.md`
- Runtime principle: `.project/concepts/constraint-execution-and-design-space-studies-claude.md`,
  Design Principle 4
- Numerical profile contract:
  `.project/active/numerical-constraint-profile/{spec,design}.md`
- Constraint generation architecture:
  `docs/architecture/reference/{08-generation,15-naming-conventions,28-constraint-lowering-and-catalog}.md`
- External dependency record: `.project/backlog/BACKLOG.md:41`
- TEAx interface references:
  `../teax/packages/teax-simkit/simkit/evaluation/{failure,evaluator}.py`,
  `../teax/packages/teax-simkit/simkit/core/pipeline_executor.py`, and
  `../teax/docs/evaluation-and-study.md`

## Research Findings

- The compile-once identity is the raw `usage_qualified_name`. Repeated concrete occurrences of
  one raw definition key intentionally share one function
  (`src/sysml_codegen/generation/constraint_catalog.py:46`). Uniqueness must therefore be checked
  over distinct definition keys, not catalog rows.
- The emitted name is currently derived inline as `constraint_pred_` plus the per-segment-sanitized
  key, lowercased (`src/sysml_codegen/generation/modules.py:100`). All functions then enter one
  Python module (`src/sysml_codegen/generation/modules.py:135` and
  `src/sysml_codegen/templates/constraint_predicates.py.jinja2:7`). A repeated `def` name makes
  Python keep the later body while both wrappers import that same name.
- The existing sanitizer is deliberately lossy. It strips surrounding quotes, replaces spaces and
  non-alphanumeric characters, collapses underscore runs, fixes empty/digit/keyword segments, joins
  qualified-name segments with `__`, and is not re-entrant
  (`../agentic-mbse/src/agentic_mbse/sysml/qualified_names.py:20` and `:83`). Codegen then case-folds
  the complete result.
- The CLI already rejects output-path normalization collisions before clearing an overwrite target
  (`src/sysml_codegen/cli/__init__.py:194` and `:968`). Predicate collisions need the same
  preservation property. Checking only during module generation would happen after directories,
  primitives, and schemas were written (`src/sysml_codegen/cli/__init__.py:977`).
- The adjacent same-IR guard is a generation-time, fail-loud invariant at the compile-once seam
  (`src/sysml_codegen/generation/constraint_catalog.py:146`). The predicate-name guard belongs next
  to it, but must also be callable from the earlier CLI preflight.
- Generated arithmetic is already plain Python and is evaluated before `_cmp` sees its operands
  (`src/sysml_codegen/generation/predicate_compiler.py:120` and `:170`). `_cmp` handles an
  already-produced non-finite value but cannot and should not intercept an arithmetic exception
  (`src/sysml_codegen/generation/predicate_compiler.py:59`). The wrapper directly calls the predicate
  before constructing `ConstraintEvaluation`
  (`src/sysml_codegen/templates/constraint_module.py.jinja2:32`).
- Existing tests cover Kleene values, connective propagation, and finite division, but not
  exceptional intermediate arithmetic (`tests/unit/test_predicate_compiler.py:116` and `:217`). The
  real-package lane already proves finite and non-finite execution behavior
  (`tests/execution/test_constraint_execution.py:53` and `:388`).
- Both TEAx evaluators catch only the executor's top-level exception and omit module identity
  (`../teax/packages/teax-simkit/simkit/evaluation/evaluator.py:112` and `:185`). The first seam
  holding both the error and module key is TEAx's serial executor
  (`../teax/packages/teax-simkit/simkit/core/pipeline_executor.py:181`). Sysml-codegen cannot fill
  `EvaluationFailure.module_or_channel` without crossing the repository boundary.
- The current template already says that a verdict against the assertion does not raise
  (`src/sysml_codegen/templates/constraint_module.py.jinja2:1`). This conflicts with the gap
  review's description of a blanket “never raises” promise. The implementation is therefore a
  wording-only clarification, not a correction of generated exception behavior or a pre-fix RED.

## Core Concept

Treat emitted predicate names as a finite output namespace that must be proven unique before any
output is changed. One pure derivation function defines the raw-key-to-function-name mapping. One
pure validator groups distinct raw keys by that result and rejects any non-injective group with a
deterministic diagnostic. The CLI runs the validator before clearing output, and the predicate
compiler runs it again as a library-boundary invariant. No successful collision-free generation
changes names. F1 stays even smaller: tests describe the boundary that already exists, and the
template states that only an adverse verdict is non-raising. TEAx later owns attachment of module
identity and evaluator normalization.

## Key Bets

- **B1. The catalog contains every definition key that can be emitted into the shared predicates
  module.** Predicate rendering consumes this same catalog and map. *If false → an unvalidated
  function can enter the module through another path and collision safety is incomplete.*

## Key Decisions

- **D1. Reject normalized predicate-name collisions.** This is the smallest mechanism that prevents
  silent wrong execution and preserves every collision-free function name, wrapper import, and
  generated baseline. It follows the existing fail-fast output-path policy
  (`docs/architecture/reference/15-naming-conventions.md:18`). *Rejected: suffix every key with a
  stable hash (unnecessary churn to every predicate and derived seal); suffix only colliding keys
  (adds allocation and set-sensitive renaming rules, and changes a previously stable name when a
  colliding definition is added).*
- **D2. Centralize exact name derivation, then validate it twice.** A small helper in the existing
  generation module produces the emitted name. A pure uniqueness guard uses it. The CLI calls the
  guard before output clearing, and `compile_shared_predicates` calls it before any predicate is
  compiled. *Rejected: validate only in the compile loop (can partially regenerate the target and
  can compile earlier entries before discovering the collision); validate only in the CLI (direct
  callers bypass it).*
- **D3. Diagnose the complete first collision group deterministically.** Group distinct raw keys by
  emitted name. Sort groups by emitted name and keys by Python string order. If collisions exist,
  raise `CodeGenerationError` for the first sorted group, naming the emitted function and every raw
  key with `repr`-style escaping. The diagnostic form is:
  `Predicate function-name collision: raw definition keys <sorted keys> all normalize to
  '<emitted name>'. Rename one; generation cannot emit them safely.` *Rejected: report the first
  catalog traversal pair (order-sensitive); silently choose a winner (the defect).*
- **D4. F1 changes tests and prose, not generated arithmetic.** Compiler-level characterization
  covers the three direct raising operations and one supported-connective nesting. A generated
  wrapper boundary test proves the original exception class and message leave `run()` unchanged
  before evidence exists. The template wording becomes “A verdict against the assertion does not
  itself raise (INV-3).”
  *Rejected: arithmetic guards or exception-to-indeterminate conversion (contradicts the owner
  ruling); labeling already-green sysml-codegen tests as RED (false evidence).*
- **D5. Carry one hashed test-only overlay unchanged across isolated revisions.** Implementation
  saves `.project/active/gap-runtime-contract/evidence/test_gap_runtime_contract_overlay.py`. It
  imports only public production seams and contains the three F2 rejection tests, the old
  later-definition overwrite probe, both no-write generation-API tests, F1 characterization, and
  source-selection assertions. The file is copied byte-for-byte into detached baseline and
  candidate worktrees; its SHA-256 is recorded before either run. Production changes are carried
  separately as a hashed, allowlisted patch into the candidate worktree. Every pytest invocation
  starts a fresh interpreter, forces the selected
  worktree's `src` to the front of `PYTHONPATH`, disables the user site and bytecode writes, and
  asserts `sysml_codegen.__file__`, the generation module's source file, and `git rev-parse HEAD`
  before behavior. `.project/active/gap-runtime-contract/evidence.md` records commands, hashes,
  expected/actual results, source paths, input hashes, route parity, and before/after byte diffs.
  *Rejected: running tests that do not exist at the baseline; using the main editable install or
  one long-lived interpreter; stashing, checking out, or resetting the current worktree; relying on
  chat or an aggregate suite result.*

## Exact Collision Contract

For a raw definition key `raw_key`, the emitted function name is exactly:

1. Split `raw_key` on `::`.
2. For each segment, apply the existing `sanitize_name` sequence: strip surrounding single/double
   quotes; replace spaces with `_`; replace each non-ASCII-alphanumeric/non-underscore character
   with `_`; collapse one or more underscores to one; strip edge underscores; substitute `unnamed`
   if empty; prefix `n_` if the first character is a digit; suffix `_` for a Python keyword.
3. Join sanitized segments with `__`.
4. Apply Python `str.lower()` to the joined name.
5. Prefix `constraint_pred_`.

The validator compares these final emitted strings. It deduplicates identical raw keys first so
compile-once sharing remains valid. The required regression pairs and expected names are:

| Class | Raw keys | Final emitted name |
|---|---|---|
| Case-fold | `Pkg::Foo`, `Pkg::foo` | `constraint_pred_pkg__foo` |
| Underscore-run | `Pkg::foo__bar`, `Pkg::foo_bar` | `constraint_pred_pkg__foo_bar` |
| Quoted hyphen | `Pkg::'Foo-Bar'`, `Pkg::Foo_Bar` | `constraint_pred_pkg__foo_bar` |

Each pair uses opposite predicates. At pre-fix revision the test must show that both keys receive
the same function name and the later definition governs both imports. Post-fix, generation stops
before either definition is emitted.

## Architecture

The graph's catalog remains the only input. The validation flow is:

`ConstraintCatalog` → distinct raw definition keys → existing normalization → grouped emitted
names → either `CodeGenerationError` or the unchanged compile/render path.

The CLI places this flow beside its existing output-path and parameter-coverage preflights, before
`_clear_output_directory`. Successful generation later reaches `compile_shared_predicates`, which
reasserts the same invariant and then runs the existing same-IR and compilation work. Both live and
snapshot routes converge on the same `PipelineContext` before this preflight
(`src/sysml_codegen/cli/__init__.py:949`), so the policy cannot drift by route.

F1's data flow is unchanged: generated wrapper → generated predicate → Python arithmetic. A false
predicate returns a `ConstraintEvaluation`; a non-finite numeric value reaches `_cmp` and may return
`indeterminate`; an arithmetic raise leaves predicate and wrapper unchanged. No evaluation object
or report can be constructed on that path. The external TEAx item must attach the module key at its
serial-executor seam and let both evaluators produce the exact normalized failure in the spec.

## Required Invariants

- **I1.** Two distinct raw definition keys in one generated package never map to one emitted
  predicate function.
- **I2.** Repeated catalog entries with one identical raw definition key still compile once.
- **I3.** Collision diagnostics are identical for any permutation of the same catalog entries and
  name every raw key in the selected collision group.
- **I4.** A collision detected through the real `run_codegen` generation API with `overwrite=True`
  occurs before overwrite clearing or any output write. If the target is absent, it remains absent.
  If pre-populated, its complete relative path set, path kinds, symlink targets, and every regular
  file byte remain identical.
- **I5.** Direct callers of `compile_shared_predicates` receive the same rejection before any call
  to the predicate compiler.
- **I6.** Collision-free raw keys retain their exact pre-fix function names and wrapper imports.
- **I7.** Generated division and power retain Python's native value/raise behavior. No generated
  catch, wrapper, guard, fallback, or exception-to-verdict conversion is added.
- **I8.** A raised operation produces no `ConstraintEvaluation`, report, or partial evidence in
  sysml-codegen's wrapper boundary.
- **I9.** This item does not claim evaluator-level F1 closure. GAP-CLOSE F1 closes only when this
  item and `[GAP-CLOSE-F1-TEAX-NORMALIZATION]` both pass.
- **I10.** Historical, route, and byte evidence proves source selection before behavior: each
  process imports sysml-codegen from the intended worktree, records that worktree's revision or
  candidate patch hash, and executes each same-named generated package in a fresh subprocess.

## Component Overview

- **Predicate name derivation and guard — `src/sysml_codegen/generation/modules.py`.** Own one
  canonical mapping from raw definition key to emitted function name and fail-loud uniqueness over
  a catalog. No new module or naming abstraction is needed.
- **Generation preflight — `src/sysml_codegen/cli/__init__.py`.** Invoke the guard after context
  construction and before output-path mutation, next to existing generation safety checks.
- **F2 unit coverage — `tests/unit/test_constraint_emission.py`.** Exercise all three normalization
  classes, deterministic diagnostics, compile-once non-collision, and direct-call safety.
- **F2 API preservation coverage — generation CLI tests.** Exercise `run_codegen` with
  `overwrite=True` against an absent target and a populated nested tree. Compare complete tree
  manifests, not one sentinel.
- **F1 compiler characterization — `tests/unit/test_predicate_compiler.py`.** Pin direct division by
  zero, zero-to-negative power, exponent overflow, and a raising comparison under a supported
  connective.
- **F1 wrapper characterization — `tests/execution/test_constraint_execution.py`.** Use production
  package generation and invoke the generated constraint wrapper boundary, asserting the original
  exception type/message and absence of evidence construction.
- **Template clarification — `src/sysml_codegen/templates/constraint_module.py.jinja2`.** Change
  only the narrow verdict sentence.
- **Evidence overlay and record — `.project/active/gap-runtime-contract/evidence/` and
  `evidence.md`.** Preserve the unchanged test overlay, generated-package probe, production-only
  candidate patch, their hashes, defect-specific RED/green commands, imported-source assertions,
  input hashes, and byte classifications. These are implementation-stage records, not generated
  product artifacts.

## Non-Goals

- Any TEAx source or test change.
- Claiming `EvaluationFailed`, module identity, both-evaluator parity, or end-to-end F1 closure from
  sysml-codegen evidence alone.
- Accepting colliding raw keys through suffixes, aliases, or source-key rewriting.
- Changing executable-profile admission, Kleene semantics, arithmetic rendering, predicate
  evaluation order, report aggregation, or partial-evidence policy.
- Refactoring the predicate compiler, catalog, generator, or TEAx executor.
- Changing general-purpose `sanitize_name` or `sanitize_qualified_name` behavior.

## Implementation Notes

- The name helper must consume the raw `::`-qualified key exactly once. Do not feed an already
  `__`-joined name back through `sanitize_qualified_name`; its contract explicitly says it is not
  re-entrant (`../agentic-mbse/src/agentic_mbse/sysml/qualified_names.py:83`).
- Build the collision map from distinct `predicate_definition_key(entry)` values. Multiple concrete
  entries for one definition are not collisions.
- The early CLI call should be gated only by `catalog is not None`; an empty `concrete_entries`
  collection passes.
- Preserve `CodeGenerationError` as the public failure type, matching the adjacent generation
  guards (`src/sysml_codegen/generation/constraint_catalog.py:40`).
- F1 exception tests assert both type and message. Pin messages in the supported project Python
  environment; do not generalize them into a codegen-owned diagnostic.
- The current docstring is already substantively narrow. Record the one-line change as clarity and
  an allowed byte diff, not as behavioral repair.
- Historical evidence must use detached worktrees under a newly created `/tmp` directory. It must
  not use `git checkout`, `git reset`, `git clean`, or `git stash` in the current worktree. Cleanup
  removes only the named temporary worktrees after the durable evidence files have been written.
- The saved overlay must not import a helper that exists only after the fix. Its F2 RED tests call
  the pre-existing `compile_shared_predicates` public seam, so baseline failure is `DID NOT RAISE
  CodeGenerationError`, not collection or import failure.

## Potential Risks

- **A direct generation surface may bypass the CLI preflight.** The compile-seam recheck makes that
  path safe. Tests cover both calls.
- **A diagnostic may depend on catalog order.** Sort emitted groups and raw keys before selecting
  and formatting the failure.
- **The early guard may duplicate name logic.** Both callers invoke one helper and one validator;
  neither reimplements normalization.
- **Exception messages may vary with Python/runtime.** Evidence records the supported environment.
  The behavior contract still requires class and message to pass through unchanged, not a
  codegen-authored universal spelling.
- **The external TEAx item may remain undone.** Keep the dependency P0 and state the incomplete F1
  status in evidence and handoff. Do not convert characterization into a closure claim.
- **Editable installs or module caches may select the wrong tree.** Put the intended worktree's
  `src` and root first in `PYTHONPATH`, disable user-site imports, assert resolved source paths and
  revision inside the overlay, and start a new Python process for every historical or generated
  package run. A source-path mismatch is a failed gate, never evidence.

## Integration Strategy

Land the guard without changing the compile map shape or renderer interface. Existing callers keep
receiving `{raw_key: (fn_name, source, args)}`. The CLI gains one preflight call; direct compilation
gains one invariant check. The docstring remains generated through the existing template. No
schema, snapshot format, package metadata, or TEAx API changes enter this item.

The external TEAx leg consumes, but is not implemented by, this design's F1 boundary: it may rely on
the original exception reaching `module.run` unchanged and on the generated module key being
`constraint_id.lower()`. It must satisfy every evaluator field and causal-chain assertion in the
approved spec before GAP-CLOSE F1 can be called closed.

## Validation Approach

### Durable overlay and source isolation

- Save one standalone pytest overlay at
  `.project/active/gap-runtime-contract/evidence/test_gap_runtime_contract_overlay.py`. It contains
  no production code changes. Record its SHA-256 and copy that exact file into both detached
  worktrees. Save the separate generated-package subprocess runner as
  `evidence/run_generated_constraint_case.py` and the strict byte-diff classifier as
  `evidence/classify_generated_tree_diff.py`; hash both.
- Create two detached worktrees from baseline
  `6db321225a5c8568db0287b67ed1d04c03079cc2` under one `mktemp -d` root. Leave the current worktree
  untouched. The baseline worktree stays clean. Export only the three approved production files as
  `evidence/candidate-production.patch`, record its SHA-256, check it, and apply it only to the
  candidate worktree. Record the candidate worktree's resulting production diff hash.
- Run through the existing agentic-mbse environment, but force the selected codegen worktree's
  `src`, repository root, and TEAx package path through `PYTHONPATH`. Set `PYTHONNOUSERSITE=1` and
  `PYTHONDONTWRITEBYTECODE=1`. Every command is a fresh `python -m pytest` or `python` process.
- At overlay import, before behavioral imports, assert that `git rev-parse HEAD` equals the expected
  baseline revision and that resolved `sysml_codegen.__file__` and
  `inspect.getsourcefile(sysml_codegen.generation.modules)` are below the expected worktree's
  `src/`. The candidate additionally verifies that its production diff SHA-256 equals the recorded
  patch hash. A mismatch fails before behavioral assertions.

### F2 behavior and pre-fix RED

- The unchanged overlay calls the pre-existing `compile_shared_predicates` seam. It has one
  rejection test for each case-fold, underscore-run, and quoted-hyphen pair, with stable pytest IDs.
  Each uses opposite predicates and expects `CodeGenerationError` containing the exact emitted name
  and both sorted raw keys.
- On the baseline, run each node separately and the three-node group. Each must exit 1 with
  `DID NOT RAISE CodeGenerationError`; collection failure, missing imports, or any other exception
  invalidates the record. Separately run the overlay's old-impact node. It must pass while proving
  both raw keys compile to the same name and the later function body supplies the result reached by
  both wrapper imports.
- On the candidate, the same three rejection nodes must pass. Add kept project tests for group-order
  permutation, identical-key compile-once behavior, exact helper outputs, and a compiler spy proving
  rejection precedes `compile_predicate`.
- Record the exact commands in Appendix A and their full stdout/stderr, exit status, overlay hash,
  imported paths, and revision in `evidence.md`.

### No partial generated artifacts

- Add two kept tests around the real `run_codegen` API with a synthetic colliding context and
  `GenerationConfig(overwrite=True)`. This exercises the actual preflight placement without a
  license-dependent model capture.
- **Absent target:** begin with a path whose parent exists but whose output root does not. After the
  expected `False` result and collision diagnostic, assert the output root still does not exist.
- **Pre-populated target:** create nested directories, at least two regular files with distinct
  bytes, and a symlink when supported. Snapshot a sorted full-tree manifest containing every
  relative path, path kind, regular-file bytes, and symlink target. After rejection, build the same
  manifest and require exact equality. This proves no clearing, directory creation, new file, file
  rewrite, or symlink replacement occurred. A surviving sentinel alone is insufficient.

### F1 characterization, not RED

- At compiler level, assert the original exception class and exact message for float division by
  zero, `0.0 ** -1.0`, and overflowing exponentiation. Nest one raising comparison under a supported
  `and` or `or` shape and assert that it raises before any compound verdict is returned.
- At the generated-wrapper boundary, invoke `run()` for a raising case and assert that the same
  exception class and message leave the wrapper unchanged. Structure the assertion so no
  `ConstraintEvaluation` or report exists; object identity is not part of the codegen contract.
- Run the overlay's F1 nodes unchanged against baseline and candidate. Both must pass and remain in
  the characterization table, outside F2 RED. Re-run existing finite/violated and
  non-finite/indeterminate suites (`tests/unit/test_predicate_compiler.py:116` and
  `tests/execution/test_constraint_execution.py:100`, `:388`).
- Link the external TEAx item's separate pre-fix RED record when available. Until then,
  `evidence.md` states that normalized module identity remains an unresolved external P0.

### Route parity and before/after bytes

- Use committed fixture `plant_values`. Before comparison, assert both generated trees contain
  `modules/constraints/predicates.py` and at least one constraint wrapper importing a function from
  it. Record a normalized SHA-256 manifest of every file under
  `tests/fixtures/plant_values`; the baseline and candidate manifest hashes must match.
- **Route parity:** in the candidate worktree, generate live and snapshot packages in distinct temp
  parents with the same package name. Compare relative path sets and every file byte with the
  existing full-tree method (`tests/conformance/test_snapshot_generation.py:33` and `:193`).
- **Route behavior:** run the live-generated and snapshot-generated same-named package in separate
  subprocesses using the hashed runner. Each runner asserts that the generated package resolves
  below its expected output root and sysml-codegen resolves below the candidate worktree before it
  checks finite verdict/margin and non-finite Kleene behavior. No package is imported twice in one
  interpreter, so `sys.modules` cannot make one route impersonate the other.
- **Before/after stability:** generate the snapshot route once in each worktree with identical
  absolute fixture input, package name, command, and environment. The allowlist contains only
  constraint wrapper files whose docstring changed and package-contract/seal artifacts transitively
  derived from those bytes. `modules/constraints/predicates.py`, every function name, and every
  wrapper import line must be byte-identical. Any other difference fails the gate.
- Store commands, source assertions, fixture manifests, output-tree manifests, classified diff,
  changed-file hashes, and subprocess results in `evidence.md`. TEAx source and tests remain outside
  this byte comparison.

## Next-Stage Handoff

The plan must treat D1–D5 and I1–I10 as fixed. Save and hash the test-only overlay before adding the
guard, then capture each baseline RED in isolated worktrees. Keep the CLI and compile-seam checks on
one pure validator. Treat F1 work as characterization plus a one-line clarity change. Do not add
guards or wrappers to generated arithmetic.

The highest-risk validation is full-tree preservation in both absent and pre-populated cases because
it fixes detection timing, not only detection existence. The second is proving source selection and
process isolation across historical and route gates. The handoff must carry
`[GAP-CLOSE-F1-TEAX-NORMALIZATION]` as an unresolved external P0; no checkbox or summary may claim
end-to-end F1 closure from this item.

## Next Steps

After design approval, use `my-plan` to sequence test-first implementation, isolated-revision RED
capture, route parity, and the two-revision byte gate. After implementation, use `my-audit`; the
implementing agent must not self-certify the external TEAx leg.

## Appendix A — Exact Evidence Commands

These commands are the required evidence protocol. They create only detached worktrees and outputs
under one named `/tmp` directory. They never switch, stash, reset, clean, or write production files
in the current worktree.

### A1. Capture and isolate the two source trees

```bash
BASE=6db321225a5c8568db0287b67ed1d04c03079cc2
ROOT_REPO=/home/reid/1cfe/sysml-codegen
EVID=$ROOT_REPO/.project/active/gap-runtime-contract/evidence
RUN_ROOT=$(mktemp -d /tmp/gap-runtime-contract-evidence.XXXXXX)
PRE=$RUN_ROOT/pre
POST=$RUN_ROOT/post
mkdir -p "$EVID"
git -C "$ROOT_REPO" worktree add --detach "$PRE" "$BASE"
git -C "$ROOT_REPO" worktree add --detach "$POST" "$BASE"
```

The implementation first saves the overlay and generated-package runner at the paths named in the
validation section. Then it captures only the approved production surface:

```bash
PROD_PATHS='src/sysml_codegen/generation/modules.py src/sysml_codegen/cli/__init__.py src/sysml_codegen/templates/constraint_module.py.jinja2'
git -C "$ROOT_REPO" diff --binary "$BASE" -- $PROD_PATHS > "$EVID/candidate-production.patch"
sha256sum "$EVID/test_gap_runtime_contract_overlay.py" "$EVID/run_generated_constraint_case.py" "$EVID/classify_generated_tree_diff.py" "$EVID/candidate-production.patch" | tee "$EVID/hashes.txt"
git -C "$POST" apply --check "$EVID/candidate-production.patch"
git -C "$POST" apply "$EVID/candidate-production.patch"
cp "$EVID/test_gap_runtime_contract_overlay.py" "$PRE/tests/unit/test_gap_runtime_contract_evidence.py"
cp "$EVID/test_gap_runtime_contract_overlay.py" "$POST/tests/unit/test_gap_runtime_contract_evidence.py"
```

The candidate patch must be non-empty. `git diff --check` runs in `POST`, and the SHA-256 of
`git -C "$POST" diff --binary "$BASE" -- $PROD_PATHS` must equal the recorded production-patch
hash. The fixture is copied once from the baseline so every route and revision reads identical
input bytes:

```bash
cp -a "$PRE/tests/fixtures/plant_values" "$RUN_ROOT/plant_values"
(cd "$RUN_ROOT/plant_values" && find . -type f -print0 | LC_ALL=C sort -z | xargs -0 sha256sum | sha256sum) | tee "$EVID/plant_values-input.sha256"
TEAX=/home/reid/1cfe/teax/packages/teax-simkit
AM=/home/reid/1cfe/agentic-mbse
OVERLAY=tests/unit/test_gap_runtime_contract_evidence.py
```

### A2. Baseline RED and characterization

Each invocation below is a separate process. The overlay's import-time gate checks `EXPECTED_REPO`,
`EXPECTED_REV`, and the imported source paths before collecting the behavioral node.

```bash
(cd "$PRE" && env EXPECTED_REPO="$PRE" EXPECTED_REV="$BASE" PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PRE/src:$PRE:$TEAX" uv run --directory "$AM" python -m pytest -q --override-ini='addopts=' "$OVERLAY::test_f2_collision_rejected[case-fold]")
(cd "$PRE" && env EXPECTED_REPO="$PRE" EXPECTED_REV="$BASE" PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PRE/src:$PRE:$TEAX" uv run --directory "$AM" python -m pytest -q --override-ini='addopts=' "$OVERLAY::test_f2_collision_rejected[underscore-run]")
(cd "$PRE" && env EXPECTED_REPO="$PRE" EXPECTED_REV="$BASE" PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PRE/src:$PRE:$TEAX" uv run --directory "$AM" python -m pytest -q --override-ini='addopts=' "$OVERLAY::test_f2_collision_rejected[quoted-hyphen]")
```

Each command must exit 1 with `DID NOT RAISE CodeGenerationError`. The combined command must report
exactly three assertion failures for that same reason:

```bash
(cd "$PRE" && env EXPECTED_REPO="$PRE" EXPECTED_REV="$BASE" PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PRE/src:$PRE:$TEAX" uv run --directory "$AM" python -m pytest -q --override-ini='addopts=' "$OVERLAY::test_f2_collision_rejected")
```

The impact and F1 commands must exit 0 at the baseline. The impact node pins the shared function
name and later-body overwrite. The F1 group pins already-correct raw exceptions and is not RED:

```bash
(cd "$PRE" && env EXPECTED_REPO="$PRE" EXPECTED_REV="$BASE" PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PRE/src:$PRE:$TEAX" uv run --directory "$AM" python -m pytest -q --override-ini='addopts=' "$OVERLAY::test_pre_fix_later_body_overwrites_earlier")
(cd "$PRE" && env EXPECTED_REPO="$PRE" EXPECTED_REV="$BASE" PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PRE/src:$PRE:$TEAX" uv run --directory "$AM" python -m pytest -q --override-ini='addopts=' "$OVERLAY::test_f1_unmangled_raise")
```

### A3. Candidate overlay

Run the same overlay from `POST` with a fresh interpreter. `EXPECTED_PATCH_SHA` is read from
`hashes.txt`; the overlay compares it with the candidate worktree's production diff before tests:

```bash
PATCH_SHA=$(sha256sum "$EVID/candidate-production.patch" | cut -d' ' -f1)
(cd "$POST" && env EXPECTED_REPO="$POST" EXPECTED_REV="$BASE" EXPECTED_PATCH_SHA="$PATCH_SHA" PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$POST/src:$POST:$TEAX" uv run --directory "$AM" python -m pytest -q --override-ini='addopts=' "$OVERLAY::test_f2_collision_rejected")
(cd "$POST" && env EXPECTED_REPO="$POST" EXPECTED_REV="$BASE" EXPECTED_PATCH_SHA="$PATCH_SHA" PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$POST/src:$POST:$TEAX" uv run --directory "$AM" python -m pytest -q --override-ini='addopts=' "$OVERLAY::test_f1_unmangled_raise")
```

Both commands must exit 0. Kept project tests then cover deterministic diagnostics, helper
equivalence, compile ordering, and both no-write target states. The two no-write nodes run together
with this exact command and must both pass:

```bash
(cd "$POST" && env EXPECTED_REPO="$POST" EXPECTED_REV="$BASE" EXPECTED_PATCH_SHA="$PATCH_SHA" PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$POST/src:$POST:$TEAX" uv run --directory "$AM" python -m pytest -q --override-ini='addopts=' "$OVERLAY::test_collision_rejection_preserves_absent_output" "$OVERLAY::test_collision_rejection_preserves_populated_tree")
```

### A4. Generation and process-isolated route checks

The evidence CLI is the selected worktree's source invoked directly, not an installed
`sysml-codegen` script. Each generation call runs in a new process:

```bash
run_generate='import os,pathlib,sysml_codegen; expected=pathlib.Path(os.environ["EXPECTED_REPO"])/"src"; assert pathlib.Path(sysml_codegen.__file__).resolve().is_relative_to(expected.resolve()); from sysml_codegen.cli import main; main()'
PKG=plant_values_evidence
mkdir -p "$RUN_ROOT/out"
(cd "$POST" && env EXPECTED_REPO="$POST" PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$POST/src:$POST" uv run --directory "$AM" python -c "$run_generate" generate --models "$RUN_ROOT/plant_values" --output "$RUN_ROOT/out/live/$PKG" --package-name "$PKG" --overwrite)
(cd "$POST" && env EXPECTED_REPO="$POST" PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$POST/src:$POST" uv run --directory "$AM" python -c "$run_generate" generate --from-snapshot "$RUN_ROOT/plant_values/extraction_snapshot.json" --output "$RUN_ROOT/out/snapshot/$PKG" --package-name "$PKG" --overwrite)
```

Require full-tree byte identity, shared predicates, and at least one importing wrapper. Then invoke
the hashed runner four times. Every invocation is a fresh process and asserts both generated-package
and codegen source paths before behavior:

```bash
for route in live snapshot; do
  for case_name in finite nonfinite; do
    env PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$RUN_ROOT/out/$route:$POST/src:$POST:$TEAX" uv run --directory "$AM" python "$EVID/run_generated_constraint_case.py" --package-root "$RUN_ROOT/out/$route" --package-name "$PKG" --codegen-root "$POST" --case "$case_name"
  done
done
```

For before/after stability, generate the snapshot route from `PRE` and `POST` into separate parents,
again using the shared snapshot path and the same package name:

```bash
(cd "$PRE" && env EXPECTED_REPO="$PRE" PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PRE/src:$PRE" uv run --directory "$AM" python -c "$run_generate" generate --from-snapshot "$RUN_ROOT/plant_values/extraction_snapshot.json" --output "$RUN_ROOT/out/before/$PKG" --package-name "$PKG" --overwrite)
(cd "$POST" && env EXPECTED_REPO="$POST" PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$POST/src:$POST" uv run --directory "$AM" python -c "$run_generate" generate --from-snapshot "$RUN_ROOT/plant_values/extraction_snapshot.json" --output "$RUN_ROOT/out/after/$PKG" --package-name "$PKG" --overwrite)
uv run --directory "$AM" python "$EVID/classify_generated_tree_diff.py" --before "$RUN_ROOT/out/live/$PKG" --after "$RUN_ROOT/out/snapshot/$PKG" --mode exact
uv run --directory "$AM" python "$EVID/classify_generated_tree_diff.py" --before "$RUN_ROOT/out/before/$PKG" --after "$RUN_ROOT/out/after/$PKG" --mode approved-docstring-only
```

The classifier records complete manifests, rejects every non-allowlisted difference, and separately
asserts shared-predicate bytes and wrapper import lines are identical. Cleanup occurs only after
`evidence.md` contains all outputs:

```bash
git -C "$ROOT_REPO" worktree remove --force "$PRE"
git -C "$ROOT_REPO" worktree remove --force "$POST"
rmdir "$RUN_ROOT" 2>/dev/null || true
```

---

Implementation completed 2026-07-18. See [plan.md](plan.md) and [evidence.md](evidence.md).
`[GAP-CLOSE-F1-TEAX-NORMALIZATION]` remains external and open.
