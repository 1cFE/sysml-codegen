# Specification: Expression Reconstruction Push-Down

**Status**: Approved
**Owner**: Reid W
**Epic**: PUSH-DOWN
**Item**: 1 — Expression Reconstruction Push-Down
**Created**: 2026-07-08
**Complexity**: HIGH
**Branch**: `truth-debt-epic` (spec only; implementation gated)

---

## Summary

Move reusable SysML expression reconstruction, feature-chain, chain-segment, and literal-node
helpers from `sysml-codegen` into `agentic_mbse.sysml.expression`, while keeping
`sysml_codegen.extraction.expression_utils` as a permanent compatibility shim.

The purpose is not to change generation behavior. It is to move SysML meaning into the shared
SysML layer so validation, docs, and future tools can use the same expression facts that
codegen relies on. The generated baselines should remain byte-identical.

---

## Current State

`src/sysml_codegen/extraction/expression_utils.py` owns the reusable reconstruction surface:

- `reconstruct_expression`
- `reconstruct_operator_expression`
- `extract_feature_reference_name`
- `extract_feature_chain_name`
- `extract_feature_chain_segments`
- `is_literal_expression`
- `extract_literal_value`
- precedence helpers and operator maps

This file is pure SysML AST handling. It imports only `SysideAdapter` from agentic-mbse and
does not need codegen-specific models.

One public-surface bug exists before the move: `extract_feature_chain_segments` is used by
codegen callers but is missing from `expression_utils.__all__`. The implementation must export
and pin it before migration so the compatibility contract is explicit.

`agentic_mbse.sysml.expression` already owns related traversal and static-expression helpers:

- `traverse_expression`
- `extract_feature_refs`
- `extract_operators`
- `is_literal_expression` meaning "true static expression", not "literal node"
- `evaluate_true_static_expression`
- `is_true_static_expression`

`agentic_mbse.sysml.binding` has a duplicate private `_extract_literal_value` helper. This item
should fold that duplicate into the shared expression API.

---

## Problem

The current boundary forces shared SysML expression knowledge to live in `sysml-codegen`.
That blocks two things:

1. agentic-mbse cannot reconstruct expression text, extract full feature-chain segments, or
   classify literal nodes without depending on sysml-codegen or duplicating logic.
2. agentic-mbse cannot enforce the codegen-compatible expression profile from the same facts
   that generation uses.

The architectural dependency must stay one-way:

```text
sysml-codegen -> agentic-mbse.sysml -> syside
```

agentic-mbse may define a codegen-compatible validation profile as a contract over SysML facts.
It must not import sysml-codegen.

---

## Scope

### In Scope

1. Pre-flight export:
   - Add `extract_feature_chain_segments` to `sysml_codegen.extraction.expression_utils.__all__`.
   - Add or move a test that fails if the helper is not exported.

2. Shared expression API:
   - Move reconstruction helpers into `agentic_mbse.sysml.expression`.
   - Preserve behavior and names where they are already public.
   - Introduce `is_literal_node` for the literal-node predicate currently named
     `is_literal_expression` in sysml-codegen.
   - Keep `is_literal_expression` as a compatibility alias in the sysml-codegen shim.

3. Literal helper consolidation:
   - Move `extract_literal_value` into the shared API.
   - Replace `agentic_mbse.sysml.binding._extract_literal_value` with the shared helper.

4. Compatibility:
   - Keep `sysml_codegen.extraction.expression_utils` as a permanent shim.
   - Preserve old import paths used by codegen and conformance tests.
   - Do not remove path-asserted files.

5. Tests:
   - Move or duplicate the relevant INV-1 dispatch-totality coverage next to the shared code.
   - Keep sysml-codegen compatibility tests for the shim path.
   - Preserve tests for precedence-aware reconstruction, literal dispatch, and full chain
     segment extraction.

6. Checking profile:
   - Decide which expression-profile checks are now enabled by the shared API.
   - Implement the cheap checks in agentic-mbse or file explicit backlog items with rule,
     fixture shape, severity, and rationale.
   - Candidate checks:
     - unsupported operator in codegen-compatible expressions;
     - anonymous or unsupported expression forms where generation cannot build a channel;
     - full feature-chain segment support for allowed chain shapes;
     - literal-node classification used by redefinition/binding checks.

### Out of Scope

- Python expression compilation in `sysml_codegen.extraction.expression_compiler`.
- Binding classification policy.
- CalcUsage extraction.
- Graph resolution or aggregation decomposition. Item 4 owns aggregation push-down.
- Any generated artifact rename or baseline recapture.

