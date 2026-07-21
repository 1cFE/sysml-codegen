# Item 2 Implementation Evidence

**Scope:** CONSTRAINT-WAVE Item 2 / R-3 only  
**Baseline and candidate HEAD:** `512786c7dfab44fba7a0185d09e845b7494c702d`  
**Outcome:** independently certified for the license-free scope. The licensed real-execution leg is
unavailable and remains unclaimed.

## Pre-item state and isolation

- The pre-item status, binary diff, HEAD, dirty-file hashes, overlap copies/diffs, and fixture
  manifest are under `evidence/pre-item/`.
- The frozen overlay SHA-256 is
  `e4212334fb39537a38280e7dd914bac64a3c2d346157ecfcc431e088bef9ebe7`.
- The separate baseline historical-impact overlay SHA-256 is
  `f9ce55ab90d213eee882ba6650efcba619d2223025e6889eddafca244a741864`.
- The final Item-2-only production patch is `evidence/item2-production.patch`, SHA-256
  `c8f03e7229b6fd96af952723cb9409b78fde9de0534156d999f81ea2a9fa580e`.
- `git apply --check` passed against the detached baseline. `git diff --check` passed in the
  detached candidate. The patch contains exactly these production paths:
  `resolution/models.py`, `analysis/constraint_lowering.py`,
  `generation/constraint_name_safety.py`, `generation/predicate_compiler.py`,
  `generation/errors.py`, `generation/modules.py`, `generation/pipeline.py`,
  `generation/registry.py`, `contracts/model_contract.py`,
  `orchestration/pipeline_context.py`, and `cli/__init__.py`.
- The detached candidate CLI contains Item 2's `_preflight_constraint_names` and contains none of
  Item 6's `ensure_package_tree_is_link_free` hunks. The live CLI still contains all four Item 6
  call/import regions. Comparing the live CLI and CLI tests with their pre-item copies shows only
  Item 2 additions, so the certified Item 6 hunks remain byte-for-byte present.

## Historical RED and candidate GREEN

The identical frozen overlay ran in fresh processes with user-site and bytecode disabled. Each
process asserted HEAD and the imported `sysml_codegen`, predicate compiler, module renderer, and
lowering paths.

- Baseline: the four reserved-name cases failed because no public exception was raised. The two
  identity-collapse cases also failed because no public exception was raised. The cross-path case
  reached the old unstructured package error with no name-safety payload.
- Candidate: all seven rejection cases passed with the required public exception and structured
  violation. The candidate no-mutation nodes passed for absent and populated roots.
- The original rejection overlay remains byte-identical. A separate final-hash impact overlay ran
  each node independently against detached baseline `512786c`: `value=4, limit=3` returned a
  violated result with the wrongly positive margin `3.0`; `status=4, limit=3` returned a simple
  violated inequality with `margin=None`; the exact rendered `verdict` wrapper reached
  `float(verdict)` after local rebinding and raised `TypeError`; compiling the exact rendered
  `def run(self, self: float, ...)` source raised duplicate-argument `SyntaxError`.

## Carrier and serialization proof

- The retained `ConstraintFormalIdentity` is immutable and excluded from Pydantic dumps. Lowering
  constructs it from existing definition, default, inline, and defensive facts before
  sanitization, and graph extension retains it on constraint module inputs.
- Kept route tests prove snapshot reconstruction, graph-copy retention, absent-QN raw fallback,
  unsafe-graph equality, and omission from dumps, model/package contracts, fingerprints, and
  snapshot payload/version. No snapshot codec, template, or schema version changed.
- The broader carrier/serialization selection passed: **70 passed, 15 skipped**. Skips were the
  separately marked licensed live legs.

## Pure policy and boundary proof

- Predicate policy reserves `value` and `status`; wrapper policy reserves `self` and `verdict`.
  The shared pure module validates identity-to-binding correspondence and graph joins, selects and
  formats violations deterministically, and verifies emitted scopes with Python `symtable`.
- Direct predicate compilation returns `PredicateCompileError`. Package render paths normalize to
  `CodeGenerationError`, retain the exact structured record, and preserve compiler exceptions as
  `__cause__`.
- Accepted predicate argument and wrapper input order remain unchanged. The templates and general
  sanitizer are unchanged.

## Renderer and writer boundary proof

| Boundary | Kept evidence | First protected action |
|---|---|---|
| predicate compiler | predicate compiler reserved-name/payload tests | body/source construction |
| shared predicate and wrapper render | constraint emission tests | source return |
| pipeline YAML | unsafe graph contract/render tests | context projection |
| registry | unsafe graph contract/render tests | registry projection |
| model contract | contract model unsafe-graph tests | fingerprint/projection |
| nine direct CLI writers | reserved-name matrix (18) plus missing-catalog matrix (18) | any path mutation/read-for-regeneration |
| `run_codegen()` | four reserved names (8) plus missing catalog (2), each absent/populated | link check, clear, or setup |

The audit reproduction was RED at the direct validator, all three renderers, all 18 direct-writer
states, and both orchestration states. After the localized fix, the validator/renderer/permutation
selection passed **23/23** and the missing-catalog writer/orchestration selection passed **20/20**.
A constraint-free graph with no catalog remains valid. Every missing-catalog rejection carries the
deterministic structured `catalog_module_join` record for `c1`. `_generate_modules()` still stages
predicate and wrapper source in memory before creating a directory or writing a file. The
overlapping Item 6 selection passed **122 passed, 2 skipped**.

Permutation coverage runs all 16 combinations of catalog entry order, catalog formal order,
predicate-leaf order, and wrapper module-input order. Every combination selects this exact
diagnostic:

