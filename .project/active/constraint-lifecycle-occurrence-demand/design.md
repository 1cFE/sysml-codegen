# Design: Lifecycle Remediation Item 1 — Occurrence and Demand Integrity

**Status:** Revised — ready for independent re-review
**Owner:** Reid W
**Created:** 2026-07-19 15:49 PDT
**Revised:** 2026-07-19 16:19 PDT
**Branch:** `constraint-exec-epic`
**Commit:** `8d4f298`
**Epic:** CONSTRAINT-LIFECYCLE-REMEDIATION — Item 1, register row 1
**Complexity:** HIGH

---

## Overview

Item 1 makes constraint disposition, finite owner expansion, and supplied-value demand one
identity-bearing flow. A verified, immutable prepared batch is built atomically for each live
construction or replay rebuild. Authoritative lowering and demand discovery consume that batch.
Supplied values then merge by the existing normalized target while retaining every origin needed
to prove that distinct lookup contexts resolve to the same semantic outcome.

The design deletes the nullable association, partial-cycle, duplicate expansion, route-counted
demand, and last-write-wins paths. It does not add a general resolver, change serialized shapes, or
take lifecycle Item 4's warning-location work.

## Related Artifacts

- **Approved contract:** `spec.md`
- **Approval:** `spec-rereview.md`
- **Historical spec review:** `spec-review.md`
- **Historical design review:** `design-review.md` — verdict **Revise**, preserved unchanged
- **Epic:** `.project/backlog/epic_constraint_execution_lifecycle_remediation.md` — Items 1 and 4
- **Ratified architecture:**
  `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md`
- **Lifecycle requirements:** `.project/active/constraint-execution-lifecycle-contract/spec.md`
- **Item 0 coordinate:** `.project/active/constraint-lifecycle-candidate-pin/evidence.md`
- **Completed occurrence work:**
  `.project/completed/20260713_part-instance-index/{spec,design,audit}.md`
- **Completed lowering work:**
  `.project/completed/20260713_constraint-lowering/{spec,design,audit}.md`
- **Primary defect evidence:**
  `.project/research/20260718-192048_constraint-exec-pr-wave-code-review.md` — R-4/R-5/R-7
- **Load-bearing references:** `docs/architecture/reference/27-snapshot-generation.md` and
  `docs/architecture/reference/28-constraint-lowering-and-catalog.md`

## Review Resolution

| Finding | Revision |
|---|---|
| C1 | A logical demand retains ordered origins and compares resolved outcomes. Different raw scopes are valid. |
| C2 | Value resolution returns the winning model record/source. Constraint-only group provenance is selected afterward. |
| C3 | Preparation stages owner results in a private local dictionary. No recording journal exists outside a successful batch. |
| C4 | The register boundary is corrected: total warning-location projection is Item 4/register row 4. Item 1 preserves current preflight behavior and records the masking risk. |
| C5 | Exact prepared-batch, enrichment, resolution, and lowering fields/signatures/call order are pinned below. |
| M1 | Serializer performs a second pure association solely for excluded-location canonicalization. Construction/rebuild still evaluates once. |
| M2 | The planned implementation union is nine Python paths plus two separately counted architecture docs, with automatic addition of every actual change. |
| M3 | A per-file executable-LOC budget targets 3,504 or fewer lines from a 3,524 baseline. Named deletions fund the types. |
| M4 | Appendix B pins exact nodes, fixtures, observations, unchanged controls, hashes, and RED/GREEN commands. |
| M5 | Every `[INFERRED]` bet remains agent-grade and evidence-challengeable. Planning language no longer hardens it. |
| A1–A4 | Copy-on-write is limited to attribute maps; snapshot-context defaults are deferred; mutation tests clone values; the cycle stack is structural and per path. |

## Research Findings

- The executable profile creates decisions from usages in source order and copies identity and
  location into each decision
  (`../agentic-mbse/src/agentic_mbse/sysml/executable_profile.py:809-899,996-1008`). Count plus
  exact identity/location equality is therefore a valid same-batch association check.
- Current demand discovery converts admission to nullable-QN membership and suppresses expansion
  failures (`src/sysml_codegen/analysis/constraint_lowering.py:430-473`). Lowering independently
  evaluates the profile and expands again (`constraint_lowering.py:869-1189`).
- Owner filtering exists, but the expander's final branch implicitly means `package`
  (`constraint_lowering.py:386-427`). Unsupported owners can reach it through the demand probe.
- Recursive revisits return an empty path list (`src/sysml_codegen/analysis/part_instance_index.py:139-161`).
  The finite cardinality, deduplication, and ordering machinery around it is already audited and
  remains authoritative (`part_instance_index.py:72-136,167-237,296-315`).
- `RecordingOccurrenceIndex` writes after each successful owner query
  (`part_instance_index.py:379-395`). That is owner-atomic, not batch-atomic.
- `_binding_target` already defines Item 1 demand identity
  (`src/sysml_codegen/resolution/supplied_values.py:37-99`). Existing absolute references can reach
  the same target from distinct sibling/retype/IFE/fusion scopes, so raw scope equality is not a
  semantic conflict.
- The current materializer counts appended routes and overwrites `synth[target.qn]`
  (`supplied_values.py:206-332`). Its value ladder returns only value/nonliteral state, although the
  matching override/redefinition is the evidence needed for group provenance.
- Live and replay duplicate demand, materialization, and bucketing
  (`src/sysml_codegen/orchestration/pipeline_builder.py:828-860`;
  `src/sysml_codegen/snapshot/graph_rebuild.py:82-134`). Replay also mutates its loaded attribute
  map. Earlier self-binding rescue can still mutate `CalcUsageData.bindings`
  (`pipeline_builder.py:572-625`; `graph_rebuild.py:77-80`).
- Serializer independently evaluates the profile to canonicalize excluded locations
  (`src/sysml_codegen/snapshot/serializer.py:139-160`). Keeping that evaluation pure avoids adding
  ephemeral batch state to capture or `PipelineContext`.

## Core Concept

This is a prepare-then-materialize pipeline with local commit. Preparation evaluates and verifies
one usage/decision association, completes warning/BLOCK preflight, filters owner kinds, expands all
supported admitted owners, and stages the exact owner-query transcript. It publishes nothing until
the whole batch succeeds. Both demand discovery and lowering then consume the returned batch.

