# Spec Review: Aggregation Decomposition and Compatibility Gates

**Spec:** `.project/active/aggregation-decomposition/spec.md`
**Contract:** `/home/reid/.agents/skills/my-spec/SKILL.md`
**Review File:** `.project/active/aggregation-decomposition/spec-review.md`
**Date:** 2026-07-08

---

## Reality Check

Sound with concerns. The spec is about the right PUSH-DOWN Item 4 and preserves the core epic boundary: neutral aggregation decomposition moves to agentic-mbse, while Python rewriting, aliases, and pipeline assembly stay in sysml-codegen. The problem is not direction. The problem is that several contract edges are still too vague for design and audit to prove exact behavior after the current `_walk_aggregation_ast` split.

---

## Audit

### Lens 1 — Faithfulness

**L1-1 · Rewrite request:** The spec says the shared API owns "unsupported-node reporting, and operator-shape reporting" while sysml-codegen keeps Python spelling, but it never states that the shared facts must preserve enough expression structure for sysml-codegen to rebuild the current `transformed_expression` exactly. Today the walker returns Python-ish expression text from every branch while collecting terms in the same context (`src/sysml_codegen/extraction/hierarchy_resolver.py:262`). The spec must require a neutral expression representation or equivalent facts that let the local adapter reproduce current expression text without moving Python source strings into agentic-mbse.

**L1-2 · Direct claim:** The wrapper requirement overstates current wrapper discipline. `_unwrap_invocation` unwraps any invocation with operands once called, regardless of function name, and only the outer non-sum branch checks `_KNOWN_WRAPPER_FUNCTIONS` (`src/sysml_codegen/extraction/hierarchy_resolver.py:211`, `src/sysml_codegen/extraction/hierarchy_resolver.py:376`). Inside `sum(...)`, `sum(filter(module.cost))` will be unwrapped by the current code path rather than treated as unsupported. The spec's profile row says that shape warns (`.project/active/aggregation-decomposition/spec.md:131`). Either the spec must define this as an intended behavior change needing separate review, or it must require preservation of the current permissive sum-operand unwrap behavior.

**L1-3 · Rewrite request:** Alias behavior is named as local, but not as a compatibility obligation. Current alias collection has pinned edge behavior: a CHAIN sibling whose dotted source leaf matches the aggregation attribute becomes an alias even if the dotted part is different (`src/sysml_codegen/extraction/hierarchy_resolver.py:590`, `tests/unit/test_hierarchy_resolver.py:1367`). The spec should require sysml-codegen alias collection, including this pinned dotted-leaf behavior, to remain byte-identical or explicitly create a reviewed behavior-change item.

### Lens 2 — Problem & Approach

**L2-1 · If-then tradeoff:** The spec requires `SumTerm`, `SingletonTerm`, and `LocalTerm` to move, but leaves the rest of the neutral result shape open (`.project/active/aggregation-decomposition/spec.md:152`). That is fine if the design can choose any neutral model, but risky if audit needs to prove no Python/pipeline leakage. The spec should add a requirement for the minimum neutral payload: terms, literal/operator nodes or facts, unsupported diagnostics, wrapper disposition, and enough ordering/structure to rebuild the local adapter output. Without that, two good designs could both satisfy the words while one cannot reproduce `AggregationExpressionData`.

**L2-2 · Direct claim:** The profile-loop table is more prescriptive than the epic in a way that may force shallow new rules. It requires Sum, Singleton, Local, and Wrapper rows to be `NEW RULE or FILED` (`.project/active/aggregation-decomposition/spec.md:128`), excluding `EXISTING` and `NO-OP`, while the epic only requires each pushed-down helper to power a rule or file a named backlog item. This should be loosened or justified. Item 3's certified profile close-out allowed filing rows when codegen policy was too local; Item 4 should not accidentally require validation rules that duplicate existing expression checks.

### Lens 3 — Pipeline Risk

