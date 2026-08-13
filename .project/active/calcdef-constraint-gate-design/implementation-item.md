# Follow-on backlog item: implement calc-definition constraint gates

**Status:** Proposed; blocked on Item 8 and owner authorization

**Type:** Cross-repository implementation

**Depends on:** `spec.md`, revised `design.md`, and Item 8 unit-lane metadata

**Item 6 estimate:** 7–9 working days

**Created:** 2026-08-13

**Revised:** 2026-08-13 after independent design review F1–F8

## Delivery boundary and provenance

`[INHERITED: orchestration stage input]` Implementation is outside the current epic/item delivery unless the owner later authorizes it.

`[INHERITED: epic_constraint_semantics_contract.md Item 6; source grade [AGENT] (ratified by owner, 2026-08-12)]` Item 6's production implementation is a separately authorized follow-on.

This file records the work. It does not authorize production edits, fixture recapture, cross-repository changes, publication, or a commit.

## Objective

`[INHERITED: rulings-20260812.md owner-stated design-search frame]` Make physics constraints support trustworthy design search.

`[INHERITED: spec.md; rulings Q2 and Q5, source grade [AGENT] (ratified by owner, 2026-08-12)]` Expand one calculation-definition constraint usage into one concrete check per matching calculation occurrence while retaining one usage-level coverage member. A failed sibling must remain visible in the complete result population.

`[AGENT]` Implement the revised design with one graph authority: a one-level qualified `NodeId`, one centralized calculation-input dereference law, and two exact constraint-formal resolution paths.

## Current state

- `[INHERITED: probes/findings.md]` Exact zero/one/many definition matching and root-formal recovery are proven for the inline probe while live elaboration indexes exist.
- `[INHERITED: probes/findings.md]` Repeated sibling uses share the current constraint key and therefore collide without full calculation identity.
- `[INHERITED: design-review.md F1]` Producer dependencies, selection, cycles, and decode validation do not yet understand a calculation-port reference.
- `[INHERITED: design-review.md F2]` Current `NodeId` is hashable but not orderable; graph v4 needs a frozen one-level grammar and explicit total key.
- `[INHERITED: design-review.md F3]` Definition-typed constraint formals require the existing constraint-actual resolver before an actual can be redirected to a calculation port.
- `[INHERITED: completed Items 2 and 3]` Graph v3, catalog 3.0.0, usage coverage, occurrence reports, completeness, and worst-state policy are landed.
- `[INHERITED: epic Item 8]` Unit metadata on constraint-formal/computed-attribute ports is a prerequisite seam owned by Item 8.

Calc-definition constraints currently end as `non_reaching / owner_kind_unattachable`. No production gate expansion exists.

## Start gate and exact dependency pins

### Codegen

- Evidence baseline: `cc14cf07630ed06c7f5cd16bff14cc055709138d` on `item7-rebuild`.
- This commit predates Item 8 and is explicitly **not** a lawful Item 6 implementation start pin.
- Before implementation begins, Item 8's kept characterizations and production behavior must exist in one reviewed immutable codegen descendant. Its full SHA must be recorded in the implementation notes. A branch name does not satisfy the gate.
- No such reviewed SHA exists in the evidence inspected on 2026-08-13. Implementation remains blocked until it does.

### Other repositories

- Agentic-mbse prerequisite: `0a529426f7dfb163a8e03e8a5d3a0cb394d217cf`, profile contract v4 and expression contract v1.
- TEAx starting consumer: `5b70ae9231949476139b157ea47b240bdb855641` on `constraint-semantics-item3`.
- TEAx must remain on that compatible unmerged baseline until a codegen catalog 4 producer candidate exists.

### Item 8 ownership gate

- `[INHERITED: epic Item 8; source grade [AGENT] (ratified by owner, 2026-08-13)]` Item 8 owns `PortMetadata.unit`, its A9/radius characterizations, agreement/disagreement tests, and three-route unit parity.
- `[INHERITED: epic Item 8]` Item 8 remains independently certifiable and owns the reviewed v3 recapture if its churn assessment fires.
- `[AGENT]` A separately authorized Item 6 owns calc-input `formal_provenance`, preserves Item 8's unit lane, and owns its later graph-v4 21-fixture recapture.
- `[AGENT]` Avoiding duplicate recapture requires an explicit amendment by the epic's owning authority that authorizes joint delivery and changes the dependency/certification boundaries. Item 6 does not assume that amendment.

