# Spec: Aggregation Decomposition and Compatibility Gates

**Status:** Certified
**Owner:** Reid W
**Created:** 2026-07-08 16:46 PDT
**Complexity:** HIGH
**Branch:** push-down-item1-expression

---

## Problem

PUSH-DOWN Item 4 needs to move the reusable SysML aggregation understanding out of
sysml-codegen without moving codegen behavior with it. The current aggregation path in
`src/sysml_codegen/extraction/hierarchy_resolver.py` walks SysML expression ASTs, unwraps
invocation wrappers, classifies sum/singleton/local terms, reports unsupported shapes, and also
builds Python-expression text plus pipeline-facing `AggregationExpressionData`. That mix blocks
agentic-mbse from validating codegen-compatible aggregation structures from shared SysML facts, and
it makes the shared/codegen boundary easy to blur.

This item separates those responsibilities. agentic-mbse should extract neutral aggregation facts
from typed SysML ASTs. sysml-codegen should turn those facts into Python expressions, input channel
names, entry points, aliases, and local `AggregationExpressionData`.

Neutral aggregation facts are the SysML-level decomposition outputs that preserve expression shape
without generated Python spelling or pipeline identifiers. At minimum, they carry typed terms,
literal facts, operator facts, wrapper disposition, expression ordering/structure, and unsupported
diagnostics. They must give sysml-codegen enough information to rebuild the current
`AggregationExpressionData` locally and exactly.

## Success Criteria

- [x] agentic-mbse exposes shared aggregation decomposition that covers sum, singleton, local,
  wrapper, literal, unsupported-node, and operator shapes without importing sysml-codegen.
- [x] `SumTerm`, `SingletonTerm`, and `LocalTerm` live in agentic-mbse as shared dataclasses, and
  sysml-codegen re-exports the same runtime class objects through existing import paths.
- [x] The shared aggregation API returns the minimum neutral result payload needed by sysml-codegen:
  ordered expression structure, typed terms, literal/operator facts, wrapper disposition, and
  unsupported diagnostics. It returns no Python source strings, sanitized codegen identifiers,
  `input_channels`, `entry_points`, aliases, or `AggregationExpressionData`.
- [x] `build_aggregation_expression` remains in sysml-codegen and reproduces the existing local
  `AggregationExpressionData` behavior exactly from the shared neutral facts, including field-level
  values and alias behavior.
- [x] Fixture byte identity is proven: `git diff -- tests/fixtures` in sysml-codegen is empty after
  targeted gates and after the full sysml-codegen suite. This repo's committed generated outputs live
  under `tests/fixtures/baseline_outputs`, so this single command is the byte-identity gate.
- [x] TYPE_MAP coverage is inventoried from the moved aggregation implementation source, and every
  direct adapter type string used by moved code is present in
  `agentic_mbse.sysml.syside_adapter.SysideAdapter.TYPE_MAP`. Transitive shared-helper adapter usage
  is either inventoried too or explicitly covered by existing shared-helper TYPE_MAP tests.
- [x] The aggregation checking-profile loop is closed in agentic-mbse: every accepted or rejected
  aggregation shape is implemented as a profile rule, covered by an existing rule, or filed with
  exact rule, fixture shape, severity, rationale, and backlog ID.
- [x] Acceptance coverage is concrete: direct builder field-level behavior, unsupported
  invocation/operator behavior, committed `agg_literal_probe`, committed `alias_agg_probe`,
  orchestration warnings and alias enrichment, data-model identity, dispatch invariants,
  scoping/input-resolver consumers, full-suite gates, and fixture byte identity are all tested or
  recorded.
- [x] Both suites pass at the item landing point, with import/type checks and known baseline caveats
  recorded: agentic-mbse full tests, sysml-codegen full tests, touched-file ruff in agentic-mbse,
  sysml-codegen `ruff check src/`, and mypy only if current baselines allow it.
- [x] `$my-spec-review` runs and is resolved before `$my-design`. Design must not start from this
  draft alone.
