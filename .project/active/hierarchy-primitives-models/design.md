# Design: Hierarchy Primitives and Data Models

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-07-08 16:19 PDT
**Branch:** push-down-item1-expression
**Commit:** e01361b

## Overview

Move the neutral hierarchy primitives into `agentic_mbse.sysml.hierarchy`: classifying one
`ReferenceUsage` redefinition, scanning owned-member redefinitions, scanning child multiplicities,
and hosting the three primitive dataclasses. sysml-codegen keeps hierarchy policy and orchestration
local, while permanent compatibility paths re-export the shared class objects and delegate the two
primitive extraction functions.

## Related Artifacts

- Spec: `.project/active/hierarchy-primitives-models/spec.md`
- Spec review: `.project/active/hierarchy-primitives-models/spec-review.md`
- Epic: `.project/backlog/epic_push_down.md`
- Current context: `.project/CURRENT_WORK.md`
- Prior audit: `.project/active/expression-reconstruction-push-down/audit.md`
- Prior audit: `.project/active/qualified-name-utility-split/audit.md`
- sysml-codegen source: `src/sysml_codegen/extraction/hierarchy_resolver.py`
- sysml-codegen models: `src/sysml_codegen/extraction/data_models.py`
- sysml-codegen snapshot loader: `src/sysml_codegen/snapshot/loader.py`
- agentic-mbse shared models: `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/data_models.py`
- agentic-mbse adapter: `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/syside_adapter.py`
- agentic-mbse validation: `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/validation/level6_architecture.py`
- agentic-mbse backlog: `/home/reid/1cfe/agentic-mbse/.project/backlog/BACKLOG.md`

## Research Findings

- The primitive classifier is `_extract_single_redefinition`. It checks `ReferenceUsage`, reads the
  first owned redefinition, detects deep `chaining_features`, classifies literal, chain, and
  expression RHS shapes, and returns `RedefinitionData`
  (`src/sysml_codegen/extraction/hierarchy_resolver.py:85`).
- `extract_redefinitions` is a thin owned-member scanner over that classifier
  (`src/sysml_codegen/extraction/hierarchy_resolver.py:175`). It is safe to move because it only
  builds the owning QN and iterates `owned_members`.
- `extract_design_overrides` uses the same classifier but adds design policy: design-level
  `PartUsage` scan, part-redefines detection, and plain-usage filtering to literal-only RHS
  (`src/sysml_codegen/extraction/hierarchy_resolver.py:198`,
  `src/sysml_codegen/extraction/hierarchy_resolver.py:209`). That stays local.
- `extract_multiplicities` scans child `PartUsage` members, excludes singletons, reads
  `cached_lower_bound`, extracts `upper_bound.referent.name`, and preserves referent defaults
  (`src/sysml_codegen/extraction/hierarchy_resolver.py:252`).
- Aggregation decomposition starts at `build_aggregation_expression` and uses
  `AggregationExpressionData`, `SumTerm`, `SingletonTerm`, and `LocalTerm`
  (`src/sysml_codegen/extraction/hierarchy_resolver.py:523`). That is Item 4 scope, not this move.
- Usage-type indexing, most-specific selection, and part-usage name collection live in
  `extract_hierarchy_data` and `_index_usage_level_retypes`
  (`src/sysml_codegen/extraction/hierarchy_resolver.py:574`,
  `src/sysml_codegen/extraction/hierarchy_resolver.py:632`). These are codegen resolution policy.
- The three moved models are currently standard-library dataclasses or enum/dataclass pairs in
  `data_models.py`: `RedefinitionType`, `RedefinitionData`, and `MultiplicityData`
  (`src/sysml_codegen/extraction/data_models.py:237`,
  `src/sysml_codegen/extraction/data_models.py:245`,
  `src/sysml_codegen/extraction/data_models.py:270`).
- `HierarchyExtractionResult` includes design overrides, aggregation expressions, warnings,
  `part_usage_names`, and `usage_type_map` (`src/sysml_codegen/extraction/data_models.py:343`).
  It stays in sysml-codegen because it bundles codegen orchestration products.
- Snapshot loading reconstructs `RedefinitionData`, `MultiplicityData`, and `HierarchyExtractionResult`
  through the existing sysml-codegen import path (`src/sysml_codegen/snapshot/loader.py:303`,
  `src/sysml_codegen/snapshot/loader.py:321`, `src/sysml_codegen/snapshot/loader.py:359`).
  Re-export identity preserves this path without a snapshot schema change.