The Item 8 verification must give Item 6 the exact paths of these kept tests:

1. constraint formal and calc usage unit agreement;
2. constraint formal and calc usage disagreement refusal;
3. computed attribute and calc usage unit agreement;
4. computed attribute and calc usage disagreement refusal;
5. live/in-place/relocated `PortMetadata` parity.

## Scope and fixed contracts

### One-level qualified identity

- `[AGENT]` Add `attached_calculation: NodeId | None` to frozen `NodeId`.
- `[AGENT]` Permit an attachment only on a constraint with an outer `DeclarationId`.
- `[AGENT]` Require one unqualified calculation ID with the same scope. Maximum depth is one.
- `[AGENT]` Include the attachment in equality and hash behavior.
- `[AGENT]` Require calc-definition constraint nodes to attach and all other constraint owners not to attach.

The exact graph v4 wire contract is fixed:

- unqualified: three-element JSON array `[kind, scope, declaration]`;
- qualified: four-element array `[kind, scope, declaration, attached]`;
- `attached`: structured unqualified calculation array, never a string or null;
- scope/declaration subarrays retain their closed current tags;
- canonical compact JSON comes only from `NodeId.to_wire()`;
- decode requires exact types/arity, constructor invariants, and byte-for-text canonical re-encoding.

`NodeId.sort_key()` is the sole order:

- kind ranks attribute `0`, calculation `1`, constraint `2`;
- occurrence scope `(0, steps)`, package scope `(1, uuid.hex)`;
- occurrence step uses UUID hex plus explicit none/integer tag;
- slot declaration `(0, uuid.hex)`, declaration ID `(1, uuid.hex)`;
- absent attachment `(0,)`, present attachment `(1, nested_sort_key)`.

Raw node comparison, wire-text ordering, rendered-name ordering, and `constraint_id` ordering are forbidden.

### Centralized calculation-input dereference

- `[AGENT]` Add `CalculationInputRef(ConsumerPortId)` to the graph input union and public elaboration exports.
- `[AGENT]` Implement one `InstanceGraph.dereference_input(consumer_id, input_ref)` law.
- `[AGENT]` Require the target port's consumer to equal the gate's attached calculation and to exist in exactly one resolved/unbound calculation input map.
- `[AGENT]` Forbid reference chaining.
- `[AGENT]` Return the originating port plus one terminal state: node, producer, literal, modeled default, or defaultless.

Every edge consumer must call that law:

- graph target validation;
- cycle/dependency inspection;
- target-selection closure;
- typed module topology;
- projection source reuse;
- decoded graph validation;
- semantic edge tests.

A producer terminal adds the real upstream calculation dependency. Literal, attribute, modeled-default, and defaultless terminals do not create an artificial dependency on the matched calculation module. Projection looks up the already-recorded `InputSource` by target calculation port.

The codec shape is exactly `{"kind":"calculation_input","target":<ConsumerPortId data>}` with no extra keys. It never serializes a copied terminal source.

### Two formal-resolution paths

- `[AGENT]` Inline predicate leaves recover an exact root calculation formal through `FeatureSlotIndex` and map directly to that formal's port on each matched calculation.
- `[INHERITED: spec.md definition-typed inference]` Definition-typed constraint formals first use the existing constraint-formal actual resolver.
- `[AGENT]` Only a resolved actual whose semantic referent is a formal on the owning calculation definition redirects to `CalculationInputRef`.
- `[AGENT]` Literal, attribute, producer, and other supported actuals remain their existing typed source.
- `[AGENT]` An omitted constraint formal keeps its constraint-definition default/defaultless law unless the model binds it to a calculation formal.
- `[AGENT]` Mismatch, duplicate, ambiguity, foreign definition, or cross-occurrence identity emits `SI_CONSTRAINT_CALC_FORMAL_INVALID`.

### Attachment, profile, polarity, and atomic expansion

