# Design: calc-definition constraint gates

**Status:** Draft, revision 2 after independent review

**Owner:** Reid W.

**Created:** 2026-08-13

**Revised:** 2026-08-13

**Code inspected:** `sysml-codegen` branch `item7-rebuild` at `cc14cf07630ed06c7f5cd16bff14cc055709138d`

## Overview

Calculation-definition constraints expand inside elaboration into one gate for every concrete calculation occurrence. The authored constraint remains the single usage-level authority; each gate carries the exact calculation occurrence identity and reuses an already-decided input source.

This revision keeps that architecture and closes review findings F1–F8. It freezes identity and ordering, centralizes input dereference, separates inline and definition-typed resolution, sequences Item 8, and makes the implementation and acceptance surfaces exact.

## Related artifacts

- Primary contract: `.project/completed/20260813_calcdef-constraint-gate-design/spec.md`
- Independent review: `.project/completed/20260813_calcdef-constraint-gate-design/design-review.md`
- Probe findings and models: `.project/completed/20260813_calcdef-constraint-gate-design/probes/findings.md` and `probes/models/`
- Epic contract: `.project/backlog/epic_constraint_semantics_contract.md`, Items 6 and 8
- Rulings: `.project/active/constraint-semantics-contract/rulings-20260812.md`, Q2, Q3, Q5
- Landed catalog design: `.project/completed/20260813_constraint-catalog-totality/design.md`
- Landed coverage design: `.project/completed/20260813_constraint-coverage-policy/design.md`
- Inherited architecture: `.project/backlog/epic_elaborate_first_architecture.md`
- Follow-on backlog item: `.project/completed/20260813_calcdef-constraint-gate-design/implementation-item.md`

## The point

`[INHERITED: rulings-20260812.md owner-stated design-search frame]` Physics constraints must make design search trustworthy.

`[INHERITED: rulings-20260812.md Q2 and Q5; source grade [AGENT] (ratified by owner, 2026-08-12)]` One calculation-definition assertion executes once per concrete calculation occurrence, while the authored usage remains one coverage member. Repeated uses must not collapse, and a failed occurrence must remain in the complete result population.

The falsifier is direct: two sibling calculations use one definition, one gate fails, and generation collapses the gates, orders a gate before its real producer, omits the failure, or cannot join the result back to its exact calculation.

## Core concept

The instance graph is the one semantic authority. A usage record represents the authored constraint. A qualified constraint `NodeId` represents each concrete gate by pairing that usage with one full calculation `NodeId`. Gate inputs either point to the matched calculation's exact input port or retain the existing typed source resolved for a definition-typed constraint actual. Projection renders those graph decisions; it never rediscovers them from names or builds a second occurrence inventory.

## Key bets

- **B1. The live elaboration indexes contain the last lossless join point.** The probe confirms exact definition matches and exact root-formal recovery while `FeatureSlotIndex` is live. *If false → no later snapshot or rendered name can recover the required formal identity lawfully.*
- **B2. One calculation input port can remain the source authority for every gate that refers to that formal.** The existing calculation port already distinguishes explicit edges, modeled defaults, and defaultless inputs. *If false → the design would need duplicate entry points or a second source-resolution authority.*
- **B3. Catalog order can remain producer-authored.** TEAx can consume the sealed ordered occurrence rows and refuse disagreement without inventing another sort. *If false → cross-repository result drill-down would need a duplicated identity-ordering implementation.*

## Key decisions

- **D1. Qualify `NodeId` by one attached calculation ID.** Rejected: a side field on `ConstraintNode` because the graph map key would still collide; a new occurrence-ID hierarchy because every port and dependency map would widen.
- **D2. Add one `CalculationInputRef` and one dereference law.** Rejected: copying an `InputRef`, because literals and defaults are keyed by consumer and would produce duplicate public inputs; scattered special cases, because validation and topology would drift.
- **D3. Preserve the existing constraint-actual resolver for definition-typed constraints.** Rejected: treating a constraint-definition formal as if it were the calculation formal, because their declaration IDs differ.
- **D4. Keep outer snapshot v6 and bump only the embedded graph to v4.** Rejected: an outer bump, because the envelope shape and nested-authority mechanism do not change.
- **D5. Keep Item 3 report schemas unchanged and expand catalog 4.0.0.** Rejected: adding calculation identity to runtime results, because the existing `constraint_id` can join through a sealed catalog occurrence row.

## Revision contracts in required order

### R1. Provenance and delivery boundary

No statement in this design or the follow-on item upgrades orchestration text or ratified agent decisions to owner-originated authority.

- `[INHERITED: epic_constraint_semantics_contract.md Item 6; source grade [AGENT] (ratified by owner, 2026-08-12)]` Production implementation is a separate follow-on from this design-stage delivery.
- `[INHERITED: orchestration stage input]` Filing the follow-on backlog item does not authorize implementation.
- `[INHERITED: spec.md; Item 3; rulings Q5]` The BLOCK denominator/build-halt conflict remains parked.

These statements remain challengeable at their true source grades.

### R2. Frozen one-level `NodeId` identity

#### Data model and constructor invariants