Materialization is one operation per normalized target, not one operation per route. Every route
becomes a `DemandOrigin`. One `LogicalDemand` retains all origins. Its resolver may evaluate several
distinct lookup contexts internally, but it accepts them only when their value/nonliteral outcomes
are semantically identical. It then chooses grouping provenance from the resolved evidence. This
keeps `_binding_target` and the existing materializer-local value ladder as the identity and value
seams. No Item 2 producer resolver is introduced.

## Key Bets

All bets below are **[INFERRED], agent-grade, and challengeable**. Design acceptance does not make
them owner-settled.

- **B1. Verified ordered pairing is sufficient within one facts batch.** Identity and location
  copies can expose deletion, duplication, and reorder without a durable key. *If false → Item 1
  cannot distinguish anonymous siblings and needs an upstream identity contract.*
- **B2. Exact `_BindingTarget.qn` equality is the complete Item 1 target identity.** Origin lookup
  contexts may differ, but their resolved outcomes can be compared. *If false → the existing
  normalizer merges distinct targets or misses a required equivalence, which belongs in a broader
  resolver contract.*
- **B3. Calc-route source is the correct grouping authority when calc and constraint routes share a
  target.** *If false → adding an assertion may legitimately regroup an existing calc input.*
- **B4. A numeric constraint-only result has deterministic provenance through the captured target,
  a real winning record source, or one portable usage source.** *If false → it cannot enter an
  existing parameter group without inventing a sentinel.*
- **B5. A live occurrence query has no external mutation before its result is returned.** This lets
  preparation stage the result privately. *If false → deleting the recording wrapper is
  insufficient to guarantee batch atomicity.*

## Key Decisions

- **D1. Centralize pure association and the profile-version guard.**
  `associate_usage_decisions(facts)` checks `PROFILE_SEMANTIC_VERSION`, evaluates the profile, checks
  cardinality, then checks identity and location for every ordered pair before returning immutable
  pairs. It emits no warning and performs no owner query. *Rejected: cardinality-only association*
  (it misses anonymous reorder/duplication). *Rejected: a new durable identity* (Item 12 scope).
- **D2. Return one exact prepared batch after private transcript staging.** Preparation computes
  every exclusion projection before expansion, caches successful part-owner queries in a local
  dictionary, and constructs the transcript only after all items succeed. The current
  `RecordingOccurrenceIndex` is deleted because it exposes a partial journal by construction.
  *Rejected: export suppression alone* (a retained recorder is still externally inspectable).
- **D3. Filter before expansion and make `package` explicit.** Only admitted `part_def`, `calc_def`,
  and `package` entries expand. Excluded and unsupported entries remain visible with empty owner
  instances and make zero occurrence queries. *Rejected: a final default package arm* (future owner
  kinds would silently become executable).
- **D4. Give cycles one public pipeline surface.** The walker raises structured
  `RecursiveContainmentError`; preparation raises `CodeGenerationError` from it with usage and
  requested-owner context. The active stack is structural and copied per recursion path. *Rejected:
  empty-subtree return* (partial truth). *Rejected: a global visited set* (breaks DAG/diamond paths).
- **D5. Represent target identity separately from origin lookup.** `_binding_target` runs before
  merge. `LogicalDemand` is target plus canonical ordered origins. Raw `instance_scope` or owning
  PartDef inequality never fails by itself. *Rejected: one chosen scope on the merged demand*
  (existing absolute-reference controls disprove it).
- **D6. Resolve one logical demand through all distinct contexts.**
  `resolve_logical_demand` calls the materializer-local precedence ladder once for each distinct
  origin lookup context, then requires identical `(value, nonliteral)` outcomes. It returns the
  winning record/source for each context. *Rejected: first/last context wins* (order becomes
  precedence). *Rejected: use the general graph resolver* (Item 2 scope).
- **D7. Select group provenance after value resolution.** Calc source wins when present. Otherwise,
  use an exact captured target source, then one real winning record source, then one portable
  constraint-usage source. At the selected tier, multiple distinct sources conflict; missing
  provenance for a numeric result fails. `Path("unknown")` is unavailable, not a group. *Rejected:
  validate provenance during merge* (the winning model record is not known yet).
- **D8. Count and emit by target order.** Logical demands sort by ascending normalized QN. Each
  target increments scan/apply/nonliteral counts once, emits at most one collision/nonliteral
  warning, and synthesizes at most one attribute. *Rejected: route-order processing* (duplicate and
  reversal-sensitive observations).
- **D9. Share copy-on-write attribute enrichment across live and replay.** The shared function
  accepts `Path | str` keys, returns a new `Path`-keyed map, and never mutates the input mapping or
  its lists. This claim does not cover the pre-existing calc self-binding rescue. *Rejected:
  route-specific materialization/bucketing* (current duplication).
- **D10. Let serializer re-associate purely.** Serialization may call
  `associate_usage_decisions` a second time solely to select and canonicalize excluded usage
  locations. It does no warning emission, BLOCK handling, expansion, or demand work. *Rejected:
  threading the ephemeral batch through context/capture* (more API and production paths for no
  serialized benefit).
- **D11. Do not absorb R-8.** Item 1 preserves the existing NON_NUMERICAL-warning-before-BLOCK
  preflight order. Association mismatch is earlier; every owner query is later. Total handling of
  unmappable warning locations remains lifecycle Item 4/register row 4. *Rejected: adding a total
  projection policy here* (wrong register owner).
- **D12. Do not bump snapshot, profile, package, catalog, or schema versions.** All new records are
  ephemeral. Serializer bytes stay unchanged for valid associated inputs. *Rejected: precautionary
  version churn* (no persisted shape or interpretation changes).

## Data Contracts

### Prepared batch

`PreparedConstraintUsage` has exactly these fields:

| Field | Type | Meaning |
|---|---|---|
| `source_index` | `int` | Original facts/profile position. |
| `usage` | `ConstraintUsageFact` | Exact source usage. |
| `decision` | `UsageDecision` | Verified decision for that usage. |
| `owner_kind` | `str` | Classified owner kind used by explicit dispatch. |
| `owner_instances` | `tuple[tuple[str, str], ...]` | `(owner_instance_path, occurrence_scope)`; empty for excluded/unsupported. |
| `projected_exclusion` | `Optional[_ProjectedExcludedLocation]` | Complete exclusion location for non-executable items; `None` for admitted items. |