- [x] There is no item-level PR closeout. This item can be audited and committed, but PR preparation
  waits until the whole PUSH-DOWN epic is implemented.

## Known Requirements

- **[HARD] REQ-AGG-01:** agentic-mbse must own only neutral aggregation decomposition facts:
  invocation unwrapping, AST walking, typed terms, expression ordering/structure, literal facts,
  operator facts, wrapper disposition, unsupported-node diagnostics, and unsupported-operator
  diagnostics.
- **[HARD] REQ-AGG-02:** sysml-codegen must keep Python rewriting, `AGG_PYTHON_OPS` Python spelling,
  `build_aggregation_expression`, `AggregationExpressionData`, `input_channels`, `entry_points`,
  aliases, warnings composed with hierarchy orchestration, and pipeline-facing assembly.
- **[HARD] REQ-AGG-03:** The shared API must not return generated Python source, Python-safe module
  or channel identifiers, sysml-codegen pipeline identifiers, or sysml-codegen data containers.
- **[HARD] REQ-AGG-04:** `SumTerm`, `SingletonTerm`, and `LocalTerm` must move as field-compatible
  shared dataclasses. Existing sysml-codegen import paths must re-export the same runtime class
  objects, not subclasses or mirrored local copies.
- **[HARD] REQ-AGG-05:** `AggregationExpressionData`, `HierarchyExtractionResult`, and
  `ScopedAggregationData` must remain sysml-codegen-local because they bundle codegen orchestration
  and pipeline assembly products.
- **[HARD] REQ-AGG-06:** The minimum neutral result payload must include every fact needed for
  sysml-codegen to rebuild the current `AggregationExpressionData` locally: ordered expression
  structure, term sequence, `SumTerm`/`SingletonTerm`/`LocalTerm` instances, literal values or
  literal render facts, operator symbols, wrapper disposition, unsupported diagnostics, and enough
  source node identity or source text references to preserve current adapter behavior.
- **[HARD] REQ-AGG-07:** The shared walker must preserve current shape classification: `sum(child.attr)`
  produces a `SumTerm`; a non-sum feature chain produces a `SingletonTerm`; a local feature reference
  produces a `LocalTerm`; wrapper invocations preserve the current unwrapping behavior.
- **[HARD] REQ-AGG-08:** Current permissive wrapper behavior inside `sum(...)` must not change in this
  item. Once `_unwrap_invocation` is called for a sum operand, any invocation with operands unwraps
  to its first operand, so `sum(filter(module.cost))` currently unwraps rather than warns. Any stricter
  unsupported-wrapper warning for this shape is profile-only future work or a separate reviewed
  behavior-change item.
- **[HARD] REQ-AGG-09:** Literal AST handling must stay before the generic invocation branch. A
  literal operand must not be mis-dispatched as an invocation or unsupported node.
- **[HARD] REQ-AGG-10:** Feature-chain handling must stay before operator handling for dual-match
  SysIDE nodes. Existing dispatch-order invariants must be updated to include the moved shared
  aggregation walker.
- **[HARD] REQ-AGG-11:** Unsupported node and unsupported operator information must survive the move
  as neutral diagnostics or flags that sysml-codegen can map to `has_unsupported_nodes` without
  changing downstream behavior. The local adapter must preserve current externally visible behavior:
  unsupported invocations set unsupported, still walk operands, and render a local call expression;
  unsupported operators set unsupported and render the raw operator with current spacing.
- **[HARD] REQ-AGG-12:** `build_aggregation_expression` must continue returning `None` for
  non-`EXPRESSION` redefinitions and `EXPRESSION` redefinitions with no AST.
- **[HARD] REQ-AGG-13:** Missing multiplicity on `sum(child.attr)` must preserve current behavior:
  record an unresolved `SumTerm`, include the child attribute as an upstream input in the local
  adapter output, and avoid inventing a multiplicity entry point.