- `[AGENT]` Add exact `owner_definition_id` to calc-definition usage records.
- `[AGENT]` Match `graph.calcs` by exact calculation definition ID and order matches only by `NodeId.sort_key()`.
- `[INHERITED: spec.md]` Support exact zero, one, and many matches, including repeated definitions in one scope.
- `[AGENT]` Build each nonempty usage batch locally and merge only after exact expected/actual set equality, unique IDs, complete formal joins, and same-occurrence input references pass.
- `[INHERITED: rulings Q3]` A valid owner with zero matches is `non_reaching / owner_has_no_occurrences`, warning if asserted and info otherwise.
- `[INHERITED: rulings Q5]` ADMIT expands to N executable gates; BLOCK emits `SI_CONSTRAINT_BLOCKED` and halts package generation; plain/requirement/nonnumerical forms remain occurrence-visible and non-executable.
- `[INHERITED: spec.md]` Preserve polarity on every occurrence and apply it once in existing wrapper finalization.

Add cause codes:

- `SI_CONSTRAINT_CALC_OWNER_INVALID`;
- `SI_CONSTRAINT_CALC_FORMAL_INVALID`;
- `SI_CONSTRAINT_CALC_EXPANSION_INVALID`.

Messages carry usage ID plus calculation/formal IDs where applicable. Structural failures do not masquerade as reachability dispositions.

### Ordered catalog, reports, and TEAx joins

- `[AGENT]` Define eligible gate sequence `G = sorted(gates, key=node_id.sort_key)` once.
- `[AGENT]` Emit wrappers, eligible catalog rows, aggregator channels, and `EXPECTED_IDS` from `G` without another sort.
- `[AGENT]` In `generation/modules.py`, materialize one ordered expected-ID tuple from those aggregator inputs. Use that same tuple to render `EXPECTED_IDS` and to populate `ConstraintGenerationPlan.expected_constraint_ids: tuple[str, ...]` in `generation/constraint_plan.py`.
- `[AGENT]` Order excluded occurrence rows by the same node key.
- `[AGENT]` Add canonical `calculation_node_id` to eligible and excluded catalog occurrence rows and bump catalog to 4.0.0.
- `[INHERITED: Item 3]` Keep usage coverage one-per-authored usage; produce exactly N occurrence results; preserve report schemas and worst-state vocabulary.
- `[AGENT]` Compare the structured plan carrier with ordered graph, catalog, wrapper, and aggregator identities at CLI preflight before any output-tree mutation. Do not parse rendered source or freshly rederive the carrier.
- `[AGENT]` Make TEAx preserve the sealed eligible catalog sequence and require exact ordered equality with report result IDs.
- `[AGENT]` Delete silent `_case_view` filtering. Missing, duplicate, malformed, extra, or out-of-order joins fail at load/query construction.

### Version and sealing decisions

- Embedded graph `instance-graph/v3` → `instance-graph/v4`.
- Outer snapshot envelope remains `6`.
- Projector semantics `instance-projector/v1` → `instance-projector/v2`.
- Catalog `3.0.0` → `4.0.0`.
- Runtime/report contract remains `2.0.0`.
- Evidence schema remains unchanged.
- Graph v3, unknown versions, noncanonical identities, missing fields, and malformed references refuse before projection. No compatibility shim is retained.
- Receipt, catalog/model-contract fingerprint, and executable seal must move through existing sealing fields.

## Out of scope

- `[INHERITED: spec.md; Item 3; rulings Q5]` Resolving the parked BLOCK denominator/build-halt premise conflict.
- `[INHERITED: spec.md]` Rendered-name reconstruction, post-build fill, or a second occurrence inventory.
- `[INHERITED: Item 3 report contract]` Report/evidence schema expansion.
- `[INHERITED: spec.md]` Requirement-side evaluation or predicate feature-chain work.
- `[AGENT]` Reimplementing Item 8's unit inference in Item 6.
- `[AGENT]` A v3 graph reader, dual catalog producer, or TEAx compatibility path that silently accepts both 3.0.0 and 4.0.0.
- `[AGENT]` Agentic-mbse profile/expression changes without a separately surfaced premise conflict and authorization.

## File-level deliverables

### sysml-codegen production