`PreparedConstraintBatch` has exactly two fields:

| Field | Type | Meaning |
|---|---|---|
| `items` | `tuple[PreparedConstraintUsage, ...]` | One item per source usage, in verified source order. |
| `occurrence_transcript` | `tuple[tuple[str, tuple[InstanceOccurrence, ...]], ...]` | Successful part-owner queries sorted by owner QN; immutable and complete. |

The batch does not enter snapshots, catalogs, facts, or `PipelineContext`. The live caller converts
its transcript to the existing `dict[str, list[InstanceOccurrence]]` only when constructing a
successful context.

### Logical demand and resolution

The four immutable materializer-local records live in `resolution/supplied_values.py`:

| Type | Exact fields |
|---|---|
| `DemandOrigin` | `route: Literal["calc", "constraint"]`; `target: _BindingTarget`; `lookup_context: tuple[str, Optional[str]]` as `(instance_scope, owning_part_def_qn)`; `group_provenance: Optional[Path]`; `diagnostic_context: str`. |
| `LogicalDemand` | `target: _BindingTarget`; `origins: tuple[DemandOrigin, ...]`. |
| `ValueResolution` | `lookup_context: tuple[str, Optional[str]]`; `value: Optional[float]`; `nonliteral: bool`; `winning_record: Optional[RedefinitionData]`; `winning_source: Optional[Path]`. |
| `ResolvedDemand` | `demand: LogicalDemand`; `outcomes: tuple[ValueResolution, ...]`; `value: Optional[float]`; `nonliteral: bool`; `group_source: Optional[Path]`. |

Origins sort by calc-before-constraint route rank, diagnostic context, lookup context, and group
path. The sort affects reproducibility, not semantic precedence. Identical lookup contexts are
evaluated once. Semantic equality means identical numeric values or the same unresolved/nonliteral
disposition. Winning record identity/source is retained as provenance evidence but is not part of
value equality.

The existing materializer tier ladder remains local. `_match_override` and `_resolve_value` return
the matched `RedefinitionData` with the value. Tier 2a performs the already-gated exact type-QN
record match locally instead of calling the float-only general helper. No graph-builder matching
semantics or producer resolver changes.

### Exact APIs

| API | Required signature/ownership |
|---|---|
| `associate_usage_decisions` | `(facts: ConstraintFacts) -> tuple[tuple[ConstraintUsageFact, UsageDecision], ...]`; owns profile guard/evaluation and complete association validation only. |
| `prepare_constraint_usages` | `(facts, *, occ_index: OccurrenceIndex, calc_usages: Sequence[CalcUsageData], source_location_mode: Literal["live", "snapshot"], source_roots: Sequence[Path]) -> PreparedConstraintBatch`; owns existing warning/BLOCK preflight, exclusion projection, owner filtering/expansion, and staged transcript. |
| `resolve_logical_demand` | `(demand, *, redefinitions, design_overrides, usage_type_map, exact_real_sources) -> ResolvedDemand`; owns context comparison and post-resolution provenance. |
| `enrich_graph_design_attributes` | `(real_design_attrs: Mapping[Union[Path, str], Sequence[DesignAttributeData]], *, calc_usages, prepared, redefinitions, design_overrides, usage_type_map) -> dict[Path, list[DesignAttributeData]]`; owns normalization, ordered resolution, warnings, synthesis, and copy-on-write bucketing. |
| `lower_constraints` | `(facts, *, prepared: PreparedConstraintBatch, registry: OutputRegistry, design_attrs: Mapping[Path, Sequence[DesignAttributeData]]) -> list[ConcreteConstraint]`; owns strict actual resolution and concrete lowering only. |

`lower_constraints` cannot accept an occurrence index, calc usages for owner expansion, source
location policy, or profile result. It cannot evaluate the profile or query occurrences. Tests may
refine names but not these ownership and no-requery constraints.

## Architecture

### Association and preparation

1. `associate_usage_decisions` checks the profile semantic version, evaluates the profile, and
   verifies the complete count/identity/location association. A mismatch raises `CodeGenerationError`
   with source index and both observed identity/location values.
2. Preparation runs existing NON_NUMERICAL warning projection and then existing BLOCK aggregation.
   No owner query occurs during either step.
3. Preparation projects every exclusion and classifies every verified pair. Unsupported or
   excluded items get empty instances. Admitted part/calc/package entries use explicit branches.
4. Part-owner results are queried into a private dictionary and reused by repeated owner QN.
   Calc-owner matches and the package singleton are local immutable tuples.
5. Only after every item succeeds does preparation freeze the ordered items and sorted transcript.
   Any later-owner failure discards all staged owner results.

The current warning-location projection can raise while rendering a NON_NUMERICAL warning and
therefore mask a later BLOCK. That known predecessor is R-8. Item 4/register row 4 owns its total
behavior. Item 1 adds no unmappable-warning test and makes no claim that the masking path is closed.
If preparation mechanically moves this code, warning bytes, order, and failure behavior remain
unchanged.

### Cycle surface

The walker uses an active structural stack per recursion path. Its key is the active definition
plus the incoming `(owning_definition_qn, feature_name, target_definition_qn)` edge. Sibling
recursion gets a copied stack. Re-entering a definition raises:

| Field | Type |
|---|---|
| `requested_owner_qn` | `str` |
| `edge_owner_qn` | `str` |
| `edge_feature_name` | `str` |
| `edge_type_qn` | `str` |
| `cycle_path` | `tuple[str, ...]` including repeated closing definition |

Canonical edge traversal selects a stable failure under feature reversal. It does not replace the
existing `_occurrence_sort_key`, change final finite order, or act as a global visited set.
Preparation catches `RecursiveContainmentError` and raises contextual `CodeGenerationError` using
`raise ... from error`. Public tests assert the outer usage/location/requested-owner context and all
five fields on `__cause__`.

### Logical resolution and provenance

1. Calc bindings and admitted prepared constraint actuals become `DemandOrigin` records. Unsupported
   source forms remain outside the materializer as they do today.