- **[HARD] REQ-AGG-14:** The local adapter must preserve field-level `AggregationExpressionData`
  compatibility: `owning_part_qn`, sanitized `owning_part_name`, `attribute_name`,
  `raw_expression_text`, `transformed_expression`, `sum_terms`, `singleton_terms`, `local_terms`,
  `input_channels`, `entry_points`, `compilability`, `has_unsupported_nodes`, default-empty
  `aliases` before orchestration enrichment, and source metadata defaults.
- **[HARD] REQ-AGG-15:** sysml-codegen must preserve current alias behavior. Alias collection stays
  local, and the pinned dotted-leaf edge remains: a CHAIN sibling whose dotted source leaf matches
  the aggregation attribute aliases the aggregation even when the dotted part name differs.
- **[HARD] REQ-AGG-16:** The TYPE_MAP inventory must be generated from the moved shared aggregation
  module source or AST. It must cover every direct literal argument passed by moved code to
  `SysideAdapter.is_instance(...)` or `SysideAdapter.elements_of_type(...)`.
- **[HARD] REQ-AGG-17:** The expected starting TYPE_MAP strings for the moved aggregation walker are
  `FeatureChainExpression`, `OperatorExpression`, and `FeatureReferenceExpression`. If design changes
  wrapper or literal detection to direct adapter checks, the inventory must also include those new
  direct strings, such as `InvocationExpression`, `LiteralInteger`, `LiteralRational`,
  `LiteralString`, `LiteralBoolean`, `LiteralInfinity`, or `NullExpression`.
- **[HARD] REQ-AGG-18:** TYPE_MAP tests must reset or bypass `SysideAdapter._type_map` so the proof is
  not order-dependent on prior tests.
- **[HARD] REQ-AGG-19:** The TYPE_MAP proof must close transitive shared-helper coverage. The design
  must either inventory adapter strings used by imported shared helpers, or explicitly rely on and
  cite existing shared-helper TYPE_MAP tests such as the expression and hierarchy inventory tests.
- **[HARD] REQ-AGG-20:** No agentic-mbse production code or validation rule may import sysml-codegen.
- **[HARD] REQ-AGG-21:** The checking-profile close-out must include a disposition table with exact
  rule, fixture shape, severity, rationale, and backlog ID for every filed row. A row may close only
  as `EXISTING`, `NEW RULE`, `FILED`, or `NO-OP`.
- **[NEED] REQ-AGG-22:** The moved API should make future agentic-mbse validation able to explain
  aggregation compatibility from SysML facts, not from generated Python strings.
- **[NEED] REQ-AGG-23:** The downstream design should keep the sysml-codegen wrapper small enough
  that a reviewer can see where neutral decomposition ends and Python/pipeline assembly begins.
- **[INFERRED] REQ-AGG-24:** The agentic-mbse shared model home should follow Item 3's established
  pattern by placing shared dataclasses in `agentic_mbse.sysml.data_models` and re-exporting them
  from the aggregation module and package root, unless design finds a stronger local convention.
- **[INFERRED] REQ-AGG-25:** Existing sysml-codegen aggregation tests should mostly remain local,
  with new shared tests added in agentic-mbse for the neutral decomposition behavior and local tests
  changed only where compatibility imports or adapter delegation need to be pinned.

## Validation Requirements

- Direct `build_aggregation_expression` coverage must assert field-level compatibility for
  representative results, including `owning_part_name` sanitization, raw and transformed expression
  text, all three term lists, `input_channels`, `entry_points`, `has_unsupported_nodes`,
  default `compilability`, empty `aliases` before orchestration enrichment, and source metadata
  defaults.
- Unsupported invocation and unsupported operator coverage must pin current local-adapter behavior:
  unsupported invocations set unsupported, walk operands, and render a local call expression;
  unsupported operators set unsupported and render the raw operator with current spacing.
- The committed `tests/fixtures/agg_literal_probe` fixture must remain unchanged and must continue
  proving literal operands do not trip the unsupported-invocation path.
- The committed `tests/fixtures/alias_agg_probe` fixture must remain unchanged and must continue
  proving aggregation alias behavior, including the dotted-leaf alias matching edge.
- Orchestration tests must cover warnings and alias enrichment around aggregation expressions after
  shared decomposition is introduced.
