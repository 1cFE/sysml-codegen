# Implementation Plan: Exact-Identity Completion (ELABORATE-FIRST Item 6)

- **Status:** Implementation Complete — audit_v3 findings remediated 2026-08-10; independent
  re-audit pending.
- **Created:** 2026-08-09
- **Owner:** Reid W
- **Branch:** `source-identity-epic`
- **Coordinated repository:** `../agentic-mbse`

## Source Documents

- **Spec:** `spec.md`
- **Item design authority map:** `design.md`
- **Product-lens ledger:** `product-lens.md` — CLEAR
- **Normative shared design:** `../elaborator-design/design.md`
- **Normative shared spec:** `../elaborator-design/spec.md`
- **Epic Item 6:** `../../backlog/epic_elaborate_first_architecture.md`
- **Gap census:**
  `../../research/20260809-153245_item6-identity-completion-and-cutover-census.md`
- **Occurrence-boundary spike:** `../spike-syside-occurrence-authority/findings.md`
- **Item-5 certification:** `../../completed/20260809_elaborator-breadth/audit_v3.md`
- **Item-5 corpus ledger:** `../../completed/20260809_elaborator-breadth/diff-ledger.md`

## The Point

SysIDE has already resolved which semantic declaration a reference denotes. The new route must
carry that exact identity through executable payload, concrete occurrence context, validated graph,
and public projection. A name, QN, rendered path, or iteration order may describe an element after
resolution. It may not select the element or reconstruct its relationships.

Item 5 proved exact consumer edges across the supported breadth. Item 6 closes the remaining places
where executable data still attaches by QN/member name, occurrence declarations are reconstructed,
or projection parses its own strings. The legacy route remains shipped and snapshot v5 remains
byte-identical. Item 7 owns the authority switch, new shipped envelope, recapture, deletion, and
final live/relocated-snapshot cutover proof.

## Implementation Strategy

### Phasing rationale

The work follows the identity pipeline in the order data enters it. Calculation payload is first
because it supplies exact definitions, formals, outputs, and compiled expressions to every later
phase. Constraint profile identity is next because it crosses the repository boundary and currently
contains the most consequential silent default. Native effective-child declarations then replace
the last reconstructed occurrence input. With those upstream contracts exact, the graph can become
structurally complete and projection can become one-way. The final phase expands the guard and
certifies the whole item against the inherited matrix and corpus.

Each phase is independently reviewable. None switches shipped authority.

### Critical path

```text
exact calc definition/formal/output payload
    -> exact constraint usage/definition/decision payload
    -> SysIDE effective children + codegen concrete occurrence expansion
    -> structured occurrences + typed IR + one-way projection
    -> full guard + 29-cell/37-fixture/public-mutation implementation evidence
    -> independent audit
    -> Item 7 cutover may begin
```

### First proof point

Construct two calculation definitions and members that collide by normalized display name, reverse
their enumeration, and attach distinct output metadata and compilation results. The new route must
select the definition, formal, output, metadata, and compiled expression by exact declaration ID.
Removing one required ID must produce a named blocking diagnostic instead of `UNKNOWN`, `float`, or
null metadata.

### Test-first evidence rule

Every phase starts with the named test stencil and a focused red run before production edits. Record
the red command/result and the later green command/result in that phase's Implementation Notes. A
test committed with already-green production code does not prove the red-first step.

### Scope boundary

- **Included:** exact calculation and constraint payload associations, the native-declaration /
  concrete-occurrence boundary, F31 disposition, structured occurrence and IR graph payload,
  one-way projection, F30 guard expansion, and Item-6 certification.
- **Excluded:** changing `build_pipeline_context`, changing the shipped snapshot envelope,
  recapturing extraction snapshots, deleting legacy code, removing dual-run machinery, or changing
  generated public names. Those are Item 7 or a separate owner-approved design.

### Progress

- [x] Phase 1 — Exact calculation payload and compilation identity
- [x] Phase 2 — Exact constraint profile identity across repositories
- [x] Phase 3 — Effective declarations and concrete occurrence authority
- [x] Phase 4 — Structured graph and one-way projection
- [x] Phase 5 — Boundary guard and certification

## Environment Setup

- [x] Confirm both repositories are on their coordinated implementation branches and record base
  commits with `git status --short --branch` and `git rev-parse HEAD`.
- [x] Confirm codegen resolves the editable `../agentic-mbse` checkout and both environments remain
  pinned to SysIDE 0.8.4. Do not accept unrelated lockfile churn.
- [x] Load the existing licensed-test environment. A licensed focused run is valid only when it
  collects the intended tests and prints zero `no live syside license` skip lines.
- [x] Record fresh pre-change full-suite, ruff, mypy, 29-cell, 37-fixture, legacy-freeze, and v5
  snapshot-byte baselines. Prior Item-5 counts are context, not the acceptance count for this item.
- [x] Keep a coordinated implementation note for both repository commits. Do not present only one
  side of the constraint API change as usable.

---

## Phase 1 — Exact Calculation Payload and Compilation Identity

### Goal

Carry exact raw SysIDE UUIDs from calculation-definition extraction through definition/formal/output
metadata and compilation. Build every new-route calculation node from ID-keyed data. Preserve the
legacy name-keyed extraction and compilation surfaces solely for the frozen shipped route.

### Assumption under test

While the live AST is available, codegen can capture stable declaration UUIDs for calculation
definitions and their executable members. Those UUIDs are sufficient to associate ASTs, compilation
results, port metadata, and graph output ports without definition QNs or member names.

### Test stencil — write this first

```python
def test_calc_payload_attachment_is_exact_and_total():
    extracted = extract_collision_probe(reverse_members=True)
    graph = elaborate(extracted.model, extracted.calc_defs)
    calc = graph.calcs[expected_calc_node_id()]
    assert calc.declaration_id == expected_calc_declaration_id()
    assert set(calc.outputs) == {expected_output_declaration_id()}
    assert calc.output_metadata[expected_output_declaration_id()].unit == "MW"
    assert calc.compilation.definition_id == expected_calc_declaration_id()
    assert_no_semantic_lookup_by_name_or_qn(graph)
```

### Changes required

