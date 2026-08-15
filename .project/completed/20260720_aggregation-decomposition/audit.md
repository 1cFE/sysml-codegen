# Audit: Aggregation Decomposition and Compatibility Gates

**Verdict:** Certify
**Audited:** 2026-07-08
**Branch:** push-down-item1-expression
**Commit:** fb7e13a

---

## Summary

Item 4 satisfies the approved spec and design. Shared aggregation decomposition now lives in
agentic-mbse as neutral SysML facts, while sysml-codegen keeps Python rendering, multiplicity
application, alias enrichment, warnings, and `AggregationExpressionData` assembly.

No blocking findings were found. The audit verified the high-risk compatibility edges: no
sysml-codegen imports in shared sysml/validation code, no codegen containers or pipeline identifiers
in the shared API, permissive `sum(filter(...))` behavior, literal-before-invocation dispatch,
feature-chain-before-operator dispatch, filed aggregation-profile rows, fixture byte identity, and
no item-level PR closeout.

## Findings

### Plan completion

All five phases are verified complete.

- Phase 1 verified: shared term dataclasses are in agentic-mbse, neutral decomposition is implemented,
  wrapper/unsupported/literal/operator facts are covered, and the combined TYPE_MAP inventory covers
  aggregation plus expression helper source (`/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/data_models.py:84`,
  `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/aggregation.py:65`,
  `/home/reid/1cfe/agentic-mbse/tests/test_sysml/test_aggregation.py:82`,
  `/home/reid/1cfe/agentic-mbse/tests/test_sysml/test_aggregation.py:228`).
- Phase 2 verified: no duplicate Level-6 rule was added; the three approved FILED rows exist with
  exact rule, fixture shape, severity, rationale, and backlog ID
  (`/home/reid/1cfe/agentic-mbse/.project/backlog/BACKLOG.md:450`).
- Phase 3 verified: sysml-codegen re-exports shared term classes, keeps local codegen containers,
  delegates raw aggregation decomposition, creates local `SumTerm` instances for multiplicity, and
  preserves field-level builder behavior (`src/sysml_codegen/extraction/data_models.py:83`,
  `src/sysml_codegen/extraction/hierarchy_resolver.py:229`,
  `src/sysml_codegen/extraction/hierarchy_resolver.py:334`,
  `tests/unit/test_hierarchy_resolver.py:1173`).
- Phase 4 verified: committed literal and alias controls are still tests, dispatch invariants now
  cover the moved shared walker, and `git diff -- tests/fixtures` is empty
  (`tests/conformance/test_agg_literal_dispatch.py:37`,
  `tests/unit/test_hierarchy_resolver.py:1374`,
  `tests/conformance/test_ast_dispatch_invariant.py:274`).
- Phase 5 verified: full-suite and lint evidence is recorded in the plan. I reran focused audit
  gates: sysml-codegen builder/model/literal/dispatch subset `190 passed`; agentic-mbse aggregation
  suite `12 passed`. Full suites and mypy baseline caveats remain as recorded in the plan.

### Spec conformance

- Shared decomposition coverage: met. `decompose_aggregation_expression` handles sum, singleton,
  local, wrapper, literal/null, unsupported node, unsupported invocation, and unsupported operator
  shapes as neutral nodes and diagnostics (`/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/aggregation.py:205`,
  `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/aggregation.py:220`).
- Shared term classes and identity: met. `SumTerm`, `SingletonTerm`, and `LocalTerm` live in
  agentic-mbse and sysml-codegen re-exports the same runtime class objects
  (`/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/data_models.py:84`,
  `src/sysml_codegen/extraction/data_models.py:83`,
  `tests/conformance/test_data_models.py:357`).
- Shared API minimum neutral payload and no-leak boundary: met. The result exposes a root tree,
  ordered terms, diagnostics, wrapper facts, and source refs, with no `input_channels`,
  `entry_points`, aliases, Python transformed expression, or codegen container
  (`/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/aggregation.py:166`,
  `/home/reid/1cfe/agentic-mbse/tests/test_sysml/test_aggregation.py:70`,
  `/home/reid/1cfe/agentic-mbse/tests/test_sysml/test_aggregation.py:98`).
- Local `build_aggregation_expression` compatibility: met. sysml-codegen rejects non-expression or
  missing-AST redefinitions, renders neutral nodes locally, fills multiplicity locally, preserves
  missing-multiplicity behavior, and returns local `AggregationExpressionData`
  (`src/sysml_codegen/extraction/hierarchy_resolver.py:229`,
  `src/sysml_codegen/extraction/hierarchy_resolver.py:268`,
  `src/sysml_codegen/extraction/hierarchy_resolver.py:358`,
  `tests/unit/test_hierarchy_resolver.py:984`,
  `tests/unit/test_hierarchy_resolver.py:1051`).
- Fixture byte identity: met. `git diff -- tests/fixtures` is empty in sysml-codegen.
- TYPE_MAP coverage: met. The source inventory covers adapter strings used by aggregation and the
  imported expression helper source, resetting adapter state in the test
  (`/home/reid/1cfe/agentic-mbse/tests/test_sysml/test_aggregation.py:208`,
  `/home/reid/1cfe/agentic-mbse/tests/test_sysml/test_aggregation.py:228`).
