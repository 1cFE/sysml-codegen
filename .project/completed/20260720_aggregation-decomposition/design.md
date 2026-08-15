# Design: Aggregation Decomposition and Compatibility Gates

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-07-08 16:56 PDT
**Branch:** push-down-item1-expression
**Commit:** fb7e13a

## Overview

Move aggregation AST decomposition into `agentic_mbse.sysml.aggregation` as neutral SysML facts.
sysml-codegen keeps the local adapter that turns those facts into Python expression text,
`AggregationExpressionData`, aliases, warnings, scoping, and pipeline inputs.

## Related Artifacts

- Spec: `.project/active/aggregation-decomposition/spec.md`
- Spec review: `.project/active/aggregation-decomposition/spec-review.md`
- Epic: `.project/backlog/epic_push_down.md`
- Current context: `.project/CURRENT_WORK.md`
- Prior certified item: `.project/active/hierarchy-primitives-models/audit.md`
- Prior design: `.project/active/hierarchy-primitives-models/design.md`
- Prior plan: `.project/active/hierarchy-primitives-models/plan.md`
- sysml-codegen source: `src/sysml_codegen/extraction/hierarchy_resolver.py`
- sysml-codegen models: `src/sysml_codegen/extraction/data_models.py`
- agentic-mbse shared models: `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/data_models.py`
- agentic-mbse hierarchy pattern: `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/hierarchy.py`
- agentic-mbse expression helpers: `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/expression.py`
- agentic-mbse adapter: `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/syside_adapter.py`

## Research Findings

- The current aggregation walker is one mixed function. It classifies terms, unwraps wrappers,
  records unsupported shapes, builds `input_channels` and `entry_points`, and emits Python-ish text
  in the same traversal (`src/sysml_codegen/extraction/hierarchy_resolver.py:262`).
- The dispatch order is load-bearing. `FeatureChainExpression` must run before
  `OperatorExpression` because SysIDE dual-matches feature chains as operators
  (`src/sysml_codegen/extraction/hierarchy_resolver.py:284`). Literal handling must run before the
  invocation catch-all because literals can expose `.function.name`
  (`src/sysml_codegen/extraction/hierarchy_resolver.py:323`).
- Wrapper behavior is intentionally permissive inside `sum(...)`. `_unwrap_invocation` peels any
  invocation with operands once the sum branch calls it, without checking the function name
  (`src/sysml_codegen/extraction/hierarchy_resolver.py:211`,
  `src/sysml_codegen/extraction/hierarchy_resolver.py:335`). A non-sum wrapper is name-gated by
  `_KNOWN_WRAPPER_FUNCTIONS` before unsupported invocation handling
  (`src/sysml_codegen/extraction/hierarchy_resolver.py:376`).
- Unsupported behavior is visible downstream. Unsupported operators set `has_unsupported` and render
  the raw operator with current spacing (`src/sysml_codegen/extraction/hierarchy_resolver.py:238`).
  Unsupported invocations set the flag, still walk operands, and render a local call expression
  (`src/sysml_codegen/extraction/hierarchy_resolver.py:382`).
- `build_aggregation_expression` is the existing local assembly point. It returns `None` for
  non-expression redefinitions or expression redefinitions with no AST, sanitizes the owning part
  name, and constructs `AggregationExpressionData` defaults locally
  (`src/sysml_codegen/extraction/hierarchy_resolver.py:399`).
- Alias collection is local orchestration behavior. The pinned dotted-leaf rule matches by source
  leaf only and ignores whether the dotted part differs
  (`src/sysml_codegen/extraction/hierarchy_resolver.py:63`,
  `tests/unit/test_hierarchy_resolver.py:1345`).
- `AggregationExpressionData`, `HierarchyExtractionResult`, and `ScopedAggregationData` are
  codegen-facing containers. Downstream graph construction reads terms, transformed expression,
  unsupported flags, and aliases to build module inputs, entry points, and compiled expressions
  (`src/sysml_codegen/resolution/graph_builder.py:1352`). Scoping wraps local aggregation data in
  `ScopedAggregationData` (`src/sysml_codegen/orchestration/pipeline_builder.py:616`).
- Snapshot loading reconstructs the three term models and local aggregation container through the
  sysml-codegen import path (`src/sysml_codegen/snapshot/loader.py:422`).