- `src/sysml_codegen/elaboration/identity.py`: one-level identity, exact codec helpers, total `sort_key()`.
- `src/sysml_codegen/elaboration/diagnostics.py`: new diagnostic enum values.
- `src/sysml_codegen/elaboration/graph.py`: `CalculationInputRef`, dereference law, usage/edge/expansion/cycle invariants.
- `src/sysml_codegen/elaboration/__init__.py`: export the new input vocabulary.
- `src/sysml_codegen/elaboration/elaborate.py`: calculation-input sealing, Item 8 metadata preservation, two formal paths, exact attachment, atomic batches.
- `src/sysml_codegen/elaboration/project.py`: calculation-port source cache, dereferenced selection/topology, sole ordered sequence, catalog identity.
- `src/sysml_codegen/snapshot/instance_graph.py`: graph v4 identity/edge/usage codec and exact refusal.
- `src/sysml_codegen/contracts/versions.py`: catalog 4.0.0.
- `src/sysml_codegen/resolution/models.py`: required-nullable calculation identity on eligible/excluded rows.
- `src/sysml_codegen/generation/modules.py`: derive one expected-ID tuple from ordered aggregator inputs, render it, and hand the same tuple to the plan.
- `src/sysml_codegen/generation/constraint_plan.py`: add structured ordered `expected_constraint_ids` to the generation plan.
- `src/sysml_codegen/cli/__init__.py`: ordered totality and join preflight.

Inspect and update tests for these sealing/version surfaces; production fields should remain unchanged unless implementation evidence contradicts the design:

- `src/sysml_codegen/snapshot/envelope.py`
- `src/sysml_codegen/orchestration/exact_pipeline_context.py`
- `src/sysml_codegen/contracts/model_contract.py`
- `src/sysml_codegen/contracts/seal.py`
- `src/sysml_codegen/templates/constraint_types.py.jinja2`
- `src/sysml_codegen/templates/report_aggregator.py.jinja2`

### sysml-codegen tests and fixture migrations

- `tests/unit/test_calcdef_constraint_gate_identity.py` (new): hash/map, cross-scope sort, ports/maps, recursion/malformed decode, canonical re-encode, catalog round trip.
- `tests/unit/test_calcdef_constraint_input_ref.py` (new): all terminal categories plus missing, chained, and cross-occurrence references.
- `tests/unit/test_constraint_attachment_cause.py`: zero/one/many and dispositions.
- `tests/conformance/test_elaboration_identity_vertical.py`: v4 identity/port vertical.
- `tests/conformance/test_elaboration_contract_matrix.py`: dereferenced cycles/dependencies and dangling refusal.
- `tests/conformance/test_elaboration_projection_one_way.py`: producer-backed topology and projection-only rendering.
- `tests/conformance/test_exact_target_selection.py`: producer/attribute selection closure.
- `tests/conformance/test_constraint_usage_domain_codec.py`: usage and calculation-input v4 codec.
- `tests/conformance/test_elaboration_graph_roundtrip.py`: graph v4 pin and fail-closed old/unknown/malformed shapes.
- `tests/conformance/test_constraint_usage_domain_totality.py`: exact derived sets and atomicity.
- `tests/conformance/test_constraint_catalog_totality.py`: ordered catalog 4 identity and mutation refusal.
- `tests/conformance/test_constraint_generation_plan_totality.py` (new): keep `test_expected_constraint_id_carrier_disagreement_refuses_before_write`; mutate missing, duplicate, extra, and reordered IDs and prove refusal before output mutation.
- `tests/conformance/test_exact_pipeline_context.py`: projector v2 receipt and mismatch.
- `tests/conformance/test_catalog_schema_version.py`: catalog 4 pin.
- `tests/conformance/test_runtime_contract_version.py`: runtime 2 plus catalog 4.
- `tests/conformance/test_snapshot_v6_routes.py`: envelope v6 / graph v4 live, in-place, relocated parity.
- `tests/conformance/test_exact_route_constraint_portability.py`: portable receipt/catalog/package/results.
- `tests/conformance/test_v6_recapture_batch.py`
- `tests/fixtures/v6_recapture_batch/batch.json`
- `tests/fixtures/v6_recapture_batch/README.md`
  - Own Item 6's reviewed graph-v4 recapture. Item 8 separately owns a v3 recapture if its churn fires, absent an explicit epic-owner joint-delivery amendment.
