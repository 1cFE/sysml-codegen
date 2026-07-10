# Spec: Hierarchy Primitives and Data Models

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-07-08 16:12 PDT
**Complexity:** MEDIUM
**Branch:** push-down-item1-expression

---

## Problem

PUSH-DOWN Items 1 and 2 are complete, audited, and committed in both repos:
agentic-mbse commit `243a15e` added shared qualified names, and sysml-codegen
commit `e01361b` split qualified-name utilities. The full PUSH-DOWN epic branch
continues on `push-down-item1-expression`; the user wants the whole epic
implemented before PR, so this item must not add item-level PR closeout.

The next blocker is hierarchy extraction. sysml-codegen still owns primitive
SysML facts that are reusable outside code generation: `:>>` redefinition
classification, multiplicity extraction, and the `RedefinitionType`,
`RedefinitionData`, and `MultiplicityData` models. Those facts are mixed with
codegen-owned policy in `hierarchy_resolver.py`: design override filtering,
usage-type and part-usage indexing, hierarchy orchestration, aggregation
rewriting, scoping, and module construction. That makes agentic-mbse validation
weaker than generation and risks duplicating hierarchy interpretation.

This item moves only the reusable primitive layer into agentic-mbse. The
codegen-specific hierarchy policy remains in sysml-codegen.

## Success Criteria

- [x] `agentic_mbse.sysml.hierarchy` exposes reusable redefinition and
  multiplicity extraction that sysml-codegen can import without copying logic.
- [x] `RedefinitionType`, `RedefinitionData`, and `MultiplicityData` live as
  field-identical standard-library dataclasses in agentic-mbse, following the
  existing shared `AttributeInfo` pattern.
- [x] sysml-codegen re-exports the identical class objects from its existing
  import paths; object identity tests prove callers are not using local copies.
- [x] sysml-codegen compatibility coverage proves `extract_redefinitions` and
  `extract_multiplicities` call the shared implementation, either through
  object identity or wrapper delegation tests.
- [x] `SysideAdapter.TYPE_MAP` coverage is verified from an implementation-site
  inventory of every `is_instance(...)` and `elements_of_type(...)` type string
  used by the moved hierarchy functions. The inventory must be generated from
  the actual moved surface, not from orchestration-only strings that stay local.
- [x] Existing sysml-codegen snapshots and generated baselines remain
  byte-identical; no fixture recapture is required for this move.
- [x] Design overrides, usage-type indexing, part-usage indexing, hierarchy
  orchestration, `HierarchyExtractionResult`, scoping, aggregation rewriting,
  and module construction remain in sysml-codegen.
- [x] Hierarchy-profile validation impact is implemented in agentic-mbse or
  filed there with exact rule, fixture shape, severity, and rationale for:
  redefinition precedence, unsupported redefinition RHS, multiplicity shapes,
  missing instantiations, and ambiguous inherited attributes.
- [x] Both repos pass the relevant targeted and full validation gates for this
  item, with no regression against the known project-wide ruff/mypy baselines.

## Known Requirements

- **[HARD]** This item starts only PUSH-DOWN Item 3 from
  `.project/backlog/epic_push_down.md`; Item 4 aggregation decomposition and
  later epic work are out of scope.
- **[HARD]** Run `$my-spec-review` after this spec and before `$my-design`.
- **[HARD]** The moved data models must remain standard-library dataclasses,
  not Pydantic models, and must preserve the exact sysml-codegen field names,
  field order, defaults, and value types.
- **[HARD]** sysml-codegen must re-export the exact shared class objects for
  `RedefinitionType`, `RedefinitionData`, and `MultiplicityData` from
  `sysml_codegen.extraction.data_models`.
- **[HARD]** sysml-codegen compatibility imports must remain stable for
  existing callers in extraction, resolution, orchestration, snapshot loading,
  and tests.
- **[HARD]** agentic-mbse must not import sysml-codegen. Shared hierarchy code
  must depend only on agentic-mbse surfaces and standard-library code.
- **[HARD]** TYPE_MAP checks must cover every type string used by the moved
  code because `SysideAdapter.is_instance` now raises on unknown names.
- **[HARD]** A shared helper may classify one `ReferenceUsage` into a primitive
  redefinition fact, but it must not move the design-level `PartUsage` scanner,
  plain-usage filtering, design-override filtering, or override precedence
  policy.
- **[HARD]** Moving `RedefinitionData` as a neutral fact carrier does not move
  every scanner that currently populates it. `target_path` and `is_deep_path`
  may remain fields on the shared dataclass, but design-override extraction and
  interpretation stay in sysml-codegen.