- Item 3 established the move pattern: shared dataclasses live in
  `agentic_mbse.sysml.data_models`, shared functions live in a focused sysml module, and
  sysml-codegen re-exports identical class objects
  (`/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/data_models.py:46`,
  `src/sysml_codegen/extraction/data_models.py:62`).
- agentic-mbse already owns the shared helper surface the aggregation module should use:
  feature chain/reference extraction, literal-node detection, literal rendering, and expression
  reconstruction (`/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/expression.py:418`,
  `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/expression.py:548`,
  `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/expression.py:640`).
- `SysideAdapter.TYPE_MAP` already maps the expected aggregation-adjacent strings:
  `FeatureChainExpression`, `FeatureReferenceExpression`, `InvocationExpression`,
  `OperatorExpression`, literal types, and `NullExpression`
  (`/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/syside_adapter.py:198`).
  The new module still needs an inventory test because direct moved-code usage, not prior existence,
  is the proof this item requires.

## Core Concept

The shared system is an aggregation decomposer, not an aggregation compiler. It walks a SysML AST
and returns a neutral expression tree plus ordered term lists and diagnostics. That tree preserves
what the expression is: sums, feature chains, local references, literals, operators, wrappers, and
unsupported shapes. sysml-codegen then uses the tree with local multiplicity data and naming policy
to rebuild the same Python expression text, input channels, entry points, warnings, aliases, and
pipeline containers it produces today. The boundary is simple: agentic-mbse explains aggregation
compatibility from SysML facts; sysml-codegen decides how those facts become generated Python.

## Key Bets

- **B1.** Aggregation term classification and expression-shape preservation are reusable SysML facts
  independent of generated Python spelling. *If false -> the move would either leak Python strings
  into agentic-mbse or fail to reproduce `AggregationExpressionData`.*
- **B2.** A neutral expression tree plus ordered terms and diagnostics is enough to rebuild the
  current local output exactly. *If false -> the adapter will need raw SysIDE re-walking and the
  shared result will not be the source of truth.*
- **B3.** Multiplicity lookup is codegen policy, not neutral decomposition. *If false -> shared
  `SumTerm` would need multiplicity fields that depend on local hierarchy extraction context and the
  PUSH-DOWN boundary would blur.*
- **B4.** A combined source inventory over aggregation plus imported expression helpers can prove
  all direct and helper adapter strings used by this move. *If false -> aggregation can fail live
  SysIDE extraction through a helper string that the direct moved-module inventory does not see.*

## Key Decisions

- **D1.** Add `agentic_mbse.sysml.aggregation` with `decompose_aggregation_expression(expr)`.
  *Rejected: moving `_walk_aggregation_ast` wholesale, because it currently returns Python text and
  codegen identifiers.*
- **D2.** Represent structure as a small neutral node model rather than returning a flat event stream.
  *Rejected: a flat list of facts, because sysml-codegen must preserve nested operator ordering and
  parenthesized rendering.*
- **D3.** Move `SumTerm`, `SingletonTerm`, and `LocalTerm` into
  `agentic_mbse.sysml.data_models`, then re-export them from `agentic_mbse.sysml.aggregation` and
  the package root. *Rejected: defining them only in `aggregation.py`, because Item 3 established
  `data_models.py` as the shared model home.*
- **D4.** sysml-codegen imports and re-exports the exact shared class objects through
  `sysml_codegen.extraction.data_models`. *Rejected: subclassing or local mirror dataclasses,
  because object identity and snapshot compatibility are explicit requirements.*
- **D5.** Keep `AggregationExpressionData`, `HierarchyExtractionResult`, and `ScopedAggregationData`
  local. *Rejected: moving them, because they carry transformed Python text, aliases, warnings,
  scoping, and pipeline assembly products.*
- **D6.** Keep Python operator spelling in `AGG_PYTHON_OPS` local and store only the SysML operator
  symbol plus supported/unsupported diagnostic facts in the neutral result. *Rejected: sharing
  Python operator maps, because agentic-mbse must not emit Python source.*
- **D7.** Preserve permissive sum-operand unwrap exactly. The shared decomposer records wrapper
  disposition but still unwraps the first operand of any invocation when reached from `sum(...)`.
  *Rejected: stricter wrapper warnings inside `sum(...)`, because that is a behavior change.*