**L3-1 · Rewrite request:** The `AggregationExpressionData` compatibility criterion is too broad to audit. It says `build_aggregation_expression` must reproduce existing behavior exactly (`.project/active/aggregation-decomposition/spec.md:34`), but the behavior includes concrete fields and edge cases: `owning_part_name` sanitization, `raw_expression_text`, `transformed_expression`, term lists, `input_channels`, `entry_points`, `has_unsupported_nodes`, default `compilability`, empty `aliases` before orchestration, and source metadata defaults (`src/sysml_codegen/extraction/data_models.py:301`). The spec should name the fields or require a field-level before/after assertion for representative instances.

**L3-2 · Rewrite request:** The targeted test requirement names broad surfaces but not the specific implementation-site inventory needed for this move (`.project/active/aggregation-decomposition/spec.md:98`). It should require tests or assertions covering the current call sites and consumers that can regress during the split: direct builder behavior, hierarchy orchestration warning and alias enrichment, data-model identity, dispatch-order invariants, scoping consumers, input resolver consumers, and fixture byte identity for `agg_literal_probe` and `alias_agg_probe`.

**L3-3 · Direct claim:** TYPE_MAP coverage is testable from source inventory, but the spec leaves a loophole for indirect helper calls. It only inventories direct string literals passed by moved code to adapter methods (`.project/active/aggregation-decomposition/spec.md:85`). If the moved module imports shared expression helpers that themselves call `SysideAdapter.is_instance`, those adapter strings can become runtime dependencies of aggregation without appearing in the moved aggregation source. The spec should require either a transitive helper inventory or an explicit statement that shared helper TYPE_MAP coverage is already pinned by existing tests and referenced by this item.

**L3-4 · Rewrite request:** Literal behavior is partly covered, but the acceptance shape is incomplete. The spec covers literal-before-invocation and the profile distinction between `sum(module.cost) + 5.0` and `sum(5.0)` (`.project/active/aggregation-decomposition/spec.md:72`, `.project/active/aggregation-decomposition/spec.md:132`). It should also require the sysml-codegen adapter to preserve the current transformed expression and `has_unsupported_nodes=False` behavior for the committed `agg_literal_probe` fixture, because that fixture was added specifically to pin this bug class (`tests/fixtures/agg_literal_probe/library.sysml:15`).

**L3-5 · Rewrite request:** Unsupported invocation and unsupported operator behavior are not concrete enough. Current unsupported invocations set `has_unsupported`, still walk operands, and return reconstructed call text; unsupported operators set `has_unsupported` and return the raw operator surrounded by spaces (`src/sysml_codegen/extraction/hierarchy_resolver.py:238`, `src/sysml_codegen/extraction/hierarchy_resolver.py:382`). The spec should require these exact local-adapter outcomes or explicitly defer their representation to design while naming the required externally visible behavior.

**L3-6 · Rewrite request:** Fixture byte identity is stated for `tests/fixtures`, but generated-output byte identity is not tied to a path or command (`.project/active/aggregation-decomposition/spec.md:36`). The spec should name what "generated-output byte identity" means in this repo for Item 4, or drop the phrase and rely on `tests/fixtures`. As written, audit cannot tell whether missing generated files are a failure.

### Lens 4 — Hygiene

**L4-1 · Rewrite request:** Some requirements are tagged `[HARD]` even though they are process obligations rather than system constraints. `REQ-AGG-16`, `REQ-AGG-17`, and the review/PR success criteria are important gates, but they are not product or interface requirements (`.project/active/aggregation-decomposition/spec.md:98`, `.project/active/aggregation-decomposition/spec.md:102`). Move them into success criteria or validation notes so the requirements list remains the design contract.

### Lens 5 — Reader Comprehension

**L5-1 · Rewrite request:** The phrase "neutral aggregation facts" carries too much of the spec. A reader can see what must not be in the shared API, but not what must be in it. Add a short definition near the Problem or first requirement: neutral facts are the SysML-level decomposition outputs that carry expression shape, terms, wrappers, literals, operators, and unsupported diagnostics without Python spelling or pipeline identifiers.

---

## Engagement Summary

**Overall take:** Revise. The spec has the right boundary and should not be reworked, but it needs sharper acceptance around the split between neutral decomposition and local Python/pipeline assembly. The biggest risk is that design can satisfy the current wording while still losing enough structure to make `AggregationExpressionData` reproduction, profile disposition, or fixture identity unreviewable.