- **[NEED]** The moved extraction behavior must preserve current semantics for
  literal, chain, and expression redefinitions, including deep target paths and
  expression text reconstruction.
- **[NEED]** Multiplicity extraction must preserve current behavior for child
  `PartUsage` multiplicities, including `cached_lower_bound`, referenced count
  attribute names, default values, and singleton exclusion.
- **[NEED]** The checking-profile loop must close inside agentic-mbse as a
  validation rule or a filed backlog item. A sysml-codegen import is not an
  acceptable closure.
- **[NEED]** Checking-profile close-out must use a per-idiom disposition matrix:
  `EXISTING`, `NEW RULE`, `FILED`, or `NO-OP`. Each `NEW RULE` or `FILED` row
  must name the exact rule, fixture shape, severity, rationale, and backlog ID
  when filed.
- **[NEED]** Profile idioms that require usage-type indexing or most-specific
  type selection, such as missing instantiations and ambiguous inherited
  attributes, must be closed without moving those indexing surfaces. If that is
  not possible from moved primitive facts alone, they must be filed as follow-up
  backlog rows with exact rule, fixture shape, severity, and rationale.
- **[INFERRED]** Existing hierarchy tests should be split so pure primitive
  model/extraction behavior moves to agentic-mbse, while design override,
  aggregation, orchestration, and pipeline behavior stays tested in
  sysml-codegen.
- **[INFERRED]** The sysml-codegen wrapper should stay permanent, matching the
  Item 1 expression shim and Item 2 qualified-name compatibility pattern.

## Non-Goals

- Move design override extraction or its filtering policy.
- Move usage-type indexing, part-usage indexing, or most-specific type
  selection.
- Move hierarchy orchestration or `HierarchyExtractionResult`.
- Move aggregation decomposition, aggregation expression rewriting,
  `AggregationExpressionData`, `SumTerm`, `SingletonTerm`, `LocalTerm`, or
  `ScopedAggregationData`.
- Move codegen scoping, channel aliasing, graph resolution, supplied-value
  materialization, module construction, or pipeline generation.
- Change snapshot schema, recapture fixtures, or revise generated baseline
  outputs.
- Add item-level PR closeout. The whole PUSH-DOWN epic closes together.

## Open Questions / Deferred to design

- Decide the exact shared module API: whether `agentic_mbse.sysml.hierarchy`
  exports only the public dataclasses and `extract_redefinitions` /
  `extract_multiplicities`, or also a private helper that classifies a single
  `ReferenceUsage` into a primitive redefinition fact. Any such helper must not
  move the design-level `PartUsage` scanner, plain-usage filter, or design
  override policy currently sharing related code paths.
- Decide whether sysml-codegen keeps `extract_redefinitions` and
  `extract_multiplicities` as wrapper functions in `hierarchy_resolver.py`, or
  imports and re-exports the shared functions directly.
- Decide how much existing `tests/unit/test_hierarchy_resolver.py` coverage
  moves to agentic-mbse versus stays in sysml-codegen as compatibility and
  integration coverage.
- Decide whether each hierarchy-profile idiom can be implemented from moved
  primitive facts now or must be filed. Missing-instantiation and ambiguous
  inherited-attribute rules likely depend on usage-type indexing facts that
  remain in sysml-codegen, so design should not assume they can land in this
  item.

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_push_down.md`
- **Required Reading:** `.project/backlog/epic_push_down.md`; `.project/CURRENT_WORK.md`; `CLAUDE.md`; `.project/active/expression-reconstruction-push-down/audit.md`; `.project/active/qualified-name-utility-split/audit.md`
- **Current source:** `src/sysml_codegen/extraction/hierarchy_resolver.py`; `src/sysml_codegen/extraction/data_models.py`; `src/sysml_codegen/snapshot/loader.py`; `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/data_models.py`; `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/syside_adapter.py`
- **Required Tests:** `tests/unit/test_hierarchy_resolver.py`; `tests/conformance/test_data_models.py`; snapshot round-trip tests that exercise `src/sysml_codegen/snapshot/loader.py`
- **Profile Required Reading:** `/home/reid/1cfe/agentic-mbse/.project/backlog/BACKLOG.md`; `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/validation/level6_architecture.py`; `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/types.py`
- **Review:** `.project/active/hierarchy-primitives-models/spec-review.md` (to be created next)
- **Design:** `.project/active/hierarchy-primitives-models/design.md` (after spec review)

---

**Next Steps:** Run `$my-spec-review` before proceeding to `$my-design`.