- agentic-mbse already hosts the needed expression and qualified-name helpers:
  `reconstruct_expression`, `extract_feature_chain_name`, `extract_feature_reference_name`,
  `is_literal_node`, and `extract_literal_value`
  (`/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/expression.py:418`,
  `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/expression.py:548`,
  `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/expression.py:570`,
  `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/expression.py:640`), and
  `sanitize_name` plus `build_element_qualified_name`
  (`/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/qualified_names.py:13`,
  `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/qualified_names.py:33`).
- `SysideAdapter.TYPE_MAP` already includes the moved primitive strings: `ReferenceUsage`,
  `PartUsage`, `FeatureChainExpression`, and `FeatureReferenceExpression`
  (`/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/syside_adapter.py:173`,
  `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/syside_adapter.py:184`,
  `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/syside_adapter.py:198`).
- agentic-mbse Level 6 already contains one hierarchy-adjacent profile check for dropped
  `AttributeUsage` expression redefinitions
  (`/home/reid/1cfe/agentic-mbse/src/agentic_mbse/validation/level6_architecture.py:788`) and an
  existing missing-instantiation rule
  (`/home/reid/1cfe/agentic-mbse/src/agentic_mbse/validation/level6_architecture.py:680`).

## Core Concept

The shared system is a hierarchy fact extractor, not a hierarchy resolver. It answers two neutral
questions from a SysML element: which owned `ReferenceUsage` members redefine attributes, and which
child `PartUsage` members carry multiplicity facts. Those answers are reusable in validation and
codegen. sysml-codegen then composes them with design override policy, usage-type indexing,
aggregation rewriting, scoping, and pipeline construction. This keeps the dependency direction
clean: agentic-mbse owns SysML facts; sysml-codegen owns generated-package behavior.

## Key Bets

- **B1.** Redefinition and multiplicity extraction are SysML facts independent of generated module
  policy. *If false -> moving them would pull codegen resolution behavior into agentic-mbse and
  break the PUSH-DOWN boundary.*
- **B2.** Field-identical dataclass re-exports are enough for snapshot and downstream compatibility.
  *If false -> consumers would observe different serialized fields or class identity despite unchanged
  JSON.*
- **B3.** The moved primitive surface uses only adapter type strings already mapped in
  agentic-mbse. *If false -> live SysIDE extraction can raise under the adapter hard-error contract.*
- **B4.** Checking-profile rows that need usage-type indexing can be filed without weakening this
  item, because the spec explicitly keeps those indexing surfaces in sysml-codegen. *If false -> the
  item cannot close SC-G without moving policy it is required to leave local.*

## Key Decisions

- **D1.** Add `agentic_mbse.sysml.hierarchy` with this public API:
  `RedefinitionType`, `RedefinitionData`, `MultiplicityData`, `extract_redefinitions`,
  `extract_multiplicities`, and `classify_redefinition`. *Rejected: moving the whole resolver,
  because design overrides, usage indexing, aggregation, and orchestration are codegen policy.*
- **D2.** Expose `classify_redefinition(member, owning_qn)` as a public primitive helper. It classifies
  one `ReferenceUsage` and replaces `_extract_single_redefinition`. *Rejected: keeping it private,
  because sysml-codegen design overrides need the same primitive classifier without duplicating the
  body.*
- **D3.** Move `RedefinitionType`, `RedefinitionData`, and `MultiplicityData` into
  `agentic_mbse.sysml.data_models`, then re-export them from `agentic_mbse.sysml.hierarchy`.
  *Rejected: defining them only in `hierarchy.py`, because `AttributeInfo` established
  `data_models.py` as the shared model home.*
- **D4.** In `sysml_codegen.extraction.data_models`, import and re-export the exact shared class
  objects. *Rejected: subclassing or local mirror dataclasses, because object identity and field
  identity must both hold.*
- **D5.** Keep `sysml_codegen.extraction.hierarchy_resolver.extract_redefinitions` and
  `extract_multiplicities` as wrapper functions that delegate to shared functions. *Rejected: direct
  function aliasing, because wrapper delegation gives stable local docstrings/import paths and lets
  tests spy on the shared function without constraining future local instrumentation.*
