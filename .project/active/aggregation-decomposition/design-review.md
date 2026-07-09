# Design Review: Aggregation Decomposition and Compatibility Gates

**Design:** `.project/active/aggregation-decomposition/design.md`
**Spec:** `.project/active/aggregation-decomposition/spec.md`
**Review File:** `.project/active/aggregation-decomposition/design-review.md`
**Date:** 2026-07-08

---

## Fundamental Assessment

Concerns. The overall boundary is right: agentic-mbse gets neutral aggregation decomposition, and sysml-codegen keeps Python spelling, aliases, warnings, multiplicity policy, and `AggregationExpressionData`. The design also preserves the known behavior traps: permissive `sum(...)` wrapper unwrapping, feature-chain-before-operator dispatch, literal-before-invocation dispatch, unsupported invocation/operator rendering, missing multiplicity, dotted-leaf aliasing, and fixture byte identity.

The design should not be reworked from scratch. It does need revision before implementation because two audit-critical loops are still too weak:

- The checking-profile disposition loop is deferred to planning instead of being carried as a concrete design decision.
- The TYPE_MAP strategy names transitive helper coverage, but relies on existing expression-helper inventory tests that do not appear to exist in the current agentic-mbse tree.

---

## Dimensional Review

### 1. Spec Compliance

**Assessment:** Concerns

The design satisfies the central split from `REQ-AGG-01` through `REQ-AGG-15`: shared neutral facts only, local Python/pipeline assembly, shared term dataclasses, local `AggregationExpressionData`, exact wrapper and dispatch behavior, missing multiplicity behavior, and local alias enrichment.

The blocker is `REQ-AGG-21`. The spec says the aggregation checking-profile close-out must include a disposition table with exact rule, fixture shape, severity, rationale, and backlog ID for every filed row. The design only says the implementation plan must decide each row and lists the rows again. It does not record any row as `EXISTING`, `NEW RULE`, `FILED`, or `NO-OP`, and its handoff explicitly leaves this open for planning. That means the design does not yet establish how the agentic-mbse profile loop closes.

### 2. Pattern Consistency

**Assessment:** Concerns

The module split follows the Item 3 pattern: shared dataclasses in `agentic_mbse.sysml.data_models`, focused shared logic in a new sysml module, package re-exports, and sysml-codegen compatibility re-exports. Keeping `AggregationExpressionData`, `HierarchyExtractionResult`, and `ScopedAggregationData` local matches current downstream ownership.

The TYPE_MAP proof pattern is only partly consistent. The current shared hierarchy test inventories direct strings from the moved module source and resets `_type_map`. The proposed aggregation test repeats that direct inventory pattern, but the transitive helper coverage is left as a citation to existing expression/helper inventory tests. In the current agentic-mbse tree, I found the hierarchy inventory test and broad adapter tests, but not an expression-helper source-inventory test equivalent to hierarchy's.

### 3. Abstraction Quality

**Assessment:** Concerns

The neutral tree abstraction is justified. A flat event list would make nested operator rendering and term ordering fragile, and moving local Python strings would violate the boundary.

The weak point is that neutral node schemas are described as implementation details while exact local reproduction is a hard requirement. The design names the required categories, but it should make the load-bearing fields explicit enough for implementation and audit: operator symbol plus operand order, invocation function name plus operand order, literal render facts, unsupported-node fallback render/source identity, wrapper disposition, and `SumNode.term_index`.

### 4. Duplication Avoidance

**Assessment:** Pass

The design avoids moving codegen containers and avoids duplicating local alias, graph, scoping, and pipeline policy. The shared term dataclass move is intentional because identity compatibility is required. The local adapter is the right place for the remaining duplication risk, and the validation plan calls for field-level tests to catch drift.

### 5. Data Structure Clarity

**Assessment:** Concerns

The moved `SumTerm`, `SingletonTerm`, and `LocalTerm` fields are clear and compatible with existing local models. The `AggregationDecomposition` payload is directionally clear: root tree, ordered terms, diagnostics, wrappers, `has_unsupported`, and source refs.

The design still leaves too much freedom in the neutral payload for unsupported and literal cases. Current local behavior renders unknown nodes as `str(node)`, unsupported invocations as `func(args)`, unsupported operators with raw operator spacing, and literals through shared reconstruction. A design that only carries type names and diagnostics can pass the written architecture while failing exact `transformed_expression` reproduction.

### 6. Route Safety

**Assessment:** Pass

There are no web routes or endpoint dispatch surfaces in this design. The relevant routing concern is AST dispatch order, and the design pins the two load-bearing orders: `FeatureChainExpression` before `OperatorExpression`, and literal/null before invocation.

### 7. Bets & Decisions Integrity

**Assessment:** Concerns

The key bets are mostly real bets about the boundary. B2 is the riskiest and correctly states what fails if the neutral tree is insufficient.