- **D8.** Close the profile loop by disposition table, not by forcing new validation rules. *Rejected:
  shallow duplicate rules, because existing expression and hierarchy profile checks may already own
  some rejected shapes.*

## Architecture

The target shape has four layers.

1. Shared data models:
   `agentic_mbse.sysml.data_models` defines `SumTerm`, `SingletonTerm`, and `LocalTerm` as exact
   dataclasses with the current field names, order, and defaults. Existing hierarchy models stay as
   they are.

2. Shared neutral decomposition:
   `agentic_mbse.sysml.aggregation` owns wrapper unwrapping, dispatch order, term classification,
   neutral expression nodes, wrapper disposition, and diagnostics. It imports only agentic-mbse
   helpers and standard-library code.

3. sysml-codegen compatibility:
   `sysml_codegen.extraction.data_models` re-exports the moved term classes as identical runtime
   objects. `sysml_codegen.extraction.hierarchy_resolver.build_aggregation_expression` stays public
   and calls shared decomposition, then local adapter functions.

4. sysml-codegen policy and consumers:
   hierarchy orchestration still appends warnings and aliases. Scoping, input resolution, graph
   assembly, snapshot loading, and fixture generation continue to consume local
   `AggregationExpressionData`.

Data flow:

1. Item 3 hierarchy extraction still creates `RedefinitionData` with `expression_ast` and
   `expression_text`.
2. `build_aggregation_expression` rejects non-expression or missing-AST redefinitions before calling
   shared decomposition.
3. Shared decomposition returns `AggregationDecomposition`.
4. sysml-codegen applies multiplicity lookup, Python operator spelling, and naming policy to produce
   `AggregationExpressionData`.
5. `extract_hierarchy_data` enriches warnings and aliases exactly as today.

## Shared API Shape

Public API:

```python
def decompose_aggregation_expression(expr_node: Any) -> AggregationDecomposition: ...
```

Minimum neutral payload:

- `root`: the ordered neutral expression tree.
- `sum_terms`, `singleton_terms`, `local_terms`: ordered shared term dataclasses collected during
  traversal. For shared `SumTerm`, `multiplicity_attr` and `multiplicity_count` are always `None`;
  sysml-codegen fills those fields in its local adapter when it has multiplicity data.
- `diagnostics`: neutral unsupported-node and unsupported-operator facts.
- `wrappers`: wrapper disposition facts, including whether a wrapper was unwrapped because it was a
  sum operand or because it was one of the known non-sum wrappers.
- `has_unsupported`: derived convenience bool.
- `source_refs`: opaque source identity or source-text references for diagnostics and exact local
  behavior. These can be raw node type names, raw SysML render text, and traversal paths, but not
  Python source or pipeline identifiers.

Neutral node types should be standard-library dataclasses with explicit fields. The shape must
cover: `sum`, feature chain, feature reference, literal, operator, invocation, unsupported, and
empty/null expression. It must carry only SysML-level text/facts.

Required node contracts:

- Operator node:
  `operator` as the raw SysML operator symbol, `operands` as the ordered child nodes,
  `unsupported` as a bool, and `diagnostic_id` when the operator is unsupported.
- Invocation node:
  `function_name`, ordered `operands`, `wrapper_disposition`, `unsupported` as a bool, and
  `diagnostic_id` when the invocation is unsupported. Unsupported invocations keep their ordered
  operands so sysml-codegen can render `func(args)` locally after recursively rendering each arg.
- Literal node:
  `literal_kind` and either `render_text` or `value`. The facts must be enough for sysml-codegen to
  reproduce current literal rendering without re-dispatching the raw SysIDE node.
- Unsupported node:
  `fallback_render`, `node_kind` or type name, `diagnostic_id`, and `diagnostic_message`.
  `fallback_render` preserves the current `str(node)` local fallback without becoming Python source.
- Sum node:
  `term_index`, `operand`, and original function/wrapper context when relevant. The wrapper context
  records whether the operand came through permissive sum-operand unwrapping.
- Feature chain node:
  `source_path`, which is the dotted path used for `SingletonTerm`, `SumTerm`, input channel
  collection, and local rendering.