- `tests/execution/test_calcdef_constraint_gate.py` (new): all public calc-gate cases, including `test_many_renders_expected_ids_in_node_sort_order`, which imports the generated aggregator and compares its rendered tuple with ordered public catalog IDs.
- `tests/execution/test_constraint_verdicts_exact_route.py`: Item 3 completeness/worst-state regression.

New public fixture directories:

- `tests/fixtures/calcdef_constraint_gate_zero/`
- `tests/fixtures/calcdef_constraint_gate_one/`
- `tests/fixtures/calcdef_constraint_gate_many/`
- `tests/fixtures/calcdef_constraint_gate_definition_typed_positive/`
- `tests/fixtures/calcdef_constraint_gate_definition_typed_mismatch/`
- `tests/fixtures/calcdef_constraint_gate_definition_typed_duplicate/`
- `tests/fixtures/calcdef_constraint_gate_definition_typed_cross_occurrence/`
- `tests/fixtures/calcdef_constraint_gate_blocked/`
- `tests/fixtures/calcdef_constraint_gate_excluded/`

Promote from `.project/active/calcdef-constraint-gate-design/probes/models/`; no test reads active-project probe files.

### Documentation

- `CLAUDE.md`
- `docs/architecture/modeling-assumptions.md`
- `docs/architecture/verification-matrix.md`
- `docs/architecture/reference/27-snapshot-generation.md`
- `docs/architecture/reference/29-contracts-and-sealing.md`

### TEAx production, tests, and fixture migrations

Production:

- `packages/teax-simkit/simkit/evaluation/package_load.py`
- `packages/teax-simkit/simkit/study/model_contract.py`
- `packages/teax-simkit/simkit/study/query.py`

Tests:

- `packages/teax-simkit/simkit/tests/evaluation/test_package_load.py`
- `packages/teax-simkit/simkit/tests/evaluation/test_package_trust.py`
- `packages/teax-simkit/simkit/tests/evaluation/test_projection.py`
- `packages/teax-simkit/simkit/tests/study/test_model_contract_skew.py`
- `packages/teax-simkit/simkit/tests/study/test_query.py`
- `packages/teax-simkit/simkit/tests/study/test_no_reconstruction.py`
- `packages/teax-simkit/simkit/tests/study/test_compatibility.py`
- `packages/teax-simkit/simkit/tests/study/test_partial_coverage_policy.py`
- `packages/teax-simkit/simkit/tests/study/test_calcdef_constraint_catalog.py` (new)

Regenerate these five existing catalog-bearing packages from the final codegen candidate:

- `simkit/tests/evaluation/fixtures/constraint_free/package_live/`
- `simkit/tests/evaluation/fixtures/excluded_only/package_live/`
- `simkit/tests/evaluation/fixtures/zero_channel/package_live/`
- `simkit/tests/evaluation/fixtures/sealed_package/package_live/`
- `simkit/tests/evaluation/fixtures/f1_arithmetic/package_live/`

Add generated cross-repository fixture:

- `simkit/tests/evaluation/fixtures/calcdef_constraint_gate_many/package_live/`

Every generated contract records the final codegen producer SHA. Do not hand-author a catalog-only substitute.

## Public acceptance matrix