---

## Requirements

### R1 — Behavior Preservation `[HARD]`

All moved helpers must produce the same results as the current sysml-codegen implementation for
the committed fixtures and unit stubs. Generated baselines must remain byte-identical.

### R2 — One-Way Dependency `[HARD]`

sysml-codegen may import shared expression helpers from agentic-mbse. agentic-mbse must not
import sysml-codegen.

### R3 — Permanent Compatibility `[HARD]`

`sysml_codegen.extraction.expression_utils` remains importable. The module becomes a shim, not
a temporary migration file.

### R4 — Clear Literal Naming `[NEED]`

The shared API must distinguish:

- literal-node detection: `is_literal_node`
- true-static-expression detection: existing `is_true_static_expression`
- compatibility alias: `sysml_codegen.extraction.expression_utils.is_literal_expression`

This avoids overloading the agentic-mbse `is_literal_expression` name, which currently means
"no design attribute references."

### R5 — Checking Profile Closure `[NEED]`

The item must leave a recorded expression-profile validation disposition. Each newly shared
helper either powers an existing check, adds a check, or files a named backlog item with the
exact rule and fixture shape.

### R6 — Merged Landing Base Before Implementation `[HARD]`

Implementation must not begin from an unmerged truth-debt or agentic-mbse branch stack. Before
any PUSH-DOWN Item 1 implementation work starts, `truth-debt-epic` must be merged to the
selected landing base for sysml-codegen, and agentic-mbse `upstream-findings-sync` plus the
`pipeline-truth-item4` companion must both be merged in agentic-mbse.

---

## Success Criteria

- [x] Implementation began only after the selected sysml-codegen landing base contained the
  merged `truth-debt-epic`, and agentic-mbse contained merged `upstream-findings-sync` plus
  merged `pipeline-truth-item4`.
- [x] `extract_feature_chain_segments` is exported before and after migration.
- [x] `agentic_mbse.sysml.expression` exposes reconstruction, precedence, feature-chain,
  chain-segment, literal-node, and literal-value helpers.
- [x] `sysml_codegen.extraction.expression_utils` remains a permanent compatibility shim.
- [x] `agentic_mbse.sysml.binding` uses the shared literal-value helper.
- [x] INV-1 dispatch-totality and precedence/literal tests cover the shared implementation.
- [x] sysml-codegen shim tests prove old imports still work.
- [x] Expression-profile validation impact is implemented or filed with fixture shape and
  severity.
- [x] sysml-codegen suite passes; agentic-mbse suite passes.
- [x] ruff and mypy do not regress from the epic anchors.
- [x] Generated baselines are byte-identical.

---

## Required Reading for Design

- `.project/backlog/epic_push_down.md`
- `src/sysml_codegen/extraction/expression_utils.py`
- `src/sysml_codegen/extraction/usage_extractor.py`
- `src/sysml_codegen/extraction/hierarchy_resolver.py`
- `src/sysml_codegen/extraction/computed_attribute_extractor.py`
- `tests/conformance/test_ast_dispatch_invariant.py`
- `tests/unit/test_expression_paren_helper.py`
- `tests/conformance/test_agg_literal_dispatch.py`
- `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/expression.py`
- `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/binding.py`
- `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/validation/level6_architecture.py`
- `/home/reid/1cfe/agentic-mbse/tests/test_sysml/test_expression.py`

---

## Implementation Gate

Do not begin implementation or land this item until the epic's external prerequisites are
satisfied on the selected landing bases:

- sysml-codegen: `truth-debt-epic` is merged to the selected landing base.
- agentic-mbse: PR #7 (`upstream-findings-sync`) is merged.
- agentic-mbse: the `pipeline-truth-item4` companion is merged.

The current session observed sysml-codegen on `truth-debt-epic` and agentic-mbse on
`pipeline-truth-item4`. That is valid for specification, but not for landing PUSH-DOWN code.

---

## Open Questions for Design

1. Should shared reconstruction helpers live directly in `agentic_mbse.sysml.expression`, or
   should reconstruction be grouped behind an internal section with explicit `__all__` exports?
   The default should be direct exports unless design finds import-cycle pressure.

2. Should agentic-mbse keep its existing `is_literal_expression` semantic name and add
   `is_literal_node`, or should the old name be deprecated? The spec requires `is_literal_node`
   for the moved predicate and leaves the existing true-static helper intact.

3. Which expression-profile checks should land in this item versus be filed? The minimum
   acceptable close is a traceability table: helper → check added / existing check / filed rule.