- Feature reference node:
  `attribute_name`, which is the bare name used for `LocalTerm` and local rendering.

```python
@dataclass
class AggregationSumNode:
    term_index: int
    operand: AggregationNode
    wrapper_context: str | None = None
```

No neutral object may carry generated Python source, sanitized channel names, entry point names,
aliases, or sysml-codegen containers.

## Local Adapter Responsibilities

`build_aggregation_expression` remains the only sysml-codegen public builder for local aggregation
data.

It rebuilds:

- `owning_part_qn` from `RedefinitionData`.
- `owning_part_name` by local `sanitize_name(getattr(part_element, "name", ""))`.
- `attribute_name`, `raw_expression_text`, and source metadata from the redefinition/defaults.
- `transformed_expression` by rendering the neutral tree with local `AGG_PYTHON_OPS`. Sum nodes use
  their `term_index` to find the locally filled sum term, so the rendered expression and the ordered
  term list cannot drift.
- `sum_terms` by reading each neutral sum term and creating a new local `SumTerm` instance with
  multiplicity fields from the local multiplicity lookup. The adapter must not mutate shared
  neutral decomposition results. If no named multiplicity exists, it creates an unresolved local
  term with `multiplicity_attr=None`, `multiplicity_count=None`, and no multiplicity entry point.
- `singleton_terms` and `local_terms` from the shared ordered lists.
- `input_channels` from feature-chain references and sum operands, in traversal order.
- `entry_points` only from sum terms whose multiplicity has a `count_attribute_name`.
- `has_unsupported_nodes` from neutral diagnostics.
- `compilability`, `aliases`, `source_file`, and `source_line` via existing dataclass defaults unless
  current behavior explicitly sets them.

Alias collection stays after builder return in `extract_hierarchy_data`. The adapter must return
`aliases=[]`; orchestration then applies `_chain_sibling_aliases_aggregation`.

## Required Invariants

- agentic-mbse production and validation code must not import `sysml_codegen`.
- The shared API must not return Python source strings, sanitized codegen identifiers,
  `input_channels`, `entry_points`, aliases, or `AggregationExpressionData`.
- `SumTerm`, `SingletonTerm`, and `LocalTerm` must be identical runtime class objects through
  `agentic_mbse.sysml.data_models`, `agentic_mbse.sysml.aggregation`, `agentic_mbse.sysml`, and
  `sysml_codegen.extraction.data_models`.
- Shared `SumTerm` field names and order remain:
  `part_usage_name`, `attribute_name`, `multiplicity_attr`, `multiplicity_count`.
- Feature-chain dispatch stays before operator dispatch in the shared walker.
- Literal/null dispatch stays before invocation dispatch in the shared walker.
- Inside `sum(...)`, any invocation with operands remains permissively unwrapped to its first
  operand up to the current depth limit. `sum(filter(module.cost))` must not become unsupported.
- Non-sum known wrappers remain unwrapped; unsupported non-sum invocations remain unsupported,
  still walk operands, and render locally as `func(args)`.
- Unsupported operators remain unsupported, and local rendering preserves the raw operator with
  current spacing.
- `build_aggregation_expression` still returns `None` for non-`EXPRESSION` redefinitions and
  `EXPRESSION` redefinitions with no AST.
- Missing multiplicity on `sum(child.attr)` keeps an unresolved `SumTerm`, includes
  `child.attr` as an input channel, and does not invent a multiplicity entry point.
- Dotted-leaf alias behavior stays local and unchanged.
- Fixture byte identity is required: `git diff -- tests/fixtures` must be empty after targeted and
  full gates.

## Component Overview

- `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/data_models.py`: shared home for
  `SumTerm`, `SingletonTerm`, and `LocalTerm`.
- `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/aggregation.py`: neutral decomposer, neutral
  expression result models, wrapper facts, diagnostics, and direct TYPE_MAP inventory test target.
- `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/__init__.py`: package-level aggregation API
  re-exports.
- `/home/reid/1cfe/agentic-mbse/tests/test_sysml/test_aggregation.py`: shared decomposition,
  dataclass field, data-model identity, dispatch, wrapper, unsupported, literal, and TYPE_MAP tests.
- `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/validation/level6_architecture.py`: optional
  codegen-compatible aggregation-profile rules, only where existing facts support them.