2. `_binding_target(source_path, instance_scope)` normalizes every origin. Origins whose exact target
   QN matches merge before any value lookup.
3. The complete target set sorts ascending. Each demand's origins receive their canonical order.
4. `resolve_logical_demand` evaluates each distinct lookup context. Raw context inequality is valid.
   Different numeric values, or a literal/nonliteral/unresolved disagreement, raise a conflict
   naming the target and ordered diagnostic contexts.
5. For a numeric result, group provenance is selected after resolution:
   - one unique calc-origin source, if any calc origin exists;
   - otherwise one exact captured design-attribute source for the target;
   - otherwise one unique real source from the winning override/redefinition records;
   - otherwise one unique portable constraint-usage source.
6. Multiple candidates at the selected tier conflict. `None`, `Path("unknown")`, the working
   directory, and synthetic sentinels do not qualify. A numeric result with no source fails.
7. All resolutions, synthetic attributes, and log events are staged locally. After the complete
   ordered set succeeds, collision/nonliteral warnings are emitted once per target and the new
   `Path`-keyed attribute map is returned.

Counts are logical-operation counts: `scanned` is the number of logical demands; `applied` is the
number with a numeric outcome, including a real-attribute collision; `non_literal_skips` is the
number with the nonliteral outcome. Internal per-context evaluations never increment them.

### Live construction and capture call order

1. Extract facts, calc/hierarchy/design data, build the output registry, and run existing calc
   binding rescue.
2. Build one live `PartInstanceIndex`.
3. Call `prepare_constraint_usages` once when lowering is enabled and usages exist.
4. Call `enrich_graph_design_attributes` with the prepared batch. No strict constraint actual is
   resolved before this returns.
5. Build `ParameterGroupDeriver` from the returned graph-only attribute map.
6. Call `lower_constraints(..., prepared=batch, ...)`.
7. Backtrack with retained constraint roots, build/extend the graph, and assemble the catalog.
8. Construct `PipelineContext`; only here convert and publish `batch.occurrence_transcript`.
9. Capture calls the existing serializer. Serializer may independently re-associate facts as
   described below; the prepared batch is not threaded into context or capture.

“Evaluate once” applies to live context construction. A capture request performs that construction
once and may perform one additional pure serializer association.

### Same-checkout replay call order

1. Load and validate the v3 snapshot, build the registry, and run existing calc binding rescue.
2. Build one `FrozenOccurrenceIndex`.
3. Call `prepare_constraint_usages` once with snapshot location policy.
4. Call the same copy-on-write enrichment function and build grouping from its `Path`-keyed return.
5. Carry the prepared batch in the existing classifier-input dictionary.
6. Build the base graph and call `lower_constraints(..., prepared=batch, ...)` without another
   frozen index, profile evaluation, or occurrence query.
7. Extend and catalog the graph.

“Evaluate once” applies to each replay rebuild. Replay remains same-checkout regression evidence,
not relocated/full-tree certification.

### Direct serializer safety

`_constraint_facts_for_snapshot` calls `associate_usage_decisions(facts)` and uses the returned
pairs only to identify excluded/unsupported usages whose copied locations need canonicalization.
The centralized profile guard protects direct serializer calls. The serializer:

- emits no profile warning;
- does not aggregate or raise BLOCK diagnostics;
- performs no owner expansion or supplied-value demand;
- mutates only its deep copy; and
- produces the same bytes for every currently valid associated input.

This honest second pure evaluation is simpler than making ephemeral construction state part of
`PipelineContext` or `capture_snapshot`.

## Required Invariants

- **I1 — association first:** complete count/identity/location verification precedes warning
  projection, filtering, expansion, and demand.
- **I2 — preflight before queries:** existing warning/BLOCK preflight completes or fails before any
  owner query. Item 1 does not claim total warning-location behavior.
- **I3 — owner totality:** each verified pair becomes supported-admitted expansion, visible
  exclusion, or a batch-halting error. Unsupported/excluded means zero queries and zero demand.
- **I4 — batch atomicity:** no transcript or prepared item is externally observable unless all
  supported admitted owners finish.
- **I5 — finite stability:** cardinality dispatch, zero/equal bounds, Cartesian expansion,
  subtype/retype/diamond dedup, same-name separation, most-specific identity, and integer sibling
  order retain audited observations.
- **I6 — one logical demand:** exact normalized target QN is the equality key. Context differences
  are resolved semantically, not rejected structurally.
- **I7 — one logical operation:** each target contributes at most one scan, apply/nonliteral result,
  warning, synthesized attribute, and grouping decision.
- **I8 — post-resolution provenance:** calc precedence and the constraint-only source ladder are
  deterministic; conflict or absence fails without a sentinel.
- **I9 — attribute-map nonmutation:** enrichment copies keys and lists and returns `Path` keys. The
  preceding calc-binding rescue mutation remains existing behavior.
- **I10 — lowering cannot rediscover:** lowering receives only the prepared batch for disposition
  and instances. It cannot evaluate the profile or query an index.
- **I11 — no Item 2 absorption:** `_binding_target` and the materializer-local value ladder remain
  the only changed demand seams. Producer/exact-QN resolution is unchanged.
- **I12 — no certification overclaim:** public live cases may close row 1. Same-checkout replay is
  non-certifying; Items 5 and 13 retain relocated/full-tree/composed proof.

## Error and Mutation Boundaries

| Boundary | Error surface | State after failure |
|---|---|---|
| Pure association | `RuntimeError` for profile-version skew; `CodeGenerationError` for count/identity/location mismatch | No warning, owner query, demand, or serializer mutation. |
| Warning/BLOCK preflight | Existing warning projection or complete BLOCK `CodeGenerationError` | Zero owner queries. Unmappable-warning masking remains open R-8 under Item 4. |
| Exclusion projection/owner classification | Contextual `CodeGenerationError` | Private staging discarded; no transcript or demand. |
| Live walker | `RecursiveContainmentError` with structural fields | No owner result; finite prefix remains local to the failed call. |
| Preparation cycle wrapper | `CodeGenerationError` from walker error | No returned batch, transcript, materializer call, context, snapshot, graph, catalog, or target mutation. |
| Frozen required owner | Contextual `CodeGenerationError` from `FrozenOccurrenceIndexCorruptionError` | Frozen index unchanged; private staging discarded; excluded/unsupported owners never query. |
| Demand normalization | Contextual unsupported-source handling as today | No value lookup or attribute mutation. |
| Logical resolution | Target/origin conflict or provenance `CodeGenerationError` | No returned enrichment map or grouping; staged attributes/log events discarded. |
| Parameter grouping | Existing error if an invalid QN/source escapes Item 1 | Indicates an Item 1 bug; no `parameter_groups.py` behavior change. |
| Strict lowering | Existing contextual resolution error | Concrete list remains local; no second query/profile evaluation. |
| Graph extension/catalog | Existing validation error | Input graph unchanged; catalog not assigned. |
| Serializer association | Pure association error | No serialized bytes; input facts unchanged. |
| CLI/capture | Context construction error | Existing output target remains byte-identical; no snapshot is written. |

