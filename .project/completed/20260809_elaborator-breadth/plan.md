# Implementation Plan: Exact-Identity Elaborator Breadth (ELABORATE-FIRST Item 5)

- **Status:** CERTIFIED 2026-08-09 (`audit_v3.md` addendum). The targeted re-verification
  confirmed the audit-v3 remediation live: invalid inherited/owned part conflicts block
  `SYSML_NAMESPACE_NOT_DISTINGUISHABLE` before occurrence expansion (strict and lenient), the
  repaired `:>>` DCS witness resolves every reference with one sensor/core occurrence, DCS:82
  wires to its one producer channel through public projection, the corrected F21 amendment is
  ratified with true premises, and every gate reproduces (154 elab / 3309 codegen / 1814 agentic /
  freeze clean). Product-lens ledger has no unresolved BLOCK. audit-F30/F31 remain open disposed
  (guard scope, plural-fallback fixture). Item 6 is out of scope and needs the owner's go.
- **Created:** 2026-08-08 11:03:33 PDT
- **Last Updated:** 2026-08-09 (audit-v3 remediation gates pass; independent re-audit pending)
- **Owner:** Reid W
- **Branch:** `source-identity-epic`
- **Base Commit:** `6bed968`

## Source Documents

- **Spec:** `../elaborator-design/spec.md`
- **Design:** `../elaborator-design/design.md`
- **Design review:** `../elaborator-design/design-review.md`
- **Identity probe record:**
  `../../research/20260808-103243_syside-identity-and-redefinition-probe-record.md`
- **Prior implementation audit (rendered-path, superseded):** `audit-20260808-rendered-path.md`
- **Epic Item 5:** `../../backlog/epic_elaborate_first_architecture.md:294-337`
- **Item-3 behavior authority:**
  `../../concepts/constraint-execution-authoritative-lifecycle-contract.md:287-368`

## The Point

SysIDE has already resolved which declaration each semantic reference denotes. Codegen must preserve
that exact declaration identity, interpret it in one exact concrete occurrence, and store the
resulting node or output-port edge. It must not reduce the referent to a name and later guess which
same-named object was intended.

One semantic source occurrence must therefore become exactly one runtime source across calculation,
constraint, FORMULA, alias, and aggregation consumers. Unsupported or unstable identity must produce
a named blocking outcome. Strings enter only after semantic identity is settled, for diagnostics,
wire encoding, and projection onto the existing generated API.

Item 5 builds and proves that complete new front end while the complete legacy front end remains the
unchanged shipped authority. Item 6, planned separately under `elaborator-cutover`, will switch the
front-end boundary, replace snapshot v5, recapture the corpus, execute the deletion ledger, and
remove the dual-run harness.

## Implementation Strategy

### Phasing rationale