- `/home/reid/1cfe/agentic-mbse/.project/backlog/BACKLOG.md`: filed aggregation-profile rows that
  cannot land without duplicate diagnostics or future profile policy.
- `src/sysml_codegen/extraction/data_models.py`: compatibility re-export for moved term classes;
  local aggregation and hierarchy containers remain here.
- `src/sysml_codegen/extraction/hierarchy_resolver.py`: local `build_aggregation_expression`,
  Python renderer, multiplicity application, warnings, and alias enrichment.
- `tests/unit/test_hierarchy_resolver.py`: local adapter field-level builder tests, unsupported
  local rendering tests, wrapper compatibility, and dotted-leaf alias pins.
- `tests/conformance/test_agg_literal_dispatch.py`: committed literal-probe compatibility gate.
- `tests/conformance/test_hierarchy_resolver.py`, `tests/conformance/test_ast_dispatch_invariant.py`,
  `tests/conformance/test_input_resolver.py`, and `tests/conformance/test_factory_aggregation.py`:
  downstream compatibility gates.

## TYPE_MAP Inventory Strategy

Use a combined source-inventory proof. The aggregation inventory must parse or inspect both
`agentic_mbse.sysml.aggregation` and the imported expression helper source that aggregation relies
on, starting with `agentic_mbse.sysml.expression`. This is stricter than the Item 3 direct-module
inventory because the current tree has broad adapter tests and hierarchy inventory, but no
expression-helper source inventory equivalent to hierarchy's direct proof.

The inventory must collect literal strings passed to:

- `SysideAdapter.is_instance(...)`
- `SysideAdapter.elements_of_type(...)`, if the implementation adds any enumeration

Expected direct aggregation strings are:

- `FeatureChainExpression`
- `OperatorExpression`
- `FeatureReferenceExpression`

Because the combined inventory traverses expression helpers, it must also cover helper strings used
by `is_literal_node`, `reconstruct_expression`, `extract_feature_chain_name`, and
`extract_feature_reference_name`, including `InvocationExpression`, `LiteralInteger`,
`LiteralRational`, `LiteralString`, `LiteralBoolean`, `LiteralInfinity`, and `NullExpression` when
they appear in the helper source.

The inventory test must reset or bypass `SysideAdapter._type_map`, so it proves TYPE_MAP coverage
without depending on test order. If implementation imports additional shared helper modules that use
the adapter, the inventory must either include those helper sources or add a separate source-inventory
test for them in the same item.

## Aggregation-Profile Disposition Strategy

The profile loop closes at design time with these dispositions. Implementation may update a row only
if code inspection proves a better existing rule or a concrete new rule with tests. Every `FILED`
row must be added to the agentic-mbse backlog with the exact rule, fixture shape, severity,
rationale, and backlog ID shown here.