## Component Responsibilities

- **`analysis/constraint_lowering.py`** owns association, profile guard, preparation, explicit owner
  dispatch, prepared data types, and lowering from prepared items.
- **`analysis/part_instance_index.py`** owns the structural active stack and
  `RecursiveContainmentError`; it deletes `RecordingOccurrenceIndex` and retains finite logic.
- **`resolution/supplied_values.py`** owns origin/demand/resolution records, semantic context
  comparison, provenance selection, unique counts, and copy-on-write enrichment.
- **`orchestration/pipeline_builder.py`** owns the live call order and publishes a successful batch
  transcript into the existing context field.
- **`snapshot/graph_rebuild.py`** owns the replay call order, one frozen index, and ephemeral batch
  carriage in classifier inputs.
- **`snapshot/serializer.py`** performs the bounded second pure association for exclusion
  canonicalization.
- **`orchestration/pipeline_context.py`**, **`snapshot/__init__.py`**, and
  **`snapshot/loader.py`** receive comment-only truth corrections if the implementation lands as
  designed.
- **`analysis/parameter_groups.py`** remains unchanged and consumes one settled synthetic source.
- **Architecture docs 27 and 28** replace recorder/query and `collect_bare_actual_demand` language.

## Compatibility and Migration

- `RecordingOccurrenceIndex`, `collect_bare_actual_demand`, and the route-level materializer tuple
  are private implementation surfaces. Delete them and migrate repository tests/callers directly;
  compatibility wrappers would preserve the obsolete paths.
- Multi-scope absolute-reference behavior is preserved by semantic outcome comparison. The existing
  sibling, retype, IFE, and fusion controls run unchanged.
- Recursive models that formerly returned a finite prefix now fail. Finite output order and
  cardinality remain compatible.
- `part_occurrences` retains the v3 dictionary/list bytes and meaning: the complete transcript of
  supported admitted part-owner expansion. Only its in-memory construction changes.
- Snapshot format stays v3; executable profile stays v4; package stays 0.1.0; facts, expression IR,
  graph, catalog, and parameter-group schemas do not change. No migration or recapture is required
  for valid same-checkout inputs.
- `build_pipeline_context_from_snapshot` still leaves facts, concrete constraints, transcript, and
  lowering-mode context fields at defaults (`orchestration/snapshot_context.py:61-76`). No prepared
  batch enters `PipelineContext`, so Item 1 does not need to touch this file. Treat the asymmetry as
  a bounded follow-up before a consumer relies on those context metadata fields.
- Warning-location totality is an open predecessor risk owned by Item 4. Existing warning code may
  move mechanically only with byte/order/failure behavior preserved.

## Non-Goals

- Item 2 calculation/aggregation/constraint producer or exact-QN resolver unification.
- Item 4 R-8 unmappable-warning projection remediation or new R-8 acceptance tests.
- Item 5 relocated whole-tree proof or Item 13 composed sealed-artifact proof.
- New target equivalence beyond `_binding_target`.
- Cross-version anonymous identity, `tracking_key`, profile outcome, catalog schema, or snapshot
  schema changes.
- Making recursive, parameterized, ranged, ordered, nonunique, unknown, or unbounded occurrence
  shapes executable.
- Changing calc self-binding rescue, `ParameterGroupDeriver`, or the strict actual-resolution
  precedence ladder.

## Potential Risks

- **Distinct contexts agree accidentally.** Existing absolute-reference controls plus an explicit
  unequal-value/nonliteral conflict test guard the semantic comparison.
- **Winning record source is often `Path("unknown")`.** It remains in diagnostic evidence but is
  excluded from provenance candidates. The portable usage fallback keeps live constraint-only
  demand functional.
- **A later owner leaks an earlier transcript.** There is no externally held journal. A fake A-then-B
  failure test asserts that preparation returns nothing and no later seam runs.
- **Cycle canonicalization changes finite order.** Error traversal is separate from final
  `_occurrence_sort_key`; unchanged finite controls run in normal and optimized modes.
- **The new types grow production code.** Appendix A budgets additions against specific helper and
  branch deletions. Any changed path auto-joins the ledger.
- **Serializer behavior drifts from construction.** Both use the pure association helper and its
  version guard; serializer tests prove no warning/query and unchanged valid bytes.

## Integration Strategy

Implement the structured cycle error and pure association first. Replace the recording wrapper with
batch-local staging and make lowering accept only the batch. Then add origin-aware resolution and
the shared enrichment return, switch live/replay callers, and delete the old paths in the same
phase. Finish with serializer reuse, truth-bearing comments/docs, and acceptance/accounting gates.
No dual path or feature flag remains.

## Validation Approach

Normal mode is primary evidence. The identical focused selection also runs with `python -O`.
Unchanged absolute-reference controls protect C1. Public licensed live fixtures prove row 1; any
license skip is unproven. Same-checkout replay is labeled non-certifying. TEAx execution is selected
with the execution marker override. Exact test bytes and fixture-overlay bytes are hashed before
RED and rechecked before GREEN.

Closeout also runs formatting, Ruff, mypy against its recorded baseline, fixture manifest checks,
the compatible full suite, `git diff --check`, the automatic production union ledger, and
branch/statement/complexity comparison. Appendix B pins the executable matrix.

## Next-Stage Handoff

Planning should start from the reviewed boundaries in this document, but every `[INFERRED]` bet and
mechanism remains agent-grade. Re-derive or challenge it if implementation evidence conflicts. The
owner-originated success criteria and register ownership are the settled constraints.

