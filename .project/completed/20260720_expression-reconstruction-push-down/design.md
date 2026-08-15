# Design: Expression Reconstruction Push-Down

**Status**: Approved
**Owner**: Reid W
**Created**: 2026-07-08
**Spec**: `.project/active/expression-reconstruction-push-down/spec.md`
**Spec Review**: `.project/active/expression-reconstruction-push-down/spec-review.md`
**Design Review**: `.project/active/expression-reconstruction-push-down/design-review.md`
**Epic**: `.project/backlog/epic_push_down.md`
**Branch**: `truth-debt-epic` (design only; implementation gated)

---

## Overview

Move expression reconstruction from `sysml-codegen` into `agentic_mbse.sysml.expression` as
shared SysML meaning. Keep `sysml_codegen.extraction.expression_utils` as a permanent shim so
existing codegen imports and path-asserting tests keep working.

## Related Artifacts

- Spec: `.project/active/expression-reconstruction-push-down/spec.md`
- Spec review: `.project/active/expression-reconstruction-push-down/spec-review.md`
- Design review: `.project/active/expression-reconstruction-push-down/design-review.md`
- Epic: `.project/backlog/epic_push_down.md`
- Required code: `src/sysml_codegen/extraction/expression_utils.py`,
  `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/expression.py`

## Research Findings

- `src/sysml_codegen/extraction/expression_utils.py:32` owns the reconstruction body today.
  It uses `SysideAdapter.is_instance`, has literal/null dispatch before invocation, and omits
  `extract_feature_chain_segments` from `__all__` at `expression_utils.py:347`.
- `tests/conformance/test_ast_dispatch_invariant.py:57` counts `reconstruct_expression` as one
  of five sysml-codegen dual-check sites. After the move, that body-order invariant belongs in
  agentic-mbse; sysml-codegen keeps only codegen-local dispatch sites.
- `tests/conformance/test_expression_compiler.py:169` separately pins
  `expression_compiler.build_expression_ast`. That remains a sysml-codegen invariant.
- `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/expression.py:257` already uses
  `is_literal_expression` for true-static detection. The moved literal-node predicate needs a
  different name.
- `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/binding.py:187` has the duplicate
  `_extract_literal_value` body that this item should remove.
- `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/validation/level6_architecture.py:779` mirrors
  codegen's literal-node set for C7. That is the first validation rule that should consume the
  shared `is_literal_node`.
- `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/syside_adapter.py:197` maps the moved
  expression, literal, invocation, and null node names. The plan must re-check this because
  `SysideAdapter.is_instance` now raises for unknown live type names.

## Core Concept

Expression reconstruction is a SysML interpretation service. It reads SysML AST nodes and
answers neutral questions: what text does this expression represent, what feature-chain
segments does it contain, and is this node a literal node? sysml-codegen should consume those
answers, but it should not own them. The generated-package policy stays in sysml-codegen; the
shared expression facts move to agentic-mbse where validation can use them before generation.

## Key Bets

1. **The moved helpers are behaviorally pure.**
   If false, moving them could change generated baselines. Mitigation: move the code
   mechanically first, preserve the sysml-codegen shim, and run byte-identity gates.

2. **agentic-mbse can host reconstruction without importing codegen policy.**
   If false, the dependency direction would invert. Mitigation: moved helpers may mention SysML
   AST node facts, but not module names, channel names, entry points, graph resolution, or
   generated artifacts.

3. **Adapter-backed dispatch is available for every moved node type.**
   If false, live SysIDE nodes could raise `ValueError` or silently miss a branch. Mitigation:
   Phase 0 and tests must verify `TYPE_MAP` contains `FeatureChainExpression`,
   `FeatureReferenceExpression`, `OperatorExpression`, `InvocationExpression`,
   `LiteralInteger`, `LiteralRational`, `LiteralBoolean`, `LiteralString`, `LiteralInfinity`,
   and `NullExpression`.

## Key Decisions

### D1 — Move by Re-Export, Not by Bulk Caller Rewrite

Add the shared implementation to `agentic_mbse.sysml.expression`, then replace
`sysml_codegen.extraction.expression_utils` with re-exports. Existing sysml-codegen callers stay
on the shim path first: `usage_extractor.py`, `hierarchy_resolver.py`,
`computed_attribute_extractor.py`, `expression_compiler.py`, and `extractor.py`.

Rejected: rewriting all sysml-codegen callers to import agentic-mbse directly. That would hide
whether the permanent compatibility path still works.