| Shape | Disposition | Exact rule | Fixture shape | Severity | Rationale | Backlog ID |
| --- | --- | --- | --- | --- | --- | --- |
| Sum aggregation | FILED | Warn when a codegen-targeted aggregation expression uses `sum(...)` on an operand that cannot decompose to a supported child feature chain or local reference, unless existing expression/hierarchy profile checks already cover the rejected operand shape. | `:>> total = sum(module.cost)` is clean; an unsupported operand shape warns only if not already covered elsewhere. | WARNING | Aggregation-specific unsupported sum operand diagnostics need profile integration over shared aggregation facts. Avoid a shallow rule in this behavior-preserving move. | `PUSH-DOWN-AGG-PROFILE-SUM-SHAPE` |
| Singleton child reference | EXISTING | Existing expression-profile chain-segment coverage reports lossy or anonymous chain segments. | `:>> total = allocation_model.total_allocation` is clean; anonymous or lossy chain segment shapes are covered by `PUSH-DOWN-EXPR-PROFILE-CHAIN-SEGMENTS`. | WARNING | Singleton aggregation controls still need local codegen tests, but early profile diagnostics for malformed chains already belong to the expression-profile row. | N/A |
| Local attribute reference | EXISTING | Existing unsupported-shape message coverage reports opaque feature reference shapes that cannot be explained by shared expression facts. | `:>> total = misc_hardware_cost` is clean; missing referent/name or opaque local reference shape is covered by `PUSH-DOWN-EXPR-PROFILE-UNSUPPORTED-SHAPE-MESSAGE`. | WARNING | Supported bare feature references are clean/no-op for profile purposes. Opaque references are a general expression-shape diagnostic, not aggregation-specific policy. | N/A |
| Invocation wrapper | FILED | Preserve current generation behavior for wrapper unwrapping. Any profile-only warning for unsupported wrappers must be explicitly separated from this item's behavior-preserving implementation. | `sum(Evaluation(module.cost))`, `sum(collect(Evaluation(module.cost)))`, `Evaluation(allocation.total)`, and current permissive `sum(filter(module.cost))` behavior are controls. A future stricter wrapper warning is filed rather than implemented here. | WARNING | Current generation is permissive inside `sum(...)`; stricter profile warning is future profile work, not this behavior-preserving move. | `PUSH-DOWN-AGG-PROFILE-WRAPPER-SHAPE` |
| Literal operand | FILED | Warn when a literal appears where codegen aggregation decomposition cannot use it as a term, while preserving supported literal rendering inside otherwise valid operator expressions. | `:>> total = sum(module.cost) + 5.0` keeps the literal in neutral operator facts; `sum(5.0)` is the filed aggregation-specific incompatible shape. | WARNING | `sum(5.0)` is aggregation-specific and should not be mixed with general literal expression support. | `PUSH-DOWN-AGG-PROFILE-LITERAL-SHAPE` |
| Unsupported AST node | EXISTING | Existing expression-profile unsupported-shape message coverage reports AST nodes that cannot be classified into supported shared expression facts. | Unknown expression node inside `:>> total = <unknown>` is covered by `PUSH-DOWN-EXPR-PROFILE-UNSUPPORTED-SHAPE-MESSAGE`; feature chain, reference, literal, operator, and supported invocation controls stay clean. | WARNING | The shared aggregation diagnostic can reuse the same expression-profile unsupported-shape policy instead of adding duplicate aggregation warnings. | N/A |
| Operator shape | EXISTING | Existing expression-profile unsupported-operator coverage reports operators outside the supported expression operator set. | Supported `+`, `-`, `*`, `/`, comparisons, logical operators, and `^` controls are covered; unknown operators are covered by `PUSH-DOWN-EXPR-PROFILE-UNSUPPORTED-OPERATOR`. | WARNING | Operator compatibility is already expressed as a shared expression-profile rule. Python spelling remains local in sysml-codegen. | N/A |

## Non-Goals

- Python rewriting or Python operator spelling in agentic-mbse.
- Moving `AggregationExpressionData`, `HierarchyExtractionResult`, or `ScopedAggregationData`.
- Codegen aliases or alias collection in agentic-mbse.
- Scoping, graph resolution, module construction, input resolver policy, or supplied-value
  materialization.
- Design overrides, usage-type indexing, part-usage indexing, or most-specific type selection.
- Template detection or virtual-binding matching.
- Snapshot schema changes or fixture recapture.
- Stricter wrapper warnings inside `sum(...)`.
- Item-level PR closeout. No item-level PR closeout happens before the whole PUSH-DOWN epic is
  implemented.

## Implementation Notes

- Prefer wrapper functions in sysml-codegen over direct aliases where local behavior may need tests
  to spy on shared delegation. Re-exported dataclasses must be direct imports, not wrappers.
- Keep the existing `_KNOWN_WRAPPER_FUNCTIONS` policy available to the shared decomposer. The name
  can move, but the set and behavior must not change in this item.
- The local renderer should be deliberately small: render neutral nodes, apply local multiplicity
  multiplication for sum nodes, and collect local fields. It should not re-walk SysIDE nodes except
  through the neutral result.
- Do not recapture fixtures. Any `tests/fixtures` diff is a failure unless a separate reviewed
  behavior-change item exists.
- Update source-file conformance expectations for `SumTerm`, `SingletonTerm`, and `LocalTerm` to
  point at `agentic_mbse/sysml/data_models.py`, while `AggregationExpressionData` remains
  `extraction/data_models.py`.

## Potential Risks

- The neutral node model may miss a fact currently implicit in string rendering. Mitigation:
  direct field-level builder tests must compare transformed expression, terms, channels, entry
  points, unsupported flags, aliases defaults, and source metadata.