De-risk semantic multi-context resolution and batch transcript rollback first. Do not start Item 4
warning-location work, Item 2 resolver work, or a version migration. An independent design re-review
must verify C1–C5, M1–M5, the Item 4 boundary, API enforceability, and the deletion budget before
planning.

## Appendix A — Deletion and Production Accounting

### Automatic path union

OD-R41 remains automatic: every production file added, changed, moved, or deleted between OD-R30
and the candidate joins the union. The following is the planned starting union, not a fixed
allowlist. All nine files are byte-identical between OD-R30 and this design's starting checkout.

The provisional executable count is physical nonblank, noncomment code with docstring spans
excluded. The same counting script must run at OD-R30 and candidate. Raw LOC remains the Item 0
newline count. Per-file caps are design budgets; actual closeout evidence controls.

| Production path | Raw baseline | Executable baseline | Add/delete budget | Candidate cap |
|---|---:|---:|---:|---:|
| `analysis/part_instance_index.py` | 447 | 228 | +16 / -10 | 234 |
| `analysis/constraint_lowering.py` | 1,454 | 1,078 | +45 / -51 | 1,072 |
| `resolution/supplied_values.py` | 332 | 208 | +82 / -70 | 220 |
| `orchestration/pipeline_builder.py` | 1,051 | 641 | +16 / -34 | 623 |
| `snapshot/graph_rebuild.py` | 243 | 156 | +22 / -36 | 142 |
| `snapshot/serializer.py` | 251 | 157 | replacement, delta ≤ 0 | 157 |
| `orchestration/pipeline_context.py` | 152 | 62 | comments only | 62 |
| `snapshot/__init__.py` | 63 | 27 | comments only | 27 |
| `snapshot/loader.py` | 1,218 | 967 | comments only | 967 |
| **Planned starting union** | **5,211** | **3,524** | **+181 / -201** | **≤ 3,504** |

Named executable additions and deletions:

- **Part index:** add the structured error and active-path stack; delete revisit-as-empty and the
  complete `RecordingOccurrenceIndex` class.
- **Lowering:** add pure association, two prepared records, local transcript staging, and explicit
  dispatch; delete `collect_bare_actual_demand`, the cardinality-only exclusion selector, profile
  re-evaluation/requery in lowering, implicit package fallback, and duplicate expansion plumbing.
- **Supplied values:** add four small origin/resolution records, context comparison, provenance
  choice, and enrichment return; delete nested tuple `_demand`, route append/count loop, silent
  missing-source drop, last-write-wins `synth[target.qn]`, and route-specific tuple plumbing.
- **Live orchestration:** one prepare/enrich/lower flow replaces the demand probe, second index,
  materialize/bucket loop, recorder, and transcript extraction.
- **Replay:** one frozen prepare/enrich flow and batch carrier replace its demand probe, first frozen
  index, in-place bucket loop, and second frozen lowering index.
- **Serializer:** an association call replaces direct profile evaluation plus the old selector; its
  deepcopy/canonicalization loop remains.

Truth-bearing comment deletions/replacements include recorder references in
`part_instance_index.py`, `pipeline_context.py:133-137`, and `snapshot/__init__.py:12-18`; the
serializer transcript wording at `serializer.py:84-87`; and the profile-guard pairing at
`loader.py:773-775`. Do not retain comments about `collect_bare_actual_demand`, a read-only probe,
lowering-owned queries, or replay in-place enrichment.

Docs are a separate non-production ledger under OD-R42 and cannot offset executable growth:

| Documentation path | Raw baseline | Required correction |
|---|---:|---|
| `docs/architecture/reference/27-snapshot-generation.md` | 134 | Transcript comes from successful prepared owner expansion. |
| `docs/architecture/reference/28-constraint-lowering-and-catalog.md` | 95 | Prepared batch/enrichment/lowering replaces old signature and demand collector. |
| **Docs total** | **229** | Separate from production gate. |

`snapshot/capture.py`, `orchestration/snapshot_context.py`, and `analysis/parameter_groups.py` are
not planned changes. If implementation touches them, any other Python/template/model path, or any
other load-bearing doc, it joins the appropriate ledger automatically. A missed per-file cap must
first trigger simplification. The union must remain non-positive or receive the owner-reviewed
deviation required by OD-R43.

Closeout repeats Ruff `C901,PLR0912,PLR0915`, an identical AST branch/statement census, and source
absence checks for all five OD-R40 paths. Comment/doc deletion never offsets executable growth.

## Appendix B — Executable Acceptance Architecture

### Stable RED/GREEN surface

All five unchanged defect nodes live in
`tests/conformance/test_constraint_occurrence_demand_acceptance.py`:

1. `test_r4_live_anonymous_association`
2. `test_r4_valid_replay_not_corrupt`
3. `test_r5_finite_first_cycle_is_atomic`
4. `test_r7_shared_target_dedup_grouping_counts`
5. `test_r7_multi_target_order_permutations`

Those nodes import only APIs present at OD-R30 and candidate:
`build_pipeline_context`, `capture_snapshot`, `build_full_graph_from_snapshot`, and
`CodeGenerationError`. They do not import prepared-batch, demand, resolution, or cycle classes.
The cycle node asserts `type(error.__cause__).__name__` and public cause fields. Candidate-only unit
tests may import the new private seams.

### Public fixture observations

Every new fixture is licensed public source and includes `PROVENANCE.md`.