### D2 — Add `is_literal_node`; Do Not Reuse agentic-mbse `is_literal_expression`

`agentic_mbse.sysml.expression.is_literal_expression` currently means "no design attribute
references." The sysml-codegen helper currently means "this AST node is one of the literal or
null node types." Those are different concepts.

The shared API adds `is_literal_node(expr)`. The sysml-codegen shim preserves
`is_literal_expression = is_literal_node`.

Rejected: changing agentic-mbse's existing `is_literal_expression` semantics. That would create
unrelated validation churn.

### D3 — Keep Reconstruction in `agentic_mbse.sysml.expression`

Do not create a new `agentic_mbse.sysml.reconstruction` module for Item 1. The existing
expression module already owns traversal, reference extraction, operator extraction, and static
expression evaluation.

Rejected: splitting early. A split may be useful after aggregation moves, but Item 1 does not
need a second expression namespace.

### D4 — Checking-Profile Closure Is a Pass/Fail Close-Out Gate

The implementation close-out must contain a profile-disposition table. It passes only if every
moved helper is marked `DONE`, `EXISTING`, `NEW RULE`, or `FILED`, and every `FILED` row names a
backlog item with exact rule, fixture shape, severity, and rationale.

Rejected: "file if not cheap." That is not checkable and does not satisfy PUSH-DOWN SC-G.

## Architecture

### Shared Layer

`/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/expression.py` gains the moved
implementation:

- reconstruction: `reconstruct_expression`, `reconstruct_operator_expression`
- feature helpers: `extract_feature_reference_name`, `extract_feature_chain_name`,
  `extract_feature_chain_segments`
- literal helpers: `is_literal_node`, `extract_literal_value`
- precedence helpers: `OPERATOR_MAP`, `RANK`, `UNARY_RANK`, `RIGHT_ASSOC`, `binary_op_of`,
  `needs_parens`

The implementation keeps using `SysideAdapter.is_instance` so real SysIDE nodes and existing
test stubs follow the same dispatch path.

### Compatibility Shim

`src/sysml_codegen/extraction/expression_utils.py` becomes a thin module that imports the
shared helpers and exposes the old names. It must include `extract_feature_chain_segments` in
`__all__`.

The shim owns only compatibility. It must not contain duplicate constants, duplicate helper
bodies, or static body-order logic.

### Public Export Boundary

Package-root exports from `agentic_mbse.sysml.__init__`:

- `reconstruct_expression`
- `reconstruct_operator_expression`
- `extract_feature_reference_name`
- `extract_feature_chain_name`
- `extract_feature_chain_segments`
- `is_literal_node`
- `extract_literal_value`

Submodule-only exports from `agentic_mbse.sysml.expression`:

- `OPERATOR_MAP`
- `RANK`
- `UNARY_RANK`
- `RIGHT_ASSOC`
- `binary_op_of`
- `needs_parens`

Internal names:

- `_is_operator_expression`
- `_is_standard_library_ref`
- any local adapter or test helper introduced during the move

The existing package-root exports for traversal, reference extraction, static-expression
evaluation, and `is_literal_expression` keep their current behavior.

### agentic-mbse Binding

`/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/binding.py` replaces the private
`_extract_literal_value` body with the shared `extract_literal_value` helper. The public
`extract_bindings` behavior does not change.

## Required Invariants

- agentic-mbse does not import `sysml_codegen`.
- sysml-codegen old imports continue to work through `sysml_codegen.extraction.expression_utils`.
- `is_literal_node`, `is_literal_expression`, and `is_true_static_expression` remain distinct
  concepts.
- In the moved `reconstruct_expression` body, `FeatureChainExpression` dispatch stays before
  `OperatorExpression`.
- In the moved `reconstruct_expression` body, literal and null dispatch stays before the
  invocation catch-all.
- sysml-codegen keeps static invariants for codegen-local dispatch sites:
  `expression_compiler.build_expression_ast`, `hierarchy_resolver._walk_aggregation_ast`,
  `usage_extractor._extract_single_binding`, and `parameter_groups._extract_default_value`.
- Full feature-chain segment extraction expands `target_feature.chaining_features`.
- Generated baselines stay byte-identical.

## Static Test Migration

agentic-mbse owns moved implementation-body invariants:

- Add tests under `/home/reid/1cfe/agentic-mbse/tests/test_sysml/` that statically inspect
  `agentic_mbse.sysml.expression.reconstruct_expression` for FCE-before-OE ordering.