- Compatibility tests must prove data-model class identity for `SumTerm`, `SingletonTerm`, and
  `LocalTerm` through the existing sysml-codegen import path.
- Dispatch invariant tests must include the moved shared aggregation walker.
- Existing scoping and input-resolver consumers of `AggregationExpressionData` must run in the
  targeted acceptance set.
- Full gates must run for both repos, with known mypy baseline caveats recorded if unchanged.
- The sysml-codegen byte-identity gate is `git diff -- tests/fixtures`. There is no separate
  generated-output path outside `tests/fixtures` for this item.

## Aggregation-Profile Disposition Requirements

The design and plan must carry this table forward and update each row to `EXISTING`, `NEW RULE`,
`FILED`, or `NO-OP`. If a row is filed, the agentic-mbse backlog entry must use the listed backlog
ID and preserve the exact rule, fixture shape, severity, and rationale.

| Shape | Allowed disposition | Exact rule | Fixture shape | Severity | Rationale | Backlog ID |
| --- | --- | --- | --- | --- | --- | --- |
| Sum aggregation | EXISTING, NEW RULE, FILED, or NO-OP | Warn when a codegen-targeted aggregation expression uses `sum(...)` on an operand that cannot decompose to a supported child feature chain or local reference, unless existing expression/hierarchy profile checks already cover the rejected operand shape. | `:>> total = sum(module.cost)` is clean; an unsupported operand shape warns only if not already covered elsewhere. | WARNING | Shared aggregation facts can identify whether `sum` operands are compatible before codegen rewrites them, but this item must not duplicate existing expression-profile rules. | `PUSH-DOWN-AGG-PROFILE-SUM-SHAPE` if filed |
| Singleton child reference | EXISTING, NEW RULE, FILED, or NO-OP | Warn when a non-sum child reference in an aggregation expression cannot decompose to a supported dotted feature chain, unless existing chain-segment profile coverage already owns the shape. | `:>> total = allocation_model.total_allocation` is clean; anonymous or lossy chain segment disposition cites the existing expression-profile row or files a new aggregation row. | WARNING | Singleton terms become upstream channels locally; unsupported chains need early profile feedback, but chain semantics may already be owned by expression-profile checks. | `PUSH-DOWN-AGG-PROFILE-SINGLETON-SHAPE` if filed |
| Local attribute reference | EXISTING, NEW RULE, FILED, or NO-OP | Warn when a PartDef-local aggregation operand cannot decompose to a supported local feature reference, unless the shape is already covered by shared expression reference checks. | `:>> total = misc_hardware_cost` is clean; missing referent/name or opaque reference shape warns or is linked to existing expression-profile coverage. | WARNING | Local terms become local inputs or alias-resolved values in sysml-codegen; opaque references are not codegen-compatible unless another profile rule already reports the same fact. | `PUSH-DOWN-AGG-PROFILE-LOCAL-SHAPE` if filed |
| Invocation wrapper | EXISTING, NEW RULE, FILED, or NO-OP | Preserve current generation behavior for wrapper unwrapping. Any profile-only warning for unsupported wrappers must be explicitly separated from this item's behavior-preserving implementation. | `sum(Evaluation(module.cost))`, `sum(collect(Evaluation(module.cost)))`, `Evaluation(allocation.total)`, and current permissive `sum(filter(module.cost))` behavior are controls; a future stricter wrapper warning is filed rather than implemented as a behavior change here. | WARNING if filed | Current code is permissive inside `sum(...)`. This item may document or file profile work, but must not turn current unwrapping into a generation warning. | `PUSH-DOWN-AGG-PROFILE-WRAPPER-SHAPE` if filed |
| Literal operand | EXISTING, NEW RULE, FILED, or NO-OP | Warn when a literal appears where codegen aggregation decomposition cannot use it as a term, while preserving supported literal rendering inside otherwise valid operator expressions. | `:>> total = sum(module.cost) + 5.0` keeps the literal in neutral operator facts; `sum(5.0)` is dispositioned without changing current generation behavior. | WARNING | Literal dispatch order is a known safety issue. The profile should distinguish literals that can stay in expression structure from literals that cannot become aggregation terms, unless existing expression checks already cover the shape. | `PUSH-DOWN-AGG-PROFILE-LITERAL-SHAPE` if filed |
| Unsupported AST node | EXISTING, NEW RULE, FILED, or NO-OP | Warn when aggregation decomposition encounters an AST node it cannot classify into a supported neutral shape, unless existing unsupported-expression profile coverage owns that shape. | Unknown expression node inside `:>> total = <unknown>` warns or cites existing coverage; feature chain, reference, literal, operator, and supported invocation controls stay clean. | WARNING | sysml-codegen currently sets `has_unsupported_nodes`; agentic-mbse needs the same compatibility fact without generated Python, but duplicate diagnostics should not be created. | `PUSH-DOWN-AGG-PROFILE-UNSUPPORTED-NODE` if filed |
| Operator shape | EXISTING, NEW RULE, FILED, or NO-OP | Warn when an aggregation expression uses an operator outside the codegen-compatible aggregation operator set, unless the existing expression-profile unsupported-operator rule already covers it. | Supported `+`, `-`, `*`, `/`, comparisons, logical operators, and `^` controls are covered; an unknown operator warns or cites existing coverage. | WARNING | Operators are part of neutral expression shape, but Python spelling remains local. Existing expression-profile unsupported-operator rows may cover part of this; the aggregation disposition must state what remains. | `PUSH-DOWN-AGG-PROFILE-OPERATOR-SHAPE` if filed |