- **D6.** Leave `extract_design_overrides` in sysml-codegen, but make it call the shared
  `classify_redefinition`. *Rejected: moving design override extraction, because its outer scan and
  plain-usage RHS filter are explicitly codegen policy.*
- **D7.** Verify TYPE_MAP from an implementation-site inventory of moved `SysideAdapter.is_instance`
  and `elements_of_type` string literals only. *Rejected: checking orchestration strings like
  `PartDefinition`, because that would blur the local/shared boundary.*
- **D8.** Do not recapture snapshots. Byte-identity gates must show no fixture churn; any fixture diff
  is a defect unless a separate reviewed behavior change is introduced. *Rejected: opportunistic
  recapture, because this is a move and re-export item.*

## Architecture

The target shape has four layers.

1. Shared data models:
   `agentic_mbse.sysml.data_models` defines the three moved class objects as standard-library
   dataclasses or enum/dataclass pairs. `AttributeInfo` stays where it is. The new models use the
   same imports the fields need: `dataclass`, `field`, `Path`, `Any`, and `Enum`.

2. Shared primitive extraction:
   `agentic_mbse.sysml.hierarchy` imports the shared models, `SysideAdapter`, shared expression
   helpers, and shared qualified-name helpers. It owns only:
   `classify_redefinition`, `extract_redefinitions`, and `extract_multiplicities`.

3. sysml-codegen compatibility:
   `sysml_codegen.extraction.data_models` re-exports the exact shared class objects while retaining
   codegen models. `sysml_codegen.extraction.hierarchy_resolver` imports the shared primitive module
   and keeps local wrapper functions for `extract_redefinitions` and `extract_multiplicities`.

4. sysml-codegen policy:
   The resolver still owns design override extraction, hierarchy orchestration, usage indexing,
   aggregation rewriting, warnings, and construction of `HierarchyExtractionResult`.

The data flow stays the same for callers. Live extraction enters
`extract_hierarchy_data`, which calls local wrappers for redefinitions and multiplicities. Those
wrappers delegate to agentic-mbse. Then sysml-codegen continues with local aggregation, design
override, and indexing steps. Snapshot loading still imports models from
`sysml_codegen.extraction.data_models`, but those names now point at the shared class objects.

## Required Invariants

- agentic-mbse must not import `sysml_codegen`.
- The moved dataclasses must keep exact field names, order, defaults, default factories, and value
  types:
  `RedefinitionData(owning_part_qn, attribute_name, redefinition_type, literal_value, source_path,
  expression_ast, expression_text, target_path, is_deep_path, source_file, source_line)` and
  `MultiplicityData(part_usage_name, owning_part_def_qn, count, count_attribute_name, default_value)`.
- `sysml_codegen.extraction.data_models.RedefinitionType is
  agentic_mbse.sysml.hierarchy.RedefinitionType`, and the same identity rule applies to
  `RedefinitionData` and `MultiplicityData`.
- `extract_redefinitions` scans only owned members. It must not call `elements_of_type`.
- `extract_multiplicities` scans only child `PartUsage` owned members and excludes singleton usages.
- `classify_redefinition` skips type-only redefinitions with no value expression.
- Literal RHS classification must use the literal-node predicate, not the older agentic-mbse
  "static expression" meaning of `is_literal_expression`.
- Design override policy remains local: design-level `PartUsage` enumeration, plain-usage filtering,
  and override precedence do not move.
- No `HierarchyExtractionResult` field moves to agentic-mbse.
- Snapshot JSON shape and generated baselines remain byte-identical.

## Component Overview

- `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/data_models.py`: shared home for the moved
  enum/dataclasses.
- `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/hierarchy.py`: shared primitive extraction
  module.
- `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/__init__.py`: package-level re-exports for
  the hierarchy API.
- `/home/reid/1cfe/agentic-mbse/tests/test_sysml/test_hierarchy.py`: moved primitive behavior and
  dataclass field tests.
- `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/validation/level6_architecture.py`: optional
  hierarchy-profile rules that can be implemented from shared facts.
- `src/sysml_codegen/extraction/data_models.py`: compatibility re-export for moved class objects;
  codegen-only models remain here.
- `src/sysml_codegen/extraction/hierarchy_resolver.py`: local hierarchy policy plus wrappers for
  shared primitive functions.