- Wrapper unwrapping can drift if implementation tries to normalize it while moving. Mitigation:
  pin `sum(filter(module.cost))`, known non-sum wrappers, and unsupported non-sum invocations.
- TYPE_MAP proof can be incomplete if helper calls hide adapter strings. Mitigation: combined
  source inventory over the moved aggregation module and the imported expression helper source, with
  `_type_map` reset or bypassed in the test.
- Profile work can duplicate existing expression diagnostics. Mitigation: every row allows
  `EXISTING` and `NO-OP`, and filed rows are acceptable when the shared fact is useful but the rule
  belongs later.
- Cross-repo editable-install state can break one suite while the other is mid-move. Mitigation:
  land agentic-mbse API/tests first, then switch sysml-codegen, then run both targeted and full
  gates before stopping.

## Integration Strategy

Implement agentic-mbse first: add moved term dataclasses, the aggregation module, exports, shared
tests, TYPE_MAP proof, and profile dispositions or backlog rows. Then update sysml-codegen data
models to re-export the moved terms and update `build_aggregation_expression` to call the shared
decomposer.

The integration must keep all existing sysml-codegen callers stable. Snapshot loading, graph
builder, input resolver, scoping, and output registry tests should keep importing through
`sysml_codegen.extraction.data_models`. The only observable source-file expectation that changes is
for the three moved term classes.

## Validation Approach

agentic-mbse validation:

- `tests/test_sysml/test_aggregation.py`: neutral decomposition for sum, singleton, local, wrapper,
  literal, unsupported node, unsupported operator, term order, neutral payload no-leak assertions,
  dataclass field order/defaults, and direct TYPE_MAP inventory.
- Data-model identity/import tests through `agentic_mbse.sysml.data_models`,
  `agentic_mbse.sysml.aggregation`, and `agentic_mbse.sysml`.
- Aggregation-profile tests only for rows that close as `NEW RULE`; otherwise backlog or existing
  rule evidence.
- Touched-file ruff and full agentic-mbse tests. Run mypy only if the current baseline allows it;
  record unchanged baseline caveats otherwise.

sysml-codegen validation:

- Direct builder tests for field-level `AggregationExpressionData` compatibility, including
  `owning_part_name`, raw/transformed expression, all term lists, `input_channels`, `entry_points`,
  `compilability`, `has_unsupported_nodes`, empty `aliases`, and source metadata defaults.
- Tests for unsupported invocation and unsupported operator local rendering.
- Wrapper tests including known wrappers and permissive `sum(filter(module.cost))`.
- Data-model identity tests proving `SumTerm`, `SingletonTerm`, and `LocalTerm` are the same shared
  class objects through the sysml-codegen path.
- Dispatch invariant tests updated to exercise the moved shared walker.
- Existing committed probes: `agg_literal_probe` and `alias_agg_probe`.
- Orchestration warnings and alias enrichment tests, including dotted-leaf alias behavior.
- Scoping/input-resolver/graph consumers:
  `tests/conformance/test_aggregation_scoping.py`,
  `tests/conformance/test_input_resolver.py`,
  `tests/conformance/test_factory_aggregation.py`,
  `tests/unit/test_output_registry_construction.py`, and graph builder aggregation tests.
- Full sysml-codegen suite, `ruff check src/`, and fixture byte identity with
  `git diff -- tests/fixtures`.

## Next-Stage Handoff

Treat these as fixed:

- Shared decomposition owns neutral facts only.
- sysml-codegen owns all Python, pipeline, alias, warning, and local container behavior.
- The neutral payload is a tree plus ordered terms, wrapper facts, and diagnostics.
- The three term dataclasses move; the three aggregation/pipeline containers stay local.
- Existing permissive wrapper behavior, dispatch order, unsupported behavior, missing multiplicity
  behavior, dotted-leaf alias behavior, and fixture byte identity are non-negotiable compatibility
  gates.

Open during planning:

- Exact names of neutral node dataclasses and diagnostic enum/string constants.

De-risk first:

- Write the shared decomposition tests and sysml-codegen direct builder field tests before changing
  production code. They are the shortest proof that the neutral payload can rebuild local behavior
  exactly.

---

Next Step: After approval -> `my-plan` for implementation.