`NodeId` remains a frozen dataclass and gains `attached_calculation: NodeId | None = None`. Hash and equality include all four fields.

`NodeId.__post_init__` enforces:

1. `kind`, `scope`, and `declaration` have the existing exact wrapper types.
2. An absent attachment is lawful for any existing node kind.
3. A present attachment is lawful only on `kind == CONSTRAINT` with an outer `DeclarationId`.
4. The attachment has `kind == CALCULATION`, has `attached_calculation is None`, and has exactly the same `scope` as the outer node.
5. No other nesting is possible. Maximum qualification depth is one.

`InstanceGraph.validate()` adds the owner-sensitive rule: a calc-definition `ConstraintNode` must have one attachment, its attached ID must key an existing `graph.calcs` node whose `calculation_definition_id` equals the usage record's `owner_definition_id`, and a non-calc-definition constraint must have no attachment.

The concrete gate identity is therefore losslessly:

```text
(constraint usage DeclarationId, full unqualified CalcNode.node_id)
```

#### Exact v4 wire grammar

`NodeId.to_wire()` is the only encoder. It returns canonical compact JSON text. An internal `to_data()` supplies structured values for nesting; no caller assembles node JSON.

- An unqualified node is an array of exactly three values: `[kind, scope, declaration]`.
- A qualified node is an array of exactly four values: `[kind, scope, declaration, attached]`.
- `kind` is exactly `"attribute"`, `"calculation"`, or `"constraint"`.
- `scope` is exactly `[` `"occurrence"`, canonical `OccurrenceId.to_wire()` string `]` or `[` `"package"`, lowercase hyphenated UUID string `]`.
- `declaration` is exactly `[` `"slot"`, UUID string `]` or `[` `"declaration"`, UUID string `]`.
- `attached` is structured JSON data, not a JSON-encoded string and not null. It is exactly an unqualified three-value calculation-node array.
- An unqualified v4 node may not carry a fourth null. A qualified node may not carry a nested four-value array.
- Canonical JSON uses `json.dumps(data, separators=(",", ":"), ensure_ascii=True)` and the canonical UUID/occurrence encoders.

`NodeId.from_wire()` validates JSON types, array arity, closed tags, UUIDs, canonical occurrence text, and the one-level constructor invariants. It then requires `decoded.to_wire() == input`; whitespace, alternate UUID spelling, noncanonical occurrence text, extra fields, nested strings, null attachments, and recursive attachments fail.

The graph v4 codec and catalog 4.0.0 both call this encoder/parser. Catalog `calculation_node_id` is exactly `attached_calculation.to_wire()`. There is no second catalog serializer.

#### Sole total-order oracle

`NodeId.sort_key()` is explicit and is the only lawful way to order nodes. Raw `sorted(node_ids)`, `to_wire()` lexical order, rendered path order, and public `constraint_id` order are forbidden.

The tuple is:

```text
(kind_rank, scope_key, declaration_key, attachment_key)
```

- `kind_rank`: attribute `0`, calculation `1`, constraint `2`.
- occurrence scope: `(0, steps)`, with each step `(root_uuid.hex, index_tag, index_value)`; `None` is `(…, 0, 0)` and an integer is `(…, 1, n)`.
- package scope: `(1, package_uuid.hex)`.
- slot declaration: `(0, root_uuid.hex)`; declaration ID: `(1, uuid.hex)`.
- no attachment: `(0,)`; attachment: `(1, attached_calculation.sort_key())`.

Every position compares values of one fixed type within its tag, so occurrence/package scopes and null/indexed steps are totally ordered. Tests freeze cross-variant order as well as hash/map behavior.

### R3. One centralized `CalculationInputRef` dereference law

The graph input union gains `CalculationInputRef(port: ConsumerPortId)`. Only a qualified constraint input may carry it.

`InstanceGraph.dereference_input(consumer_id, input_ref)` owns the law. No validator, projector, selector, topology builder, or codec duplicates it.

For a direct `NodeRef`, `ProducerRef`, or `LiteralInput`, it returns that terminal source unchanged. For a `CalculationInputRef`, it proves all of the following:

1. `consumer_id` keys a qualified constraint.
2. `input_ref.port.consumer == consumer_id.attached_calculation`.
3. The target calculation exists.
4. The target formal is present in exactly one of the calculation's resolved `inputs` or `unbound_formals` maps.
5. A resolved calculation input is not another `CalculationInputRef`; dereference depth is one.

The result carries the originating calculation port plus exactly one terminal state: `NodeRef`, `ProducerRef`, `LiteralInput`, modeled-default metadata, or defaultless metadata.

Every edge consumer calls this law:

| Consumer | Required behavior after dereference |
|---|---|
| Graph edge validation | Validate the terminal node/producer and the port/occurrence invariants. |
| Cycle and semantic dependency inspection | Follow the terminal `ProducerRef` calculation; do not add the matched calculation merely because it owns the port. |
| Target selection closure | Include a terminal producer calculation or attribute node exactly as for a direct edge. |
| Typed module topology | Add the terminal producer calculation as the gate dependency. Literal, attribute, modeled-default, and defaultless states add no artificial calculation-module dependency. |
| Projection | Fetch the `InputSource` already recorded for the originating calculation port; never mint a gate-local source. |
| Graph v4 codec | Encode only the exact target `ConsumerPortId`; after full decode, graph validation invokes the same dereference law before returning the graph. |