- `src/sysml_codegen/snapshot/loader.py`: unchanged import path and deserialization behavior.
- `tests/unit/test_hierarchy_resolver.py`: local wrapper, design override, aggregation, and
  orchestration tests.
- `tests/conformance/test_data_models.py`: object identity and compatibility field pins.

## What Stays in sysml-codegen

- Design override extraction and filtering: `extract_design_overrides`,
  `_keep_plain_usage_override`, and design-level `PartUsage` enumeration.
- Redefinition precedence in downstream supplied-value and pipeline paths.
- Usage-type indexing, part-usage indexing, and most-specific type selection:
  `_index_usage_level_retypes`, `usage_type_map`, `part_usage_names`, `most_specific`, and
  `owned_feature_typing_targets`.
- `HierarchyExtractionResult`.
- Hierarchy orchestration in `extract_hierarchy_data`.
- Aggregation expression rewriting, `AGG_PYTHON_OPS`, `_walk_aggregation_ast`,
  `_AggregationContext`, `build_aggregation_expression`, alias collection, and warnings.
- Scoping and aggregation expression localization in orchestration/pipeline builder code.
- Module construction, channel aliases, graph resolution, supplied-value materialization, and
  parameter-group derivation.

## Public API

Target public API:

```python
from agentic_mbse.sysml.hierarchy import (
    MultiplicityData,
    RedefinitionData,
    RedefinitionType,
    classify_redefinition,
    extract_multiplicities,
    extract_redefinitions,
)
```

Signatures:

```python
def classify_redefinition(member: Any, owning_qn: str) -> RedefinitionData | None: ...
def extract_redefinitions(part_element: Any) -> list[RedefinitionData]: ...
def extract_multiplicities(part_element: Any) -> list[MultiplicityData]: ...
```

`agentic_mbse.sysml.__init__` should also re-export these names. `classify_redefinition` is a
primitive API despite replacing a private sysml-codegen helper, because design overrides need the
same one-member classification without moving their scanner.

## Dataclass Move and Re-Export Strategy

Move the exact current definitions, not adapted versions.

- `RedefinitionType` remains a `str, Enum` with values `literal`, `chain`, and `expression`.
- `RedefinitionData` remains a standard-library dataclass. Its `target_path` default factory stays
  `list`; `source_file` default factory stays `lambda: Path("unknown")`; `expression_ast` remains
  `Any`.
- `MultiplicityData` remains a standard-library dataclass with no defaults for its five fields.

sysml-codegen import strategy:

- Remove local definitions for the three moved class objects from `data_models.py`.
- Import them from `agentic_mbse.sysml.hierarchy` or `agentic_mbse.sysml.data_models`.
- Keep them in `__all__` under the same names.
- Do not subclass or wrap them.
- Leave `HierarchyExtractionResult` and aggregation dataclasses local, with annotations pointing at
  the imported shared classes.

Tests must prove both field identity and object identity. Field identity should compare
`[(f.name, f.default, f.default_factory, f.type) for f in dataclasses.fields(cls)]` or an equivalent
stable subset that catches order and defaults.

## Compatibility Paths

`sysml_codegen.extraction.hierarchy_resolver` keeps these functions:

- `extract_redefinitions(part_element)`
- `extract_multiplicities(part_element)`

Each wrapper delegates to `agentic_mbse.sysml.hierarchy`. Compatibility tests should monkeypatch the
shared function and assert the wrapper calls it with the original object and returns the patched
sentinel. That is stronger than only checking behavior and does not require direct function identity.

`extract_design_overrides` remains local and calls `shared_hierarchy.classify_redefinition(...)`.
Tests should monkeypatch the classifier and prove the local plain-usage filter still drops
CHAIN/EXPRESSION results from plain usages while retaining literals. This proves shared delegation
without moving the policy.

## TYPE_MAP Inventory Strategy

The implementation must generate the inventory from the moved shared source, not from this design
or from sysml-codegen orchestration. The intended inventory is:

| Moved function | Adapter call strings |
| --- | --- |
| `classify_redefinition` | `ReferenceUsage`, `FeatureChainExpression`, `FeatureReferenceExpression` |
| `extract_redefinitions` | none beyond `classify_redefinition` |
| `extract_multiplicities` | `PartUsage` |