The order follows the validation sequence in
[the design](../elaborator-design/design.md#validation-approach). Kept tests first determine whether
the SysIDE identity foundation is viable. The first production landing then carries identity through
the entire vertical path in one atomic cross-repository unit. Only after that authority exists do we
port breadth, project to the public generation seam, and grind the corpus.

The existing `src/sysml_codegen/elaboration/` package and its tests are useful behavior and fixture
evidence, but they implement the superseded rendered-path design. No implementation phase is marked
complete merely because that package currently passes friendly fixtures. Reuse code where it already
matches the approved design; replace its identity mechanics rather than wrapping them.

### Critical path

```text
kept SysIDE identity probes
    -> exact evidence + new occurrence walker + typed graph + one resolver
    -> all consumer forms and fail-closed diagnostics
    -> full projection + internal graph round-trip
    -> 29-cell / 37-fixture dual-run proof + public mutation
    -> owner checkpoint before Item 6
```

### First proof point

A reference whose SysIDE referent is an outer chain root must still target that outer occurrence when
a nearer same-named root exists. In the same vertical slice, an ordinary implied parameter
redefinition must join its definition formal's slot. Reversing traversal and relationship order must
not change either edge.

### Test-first evidence rule

Each phase begins by adding or changing the named tests and observing the relevant test fail before
production code changes. Record the failing command/result and the later green command/result in
that phase's Implementation Notes. A test added in the same commit as implementation is not, by
itself, proof of the required red-first sequence.

### Scope boundary

- **Included:** exact identity foundation, complete new-route semantics, projection, an internal
  instance-graph round-trip, dual-run tooling, the 29-cell matrix, the 37-fixture ledger, and the
  off-default public mutation.
- **Excluded:** changing the shipped `build_pipeline_context` route, changing or recapturing snapshot
  v5, deleting legacy code, or adding a shipped feature flag. Those moves are Item 6 and remain one
  atomic landing per [the design](../elaborator-design/design.md#integration-strategy).

### Progress

- [x] Phase 1 — Identity-foundation kill probes
- [x] Phase 2 — Atomic exact-ID vertical slice
- [x] Phase 3 — Semantic breadth and fail-closed behavior
- [x] Phase 4 — Projection and internal graph round-trip
- [x] Phase 5 — Dual-run corpus proof and owner checkpoint (audit-v3 remediation and corrected
  owner checkpoint complete; independent audit owns certification)

---

## Phase 1 — Identity-Foundation Kill Probes

### Goal

Replace session-only probe evidence with kept licensed tests before production code depends on
SysIDE's identity behavior. This phase changes tests, fixtures, and the research evidence record only.

### Assumption under test

SysIDE 0.8.4 supplies reload-stable IDs for the supported declaration boundary, resolved referents
carry those exact IDs, and authored plus implied redefinitions expose stable semantic endpoint IDs.
Null-QN declarations outside that boundary can be detected and rejected rather than joined by name.
See [B1/B2](../elaborator-design/design.md#proven-assumptions-and-remaining-bet) and
[Appendix A cases 1, 3, and 5](../elaborator-design/design.md#appendix-a--required-adversarial-identity-cases).

### Test stencil — write this first

```python
def test_syside_identity_boundary_is_repeatable():
    first = load_identity_probe(relocated=False, reverse_files=False)
    second = load_identity_probe(relocated=True, reverse_files=True)
    assert first.named_declaration_ids == second.named_declaration_ids
    assert first.resolved_referent_id == first.referred_declaration_id
    assert first.implied_redefinition_endpoints == second.implied_redefinition_endpoints
    assert first.relationship_id != second.relationship_id
    assert first.null_qn_element_id != second.null_qn_element_id
```

### Changes required

**Design references:** [D1](../elaborator-design/design.md#d1--declaration-identity-is-syside-element_id),
[D2](../elaborator-design/design.md#d2--feature-slots-follow-all-materialized-redefinition-edges),
[Potential Risks](../elaborator-design/design.md#potential-risks).

- [x] **Codegen kept probe:** create
  `tests/conformance/test_elaboration_identity_foundation.py` covering independent loads,
  relocation, file order, harmless source/model edits, referent equality, UUID version/stability,
  null-QN executable disposition, and relationship-ID exclusion.
- [x] **Agentic kept probe:** create
  `../agentic-mbse/tests/test_sysml/test_syside_identity_contract.py` covering the raw SysIDE
  `element_id`, exact referent, chain, typing, and `Redefinition` endpoint surfaces without adding a
  production identity abstraction yet.
- [x] **Fixture:** reuse `spec_chain_twolevel`, `shadowed_reference`, and
  `sibling_channel_ambiguity`; add `tests/fixtures/elab_identity_collision_probe/` only for a
  null-QN/same-name form that the kept corpus cannot already expose.
- [x] **Evidence record:** append kept test names, commands, and observed outcomes to
  `../../research/20260808-103243_syside-identity-and-redefinition-probe-record.md`; do not rewrite
  the earlier session-evidence provenance.

### Validation

**Automated:**

- [x] Codegen focused licensed probe:
  `uv run pytest tests/conformance/test_elaboration_identity_foundation.py -q` — all collected,
  zero license-skip lines.
- [x] Agentic focused licensed probe from `../agentic-mbse`:
  `uv run pytest tests/test_sysml/test_syside_identity_contract.py -q` — all collected, zero
  license-skip lines.
- [x] Repeat both commands after relocating the fixture copy through the tests; IDs and endpoint
  families remain identical.

**Manual:**

- [x] Review the recorded ID matrix: named IDs and endpoint IDs are stable; null-QN and relationship
  IDs are never presented as stable declaration identity.

**What we know works after this phase:** The upstream identity assumptions are reproducible and the
exact fail-closed boundary is known. Any failure is a stop condition; Phase 2 does not start.

---

## Phase 2 — Atomic Exact-ID Vertical Slice

### Goal

Land one exact semantic authority from SysIDE evidence through a clean occurrence walker, typed
graph identity, and the contextual resolver. Prove one representative of every resolution class
before porting the remaining shapes.

### Assumption under test

Exact declaration IDs plus an exact consumer occurrence are sufficient to resolve a chain,
definition-owned reference, usage-owned reference, authored/implied redefinition, expression
operand set, and aggregation term without QNs, names, rendered paths, or first-match selection.
See [D3-D7](../elaborator-design/design.md#d3--the-new-front-end-owns-a-clean-exact-id-occurrence-walker)
and [Required Invariants](../elaborator-design/design.md#required-invariants).

### Test stencil — write this first

```python
def test_exact_vertical_slice_ignores_nearer_same_name_and_order():
    graph = elaborate_exact(load_shadow_trap(reverse_iteration=True))
    edge = graph.input_edge(consumer_id(), formal_port_id())
    assert edge.target == outer_source_node_id()
    assert graph.slot_of(implied_usage_formal_id()) == graph.slot_of(definition_formal_id())
    assert isinstance(edge.target, NodeId | OutputPortId)
    assert graph.rendered_names_are_metadata_only()
```

### Changes required

**Design references:** [D1-D5](../elaborator-design/design.md#key-decisions),
[Live construction](../elaborator-design/design.md#live-construction),
[Component Overview](../elaborator-design/design.md#component-overview), and
[Integration Strategy](../elaborator-design/design.md#integration-strategy).

- [x] **Agentic tests first:** extend the Phase-1 suite and the existing expression tests to require
  an adapter accessor and exact IDs on resolved target/chain/redefinition facts. Pin the
  `agentic-mbse` dependency to the reviewed SysIDE 0.8.4 boundary.
- [x] **Agentic production surface:** update
  `../agentic-mbse/src/agentic_mbse/sysml/{syside_adapter.py,data_models.py,expression.py}` so the
  adapter alone reads `element_id` and evidence retains exact element and endpoint UUIDs. Agentic
  owns raw parser UUID facts; it does not import codegen identity types.
- [x] **Codegen identity tests first:** create
  `tests/unit/test_elaboration_identity.py`,
  `tests/unit/test_elaboration_occurrence.py`, and
  `tests/conformance/test_elaboration_identity_vertical.py`. Include runtime type separation,
  canonical UUID serialization, same-name traps, order reversal, and the exact five-form vertical
  slice.
- [x] **Existing-test migration:** update the existing `test_elaboration_*.py` helpers to query
  typed graph identities or explicit display metadata. Keep their semantic assertions green without
  adding a rendered-path compatibility index to production.
- [x] **Codegen identity boundary:** create `src/sysml_codegen/elaboration/identity.py` with the
  frozen runtime identity types and the one contextual bridge; wrap raw adapter UUIDs once at this
  boundary.
- [x] **New occurrence authority:** create `src/sysml_codegen/elaboration/occurrence.py`; port the
  required finite multiplicity, containment, subtype, and cycle behavior without importing or
  adapting `analysis.part_instance_index` types.
- [x] **Exact evidence:** replace the semantic fields in
  `src/sysml_codegen/extraction/{source_evidence.py,binding_evidence.py}` with declaration/segment/
  formal/redefinition endpoint IDs. Retain authored text and QNs only as diagnostic metadata.
- [x] **Typed graph and resolver:** replace rendered string keys and string input/output selectors in
  `src/sysml_codegen/elaboration/{graph.py,elaborate.py,__init__.py}` with the identity types and one
  resolver. Relationship-object IDs and sanitized term keys cannot key slots or edges.
- [x] **Isolation guard:** add `tests/unit/test_elaboration_import_boundaries.py` to reject imports
  of `PartInstanceIndex`, `PathStep`, `InstanceOccurrence`, rendered-path parsing, `sanitize_name`,
  or first-match selection inside the new identity/occurrence/resolver modules.
- [x] **Legacy freeze:** keep `analysis/part_instance_index.py`, the legacy pipeline, and snapshot v5
  behavior unchanged; extend existing snapshot/legacy regression tests only as needed to prove
  byte identity.

### Validation

**Automated:**

- [x] Run the Phase-1 kill probes and all new Phase-2 unit/conformance tests in both repositories.
- [x] Run existing part-index, source-evidence, elaboration spike-parity, shadowing, sibling,
  specialization, aggregation, and snapshot-v5 tests.
- [x] Run full suites in both repositories, `uv run ruff check src tests`, codegen
  `uv run mypy src/`, and record exact counts/baseline.
- [x] `git diff --check` in both repositories.

**Manual:**

- [x] Inspect one graph dump: identity fields are structured IDs; names and QNs appear only in
  display/provenance fields.
- [x] Record both repository commits/branches as one coordinated acceptance unit. Do not land or
  advertise a partially authoritative identity rider.

**What we know works after this phase:** The new route has one exact identity authority and no
dependency on the legacy occurrence walker. The five representative source forms survive the full
parser-to-edge path under adversarial names and order.

---

## Phase 3 — Semantic Breadth and Fail-Closed Behavior

### Goal

Port every supported consumer/value form onto the exact bridge and close the audit's silent-fallback,
ordering, alias-cycle, and rendered-key overwrite findings before projection begins.

### Assumption under test

The approved value precedence and one resolver cover usage/definition attributes, retypes,
specialization, EXPOSE aliases, calculation and constraint bindings, FORMULA nodes, expression
redefinitions, and finite aggregation expansion. Unsupported forms can block without becoming
unbound inputs or value-less sources. See
[D6-D7](../elaborator-design/design.md#d6--redefinition-precedence-is-one-ordered-candidate-model)
and [D10](../elaborator-design/design.md#d10--unsupported-identity-fails-closed-through-a-fixed-diagnostic-catalog).

### Test stencil — write this first

```python
def test_every_authored_rhs_becomes_edge_literal_or_blocking_diagnostic():
    result = elaborate_lenient(load_fail_closed_family())
    assert result.binding(authored_chain()).target == exact_node_id()
    assert result.binding(authored_literal()).literal == 7.0
    assert result.finding(invocation_rhs()).code == "SI_EXPRESSION_SOURCE_UNSUPPORTED"
    assert result.finding(alias_cycle()).code == "SI_ALIAS_CYCLE"
    assert not result.has_unbound_candidate(invocation_rhs())
```

### Changes required

**Design references:** [Exact contextualization rules](../elaborator-design/design.md#exact-contextualization-rules),
[D6-D8](../elaborator-design/design.md#d6--redefinition-precedence-is-one-ordered-candidate-model),
[Diagnostics](../elaborator-design/design.md#d10--unsupported-identity-fails-closed-through-a-fixed-diagnostic-catalog).

- [x] **Tests first:** extend the existing `test_elaboration_*.py` suites with semantic ID/edge
  assertions and order reversal where a current test passes only because iteration is friendly.
  Remove any remaining test dependence on rendered-path identity rather than preserving a
  compatibility surface.
- [x] **Fail-closed suite:** create `tests/conformance/test_elaboration_fail_closed.py` for
  invocation RHS, unsupported FORMULA terms, alias cycles, missing/dangling IDs, ambiguous contexts,
  incomparable writers, constraint evidence aggregation, and partial lenient graphs.
- [x] **Collision suite:** create `tests/conformance/test_elaboration_identity_collisions.py` for
  same-name, sanitization, expression-operand, output-port, and aggregation-root collisions.
- [x] **Population and precedence:** finish the exact-ID implementation in
  `src/sysml_codegen/elaboration/elaborate.py` for all supported node kinds and apply occurrence >
  most-specific definition > default independently of model order.
- [x] **Graph validation:** finish blocking diagnostics and projectability checks in
  `src/sysml_codegen/elaboration/{graph.py,identity.py}`. Strict/lenient changes reporting only; it
  cannot change or fabricate an edge.
- [x] **Evidence completeness:** update shared extraction evidence only where the new route needs to
  distinguish no RHS from unsupported RHS. Keep legacy shipped behavior and serialized v5 bytes
  unchanged.
- [x] **Contract stop:** keep non-finite multiplicity block-loud. If a literal override of a
  computed attribute or another shape lacks an Item-3 disposition, stop and surface it to the owner
  before implementing semantics.

### Validation

**Automated:**

- [x] Run all elaboration conformance tests in strict and lenient modes where applicable; every
  supported form has exact edges and every rejected form has its contract code.
- [x] Run focused legacy silent-failure, extraction, constraint, aggregation, and snapshot-v5 tests;
  no legacy output changes.
- [x] Run full codegen and agentic suites, ruff, mypy baseline, and `git diff --check`.

**Manual:**

- [x] Run one adversarial fixture lenient and inspect every authored RHS: each has a direct edge,
  literal, or blocking diagnostic; none becomes a clean entry-point candidate.

**What we know works after this phase:** The complete supported semantic surface builds one valid
typed graph, and malformed/unsupported identity cannot escape as apparently usable input.

---

## Phase 4 — Projection and Internal Graph Round-Trip

### Goal

Project the validated instance graph onto the complete existing `ComputationGraph` seam and prove an
internal serialized graph can reconstruct and project without live semantic resolution.

### Assumption under test

The resolved graph contains every fact needed for module wiring, entry-point classification and
groups, execution order, output aliases, constraint catalog assembly, registry rendering, and
offline projection. This is remaining bet B3 in
[the design](../elaborator-design/design.md#proven-assumptions-and-remaining-bet).

### Test stencil — write this first

```python
def test_projection_and_round_trip_need_no_semantic_lookup():
    live = elaborate_exact(load_mixed_consumers())
    projected = project(live)
    rebuilt = decode_instance_graph(encode_instance_graph(live))
    assert rebuilt == live
    assert project(rebuilt) == projected
    assert projected.fallback_entry_points == set()
    assert render_yaml(projected) == expected_yaml()
```

### Changes required

**Design references:** [D8](../elaborator-design/design.md#d8--projection-owns-strings-and-implements-the-complete-generation-seam),
[D9](../elaborator-design/design.md#d9--snapshot-payload-is-the-resolved-instance-graph),
[Projection component](../elaborator-design/design.md#component-overview), and
[Deletion Ledger](../elaborator-design/design.md#deletion-ledger).

- [x] **Projection tests first:** create `tests/conformance/test_elaboration_projection.py` covering
  all module kinds, exact producer wiring, all three entry-point classes, parameter groups,
  topological order, aliases, registry text, constraint catalog, V11 coverage, and public rendering
  collisions.
- [x] **Generation-boundary test first:** create
  `tests/conformance/test_elaboration_generation_boundary.py` and graduate the proven probe-3 YAML/
  registry assertions onto the exact graph and real templates.
- [x] **Projection implementation:** create `src/sysml_codegen/elaboration/project.py`. Use ADR-003
  helpers only after edge identity is fixed; no projection string may flow back into the graph.
- [x] **Constraint catalog seam:** add the narrow graph-driven catalog assembly needed by projection
  in `analysis/constraint_lowering.py` and/or `generation/constraint_catalog.py`, protected by
  existing legacy route tests. Do not rerun actual resolution.
- [x] **Round-trip tests first:** create
  `tests/conformance/test_elaboration_graph_roundtrip.py` for canonical UUID/ID encoding,
  expression IR, diagnostics, malformed payloads, fingerprints, and live/rebuilt projection parity.
- [x] **Internal graph codec:** create `src/sysml_codegen/snapshot/instance_graph.py` with canonical
  resolved-graph encoding/validation. Keep it unconnected to the shipped v5 loader, capture command,
  CLI, and stored fixture snapshots.
- [x] **Export boundary:** expose only the internal new-route construction/projection functions from
  `elaboration/__init__.py`; keep the public shipped pipeline entry unchanged.

### Validation

**Automated:**

- [x] Focused projection, constraint-catalog, graph-round-trip, generation, registry, and malformed-
  snapshot tests pass.
- [x] Live graph -> canonical bytes -> rebuilt graph -> projection is equal; repeated encoding is
  byte-identical.
- [x] Existing generation and snapshot-v5 suites remain byte-identical.
- [x] Full codegen and agentic suites, ruff, mypy baseline, and `git diff --check` pass.

**Manual:**

- [x] Inspect generated YAML, registry, schema/input groups, output aliases, and constraint catalog
  for the mixed-consumer and nested-constraint fixtures.
- [x] Search the graph decoder/projector for model loading, referent lookup, occurrence
  contextualization, or rendered-path parsing; none is present.

**What we know works after this phase:** The complete new front end reaches real generation, and its
resolved graph is sufficient for future snapshot v6 without changing the shipped snapshot route.

---

## Phase 5 — Dual-Run Corpus Proof and Owner Checkpoint

### Goal

Run the complete legacy and exact-ID routes independently over the corpus, classify every public
graph difference, execute the inherited contract matrix, and prove the customer-visible mutation
before Item 6 begins.

### Assumption under test

The new route implements the required semantics across the entire maintained corpus, and every
difference from legacy is either an expected collapse/fix or a surfaced defect. No compatibility
rule needs old occurrence objects inside the new route. See
[Integration Strategy](../elaborator-design/design.md#integration-strategy) and
[Validation Approach](../elaborator-design/design.md#validation-approach).

### Test stencil — write this first

```python
def test_public_mutation_reaches_exactly_one_source_fanout():
    baseline = generate_with_exact_route(source_value=default_value())
    changed = generate_with_exact_route(source_value=off_default_value())
    assert changed.public_inputs.count(source_public_name()) == 1
    assert changed.changed_consumers == expected_calc_constraint_aggregation_consumers()
    assert changed.unrelated_consumers == baseline.unrelated_consumers
```

### Changes required

**Design references:** [route isolation](../elaborator-design/design.md#integration-strategy),
[validation gates](../elaborator-design/design.md#validation-approach), and
[adversarial cases 12-14](../elaborator-design/design.md#appendix-a--required-adversarial-identity-cases).

- [x] **Internal route test first:** create an internal new-route construction entry in
  `src/sysml_codegen/orchestration/elaborated_pipeline.py`; add tests proving it is not a CLI flag,
  does not alter `build_pipeline_context`, and never consumes legacy intermediate objects.
- [x] **Diff harness:** create an internal comparator under
  `src/sysml_codegen/elaboration/diff.py` or test support. Compare modules, ports/channels, direct
  wiring, entry-point types/groups, execution order, aliases, and constraint catalog after both
  complete routes run independently.
- [x] **Contract matrix (remediation baseline: 5 reproduced failures, 7 unwritten cells, and 9
  internal-only public claims):** create
  `tests/conformance/test_elaboration_contract_matrix.py` mapping all
  29 inherited cells to exact new-route outcomes. Do not duplicate the cell definitions in
  production code.
- [x] **Public mutation:** create `tests/conformance/test_elaboration_public_mutation.py` covering
  calculation, constraint, aggregation, live projection, and relocated internal graph round-trip.
- [x] **Corpus runner and ledger:** create the repeatable corpus command and
  `.project/active/elaborator-breadth/diff-ledger.md`; classify all 37 fixture rows as
  expected-collapse, expected-fix, needs-review, or new-bug with zero unclassified rows.
- [x] **Ledger gate:** after landed code and the observed public mutation, append a resolution block
  to `product-lens.md` for `audit-F1`, `audit-F2`, and `audit-F3`. Design citations alone cannot
  resolve them.
- [x] **Owner checkpoint:** present the classified ledger, contract-matrix result, public mutation,
  exact gate counts, and remaining Item-6 deletion/cutover work. Do not begin Item 6 before owner
  approval.

### Validation

**Automated:**

- [x] All 37 fixtures have two complete route results and zero unclassified differences.
- [x] All 29 contract cells execute and are green or emit their required named diagnostic at the
  required evidence tier. Remediation baseline: 5 reproduced failures (C5, C17, C18, C21, C26),
  7 unwritten cells (C2, C3, C4, C6, C7, C14, C23), and 9 supported cells whose cited evidence
  stops at the internal graph rather than generated public output.
- [x] Public off-default mutation changes every and only the intended consumers on live and rebuilt-
  graph routes.
- [x] Legacy `build_pipeline_context`, v5 snapshot bytes, CLI behavior, and existing generated
  baselines remain unchanged before cutover.
- [x] Full codegen and agentic suites, scoped ruff, mypy baseline, and `git diff --check` pass with exact
  counts and licensed-test evidence recorded.

**Manual:**

- [x] Review every `needs-review`/`new-bug` ledger row against the Item-3 contract; unresolved rows
  block Item 5 completion.
- [x] Inspect one generated package with the off-default value and verify the single public input and
  exact fan-out at the rendered YAML/schema boundary.

**What we know after the checkpoint:** The independent exact-ID route has complete corpus coverage,
snapshot-shape evidence, and public live/rebuilt mutation proofs while legacy remains shipped and
frozen. The owner completed the row-by-row semantic review on 2026-08-09 and authorized the
remediation decisions below. Item 5 remains incomplete until those decisions are implemented, all
29 cells execute at the required evidence tier, the ledger has no unresolved rows, and the gates
rerun. Item 6 must not begin before that result is reviewed.

### Phase 5 Remediation Decisions — owner checkpoint 2026-08-09

Authority note: each item below began as an agent recommendation and was explicitly accepted by the
owner during the checkpoint walkthrough. Per the provenance rule, each remains agent-grade and is
recorded as `[AGENT] (ratified by owner, 2026-08-09)` rather than rewritten as owner-originated.

- **[AGENT] (ratified by owner, 2026-08-09) Finite modeled multiplicity:** `[count]` where the
  modeled integer value is known and finite has the same occurrence cardinality as `[4]`. Evaluate
  and expand it. Block only a genuinely unresolved or unbounded cardinality. Do not amend C17/C26
  to accommodate the current literal-token check.
- **[AGENT] (ratified by owner, 2026-08-09) C18 language boundary:** a reference to a feature that
  does not exist is rejected by SysML loading. Preserve the parser detail identifying the missing
  feature; do not duplicate language name resolution in elaboration. Amend C18's expected boundary.
- **[AGENT] (ratified by owner, 2026-08-09) Computed behavior:** `attr_expr_probe.scaled_area` and
  the nine inherited formulas on the three concrete `unresolvable_attr_probe` instances are
  modeled runtime behavior that legacy dropped. Keep the exact modules and classify both deltas as
  expected fixes. Correct audit-F15's claim that these are definition/template runtime nodes.
- **[AGENT] (ratified by owner, 2026-08-09) Public compatibility:** preserve existing parameter
  group names and generated filenames such as `design_params.json` and `toy_plant_params.json`.
  Exact semantic identity stays internal and does not require a public group rename. Preserve
  existing alias output filenames/scopes for the same reason.
- **[AGENT] (ratified by owner, 2026-08-09) Constraint inputs and defaults:** every modeled value
  referenced by an inline predicate is a real constraint input. Defaulted constraint formals remain
  visible and overridable; a supported scalar default is populated, while an unsupported default
  remains visible and unfilled rather than disappearing.
- **[AGENT] (ratified by owner, 2026-08-09) Concrete occurrence independence:** each concrete
  `cell[i]` owns its own source, calculation, and constraint even when all defaults are equal. The
  exact `constraint_multi_instance` result is an expected fix over legacy's collapsed calculation.
- **[AGENT] (ratified by owner, 2026-08-09) Public occurrence keys:** externally supplied modeled
  sources identify the concrete occurrence (`demo_plant`), not only its reusable type
  (`Toy_Plant`), so multiple instances cannot collapse.
- **[AGENT] (ratified by owner, 2026-08-09) Entry-point class:** bound modeled attributes such as
  `plant_length`, `plant_width`, `plant_unit_cost`, and `plant_budget` are `DESIGN_ATTRIBUTE`s.
  `LIBRARY_DEFAULT` remains the fallback for an unbound calculation or constraint formal.
- **[AGENT] (ratified by owner, 2026-08-09) Stable public constraint IDs:** an unchanged modeled
  constraint retains its existing public ID. Parser UUIDs remain internal; projection may block a
  genuine public collision but must not churn IDs merely because the internal authority changed.
- **[AGENT] (ratified by owner, 2026-08-09) Executable constraint profile:** numerical predicates
  remain executable. A valid non-numerical statement such as string equality is recorded as
  excluded with the existing warning; Phase 5 does not expand the certified execution profile.
- **[AGENT] (ratified by owner, 2026-08-09) Calculation redefinition:** at one occurrence, a
  redefining calculation replaces the inherited calculation. Instantiate only the most-specific
  declaration; do not render or execute both under disambiguated names.
- **[AGENT] (ratified by owner, 2026-08-09) Usage-context references:** a valid reference such as
  `analyzer::baseline_value` resolves to the concrete analyzer occurrence selected by SysML. Fix
  contextualization; a supported reference must not be reclassified as a loud unsupported form.
- **[AGENT] (ratified by owner, 2026-08-09) Acceptance evidence:** every matrix cell's evidence must
  execute. A function-name source-text check is not evidence. Supported cells must reach generated
  public behavior, including an off-default mutation where the contract requires it; internal graph
  assertions remain diagnostic tests only.
- **[AGENT] (ratified by owner, 2026-08-09) Unwritten cells:** C2, C3, C4, C6, C7, C14, and C23 are
  unfinished work, not blockers. Author their fixtures and executable public evidence before Phase
  5 completes.

### Audit-v2 Remediation Decisions — owner checkpoint 2026-08-09

Authority note: these dispositions began as the implementation agent's audit assessment and were
explicitly accepted by the owner. They remain agent-grade recommendations ratified by the owner.

- **[AGENT] (ratified by owner, 2026-08-09) audit-F20:** qualified-reference occurrence selection
  must use exact parser declaration/containment identity and fail closed when that identity cannot
  select one occurrence. Authored qualifier text may classify the written form, but may not select
  a semantic edge. The concrete failing producer shape is the deep
  `measurement_system::...::metric_value` reference; `analyzer::baseline_value` itself resolves as
  an attribute slot and does not exercise the producer-output string branch.
- **[AGENT] (ratified by owner, 2026-08-09) audit-F21:** DCS:92 is semantic-referent evidence for
  C5; `elab_matrix_c5` owns C5's generated public topology and mutation acceptance. DCS:82 is also
  supported on the valid witness: explicit `:>>` redefinitions leave one concrete `sensor.core`
  producer, and exact projection wires `ref_analysis.data_point` to its `metric_value` output. The
  former plain same-name part declarations were an invalid namespace shape, not three legitimate
  producer occurrences, and now fail `SYSML_NAMESPACE_NOT_DISTINGUISHABLE` before occurrence
  expansion. No public disambiguation or string reconstruction is approved.
- **[AGENT] (ratified by owner, 2026-08-09) audit-F22/F23:** mechanically compare the corpus ledger's
  recorded route outcomes with an actual runner result, and replace the remaining source-text
  discovery assertion with executed discovery. These are evidence-hygiene fixes, not semantic
  blockers.
- **[AGENT] (ratified by owner, 2026-08-09) audit-F24:** assert the complete public input key set
  before comparing mutation values. A C23 override of generated input JSON is the correct public
  action for an independently overridable library default; retain it and strengthen the surrounding
  topology/isolation evidence rather than relabeling it fake evidence.
- **[AGENT] (ratified by owner, 2026-08-09) audit-F25:** correct the finding: `IdentityBoundaryError`
  and `InvalidRedefinitionFamilyError` already carry `ElaborationCode`s and are converted to
  structured elaboration diagnostics. The remaining uncatalogued exceptions are
  `NonFiniteMultiplicityError` and `RecursiveContainmentError`; unify those without claiming three
  uncoded identity/redefinition paths.
- **[AGENT] (ratified by owner, 2026-08-09) audit-F26:** the live legacy compatibility oracle is
  intentional Item-5 dual-run scaffolding. Replace it with literal public-name regression evidence
  as part of the Item-6 cutover that deletes the legacy route, not as an Item-5 semantic fix.
- **[AGENT] (ratified by owner, 2026-08-09) audit-F27:** a finite constant integer expression such
  as `[2 * 2]` remains inside the recorded finite-multiplicity decision. Implement the supported
  finite evaluation or obtain an explicit owner narrowing; renaming the error alone cannot narrow
  the ratified rule. Ordered/nonunique/range shapes must receive an accurate named outcome rather
  than being mislabeled non-finite.
- **[AGENT] (ratified by owner, 2026-08-09) Gate wording:** the substantive audit-v2 gates stand,
  but the plan must record the exact selection behind the 200-test elaboration count before calling
  that count reproducible. The documented elaboration glob collected 146 tests at the audit and
  now collects 152 after the remediation tests were added.

### Phase 5 Remediation Sequence

- [x] Add failing public/contract tests for the ratified corpus decisions and split matrix states
  into executable, reproduced failure, and unwritten evidence without imperative xfails.
- [x] Fix finite modeled multiplicity plus C17/C26 aggregation mutation evidence.
- [x] Fix constraint actual/default projection, non-numerical profile admission, and stable public
  constraint rendering.
- [x] Fix most-specific calculation instantiation and usage-context occurrence resolution.
  Most-specific instantiation is verified. audit-F20's rendered-path selector is removed and
  usage-owned exact referents resolve by identity. The repaired DCS deep producer-output reference
  resolves through its exact declaration and concrete occurrence identity.
- [x] Execute the audit-v2 F20/F22–F25/F27 implementation remediation above and retain F26 for
  Item 6. The corpus runner now checks recorded outcomes, discovery executes, public mutation
  isolation checks exact key sets, multiplicity/recursion failures are coded, and finite constant
  integer expressions expand.
- [x] Obtain and record the explicit F21 fixture/contract/rendering ruling before certification.
  The corrected recommendation was ratified by the owner on 2026-08-09: DCS:82 is supported on the
  valid explicit-redefinition witness; the former plain declaration shape is invalid and blocks at
  model validation.
- [x] Preserve public group/alias names while retaining concrete occurrence keys and correct
  entry-point classes.
- [x] Author the seven missing matrix fixtures and public tests; replace source-text evidence with
  executed outcomes for all 29 cells.
- [x] Rerun the 37-fixture corpus, rewrite every classification against the ratified decisions, and
  correct the audit/product-lens findings whose premises changed. DCS now compares legacy
  `graph 5/7/0/0` with exact `graph 5/4/0/1` and is an `expected-fix`; the ledger totals are 26
  `expected-collapse` and 11 `expected-fix` with zero unresolved rows.
- [x] Run final codegen/agentic, public generation, snapshot-v5 freeze, lint, type, and diff gates;
  return to the owner checkpoint before Item 6.

**Remediation implementation note — 2026-08-09:** The first seven owner-ratified regression tests
failed before production changes and now pass. The exact walker evaluates a finite integer
multiplicity through the parser-resolved attribute declaration and applies one deep literal override
to every expanded child. Constraint projection now uses the existing executable-profile and modeled-
default authorities, keeps inline predicate sources and omitted default formals visible, excludes
non-numerical equality, and mints the established public constraint ID. Calculation population picks
the most-specific writer per feature slot. Usage-owned qualified references use their exact resolved
leaf declaration. The audit-v3 correction rejects DCS's former invalid part shape before occurrence
expansion; the repaired valid fixture resolves its one exact producer. Existing `_params` group
names, alias scopes, concrete
occurrence keys, and modeled-attribute entry classes are preserved. Focused validation: 25 passed
across aggregation, projection, graph round-trip, generation, public mutation, and remediation tests.

The matrix no longer searches test source or uses xfails. Each of its 29 cells now invokes a kept
public-route or named-diagnostic check. Every runtime cell projects both the live and relocated
instance graph, renders the public pipeline and input JSON, and applies an isolated off-default
mutation. Focused matrix validation passes 31 tests. C18 now ends at the licensed SysIDE load error
and preserves `ghost_cost` in the diagnostic, as recorded in the amended authoritative contract.

---

## Environment Setup

Use the commands and environment from `CLAUDE.md`.

- Codegen virtual environment uses editable `../agentic-mbse`; keep that checkout on the coordinated
  identity branch until the cross-repository landing/merge decision is recorded.
- Licensed SysIDE tests must collect and run. A `no live syside license` skip is a failed phase gate,
  not an acceptable green result.
- Capture a fresh pre-change baseline for both repositories before Phase 1 and record exact pytest,
  ruff, and mypy results in Implementation Notes.
- Preserve unrelated dirty worktree changes. Do not reset or rewrite existing user changes.

## Risk Management

See [design risks](../elaborator-design/design.md#potential-risks) for the full analysis.

- **Upstream identity changes:** Phase 1 is a kill gate and SysIDE 0.8.4 is pinned for the landing.
- **Cross-repository type ownership:** `agentic-mbse` exposes raw exact parser UUID facts; codegen
  wraps them in runtime semantic ID types. This preserves dependency direction and prevents a
  shared string type from becoming the authority.
- **Atomic Phase 2 is large:** tests and implementation may be developed in smaller local steps, but
  the phase is accepted/landed only when evidence, occurrence identity, graph IDs, and resolver are
  authoritative together.
- **Legacy compatibility pressure:** compare only complete public results. Never adapt old
  occurrences into the new graph or repair the legacy resolver during Item 5.
- **Null-QN forms:** use a proven stable owning-membership coordinate or fail `SI_ID_UNSTABLE`; never
  generate an identity from a name or position.
- **Projection collisions:** retain both semantic nodes internally and block before writing the
  colliding public name.
- **Hidden semantics question:** a shape not answered by the 29-cell contract stops its phase and is
  surfaced to the owner. A convenient legacy result is not a disposition.
- **Test chronology:** record red and green commands/results in this file as implementation happens.

## Hard Stop Conditions

- Phase-1 stability, referent-equality, or redefinition-endpoint probes fail.
- The new front end requires QN/name lookup, legacy occurrence adaptation, or relationship-object IDs
  to resolve a supported cell.
- A supported consumer shape cannot be represented by direct typed graph edges under the contract.
- Projection or graph reconstruction requires the live SysIDE AST to make a semantic decision (B3
  falsified).
- Legacy shipped output or snapshot v5 bytes change before the owner-approved Item-6 cutover.

## Implementation Notes

Fill these immediately during implementation. Do not mark a phase complete without its red-first
record, green gates, actual changes, issues, deviations, and commit/branch evidence.

### Phase 1 Completion

**Completed:** 2026-08-08 11:27:44 PDT

**Red-first evidence:** Before either kept gate existed, both named focused commands exited with
pytest collection errors (`file or directory not found`, zero tests collected). No production code
changed during Phase 1. The first complete agentic probe then failed on a deep-path redefinition
whose endpoints were null-QN UUIDv4 values; that test model was outside the supported stable-ID
boundary and was corrected to exercise named authored endpoints while the null-QN negative remains
explicitly covered.

**Green validation:**

- Codegen identity foundation: 4 passed, zero license-skip lines.
- Agentic raw identity contract: 3 passed, zero license-skip lines.
- Both tests relocate/reload internally and reverse file order; named and endpoint IDs remain
  stable, while null-QN and relationship IDs change as required.
- Ruff passed on both new test files; `git diff --check` passed.

**Actual changes:**

- Added `tests/conformance/test_elaboration_identity_foundation.py`.
- Added `tests/fixtures/elab_identity_collision_probe/model.sysml` because no existing kept fixture
  exposed a null-QN executable declaration.
- Added `../agentic-mbse/tests/test_sysml/test_syside_identity_contract.py` with a self-contained
  raw SysIDE model so the upstream repository does not depend on a sibling checkout.
- Appended kept-test evidence to the persisted identity probe record.

**Issues / deviations:** The first agentic fixture form confirmed that deep-path redefining
endpoints can be null-QN and unstable. It was not admitted as stable identity. The supported probe
uses named specialization endpoints; the negative boundary stays covered in codegen. No design
semantics changed.

**Commits / branches:** Coordinated uncommitted working trees on codegen `source-identity-epic`
(`6bed968`) and agentic-mbse `elaborate-first-salvage` (`65a35d7`). No commit was requested or
created at this checkpoint.

### Phase 2 Completion

**Completed:** 2026-08-08 12:07:49 PDT

**Red-first evidence:** The new codegen identity, occurrence, isolation, and vertical-slice command
first failed during collection because `identity.py`, `occurrence.py`, and the typed exports did not
exist. The extended agentic contract first produced two failures: the adapter had no `element_id`
accessor, and `feature_chain_facts` still returned the legacy tuple rather than an exact fact object.
No production implementation preceded those failures.

**Green validation:**

- New codegen Phase-2 gate: 10 passed (4 identity, 3 occurrence, 1 isolation, 2 vertical).
- Migrated elaboration suite: 73 passed with typed test queries and no production string-key index.
- Full codegen: 3230 passed, 47 skipped, 18 deselected. The net count is the 14 new Phase-1/2
  tests minus six retired static-inventory parameter cases.
- Full agentic-mbse: 1814 passed, 1 skipped, 33 deselected. The three new identity tests account for
  the increase from the 1811 baseline.
- Changed source and tests pass Ruff in both repositories. Full `src tests` Ruff remains at the
  existing repository debt baseline (360 codegen, 127 agentic); no changed file contributes an
  error. Mypy remains at the existing 72 codegen and 105 agentic errors, with zero errors in the new
  codegen elaboration package. Both locks pass `uv lock --check`.
- Snapshot-v5 bytes are unchanged, both repository `git diff --check` commands pass, and the
  Phase-1 kill probes still collect with zero license skips.
- Manual dump showed `NodeId` / `OccurrenceId` / `FeatureSlotId` keys and typed port edges;
  `rendered_names_are_metadata_only()` returned true.

**Actual changes:**

- Pinned agentic-mbse to SysIDE 0.8.4 and added the sole raw UUID accessor plus exact target,
  semantic-chain, owner, typing, and redefinition endpoint facts.
- Added frozen declaration, slot, occurrence, node, and port identity types with canonical wire
  encodings; added the independent finite occurrence walker over exact containment slots.
- Replaced the elaborator graph and resolver with typed IDs and direct edges. Names and QNs remain
  display/provenance metadata. The new route does not import the legacy occurrence authority.
- Replaced extraction semantic evidence with exact formal/referent/segment/redefinition UUIDs while
  preserving diagnostic properties and legacy snapshot bytes.
- Migrated the kept elaboration suites through `tests/helpers/elaboration_graph.py`, which converts
  fixture display descriptions to typed IDs only at test assertion boundaries.
- Updated exact-ID mocks and the AST-dispatch inventory to match the new adapter contract and the
  new FCE/FRE-only resolver functions.

**Issues / deviations:** SysIDE's flattened `usage.types` includes inherited library definitions,
so executable typing is read from the usage's owned `FeatureTyping` relationship instead of list
position. Bare constraint usages legitimately have no typed constraint definition and keep their
own exact declaration ID. Deep-path redefinition wrappers remain null-QN UUIDv4 objects; their
stable resolved endpoint participates in the slot while the wrapper ID is excluded. These are
parser-shape adaptations inside the approved exact-ID boundary, not semantic changes. Full-tree
Ruff is recorded but not repaired because its 360/127 findings predate and exceed this phase.

**Commits / branches:** Coordinated uncommitted working trees on codegen `source-identity-epic`
(`6bed968`) and agentic-mbse `elaborate-first-salvage` (`65a35d7`). They are one acceptance unit;
neither side is independently authoritative. No commit was requested or created.

### Phase 3 Completion

**Completed:** 2026-08-08 12:44:27 PDT

**Red-first evidence:** The first focused command collected the existing import-boundary tests but
failed collection for both new suites: `ElaborationDiagnosticError` and `GraphValidationError` did
not exist. After the initial diagnostic implementation, the authored fail-closed fixture produced
the old `SI_OCCURRENCE_MISSING`/clean-invocation behavior instead of the expected alias-cycle and
unsupported-expression outcomes. These failures preceded the production changes they required.

**Green validation:** 88 elaboration tests passed after the semantic changes; the focused legacy
silent-failure/extraction/constraint/aggregation/snapshot-v5 selection passed 162 tests. The full
codegen gate passed 3241 / 47 / 18 and the coordinated agentic-mbse gate remained 1814 / 1 / 33,
with zero license-skip lines in the kept licensed selections. Changed-file Ruff and both repository
`git diff --check` gates pass. Mypy remains at the accepted 72-error baseline with zero errors in
`elaboration/`; the final collision-only addition passes 3 focused tests and Ruff.

**Actual changes:** Added one diagnostic vocabulary and typed graph validation/projectability;
strict mode now rejects blocking graph diagnostics while lenient mode records the same identity
outcome. Ambiguity is distinct from absence, and the model-wide unique-leaf fallback is removed.
Value and containment precedence now use the actual subtype partial order instead of closure depth.
Alias cycles and unsupported behavior invocations in computed attributes block with named codes;
standard `sum` plurality compares the pinned SysIDE 0.8.4 declaration UUID. Added fail-closed,
collision, and precedence tests plus `elab_fail_closed_probe`; extended the display-boundary guard.

**Issues / deviations:** Shared extraction evidence already distinguishes absent RHS from unsupported
RHS, so no evidence or legacy-route change was needed. The plan's computed-attribute literal
override stop condition was not encountered; its existing loud `RuntimeError` remains untouched
pending an owner disposition. Non-finite multiplicity remains block-loud. The first full mypy run
exposed six new graph typing errors; they were fixed before completion, restoring the exact 72
baseline. No semantics deviation was taken.

**Commits / branches:** Coordinated uncommitted working trees remain on codegen
`source-identity-epic` (`6bed968`) and agentic-mbse `elaborate-first-salvage` (`65a35d7`). No commit
was requested or created.

### Phase 4 Completion

**Completed:** 2026-08-08 13:11:42 PDT

**Red-first evidence:** The new Phase-4 command initially failed during collection with three
missing boundaries: `ProjectionError`, `project`, and `snapshot.instance_graph`. Those failures
preceded the projection and codec implementations. The first round-trip run then failed on an
over-strong computed-node identity check; the decoder was corrected to validate a computed
calculation by its feature-slot identity rather than equating the slot root with the selected
writer declaration.

**Green validation:** The projection/generation/round-trip selection passes 9 tests, including
diagnostic preservation and a re-fingerprinted malformed identity. The focused projection plus
legacy constraint and snapshot-v5 gate passes 378 tests. All five concrete mixed-consumer
constraint wrappers and the report wrapper compile from the projected graph; one shared predicate
is compiled once. Full codegen passes 3253 / 47 / 18, and coordinated agentic-mbse remains
1814 / 1 / 33. Changed-file Ruff and `git diff --check` pass. Mypy reports 70 existing errors and
zero errors in `elaboration/` or `snapshot/instance_graph.py`, improving rather than exceeding the
accepted 72-error repository baseline.

**Actual changes:** Added graph-only projection for calculation, FORMULA, aggregation, constraint,
and report-aggregator modules; direct producer wiring; all entry-point classes and source groups;
topological ordering; output aliases; constraint catalog/fingerprint assembly; and public rendering
collision checks. Extended graph nodes with neutral expression IR, port metadata, compilation and
source metadata, constraint predicate/provenance fields, and structural expression-port ordinals.
Added the canonical `instance-graph/v1` codec with explicit typed identity/edge records, SHA-256
fingerprints, redundant identity validation, diagnostic preservation, and live/rebuilt projection
parity. Exported only the internal elaborate/project boundary and registered its raw-AST dispatch
site in the existing audited inventory.

**Issues / deviations:** Projection uses the existing public `ComputationGraph` and generation
models without changing their schemas or the shipped pipeline. The internal codec is deliberately
unconnected to snapshot v5. Parameter grouping is rendered from the resolved node's retained source
file; no live model lookup is needed. The first full codegen run exposed the static raw-AST dispatch
inventory increase from three to four dual-check sites. The new exact-ID collector was added to the
audited list with the required FCE-before-Operator guard, after which the full suite passed. No
semantic premise conflict or hard stop was encountered.

**Commits / branches:** Coordinated uncommitted working trees remain on codegen
`source-identity-epic` (`6bed968`) and agentic-mbse `elaborate-first-salvage` (`65a35d7`). No commit
was requested or created.

### Phase 5 Completion

**Completed:** 2026-08-09 after the owner ratified the row-by-row remediation decisions and the
corrected F21 evidence boundary. All 29 contract cells execute at their required public or
diagnostic boundary. The closed 37-fixture ledger has zero unresolved rows. Independent re-audit
owns certification; Item 6 remains out of scope and has not begun.

**Red-first evidence:** The off-default mixed-consumer mutation first failed because projected
constraint module names carry a deterministic digest suffix; the assertion was corrected to compare
the stable constraint identity. The shadowed outer-referent public mutation then failed on an
incorrect rendered module-name expectation and passed after correcting only the test. The initial
matrix/fail-closed selection exposed a missing `ElaborationError` import and then reached its honest
17-green/12-xfail result. The internal route implementation preceded its kept test run, so this phase
does not satisfy the plan's phase-wide red-first chronology. No contrary sequence is claimed.

**Green validation:** The reproducible exact-elaboration command is `.venv/bin/pytest -q
tests/unit/test_elaboration*.py tests/conformance/test_elaboration*.py`; after audit-v3 remediation
it collects and passes 154 tests, including the 31-test contract matrix and the 3/3 live ledger
comparison over all 37 fixtures. The post-remediation full licensed codegen gate passes 3309 / 47 /
18 with no xfails. The coordinated agentic-mbse gate passes 1814 / 1 / 33. Changed-file Ruff and
format pass. Mypy remains at the accepted 72-error repository baseline, with zero errors in the
exact elaboration, codec, or internal-route files. `git diff --check` passes. Snapshot-v5 and
generated-baseline paths are unchanged.

**Actual changes:** Added a complete internal exact route that does not import the shipped builder,
legacy occurrence types, or snapshot v5; a route-neutral public graph signature/diff; a repeatable
37-fixture corpus command; the classified diff ledger; the authoritative 29-cell evidence map; and
public mutation proofs across live projection, decoded internal graph projection, and generated JSON.
The mixed-consumer mutation changes one source from 42 to 47 and reaches exactly its calculation,
constraint, and FORMULA consumers. The shadow mutation changes only the loaded outer referent and
proves the nearer same-named inner attribute is not projected as the calculation input.

Audit-v2 remediation removed qualifier-text/display-path selection from leaf resolution and added an
AST guard against its return. The corpus ledger now checks a real dual run, matrix mutation evidence
checks the complete public key set, multiplicity and recursion failures use structured codes, and
finite constant integer expressions expand. Audit-v3 remediation promotes SysIDE's
`namespace-distinguishability` diagnostic only at semantic `PartUsage` sites, before the exact
walker runs. A dedicated invalid fixture proves strict and lenient paths do not build the duplicate
tree. DCS now uses explicit `:>>` for `array` and `sensor`; DCS:82 projects to its one exact core
output, and its public test asserts that edge.

**Issues / deviations:** The rerun corpus produces 26 `expected-collapse` and 11 `expected-fix`
rows, with zero `needs-review` and zero `new-bug`. Exact-ID produces 13 graphs and 24 typed errors;
legacy produces 36 graphs and one shared no-calculation-definition error. The C18 contract now
records the observed language load boundary. The audit-v3 probe found SysIDE already emits the
needed part-conflict diagnostic while agentic-mbse Level 1 intentionally ignores non-parser
diagnostics; the exact-route API therefore requires the loader validation diagnostics and promotes
the narrow part-conflict condition itself. The repaired DCS row also exposed a dormant corpus
formatter key mismatch (`aliases` versus `output_aliases`), fixed under the existing live ledger
test. Repository-wide `ruff check .` still reports unrelated historical lint debt; the complete
Phase-3–5 scope is clean.

**Commits / branches:** Coordinated uncommitted working trees remain on codegen
`source-identity-epic` (`6bed968`) and agentic-mbse `elaborate-first-salvage` (`65a35d7`). No commit
was requested or created.

---

**Status flow:** Draft -> In Progress -> Owner Checkpoint -> Complete

**Next step:** Item 5 is certified and ready for `/_my_close`. Do not begin Item 6 without the
owner's go; audit-F30/F31 dispositions remain open non-blocking work.