Projection maintains a source map keyed by calculation `ConsumerPortId` while it builds calculation module inputs. Gate projection dereferences, then requires that exact key in the map. A producer-backed source still returns the same producer channel, and topology now guarantees that producer runs first.

The edge codec shape is exact:

```text
{"kind":"calculation_input","target":<ConsumerPortId data>}
```

Only keys `kind` and `target` are accepted. The target uses the existing exact consumer-port codec, which uses the one `NodeId` codec above. Cross-occurrence, missing-port, chained-reference, producer-cycle, and selection-closure mutations fail through the centralized law.

### R4. Inline and definition-typed formal resolution are distinct

#### Inline predicate path

An inline calc-definition assertion refers directly to formals on its owning calculation definition.

1. While `FeatureSlotIndex` is live, recover each leaf's exact root calculation formal.
2. Require that root to belong to `owner_definition_id`.
3. On each matched `CalcNode`, find exactly one input port with that root-formal provenance.
4. Store `CalculationInputRef` to that matched port.

Missing, duplicate, foreign-definition, or cross-occurrence ports are `SI_CONSTRAINT_CALC_FORMAL_INVALID`. No unbound fallback is invented.

#### Definition-typed constraint path

A definition-typed assertion's predicate leaves are constraint-definition formals. Their IDs must not be compared to calculation-formal IDs.

1. Run the existing exact constraint-formal actual resolver.
2. If the resolved actual's semantic referent is a formal on the owning calculation definition, map that exact formal to the matched calculation occurrence port and emit `CalculationInputRef`.
3. If the resolved actual is a literal, attribute, producer, or other already-supported typed source, retain that direct resolved source.
4. If the constraint formal is omitted, retain its existing constraint-definition default or defaultless behavior. Do not redirect it unless the modeled actual explicitly refers to a calculation formal.
5. Reject mismatched, duplicate, ambiguous, foreign-definition, or cross-occurrence formal identities with `SI_CONSTRAINT_CALC_FORMAL_INVALID`.

This is one resolver authority with a calc-formal redirection case, not a calc-definition-specific resolver lane. It preserves the spec's `[INFERRED]` source grade and makes it testable rather than silently hardening it.

### R5. Item 8 prerequisite and ownership

`[INHERITED: epic_constraint_semantics_contract.md Item 8; source grade [AGENT] (ratified by owner, 2026-08-13)]` Item 8 fixes the constraint-formal and computed-attribute unit lane and names Item 6 as a consumer.

Item 8 is frozen in the reviewed codegen commit
`62a07e5c870158672eb100f1cba73adfe4c9df28`. Its exact evidence bundle is
`.project/completed/20260813_unit-lane-port-metadata/verification.md`. This full SHA, not the branch name or the
older `cc14cf0…` evidence baseline, satisfies Item 6's unit-lane dependency pin. Item 6 remains
separately blocked on owner authorization.

Ownership is split by field and gate:

- **Item 8 owns `PortMetadata.unit`.** It owns the A9-shape and radius-derivation characterizations plus agreement/disagreement tests for calculation, constraint-formal, and computed-attribute ports.
- **Item 6 owns calc-port `formal_provenance` completeness.** It may populate missing root-formal provenance, but it must preserve Item 8's unit text and refusal behavior.
- **The instance graph remains the runtime authority** for the combined `PortMetadata`; item ownership is delivery ownership, not a second semantic source.
- **Item 8 is independently certified.** Its final Git-derived inventory has 23 sorted tracked
  snapshot paths and exactly 23 rows, with no missing, extra, duplicate, added, removed, or stale
  path. Every graph payload and relevant unit map is identical, so Item 8 ran no capture command;
  the v3 recapture count is zero and no receipt exists. The exact sorted set and per-path digests
  are in the evidence bundle.
- **A later authorized Item 6 owns its graph-v4 recapture.** It must derive its own tracked snapshot
  set from Git at Item 6's immutable pre-recapture baseline. It must not reuse Item 8's count or the
  historical accepted-batch subset.

Avoiding duplicate recapture requires an explicit epic-owner amendment that authorizes a joint Item 8/Item 6 delivery and changes the dependency and certification boundaries. Item 6 does not assume that amendment. Without it, Item 8 lands and certifies independently, including its v3 recapture when churn fires; only then may a separately authorized Item 6 start and later own the v4 recapture.

Item 6 consumes these exact Item 8-owned nodes from the frozen commit:

- `tests/conformance/test_unit_lane_port_metadata.py::test_constraint_and_calculation_unit_agreement_projects_one_entry` — exact `Dimensionless` on both ports produces one public entry source.
- `tests/conformance/test_unit_lane_port_metadata.py::test_constraint_and_calculation_unit_disagreement_refuses` — exact `cm` versus `m` raises `ProjectionError` / `SI_RENDERING_COLLISION` on `UnitLaneConstraintDisagreement__disagreement__shared_length`; no conversion.
- `tests/conformance/test_unit_lane_port_metadata.py::test_computed_and_calculation_unit_agreement_projects_one_entry` — exact `m` on both ports produces one public entry source.
- `tests/conformance/test_unit_lane_port_metadata.py::test_computed_and_calculation_unit_disagreement_refuses` — exact `cm` versus `m` raises `ProjectionError` / `SI_RENDERING_COLLISION` on `UnitLaneComputedDisagreement__disagreement__shared_length`; no normalization.
- `tests/conformance/test_unit_lane_port_metadata.py::test_live_in_place_and_relocated_routes_preserve_unit_metadata` — exact selected port IDs, complete `PortMetadata`, graph-v3 units, and projected unit text agree on live, in-place v6, and relocated v6 routes.

### R6. Construction, attachment, disposition, and atomicity

Elaboration order is fixed:

1. Build values, deep literals, aliases, computed producers, and calculation nodes.
2. Collect calculation input candidates while `FeatureSlotIndex` is live.
3. Resolve calculation aliases, expressions, and bindings.
4. Seal every calculation formal as one resolved edge, modeled default, or defaultless unbound formal, including Item 8 unit metadata and Item 6 formal provenance.
5. Create the usage-tier constraint record.
6. Match calc-definition owners, resolve inline or definition-typed inputs, validate the complete local gate batch, and merge it atomically.
7. Build ordinary constraints through their established resolver path.
8. Run readiness and full graph validation.

No calc gate enters the later ordinary-constraint queue. There is no post-build fill.

For usage `U`, the expected set is every `graph.calcs` node whose `calculation_definition_id == U.owner_definition_id`, ordered by `NodeId.sort_key()`. `ConstraintUsageRecord` gains the exact `owner_definition_id` for calc-definition owners. This derived set is not stored as a second inventory.

Before merge, the local batch proves exact expected/actual set equality, unique gate IDs, one formal mapping per input, same-usage predicate and polarity, and same-occurrence input references. A failed batch contributes zero gate nodes to the projectable graph.

Disposition and diagnostics are cause-based:

| Cause | Disposition | Diagnostic/result |
|---|---|---|
| Missing or malformed owner identity | `non_reaching / classification_incomplete / error` | `SI_CONSTRAINT_CALC_OWNER_INVALID`; nonprojectable |
| Valid owner, zero matches | `non_reaching / owner_has_no_occurrences` | existing `SI_CONSTRAINT_UNATTACHED`; asserted warning, nonasserted info |
| Nonempty ADMIT | `eligible / admitted / info` | N executable gates |
| Nonempty plain or requirement form | `excluded / unassessed_form / info` | N excluded occurrence rows |
| Nonempty nonnumerical form | `excluded / non_numerical / info` | N excluded occurrence rows |
| Nonempty BLOCK | `excluded / profile_blocked / info` | existing `SI_CONSTRAINT_BLOCKED`; no package |
| Invalid formal mapping | no fabricated transition | `SI_CONSTRAINT_CALC_FORMAL_INVALID`; no batch |
| Missing, duplicate, extra, malformed, or partial batch | no fabricated transition | `SI_CONSTRAINT_CALC_EXPANSION_INVALID`; no batch |

The three new codes are declared in `src/sysml_codegen/elaboration/diagnostics.py`. Messages include the usage declaration ID; formal/expansion failures also include deterministic calculation/formal IDs.

Predicate IR is shared immutably across occurrences. `is_negated` is copied to each gate. Existing wrapper finalization applies polarity once, preserves indeterminate, and flips a simple margin once. Requirement-side evaluation and predicate feature chains remain out of scope.

### R7. Projection, catalog, reporting, and fail-closed order

Let `G` be the eligible gate nodes ordered by `node_id.sort_key()`. `G` is the sole occurrence-order oracle.

In one pass over `G`, projection emits:

1. wrapper modules;
2. eligible catalog `concrete_entries`;
3. aggregator input channels; and
4. the corresponding `EXPECTED_IDS` tuple of minted public `constraint_id` values.

`src/sysml_codegen/generation/modules.py` materializes one local ordered tuple from those already-ordered aggregator inputs. The same tuple is used both to render the aggregator template's `EXPECTED_IDS` and to populate `ConstraintGenerationPlan.expected_constraint_ids: tuple[str, ...]` in `src/sysml_codegen/generation/constraint_plan.py`. The plan field is a structured receipt of the rendered order, not a fresh derivation and not a second identity authority.

Excluded occurrence rows are independently ordered by their node's same `sort_key()`. No tier sorts by `constraint_id`, display path, or serialized JSON text.

Catalog 4.0.0 adds `calculation_node_id: string | null` to eligible and excluded occurrence rows. It is required and canonical for calc-definition occurrences and null otherwise. The lossless occurrence identity is the existing `declaration_id` plus this field. Usage rows remain one per authored usage and gain no occurrence array.

Generation preflight compares ordered identities, not only sets and counts:

- graph eligible sequence by `sort_key()`;
- catalog eligible row sequence;
- wrapper/module sequence;
- aggregator input sequence; and
- `ConstraintGenerationPlan.expected_constraint_ids`, which is the exact sequence rendered as `EXPECTED_IDS`.

The CLI performs this comparison after the complete generation plan exists and before any output-tree mutation. It compares the carried sequence with the ordered catalog identities and ordered wrapper identities, in addition to the graph and aggregator checks. It also verifies usage counts, unique calculation IDs per usage, exact owner-derived occurrence sets, and unique public IDs. Any disagreement is a named integrity refusal before files are written or package sealing begins.

The aggregator returns results in `EXPECTED_IDS` order and retains Item 3's completeness and worst-state laws. With N eligible occurrences there are exactly N results; missing, duplicate, or extra values fail. One violation or indeterminate result cannot be hidden at the first, middle, or last position.

TEAx does not sort. It preserves the sealed eligible catalog row order, requires the report's ordered `constraint_id` sequence to equal that catalog sequence exactly, and constructs one catalog view per result. Missing, duplicate, malformed, or extra catalog/result IDs fail at package load or query construction. The current `_case_view` behavior that silently filters a missing catalog lookup is deleted. The report and evidence schemas remain unchanged.

### R8. Versions, sealing, and compatibility

| Contract | Decision |
|---|---|
| Embedded instance graph | `instance-graph/v3` → `instance-graph/v4` |
| Outer snapshot envelope | keep `6` |
| Projector semantics | `instance-projector/v1` → `instance-projector/v2` |
| Constraint catalog | `3.0.0` → `4.0.0` |
| Runtime/report contract | keep `2.0.0` |
| Evidence schema | unchanged |

Graph v4 is exact and has no v3 shim. An outer v6 snapshot naming v3, an unknown version, a malformed identity/reference, or a missing v4 field refuses with `SI_SNAPSHOT_INVALID` before projection. The outer envelope stays v6 because its shape already seals embedded graph and projector tokens.

The projection receipt records projector v2 and its computation digest. Catalog value/version changes move the model-contract fingerprint. Wrapper/source changes move the executable fingerprint. Runtime 2.0.0 remains because report value schemas do not change. Snapshot relocation changes none of these semantic values.

A separately authorized Item 6 derives the then-current tracked
`tests/fixtures/**/instance_graph_snapshot.json` set from Git at its own immutable pre-recapture
baseline and recaptures every final tracked path at graph v4 through
`tests/conformance/test_v6_recapture_batch.py` and
`tests/fixtures/v6_recapture_batch/batch.json`. Its disposition rows must equal the union of its
pre/final sets with no missing, extra, or duplicate row; its reviewed graph-v4 rows must equal its
final set; and every addition/removal needs authority. Item 8's frozen evidence measured 23 paths,
equal pre/final sets, and zero v3 recaptures, but neither that count nor the historical 15-path
accepted subset is Item 6's future scope authority. Old v3 expectations and calc-definition
`owner_kind_unattachable` assertions are deleted from the Item 6 line rather than supported in
parallel.

## Component overview and exact file manifest

### sysml-codegen production

- `src/sysml_codegen/elaboration/identity.py:149`: one-level `NodeId`, strict codec helpers, `sort_key()`.
- `src/sysml_codegen/elaboration/diagnostics.py:10`: three new cause codes.
- `src/sysml_codegen/elaboration/graph.py:90`: `CalculationInputRef`, centralized dereference, owner and edge invariants, cycle traversal.
- `src/sysml_codegen/elaboration/__init__.py`: export the new graph input vocabulary.
- `src/sysml_codegen/elaboration/elaborate.py:558`: Item 8-aware port metadata, phased resolution, exact attachment, two formal paths, atomic expansion.
- `src/sysml_codegen/elaboration/project.py:205`: source cache/dereference, selection closure, topology, `sort_key()`-ordered wrappers/catalog/aggregator.
- `src/sysml_codegen/snapshot/instance_graph.py:64`: graph v4, qualified identity, calculation-port edge codec, exact decode refusal.
- `src/sysml_codegen/contracts/versions.py:35`: catalog 4.0.0.
- `src/sysml_codegen/resolution/models.py:524`: calculation identity on eligible/excluded rows.
- `src/sysml_codegen/generation/modules.py:354`: derive one ordered expected-ID tuple from aggregator inputs, use it for rendering, and pass it into the generation plan.
- `src/sysml_codegen/generation/constraint_plan.py:17`: carry structured `expected_constraint_ids` beside rendered sources and coverage.
- `src/sysml_codegen/cli/__init__.py:317`: ordered graph/catalog/aggregator totality.

Version/sealing surfaces must be inspected and their tests updated even if their production shape remains unchanged:

- `src/sysml_codegen/snapshot/envelope.py:100`
- `src/sysml_codegen/orchestration/exact_pipeline_context.py:60`
- `src/sysml_codegen/contracts/model_contract.py:60`
- `src/sysml_codegen/contracts/seal.py:95`
- `src/sysml_codegen/templates/constraint_types.py.jinja2:23`
- `src/sysml_codegen/templates/report_aggregator.py.jinja2:18`