| Behavior/source/failure | Fixture or named mutation | Public assertion |
|---|---|---|
| Zero | `calcdef_constraint_gate_zero` | one usage, count 0, cause/severity, no occurrence/result |
| One inline gate | `calcdef_constraint_gate_one` | one unique gate/catalog/result join |
| Literal actual | `calcdef_constraint_gate_one` | same source ID, one field, correct result |
| Design attribute | `calcdef_constraint_gate_one` | same node source, selected dependency, drill-down |
| Modeled default | `calcdef_constraint_gate_one` | one defaulted public entry shared by calc/gate |
| Defaultless formal | `calcdef_constraint_gate_one/defaultless_supplied.json` | one required public field supplied and shared |
| Producer-backed same formal | `calcdef_constraint_gate_many` | same channel, zero duplicate fields, producer ordered before gate |
| Repeated definitions | `calcdef_constraint_gate_many` | N unique qualified IDs and N results in `sort_key()` order |
| Failed sibling positions | `many/fail_first.json`, `fail_middle.json`, `fail_last.json` | complete ordered results and violation headline each time |
| Positive/negative/indeterminate | `one/positive.json`, `negated.json`, `indeterminate.json` | polarity and margin applied once |
| Definition-typed positive | `calcdef_constraint_gate_definition_typed_positive` | calc-formal redirect plus direct literal/attribute actuals |
| Definition mismatch | `..._definition_typed_mismatch` | exact formal diagnostic |
| Definition duplicate | `..._definition_typed_duplicate` | exact formal diagnostic |
| Definition cross-occurrence | `..._definition_typed_cross_occurrence` | exact formal diagnostic |
| BLOCK | `calcdef_constraint_gate_blocked` | named halt, no package/report, no denominator assertion |
| Plain/requirement/nonnumerical | `calcdef_constraint_gate_excluded` | N excluded rows, no executable result |
| Invalid owner | `calc_owner_missing_or_malformed` mutation | owner diagnostic and nonprojectable graph |
| Missing/cross/chained calc port | `test_calcdef_constraint_input_ref.py` mutations | validation/decode refusal |
| Producer cycle | `test_elaboration_contract_matrix.py` mutation | cycle refusal through dereference law |
| Selection closure | many fixture targeted generation | real producer remains selected |
| Partial/duplicate/extra expansion | usage-totality mutations | exact expected/actual refusal, zero partial batch |
| v3/unknown/noncanonical/recursive ID | graph-roundtrip/identity mutations | snapshot refusal before projection |
| TEAx missing/duplicate/extra/out-of-order join | query/model-skew mutations | load/query refusal, never silent omission |
| Generation-plan expected-ID disagreement | `test_expected_constraint_id_carrier_disagreement_refuses_before_write` | CLI refuses missing/duplicate/extra/reordered carrier before output mutation |
| Public rendered expected tuple | `test_many_renders_expected_ids_in_node_sort_order` | generated aggregator `EXPECTED_IDS` exactly equals ordered catalog IDs |
| Live/in-place/relocated | one, many, definition-positive | same IDs, metadata, receipts, catalog, seals, reports |

For the producer-backed and defaultless cases, acceptance combines source identity, generated field count, execution order, and report drill-down in the same public test. Internal graph assertions alone do not satisfy them.

## Success criteria

- `[INHERITED: spec.md]` Exact zero/one/many expansion works for repeated definitions without collision or partial batches.
- `[AGENT]` Qualified IDs pass frozen grammar, acyclicity, hash/map, port, canonical-codec, and total-order tests.
- `[AGENT]` Every edge consumer uses the centralized dereference law; producer topology, cycle, and selection tests prove it.
- `[INHERITED: spec.md]` Inline and definition-typed formals follow their exact distinct resolver paths.
- `[INHERITED: spec.md]` Explicit, defaulted, and defaultless calculation sources are shared without a gate-local duplicate.
- `[INHERITED: epic Item 8]` Unit metadata agreement/refusal remains Item 8's behavior on all three routes; Item 6 preserves it.
- `[INHERITED: Items 2 and 3]` Coverage remains usage-level, results remain complete occurrence-level, and worst state exposes any failed sibling.
- `[AGENT]` Graph, catalog, wrappers, aggregator, expected IDs, results, and TEAx joins agree in `NodeId.sort_key()`-derived order.
- `[INHERITED: Item 3]` `ConstraintEvaluation`, `ConstraintReport`, evidence schema, and headline vocabulary do not change.
- `[AGENT]` Graph v4, projector v2, catalog 4.0.0, receipts, model fingerprints, executable seals, and final producer/consumer SHAs agree.
- `[INHERITED: spec.md; Item 3; rulings Q5]` The BLOCK premise conflict remains parked; only build halt is tested.

## Phased implementation outline

### Phase 0: prerequisite gate

- Complete or consume Item 8's kept tests and production behavior.
- If Item 8's churn assessment fires, let Item 8 perform and certify its own v3 recapture.
- Record the exact reviewed codegen descendant SHA.
- Treat a joint delivery that avoids the later duplicate recapture as unavailable unless the epic owner explicitly amends the dependency and certification contract.

Exit: combined `PortMetadata` behavior is frozen; Item 6 is authorized; no unresolved start pin remains.

### Phase 1: identity and central edge law

- Implement one-level `NodeId`, exact codec helpers, and `sort_key()`.
- Implement/export `CalculationInputRef` and centralized dereference.
- Add hash/map/port/codec/dereference/cycle/selection/topology tests before elaborator expansion.