- Aggregation-profile loop: met. Sum, wrapper, and literal rows are FILED in the agentic-mbse
  backlog; singleton, local, unsupported-node, and operator shapes remain covered by existing
  expression-profile rows as designed (`/home/reid/1cfe/agentic-mbse/.project/backlog/BACKLOG.md:450`).
- Acceptance coverage: met. Direct builder fields, unsupported invocation/operator rendering,
  literal fixture behavior, alias behavior, data-model identity, dispatch invariants, and downstream
  consumers are covered by the recorded gates and focused rerun
  (`tests/unit/test_hierarchy_resolver.py:1117`,
  `tests/unit/test_hierarchy_resolver.py:1139`,
  `tests/unit/test_hierarchy_resolver.py:1476`,
  `tests/conformance/test_data_models.py:357`).
- Full landing gates: met with caveat. Recorded full suites pass; touched-file ruff and
  sysml-codegen `ruff check src/` are clean. Both project-wide mypy runs still fail at unchanged
  pre-existing baselines: agentic-mbse 107 errors, sysml-codegen 98 errors.
- Review sequencing: met. Spec review and design review both reached Approved after revisions.
- No item-level PR closeout: met. No PR preparation or item closeout was performed.

All tagged requirements REQ-AGG-01 through REQ-AGG-25 are satisfied for this item. Non-goals were
respected: Python rendering, aliases, local containers, design overrides, scoping, graph resolution,
template detection, virtual binding, snapshot schema changes, fixture recapture, and PR closeout did
not move into the shared agentic-mbse aggregation API.

### Design conformance

Implementation follows the approved design.

- The shared system is an aggregation decomposer, not a compiler: it imports agentic-mbse helpers
  and returns neutral dataclasses (`/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/aggregation.py:12`,
  `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/aggregation.py:65`).
- sysml-codegen owns Python operator spelling and local rendering through `AGG_PYTHON_OPS` and
  `_render_neutral_aggregation_node` (`src/sysml_codegen/extraction/hierarchy_resolver.py:50`,
  `src/sysml_codegen/extraction/hierarchy_resolver.py:268`).
- The required dispatch order is preserved and tested: feature chains before operators, literals
  before invocation (`/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/aggregation.py:226`,
  `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/aggregation.py:263`,
  `tests/conformance/test_ast_dispatch_invariant.py:274`).
- Permissive wrapper behavior is preserved. `sum(filter(module.cost))` stays supported and does not
  set `has_unsupported_nodes` (`/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/aggregation.py:276`,
  `tests/unit/test_hierarchy_resolver.py:1374`).
- Alias collection remains local and preserves the dotted-leaf edge
  (`src/sysml_codegen/extraction/hierarchy_resolver.py:60`,
  `src/sysml_codegen/extraction/hierarchy_resolver.py:549`,
  `tests/unit/test_hierarchy_resolver.py:1476`).

### Code integrity

No issues found.

The new split keeps contracts readable: shared decomposition returns one neutral result, and the
local adapter renders that result into codegen fields. I did not find policy hidden in shared
utilities, broad silent fallbacks, unused compatibility shims beyond the intentionally retained
`_walk_aggregation_ast` compatibility wrapper, or codegen identifiers leaking into agentic-mbse.

---

## Certification

Checked:

- `.project/active/aggregation-decomposition/{spec,design,plan}.md`
- `.project/backlog/epic_push_down.md`
- `.project/CURRENT_WORK.md`
- Changed sysml-codegen source and tests listed in the stage input
- Changed agentic-mbse source, tests, and backlog rows listed in the stage input
- No `sysml_codegen` imports under `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml` or
  `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/validation`
- No sysml-codegen fixture diff

Audit rerun:

- `uv run pytest tests/unit/test_hierarchy_resolver.py tests/conformance/test_data_models.py tests/conformance/test_agg_literal_dispatch.py tests/conformance/test_ast_dispatch_invariant.py`
  -> `190 passed`
- `cd /home/reid/1cfe/agentic-mbse && uv run pytest tests/test_sysml/test_aggregation.py`
  -> `12 passed`
- `git diff -- tests/fixtures` -> empty

Marked:

- Item spec success criteria complete.
- Item plan checkboxes complete where verified or satisfied as documented no-op.
- PUSH-DOWN epic Item 4 heading and Item 4 success criteria complete.
- `CURRENT_WORK.md` Item 4 status as certified.

Left open:

- Top-level PUSH-DOWN epic success criteria are not marked here because this is an Item 4 audit, not
  an epic audit.
- No pre_pr or PR closeout was performed.

---

## Addendum — 2026-07-10 (remediation + recorded deviation)

Independent epic audit findings closed for this item:
- **Recorded deviation (no code change): unary-minus render.** The pre-move code compared
  the raw operator enum (`syside.Operator.Minus == "-"` is False), so real nodes rendered
  `-(x)`; the shared decompose str-normalizes the operator, so the adapter now renders
  `-x`. Python-semantically identical, unpinned edge, matches the previously *tested*
  behavior; accepted as an improvement rather than reverted.
- `**` added to shared `SUPPORTED_OPERATORS` (codegen `AGG_PYTHON_OPS` supports it via
  `OPERATOR_MAP`; the omission would have made a future profile rule false-positive on a
  compilable `x ** y` aggregation).
- Dead field `InvocationNode.wrapper_disposition` (never assigned) removed.
- `test_combined_type_map_inventory_is_mapped` now checks the inventory against the REAL
  `SysideAdapter._get_type_map()` instead of a fake map built from the inventory.
