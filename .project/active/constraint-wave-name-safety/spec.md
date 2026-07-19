# Spec: Generated Constraint Name-Safety Boundary

**Status:** Certified — all success criteria met, including the real-simkit execution gate (SC-9,
verified 2026-07-19). Licensed live/snapshot parity (design I11) is out of this item's scope and
tracked under Item 8.
**Owner:** Reid W
**Created:** 2026-07-18 19:51 PDT
**Complexity:** MEDIUM
**Branch:** constraint-exec-epic
**Epic:** CONSTRAINT-WAVE-REMEDIATION — Item 2 (R-3)

---

## Problem

Generated constraint code places model-derived formal names into two Python function scopes. The
predicate compiler uses them as parameters beside its own `value` and `status` locals. The wrapper
template uses them as `run` parameters beside `self` and its `verdict` local. The current guard
checks only whether each predicate leaf parameter is a legal Python identifier. Wrapper parameter
names take a separate route through lowering and `sanitize_name()`. Neither route checks its final
bound names against generated bindings, and the package boundary does not prove that the predicate
parameter and wrapper input for one model formal still correspond unambiguously.

The reproduced R-3 cases show four consequences from valid model input. A `value` or `status`
formal silently corrupts margin evidence. A `verdict` formal raises `TypeError` during every run. A
`self` formal produces a duplicate parameter and the emitted module fails to import with
`SyntaxError`. Generation currently accepts all four cases, so failure can surface after source is
emitted or, worse, execution can return plausible but false evidence.

This is an agent-shaped remediation contract derived from reproduced review evidence. Its scope
and choices are not owner-originated settled requirements.

## Success Criteria

- [x] Each `value`, `status`, `verdict`, and `self` regression independently reproduces its
      recorded R-3 failure on sysml-codegen `512786c`. The record identifies the exact revision,
      command, generated scope, and observed corruption or exception; setup failures do not count
      as RED evidence.
- [x] At the candidate revision, the predicate boundary rejects final leaf parameters `value` and
      `status`, and the wrapper boundary rejects final module-input parameters `self` and `verdict`.
      Full generation therefore rejects all four cases before changing the target tree.
- [x] No accepted predicate function has duplicate final leaf parameters or a leaf parameter that
      overlaps a parameter or local bound by the compiled predicate. Repeated references to the
      same model formal remain one parameter and are not treated as a collision.
- [x] No accepted wrapper `run` function has duplicate final module-input parameters or a module
      input that overlaps a parameter or local bound by the wrapper.
- [x] Every accepted predicate parameter maps unambiguously to exactly one wrapper module input for
      the same model formal. Two distinct formal identities cannot be hidden by an equal derived
      name, and disagreement between the predicate name and wrapper name cannot pass through
      name-only reconciliation.
- [x] A kept completeness check covers both generated scopes using structured binding inventories,
      Python AST inspection, or another representation tied to emitted Python bindings. Adding or
      renaming a generated parameter or local without updating the policy makes the check fail.
- [x] Defect-focused tests cover reserved collisions in both scopes, wrapper-name collapse after
      `sanitize_name()`, distinct predicate formal identities that would share one emitted
      parameter, and cross-path disagreement. Results and diagnostics are independent of catalog,
      formal, leaf-traversal, and module-input ordering.
- [x] Rejected orchestration leaves the complete output target unchanged: an absent target remains
      absent, while an existing tree retains the same relative paths, path kinds, symlink targets,
      directory structure, and regular-file bytes. Direct generation APIs perform no write before
      returning the same rejection outcome.
- [x] Collision-free controls generate and import a real constraint module, then execute satisfied
      and violated simple inequalities. They assert the exact `actual_value`, `status`, signed
      margin value, and observed input values for both runs. **Verified 2026-07-19** in the
      agentic-mbse venv (pandas 2.3.3, teax-simkit on `sys.path`): the `x <= limit` package
      generated, imported real TEAx, and executed both runs. Satisfied `(True, 'satisfied', 1.0,
      {'x': 2.0, 'limit': 3.0})`; violated `(False, 'violated', -1.0, {'x': 4.0, 'limit': 3.0})`
      (`evidence/collision-free-execution-tuples.txt`).
- [x] Direct predicate compilation reports predicate-scope collisions as `PredicateCompileError`.
      Package rendering, direct generation, and orchestration report generated-package collisions
      as `CodeGenerationError`. No path falls through to raw `SyntaxError`, `TypeError`, or
      silently corrupted evidence.
- [x] Existing accepted formal names, predicate names, wrapper signatures, pipeline wiring, and
      generated bytes remain unchanged. Focused tests pass normally and under optimized Python.

## Known Requirements

- **[INFERRED]** Use one generated-constraint name-safety policy with separate inventories for the
  two actual Python scopes. The predicate inventory currently reserves `value` and `status`; the
  wrapper inventory currently reserves `self` and `verdict`. Full package generation applies both
  inventories, so the accepted model-formal set is disjoint from their union without pretending
  that both naming paths have one derivation. Source: agent-shaped Epic Item 2, primary review R-3,
  and spec-review L1-2.
- **[INFERRED]** Reject a colliding formal instead of renaming it. Rejection preserves every
  accepted identifier and pipeline interface, avoids a second raw-to-emitted-name mapping, and
  matches the existing fail-fast predicate-function collision policy. The epic permits rejection
  or collision-safe mapping; no owner-originated choice settles either option.
- **[INFERRED]** At the predicate compiler boundary, check the exact leaf `source_name` strings that
  become Python parameters. Equal repeated references to one formal deduplicate normally. Distinct
  model formal identities must never be collapsed into one parameter merely because their final
  `source_name` strings are equal.