- Add tests that statically inspect the same body for literal/null-before-invocation ordering.
- Add behavioral dual-match stub tests for `reconstruct_expression`.

sysml-codegen owns codegen-local dispatch invariants:

- Remove `expression_utils.py:reconstruct_expression` from sysml-codegen's static dual-check
  inventory and count.
- Keep `expression_compiler.build_expression_ast`,
  `hierarchy_resolver._walk_aggregation_ast`, `usage_extractor._extract_single_binding`, and
  `parameter_groups._extract_default_value` in the sysml-codegen invariant inventory.
- Keep behavioral tests that call `reconstruct_expression` through the shim. Those prove the
  old import path still reaches the shared implementation.

sysml-codegen shim tests:

- Import every name in `expression_utils.__all__`.
- Assert `extract_feature_chain_segments` is present in `__all__`.
- Assert `is_literal_expression is is_literal_node` through the shim.
- Assert selected shim exports are identical objects to `agentic_mbse.sysml.expression` exports.

## Checking-Profile Disposition

The close-out table is a pass/fail artifact. These are the required rows and default
dispositions:

| Helper | Disposition | Rule / backlog item | Fixture shape | Severity | Rationale |
|---|---|---|---|---|---|
| `is_literal_node` | NEW RULE | Rule: Level-6 C7 `L6_ATTR_REDEF_EXPR_DROPPED` warns when an AttributeUsage redefinition RHS is not `is_literal_node` | `attribute :>> attr = a + b` warns; `attribute :>> attr = 1`, string, boolean, infinity, and null do not warn | WARNING | Replaces the local literal mirror with the shared codegen-compatible literal-node fact. |
| `extract_literal_value` | EXISTING | `agentic_mbse.sysml.binding.extract_bindings` literal binding value extraction | `CalculationUsage` member bound to numeric, string, boolean, infinity, and null literal nodes | N/A | Removes duplicate implementation; no new validation policy. |
| `extract_feature_chain_segments` | FILED | `PUSH-DOWN-EXPR-PROFILE-CHAIN-SEGMENTS`: reject a codegen-compatible profile chain if full segment extraction is empty, lossy, or uses an unsupported anonymous segment | `a.b.c` chain where `target_feature.name is None` and `target_feature.chaining_features == [b, c]` | ERROR | Codegen-compatible profile should reject unsupported or lossy chain shapes before generation, but wiring the profile needs fixture work beyond the move. |
| `extract_feature_chain_name` | EXISTING | Existing reference-name messaging and binding source-path extraction | `part.attr` FeatureChainExpression with operand root plus target feature name | N/A | Existing codegen behavior is preserved through the shared helper. |
| `extract_feature_reference_name` | EXISTING | Existing expression compiler and hierarchy reference-name extraction | FeatureReferenceExpression using referent, membership fallback, declared name, and name fallback | N/A | Existing codegen behavior is preserved through the shared helper. |
| `reconstruct_expression` | FILED | `PUSH-DOWN-EXPR-PROFILE-UNSUPPORTED-SHAPE-MESSAGE`: warn when codegen-compatible validation sees an expression shape that reconstructs only through the opaque `str(node)` fallback | unsupported anonymous expression form that reconstructs only via `str(node)` | WARNING | Validation should produce clearer codegen-compatible diagnostics when reconstruction falls back to opaque text. |
| `reconstruct_operator_expression` | FILED | `PUSH-DOWN-EXPR-PROFILE-UNSUPPORTED-OPERATOR`: error when a codegen-targeted expression uses an operator outside the supported operator set | OperatorExpression with an operator outside the codegen-supported set, plus supported `+`, `-`, `*`, `/`, comparisons, `and`, `or`, `not` controls | ERROR | agentic-mbse should flag operators codegen cannot compile before generation. |
| `OPERATOR_MAP`, `RANK`, `UNARY_RANK`, `RIGHT_ASSOC`, `binary_op_of`, `needs_parens` | EXISTING | agentic-mbse reconstruction and precedence tests | nested binary, unary, right-associative power, and n-ary operator stubs | N/A | These are implementation support for reconstruction, not standalone profile rules. |

If implementation changes any row, the close-out must explain why and keep the same fields.
`FILED` rows must be added to the agentic-mbse backlog before the item closes.

## Implementation Gate

The implementation plan must start with Phase 0. Phase 0 is complete only after it records:

- the selected sysml-codegen landing base commit or branch;
- proof that the selected sysml-codegen base contains merged `truth-debt-epic`;
- the selected agentic-mbse landing base commit or branch;
- proof that agentic-mbse `upstream-findings-sync` is merged;
- proof that agentic-mbse `pipeline-truth-item4` is merged;
- the current merged truth-debt status and the two merged agentic-mbse companion statuses in
  `plan.md`.

No code edit may happen before Phase 0 is checked off. Design and planning may proceed on the
current branch; implementation may not.

## Adapter-Dispatch Precondition

Before moving code, agentic-mbse tests must verify the adapter can resolve every type name used
by the moved helpers:

- expressions: `FeatureChainExpression`, `FeatureReferenceExpression`, `OperatorExpression`,
  `InvocationExpression`
- literals: `LiteralInteger`, `LiteralRational`, `LiteralBoolean`, `LiteralString`,
  `LiteralInfinity`
- null: `NullExpression`

This can be a direct `SysideAdapter.get_type(name)` / `_get_type_map()` test in the live path
and mock fallback tests for license-free unit coverage. The literal and null names are
load-bearing because C7 and reconstruction both depend on them.

## Non-Goals

- No Python expression compiler move.
- No binding classification move.
- No CalcUsage extraction move.
- No aggregation decomposition move.
- No direct generated-artifact naming or channel policy in agentic-mbse.
- No baseline recapture unless an unexpected diff reveals a real behavior change.

## Implementation Notes

- Start with the pre-flight `extract_feature_chain_segments` export and test before moving code.
- Move code mechanically first. Rename only the literal predicate during the move.
- Keep compatibility aliases in one place: the sysml-codegen shim.
- Do not clean up sysml-codegen callers to import agentic-mbse directly in the same pass. The
  old import path is the contract.
- Do not widen `is_literal_type`; it remains local support for static-expression evaluation
  unless a later cleanup proves it can be retired.

## Potential Risks

- **Half-migrated editable installs.** A green sysml-codegen tree may depend on an unmerged local
  agentic-mbse checkout. Mitigation: Phase 0 records bases, and implementation lands the
  agentic-mbse move before switching the sysml-codegen shim.
- **False static coverage.** sysml-codegen tests could keep parsing the shim and count no real
  body. Mitigation: move body-order checks to agentic-mbse and replace shim inspection with
  import/export/alias checks.
- **Validation drift.** C7 could keep a private literal list after the shared helper exists.
  Mitigation: make `is_literal_node` a required `NEW RULE` row, not an optional cleanup.

## Integration Strategy

The move is a cross-repo pair:

1. Add shared helpers and tests in agentic-mbse.
2. Switch agentic-mbse binding and C7 to the shared helpers.
3. Convert sysml-codegen `expression_utils.py` to a permanent shim.
4. Adjust sysml-codegen tests to prove compatibility and keep codegen-local invariants.
5. Run both suites and byte-identity gates.

The dependency direction remains:

```text
sysml-codegen -> agentic-mbse.sysml -> syside
```

## Validation Approach

agentic-mbse:

- reconstruction, precedence, literal-node, literal-value, and chain-segment unit tests;
- moved static invariants for `reconstruct_expression`;
- C7 tests covering expression RHS warning and literal/null non-warning cases;
- adapter TYPE_MAP coverage for moved type names;
- full test suite, ruff, and mypy.

sysml-codegen:

- shim import/export/alias tests;
- existing unit tests that import through `sysml_codegen.extraction.expression_utils`;
- static invariants for codegen-local dispatch only;
- full test suite, ruff, and mypy;
- generated baselines byte-identical.

## Next-Stage Handoff

Fixed for planning:

- target module is `agentic_mbse.sysml.expression`;
- sysml-codegen `expression_utils.py` is a permanent shim;
- `is_literal_node` is the shared literal-node predicate;
- package-root exports are the seven public helpers listed above;
- precedence helpers are submodule-only;
- Phase 0 merge-status recording is mandatory before any code edit;
- profile-disposition close-out is pass/fail and must include named backlog rows for filed
  rules.

Open for planning:

- exact agentic-mbse backlog file name for `PUSH-DOWN-EXPR-PROFILE-CHAIN-SEGMENTS` and
  `PUSH-DOWN-EXPR-PROFILE-UNSUPPORTED-SHAPE-MESSAGE`;
- whether `PUSH-DOWN-EXPR-PROFILE-UNSUPPORTED-OPERATOR` can be implemented cheaply in Item 1
  instead of filed. If it is filed, the table fields above are mandatory.

---

Next Step: after design approval, use `$my-plan`.
