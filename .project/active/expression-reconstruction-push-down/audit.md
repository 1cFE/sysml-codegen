# Audit: Expression Reconstruction Push-Down

**Verdict:** Certify
**Audited:** 2026-07-08
**Branch:** push-down-item1-expression
**Commit:** 337d001

---

## Summary

PUSH-DOWN Item 1 delivers the requested cross-repo move. The shared SysML expression helpers now
live in agentic-mbse, sysml-codegen keeps a permanent compatibility shim, and generated fixtures
did not change.

The only residual risks are baseline-tooling issues outside this item: project-wide ruff and
mypy still fail on existing debt. The item-specific lint, tests, suite runs, mypy baseline count,
and byte-identity checks are acceptable.

## Findings

### Plan Completion

All phases are verified complete.

- Phase 0 landing-base gate is recorded in `plan.md`; sysml-codegen started from merged PR #6
  commit `337d001`, and agentic-mbse started from `d582940` with the required companion ancestry.
- Phases 1-2 are implemented in agentic-mbse: shared reconstruction and literal helpers are in
  `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/expression.py:418`, public exports are in
  `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/__init__.py:12`, binding uses
  `extract_literal_value` at `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/binding.py:150`,
  and C7 uses `is_literal_node` at
  `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/validation/level6_architecture.py:783`.
- Phases 3-4 are implemented in sysml-codegen: the compatibility shim is
  `src/sysml_codegen/extraction/expression_utils.py:7`, shim tests are
  `tests/unit/test_expression_utils_shim.py:8`, and codegen-local dispatch inventory excludes
  the moved body at `tests/conformance/test_ast_dispatch_invariant.py:57`.
- Phase 5 is implemented: profile follow-up rules are filed in
  `/home/reid/1cfe/agentic-mbse/.project/backlog/BACKLOG.md:201`.
- Phase 6 is complete with recorded validation and byte-identity proof.

### Spec Conformance

- R1 Behavior Preservation: met. sysml-codegen full suite passed (`2119 passed, 4 skipped`),
  snapshot tests passed (`87 passed`), and `git diff -- tests/fixtures` was empty.
- R2 One-Way Dependency: met. `grep -R -n "sysml_codegen" src tests` in agentic-mbse returned no
  matches.
- R3 Permanent Compatibility: met. `expression_utils.py` remains importable and delegates to
  shared helpers (`src/sysml_codegen/extraction/expression_utils.py:7`).
- R4 Clear Literal Naming: met. agentic-mbse exposes `is_literal_node` while keeping existing
  `is_literal_expression`; sysml-codegen aliases the old name at
  `src/sysml_codegen/extraction/expression_utils.py:24`.
- R5 Checking Profile Closure: met. The filed rows include rule, fixture shape, severity, and
  rationale at `/home/reid/1cfe/agentic-mbse/.project/backlog/BACKLOG.md:201`,
  `/home/reid/1cfe/agentic-mbse/.project/backlog/BACKLOG.md:218`, and
  `/home/reid/1cfe/agentic-mbse/.project/backlog/BACKLOG.md:235`.
- R6 Merged Landing Base: met via Phase 0 evidence in `plan.md`.

All spec success criteria are met. The ruff/mypy criterion is interpreted against the epic anchor:
sysml-codegen source ruff is clean and mypy remains at the planned `97` errors.

### Design Conformance

Implementation follows the design.

- D1 move-by-re-export is followed: callers can still use the sysml-codegen shim, and the shim
  tests pin identity with shared exports at `tests/unit/test_expression_utils_shim.py:8`.
- D2 literal naming is followed: `is_literal_node` is separate from true-static expression tests,
  with explicit coverage in `/home/reid/1cfe/agentic-mbse/tests/test_sysml/test_expression.py:1031`.
- D3 expression-module placement is followed: moved helpers are in
  `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/expression.py:418`.
- D4 profile closure is followed with the filed backlog rows.
- Required invariants are covered: FCE-before-OE and literal/null-before-invocation checks moved
  with the body at `/home/reid/1cfe/agentic-mbse/tests/test_sysml/test_expression.py:1047`, and
  codegen-local dispatch counts remain pinned at
  `tests/conformance/test_ast_dispatch_invariant.py:255`.

### Code Integrity

No certification-blocking issues found.

The sysml-codegen shim is small and compatibility-only. The shared helpers are direct AST
interpretation helpers and do not introduce codegen policy into agentic-mbse. The `str(node)`
fallback in `reconstruct_expression` is inherited behavior and is explicitly tracked as a future
profile warning rather than hidden as accepted validation behavior.

## Certification

Checked:

- agentic-mbse targeted tests: `93 passed`
- agentic-mbse full suite: `1247 passed, 1 skipped, 33 deselected, 6 warnings`
- agentic-mbse touched-file ruff: passed
- agentic-mbse mypy: baseline failure, `104 errors in 21 files`, no remaining moved-helper
  errors
- sysml-codegen focused expression/invariant tests: `70 passed`
- sysml-codegen full suite: `2119 passed, 4 skipped`
- sysml-codegen snapshot tests: `87 passed`
- sysml-codegen `ruff check src/`: passed
- sysml-codegen mypy: baseline failure, `97 errors in 22 files`
- sysml-codegen fixture diff: empty

Marked this item certified. Next stage is pre-PR cleanup and PR preparation.