### sysml-codegen tests and migrations

- `tests/unit/test_calcdef_constraint_gate_identity.py` (new): hash/map keys, total cross-scope ordering, `ConsumerPortId`, dependency-map keys, one-level construction, catalog round trip.
- `tests/unit/test_calcdef_constraint_input_ref.py` (new): centralized dereference categories and missing/cross/chained port mutations.
- `tests/unit/test_constraint_attachment_cause.py`: zero/one/many and exact disposition transitions.
- `tests/conformance/test_elaboration_identity_vertical.py`: canonical re-encode and malformed/recursive qualified identity refusal.
- `tests/conformance/test_elaboration_contract_matrix.py`: direct and dereferenced producer cycles and dangling edges.
- `tests/conformance/test_elaboration_projection_one_way.py`: producer-backed gate topology and no rediscovery.
- `tests/conformance/test_exact_target_selection.py`: producer and attribute selection closure through a gate.
- `tests/conformance/test_constraint_usage_domain_codec.py`: exact usage/qualified-edge v4 round trip.
- `tests/conformance/test_elaboration_graph_roundtrip.py`: v4 pin and v3/unknown/missing-shape refusal.
- `tests/conformance/test_constraint_usage_domain_totality.py`: owner-derived exact set and atomic N.
- `tests/conformance/test_constraint_catalog_totality.py`: catalog 4 ordered identity and mutation refusal.
- `tests/conformance/test_constraint_generation_plan_totality.py` (new): kept `test_expected_constraint_id_carrier_disagreement_refuses_before_write` mutation proves a stale, missing, duplicate, extra, or reordered carrier fails before output mutation.
- `tests/conformance/test_exact_pipeline_context.py`: projector v2 receipt and disagreement.
- `tests/conformance/test_catalog_schema_version.py`: catalog 4 producer/consumer pin gate.
- `tests/conformance/test_runtime_contract_version.py`: catalog 4 with runtime still 2.0.0.
- `tests/conformance/test_snapshot_v6_routes.py`: outer v6 / graph v4 live, in-place, relocated parity.
- `tests/conformance/test_exact_route_constraint_portability.py`: receipt/catalog/package/result portability.
- `tests/conformance/test_v6_recapture_batch.py`, `tests/fixtures/v6_recapture_batch/batch.json`, and
  its `README.md`: one reviewed final-schema graph-v4 recapture over the exact Git-derived Item 6
  final tracked set, with union/pre/final row equality and authorized path-set drift. Item 8's
  measured 23-path set and historical 15-path accepted subset are evidence, not fixed Item 6
  scope.
- `tests/execution/test_calcdef_constraint_gate.py` (new): public source sharing, topology, polarity, failed sibling positions, drill-down, and `test_many_renders_expected_ids_in_node_sort_order`, which imports the generated aggregator and asserts its rendered `EXPECTED_IDS` tuple equals the public ordered catalog IDs.
- `tests/execution/test_constraint_verdicts_exact_route.py`: unchanged Item 3 completeness/headline contract.

Item 8-owned kept characterizations must be recorded by exact path in its verification before Item 6 starts. Item 6 runs them unchanged as a prerequisite gate.

### TEAx production, tests, and fixture migration

Production:

- `packages/teax-simkit/simkit/evaluation/package_load.py`: accept only catalog 4.0.0 on the new consumer line and validate ordered join population.
- `packages/teax-simkit/simkit/study/model_contract.py`: preserve ordered entries, validate exact calc identity and duplicates.
- `packages/teax-simkit/simkit/study/query.py`: expose calculation drill-down and replace silent filtering with refusal.

Existing tests to revise:

- `packages/teax-simkit/simkit/tests/evaluation/test_package_load.py`
- `packages/teax-simkit/simkit/tests/evaluation/test_package_trust.py`
- `packages/teax-simkit/simkit/tests/evaluation/test_projection.py`
- `packages/teax-simkit/simkit/tests/study/test_model_contract_skew.py`
- `packages/teax-simkit/simkit/tests/study/test_query.py`
- `packages/teax-simkit/simkit/tests/study/test_no_reconstruction.py`
- `packages/teax-simkit/simkit/tests/study/test_compatibility.py`
- `packages/teax-simkit/simkit/tests/study/test_partial_coverage_policy.py`
- `packages/teax-simkit/simkit/tests/study/test_calcdef_constraint_catalog.py` (new cross-repository acceptance home)

Regenerate every committed TEAx package that embeds catalog 3.0.0, not only a new fixture:

- `simkit/tests/evaluation/fixtures/constraint_free/package_live/`
- `simkit/tests/evaluation/fixtures/excluded_only/package_live/`
- `simkit/tests/evaluation/fixtures/zero_channel/package_live/`
- `simkit/tests/evaluation/fixtures/sealed_package/package_live/`
- `simkit/tests/evaluation/fixtures/f1_arithmetic/package_live/`

Add and vendor `simkit/tests/evaluation/fixtures/calcdef_constraint_gate_many/package_live/` from the final codegen producer candidate. Its contract files record the producer SHA. No standalone hand-authored catalog fixture substitutes for generated package acceptance.