**Design references:** [item choices](design.md#item-local-implementation-choices), shared design
[D1](../elaborator-design/design.md#d1--declaration-identity-is-syside-element_id),
[D7](../elaborator-design/design.md#d7--graph-edges-use-consumer-port-and-target-identity), and
[D10](../elaborator-design/design.md#d10--unsupported-identity-fails-closed-through-a-fixed-diagnostic-catalog).

- [x] **Tests first:** create `tests/conformance/test_elaboration_payload_identity.py`. Cover two
  definitions with colliding normalized names, same-named members, reversed declaration/member
  order, exact output/formal metadata, exact compiled expressions, and missing/conflicting ID
  outcomes. Include one change that edits display metadata only and leaves the synthetic exact IDs
  fixed.
- [x] **Extraction unit pins:** extend `tests/unit/test_extractor.py`,
  `tests/conformance/test_extractor.py`, and `tests/conformance/test_return_style_extraction.py` to
  require a live UUID for each supported calculation definition, formal, output, and intermediate
  member. Pin the raw UUID boundary and prove anonymous/unstable executable members fail closed.
- [x] **Additive live identity sidecars:** update
  `src/sysml_codegen/extraction/data_models.py` and `extractor.py`. Add optional raw-UUID fields and
  exact-ID AST/member maps beside the existing name-keyed fields. Live extraction must populate
  every required exact field. Snapshot-v5 loading may construct the optional fields as absent
  because Item 6 never routes those legacy records into exact elaboration.
- [x] **Exact compiler surface:** update
  `src/sysml_codegen/extraction/expression_compiler.py` so its internal dependency walk is keyed by
  member/output UUID. Return an exact result containing the calculation-definition UUID, exact
  output UUIDs, exact dependency UUIDs, compilability, and rendered expression metadata. Keep
  `compile_calc_def()` as the frozen legacy adapter; the new route must call an explicitly exact
  entry point and may not convert its result back to names for lookup.
- [x] **Exact elaborator indexes:** replace the QN-keyed calculation-definition and compilation
  maps in `src/sysml_codegen/elaboration/elaborate.py` with `DeclarationId` maps. Attach
  `ConsumerPortId` and `OutputPortId` metadata by the exact formal/output declaration. A missing
  required metadata or compilation association becomes a blocking D10 diagnostic; remove the
  new-route `UNKNOWN`, default-`float`, and null-metadata fallbacks.
- [x] **Graph totality:** update `src/sysml_codegen/elaboration/graph.py` validation so every
  declared calculation input/output has one name record, one explicit metadata record, and the
  expected compilation/IR state. Duplicate conflicting records and associations to absent ports
  fail before projection.
- [x] **Legacy byte freeze:** update `src/sysml_codegen/snapshot/serializer.py` only to explicitly
  exclude new live-only identity/AST sidecars. Keep the v5 loader defaults and committed extraction
  snapshots unchanged. Do not add the new fields to snapshot v5.
- [x] **Focused compiler coverage:** extend `tests/unit/test_expression_compiler.py` and
  `tests/conformance/test_expression_compiler.py` with exact-ID dependency/output cases, including
  an undeclared intermediate and two rendered-name collisions. Existing legacy compiler tests must
  remain unchanged in behavior.

### Validation

**Automated:**

- [x] `uv run pytest tests/conformance/test_elaboration_payload_identity.py tests/unit/test_extractor.py tests/unit/test_expression_compiler.py tests/conformance/test_expression_compiler.py -q`
- [x] `uv run pytest tests/conformance/test_extraction_snapshots.py tests/conformance/test_snapshot_v5_gate.py tests/conformance/test_legacy_snapshot_closure.py -q`
- [x] Compare the committed v5 snapshot files and legacy generated-output baseline to the recorded
  pre-change hashes; zero bytes change.
- [x] `uv run ruff check src/sysml_codegen/extraction src/sysml_codegen/elaboration tests/unit/test_extractor.py tests/unit/test_expression_compiler.py tests/conformance/test_elaboration_payload_identity.py`
- [x] `uv run mypy src/` with no new error in a changed new-route file.

**Manual:**

- [x] Inspect one exact compiler result and graph node. UUIDs key definition, formals, outputs,
  dependencies, and metadata; names/QNs occur only as display/template metadata.
- [x] Search the Phase-1 new-route diff for `qualified_name` or member-name dict access and account
  for every hit as rendering, diagnostics, or the frozen legacy adapter.

**What we know works after this phase:** Calculation executable payload is exact and total. Display
collisions or enumeration changes cannot swap compilation or port metadata, and absent identity
cannot become a usable default.

---

## Phase 2 — Exact Constraint Profile Identity Across Repositories

### Goal

Preserve exact constraint usage and effective-definition identity through extraction, profile
evaluation, and codegen graph attachment without changing the neutral fact schema. Remove the
new-route QN join and the missing-decision-to-`ADMIT` fallback.

### Assumption under test

The extraction pass can associate each live constraint usage with its exact UUID and exact effective
definition UUID before neutralizing facts. The existing profile can evaluate the same neutral
predicate when that exact association is supplied directly.

### Test stencil — write this first

```python
def test_identified_profile_returns_one_exact_decision_per_usage():
    identified = extract_identified_constraint_facts(collision_model())
    result = evaluate_identified_profile(identified, reverse_order=True)
    assert {item.usage_id for item in result.decisions} == expected_usage_ids()
    decision = result.by_usage_id[blocked_usage_id()]
    assert decision.effective_definition_id == expected_definition_id()
    assert decision.decision.eligibility is Eligibility.BLOCK
    assert admitted_usage_id() not in result.missing_usage_ids
```

### Changes required

**Design references:** [item choices](design.md#item-local-implementation-choices), shared design
[D1](../elaborator-design/design.md#d1--declaration-identity-is-syside-element_id),
[D7](../elaborator-design/design.md#d7--graph-edges-use-consumer-port-and-target-identity), and the
[repository boundary](../elaborator-design/design.md#component-overview).

- [x] **Agentic tests first:** extend
  `../agentic-mbse/tests/test_sysml/test_constraint_extraction_ordering.py` and
  `test_executable_profile.py`. Cover duplicate/absent QNs, anonymous usage, reversed extraction
  order, exact reused-definition selection, and all four `Eligibility` values. Prove each extracted
  supported usage receives exactly one decision with the same usage UUID.
- [x] **Live wrapper, neutral facts unchanged:** in
  `../agentic-mbse/src/agentic_mbse/sysml/constraint_extraction.py`, add ID-bearing live wrapper
  records around `ConstraintUsageFact` and `ConstraintDefinitionFact`. Each usage record carries its
  validated UUID and the exact reused-definition UUID when that form has one. Keep
  `IdentityFact`, `ConstraintFacts`, golden neutral JSON, and their serializers unchanged.
- [x] **Exact evaluator entry point:** refactor
  `../agentic-mbse/src/agentic_mbse/sysml/executable_profile.py` so the core evaluates a usage
  against an already-selected definition. Add an identified entry point/result that indexes
  decisions by exact usage UUID. Preserve the current neutral `evaluate_profile()` behavior for
  existing callers, but the codegen exact route may not call its QN-based definition adapter.
- [x] **Adapter-only UUID access:** use `SysideAdapter.element_id()` in agentic extraction and do not
  let neutral facts or codegen reach into `element.element_id`. Add an import/API boundary test if
  the existing SysIDE identity-contract test does not already hold this line.
- [x] **Codegen exact attachment:** update `src/sysml_codegen/elaboration/elaborate.py` to consume
  the identified profile. Wrap raw UUIDs once as `DeclarationId`, attach a decision to the exact
  `ConstraintNode`, and reject zero, duplicate, or unrecognized decisions. Delete the new-route
  QN-keyed decision map and the `decision is None -> Eligibility.ADMIT` behavior.
- [x] **Closed graph state:** change `ConstraintNode.eligibility` in
  `src/sysml_codegen/elaboration/graph.py` from an open string/default to the closed `Eligibility`
  enum with no implicit `ADMIT`. Retain the typed `ExpressionIR` decision object for Phase 4 rather
  than serializing it early.
- [x] **Cross-repository conformance:** extend
  `tests/conformance/test_elaboration_payload_identity.py` with exact constraint usage/definition
  cases. Assert BLOCK, UNASSESSED, NON_NUMERICAL, and ADMIT survive graph construction without
  selection by QN or order.

### Validation

**Automated:**

- [x] From `../agentic-mbse`:
  `uv run pytest tests/test_sysml/test_constraint_extraction.py tests/test_sysml/test_constraint_extraction_ordering.py tests/test_sysml/test_executable_profile.py -q`
- [x] From codegen:
  `uv run pytest tests/conformance/test_elaboration_payload_identity.py tests/conformance/test_constraint_snapshot_identity.py tests/conformance/test_elaboration_model_validation.py -q`
- [x] Run agentic neutral-fact serialization/golden tests and prove their bytes and field inventory
  are unchanged.
- [x] `uv run ruff check src tests` and `uv run mypy src/` in both repositories; record the existing
  baseline separately from any changed-file error.
- [x] `git diff --check` in both repositories.

**Manual:**

- [x] Trace one definition-typed constraint from live usage UUID through selected definition UUID,
  profile decision, graph node, and typed consumer ports. No step uses the QN as a key.
- [x] Review the coordinated diff as one API unit. The agentic wrapper is live-only and the neutral
  serialized contract remains parser-independent.

**What we know works after this phase:** Every supported live constraint usage has exactly one
exactly associated profile decision. Missing association blocks instead of admitting execution, and
the neutral constraint-fact contract stays unchanged.

---

## Phase 3 — Effective Declarations and Concrete Occurrence Authority

### Goal

Make SysIDE's `Usage.usages` the sole authority for effective child declarations while codegen
retains only finite concrete expansion and contextual occurrence identity. Remove traversal-order
fallbacks and close audit-F31 with a kept valid-model disposition.

### Assumption under test

On supported SysIDE 0.8.4, `Usage.usages` supplies the correct inherited, retyped, explicitly
redefined, and implied effective child declaration set. Codegen can expand that set into exact
parent/index contexts without global owner/type closure or name grouping.

### Test stencil — write this first

```python
def test_native_children_feed_exact_concrete_occurrences():
    index = build_occurrences(load_plural_retype_fixture(reverse_order=True))
    parent = index.record(parent_occurrence_id())
    assert parent.child_declarations == expected_usage_declaration_ids()
    assert index.children(parent.id) == expected_indexed_occurrence_ids()
    assert index.record(child_occurrence_id(1)).parent == parent.id
    assert no_global_owner_or_name_selection(index)
```

### Changes required

**Design references:** shared design
[D3](../elaborator-design/design.md#d3--the-new-front-end-owns-a-clean-exact-id-occurrence-walker),
[exact contextualization](../elaborator-design/design.md#exact-contextualization-rules), and the
[boundary spike](../spike-syside-occurrence-authority/findings.md).

- [x] **Learning fixture first:** add one minimal fixture under `tests/fixtures/` that combines
  inherited children, a retype, explicit/implied redefinition, finite multiplicity, a same-named
  shadow outside the permitted scope, and the plural shape needed to exercise the two F31 branches.
  Add its `PROVENANCE.md` with the owner/research referents and the exact behavior each assertion
  probes.
- [x] **Native-boundary tests:** extend `tests/unit/test_elaboration_occurrence.py` and create
  `tests/conformance/test_elaboration_plural_scope.py`. Compare `Usage.usages` declaration UUIDs to
  occurrence records, reverse model/relationship order, and assert exact parent, index, effective
  usage, and effective type IDs.
- [x] **Replace child selection:** update `src/sysml_codegen/elaboration/occurrence.py` so child
  declarations come from the current usage's native `usages` collection. Remove the global
  owner/type-closure reconstruction. Retain supported composite filtering, finite constant
  multiplicity evaluation, typed/untyped usage handling, parent/index context, and cycle checks.
- [x] **Remove display-order choices:** update occurrence/elaboration display metadata selection so
  no `alternatives[0]`, first-enumerated base candidate, or similar traversal-order fallback affects
  either semantics or chosen display provenance. If display provenance has multiple equal semantic
  candidates, derive one deterministic record from exact IDs or surface an explicit collision.
- [x] **F31 disposition:** drive both plural fallback branches with the kept fixture. If a valid
  model reaches a branch, implement the design's permitted-scope rule and assert out-of-scope
  candidates are excluded. If no valid supported model can reach it, keep the evidence and delete
  the branch. In either outcome, model-wide fallback is removed.
- [x] **Elaborator integration:** update `src/sysml_codegen/elaboration/elaborate.py` so definition-
  and usage-owned contextualization consumes only the occurrence index's exact declaration/type/
  ancestor indexes. Remove fallback candidate enumeration that is not anchored to the consumer's
  permitted scope.
- [x] **Version gate:** rerun the SysIDE identity and native-boundary probes against exactly 0.8.4.
  Any upstream-version change stops the phase and requires explicit review; it does not trigger a
  QN/name fallback.

### Validation

**Automated:**

- [x] `uv run pytest tests/unit/test_elaboration_occurrence.py tests/conformance/test_elaboration_plural_scope.py tests/conformance/test_elaboration_specialization_retypes.py tests/conformance/test_elaboration_phase5_remediation.py -q`
- [x] `uv run pytest tests/conformance/test_elaboration_identity_foundation.py tests/conformance/test_elaboration_identity_vertical.py tests/conformance/test_elaboration_identity_collisions.py -q`
- [x] Run `.project/active/spike-syside-occurrence-authority/probe.py` in the licensed environment
  and compare the declaration-boundary observations to its kept findings.
- [x] Reverse file, relationship, subtype, and child enumeration in tests; occurrence IDs and graph
  edges remain identical.
- [x] `uv run ruff check src/sysml_codegen/elaboration tests/unit/test_elaboration_occurrence.py tests/conformance/test_elaboration_plural_scope.py`

**Manual:**

- [x] Inspect one occurrence tree. Each record names exact parent, containment slot, effective usage
  declaration, effective types, and index; display paths are derived side data.
- [x] Record F31 as “supported with scoped witness” or “unreachable and branch deleted,” citing the
  kept test. Do not retain an unproven fallback.

**What we know works after this phase:** SysIDE owns effective declaration selection, codegen owns
only concrete finite contexts, and no global/traversal-order fallback can widen plural resolution.

---

## Phase 4 — Structured Graph and One-Way Projection

### Goal

Make the validated instance graph contain every structural fact projection needs. Projection may
render public strings, but it may not parse them or rediscover semantic dependencies.

### Assumption under test

Exact occurrence records, typed nodes/ports/edges, typed neutral IR, value sites, and display
metadata are sufficient to render the complete current `ComputationGraph` seam without splitting
paths, indexing semantic payload by name/QN, or topologically sorting through rendered channels.

### Test stencil — write this first

```python
def test_projection_uses_only_typed_graph_structure():
    graph = structured_graph_with_misleading_display_metadata()
    rebuilt = decode_instance_graph(encode_instance_graph(graph))
    projected = project(rebuilt)
    assert projected.execution_order == expected_order_from_producer_edges()
    assert projected.output_aliases == expected_aliases_from_occurrence_records()
    assert projected.constraint_catalog == expected_catalog_from_typed_ports()
    assert semantic_edges(rebuilt) == semantic_edges(graph)
```

### Changes required

**Design references:** shared design
[D4](../elaborator-design/design.md#d4--node-identity-is-structured-and-opaque),
[D8](../elaborator-design/design.md#d8--projection-owns-strings-and-implements-the-complete-generation-seam),
and [D9](../elaborator-design/design.md#d9--snapshot-payload-is-the-resolved-instance-graph).

- [x] **Tests first:** extend `tests/conformance/test_elaboration_graph_roundtrip.py` and
  `test_elaboration_projection.py`; create
  `tests/conformance/test_elaboration_projection_one_way.py`. Mutate only display paths, module
  spellings, channel spellings, and IR display identity while keeping typed structure fixed. Assert
  dependency/owner/alias identity stays fixed or a public rendering collision blocks.
- [x] **Occurrence records in graph:** add a structured occurrence record to
  `src/sysml_codegen/elaboration/graph.py` and an `InstanceGraph.occurrences` index. Store exact
  parent, containment slot/index, effective usage, effective types, and display-segment metadata.
  Validate that every occurrence-scoped node has a record and every non-root occurrence has one
  existing parent.
- [x] **Typed IR in memory:** replace `CalcNode.expression_ir: str` and
  `ConstraintNode.predicate_ir: str` with typed
  `agentic_mbse.sysml.expression_ir.ExpressionIR`. Keep exact `ConsumerPortId`/
  `ExpressionPortId` associations for feature-reference positions. Validate one permitted edge set
  per reference occurrence before projection.
- [x] **Closed executable state:** make calculation compilability and constraint eligibility
  explicit validated graph fields. Remove default `PortMetadata()` reads for required ports and the
  decoder's default-`ADMIT` behavior. Reject invalid IR tags, eligibility values, missing metadata,
  extra/missing expression ports, dangling occurrence records, and conflicting output ports.
- [x] **Internal codec v2:** update `src/sysml_codegen/snapshot/instance_graph.py` to encode
  structured occurrences and typed IR canonically. Bump the internal schema from
  `instance-graph/v1` to `instance-graph/v2`, reject v1/unknown tags, and verify the fingerprint
  before construction. This is internal Item-6 evidence; do not connect it to the shipped v5
  snapshot loader or capture command.
- [x] **Projection ownership:** update `src/sysml_codegen/elaboration/project.py` to render owner and
  alias paths from occurrence records. Remove `rsplit`, `split`, or substring parsing that infers
  constraint ownership, alias instance scope, or source grouping from a rendered path.
- [x] **Projection IR:** traverse the typed IR object directly and map each feature-reference
  occurrence to its exact typed port. Render Python expression text and neutral constraint payload
  only at the public seam. Do not parse canonical JSON or recover formal identity from an IR name/QN.
- [x] **Typed topological sort:** compute module dependencies from `ProducerRef` targets before
  channel rendering. Add the synthetic constraint-report aggregator dependency explicitly after
  constraint nodes are known. Public channels remain output metadata and cannot select a producer.
- [x] **Value-site use:** derive entry-point classification from `ValueSite`, as D8 requires, rather
  than treating every `NodeRef` as a design attribute or reconstructing the class from names/value
  equality.
- [x] **Public seam parity:** keep `ComputationGraph`, generated names, registry renderer return
  contract, aliases, parameter groups, constraint catalog, and generated files unchanged for every
  green-or-equivalent Item-5 row. A genuine rendering collision remains a named block.

### Validation

**Automated:**

- [x] `uv run pytest tests/conformance/test_elaboration_graph_roundtrip.py tests/conformance/test_elaboration_projection.py tests/conformance/test_elaboration_projection_one_way.py tests/conformance/test_elaboration_generation_boundary.py -q`
- [x] Add malformed-codec cases for missing occurrence, wrong parent, invalid IR tag/version,
  invalid eligibility, missing metadata, extra expression edge, channel-name collision, and typed
  producer cycle; each fails with the named D10 outcome before generation.
- [x] Compare live graph projection with internal-v2 round-trip projection across the focused
  calculation, constraint, FORMULA, alias, and aggregation fixtures.
- [x] Run the frozen legacy/v5 gates; no committed snapshot or generated baseline changes.
- [x] `uv run ruff check src/sysml_codegen/elaboration src/sysml_codegen/snapshot/instance_graph.py tests/conformance/test_elaboration_projection_one_way.py`
- [x] `uv run mypy src/` with no changed new-route error.

**Manual:**

- [x] Search `project.py` for path parsing, name/QN indexes, and channel-to-producer reverse maps.
  Every remaining string operation must render or validate the public surface, never derive owner,
  alias scope, input identity, or dependency.
- [x] Inspect a canonical internal-v2 payload. It contains occurrence records, typed identities,
  direct edges, IR objects, closed eligibility/compilability state, and a valid fingerprint. It
  contains no live SysIDE object.

**What we know works after this phase:** The graph is a complete projectable artifact. Projection is
mechanical and one-way; changing presentation metadata cannot redirect semantic ownership or order.

---

## Phase 5 — Boundary Guard and Certification

### Goal

Protect the complete exact-resolution/projection boundary from regression and certify Item 6 across
the authoritative matrix, dual-run corpus, public generation mutation, both repositories, and the
frozen shipped route.

### Assumption under test

After Phases 1–4, every supported runtime source has one exact internal identity and every bound
consumer reaches it through typed edges. A complete static guard plus adversarial runtime evidence
can detect any return to string/QN/name selection or fail-open payload defaults.

### Test stencil — write this first

```python
@pytest.mark.parametrize("cell", supported_runtime_source_cells())
def test_off_default_source_reaches_every_and_only_bound_consumer(cell, tmp_path):
    baseline, changed = cell.project_exact_routes(tmp_path)
    assert changed.source_value == cell.off_default_value
    assert changed.consumers_of(cell.source_id) == cell.expected_consumers
    assert baseline.consumers_of(cell.source_id) == cell.expected_consumers
    assert changed.independent_sources == baseline.independent_sources
    assert cell.generated_pipeline_uses_exact_routes(changed)
```

### Changes required

**Design references:** shared design
[Validation Approach](../elaborator-design/design.md#validation-approach),
[Required Invariants](../elaborator-design/design.md#required-invariants), and
[Appendix A](../elaborator-design/design.md#appendix-a--required-adversarial-identity-cases).

- [x] **Expand F30 guard:** update `tests/unit/test_elaboration_import_boundaries.py` to scan the
  full semantic boundary: identity, occurrence, elaboration, graph validation, internal codec, and
  projection. Use AST checks scoped to selection/association functions so display rendering remains
  legal. Reject name/QN/rendered-path selectors, prefix/suffix matching, legacy occurrence imports,
  first-match selection, QN-keyed executable payload maps, IR string parsing for identity, and
  channel-to-producer reverse lookup for topological order.
- [x] **Guard falsifier:** add a small test-only mutation or parsed source snippet for each banned
  family and prove the guard fails. A guard that has only ever passed the production source is not
  certified.
- [x] **Strengthen runtime-cell evidence:** update
  `tests/conformance/test_elaboration_contract_matrix.py` so every `RUNTIME_CELLS` entry declares
  the complete expected consumer set, including calculation, constraint, FORMULA, alias, and
  aggregation consumers where present. For each cell, mutate one source off default and assert the
  exact public topology contains every and only that consumer set. Also assert all independent
  sources and their generated inputs remain unchanged.
- [x] **Public boundary evidence:** extend
  `tests/conformance/test_elaboration_public_mutation.py` to check the complete consumer set using
  typed graph identity before projection and the generated pipeline/input surface after projection.
  Retain Item 7's responsibility for the final shipped live-and-relocated-snapshot mutation.
- [x] **Matrix and corpus:** run all 29 authoritative cells and the 37-fixture dual-run corpus. Every
  row must be green or one named expected diagnostic. Update
  `../../completed/20260809_elaborator-breadth/diff-ledger.md` only if the ledger's maintained schema
  allows an Item-6 verification annotation without rewriting Item-5 history; otherwise record the
  run in this plan's Implementation Notes.
- [x] **Route isolation/freeze:** prove the legacy route remains the shipped black-box authority,
  no new route imports legacy occurrence/resolution machinery, and no exact graph is built from a
  mixture of the two. Snapshot v5 bytes, legacy generated output, capture behavior, and CLI default
  route remain unchanged.
- [x] **Scale smoke:** run the internal exact route and projection on one real TEAx-scale model that
  is already in the maintained licensed corpus. Record time/memory and any named diagnostic. Do not
  turn this into the Item-7 shipped live/snapshot smoke.
- [x] **Update artifacts:** check all five plan phases immediately after their gates pass. Record
  deviations and exact test counts here; update `../../CURRENT_WORK.md` with Item-6 status and Item-7
  readiness. Do not mark the item certified; `$my-audit` owns independent certification.

### Validation

**Focused and contract gates:**

- [x] `uv run pytest tests/unit/test_elaboration_import_boundaries.py -q`
- [x] `uv run pytest tests/conformance/test_elaboration_contract_matrix.py tests/conformance/test_elaboration_public_mutation.py tests/conformance/test_elaboration_generation_boundary.py -q`
- [x] `uv run pytest tests/conformance -k 'elaboration or constraint_snapshot_identity' -q`
- [x] `uv run python scripts/run_elaboration_corpus.py` — 37 discovered, 37 classified, zero
  unclassified rows.

**Repository-wide gates:**

- [x] Codegen: `uv run pytest tests/`
- [x] Codegen: `uv run ruff check src tests`
- [x] Codegen: `uv run mypy src/` — no new changed-file errors; record the total baseline.
- [x] Agentic: `uv run pytest tests/`
- [x] Agentic: `uv run ruff check src tests`
- [x] Agentic: `uv run mypy src/`
- [x] `git diff --check` in both repositories.

**Freeze and manual gates:**

- [x] Licensed runs collect all intended tests with zero `no live syside license` skip lines.
- [x] Committed extraction-snapshot/v5 files and legacy generated baselines are byte-identical to the
  recorded pre-change hashes.
- [x] Search both diffs for new name/QN/rendered-path selection, silent `.get(..., ADMIT/UNKNOWN/
  float/None)` behavior, and first-enumerated candidates. Disposition every hit.
- [x] Review the public mutation report by runtime cell: the changed source, exact consumer set,
  unchanged independent sources, and generated route are explicit.
- [x] Confirm Item 7 remains the only owner of route switch, new shipped envelope, recapture,
  deletion ledger, and harness removal.

**What we know works after this phase:** Exact identity covers executable payload, effective
declarations, concrete occurrences, structured graph state, and projection for the complete
supported surface. The inherited matrix and corpus remain classified, public mutation reaches every
and only bound consumer, and the shipped legacy/v5 route is unchanged. Item 7 can begin after an
independent `$my-audit` certifies these claims.

---

## Risk Management

- **Cross-repository partial landing:** the identified constraint wrapper and codegen consumer are
  one coordinated unit. Keep both branches/commits recorded and do not advertise a one-sided state.
- **Live-only IDs leak into v5:** exact sidecars are optional at the shared extraction dataclass but
  mandatory at the live exact-route boundary. The v5 serializer explicitly excludes them and byte
  gates catch leakage.
- **Parallel exact and legacy compiler paths drift:** share the AST walk internally. The legacy
  adapter preserves existing outputs; exact results remain UUID-keyed. Tests run both surfaces over
  the same fixtures.
- **Neutral constraint schema becomes parser-specific:** parser UUIDs live only in the identified
  wrapper. Golden neutral serialization and field-inventory tests block leakage.
- **Native `Usage.usages` differs on an unprobed shape:** Phase 3 combines inheritance, retyping,
  redefinition, and multiplicity before graph work. A mismatch is surfaced against the recorded
  design premise; it is not repaired with global name grouping.
- **Projection still reconstructs structure indirectly:** the Phase-4 adversarial metadata test and
  Phase-5 AST guard cover owner, alias, IR input, and topological-order paths separately.
- **Internal codec mistaken for cutover:** `instance-graph/v2` remains an internal test artifact.
  Item 7 designs and lands the shipped envelope and relocation contract.
- **Matrix mutation proves only value files:** strengthened evidence asserts the exact complete
  consumer set and generated routes, including independent-source noninterference.
- **Work expands into public renaming:** collisions block with `SI_RENDERING_COLLISION`. Automatic
  disambiguation or public-name changes require a separate owner-approved design.

## Implementation Notes

Record commands, counts, commits, deviations, and decisions here as each phase executes. Preserve
the red-first evidence and update checkboxes immediately; do not reconstruct the history at the end.

### Phase 1–2 audit remediation

- **Completed:** 2026-08-09 20:05 PDT.
- **audit-F1:** Definition-typed constraint nodes retain only the typed effective-definition ID and
  definition display metadata. Projection now renders the public `definition:{qualified-name}`
  source key. The focused regression failed red on the parser UUID and passes after the change.
- **audit-F2:** Shared calculation extraction now records a stable UUID sidecar when available and
  leaves it empty for null-QN or non-v5 members. It no longer raises the audit's bare `ValueError`.
  Exact elaboration remains the enforcement boundary and reports missing required definition or
  port identity as `SI_ID_MISSING`.
- **audit-F3:** The corpus-ledger test now reads the archived Item-5 ledger. Its two structural
  checks pass. The live comparison runs and currently reports one real Phase 3–4 outcome mismatch:
  `return_styles` is `SI_REDEFINITION_INVALID`, while the archived ledger records
  `3× SI_SELF_BINDING`. The gate is active; the current phase work must classify or correct that
  outcome before Phase 5.
- **Validation:** The two focused F1/F2 regressions pass; 45 impacted extraction/elaboration/codec/
  projection tests pass; all 83 legacy/v5 freeze tests pass; changed-scope ruff and both repository
  `git diff --check` gates are clean. Full codegen mypy reports 81 errors. None points at an F1/F2
  remediation line; the increase from the audited 71-error baseline is in concurrent Phase-4
  graph/codec/projection work.

### Phase 1

- **Completed:** 2026-08-09 16:43 PDT
- **Red evidence:** Valid licensed fixture collected 7 tests; all 7 failed on the absent exact
  definition/member fields, exact compiler entry point, and graph attachment fields. The first
  fixture draft used unavailable local type aliases; that model preflight was corrected before the
  feature-level red run and is not counted as red evidence.
- **Changes made:** Added live-only raw UUID sidecars on calc definitions and members; exact-ID AST,
  member-name, and intermediate maps; `compile_calc_def_exact()` with UUID dependency/output
  results; exact definition/formal/output payload indexes in elaboration; explicit definition,
  compilation, and compiled-output identities on `CalcNode`; graph payload-totality validation;
  internal-codec transport for those Phase-1 graph fields; and the collision/missing/conflicting
  identity fixture and test coverage.
- **Green evidence:** Required focused plus extraction/return pins: 184 passed. Broad exact-route
  conformance excluding the known corpus-ledger bookkeeping failures: 151 passed. Legacy/v5 freeze:
  83 passed. Changed-scope ruff: clean. Mypy: no new error in `data_models.py`,
  `expression_compiler.py`, `elaborate.py`, `graph.py`, or `instance_graph.py`; only the existing
  extractor baseline remains. Combined committed snapshot/generated-baseline SHA-256 stayed
  `25e45ad6cc8885acb2e7c58f48d76376f94c9ce4fbf22d6ea31a1d6a9aa0f28f`.
- **Issues encountered:** Fresh pre-change codegen full suite was 3307 passed / 47 skipped /
  18 deselected with two existing `test_elaboration_corpus_ledger.py` failures. The corpus runner
  itself remained 37/37 and the 29-cell matrix remained 31/31. Agentic pre-change was 1814 passed /
  1 skipped / 33 deselected. Baselines were 72 codegen mypy errors, 105 agentic mypy errors, one
  unrelated agentic ruff error, and clean codegen source ruff.
- **Deviations:** The serializer already honored per-field `snapshot_exclude` metadata, so the new
  sidecars use that mechanism instead of changing serializer logic. The internal v1 graph codec now
  carries the Phase-1 identity fields so existing round-trip evidence stays valid; Phase 4 still
  owns structured occurrences/typed IR and the v2 bump. No shipped snapshot-v5 field or byte moved.
- **Base commits:** codegen `b9c22c0c66ab432216628fc84beaf3f2ac0a7e0c`; agentic-mbse
  `2e679537691be87465543ba682044a0281b38f13`.

### Phase 2

- **Completed:** 2026-08-09 17:07 PDT
- **Red evidence:** Agentic collected zero tests with two import errors because the identified
  wrapper and evaluator API did not exist. After adding the live codegen collision fixture, its
  focused eight-test run reached the feature boundary: seven passed and the new constraint test
  failed because graph eligibility was the open string `"block"`, not `Eligibility.BLOCK`.
  The later decision-inventory pin caught duplicate UUID decisions escaping as a raw `ValueError`;
  it was mapped to the named `SI_EDGE_DANGLING` boundary before the green run.
- **Changes made:** Agentic now returns live-only identified definition/usage records around the
  unchanged neutral facts and evaluates definition-typed usages against an exact UUID-selected
  definition. Codegen validates the live usage/definition inventory, wraps stable UUIDs once,
  attaches decisions by exact usage ID, and rejects missing, duplicate, foreign, or disagreeing
  associations. `ConstraintNode` carries closed `Eligibility`, exact effective-definition ID, and
  typed `ExpressionIR`; only the internal graph codec serializes the IR. The QN decision join and
  missing-decision `ADMIT` default are gone.
- **Green evidence:** Required agentic focus: 66 passed. Required codegen focus: 19 passed; final
  payload/codec/projection focus: 21 passed. Broad exact-route
  conformance: 157 passed. Agentic full suite: 1,818 passed / 1 skipped / 33 deselected. Codegen
  post-fix full suite excluding only the archived-ledger file: 3,324 passed / 47 skipped /
  18 deselected. The two archived-ledger failures are the recorded pre-change baseline. Legacy/v5
  freeze: 83 passed. Changed-file ruff is clean in both repositories. Full ruff remains at the
  existing test-tree baselines (127 agentic, 361 codegen). Mypy returned the 105-error agentic
  baseline and 71 codegen errors versus 72 pre-change, with no error in a changed route file.
  `git diff --check` is clean in both repositories.
- **Freeze evidence:** Agentic neutral golden SHA-256 matches `HEAD` at
  `3270886a2775192ae5b03873fc3d9dad9dd008808cc30b7333f43d0ee5c81800`. The combined committed
  extraction-snapshot/generated-baseline hash remains
  `25e45ad6cc8885acb2e7c58f48d76376f94c9ce4fbf22d6ea31a1d6a9aa0f28f`.
- **Coordinated repository state/deviations:** Changes are intentionally uncommitted in both
  coordinated worktrees; no one-sided API is presented as landed. The existing neutral
  `evaluate_profile()` QN adapter remains for legacy callers. The live exact route calls only
  `evaluate_identified_profile()`. The internal codec remains `instance-graph/v1`; its wire JSON
  gains the exact definition ID but no shipped snapshot-v5 byte changes. A post-phase full run also
  exposed and corrected the Phase-1 dataclass field-inventory pin for the five live-only sidecars.

### Phase 3

- **Completed:** 2026-08-09 19:48 PDT
- **Red evidence:** The corrected licensed fixture run collected 11 tests: 10 passed and the new
  native-boundary test failed because `ExactOccurrence` had no child-declaration record. The first
  fixture draft used a binding value that SysIDE correctly rejected as non-overridable; it was
  changed to a default before the feature-level red run and is not counted as red evidence.
- **Changes made:** Added `elab_native_plural_scope` with provenance, native declaration/occurrence
  assertions, sibling-scope plural formulas, and reversed-enumeration evidence. The occurrence
  walker now consumes each usage's native `usages` view, filters to supported user-model composite
  parts, chooses the unique effective declaration through exact redefinition endpoints, and records
  the chosen child IDs. The global owner/type child reconstruction is gone. Attribute and
  calculation slot display provenance now requires the exact slot root instead of taking the first
  enumerated candidate.
- **Green evidence:** Required Phase-3 selection: 37 passed with zero license-skip lines. The two
  plan commands account for 28 and 9 tests respectively. The kept SysIDE probe reproduced the
  recorded 6/5/3/4/2 occurrence counts across `d38_caret`, `deep_cross_scope_probe`,
  `nested_occurrence_override_probe`, `retype_model`, and `spec_chain_twolevel`. Changed-scope ruff
  is clean.
- **F31 disposition:** **supported with scoped witness.** The valid fixture reaches both package-
  scoped and cross-root occurrence-scoped plural selection. Both must start from an exact top-level
  occurrence declaration. Nested candidates outside the consumer lineage are excluded; the prior
  model-wide returns are deleted. The calculation-root mirror now receives the plural contract and
  applies the same top-level permitted-scope rule instead of collapsing to scalar selection.
- **Issues/deviations:** `Usage.usages` returns the applicable base and redefining declarations for
  one slot, not only the winner. The implementation therefore selects the sole declaration that
  redefines every other native candidate through the already-authoritative exact endpoint graph.
  It does not restore owner/name/type-closure reconstruction. No shipped route or snapshot byte was
  changed.

### Phase 4

- **Completed:** 2026-08-09 20:10 PDT.
- **Red evidence:** The initial focused run collected 17 tests: 9 passed and 8 failed on the v1
  codec tag, absent occurrence records, accepted malformed IR/ports, display-path-derived
  constraint ownership, and missing occurrence/cycle validation. The deferred audit-F4 pin then
  failed independently because an exact `Integer` constraint input still projected as `float`.
- **Changes made:** `InstanceGraph` now carries validated occurrence records, typed expression IR,
  closed compilability/eligibility, total port metadata, and typed producer edges. The internal
  codec is `instance-graph/v2`, fingerprints before construction, transports IR as JSON objects,
  and rejects v1 or malformed graph state. Projection renders occurrence ownership and aliases from
  structured records, traverses IR objects directly, orders modules from `ProducerRef` edges, and
  uses `ValueSite` for entry-point classification. Constraint input types now come from the exact
  feature slot's `FeatureTyping`; the fail-open `float` default from audit-F4 is deleted.
- **Green evidence:** The required Phase-4 selection passes 22 tests. Broad exact-route conformance
  excluding only the separately recorded corpus-ledger outcome passes 171 tests with zero license
  skips. Phase-3 regression selection passes 28 tests, and the second identity selection accounts
  for the remaining 9 Phase-3 tests. Frozen legacy/v5 gates pass 83 tests. Changed-scope ruff and
  `git diff --check` are clean. Full mypy reports the established 71 errors in 17 legacy files and
  none in a changed new-route file. Committed snapshot and generated-baseline paths have no diff.
- **Internal codec/manual review:** A canonical payload reports `instance-graph/v2`, a 64-character
  fingerprint, all eight structured occurrence fields, and typed `expression-ir/v1` objects; it is
  JSON-only and carries no live SysIDE object. Remaining `project.py` string splits only render
  public class/module names. Typed output-port maps select producers; rendered channel maps only
  render outputs and detect public collisions.
- **Scope/deviation:** The codec remains internal Item-6 evidence. The shipped v5 loader, capture
  command, generated names, and route authority are unchanged. Phase 5 still owns the complete
  boundary guard, corpus classification, full repository gates, and certification.

### Audit v2 remediation

- **Completed:** 2026-08-09.
- **audit-F5:** Accepted. Constraint inputs now carry exact declaration-bound formal provenance in
  their typed port metadata. Graph validation and codec v2 reject absent or mismatched provenance;
  projection consumes that payload directly. The rendered-name join and fabricated null-QN
  identity are deleted. A quoted `'max power'` formal and a re-fingerprinted malformed payload pin
  both the positive and fail-closed paths.
- **audit-F6:** Accepted as a regression and corrected on cause. The failing slot was the unscoped
  `StyleD::y` return attribute rooted at `Performances::Evaluation::result`, not the supported
  bare-`in` `BareInC::x` formal. Restoring the pre-Phase-3 scoped-value admission rule makes
  `return_styles` reach exactly its three authored `SI_SELF_BINDING` diagnostics.
- **Green evidence:** Focused remediation 3 passed; Phase-3 selection 38 passed; Phase-4 selection
  24 passed; corpus-ledger selection 3 passed; broad exact-route conformance 177 passed; frozen
  legacy/v5 gates 83 passed; the corpus runner discovered and classified all 37 fixtures.
  Changed-file ruff and both repositories' `git diff --check` are clean. Full mypy remains at the
  recorded 71 errors in 17 legacy files, with none in the changed elaboration/projection/codec
  files. Committed snapshot and generated-baseline paths are unchanged.
- **Scope at this checkpoint:** This resolved the two Phase-3/4 audit findings. Phase 5 was still
  unstarted here; its completed evidence is recorded below.

### Phase 5

- **Completed:** 2026-08-09 21:13 PDT.
- **Red evidence:** After the parsed-source falsifier harness itself was corrected, the focused
  guard run had one production failure. It reported first-match selection in exact occurrence
  winner handling and name/rendered-module comparison in projection order. The production fix
  destructures the already-proven unique winner and stores projected modules by typed semantic key.
  The completed guard has eight falsifiers, one for every banned family, and passes 13 tests.
- **Boundary and public evidence:** F30 now scans identity, occurrence, elaboration, graph
  validation, the internal codec, and projection. Selection/association functions reject legacy
  resolution imports, presentation-key lookup/comparison, prefix/suffix selectors, first-match
  selection, IR parsing outside the codec, and channel reverse lookup. Every runtime cell declares
  complete public consumers and relevant aliases. Off-default mutation preserves the complete
  typed-route inventory, reaches every and only the declared public/generated consumers, and leaves
  independent sources unchanged. The focused matrix/public/generation selection passes 34 tests.
- **Matrix/corpus evidence:** Broad exact-route conformance passes 177 tests with zero license-skip
  lines. This includes all 29 authoritative matrix cells and the archived-ledger checks. The corpus
  runner discovers and classifies all 37 fixtures with outcomes matching the archived Item-5
  ledger. The ledger was not amended because its historical schema and every maintained outcome are
  unchanged.
- **Route isolation and freeze:** Static checks prove CLI and capture still use the legacy builder,
  the internal exact entry point does not import the legacy builder or snapshot rebuild, and no
  mixed graph route is available. Frozen legacy/v5 gates pass 83 tests. No committed extraction
  snapshot, v5 file, or generated baseline differs. Their combined SHA-256 remains
  `25e45ad6cc8885acb2e7c58f48d76376f94c9ce4fbf22d6ea31a1d6a9aa0f28f`.
- **Scale smoke:** The internal exact route was run on the maintained `solar_battery_model` corpus
  model under `/usr/bin/time -v`. It stopped by the expected classified outcome, exactly 24
  `SI_SELF_BINDING` diagnostics, in 0.97 seconds with 208,220 KiB maximum RSS. No shipped authority,
  snapshot, or cutover surface was exercised.
- **Repository gates:** Codegen: 3,356 passed / 47 skipped / 18 deselected. Agentic: 1,818 passed /
  1 skipped / 33 deselected. Both `git diff --check` gates pass. Changed Phase-5 files pass ruff.
  Full ruff records the existing test-tree baselines: 358 codegen and 127 agentic findings. Mypy
  records the existing baselines: 71 errors in 17 codegen files and 105 errors in 23 agentic files;
  none is in the changed occurrence/projection files.
- **Manual review:** Remaining name/QN/rendered-path operations are public rendering, collision
  checks, exact-type vocabulary rendering, legacy compatibility, or generated-output assertions.
  Remaining candidate indexing follows an exact cardinality check. No silent executable default or
  first-enumerated semantic winner remains. Item 7 still solely owns cutover, the shipped envelope,
  recapture, deletion, harness removal, and the final live/relocated-snapshot proof.
- **Independent audit:** Pending. These implementation results do not certify Item 6.

### audit_v3 remediation — audit-F7 through audit-F9

- **Completed:** 2026-08-10.
- **Red evidence:** The F7 fixture returned normally instead of raising on its profile `BLOCK`.
  The F9 falsifier added an unlisted selector function and the guard returned no violation. The F8
  alternating-sweep probe forced equal sort keys and reversed the second live enumeration; the
  positional `zip` attached each anonymous fact to the other usage UUID. All three failed before
  production changes.
- **audit-F7:** Added `SI_CONSTRAINT_BLOCKED` to D10. Every profile `BLOCK` records one named graph
  diagnostic with the profile reason and exact consumer. Strict elaboration raises
  `ElaborationDiagnosticError`; lenient mode retains the typed node for corpus inspection; graph
  round-trip preserves the diagnostic; projection refuses the graph. The fixture asserts the
  `blocked_guard` halt and `block_real_equality_requires_tolerance` reason before generation.
- **audit-F8:** Neutral facts and live elements are now paired in the same extraction record and
  indexed by usage UUID. The second sweep and positional `zip` are deleted. Item 7's deletion
  ledger now names the identified extraction/evaluator, exact compiler, and paired calculation-map
  duals, with the convergence action for each. Neutral schema and serialization remain unchanged.
- **audit-F9:** F30 is deny-by-default. Every function in identity, occurrence, elaboration, graph,
  internal codec, and projection is scanned automatically. Five qualified-function exemptions cover
  only wire decoding or public rendering, name their exact waived rule, and fail if the waived
  syntax disappears. A newly added function is guarded without updating a function allowlist.
  SC5 was not narrowed. The optional constraint-module-type collision concern is separate public
  rendering policy, not semantic selector coverage, and was not folded into this remediation.
- **Green evidence:** F7/F9/codec/projection focus 44 passed; agentic extraction/profile 67 passed;
  neutral serialization/schema 28 passed; guard 14 passed; broad exact route 178 passed; matrix,
  public mutation, generation, and legacy/v5 freeze combined 131 passed; corpus 37/37 with archived
  outcomes unchanged. Full codegen: 3,358 passed / 47 skipped / 18 deselected. Full agentic: 1,819
  passed / 1 skipped / 33 deselected. Changed-file ruff passes; full ruff remains at 358 codegen /
  127 agentic findings. Mypy remains at 71 errors in 17 codegen files / 105 errors in 23 agentic
  files, with no changed-file error. Both `git diff --check` gates pass. The frozen artifact hash
  remains `25e45ad6cc8885acb2e7c58f48d76376f94c9ce4fbf22d6ea31a1d6a9aa0f28f`.
- **Certification state:** `audit_v3.md` remains the independent verdict of record. Spec SC2 and
  SC5 remain unchecked until an independent re-audit verifies these responses. Phase checkboxes
  remain implementation progress only.

---

**Next step:** Run an independent `$my-audit` recheck of audit-F7 through audit-F9. Item 7 may begin
only after that audit certifies Item 6.