Exit: malformed identities and references fail, and producer-backed dependencies are semantic rather than accidental.

### Phase 2: elaboration and formal paths

- Seal calculation inputs with Item 8 units and Item 6 formal provenance.
- Implement inline mapping and definition-typed existing-resolver redirection.
- Implement exact owner matching, zero/one/many atomic batches, causes, profile, and polarity.

Exit: complete live graphs cover all named source/formal fixtures with no post-build fill.

### Phase 3: projection, catalog, and ordered totality

- Reuse calculation-port sources.
- Derive all occurrence artifacts from one `sort_key()` sequence.
- Carry the renderer's exact ordered expected-ID tuple in `ConstraintGenerationPlan` and fail preflight disagreement before output mutation.
- Emit catalog 4.0.0 and strengthen ordered preflight.
- Prove N results, failed positions, unchanged report schema, receipts, and seals.

Exit: live packages have exact ordered drill-down and no duplicate sources.

### Phase 4: graph v4 and Item 6 recapture

- Freeze graph v4 and projector v2.
- Recapture the 21-fixture batch at graph v4 under Item 6 ownership. This may follow Item 8's independently required v3 recapture; avoiding that second pass requires explicit epic-owner joint-delivery authorization.
- Run live, in-place, relocated, version refusal, docs, and full codegen gates.
- Create the immutable codegen producer candidate only after the baseline passes.

Exit: producer candidate and reviewed recapture are fixed.

### Phase 5: TEAx consumer and publication

- Update TEAx from exact baseline `5b70ae9…`.
- Regenerate all five existing packages and add the calc-gate package from the producer candidate.
- Enforce catalog 4.0.0 and exact ordered fail-closed joins.
- Run TEAx and cross-repository execution baselines.
- Record final full producer and consumer SHAs after they pass.
- Merge/publish codegen first, TEAx second; run `$my-audit` before close.

Exit: every public acceptance row passes at immutable pins.

## Effort and risk

Item 6 estimate: **7–9 working days**, excluding Item 8's separately estimated 0.5–1 day prerequisite.

- identity, dereference, and graph tests: 1.5–2 days;
- elaboration and definition-typed fixtures: 2–2.5 days;
- ordered projection/catalog/sealing: 1.5 days;
- graph v4 recapture/routes/docs: 1–1.5 days;
- TEAx regeneration, fail-closed joins, and cross-repository gates: 1–1.5 days.

The primary risk is missing an edge consumer and allowing producer-backed behavior to depend on incidental order. The central helper plus a deliberately adverse producer name makes that defect observable.

## Parked premise conflict

- `[INHERITED: constraint coverage policy Item 3]` An asserted profile-BLOCK usage is described as denominator-visible and unassessed.
- `[INHERITED: spec.md; rulings Q5, source grade [AGENT] (ratified by owner, 2026-08-12)]` Profile BLOCK halts package generation, so no runtime report exists.

Implementation preserves both as a parked conflict. It tests build halt and creates no denominator/report artifact after halt.

## Required reading

1. `.project/active/calcdef-constraint-gate-design/spec.md`
2. `.project/active/calcdef-constraint-gate-design/design.md`
3. `.project/active/calcdef-constraint-gate-design/design-review.md`, F1–F8
4. `.project/active/calcdef-constraint-gate-design/probes/findings.md`
5. `.project/active/calcdef-constraint-gate-design/probes/models/`
6. `.project/backlog/epic_constraint_semantics_contract.md`, Items 6 and 8
7. Item 8's final design/verification and exact kept-test paths once filed
8. `.project/active/constraint-semantics-contract/rulings-20260812.md`, Q2, Q3, Q5
9. `.project/completed/20260813_constraint-catalog-totality/design.md` and landed code
10. `.project/completed/20260813_constraint-coverage-policy/design.md` and landed code
11. `.project/backlog/epic_elaborate_first_architecture.md`
12. `CLAUDE.md` and repository `AGENTS.md` rules
13. TEAx consumer at `5b70ae9231949476139b157ea47b240bdb855641`
14. Agentic-mbse contracts at `0a529426f7dfb163a8e03e8a5d3a0cb394d217cf`