- **[INFERRED]** At the wrapper boundary, check the exact `ModuleInput.param_name` strings that
  become `run` parameters after lowering's formal-name derivation. Two distinct source formal
  identities that sanitize to one wrapper parameter are a collision even when the name is not
  reserved.
- **[INFERRED]** At the package boundary, verify a one-to-one correspondence between predicate
  parameters and wrapper inputs by source formal identity, not by equal strings alone. A name
  disagreement for one identity or one emitted name representing multiple identities is rejected.
  This is the narrow cross-path check; it does not change the sanitizer or introduce general
  qualified-name architecture.
- **[INFERRED]** Preserve the richest source identity already available at each boundary. A direct
  compiler diagnostic must contain the predicate function name, final leaf parameter, colliding
  generated binding, and any leaf source identity supplied to the compiler. A package diagnostic
  must additionally contain the constraint ID or usage qualified name and, for every involved
  formal, its raw name and qualified identity when extraction provides them. If those fields would
  otherwise be lost before package preflight, thread only a minimal immutable formal-identity
  record through constraint input/module metadata; do not reconstruct raw identity from a sanitized
  name.
- **[INFERRED]** Run the complete package collision preflight before output clearing, directory
  creation, schema or primitive emission, or any other target-tree mutation. Direct generation
  APIs that can write constraint artifacts perform the same preflight before their first write.
  Direct compiler/render boundaries recheck the scope they can bypass without weakening the
  orchestration no-mutation guarantee.
- **[INFERRED]** Map failures by public boundary. `compile_predicate()` raises
  `PredicateCompileError` for predicate-scope violations. Package render/generation APIs and the
  orchestration preflight raise `CodeGenerationError`, normalizing any lower-level name-safety
  failure while retaining the same structured collision facts. Generated Python never becomes the
  validation mechanism.
- **[INFERRED]** Collision selection and diagnostics are deterministic. Collision records use the
  fixed scope order `predicate`, then `wrapper`; within a scope they sort by final emitted binding
  and then by the richest stable source identity available. The first record in that order is
  reported, and all source identities sharing that collision are listed in the same sorted order.
  Catalog, formal, leaf-traversal, and module-input permutations cannot change the exception type
  or message.
- **[INFERRED]** Derive or verify each reserved inventory against structured emitted bindings. A
  shared structured declaration, Python AST inspection of rendered representative functions, or an
  equivalent semantic check is acceptable. Regex matching, raw string searching, or parsing Jinja
  template/source text is not sufficient because whitespace or template formatting must not define
  Python scope correctness.
- **[INFERRED]** Collision-free generation is byte-stable. This remediation adds no suffixes,
  aliases, sanitizer changes, or user-visible renaming for accepted formals.
- **[INFERRED]** Because this contract selects the epic's permitted rejection option, the four
  colliding candidate modules do not import or execute after the fix. The epic's agent-grade
  criterion is amended conditionally: rejection is GREEN through deterministic pre-mutation
  failure; mapping would have been GREEN through execution of all four names. Collision-free
  controls preserve ordinary post-fix execution under either choice.

## Non-Goals

- General ADR-003 identifier refactoring, qualified-name architecture changes, or changes to
  `sanitize_name()` / `sanitize_qualified_name()`.
- Collision policy for non-constraint templates, module paths, registry classes, channels, schema
  files, or predicate function names already covered by GAP-CLOSE F2.
- User-facing or pipeline-wide renaming of generated constraint formals.
- Changes to executable-profile admission, constraint lowering semantics, Kleene logic, polarity,
  margin rules, or report aggregation.
- Fixes for R-1, R-2, R-4, or any Medium/Low finding from the primary review.
- Production implementation, commits, pushes, PR comments, merges, or other remote-state changes
  during this spec stage.

## Open Questions / Deferred to design

- Choose the exact representation for the two scope inventories and the minimal formal-identity
  metadata threaded to package preflight. The design must not add provenance fields beyond those
  needed for collision correspondence and diagnostics.
- Choose whether completeness uses a shared structured declaration, Python AST inspection, or an
  equivalent semantic check tied to emitted bindings. Regex, raw string search, and Jinja
  template/source parsing are excluded.
- Choose the internal collision record and exception-normalization helper that produce the fixed
  public exception mapping and ordering above without coupling lower-level code to orchestration.
- Define the isolated historical-evidence harness and exact focused normal/optimized commands in
  the implementation plan. The evidence must not modify or reset the dirty worktree.

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_constraint_pr_wave_remediation.md` — Item 2
- **Required Reading:**
  - `.project/research/20260718-192048_constraint-exec-pr-wave-code-review.md` — primary review R-3
  - `src/sysml_codegen/generation/predicate_compiler.py`
  - `src/sysml_codegen/generation/modules.py`
  - `src/sysml_codegen/templates/constraint_module.py.jinja2`
  - `src/sysml_codegen/templates/constraint_predicates.py.jinja2`
  - `.project/active/gap-runtime-contract/spec.md`
  - `.project/active/gap-runtime-contract/design.md`
  - `tests/unit/test_constraint_emission.py`
  - `tests/unit/test_predicate_compiler.py`
  - `tests/conformance/test_constraint_generation_integration.py`
  - `docs/architecture/reference/15-naming-conventions.md`
- **Project State:** `.project/CURRENT_WORK.md`
- **Review:** `.project/active/constraint-wave-name-safety/spec-review.md` — Revise; all must-fix
  findings incorporated in this draft
- **Design:** `.project/active/constraint-wave-name-safety/design.md` (to be created)

---

**Next Steps:** After approval, run `my-spec-review`, then proceed to `my-design`.
