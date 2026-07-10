# Design Review: Expression Reconstruction Push-Down

**Design:** `.project/active/expression-reconstruction-push-down/design.md`
**Spec:** `.project/active/expression-reconstruction-push-down/spec.md`
**Review File:** `.project/active/expression-reconstruction-push-down/design-review.md`
**Date:** 2026-07-08

---

## Fundamental Assessment

Sound.

The revised design is ready for planning. The core architecture is still the right one:
move reusable SysML expression facts into `agentic_mbse.sysml.expression`, keep generation
policy in sysml-codegen, and preserve `sysml_codegen.extraction.expression_utils` as a
permanent shim.

The prior must-fix findings are resolved. The remaining open items are planning details,
not design blockers.

---

## Dimensional Review

### 1. Spec Compliance

**Assessment:** Pass

The design satisfies the approved spec:

- The shared API surface covers reconstruction, precedence helpers, feature references,
  feature chains, full chain segments, literal-node detection, and literal-value extraction.
- The sysml-codegen module remains a permanent compatibility shim.
- `is_literal_node` is added without changing agentic-mbse's existing
  `is_literal_expression` semantics.
- `agentic_mbse.sysml.binding` is explicitly switched from its private literal extractor to
  the shared helper.
- The implementation gate is carried into the design as a mandatory Phase 0 gate.
- The checking-profile disposition is now a pass/fail close-out artifact.

The prior checking-profile gap is closed. The design names each helper's disposition and, for
filed rules, gives a rule identifier, fixture shape, severity, and rationale:

- `PUSH-DOWN-EXPR-PROFILE-CHAIN-SEGMENTS`
- `PUSH-DOWN-EXPR-PROFILE-UNSUPPORTED-SHAPE-MESSAGE`
- `PUSH-DOWN-EXPR-PROFILE-UNSUPPORTED-OPERATOR`

The C7 close-out is also concrete: Level-6 `L6_ATTR_REDEF_EXPR_DROPPED` must use
`is_literal_node`, with expression-warning and literal/null non-warning fixture shapes.

### 2. Pattern Consistency

**Assessment:** Pass

The design follows the repo's established push-down pattern: add the shared implementation in
agentic-mbse, keep sysml-codegen callers on the permanent shim path, and use tests to prove
both the new shared behavior and the old import contract.

The prior static-test migration gap is resolved. The split is now explicit:

- agentic-mbse owns the moved `reconstruct_expression` body-order invariants;
- sysml-codegen keeps codegen-local dispatch invariants for `expression_compiler`,
  `hierarchy_resolver`, `usage_extractor`, and `parameter_groups`;
- sysml-codegen shim tests verify import/export/alias identity instead of parsing a moved
  implementation body.

### 3. Abstraction Quality

**Assessment:** Pass

The design keeps the abstraction small. It extends the existing
`agentic_mbse.sysml.expression` module instead of introducing a new reconstruction namespace.
That is the simplest shape that satisfies the spec.

The `is_literal_node` name earns its place because it separates literal AST-node detection from
agentic-mbse's existing true-static expression predicate.

### 4. Duplication Avoidance

**Assessment:** Pass

The design removes the duplicate literal-value helper in `agentic_mbse.sysml.binding` and
prevents a second reconstruction implementation by turning sysml-codegen's module into a
re-export shim.

The shim boundary is clear: it owns compatibility names only, not duplicate constants or helper
bodies.

### 5. Data Structure Clarity

**Assessment:** Pass

This design mostly moves functions, not data models. The public API boundary is now
deterministic:

- package-root exports from `agentic_mbse.sysml.__init__` are the seven listed public helpers;
- precedence constants and support helpers remain submodule-only;
- local adapter/test helpers and private checks remain internal.

That is enough for a plan to pin imports and for tests to detect accidental API drift.

### 6. Route Safety

**Assessment:** Pass

No routes or endpoints are involved.

The import-path equivalent is safe: sysml-codegen keeps an explicit compatibility path, and
agentic-mbse remains free of sysml-codegen imports.

### 7. Bets & Decisions Integrity

**Assessment:** Pass

The design's bets are now honest and testable. The previously hidden adapter-dispatch bet is
surfaced as a key bet and a pre-move test target. The design names every type that must resolve
through `SysideAdapter`:

- `FeatureChainExpression`
- `FeatureReferenceExpression`
- `OperatorExpression`
- `InvocationExpression`
- `LiteralInteger`
- `LiteralRational`
- `LiteralBoolean`
- `LiteralString`
- `LiteralInfinity`
- `NullExpression`

This matches the current agentic-mbse adapter direction, where unmapped live type names raise
rather than silently no-op.

The key decisions also state rejected alternatives, especially the choice to re-export through
the shim instead of rewriting sysml-codegen callers directly.

### 8. Reader Comprehension

**Assessment:** Pass

The design gives the reader the mental model before the mechanism: expression reconstruction is
a SysML interpretation service, while codegen consumes the facts and keeps generation policy.

The revised gate, API boundary, profile-disposition table, and static-test migration are easy
to find. No wording issue blocks implementation planning.

---

## Issues by Severity

### Critical

- None.

### Major

- None.

### Minor

- The exact agentic-mbse backlog file location for the filed expression-profile rules is still
  open for planning. This is not a design blocker because the filed rule IDs, fixture shapes,
  severities, and rationales are already specified.
- Planning should decide whether `PUSH-DOWN-EXPR-PROFILE-UNSUPPORTED-OPERATOR` is cheap enough
  to implement in Item 1. If not, the design already defines the mandatory filed-rule fields.

---

## Recommendations

1. In `$my-plan`, make Phase 0 the first checkbox and prohibit code edits until it records the
   selected sysml-codegen base, merged `truth-debt-epic`, merged agentic-mbse
   `upstream-findings-sync`, and merged agentic-mbse `pipeline-truth-item4`.
2. Keep the profile-disposition table as a close-out gate. Do not close Item 1 unless every row
   is `DONE`, `EXISTING`, `NEW RULE`, or `FILED`, and every `FILED` row exists in the
   agentic-mbse backlog with the design's fields.
3. In the plan, treat the static invariant migration as cross-repo work, not as a sysml-codegen
   test deletion. The moved body-order invariant must land beside the moved implementation.

---

## Resolutions

- **Checking-profile closure:** Resolved. The design now defines a pass/fail
  profile-disposition table with named rules, fixture shapes, severities, and rationales.
- **Phase 0 implementation gate:** Resolved. The design now requires a plan-checkable Phase 0
  that records selected landing bases and merged prerequisite status before any code edit.
- **Static invariant migration:** Resolved. The design splits moved implementation invariants
  into agentic-mbse and keeps codegen-local dispatch invariants in sysml-codegen.
- **Public export boundary:** Resolved. The design now lists package-root exports,
  submodule-only exports, and internal names.
- **Adapter-dispatch / TYPE_MAP precondition:** Resolved. The design states the load-bearing
  adapter bet and requires pre-move coverage for every moved type name.

---

**Overall:** Approve
**Next Steps:** Proceed to `$my-plan`. Carry the Phase 0 gate, profile-disposition close-out,
static-test migration, public export boundary, and TYPE_MAP precondition into the plan.