The test should inspect the moved module source or AST for literal arguments to
`SysideAdapter.is_instance(...)` and `SysideAdapter.elements_of_type(...)`, then assert that every
collected string is present in `SysideAdapter._get_type_map()` under a monkeypatched fake syside.
It must not include strings used only by `extract_hierarchy_data`, such as `PartDefinition`.

## Checking-Profile Disposition Matrix

Implementation close-out must update this matrix to `EXISTING`, `NEW RULE`, `FILED`, or `NO-OP`.
Rows marked `FILED` below include the backlog ID that should be added to the agentic-mbse backlog if
the implementation confirms the rule cannot land in this item.

| Idiom | Disposition | Exact rule | Fixture shape | Severity | Rationale | Backlog ID |
| --- | --- | --- | --- | --- | --- | --- |
| Redefinition precedence | FILED | Warn when one consumer scope has both a design-level override and a type-level literal redefinition for the same target, and the design override wins under codegen precedence. | Part def `Driver` has `:>> efficiency = 0.3`; design usage has `:>> driver.efficiency = 0.35`. | WARNING | Precedence depends on design override scope and supplied-value policy that remain in sysml-codegen. Filing avoids importing codegen. | `PUSH-DOWN-HIER-PROFILE-REDEF-PRECEDENCE` |
| Unsupported redefinition RHS | NEW RULE | Warn when a `ReferenceUsage` redefinition classifies as `EXPRESSION` but the expression reconstructs through unsupported/opaque shapes or unsupported operators already known to the codegen-compatible expression profile. | Bare `:>> cost = unsupported_fn(a.b)` plus clean literal, chain, and arithmetic-expression controls. | WARNING | Shared primitive classification exposes expression RHS early; Level 6 can flag risk without codegen imports. Some unsupported operator coverage may be shared with filed expression-profile rows. | n/a |
| Multiplicity shapes | NEW RULE | Warn when a child `PartUsage` multiplicity has no resolvable `cached_lower_bound` or has an upper-bound referent without an integer default. | Child `part cell[pack_count]` where `pack_count` has no literal integer default, plus a clean `[20]` or `[pack_count=20]` control. | WARNING | Shared multiplicity facts expose exactly the shape codegen uses for sum expansion entry points. This can be checked from moved primitives. | n/a |
| Missing instantiations | EXISTING | `L6_CALC_DEF_NO_INSTANTIATION`: a calc-bearing part def is never instantiated plainly or by retyping. | Existing Level 6 fixture with calc-bearing part definition and no usage. | ERROR | agentic-mbse already owns this check; Item 3 should document that it is existing, not powered by moved primitive facts. | n/a |
| Ambiguous inherited attributes | FILED | Warn when a usage has multiple incomparable owned typings that can supply different inherited attribute defaults for the same target. | Part usage with two unrelated typed targets, each redefining the same attribute literal; codegen resolves sorted-first with a warning. | WARNING | Detection requires most-specific type comparison and inherited attribute selection. Those are explicitly local to sysml-codegen for this item. | `PUSH-DOWN-HIER-PROFILE-AMBIG-INHERITED-ATTR` |

No row may close by importing sysml-codegen into agentic-mbse.

## Test Placement

agentic-mbse:

- Add `tests/test_sysml/test_hierarchy.py` for dataclass construction, enum values, literal/chain
  /expression redefinition classification, type-only skip, non-`ReferenceUsage` skip, deep-path
  target extraction, multiplicity count/default extraction, singleton exclusion, and float
  `cached_lower_bound` integer casting.
- Add API import tests for `agentic_mbse.sysml.hierarchy` and package-root exports.
- Add TYPE_MAP inventory tests from moved implementation source.
- Add or update Level 6 tests under `tests/test_validation/` only for the `NEW RULE` rows that
  actually land.

sysml-codegen:

- Keep design override tests in `tests/unit/test_hierarchy_resolver.py`.
- Keep aggregation, scoping, alias, orchestration, and pipeline tests in sysml-codegen.
- Add wrapper delegation tests for `extract_redefinitions` and `extract_multiplicities`.
- Add classifier-delegation tests for `extract_design_overrides`.
- Update `tests/conformance/test_data_models.py` to assert moved class object identity and exact
  dataclass fields through the existing sysml-codegen import path.