## Non-Goals

- Python rewriting or Python operator spelling in agentic-mbse.
- Codegen aliases or alias collection.
- Design overrides.
- Usage-type indexing, part-usage indexing, or most-specific type selection.
- Scoping, graph resolution, module construction, supplied-value materialization, or pipeline
  assembly.
- Template detection.
- Virtual-binding matching.
- Moving `AggregationExpressionData`, `HierarchyExtractionResult`, or `ScopedAggregationData`.
- Snapshot schema changes or fixture recapture.
- Item-level PR closeout.

## Open Questions / Deferred to design

- Decide the shared API shape and names for the neutral aggregation result, unsupported-shape report,
  and walker entry point.
- Decide whether operator support is represented as a neutral supported-operator set in
  agentic-mbse or as unsupported-operator facts consumed by sysml-codegen, while keeping Python
  spelling local.
- Decide whether `SumTerm`, `SingletonTerm`, and `LocalTerm` are imported directly from
  `agentic_mbse.sysml.data_models` or through `agentic_mbse.sysml.aggregation` in sysml-codegen.
- Decide which aggregation-profile rows can land now and which must be filed because they depend on
  profile infrastructure outside this item.

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_push_down.md`
- **Current Work:** `.project/CURRENT_WORK.md`
- **Prior certified item:** `.project/active/hierarchy-primitives-models/audit.md`
- **Prior design:** `.project/active/hierarchy-primitives-models/design.md`
- **Prior plan:** `.project/active/hierarchy-primitives-models/plan.md`
- **sysml-codegen source:** `src/sysml_codegen/extraction/hierarchy_resolver.py`
- **sysml-codegen models:** `src/sysml_codegen/extraction/data_models.py`
- **agentic-mbse shared models:** `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/data_models.py`
- **agentic-mbse hierarchy pattern:** `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/hierarchy.py`
- **agentic-mbse expression helpers:** `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/expression.py`
- **agentic-mbse adapter:** `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/syside_adapter.py`
- **agentic-mbse backlog:** `/home/reid/1cfe/agentic-mbse/.project/backlog/BACKLOG.md`
- **Spec Review:** `.project/active/aggregation-decomposition/spec-review.md` (Revise verdict; must be resolved before design)
- **Design:** `.project/active/aggregation-decomposition/design.md` (to be created only after `$my-spec-review`)

---

**Next Steps:** Resolve `$my-spec-review` before `$my-design`. Do not do an item-level PR closeout;
continue the PUSH-DOWN epic after audit and implementation.