`Constraint name-safety violation: constraint_id='C1', usage_qualified_name='Pkg::C1': scope='predicate', kind='binding_identity_collision', final_binding='x'; identities=[raw_name='x', qualified_name='A::x', raw_name='x', qualified_name='B::x']`

A separate safe control pins predicate arguments as `second, first`, proving diagnostic sorting
does not reorder a successful signature.

## Collision-free byte and execution controls

- Baseline and Item-2-only candidate generated `constraint_multi_instance` from the same absolute
  input and package name. `compare_generated_trees.py` found **27 files in each tree and no path,
  kind, symlink-target, or byte difference**.
- `constraint_inline` was not used as the safe control after inspection showed its inherited
  `value` formal is exactly an R-3 rejection case. The fixed safe control is
  `constraint_multi_instance`; no provenance was invented.
- The real execution node generated the `x <= limit` package, then failed during the external TEAx
  import with `ModuleNotFoundError: pandas`: **1 failed, 9 deselected**. The satisfied/violated
  tuples therefore remained unclaimed at audit time. No mock was substituted.
  **Update 2026-07-19: this leg is now executed and green** — see "Execution gate (2026-07-19)".

## Test gates

- Audit-remediated focused Item 2 selection, normal: **174 passed**.
- Audit-remediated focused Item 2 selection, `PYTHONOPTIMIZE=1`: **174 passed** (one expected pytest warning about
  assertions outside test modules under `-O`).
- Independent post-annotation import/name-safety/CLI check reported by the stage input: **42/42**.
- Broader 177-node selection after correcting the inherited `constraint_inline` expectation:
  **149 passed, 28 skipped**.
- Full repository suite with the localized validator fix:
  `UV_CACHE_DIR=/tmp/sysml-codegen-uv-cache uv run pytest`: **2,654 collected, 10 deselected,
  2,644 selected; 23 failed, 2,320 passed, 205 skipped, 96 errors**.
- The full-suite failures/errors are confined to the repository's known Syside-license-dependent
  live extraction and downstream fixture families. The Item 2 tests do not fail. This is a
  classified failing repository gate, not a green full-suite claim.

## Static, diff, fixture, and scope gates

- Ruff passed for `src/`, every Item 2 test, and the evidence scripts. The frozen overlay has a
  narrow `I001` per-file exemption so its executed hash is not changed.
- Ruff format passed for the 22 planned Item 2 paths after excluding the frozen overlay. The
  additionally touched `test_module_kind_faildloud.py` is not formatted at HEAD either; its Item 2
  hunk only adds carrier facts and was left unformatted to avoid unrelated churn.
- Full mypy remains the recorded baseline: **76 errors in 17 files (64 source files checked)**,
  with no Item 2 error. Targeted mypy followed imports and reported **74 inherited errors in 16
  files**, with none in a named Item 2 module.
- `git diff --check` is clean for all Item 2 source, tests, and artifacts.
- The recomputed sorted fixture SHA-256 manifest is byte-identical to the pre-item manifest, and
  `git diff -- tests/fixtures` is empty.
- No template, snapshot codec/version, catalog schema, general sanitizer, Item 4 file, commit,
  push, PR, merge, or remote action is part of Item 2.

## Execution gate (2026-07-19)

The previously-blocking dependency is now available, so the real-simkit execution leg was run.

- **Environment.** Fresh subprocesses hosted in the agentic-mbse venv
  (`/home/reid/1cfe/agentic-mbse/.venv/bin/python`, CPython 3.12.3, pandas 2.3.3) with
  `PYTHONPATH=/home/reid/1cfe/sysml-codegen/src` and
  `TEAX_SIMKIT_PATH=/home/reid/1cfe/teax/packages/teax-simkit`. Not mocked. The codegen venv still
  lacks pandas; this recipe is the working one recorded in project memory.
- **Pinned execution-gate node.**
  `python -m pytest -q -m execution tests/execution/test_constraint_execution.py -k name_safety_collision_free`
  → **1 passed, 14 deselected** (node `test_name_safety_collision_free_exact_evidence`). The
  `run_collision_free_control.py` wrapper, run as its own fresh subprocess, produced the same
  **1 passed, 14 deselected**.
- **Exact tuples** (`(actual_value, status, margin, observed)`), captured independently by
  `capture_collision_free_tuples.py` (a fresh subprocess reusing the node's production generation +
  real-simkit run helpers) and saved to `collision-free-execution-tuples.txt`:
  - Satisfied (`x=2.0, limit=3.0`): `(True, 'satisfied', 1.0, {'x': 2.0, 'limit': 3.0})`.
  - Violated (`x=4.0, limit=3.0`): `(False, 'violated', -1.0, {'x': 4.0, 'limit': 3.0})`.
  Both equal the node's asserted values. The generated `predicates.py` carries exactly one
  `def constraint_pred_`; no colliding-name mapping/alias is emitted.
- **One-tree deviation.** The plan phase ran the control against the baseline and candidate
  worktrees, both removed after the byte-identity step. The control ran once against the current
  working tree (the byte-identity candidate); the 27-file byte-identical baseline/candidate
  manifests are the bridge for the removed second tree — both trees emit identical bytes, so the
  baseline result is the same bytes executed here.

This closes spec SC-9 and the epic Item 2 execution success criterion. Licensed live/snapshot
parity (design I11) stays out of this item's scope and is tracked under Item 8.

## Remaining unavailable evidence

The real collision-free execution leg above is now complete. What remains outside this item is the
licensed Syside live lowering and live/snapshot parity (design I11), which requires a Syside
license unavailable in this environment and is tracked under Item 8. The license-free
implementation, byte proof, execution gate, and all Item 2-focused gates are complete.
