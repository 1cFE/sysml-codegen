# Implementation Plan: CONSTRAINT-WAVE Item 2 — Generated Constraint Name Safety

**Status:** Certified (license-free scope) — external execution evidence unavailable
**Created:** 2026-07-18
**Last Updated:** 2026-07-18
**Scope:** Item 2 / R-3 only. No commits, pushes, PR work, fixture recapture, or unrelated cleanup.

## Source Documents

- **Revised spec:** [spec.md](spec.md)
- **Historical spec review:** [spec-review.md](spec-review.md) — its four findings are incorporated
  in the revised spec.
- **Revised design:** [design.md](design.md) — the implementation contract for decisions,
  invariants, route coverage, and evidence.
- **Historical design review:** [design-review.md](design-review.md) — M1–M4 and m1–m4 are
  incorporated in the revised design.
- **Primary R-3 evidence:**
  [20260718-192048_constraint-exec-pr-wave-code-review.md](../../research/20260718-192048_constraint-exec-pr-wave-code-review.md)
- **Epic:** [epic_constraint_pr_wave_remediation.md](../../backlog/epic_constraint_pr_wave_remediation.md),
  Item 2.

## Implementation Strategy

### Phasing Rationale

Freeze the four historical failures and the worktree firewall before production edits. Next prove
the highest-risk premise: the existing facts can reconstruct a minimal formal-identity carrier on
live and snapshot routes, and Pydantic copies retain it without changing serialized payloads. Only
then add the pure two-scope policy, symbol-table completeness check, and direct compiler/renderer
adapters. After those lower boundaries are green, apply the full graph preflight to every graph-aware
renderer and writer, including `run_codegen()` before target clearing. Finish with isolated
candidate evidence, exact byte/execution controls, and repository gates.