### Documentation

- `CLAUDE.md`
- `docs/architecture/modeling-assumptions.md`
- `docs/architecture/verification-matrix.md`
- `docs/architecture/reference/27-snapshot-generation.md`
- `docs/architecture/reference/29-contracts-and-sealing.md`

These document Item 8 metadata ownership, qualified identity, centralized dereference, graph v4 under envelope v6, projector v2, catalog 4.0.0, exact ordering, recapture, and consumer refusal.

## Named fixture and mutation matrix

Every claimed public category has one owner and observation route.

| Category | Named fixture or mutation | Public observation |
|---|---|---|
| Valid zero | `tests/fixtures/calcdef_constraint_gate_zero/` | CLI live/snapshot diagnostics and usage catalog |
| Inline literal, design attribute, modeled default | `tests/fixtures/calcdef_constraint_gate_one/` | generated input schema, source IDs, execution report, catalog join |
| Defaultless same formal | `calcdef_constraint_gate_one`, public case `defaultless_supplied.json` | one required public field supplied through generated package; calculation and gate share it |
| Producer-backed same formal and repeated definitions | `tests/fixtures/calcdef_constraint_gate_many/` | target selection, pipeline order, source ID, generated field count, report drill-down |
| Failure at every ordered position | `calcdef_constraint_gate_many`, cases `fail_first.json`, `fail_middle.json`, `fail_last.json` | exact result order and violation headline |
| Positive/negated polarity | `calcdef_constraint_gate_one`, cases `positive.json`, `negated.json`, `indeterminate.json` | wrapper result and margin through public execution |
| Definition-typed positive | `tests/fixtures/calcdef_constraint_gate_definition_typed_positive/` | live/snapshot generation and execution; calc-formal actual redirects, direct literal/attribute actuals remain direct |
| Definition-typed mismatch | `tests/fixtures/calcdef_constraint_gate_definition_typed_mismatch/` | CLI `SI_CONSTRAINT_CALC_FORMAL_INVALID` |
| Definition-typed duplicate | `tests/fixtures/calcdef_constraint_gate_definition_typed_duplicate/` | CLI `SI_CONSTRAINT_CALC_FORMAL_INVALID` |
| Definition-typed cross-occurrence | `tests/fixtures/calcdef_constraint_gate_definition_typed_cross_occurrence/` | CLI `SI_CONSTRAINT_CALC_FORMAL_INVALID` |
| Profile BLOCK | `tests/fixtures/calcdef_constraint_gate_blocked/` | CLI `SI_CONSTRAINT_BLOCKED`; absence of package/report |
| Plain, requirement, nonnumerical | `tests/fixtures/calcdef_constraint_gate_excluded/` | N excluded catalog rows, zero executable wrappers/results |
| Invalid owner | mutation `calc_owner_missing_or_malformed` in `test_constraint_attachment_cause.py` | exact owner diagnostic |
| Missing/cross/chained port | mutations in `test_calcdef_constraint_input_ref.py` | graph validation and decode refusal |
| Producer cycle/topology/selection | mutations in `test_elaboration_contract_matrix.py`, plus many fixture | cycle refusal; producer-before-gate; selected producer retained |
| Partial/duplicate/extra expansion | mutations in `test_constraint_usage_domain_totality.py` | graph/preflight refusal with expected/actual IDs |
| v3/unknown/noncanonical/recursive codec | mutations in `test_elaboration_graph_roundtrip.py` and identity vertical test | `SI_SNAPSHOT_INVALID` before projection |
| Missing/duplicate/extra TEAx join | mutations in `simkit/tests/study/test_query.py` and `test_model_contract_skew.py` | package-load/query refusal; no silent filtering |

The producer-backed many fixture deliberately gives the upstream producer a rendered name that would sort after the gate. Passing therefore proves semantic topology, not accidental construction/name order. The same formal is observed by the calculation and gate. Its public assertions combine source identity, no duplicate generated field, producer-before-gate execution, and exact report-to-catalog drill-down.

## Integration and producer-first pins

Known evidence baselines:

- Codegen evidence baseline: `cc14cf07630ed06c7f5cd16bff14cc055709138d`. It is not a lawful Item 6 start pin because Item 8 is absent.
- Agentic-mbse prerequisite: `0a529426f7dfb163a8e03e8a5d3a0cb394d217cf` with profile v4 and expression v1.
- TEAx Item 3 consumer baseline: `5b70ae9231949476139b157ea47b240bdb855641` on `constraint-semantics-item3`.

The exact Item 6 start pin is intentionally unavailable until Item 8 produces a reviewed immutable codegen descendant. Implementation must stop at that gate and record the actual full SHA; no branch name or `cc14cf0…` satisfies it.

Rollout order:

1. Complete and independently certify Item 8 on the codegen line. If its churn assessment fires, Item 8 performs and reviews its required v3 recapture. Freeze its exact reviewed SHA and run its agreement/disagreement and three-route tests.
2. Apply Item 6 graph/elaboration/projection work on that descendant. Freeze graph v4 only after the combined `PortMetadata` shape passes.
3. Perform Item 6's reviewed v4 recapture and all codegen gates. This is a separate recapture if Item 8 already required one. Skipping the earlier pass is lawful only under an explicit epic-owner amendment authorizing joint delivery. Create an immutable codegen producer candidate; record its full SHA only after this baseline passes.
4. From TEAx `5b70ae9…`, regenerate all five existing packages plus the calc-gate many package using that producer candidate. Update catalog 4 load/query behavior and run the TEAx baseline. Record the final TEAx SHA only after it passes.
5. Run codegen public execution acceptance against that exact TEAx SHA and agentic-mbse `0a52942…`.
6. Merge/publish codegen first, then TEAx. Final verification records both immutable SHAs. A consumer that accepts catalog 4.0.0 never leads its producer.

No agentic-mbse change is expected. Evidence that profile v4, expression v1, or Item 8's unit invariant must change is a premise conflict and stops implementation for owner disposition.

## Required invariants

1. One usage record remains the only authored constraint authority.
2. Every calc gate identity contains exactly one unqualified full calculation `NodeId`.
3. `NodeId.sort_key()` is the only occurrence-order oracle.
4. Graph and catalog use the same canonical node encoder/parser.
5. Every `CalculationInputRef` dereferences through one graph law and at most one hop.
6. A producer-backed gate depends on the real producer, not on accidental module construction order.
7. Inline leaves and definition-typed formals use their distinct exact resolution paths.
8. Calculation inputs are sealed before gates are constructed; no post-build fill exists.
9. A nonempty expansion is complete or absent.
10. Item 8 owns unit metadata and any required v3 recapture; Item 6 preserves that metadata and owns calc formal provenance and its later v4 recapture unless an epic-owner amendment explicitly joins the deliveries.
11. Coverage is usage-level; catalog/results are occurrence-level and complete.
12. Report schemas and headline vocabulary remain Item 3's contract.
13. Missing, duplicate, malformed, extra, or out-of-order joins fail closed in codegen and TEAx.

## Non-goals

- Resolving the parked BLOCK denominator/build-halt premise conflict.
- Rendered-name reconstruction.
- A post-build gate fill or second occurrence inventory.
- Requirement-side evaluation.
- Predicate feature-chain support.
- Report-schema or evidence-schema expansion.
- A v3 graph compatibility reader or dual catalog producer.
- Reworking Item 8's unit inference inside Item 6.

## Potential risks

- **Hidden edge visitor:** a code path may inspect `InputRef` without the central helper. Mitigation: import-boundary/grep assertion plus producer topology, selection, cycle, and decode tests.
- **Codec drift:** catalog and graph could serialize identity differently. Mitigation: one encoder, canonical re-encode refusal, and catalog round trip.
- **Metadata churn:** Item 8 may move fixture fingerprints. Mitigation: freeze Item 8 first and perform one combined final v4 recapture.
- **Consumer omission:** TEAx may continue filtering broken joins. Mitigation: ordered population equality at load/query construction and mutation tests.
- **Fixture overfitting:** internal assertions may pass without public behavior. Mitigation: named model fixtures and live/in-place/relocated execution paths.

## Validation approach

Validation proceeds from the smallest contract outward:

1. Identity and dereference unit tests freeze hashability, grammar, sort, and edge semantics.
2. Elaborator tests prove two formal paths, atomic zero/one/many, causes, polarity, and Item 8 metadata preservation.
3. Conformance tests prove cycles, selection, topology, ordered catalog/aggregator agreement, graph v4 refusal, receipts, and the single recapture.
4. Public execution tests prove shared sources, generated field counts, producer order, defaultless supply, failed sibling positions, and drill-down.
5. TEAx tests regenerate the full catalog-affected fixture population and refuse every join skew.
6. Licensed full suites, ruff zero-new, mypy zero-new, snapshot manifest review, and `git diff --check` complete the producer and consumer baselines.

## Parked premise conflict

`[INHERITED: constraint coverage policy Item 3]` An asserted profile-BLOCK usage is described as denominator-visible and unassessed.

`[INHERITED: spec.md; rulings-20260812.md Q5, source grade [AGENT] (ratified by owner, 2026-08-12)]` Profile BLOCK halts package generation, so no runtime report exists.

This design does not choose between them. It implements and tests build halt only. It does not fabricate a report, denominator row, or post-halt evaluation. The broader wording remains parked for its assigned owner/documentation disposition.

## Next-stage handoff

Fixed for implementation:

- one-level qualified identity and exact codec;
- one central input dereference law;
- separate inline and definition-typed resolver paths;
- Item 8 metadata prerequisite and ownership;
- `NodeId.sort_key()` as the sole order;
- one structured generation-plan expected-ID carrier rendered and preflighted from that order;
- graph v4, envelope v6, projector v2, catalog 4.0.0, runtime 2.0.0;
- complete named fixture/mutation matrix;
- producer-first cross-repository order.

Blocked before implementation authorization: the immutable Item 8-containing codegen start SHA does not yet exist in the inspected evidence. Once it exists and the owner authorizes the follow-on, implementation follows `implementation-item.md` and returns to an independent design review/audit gate.