- Keep snapshot round-trip coverage against `src/sysml_codegen/snapshot/loader.py`.
- Add a no-churn gate: `git diff -- tests/fixtures` after targeted and full tests.

## Non-Goals

- No aggregation decomposition move. That is PUSH-DOWN Item 4.
- No design override scanner move.
- No usage-type map or most-specific type-selection move.
- No `HierarchyExtractionResult` move.
- No snapshot schema change or fixture recapture.
- No direct sysml-codegen dependency from agentic-mbse.
- No item-level PR closeout.

## Implementation Notes

Use shared imports in `agentic_mbse.sysml.hierarchy`, not sysml-codegen shims:
`agentic_mbse.sysml.expression`, `agentic_mbse.sysml.qualified_names`, and
`agentic_mbse.sysml.syside_adapter`.

Use `is_literal_node` for RHS classification. Do not use
`agentic_mbse.sysml.expression.is_literal_expression`; that name means "no feature refs" in
agentic-mbse.

`classify_redefinition` should preserve the current first-redefinition behavior. Changing that to
scan all owned redefinitions would be a behavior change and should be separate.

`source_file` and `source_line` remain available on `RedefinitionData`, but the moved primitive
extractor does not need to start populating them. Snapshot no-churn depends on preserving current
defaults.

## Potential Risks

- A wrapper accidentally keeps a copied implementation body. Mitigation: monkeypatch delegation
  tests for both public wrappers and the design override classifier path.
- A dataclass field default changes during the move. Mitigation: exact field-order/default tests in
  both repos.
- A validation rule overreaches and flags a codegen-supported shape. Mitigation: every new rule needs
  positive and negative fixtures, and file rows that need local indexing rather than guessing.
- TYPE_MAP testing accidentally checks local orchestration strings. Mitigation: generate the string
  set from the moved module source only.
- Fixture churn slips in through serialization. Mitigation: run snapshot and fixture diff gates and
  treat any diff as a defect.

## Integration Strategy

Land agentic-mbse first: shared models, `hierarchy.py`, tests, TYPE_MAP inventory, and any profile
rows. Then update sysml-codegen to import the shared classes and delegate primitive extraction
through the permanent compatibility functions. Run the targeted sysml-codegen hierarchy and snapshot
tests before full-suite gates so any incompatibility is localized.

The move composes with Items 1 and 2. It must import shared expression and qualified-name helpers
from agentic-mbse directly, not from sysml-codegen compatibility shims.

## Validation Approach

Targeted gates:

- agentic-mbse: `uv run pytest tests/test_sysml/test_hierarchy.py`
- agentic-mbse: targeted Level 6 tests for any new hierarchy-profile rules
- agentic-mbse: `uv run ruff check` on touched files
- sysml-codegen: `uv run pytest tests/unit/test_hierarchy_resolver.py tests/conformance/test_data_models.py`
- sysml-codegen: snapshot loader or snapshot round-trip tests touching hierarchy data
- sysml-codegen: `uv run ruff check` on touched files
- sysml-codegen: `git diff -- tests/fixtures`

Full gates:

- agentic-mbse full pytest suite
- sysml-codegen full pytest suite
- sysml-codegen `uv run ruff check src/`
- mypy in both repos if the current baseline allows it; otherwise record unchanged baseline counts.

Success requires no generated baseline or fixture churn.

## Next-Stage Handoff

Treat as fixed:

- The public shared API and permanent sysml-codegen compatibility paths.
- The three moved models are exact shared class objects.
- Design overrides, indexing, aggregation, orchestration, and `HierarchyExtractionResult` stay local.
- TYPE_MAP verification is generated from moved implementation strings.

Treat as risky:

- The distinction between literal-node classification and static-expression classification.
- The temptation to satisfy profile rows by moving usage-type indexing.
- Snapshot no-churn.

Treat as open for implementation judgment:

- Whether the `unsupported redefinition RHS` rule lands now or updates an existing expression-profile
  filed row with the hierarchy trigger. If it is filed instead, the implementation close-out must add
  a backlog row with exact rule, fixture shape, severity, and rationale.

## Next Steps

After approval, run `$my-plan` or `$my-implement` for the cross-repo move. Because this touches both
repos and has profile/backlog obligations, a persistent plan is preferable before implementation.

---
Next Step: After approval -> `$my-plan`