There is one hidden bet: existing expression-helper TYPE_MAP coverage is strong enough to stand in for transitive aggregation dependencies. The current tree does not appear to have a source-inventory test for expression helpers like `reconstruct_expression`, `is_literal_node`, or `extract_feature_chain_segments`. That makes B4 weaker than the design admits.

### 8. Reader Comprehension

**Assessment:** Pass

The design gives a clear mental model before the mechanisms: shared decomposition explains SysML facts; sysml-codegen decides generated Python and pipeline assembly. The review-relevant behavior pins are easy to find. The main gaps are substance, not prose.

---

## Issues by Severity

### Critical

- Profile-loop close-out is deferred instead of designed. The design does not disposition the seven aggregation-profile rows as `EXISTING`, `NEW RULE`, `FILED`, or `NO-OP`, nor does it give filed rows exact rule, fixture shape, severity, rationale, and backlog ID. This leaves `REQ-AGG-21` unproven before implementation. - Spec Compliance

### Major

- TYPE_MAP transitive coverage relies on tests that are not present. The design cites existing expression and hierarchy helper inventory tests, but the current agentic-mbse tree shows the hierarchy inventory test and broad adapter coverage, not an expression-helper source-inventory test. The design must require adding an expression-helper inventory test or extending the aggregation inventory to include the imported helper sources. - Pattern Consistency

- Neutral node schemas are too loose for exact reproduction. The design says neutral node types are implementation details, but exact local `transformed_expression` reproduction depends on specific fields for operators, invocations, literals, unsupported nodes, wrapper disposition, and sum term indexing. Without those fields stated, implementation could satisfy the architecture and still lose byte identity. - Data Structure Clarity

### Minor

- The design says shared `SumTerm` instances have multiplicity fields always `None` and sysml-codegen fills them. It should state whether the adapter creates new `SumTerm` objects or mutates copied shared objects. New objects are safer because shared decomposition results stay neutral if inspected in tests. - Abstraction Quality

---

## Recommendations

1. Add a design-level aggregation-profile disposition table. Each row should close as `EXISTING`, `NEW RULE`, `FILED`, or `NO-OP`; filed rows should carry the exact backlog ID and required rule metadata from the spec.
2. Tighten the TYPE_MAP strategy. Either add a source-inventory test for expression helpers used by aggregation, or make the aggregation inventory traverse the imported helper modules and prove all adapter strings after resetting `_type_map`.
3. Make the neutral node contract explicit enough to audit exact rendering. Name the fields required for operator, invocation, literal, unsupported, wrapper, and sum nodes.
4. State that local multiplicity application creates local `SumTerm` instances rather than mutating the shared neutral result, unless there is a concrete reason to mutate.

---

## Re-Review: 2026-07-08

**Scope:** Narrow re-review of the patched design against the prior Revise findings only, plus a check for blockers introduced by the patch.

**Result:** The prior blockers are resolved. The patched design now closes the profile loop at design time, requires a combined TYPE_MAP source inventory over aggregation plus imported expression helpers, makes neutral node contracts explicit enough to preserve local rendering behavior, and states that sysml-codegen creates new local `SumTerm` instances instead of mutating neutral decomposition results.

**Finding status:**

- **Profile-loop close-out resolved:** The design now includes a seven-row aggregation-profile disposition table. Filed rows include exact rule, fixture shape, severity, rationale, and backlog ID. Existing rows cite the owning expression-profile rows.
- **TYPE_MAP transitive coverage resolved:** The design now requires inventory over both `agentic_mbse.sysml.aggregation` and imported `agentic_mbse.sysml.expression` helper source, with `_type_map` reset or bypassed. This removes the prior reliance on a non-existent expression-helper inventory test.
- **Neutral node schema resolved:** The design now names load-bearing fields for operator, invocation, literal, unsupported, sum, feature-chain, and feature-reference nodes. That is enough design contract for the local adapter to reproduce current `transformed_expression` behavior without moving Python spelling into agentic-mbse.
- **Multiplicity mutation concern resolved:** The local adapter now creates new local `SumTerm` instances with multiplicity fields and must not mutate shared neutral decomposition results.

**New blocking issues introduced:** None found. The validation section still uses the shorthand "direct TYPE_MAP inventory," but the dedicated TYPE_MAP strategy is explicit about the combined source inventory and controls the implementation requirement.

---

## Resolutions

- **Profile-loop close-out:** Resolved by adding the design-level disposition table.
- **TYPE_MAP transitive coverage:** Resolved by requiring combined source inventory over aggregation and imported expression helpers.
- **Neutral node schemas:** Resolved by naming the load-bearing node fields.
- **Multiplicity mutation:** Resolved by requiring new local `SumTerm` instances during local multiplicity application.

---

**Overall:** Approve
**Next Steps:** Proceed to `my-plan` for implementation. The reviewer does not edit the design.