This order follows [design.md#next-stage-handoff](design.md#next-stage-handoff). It separates
provenance feasibility from collision policy, and collision policy from mutation timing, so a
failure identifies which premise broke.

### Critical Path

Frozen `512786c` R-3 overlay → excluded carrier retained across lowering/rebuild/copies → pure
scope and correspondence validators plus semantic binding completeness → public exception adapters
at direct compiler/render seams → full preflight at every graph-aware render/write boundary →
collision-free byte and execution proof → focused, optimized, broader, full, static, diff, and
fixture gates.

### First Proof Point

Before policy code exists, tests must prove that definition, omitted-default, inline, and defensive
non-definition routes produce the identity described in
[design.md#identity-construction-matrix](design.md#identity-construction-matrix), that
`extend_graph_with_constraints()` preserves it through deep model copies, and that all named dump,
contract, fingerprint, generated-contract, and snapshot surfaces remain unchanged. If a valid route
has neither a qualified identity nor an honest raw identity, stop and surface the premise conflict;
do not weaken correspondence or invent provenance.

### Scope and Dirty-Work Firewall

The worktree is already dirty. Item 6 currently edits `src/sysml_codegen/cli/__init__.py`,
`tests/unit/test_cli_generation.py`, contract/seal files, and related tests. Item 2 must add hunks to
the first two overlapping files without removing, rewriting, formatting, or absorbing Item 6's
symlink-symmetry changes. All other pre-existing tracked and untracked work is user work.

- [x] Before Phase 1, save `git status --short`, `git diff --binary`, the current HEAD, and SHA-256
  hashes of every dirty tracked file under
  `.project/active/constraint-wave-name-safety/evidence/pre-item/`.
- [x] Save separate pre-item copies and diffs of `src/sysml_codegen/cli/__init__.py` and
  `tests/unit/test_cli_generation.py`; use them to prove the existing Item 6 hunks survive after
  Item 2 adds overlapping-file changes.
- [x] Save a sorted SHA-256 manifest of every regular file under `tests/fixtures/`. Fixture bytes
  are immutable for this item.
- [x] At every phase boundary, review `git status --short` and `git diff --` for that phase's
  allowlist. Do not run checkout, reset, clean, stash, broad formatting, or any command that changes
  unrelated paths.
- [x] Build isolated candidate evidence from an Item-2-only delta against the saved pre-item copies.
  Do not mistake the pre-existing Item 6 delta for Item 2 or include it in the historical candidate
  patch.

### Overall Validation Approach

- Write and run the named tests before each production batch; save the expected RED reason.
- Test direct pure/compiler/render boundaries before orchestration and filesystem writers.
- Use full manifests for no-mutation claims: relative path, kind, directory entry, symlink target,
  and regular-file bytes.
- Keep normal pytest as primary assertion evidence. Repeat the focused selection under
  `PYTHONOPTIMIZE=1` to prove production behavior does not depend on `assert`.
- Run the real collision-free generated module in the execution environment, outside the default
  pytest marker filter.
- Compare a fixed collision-free package at `512786c` and the Item-2 candidate. The permitted
  generated-tree diff is empty.
- Record exact commands, revisions, imported paths, hashes, exit statuses, pass/skip/fail/error
  counts, license state, and any inherited failure classification in `evidence/evidence.md`.

---

## Phase 1: Freeze Historical R-3 Evidence and Scope Baselines

### Goal

Create one baseline-compatible, test-only overlay that independently captures `value`, `status`,
`verdict`, and `self`, plus the three identity/correspondence defects. Freeze all worktree, fixture,
serialization, and generated-byte baselines before production changes.

### Assumption Under Test

Revision `512786c` reaches each recorded R-3 behavior through the intended generated scope, and a
single overlay can prove those behaviors without importing the current checkout or candidate-only
helpers. See [design.md#red-tests-at-512786c](design.md#red-tests-at-512786c) and decision D7 in
[design.md#key-decisions](design.md#key-decisions).

### Test Stencil (Write This First)

```python
@pytest.mark.parametrize("formal", ["value", "status", "verdict", "self"])
def test_r3_rejected_at_public_boundary(formal):
    case = build_baseline_compatible_case(formal)
    with pytest.raises(case.expected_exception):
        case.invoke_public_boundary()

def test_r3_historical_impact(case):
    observed = case.invoke_old_generated_code()
    assert observed == case.recorded_corruption_or_exception
```

### Changes Required

**See:** [design.md#historical-overlay-and-byte-proof](design.md#historical-overlay-and-byte-proof),
[design.md#validation-approach](design.md#validation-approach), and required invariants I7, I8,
I11, and I12 in [design.md#required-invariants](design.md#required-invariants).

- [x] `.project/active/constraint-wave-name-safety/evidence/test_name_safety_overlay.py` and
  separately hashed `test_name_safety_historical_impact.py` (new, test-only): add separate
  rejection and historical-impact nodes for all four names without changing the frozen rejection
  overlay. The `value`
  impact must show the wrong positive signed margin, `status` must show `margin=None`, `verdict`
  must reach the recorded `TypeError`, and `self` must reach duplicate-parameter `SyntaxError`.
- [x] In the same overlay, add separate rejection nodes for two resolved predicate identities with
  one final leaf name, two definition formals that collapse after `sanitize_name()`, and one source
  identity with disagreeing predicate/wrapper names.
- [x] Make every overlay process assert exact HEAD, `sysml_codegen.__file__`, and the resolved paths
  for `predicate_compiler.py`, `modules.py`, and `constraint_lowering.py` before behavior. Use only
  imports and fixture constructors available at `512786c`.
- [x] `.project/active/constraint-wave-name-safety/evidence/run_collision_free_control.py` (new):
  add a fresh-process runner for the fixed `x <= limit` package. It must assert the generated
  package import path and exact satisfied/violated evidence fields.
- [x] `.project/active/constraint-wave-name-safety/evidence/compare_generated_trees.py` (new):
  compare sorted complete manifests and file bytes. Any path, kind, symlink-target, or byte delta is
  fatal; there is no approved diff set.
- [x] `.project/active/constraint-wave-name-safety/evidence/evidence.md` (new): create sections for
  pre-item state, historical RED, candidate GREEN, carrier/serialization proof, byte/execution
  proof, test gates, static gates, and fixture/diff gates. Do not claim results before commands run.

### Validation

**Isolated historical commands:**

```bash
evidence_root="$(mktemp -d)"
git worktree add --detach "$evidence_root/baseline" 512786c
git worktree add --detach "$evidence_root/candidate" 512786c
git -C "$evidence_root/baseline" rev-parse HEAD
git -C "$evidence_root/candidate" rev-parse HEAD
sha256sum .project/active/constraint-wave-name-safety/evidence/test_name_safety_overlay.py
```

For every node, run a fresh process with this environment and substitute the selected worktree for
`<tree>`:

```bash
env -u PYTHONPATH PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 \
  PYTHONPATH="<tree>/src:<tree>" \
  uv run --project "<tree>" pytest -q -p no:cacheprovider \
  "<tree>/.evidence/test_name_safety_overlay.py::<node>"
```

- [x] Run the separately hashed historical-impact overlay with the detached baseline first on
  `PYTHONPATH`. Run each four-name node in its own process; each must pass and record the exact
  corruption or exception while the frozen rejection overlay hash remains unchanged.
- [x] Run each corresponding typed-rejection node separately at the baseline. Each must fail only
  because the expected public exception was not raised. Collection, revision, path, import,
  fixture, or setup failures invalidate the record.
- [x] Run the three identity/correspondence rejection nodes separately and record their independent
  baseline RED reasons.
- [x] Confirm the overlay SHA-256 is identical in both worktrees and the current dirty worktree has
  not changed.
- [x] Save the complete fixture manifest with:

```bash
find tests/fixtures -type f -print0 | sort -z | xargs -0 sha256sum
```

**What We Know Works After This Phase:**

The seven unsafe acceptance/rejection defects are independently reproducible from the pinned
source, and every baseline needed to distinguish Item 2 from Item 6 or fixture drift is durable.
The exact historical corrupted outcomes remain sourced to the review rather than a new overlay run.

---

## Phase 2: Retain the Formal-Identity Carrier Without Serialization Change

### Goal

Add the minimal immutable identity carrier and thread it through every lowering route into
constraint `ModuleInput` objects. Prove retention across live/snapshot reconstruction and Pydantic
copies while proving omission from all serialized and generated payloads.

### Assumption Under Test

The facts already carried by snapshot v3/facts-v1 are sufficient to construct the identity matrix,
and `Field(exclude=True)` preserves in-memory copy semantics without entering dumps, contracts,
fingerprints, seals, or snapshot bytes. See [design.md#binding-and-identity-model](design.md#binding-and-identity-model),
[design.md#identity-construction-matrix](design.md#identity-construction-matrix), and
[design.md#live-and-snapshot-availability](design.md#live-and-snapshot-availability).

### Test Stencil (Write This First)

```python
def test_definition_identity_survives_graph_copy_but_not_dump():
    concrete = lower_definition_formal(raw="limit", qn="Pkg::C::limit")
    graph = extend_graph_with_constraints(empty_graph(), [concrete], deriver())
    carrier = constraint_module(graph).inputs[0].formal_identity
    assert carrier == ConstraintFormalIdentity(raw_name="limit", qualified_name="Pkg::C::limit")
    assert graph.model_copy(deep=True).modules[-1].inputs[0].formal_identity == carrier
    assert "formal_identity" not in graph.model_dump(mode="json")["modules"][-1]["inputs"][0]
```

### Changes Required

**See:** decision D3 in [design.md#key-decisions](design.md#key-decisions), invariants I10–I12 in
[design.md#required-invariants](design.md#required-invariants), and the carrier notes in
[design.md#implementation-notes](design.md#implementation-notes).

- [ ] `tests/conformance/test_constraint_lowering.py:564` (tests first): extend the existing
  definition-formal helpers and add explicit actual, omitted default, inline leaf, defensive
  non-definition actual, and omitted-QN cases. Assert the exact raw/QN pair on
  `ConcreteConstraintInput`, including absent-QN raw fallback and one-sided/multiple-target
  fail-closed cases.
- [ ] `tests/conformance/test_constraint_name_safety_routes.py` (new, tests first): prove the same
  carrier reaches the matching constraint `ModuleInput` after `extend_graph_with_constraints()`;
  prove deep/shallow model copies retain it; prove a facts codec round trip followed by snapshot
  graph rebuild reconstructs an equal carrier and equal unsafe graph. Keep any licensed live
  fixture parity as a separately marked leg, not a prerequisite for the license-free synthetic
  route proof.
- [ ] `tests/unit/test_contract_models.py:27`,
  `tests/conformance/test_fingerprint_stability.py:44`, and
  `tests/conformance/test_snapshot_generation.py:98` (tests first): pin omission from carrier model
  Python/JSON dumps, complete `ComputationGraph.model_dump()`, model-contract payload and exact
  bytes, catalog fingerprint input, generated model/package contracts, and snapshot sections/version.
  Pin separately that the only internal `model_json_schema()` change is the two optional carrier
  properties; no generated or snapshot schema changes.
- [x] `src/sysml_codegen/resolution/models.py:141` and `:268`: add the immutable data-only identity
  type and optional excluded fields on `ModuleInput` and `ConcreteConstraintInput`. Resolution owns
  this record; it must not import generation code.
- [x] `src/sysml_codegen/analysis/constraint_lowering.py:601`, `:702`, `:971`, and `:1146`: construct
  identity before sanitization, pass it through explicit/default/inline/defensive resolution, and
  copy it at graph extension. Preserve sanitizer behavior, formal order, resolution order, and
  first-occurrence semantics.
- [x] `src/sysml_codegen/orchestration/pipeline_builder.py` and snapshot codecs/templates: expect no
  production edit. If tests require one, stop and reconcile the evidence with
  [design.md#live-and-snapshot-availability](design.md#live-and-snapshot-availability) before
  broadening the patch.

### Validation

**Automated:**

- [ ] `uv run pytest -q tests/conformance/test_constraint_lowering.py -k "formal or identity or default or inline"`
- [x] `uv run pytest -q tests/conformance/test_constraint_name_safety_routes.py tests/unit/test_contract_models.py tests/conformance/test_fingerprint_stability.py tests/conformance/test_snapshot_generation.py`
- [x] Repeat `tests/conformance/test_constraint_name_safety_routes.py` under
  `PYTHONOPTIMIZE=1`.
- [x] Run targeted Ruff/format and mypy on `resolution/models.py`, `constraint_lowering.py`, and the
  touched Phase 2 tests.

**Payload and scope checks:**

- [x] Compare snapshot JSON before/after for the synthetic round trip: version and section names are
  exact, and no identity-carrier key appears.
- [x] Compare the Phase 1 fixture manifest and `git diff -- tests/fixtures`; both must be unchanged.
- [x] Confirm the saved Item 6 hunks and all unrelated dirty paths remain present and unmodified.

**What We Know Works After This Phase:**

Every supported route carries the richest identity already available, live and snapshot rebuilds
agree, copies retain provenance, and no serialization or generated-byte surface sees the carrier.

---

## Phase 3: Implement Pure Scope Policies, Completeness, and Direct Boundaries

### Goal

Implement the shared data-only collision vocabulary, deterministic pure validators, and semantic
symbol-table checker. Enforce them at direct predicate compilation and constraint render seams with
the required exception types and one preserved structured violation.

### Assumption Under Test

Python's symbol table reports all bindings in the exact emitted function scopes, and the structured
identity inventory can distinguish safe repetition from collisions without sorting successful
predicate arguments or changing emitted bytes. See decisions D2, D5, and D6 in
[design.md#key-decisions](design.md#key-decisions),
[design.md#scope-completeness-algorithm](design.md#scope-completeness-algorithm), and invariants
I1–I6, I8, and I9 in [design.md#required-invariants](design.md#required-invariants).

### Test Stencil (Write This First)

```python
def test_predicate_generated_local_collision_is_structured():
    ir = predicate_with_resolved_leaf("value", "Pkg::C::value")
    with pytest.raises(PredicateCompileError) as error:
        compile_predicate(ir, "constraint_pred_pkg__c")
    assert error.value.name_safety_violation.scope == "predicate"
    assert error.value.name_safety_violation.final_binding == "value"

def test_policy_completeness_fails_when_emitted_scope_gains_a_binding():
    source = production_predicate_source() + "\n    injected_local = 1\n"
    with pytest.raises(ScopePolicyMismatch):
        verify_emitted_scope(source, PREDICATE_SCOPE_POLICY)
```

### Changes Required

**See:** [design.md#scope-policies](design.md#scope-policies),
[design.md#deterministic-diagnostics](design.md#deterministic-diagnostics),
[design.md#exception-normalization-and-payload-flow](design.md#exception-normalization-and-payload-flow),
and [design.md#component-overview-and-file-level-changes](design.md#component-overview-and-file-level-changes).

- [ ] `tests/unit/test_constraint_name_safety.py` (new, tests first): cover predicate/wrapper
  reserved overlaps; distinct identities sharing a binding; one identity under multiple bindings;
  same-identity/same-name repetition; missing/extra/one-sided provenance; cross-path name
  disagreement; duplicate/missing catalog-module joins; fixed predicate-before-wrapper ordering;
  and message/record invariance under catalog, formal, leaf, and module-input permutations.
- [ ] In the same file, compare production predicate and wrapper outputs with their policies using
  at least two model-parameter sentinels. Add independent mutation cases for positional-only,
  regular, keyword-only, variadic parameters; `Assign`, `AnnAssign`, `AugAssign`, tuple/list/starred
  unpacking; sync/async `for` and `with`; exception aliases; imports; and named expressions. Add
  fail-loud cases for comprehensions, generator expressions, lambdas, nested functions/classes,
  `global`, and `nonlocal`.
- [ ] `tests/unit/test_predicate_compiler.py:202` (tests first): add exact `value`/`status`
  collisions, two target QNs sharing one leaf name, repeated same-identity deduplication,
  collision-free first-occurrence argument order, exact `PredicateCompileError` payload/message,
  and direct semantic-completeness failure before source return.
- [ ] `tests/unit/test_constraint_emission.py:44` (tests first): update constraint fixtures with
  provenance, then add `self`/`verdict`, wrapper sanitize collapse, missing/extra identity,
  cross-path disagreement, forged compiled-map completeness, direct-render error type, and
  collision-free exact-source controls.
- [ ] Add boundary-normalization tests asserting that direct compiler errors are
  `PredicateCompileError`; shared compilation, predicate-module rendering, wrapper rendering, and
  `generate_teax_module()` expose `CodeGenerationError`; the exact violation object is retained;
  compiler-to-package conversion has `__cause__`; messages match the centralized formatter; and
  unrelated compiler errors normalize with payload `None` only where the design requires.
- [x] `src/sysml_codegen/generation/constraint_name_safety.py` (new): implement immutable policy
  binding and violation records, two structured policies, predicate and wrapper inventory builders,
  pure unit/correspondence/graph checks, fixed sorting/formatting, and the `symtable`-based semantic
  checker. It performs no sanitization, filesystem access, public-exception construction, CLI
  import, or generation-facade import.
- [x] `src/sysml_codegen/generation/predicate_compiler.py:99`, `:202`, and `:240`: attach the optional
  structured payload, inventory leaves before string deduplication/body compilation, preserve safe
  argument order, and verify the exact returned predicate scope.
- [x] `src/sysml_codegen/orchestration/pipeline_context.py:51` and
  `src/sysml_codegen/generation/errors.py`: add the optional typed payload and lazy package-boundary
  adapter without introducing a runtime import cycle.
- [x] `src/sysml_codegen/generation/modules.py:131`, `:167`, `:188`, and `:280`: normalize compiler
  errors, verify supplied shared predicate source, replace name-only wrapper reconciliation with
  identity correspondence, verify exact wrapper `run` bindings, and preserve GAP-CLOSE's existing
  predicate-function-name guard and compile-once behavior.
- [x] Keep both constraint templates unchanged. The completeness check observes their exact emitted
  Python; it does not parse Jinja, use regex, or search raw strings.

### Validation

**Automated:**

- [x] `uv run pytest -q tests/unit/test_constraint_name_safety.py`
- [x] `uv run pytest -q tests/unit/test_predicate_compiler.py tests/unit/test_constraint_emission.py`
- [x] `PYTHONOPTIMIZE=1 uv run pytest -q tests/unit/test_constraint_name_safety.py tests/unit/test_predicate_compiler.py tests/unit/test_constraint_emission.py`
- [x] `uv run pytest -q tests/conformance/test_constraint_generation_integration.py`
- [x] Run Ruff/format on the Phase 3 files and targeted mypy on all five production modules changed
  in this phase.

**Manual code checks:**

- [x] Confirm diagnostic sorting never reorders successful predicate arguments or wrapper inputs.
- [x] Confirm no accepted name, sanitizer, template context, function name, signature, or pipeline
  interface changed.
- [x] Confirm the pure module has no import edge to CLI, public generation facade, or public error
  classes.

**What We Know Works After This Phase:**

Both actual Python scopes have complete structured policies; all direct compile/render bypasses
reject unsafe bindings deterministically with normalized structured errors; accepted source remains
unchanged.

---

## Phase 4: Preflight Every Graph-Aware Renderer and Writer Before Mutation

### Goal

Apply the full graph validator at every graph-aware render and write boundary. Make
`_generate_modules()` render all constraint Python in memory before its first write, and run the
shared `run_codegen()` preflight after live/snapshot convergence but before clearing or setup.

### Assumption Under Test

Every API that can validate predicate/wrapper correspondence has the complete graph at entry, and
the nine direct CLI writers can reject before any filesystem operation. See decision D4 in
[design.md#key-decisions](design.md#key-decisions),
[design.md#render-and-write-boundary-inventory](design.md#render-and-write-boundary-inventory), and
invariants I6–I8 in [design.md#required-invariants](design.md#required-invariants).

### Test Stencil (Write This First)

```python
@pytest.mark.parametrize("writer", GRAPH_AWARE_WRITERS)
@pytest.mark.parametrize("initial_tree", ["absent", "populated"])
def test_unsafe_graph_rejected_before_writer_io(writer, initial_tree, tmp_path):
    output = prepare_tree(tmp_path, initial_tree)
    before = complete_tree_manifest(output)
    with pytest.raises(CodeGenerationError) as error:
        writer(unsafe_context(), config_for(output))
    assert error.value.name_safety_violation is selected_violation
    assert complete_tree_manifest(output) == before
```

### Changes Required

**See:** [design.md#package-data-flow](design.md#package-data-flow),
[design.md#render-and-write-boundary-inventory](design.md#render-and-write-boundary-inventory), and
[design.md#integration-strategy](design.md#integration-strategy).

- [ ] `tests/unit/test_cli_generation.py:108` (tests first): add unsafe graph builders for all four
  reserved names, predicate identity collapse, wrapper sanitizer collapse, missing provenance,
  cross-path disagreement, and duplicate/missing catalog-module joins. Assert fixed selection and
  exact diagnostic equality under all relevant permutations.
- [x] Expand the complete-tree manifest helper so a missing root, directories, regular files,
  symlinks, and symlink targets are represented without following links. Preserve the current Item
  6 symlink-root test and its production hunks unchanged.
- [x] Parameterize both absent and populated targets across `_generate_schemas`,
  `_generate_modules`, `_generate_stencils`, `_generate_pipeline`, `_generate_registry`,
  `_generate_entry_points`, `_generate_backlog`, `_generate_tests`, and `_seal_package`. Each direct
  call must raise `CodeGenerationError` with the same selected payload before its first filesystem
  operation. Do not infer one writer's safety from another.
- [ ] Add `run_codegen()` tests for live-context and snapshot-context convergence. For all four
  reserved names, `run_codegen()` returns `False`, logs the deterministic message with the selected
  structured record, never reaches clear/setup, leaves an absent root absent, and preserves a
  populated complete manifest. Add a `cmd_generate` assertion for existing nonzero exit/stderr
  behavior without claiming an object crosses the process boundary.
- [x] `tests/conformance/test_constraint_generation_integration.py:67` (tests first): make the
  offline graph fully provenance-bearing; exercise direct full-surface generation; verify forged
  predicate/wrapper source cannot bypass semantic completeness; retain AST parse checks for every
  emitted Python artifact.
- [x] Add direct graph-renderer tests for `generate_pipeline_yaml()`, `generate_registry()`, and
  `build_model_contract()`: unsafe graphs raise before context/projection/fingerprinting, safe graphs
  retain exact output.
- [x] `src/sysml_codegen/generation/pipeline.py:26`,
  `src/sysml_codegen/generation/registry.py:185`, and
  `src/sysml_codegen/contracts/model_contract.py:27`: invoke the full package adapter before reading
  graph data into output context.
- [x] `src/sysml_codegen/cli/__init__.py:290`, `:333`, `:402`, `:488`, `:511`, `:538`, `:568`,
  `:587`, and `:610`: call one private full-preflight adapter at entry, before path construction that
  mutates, reads used for smart regeneration, `mkdir`, copy, seal inspection, or write.
- [x] Refactor `_generate_modules()` so compilation, predicate-module rendering, and every
  constraint wrapper render/symbol check finish in memory before its first `mkdir`, package-init
  creation, or write. Preserve existing module iteration and write bytes once staging succeeds.
- [x] `src/sysml_codegen/cli/__init__.py:950`: run the same full preflight immediately after either
  context route builds the graph and before Item 6's link-free check, overwrite clearing, output
  setup, primitives, schemas, or any writer. Retain the F2 predicate-name check within the full
  validation path and retain Item 6 exception handling/link checks.

### Validation

**Automated:**

- [x] `uv run pytest -q tests/unit/test_cli_generation.py`
- [x] `uv run pytest -q tests/conformance/test_constraint_generation_integration.py tests/unit/test_contract_models.py`
- [x] `PYTHONOPTIMIZE=1 uv run pytest -q tests/unit/test_cli_generation.py tests/conformance/test_constraint_generation_integration.py`
- [x] Re-run the current Item 6 focused files after every overlapping CLI batch:

```bash
uv run pytest -q tests/unit/test_cli_generation.py tests/unit/test_contract_models.py \
  tests/unit/test_verify_package.py tests/conformance/test_seal_step9.py \
  tests/conformance/test_fingerprint_stability.py
```

**Boundary review:**

- [x] For each renderer/writer in
  [design.md#render-and-write-boundary-inventory](design.md#render-and-write-boundary-inventory),
  cite one kept test node and its first possible I/O/render action in `evidence/evidence.md`.
- [x] Confirm `_setup_output_directories`, `_generate_primitives`, and lower entry-point helpers did
  not gain an unrelated graph parameter; `run_codegen()` or their graph-aware parent protects them.
- [x] Compare the saved pre-item overlap diffs. Every Item 6 hunk remains, and Item 2 adds only
  reviewable adjacent or separate hunks.

**What We Know Works After This Phase:**

No graph-aware bypass can return or write an unsafe generated package. Direct writers and full
orchestration reject before mutation, while lower render seams independently retain the same policy.

### Independent Audit Remediation

- [x] A constraint module with `constraint_catalog=None` produces a deterministic structured
  `catalog_module_join` violation; a graph with neither constraint modules nor catalog remains
  valid.
- [x] Direct validation, pipeline YAML, registry, model contract, all nine writers, and
  `run_codegen()` reject that state before mutation. Writer and orchestration tests cover absent
  and populated targets.
- [x] Sixteen kept permutations cover catalog, formal, predicate-leaf, and module-input order,
  pinning one exact selected diagnostic. A separate safe control retains first-occurrence argument
  order.
- [x] A separate hashed baseline overlay independently executes the four reviewed historical
  impacts while the original rejection overlay remains byte-identical.

---

## Phase 5: Prove Candidate Rejection, Collision-Free Bytes, Execution, and Repository Gates

### Goal

Run the frozen overlay against an isolated Item-2 candidate, prove all seven rejection nodes GREEN,
prove collision-free output is byte-identical to `512786c`, execute exact satisfied/violated
controls, and finish all focused, optimized, broader, full, static, diff, and fixture gates.

### Assumption Under Test

The implementation changes only unsafe acceptance. Collision-free code generation, contracts,
fingerprints, seals, imports, and runtime evidence remain exact. See
[design.md#historical-overlay-and-byte-proof](design.md#historical-overlay-and-byte-proof),
[design.md#green-focused-tests](design.md#green-focused-tests), and invariant I12 in
[design.md#required-invariants](design.md#required-invariants).

### Test Stencil (Write This First)

```python
def test_name_safety_collision_free_exact_evidence(generated_package):
    satisfied = generated_package.run(x=2.0, limit=3.0)
    violated = generated_package.run(x=4.0, limit=3.0)
    assert evidence_tuple(satisfied) == (True, "satisfied", 1.0, {"x": 2.0, "limit": 3.0})
    assert evidence_tuple(violated) == (False, "violated", -1.0, {"x": 4.0, "limit": 3.0})
```

### Changes Required

- [x] `tests/execution/test_constraint_execution.py:326` (tests first): add
  `test_name_safety_collision_free_exact_evidence`, one focused real generated-package node for
  `x <= limit`. Run satisfied and violated inputs and assert exact
  `actual_value`, `status`, signed margin, and `observed` mapping. Assert the generated module import
  path and that no colliding-name mapping/alias exists.
- [x] Update `.project/active/constraint-wave-name-safety/evidence/evidence.md` with immutable
  baseline/candidate revisions, overlay and Item-2-only patch SHA-256 values, imported paths, exact
  commands/output, byte manifests, execution results, suite counts, license state, static baseline,
  fixture manifest, and dirty-scope comparison.
- [x] Do not modify production code merely to make evidence harnessing easier. Evidence scripts
  remain compatible with the pinned baseline.

### Isolated Candidate Evidence

- [x] Construct the Item-2-only production delta by comparing saved pre-item copies with the final
  allowlisted working files. Review it path-by-path, then apply it to the detached candidate only
  after `git apply --check`. The patch must exclude all pre-existing Item 6 and unrelated changes.
- [x] Assert candidate HEAD remains `512786c`, then assert candidate module import paths before
  every node. Hash the applied patch and overlay.
- [x] Run all seven rejection nodes separately in the candidate with the Phase 1 fresh-process
  command. Each must pass at the public boundary with the expected exception type, exact structured
  payload, deterministic message, and no raw `SyntaxError`/`TypeError`/corrupted evidence.
- [x] Run the no-mutation overlay nodes against both absent and populated roots in the candidate.
- [x] Generate the fixed collision-free package in baseline and candidate worktrees with the same
  absolute input, package name, and output layout. Run
  `compare_generated_trees.py`; require an empty diff for paths, kinds, symlink targets, and bytes.
- [x] Run `run_collision_free_control.py` in fresh subprocesses against both generated trees. Save
  the exact satisfied and violated evidence tuples. **Done 2026-07-19** in the agentic-mbse venv
  (`/home/reid/1cfe/agentic-mbse/.venv/bin/python`, pandas 2.3.3; `src` on `PYTHONPATH`,
  `TEAX_SIMKIT_PATH=/home/reid/1cfe/teax/packages/teax-simkit`). Exact tuples saved to
  `evidence/collision-free-execution-tuples.txt`: satisfied `(True, 'satisfied', 1.0, {'x': 2.0,
  'limit': 3.0})`, violated `(False, 'violated', -1.0, {'x': 4.0, 'limit': 3.0})`.
  **Deviation (one tree):** the baseline/candidate worktrees were already removed after the
  byte-identity step. The control ran once against the current working tree (the byte-identity
  candidate). The 27-file byte-identical baseline/candidate manifests
  (`collision-free-baseline.sha256` vs `collision-free-candidate.sha256`) are the bridge for the
  removed second tree — both trees generate identical bytes, so the executed result is the same.
- [x] Remove only the two named temporary worktrees after all durable evidence is written. Do not
  remove or alter the current worktree.

### Focused and Optimized Gates

```bash
uv run pytest -q \
  tests/unit/test_constraint_name_safety.py \
  tests/unit/test_predicate_compiler.py \
  tests/unit/test_constraint_emission.py \
  tests/unit/test_cli_generation.py \
  tests/unit/test_contract_models.py \
  tests/conformance/test_constraint_name_safety_routes.py \
  tests/conformance/test_constraint_generation_integration.py

PYTHONOPTIMIZE=1 uv run pytest -q \
  tests/unit/test_constraint_name_safety.py \
  tests/unit/test_predicate_compiler.py \
  tests/unit/test_constraint_emission.py \
  tests/unit/test_cli_generation.py \
  tests/unit/test_contract_models.py \
  tests/conformance/test_constraint_name_safety_routes.py \
  tests/conformance/test_constraint_generation_integration.py
```

- [x] Require both commands to pass. Record that normal mode is primary assertion evidence and the
  optimized run proves production behavior is not implemented with removable assertions.

### Execution Gate

```bash
uv run pytest -q -m execution \
  tests/execution/test_constraint_execution.py -k name_safety_collision_free
```

- [x] Require the exact satisfied/violated node to pass in the configured execution environment.
  If the external execution dependency is unavailable, record the environment failure accurately;
  do not claim the success criterion or substitute a mocked wrapper run. **Passed 2026-07-19**:
  `PYTHONPATH=/home/reid/1cfe/sysml-codegen/src TEAX_SIMKIT_PATH=/home/reid/1cfe/teax/packages/teax-simkit
  /home/reid/1cfe/agentic-mbse/.venv/bin/python -m pytest -q -m execution
  tests/execution/test_constraint_execution.py -k name_safety_collision_free` →
  `1 passed, 14 deselected`. Real TEAx import (pandas 2.3.3 present); no mock. The previously
  blocking `ModuleNotFoundError: pandas` is resolved in this environment.

### Broader and Full Gates

```bash
uv run pytest -q \
  tests/conformance/test_constraint_lowering.py \
  tests/conformance/test_constraint_pipeline_threading.py \
  tests/conformance/test_snapshot_constraint_parity.py \
  tests/conformance/test_snapshot_generation.py \
  tests/conformance/test_fingerprint_stability.py \
  tests/unit/test_snapshot_v3_gate.py \
  tests/unit/test_concrete_constraint_model.py \
  tests/unit/test_constraint_graph_extension.py \
  tests/conformance/test_seal_step9.py \
  tests/unit/test_verify_package.py

uv run pytest tests/
```

- [x] Record exact pass/skip/fail/error counts and license state. Classify inherited full-suite
  failures with evidence; do not call a failing gate green or fix unrelated failures in this item.
- [x] If licensed live/snapshot parity runs, record it separately from the license-free snapshot
  reconstruction proof. Do not silently treat a license skip as parity evidence.

### Static, Diff, and Fixture Gates

```bash
uv run ruff check src/ \
  tests/unit/test_constraint_name_safety.py \
  tests/unit/test_predicate_compiler.py \
  tests/unit/test_constraint_emission.py \
  tests/unit/test_cli_generation.py \
  tests/unit/test_contract_models.py \
  tests/conformance/test_constraint_name_safety_routes.py \
  tests/conformance/test_constraint_generation_integration.py \
  tests/execution/test_constraint_execution.py \
  .project/active/constraint-wave-name-safety/evidence/*.py

uv run ruff format --check \
  src/sysml_codegen/resolution/models.py \
  src/sysml_codegen/analysis/constraint_lowering.py \
  src/sysml_codegen/generation/constraint_name_safety.py \
  src/sysml_codegen/generation/predicate_compiler.py \
  src/sysml_codegen/generation/errors.py \
  src/sysml_codegen/generation/modules.py \
  src/sysml_codegen/generation/pipeline.py \
  src/sysml_codegen/generation/registry.py \
  src/sysml_codegen/contracts/model_contract.py \
  src/sysml_codegen/orchestration/pipeline_context.py \
  src/sysml_codegen/cli/__init__.py \
  tests/unit/test_constraint_name_safety.py \
  tests/unit/test_predicate_compiler.py \
  tests/unit/test_constraint_emission.py \
  tests/unit/test_cli_generation.py \
  tests/unit/test_contract_models.py \
  tests/conformance/test_constraint_name_safety_routes.py \
  tests/conformance/test_constraint_generation_integration.py \
  tests/execution/test_constraint_execution.py \
  .project/active/constraint-wave-name-safety/evidence/*.py

uv run mypy src/
git diff --check -- \
  src/sysml_codegen/resolution/models.py \
  src/sysml_codegen/analysis/constraint_lowering.py \
  src/sysml_codegen/generation/constraint_name_safety.py \
  src/sysml_codegen/generation/predicate_compiler.py \
  src/sysml_codegen/generation/errors.py \
  src/sysml_codegen/generation/modules.py \
  src/sysml_codegen/generation/pipeline.py \
  src/sysml_codegen/generation/registry.py \
  src/sysml_codegen/contracts/model_contract.py \
  src/sysml_codegen/orchestration/pipeline_context.py \
  src/sysml_codegen/cli/__init__.py \
  tests .project/active/constraint-wave-name-safety
git diff -- tests/fixtures
```

- [x] Compare full-project mypy with the recorded 76-error baseline and require no new or changed
  error. Also run targeted mypy on every touched production file and record its exact result.
- [x] Require `git diff --check` clean for Item 2 paths. Review any whole-tree whitespace report by
  path so unrelated dirty work is not misattributed.
- [x] Recompute the sorted fixture SHA-256 manifest and require exact equality with Phase 1. Require
  `git diff -- tests/fixtures` empty; no fixture recapture is allowed.
- [x] Review the final Item-2-only patch against the file list in
  [design.md#component-overview-and-file-level-changes](design.md#component-overview-and-file-level-changes).
  Templates, snapshot codecs/version, catalog schema, general sanitizers, Item 6 files outside the
  two intentional overlaps, and unrelated dirty paths must not enter the patch.
- [x] Confirm no commit, push, PR comment, merge, or other remote action occurred.

**What We Know Works After This Phase:**

All R-3 cases reject deterministically before output mutation, every exercised direct boundary
returns its required structured exception, collision-free packages remain byte-identical, and Item
2 is isolated from Item 6, fixtures, and unrelated dirty work. Exact external execution evidence is
still unavailable because the TEAx import path lacks `pandas` in this environment.

---

## Risk Management

**See:** [design.md#potential-risks](design.md#potential-risks) for the full risk analysis.

- **Carrier disappears during a model copy:** Phase 2 tests copy retention before any policy relies
  on it, and missing provenance fails closed.
- **Excluded metadata leaks into a payload:** Phase 2 pins each dump/schema/contract/fingerprint
  surface locally; Phase 5 adds an exact generated-tree comparison.
- **Inline facts lack qualified identity:** use only the design's honest raw-name fallback. One-sided
  provenance rejects; occurrence identity is never invented.
- **Symbol-table completeness gives false confidence:** production-source checks use two sentinels,
  and the mutation matrix covers every supported binding class and every fail-loud child/declaration
  class.
- **A lower boundary leaks the wrong exception:** one immutable record and centralized formatter are
  asserted across compiler, render, writer, orchestration-log, and process boundaries.
- **A direct writer mutates early:** every writer receives its own absent/populated manifest test;
  `_generate_modules()` additionally stages all constraint source before its first write.
- **Historical evidence imports the wrong checkout:** every process asserts revision and resolved
  paths with user-site and bytecode disabled.
- **Item 2 absorbs Item 6:** pre-item overlap copies/diffs are durable, Item 6's focused selection is
  rerun after CLI edits, and the isolated candidate uses an Item-2-only delta.

## Environment Setup

Use the existing `uv` environment and commands from the repository [CLAUDE.md](../../../CLAUDE.md).
Do not install or upgrade dependencies as part of this item. Licensed live extraction and the real
execution lane are separate evidence legs; record availability and skips precisely.

## Implementation Notes

Fill these sections immediately after each phase. Record actual files, commands, counts, issues,
and deviations; do not rewrite planned checklists to make a deviation disappear.

### Phase 1 Completion

**Completed:** 2026-07-18. The dirty-work firewall, pinned detached worktrees, hashed overlay,
seven independent baseline rejection failures, fixture manifest, and evidence harnesses were
created before production changes.

**Actual Changes:** Added the frozen overlay, generated-tree comparator, execution-control runner,
pre-item status/diff/hash captures, overlap copies, and fixture hashes under `evidence/`.

**Validation Evidence:** Baseline and candidate HEAD were
`512786c7dfab44fba7a0185d09e845b7494c702d`; overlay SHA-256 is
`e4212334fb39537a38280e7dd914bac64a3c2d346157ecfcc431e088bef9ebe7`.
The four reserved-name and three identity/correspondence rejection nodes were independently RED
for the expected missing/unstructured exception reason.

**Issues / Deviations:** The frozen rejection overlay remains unchanged. Audit remediation added a
separate overlay, SHA-256
`f9ce55ab90d213eee882ba6650efcba619d2223025e6889eddafca244a741864`, and ran its four nodes
independently at `512786c`. They reproduced the positive violated `value` margin, `status`
`margin=None`, post-rebinding `verdict` `TypeError`, and duplicate-argument `self` `SyntaxError`.

### Phase 2 Completion

**Completed:** 2026-07-18. The excluded immutable carrier is retained through lowering, graph
extension, snapshot reconstruction, and Pydantic copies without a snapshot/schema version bump.

**Actual Changes:** Added `ConstraintFormalIdentity` and excluded optional fields in the resolution
models. Lowering now creates the richest honest raw/QN identity available before sanitization and
copies it to constraint module inputs. Snapshot codecs, templates, and pipeline builder are
unchanged.

**Validation Evidence:** The carrier/serialization selection passed 70 tests with 15 licensed
skips. Focused and optimized route tests passed. Dumps and the checked snapshot v3 fixture contain
no carrier key; fixture hashes are unchanged.

**Issues / Deviations:** The kept route test proves the license-free snapshot rebuild and deep-copy
path. The plan's larger per-route lowering matrix and separately licensed live parity were not all
added, so those granular boxes remain unchecked rather than overstated.

### Phase 3 Completion

**Completed:** 2026-07-18. Pure two-scope policies, identity correspondence, graph validation,
semantic symbol-table completeness, and normalized direct-boundary exceptions are implemented.

**Actual Changes:** Added the data-only name-safety module; integrated it into predicate compilation,
shared predicate rendering, wrapper rendering, and package error adaptation. Successful argument
and input ordering, templates, and sanitizers are unchanged.

**Validation Evidence:** After audit remediation the focused selection passed 174/174 in normal
mode and 174/174 under `PYTHONOPTIMIZE=1`. Sixteen diagnostic permutations select the same exact
record, and a safe-order control retains `second, first`. Ruff is clean and mypy reports no Item 2
error.

**Issues / Deviations:** The kept symbol-table tests exercise production scopes and fail on an
injected local, but do not contain every binding-form mutation listed in the plan stencil. The
corresponding exhaustive-matrix checkbox remains unchecked.

### Phase 4 Completion

**Completed:** 2026-07-18; independently audited gap remediated the same day. Full graph preflight
now protects all graph renderers, all nine direct CLI writers, and `run_codegen()` before
target-tree mutation, including a constraint module with no catalog. Constraint Python is staged
in memory before module writes.

**Actual Changes:** Added package preflight to pipeline YAML, registry, model contract, writer entry
points, and orchestration. Added absent/populated complete-tree tests and structured log payload
checks. Preserved the pre-item Item 6 CLI and CLI-test hunks.

**Validation Evidence:** The missing-catalog audit probe was RED at the validator, all renderers,
all 18 writer states, and both orchestration states. After the fix, validator/renderer/permutation
coverage passed 23/23 and missing-catalog writer/orchestration coverage passed 20/20. The
overlapping Item 6 selection passed 122 with 2 skipped.

**Issues / Deviations:** No separate `cmd_generate` process assertion was added, and licensed route
parity remains unavailable. The audit-required missing-catalog state is covered at every direct
writer and orchestration state.

### Phase 5 Completion

**Completed:** 2026-07-18 for all license-free implementation and repository evidence. The real
external execution assertion remains unavailable.

**Actual Changes:** Built and checked an Item-2-only production patch, proved the safe generated
tree byte-identical, added the real execution node, wrote `evidence/evidence.md`, and removed the
two detached evidence worktrees after preserving their results.

**Validation Evidence:** Candidate overlay 7/7 GREEN; collision-free baseline/candidate trees are
27-file byte-identical; broader selection 149 passed, 28 skipped; full suite 2,320 passed, 205
skipped, 23 failed, 96 errors, 10 deselected. Full failures/errors are the known Syside-license
families, not Item 2. Ruff passed, planned format paths passed, `git diff --check` passed, mypy
matched its 76-error baseline with no Item 2 error, and fixture hashes matched exactly. The final
Item-2-only patch SHA-256 is
`c8f03e7229b6fd96af952723cb9409b78fde9de0534156d999f81ea2a9fa580e`.

**Issues / Deviations:** The real `x <= limit` node generated its package but TEAx import stopped at
`ModuleNotFoundError: pandas` (1 failed, 9 deselected). Exact satisfied/violated tuples and licensed
live/snapshot parity remained unchecked and unclaimed as of 2026-07-18. `constraint_inline` was
rejected as an invalid safe control because its inherited formal is `value`;
`constraint_multi_instance` supplied the honest byte control.

### Phase 5 execution-gate addendum

**Completed:** 2026-07-19. The `pandas` block is resolved in the agentic-mbse venv, so the two
open Phase 5 execution boxes (plan.md:572-573, 609-611) were closed.

**Environment:** `/home/reid/1cfe/agentic-mbse/.venv/bin/python` (CPython 3.12.3, pandas 2.3.3),
`PYTHONPATH=/home/reid/1cfe/sysml-codegen/src`,
`TEAX_SIMKIT_PATH=/home/reid/1cfe/teax/packages/teax-simkit`. Fresh subprocesses; not mocked. The
codegen venv still lacks pandas — this hosted recipe is the working one (project memory).

**Result:** Pinned execution-gate node `1 passed, 14 deselected`;
`run_collision_free_control.py` wrapper reproduced `1 passed, 14 deselected`. Exact tuples
(captured independently by `capture_collision_free_tuples.py`, saved to
`evidence/collision-free-execution-tuples.txt`): satisfied `(True, 'satisfied', 1.0, {'x': 2.0,
'limit': 3.0})`, violated `(False, 'violated', -1.0, {'x': 4.0, 'limit': 3.0})`. Both equal the
node's asserted values; the generated `predicates.py` carries exactly one predicate def.

**Deviation (one tree):** the baseline/candidate worktrees were already removed after the
byte-identity step, so the control ran once against the current working tree (the byte-identity
candidate). The 27-file byte-identical baseline/candidate manifests are the bridge for the removed
second tree. Licensed live/snapshot parity (design I11) stays out of scope, tracked under Item 8.

---

**Status:** Draft → In Progress → Needs Work → Implementation Complete → Certified (license-free scope) → Complete (execution gate closed 2026-07-19; licensed live/snapshot parity → Item 8)