| Fixture | Pinned source and expected projection |
|---|---|
| `constraint_occurrence_demand/anonymous` | Package `OccurrenceDemandAnonymous`. Anonymous admitted part-owned actual references value `3.0`; a distinct anonymous unsupported-owner actual references `41.0`. Both identity QNs are null. Only `OccurrenceDemandAnonymous__design__admitted__admitted_value` appears, default `3.0`; catalog has one eligible and one `unsupported_owner` exclusion; warnings are `[]`; transcript contains only the admitted part owner. |
| `constraint_occurrence_demand/cycle` | Package `OccurrenceDemandCycle`. `Node` has a finite singleton declaration before `recursive : Node`; an `A → B → A` variant and declaration-reversed variants carry the same assertion. A pre-existing output target contains `b"sentinel\n"` and remains byte-identical on failure. |
| `constraint_occurrence_demand/overrides` | Package `OccurrenceOverride`. `Cell` asserts `reading >= 5.0`; sibling usages `low` and `high` supply `4.0` and `6.0`. Targets are `OccurrenceOverride__plant__low__reading` and `OccurrenceOverride__plant__high__reading`. Catalog has two eligible entries with `expected_value=True`; generated inputs carry 4.0/6.0; TEAx reports low `violated/False` and high `satisfied/True`. |
| `constraint_occurrence_demand/shared` | Package `DemandShared`; target `DemandShared__plant__source__value`; literal `17.0`. Calc route is in `calc_route.sysml`, assertion in `constraint_route.sysml`. Exactly one graph entry point has default `17.0`, group `calc_route_params`; one eligible constraint input names the target; catalog-native identity/path/channel fields match live/replay; counts are 1/1/0, exact OD-A08 INFO, warnings `[]`. |
| `constraint_occurrence_demand/constraint_only` | Package `DemandConstraintOnly`; target `DemandConstraintOnly__plant__source__value`; literal `23.0`; no calc binding. Live extraction currently exposes the winning record source as unavailable, so portable `constraint_route.sysml` yields group `constraint_route_params`. One graph entry point has default `23.0`; one eligible constraint input names the target; counts are 1/1/0, exact OD-A09 INFO, warnings `[]`. Unit cases separately prove exact-target and real-winning-record tiers. |
| `constraint_occurrence_demand/order` | Package `DemandOrder`. `a_collision` has real `101.0` plus supplied `11.0`; `b_nonliteral` has a highest-precedence CHAIN; `c_clean` has supplied `33.0`. Target order is the three exact spec QNs; only `c_clean` synthesizes with `33.0`; collision keeps `101.0`; counts and exact warnings are OD-A10's 3/2/1 sequence. |

Catalog assertions use only catalog-native fields: usage identity, owner instance path, expected
value, and evaluation channel. Values/groups are asserted on graph entry-point groups and emitted
input projection; target binding is asserted on `ConcreteConstraint.inputs`. The tests do not
invent a catalog value/group API.

### OD-A01–OD-A13 map

| Case | Exact proof |
|---|---|
| **OD-A01** | Unchanged `test_r4_live_anonymous_association`; candidate unit `tests/unit/test_constraint_usage_preparation.py::test_association_rejects_independent_decision_mutations_before_preflight`. Clone identity/location with `dataclasses.replace`/`deepcopy` before deletion, duplication, reorder, identity edit, and location edit; spy queries stay zero. |
| **OD-A02** | `tests/unit/test_constraint_usage_preparation.py::test_excluded_unsupported_zero_query_and_package_branch` covers admitted part/calc/package, excluded supported, requirement owner, and unknown owner. Only admitted part queries. Missing admitted frozen key alone wraps corruption. Unchanged replay node proves the valid transcript. |
| **OD-A03** | Existing unchanged `tests/conformance/test_constraint_lowering.py::test_multi_instance_three_ids_three_channels_shared_binding`, `tests/conformance/test_constraint_pipeline_threading.py::test_multi_instance_end_to_end_through_wired_path`, `tests/conformance/test_constraint_catalog_determinism.py::test_catalog_fingerprint_deterministic_across_repeated_live_loads`, and `tests/execution/test_constraint_execution.py::test_multi_instance_expansion_n_modules_one_predicate`. Pin cell[0]/[1]/[2] suffixes `5993bca31703d2d1`, `a2a2b85c4b80089f`, `53df666e4d2f4530` and shared channel `constraint_multi_instance__the_design__c__cell__power_calc__p`. |
| **OD-A04** | `tests/execution/test_constraint_occurrence_demand_execution.py::test_sibling_literal_overrides_produce_distinct_values_and_verdicts` asserts exact 4.0/6.0 generated inputs and violated/satisfied execution. |
| **OD-A05** | Unchanged `test_r5_finite_first_cycle_is_atomic`; candidate unit `tests/unit/test_constraint_usage_preparation.py::test_later_owner_cycle_discards_staged_transcript`. Owner A succeeds, B cycles; no batch/transcript returns and enrichment/lowering spies stay zero. Self-cycle cause fields are requested/edge owner/type `OccurrenceDemandCycle__Node`, feature `recursive`, path `(OccurrenceDemandCycle__Node, OccurrenceDemandCycle__Node)`. Indirect path is `(OccurrenceDemandCycle__A, OccurrenceDemandCycle__B, OccurrenceDemandCycle__A)` with closing B→A edge. |
| **OD-A06** | Existing unit nodes `test_bare_fixed` through `test_unrecognized_upper_bound_node_blocks`; existing conformance nodes `test_nine_instance_oracle`, `test_same_name_collision`, `test_equal_bounds_admit`, `test_cartesian_expansion`, `test_closure_times_multiplicity`, `test_determinism`, and `test_blocking_names_owner_and_feature`. Add `test_zero_count_returns_empty`, `test_multi_digit_occurrence_order_is_numeric` with `[0]` through `[11]`, and structural retype/diamond controls without changing the nine-path oracle. |
| **OD-A07** | Unchanged `test_r4_valid_replay_not_corrupt` captures immediately, compares association/target/group/count/input/catalog projections and warnings `[]`, and labels replay `same-checkout regression, non-certifying`. |
| **OD-A08** | Unchanged `test_r7_shared_target_dedup_grouping_counts` asserts the exact shared fixture projection, OD-A08 INFO, one producer, 1/1/0, and live/replay route/list reversals. |
| **OD-A09** | `tests/conformance/test_constraint_occurrence_demand_acceptance.py::test_r7_constraint_only_provenance_after_resolution` asserts the exact public projection. `tests/unit/test_logical_demand_resolution.py::test_constraint_only_provenance_ladder_and_missing_failure` covers exact captured source, real winning `values.sysml` source → `values_params`, usage fallback, conflicts, and total absence. |
| **OD-A10** | Unchanged `test_r7_multi_target_order_permutations` asserts exact target/synthesis order, defaults, `scanned=3`, `applied=2`, `non_literal_skips=1`, both spec warning bytes once/in order, and complete live/replay input reversal. |
| **OD-A11** | The five named nodes above are authored once, hashed, overlaid at OD-R30, and run one fresh process per node. RED must reach the named behavioral assertion; unchanged bytes pass at GREEN. Historical 31 greens remain controls only. |
| **OD-A12** | Run focused normal/`-O`, affected union, compatible full suite, explicit licensed A01/A04/A05/A08/A09/A10 selection, and TEAx execution separately. `-rs` exposes skips; a skip is unproven. |
| **OD-A13** | Evidence freezes the automatic changed-path union, applies zero-side treatment, reports raw/executable and Ruff/AST changes per file, and proves all five OD-R40 paths absent. Docs/tests/fixtures remain separate ledgers. |