**Here's what I need you to weigh in on:**

1. **[L1-1, L2-1]** Define the minimum neutral result payload. The spec must say what facts move, not only what strings and identifiers stay local.
2. **[L1-2]** Decide whether unsupported wrappers inside `sum(...)` should preserve current permissive unwrap behavior or become a reviewed behavior change.
3. **[L1-3, L3-1]** Require exact compatibility for local `AggregationExpressionData` and alias behavior, including pinned dotted-leaf alias matching.
4. **[L2-2]** Fix the profile table so it allows legitimate `EXISTING` or `NO-OP` dispositions where shared expression or hierarchy rules already cover a shape.
5. **[L3-2, L3-4, L3-5]** Make acceptance test coverage concrete: current builder fields, unsupported behavior, literal probe, alias probe, orchestration warnings, and downstream consumers.
6. **[L3-3]** Close the TYPE_MAP proof loophole by requiring transitive helper coverage or an explicit dependency on existing shared-helper inventory tests.

---

## Re-Review: 2026-07-08

**Scope:** Narrow re-review of the patched spec against the prior must-fix findings. I did not reopen the full spec beyond checking for new blocking issues introduced by the patch.

**Result:** The prior blocking findings are resolved. The patched spec now defines the minimum neutral payload, preserves current permissive wrapper behavior inside `sum(...)`, makes field-level `AggregationExpressionData` and dotted-leaf alias compatibility explicit, allows all four profile dispositions, adds concrete validation coverage, closes direct and transitive TYPE_MAP coverage, and clarifies the byte-identity gate as `git diff -- tests/fixtures`.

**Finding status:**

- **[L1-1, L2-1, L5-1] Resolved:** Neutral aggregation facts are now defined in the Problem section and success criteria, with typed terms, literal/operator facts, wrapper disposition, ordering/structure, and unsupported diagnostics required (`spec.md:25`, `spec.md:37`, `spec.md:84`).
- **[L1-2] Resolved:** The spec now preserves current permissive wrapper behavior inside `sum(...)` and separates stricter wrapper warnings into profile-only future work or a separate behavior-change item (`spec.md:92`, `spec.md:184`).
- **[L1-3, L3-1] Resolved:** The spec now requires field-level `AggregationExpressionData` compatibility and pins local dotted-leaf alias behavior (`spec.md:41`, `spec.md:112`, `spec.md:117`, `spec.md:150`).
- **[L2-2] Resolved:** The profile table now allows `EXISTING`, `NEW RULE`, `FILED`, or `NO-OP` for every row, and each row avoids duplicate diagnostics when existing expression or hierarchy profile checks already own the shape (`spec.md:175`, `spec.md:181`).
- **[L3-2, L3-4, L3-5] Resolved:** Validation requirements now name builder field coverage, unsupported invocation/operator behavior, `agg_literal_probe`, `alias_agg_probe`, orchestration warnings and alias enrichment, dispatch invariants, scoping/input-resolver consumers, full gates, and fixture byte identity (`spec.md:148`).
- **[L3-3] Resolved:** TYPE_MAP coverage now includes direct moved-code inventory plus transitive shared-helper coverage or explicit reliance on existing helper inventory tests (`spec.md:47`, `spec.md:120`, `spec.md:130`).
- **[L3-6] Resolved:** Byte identity is now scoped to `git diff -- tests/fixtures`, with `tests/fixtures/baseline_outputs` called out as the committed generated-output location (`spec.md:44`, `spec.md:170`).
- **[L4-1] Resolved enough:** The spec moved detailed process coverage into `Validation Requirements`. Some process gates remain in Success Criteria, which is appropriate for this pipeline stage and no longer pollutes the tagged `[HARD]` requirement list.

**New blocking issues introduced:** None found.

---

## Resolutions

Re-review resolved the prior findings. No user decision remains required before design.

---

**Verdict:** Approve
**Next Steps:** Proceed to `my-design` for PUSH-DOWN Item 4. Do not do item-level PR closeout; continue the whole PUSH-DOWN epic flow.