Unchanged C1 controls run without edits or candidate-only imports:

- `tests/conformance/test_sibling_channel_ambiguity.py::test_chamber_power_disambiguated_to_chamber_b`
- `tests/conformance/test_matcher_reclassification.py::test_quoted_owner_refs_reclassify_to_design_attribute`
- `tests/conformance/test_matcher_reclassification.py::test_shared_design_attribute_key_collapses`
- `tests/conformance/test_ife_plant.py::test_ife_plant_graph_builds`
- `tests/conformance/test_ife_plant.py::test_shape4_wires_to_exact_channel`
- `tests/conformance/test_fusion_tea_snapshot.py::test_fusion_tea_snapshot_zero_offenders`
- `tests/conformance/test_fusion_tea_snapshot.py::test_renamed_consumers_collapse_to_one_source_ep`

Candidate unit nodes
`tests/unit/test_logical_demand_resolution.py::test_absolute_target_accepts_distinct_scopes_with_equal_outcomes`
and `::test_absolute_target_rejects_different_semantic_outcomes` isolate the new rule.

### Unchanged-test overlay and hashes

Test hashes cannot exist before the test bytes are authored. Evidence creates them once, records the
actual SHA-256 values, and verifies the same manifest at RED and GREEN; no placeholder digest is
accepted.

```bash
ITEM1_RED_ROOT=$(mktemp -d /tmp/item1-red.XXXXXX)
git worktree add --detach "$ITEM1_RED_ROOT/sysml-codegen" ecdc7285be1508c08e82830c93072306f40e6b34
git -C ../agentic-mbse worktree add --detach "$ITEM1_RED_ROOT/agentic-mbse" 515e08bbcd70aa9d23212765161bd02b3e3d8f23
git -C ../teax worktree add --detach "$ITEM1_RED_ROOT/teax" d545701f575133350474108c96202a2ac5244462
```

At a committed candidate revision, overlay only the unchanged public RED file and its fixtures:

```bash
GREEN_REV=$(git rev-parse HEAD)
git archive "$GREEN_REV" -- tests/conformance/test_constraint_occurrence_demand_acceptance.py tests/fixtures/constraint_occurrence_demand | tar -xf - -C "$ITEM1_RED_ROOT/sysml-codegen"
find tests/conformance/test_constraint_occurrence_demand_acceptance.py tests/fixtures/constraint_occurrence_demand -type f -print0 | sort -z | xargs -0 sha256sum > "$ITEM1_RED_ROOT/overlay.sha256"
sha256sum tests/conformance/test_constraint_occurrence_demand_acceptance.py > "$ITEM1_RED_ROOT/unchanged-tests.sha256"
```

Run `sha256sum -c "$ITEM1_RED_ROOT/overlay.sha256"` from both the candidate and RED worktree before
tests. Record the manifest and standalone test-file digest in evidence. Create the RED environment
with `uv sync --frozen` from its sysml-codegen worktree; its sibling paths resolve to the pinned
agentic-mbse and TEAx worktrees above.

Run each node in a fresh process at RED and GREEN:

```bash
RED_NODES=(
  tests/conformance/test_constraint_occurrence_demand_acceptance.py::test_r4_live_anonymous_association
  tests/conformance/test_constraint_occurrence_demand_acceptance.py::test_r4_valid_replay_not_corrupt
  tests/conformance/test_constraint_occurrence_demand_acceptance.py::test_r5_finite_first_cycle_is_atomic
  tests/conformance/test_constraint_occurrence_demand_acceptance.py::test_r7_shared_target_dedup_grouping_counts
  tests/conformance/test_constraint_occurrence_demand_acceptance.py::test_r7_multi_target_order_permutations
)
for node in "${RED_NODES[@]}"; do uv run --frozen pytest -q -rs "$node"; done
```

### Candidate gates

```bash
uv run --frozen pytest -q -rs tests/conformance/test_constraint_occurrence_demand_acceptance.py tests/unit/test_constraint_usage_preparation.py tests/unit/test_logical_demand_resolution.py tests/unit/test_part_instance_index.py tests/unit/test_supplied_values.py
uv run --frozen python -O -m pytest -q -rs tests/conformance/test_constraint_occurrence_demand_acceptance.py tests/unit/test_constraint_usage_preparation.py tests/unit/test_logical_demand_resolution.py tests/unit/test_part_instance_index.py tests/unit/test_supplied_values.py
uv run --frozen pytest -q -rs tests/unit/test_occurrence_roundtrip_parity.py tests/conformance/test_part_instance_index.py tests/conformance/test_constraint_lowering.py tests/conformance/test_constraint_lowering_integrity.py tests/conformance/test_constraint_pipeline_threading.py tests/conformance/test_snapshot_constraint_parity.py tests/conformance/test_constraint_migration_mapping.py tests/conformance/test_parameter_group_deriver.py tests/conformance/test_sibling_channel_ambiguity.py tests/conformance/test_matcher_reclassification.py tests/conformance/test_ife_plant.py tests/conformance/test_fusion_tea_snapshot.py
uv run --frozen pytest -q -rs tests/
TEAX_SIMKIT_PATH=../teax/packages/teax-simkit uv run --frozen pytest -q -rs -o addopts= -m execution tests/execution/test_constraint_occurrence_demand_execution.py tests/execution/test_constraint_execution.py::test_multi_instance_expansion_n_modules_one_predicate
```

Run a separate explicit licensed selection containing A01, A04, A05, A08, A09, and A10 and record
license state plus `-rs` output. Default full-suite success cannot certify skipped public cells.

---

Next Step: independent `my-design-review`; after approval, `my-plan`
