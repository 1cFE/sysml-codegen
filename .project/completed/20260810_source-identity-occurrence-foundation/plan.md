# Implementation Plan: Semantic Identity and Occurrence Foundation

> **⛔ SUPERSEDED (2026-08-07). Do not resume this plan.** The Item-4 architecture was stopped
> after phases 1–2; the elaborate-first replacement is the plan of record
> (`.project/backlog/epic_elaborate_first_architecture.md`, via
> `.project/research/20260807-145336_elaborate-first-instance-graph-architecture.md`).
> The phase-1–2 implementation is preserved on branch `item4-phases12-forensic` (codegen
> `69eef3b`, agentic-mbse `9724f1d`); salvage happens only through ELABORATE-FIRST Item 2.

**Status:** Superseded — frozen after Phases 1–2 (audit: Needs Work); Phase 3 never started
**Owner:** Reid W
**Created:** 2026-08-07
**Last Updated:** 2026-08-07
**Branch:** `source-identity-epic`

## Source Documents

- [Spec](./spec.md)
- [Design](./design.md) — component responsibilities, decisions, and invariants
- [Design review](./design-review.md) — resolved findings and carry-forward boundary
- [Authoritative lifecycle contract](../../concepts/constraint-execution-authoritative-lifecycle-contract.md)

## The Point

**[OWNER]** One semantic source occurrence must become exactly one runtime source across all of its
calculation, constraint, and aggregation consumers: one public input for an externally supplied
value or one producer channel for a computed value. Item 4 must make that result derivable from the
modeled declaration and concrete occurrence before any consumer selects a runtime source. It must
not invent identity from a consumer owner, parameter name, written leaf, or current value. Source:
SOURCE-IDENTITY epic mission invariant and lifecycle invariants 55–56.

This item also repairs the C19 occurrence/definition mismatch so both consumers receive the modeled
`80.0` override. It does not fix the broader customer-visible fan-out defect. The legacy producer
key table stays in control until Item 5, and C14/C26 remain explicit current-defect pins.

## Implementation Strategy

### Phasing Rationale

Retire evidence loss before implementing identity semantics. Then prove contextual occurrence
projection independently before changing the live pipeline. Integrate C19 only after those two
foundations pass. Move snapshots last because version 6, capture, replay, and all 37 committed
snapshots must land together. The `agentic-mbse` author-diagnostic leg is independent of that
critical path and may land earlier or later, but Item 4 is incomplete until it passes.

Phases 1–4 are incremental implementation checkpoints but one atomic codegen landing unit. Do not
publish an intermediate snapshot format, an optional manifest, or a partially recaptured corpus.

### Critical Path

1. Exact extraction evidence exists for every supported route.
2. One authority projects that evidence through `PartInstanceIndex` into a complete manifest.
3. The live pipeline carries the manifest and uses it only for C19 value adaptation.
4. Snapshot v6 stores the completed manifest and sealed query transcript for exact replay.
5. Upstream diagnostics and all foundation coordinates pass.

### First Proof Point

A licensed extraction test must show that a deep calculation chain, constraint leaf, aggregation
term, and redefinition each retain the exact resolved target before mutable rewrites. The same test
must show that `_rewrite_virtual_bindings` cannot mutate that evidence. If any route lacks an exact
target, stop and extend extraction; do not add name reconstruction.

### Stop Conditions

- Stop before Phase 2 if aggregation or deep-chain target identity cannot be retained from SysIDE
  evidence without a name-based lookup.
- Stop before Phase 4 if C19 changes any non-C19 precedence outcome or if C14/C26 topology moves.
- Stop before recapture if replay can ask an owner query absent from the successful live transcript.
- Return to design review if implementation requires a second walker, a compatibility window, or
  producer-key selection based on the new identity in Item 4.

### Overall Validation Approach

- Write each phase's tests first and observe the intended red result.
- Run focused license-free tests after each change; run licensed live tests at each structural seam.
- Compare semantic structures, not values or rendered paths alone.
- Keep graph, schema, and generated-package baselines unchanged outside the reviewed C19 behavior.
- Record implementation notes and check off each phase immediately when its validation passes.

---

## Phase 1: Preserve Exact Extraction Evidence

### Goal

Capture immutable semantic evidence before chain flattening, virtual-binding rewrite, aggregation
decomposition, or snapshot AST removal. Establish distinct readiness dispositions for self-binding,
indexed-source, and deferred expression-source forms. See [Research Findings](./design.md#research-findings),
[B1/B3](./design.md#key-bets), and [Implementation Notes](./design.md#implementation-notes).

### Assumption Under Test

SysIDE's resolved referents and redefinition edges are sufficient to identify every supported
calculation, constraint, aggregation, and modeled-value-site source without using a consumer-local
name. Unsupported forms can retain honest diagnostic evidence even though generation later fails.

### Test Stencil — Write First

```python
def test_exact_reference_evidence_survives_rewrite(live_mixed_fixture):
    extracted = extract_all_source_evidence(live_mixed_fixture)
    assert extracted.calc.semantic_target == expected_calc_target
    assert extracted.constraint.semantic_target == expected_constraint_target
    assert extracted.aggregation.semantic_target == expected_aggregation_target
    before = extracted.calc.reference_evidence
    rewrite_virtual_bindings(extracted.calc_usages, extracted.hierarchy)
    assert extracted.calc.reference_evidence == before
```

### Changes Required

**Tests and fixtures — write first**

- [x] Add `tests/conformance/test_source_identity_extraction.py` with live target-fidelity,
  deep-chain, redefinition, value-site, and post-rewrite immutability cases.
- [x] Add `tests/fixtures/source_identity_mixed_consumers/` with `PROVENANCE.md`; keep one exact
  mixed route for C8, C11–C13, C15, C24, and C25 rather than duplicating it per consumer.
- [x] Extend `tests/conformance/test_source_identity_routes.py:78` to distinguish reference-derived
  literals from usage-authored literals using the new immutable evidence while retaining the current
  fan-out pins.
- [ ] Add readiness cases for exact self-binding, indexed `#(i)`, general expression source, and a
  same-named outer-feature control. Reuse `expression_binding_probe`, `self_named_binding_trap`, and
  `shadowed_reference` where their published coordinates fit.

**Extraction evidence**

- [x] Add the immutable evidence/value types needed by extraction in
  `src/sysml_codegen/analysis/source_identity.py` (new). Keep consumer coordinates out of equality
  and hashing per [D1–D3](./design.md#key-decisions).
- [x] Extend `BindingInfo` and the dispatch at
  `src/sysml_codegen/extraction/usage_extractor.py:56,768-910` to retain the exact RHS referent,
  bound formal, authored source form, and indexed/expression classification for every chain length.
- [ ] Extend aggregation extraction at
  `src/sysml_codegen/extraction/hierarchy_resolver.py:388,499` and
  `src/sysml_codegen/extraction/data_models.py:246` so each structural term position keeps its exact
  target evidence before names are rendered.
- [ ] Extend the neutral decomposition in
  `../agentic-mbse/src/agentic_mbse/sysml/aggregation.py:207` and its term facts only as needed to
  carry resolved target evidence into codegen. This dependency change belongs to the codegen
  evidence path; it is separate from Phase 5's independently landable validation leg.
- [x] Preserve modeled value-site evidence for definition defaults, occurrence `:>>` overrides, and
  usage-authored literals. Keep supplied values and provenance on their existing extraction records,
  joined by the typed coordinate defined in [D2](./design.md#key-decisions).
- [ ] Add codegen readiness screening that emits the exact D8 dispositions before registry
  construction. Do not delete the legacy rescue yet; Item 5 owns its removal.

### Validation

**Automated**

- [x] `uv run pytest tests/conformance/test_source_identity_extraction.py -q`
- [x] `uv run pytest tests/conformance/test_source_identity_routes.py tests/conformance/test_ast_dispatch_invariant.py tests/conformance/test_virtual_binding_rewrite.py -q`
- [x] Run the new live extraction cases with a SysIDE license; no required case may be skipped.
- [x] `uv run ruff check src/ tests/conformance/test_source_identity_extraction.py`
- [x] `uv run mypy src/`

**Manual**

- [x] Inspect one deep-chain record before and after virtual-binding rewrite. The semantic target,
  source form, and bound formal must be byte/field equal.
- [ ] Confirm diagnostic text may use names for context but no constructor derives identity from a
  name, current value, or consumer owner.

**What We Know Works After This Phase**

Handled calculation, constraint, and value-site routes retain immutable evidence through the tested
rewrite seam. Aggregation chain-root transport and complete unsupported-expression readiness remain
open.

---

## Phase 2: Build the Identity Authority and Contextual Occurrence Projection

### Goal

Implement the immutable identity/manifest model, typed consumer and value-site coordinates,
contextual projection, query recording, and structured aggregation scoping. See
[Architecture](./design.md#architecture), [D4–D5](./design.md#key-decisions), and
[I1–I8](./design.md#required-invariants).

### Assumption Under Test

The existing occurrence index can uniquely project supported definition- and occurrence-level
referents in consumer context. Unique, missing, and ambiguous outcomes can be decided without a
second model scan or global first-pick.

### Test Stencil — Write First

```python
def test_contextual_projection_is_shared_and_distinct(authority, evidence):
    manifest = authority.finalize(evidence)
    assert manifest.for_calc(C8).identity == manifest.for_constraint(C8).identity
    assert manifest.for_aggregation(C8).identity == manifest.for_calc(C8).identity
    assert manifest.for_occurrence("child_a").identity != manifest.for_occurrence("child_b").identity
    with pytest.raises(SourceIdentityError, match="SI_OCCURRENCE_AMBIGUOUS"):
        authority.finalize(ambiguous_definition_evidence())
```

### Changes Required

**Tests and fixtures — write first**

- [x] Add `tests/unit/test_source_identity.py` for identity equality/hash, deterministic ordering,
  duplicate coordinates, value-site joins, unique/missing/ambiguous projection, and exact failures.
- [ ] Add `tests/conformance/test_source_identity_occurrences.py` for C8–C10 and C18–C21 using
  structured occurrences rather than rendered paths.
- [x] Add focused ambiguity and genuine-miss fixtures under
  `tests/fixtures/source_identity_occurrence_ambiguity/` and
  `tests/fixtures/source_identity_absent_referent/`, each with an exact `PROVENANCE.md` key.
- [ ] Extend `tests/conformance/test_aggregation_scoping.py:89` with a legacy-versus-structured
  comparison of the exact sorted `(aggregation expression, instance_path)` set.

**Authority and occurrence substrate**

- [ ] Complete `src/sysml_codegen/analysis/source_identity.py`: immutable declaration/occurrence
  identity, typed coordinates, manifest records, projection outcomes, query recorder, deterministic
  lookup/serialization order, and D8 failure codes.
- [x] Extend `src/sysml_codegen/analysis/part_instance_index.py:321-462` only with exact reverse/path
  queries the projection needs. Keep `occurrences_of` as the shared protocol and do not add a walker.
- [x] Add tests to `tests/unit/test_part_instance_index.py:135` and
  `tests/conformance/test_part_instance_index.py:115` for any new lookup, including cycle/non-finite
  atomicity and the intended constraint-free source-query failure boundary.
- [ ] Change aggregation scoping at
  `src/sysml_codegen/orchestration/pipeline_builder.py:634-720` to keep the current extracted-calc-
  usage eligibility rule while taking structured instance paths from the authority.
- [x] Record successful occurrence owner queries by phase. Manifest finalization must not seal the
  recorder; sealing belongs to live and replay integration.

### Validation

**Automated**

- [x] `uv run pytest tests/unit/test_source_identity.py tests/unit/test_part_instance_index.py -q`
- [x] `uv run pytest tests/conformance/test_source_identity_occurrences.py tests/conformance/test_aggregation_scoping.py tests/conformance/test_part_instance_index.py -q`
- [ ] Run all license-marked occurrence and aggregation cases with SysIDE available; no required
  structural oracle may remain skipped.
- [x] `uv run ruff check src/ tests/unit/test_source_identity.py tests/conformance/test_source_identity_occurrences.py`
- [x] `uv run mypy src/`

**Manual**

- [x] Search the new authority for `split`, `rsplit`, rendered `instance_path`, and leaf-name lookup.
  Each occurrence must be diagnostic/rendering code only, never identity or projection logic.
- [ ] Compare structured aggregation output against the pre-change helper on all maintained
  aggregation fixtures before removing the dotted-path source.

**What We Know Works After This Phase**

The authority types, deterministic direct-query outcomes, recorder, and occurrence-index extensions
work on the exercised routes. Complete manifest construction and independently structured
aggregation eligibility remain open.

---

## Phase 3: Integrate the Live Route and Repair C19

### Goal

Build one authority for every live model, finalize the manifest before producer resolution, keep the
query recorder open through C19 value adaptation, attach manifest records to all producer requests,
and replace only C19's string-scope miss. See [D4/D7/D8](./design.md#key-decisions),
[Component Overview](./design.md#component-overview), and [I9–I11](./design.md#required-invariants).

### Assumption Under Test

Attaching identity evidence while the legacy key table ignores it leaves runtime topology unchanged
outside C19 and explicit fail-closed readiness behavior.

### Test Stencil — Write First

```python
def test_c19_repairs_value_without_item5_cutover(live_context, caplog):
    calc = live_context.manifest.require(C19_CALC)
    constraint = live_context.manifest.require(C19_CONSTRAINT)
    assert calc.identity == constraint.identity
    assert observed_values(live_context, calc.identity) == {80.0}
    assert "unmatched override" not in caplog.text
    assert current_topology(live_context, C14, C26) == ITEM4_DEFECT_PINS
```

### Changes Required

**Tests — write first**

- [ ] Add `tests/conformance/test_source_identity_pipeline.py` for live manifest completeness,
  recorder lifecycle, C19 calculation/constraint agreement, flat sibling preservation, and C14/C26
  current-defect topology pins.
- [ ] Replace the C19 tripwire expectation at `tests/unit/test_supplied_values.py:434` with the exact
  identity/value-site acceptance and add missing/ambiguous value-site failure cases. Retain unrelated
  precedence-ladder tests unchanged.
- [ ] Extend resolver/request tests found by `rg 'ProducerRequest\(' tests/` so every request carries
  a complete manifest record or explicit disposition. Do not weaken request presence assertions for
  test convenience.

**Live orchestration and consumers**

- [ ] Build one authority after model load in
  `src/sysml_codegen/orchestration/pipeline_builder.py:833`; use it for aggregation scoping,
  constraint preparation, identity finalization, and C19 value adaptation.
- [ ] Publish the immutable manifest and sealed union transcript on
  `src/sysml_codegen/orchestration/pipeline_context.py:75`. Seal only after all query-producing live
  phases succeed, immediately before returning the completed context.
- [ ] Update `src/sysml_codegen/resolution/supplied_values.py:425,565` to use complete manifest
  identity/value-site records only for C19. Preserve the existing precedence ladder for every other
  outcome and fail with `SI_VALUE_SITE_MISSING`/`SI_VALUE_SITE_AMBIGUOUS` at the exact join.
- [ ] Add the manifest record to `ProducerRequest` at
  `src/sysml_codegen/resolution/producer_resolution.py:100` and assert it at the public boundary
  (`:616`) without consulting it in the Item-4 key table.
- [ ] Thread the record through all five source call sites:
  `analysis/dependency_backtracker.py:597`, `analysis/constraint_lowering.py:175`, and
  `resolution/graph_builder.py:1404,1641,1664`.
- [ ] Remove no legacy resolution, VBR, rescue, backfill, or materialization route. Item 5 owns that
  deletion register and key-table cutover.

### Validation

**Automated**

- [ ] `uv run pytest tests/unit/test_supplied_values.py tests/unit/test_producer_resolution_table.py -q`
- [ ] `uv run pytest tests/conformance/test_source_identity_pipeline.py tests/conformance/test_source_identity_routes.py tests/conformance/test_shared_producer_convergence.py -q`
- [ ] Run C19 live with SysIDE and assert both consumers observe `80.0`; no required live case skips.
- [ ] `uv run pytest tests/conformance/test_factory_calc_usage.py tests/conformance/test_pipeline_module_expansion.py -q`
- [ ] `uv run ruff check src/ tests/conformance/test_source_identity_pipeline.py`
- [ ] `uv run mypy src/`

**Manual**

- [ ] Compare C14/C26 entry-point topology with the pre-phase output. It must remain the current
  defect shape and be labeled as such in the tests.
- [ ] Inspect the five request construction sites. Each must locate a manifest record by typed
  consumer coordinate; none may construct semantic identity locally.

**What We Know Works After This Phase**

The live route owns one completed identity manifest, C19 carries its modeled value to both consumers,
and Item 4 has not performed Item 5's resolver or topology cutover.

---

## Phase 4: Cut Snapshots Atomically to Version 6

### Goal

Make the manifest and sealed union query transcript load-bearing snapshot-v6 sections, replay stored
identity without semantic projection, recapture all 37 registered fixtures, and review every diff.
See [D6](./design.md#key-decisions), [Snapshot Boundary](./design.md#component-overview), and
[Snapshot Contract](./design.md#validation-approach).

### Assumption Under Test

Every owner query replay issues is present in the sealed live transcript. Constraint preparation and
C19 value adaptation issue exactly equal owner-query sets on live and replay routes.

### Test Stencil — Write First

```python
def test_v6_manifest_and_query_coverage_round_trip(live_capture):
    loaded = load_extraction_snapshot(live_capture.path)
    replay = build_pipeline_context_from_snapshot(live_capture.path)
    assert replay.source_identity_manifest == live_capture.context.source_identity_manifest
    assert replay.query_set <= live_capture.context.sealed_query_set
    assert replay.constraint_queries == live_capture.context.constraint_queries
    assert replay.c19_queries == live_capture.context.c19_queries
    assert replay.identity_projection_calls == 0
```

### Changes Required

**Tests — write first**

- [ ] Update `tests/conformance/test_snapshot_v5_gate.py` into the v6 envelope gate: v5 rejects at
  the first gate with recapture guidance, and all 37 committed snapshots must be v6.
- [ ] Add `tests/conformance/test_source_identity_snapshot.py` for required manifest shape, nested
  corruption pointers, duplicate coordinates, absent frozen queries, exact manifest parity, query
  coverage, relocated replay, and zero replay projection.
- [ ] Extend `tests/conformance/test_snapshot_constraint_parity.py:29` and
  `tests/conformance/test_extraction_snapshots.py:58` to assert identity/transcript parity, not only
  graph or deserialization success.

**Snapshot boundary**

- [ ] Bump `SNAPSHOT_FORMAT_VERSION` at `src/sysml_codegen/snapshot/__init__.py:30` from 5 to 6.
- [ ] Add deterministic manifest and union-transcript serialization to
  `src/sysml_codegen/snapshot/serializer.py:60`; keep rendered paths display-only.
- [ ] Add load-bearing shape validation and immutable reconstruction to
  `src/sysml_codegen/snapshot/loader.py:645,684`. Validate every nested declaration, path step,
  member segment, coordinate kind, disposition, and duplicate before graph code runs.
- [ ] Pass the sealed structures through `src/sysml_codegen/snapshot/capture.py:20`,
  `src/sysml_codegen/snapshot/graph_rebuild.py:39`, and
  `src/sysml_codegen/orchestration/snapshot_context.py`. Replay must use the stored manifest plus
  `FrozenOccurrenceIndex`; it must not rerun live-only aggregation scoping or identity projection.
- [ ] Update `scripts/capture_extraction_snapshots.py:197` so extraction-only fixtures also serialize
  completed diagnostic-bearing manifest records and their successful query transcript. Full
  generation from self/index/expression dispositions still fails before registry construction; the
  snapshot remains loadable for inspection.
- [ ] Recapture exactly the 37 registered `tests/fixtures/*/extraction_snapshot.json` files with the
  supported capture script. Do not hand-edit snapshots or add a v5 compatibility shim.
- [ ] Write `.project/active/source-identity-occurrence-foundation/snapshot-recapture-review.md`
  classifying each fixture's non-`captured_at` changes into version, manifest, occurrence transcript,
  or unrelated extraction drift. Any unrelated drift needs an explicit resolution before completion.

### Validation

**Automated**

- [ ] `uv run python scripts/capture_extraction_snapshots.py` with a configured SysIDE license.
- [ ] `uv run pytest tests/conformance/test_snapshot_v5_gate.py tests/conformance/test_source_identity_snapshot.py -q`
- [ ] `uv run pytest tests/conformance/test_snapshot_constraint_parity.py tests/conformance/test_snapshot_contract.py tests/conformance/test_extraction_snapshots.py tests/conformance/test_legacy_snapshot_closure.py -q`
- [ ] `uv run pytest tests/conformance/test_snapshot_generation.py tests/conformance/test_whole_tree_portability.py -q`
- [ ] `uv run ruff check src/ scripts/capture_extraction_snapshots.py tests/conformance/test_source_identity_snapshot.py`
- [ ] `uv run mypy src/`

**Manual**

- [ ] Confirm exactly 37 committed snapshot files changed and every file reports version 6.
- [ ] Review `snapshot-recapture-review.md` against the actual diff. `captured_at` churn is expected;
  an unexplained graph/schema/package or extraction-data change is not.
- [ ] Verify a relocated snapshot produces byte-equal manifest identity and does not consult checkout
  paths as semantic input.

**What We Know Works After This Phase**

Live capture and replay share one immutable identity authority, v5 fails closed, all maintained
snapshots use v6, and replay query coverage is proven rather than assumed.

---

## Phase 5: Land Author Diagnostics and Certify Item 4

### Goal

Correct the upstream self-binding oracle, add the indexed-source readiness diagnostic, prove every
SIF-11 coordinate, and run the complete repository gates. This phase follows [D9](./design.md#key-decisions)
and [Validation Approach](./design.md#validation-approach); it may land independently of Phases 1–4.

### Assumption Under Test

Exact semantic comparison can detect self-binding regardless of same-named outer features, and the
valid indexed expression form can be identified without treating it as malformed SysML or flattening
it into a supported source.

### Test Stencil — Write First

```python
def test_authoring_diagnostics_match_codegen_boundary(models):
    assert code(models.self_binding) == "L2_SELF_NAMED_BINDING"
    assert code(models.self_binding_with_outer_name) == "L2_SELF_NAMED_BINDING"
    assert code(models.owner_qualified_reference) is None
    indexed = issue(models.indexed_source)
    assert indexed.code == "L6_INDEXED_SOURCE_UNSUPPORTED"
    assert indexed.severity is Severity.ERROR
```

### Changes Required

**Upstream tests — write first**

- [ ] Replace the rescue-aware negative oracles at
  `../agentic-mbse/tests/test_validation/test_item12_checks.py:73,84` with positive self-binding
  failures plus owner-qualified and genuine non-self controls. Do not delete, skip, or xfail them.
- [ ] Add an indexed-source fixture and exact blocking assertion under
  `../agentic-mbse/tests/fixtures/item12/` and `test_item12_checks.py`.

**Upstream validation**

- [ ] Correct `check_self_named_bindings` at
  `../agentic-mbse/src/agentic_mbse/validation/level2_structure.py:358` to compare the bound formal
  with the SysIDE-resolved RHS referent. A same-named outer feature is diagnostic context only.
- [ ] Add `L6_INDEXED_SOURCE_UNSUPPORTED` to
  `../agentic-mbse/src/agentic_mbse/sysml/types.py:66` and implement the Level-6 valid-but-unsupported
  source check in `validation/level6_architecture.py`, including runner metrics.
- [ ] Keep codegen enforcement independent. Upstream validation output must not become an input to
  the source-identity authority.

**Final foundation acceptance**

- [ ] Add `tests/conformance/test_source_identity_acceptance.py` as the exact SIF-11 coordinate map.
  Reuse Phase-1/2 fixtures and point each C8–C15, C17–C21, C24–C26, and 22a assertion at its exact
  referent, occurrence, consumer, value-state, and topology key.
- [ ] Assert C14/C26 canonical pre-resolution identity while retaining their current defective public
  topology. Do not phrase Item-4 completion as “fan-out fixed.”
- [ ] Record phase completion notes below, update `.project/CURRENT_WORK.md`, and hand the completed
  plan to `my-implement`/`my-audit` without self-certifying it.

### Validation

**Automated — `agentic-mbse`**

- [ ] From `../agentic-mbse`: `uv run pytest tests/test_validation/test_item12_checks.py -q`
- [ ] From `../agentic-mbse`: `uv run pytest tests/ -m ""`
- [ ] From `../agentic-mbse`: `uv run ruff check src/ tests/`
- [ ] From `../agentic-mbse`: `uv run mypy src/`

**Automated — `sysml-codegen`**

- [ ] `uv run pytest tests/conformance/test_source_identity_acceptance.py tests/conformance/test_source_identity_routes.py -q`
- [ ] `uv run pytest tests/`
- [ ] `uv run ruff check src/`
- [ ] `uv run mypy src/`
- [ ] Run every license-marked source-identity, occurrence, C19, snapshot-capture, and relocated
  parity test with SysIDE configured; record any environment skip as incomplete, not passing.
- [ ] `git diff --check`

**Manual**

- [ ] Confirm computation-graph, parameter-schema, and generated-package baselines have no
  unreviewed diff.
- [ ] Confirm the resolver key table still ignores the new request identity and all Item-5 deletion
  targets remain present.
- [ ] Confirm `snapshot-recapture-review.md` covers all 37 snapshots and the exact query-parity gate.

**What We Know Works After This Phase**

Item 4 satisfies the spec across live and snapshot routes, authors receive the assigned actionable
diagnostics, and the identity foundation is ready for Item 5 without claiming its resolver cutover.

---

## Environment Setup

See the repository `CLAUDE.md` files for the full environment rules.

- `sysml-codegen` requires the sibling `agentic-mbse` checkout installed editable.
- Live extraction, occurrence tests, and the 37-snapshot recapture require `SYSIDE_LICENSE_KEY`.
- Phase 5 requires a writable `../agentic-mbse` checkout; sandbox/worktree permissions must cover
  that repository before implementation starts.
- Keep phases 1–4 on the same codegen branch until the v6 snapshot unit is complete.

## Risk Management

See [design risks](./design.md#potential-risks) for the full analysis.

- **Phase 1 — aggregation target loss:** prove resolved targets at extraction and stop rather than
  reconstruct from term spelling.
- **Phase 2 — contextual ambiguity:** test unique/missing/ambiguous outcomes before pipeline use and
  keep every new structural query on `PartInstanceIndex`.
- **Phase 3 — accidental Item-5 cutover:** pin all non-C19 precedence and C14/C26 topology before
  attaching identity to requests.
- **Phase 4 — transcript undercoverage and snapshot drift:** seal late, compare query sets by phase,
  recapture all 37 together, and classify every diff.
- **Phase 5 — cross-repository skew:** keep codegen independently fail-closed and treat the upstream
  validation change as an independently landable but completion-required leg.

## Implementation Notes

*Fill these during implementation. Check off a phase and add its note immediately after validation.*

### Phase 1 Completion

**Implementation pass completed:** 2026-08-07

**Audit:** Needs Work — invocation expressions bypass readiness, and aggregation terms lose the
resolved chain root needed to derive the C24 source occurrence. See [audit.md](./audit.md).

**Actual Changes:**
- `agentic-mbse` shared evidence layer: `ResolvedTargetFact` (frozen; exact referent QN,
  metatype, owner, redefinition edges) in `sysml/data_models.py`; builders
  `resolved_target_fact()` and `feature_chain_facts()` (root/leaf/segments/index detection for
  chains of any length) in `sysml/expression.py`. Neutral aggregation nodes carry root and leaf
  facts, while the shared `SumTerm`/`SingletonTerm`/`LocalTerm` currently retain only the resolved
  leaf (`sysml/aggregation.py`). `classify_redefinition` records `member_qualified_name` +
  `redefined_target_qns` (exact chained QNs for deep paths) on `RedefinitionData`
  (`sysml/hierarchy.py`). All new fields are `snapshot_exclude` — v5 wire bytes verified
  unchanged by direct serializer probe. Two dataclass field-contract pin tests updated
  (`tests/test_sysml/test_aggregation.py`, `test_hierarchy.py`); suite 1811 passed.
- Codegen: new `src/sysml_codegen/analysis/source_identity.py` (Phase-1 scope): `SourceForm`,
  frozen `SourceReferenceEvidence` (bound formal + exact referent + chain root/segments +
  written form; `is_self_binding` is exact referent-vs-formal comparison), `ValueSiteKind`,
  `ReadinessCode`/`ReadinessFinding`, `screen_source_readiness()`. `BindingInfo` gained the
  immutable `reference_evidence` field (snapshot-excluded); handled reference dispatch arms populate
  it (`usage_extractor.py` — chain evidence covers every handled chain length; `#(i)` detected via
  `IndexExpression` first operand or bare RHS, retained as `INDEXED_SOURCE`, never flattened).
  `hierarchy_resolver.py` copies term `resolved_target` through the codegen render path.
  `DesignAttributeData.raw_qualified_name` (snapshot-excluded) carries the definition-default
  value-site identity. `pipeline_builder.py` Step 5.45 emits the D8 dispositions (warnings)
  before registry construction.
- Tests: `tests/conformance/test_source_identity_extraction.py` (16 live cases, red observed
  first, then green: target fidelity for C11/C12/C13/C15/C24/C25 forms, deep-chain leaf,
  constraint-leaf parity, aggregation term targets, value-site identities, post-VBR
  immutability incl. `is`-identity, readiness dispositions with same-named-outer + shadowed
  controls). Routes file gained the live evidence-based authored-vs-reference-derived
  discriminator on fusion_tea (snapshot pins retained). New fixtures:
  `source_identity_mixed_consumers/` (all-supported, one exact route per assigned cell,
  PROVENANCE.md maps route→cell) and `source_identity_indexed_source/` (SRC-02/02a committed
  home; the Item-1 probe was throwaway).
- Gates: focused suites green (16 + 12 routes + 18 dispatch + 46 VBR + snapshots/aggregation/
  supplied-values 111); ruff clean on src + new tests; mypy exactly at the 72-error accepted
  baseline (zero new); agentic-mbse 1811 passed, changed files ruff-clean.

**Issues:**
- SysIDE QN oracle facts pinned by probe: `str(qualified_name)` quotes multi-word segments
  (`…::'Avail Plant'::availability`); the adapter's closed type map has no `Definition` or
  `IndexExpression` entries, so owner classification and index detection use metatype names.
- The parser rejects `:>>` overrides of `=`-fixed attributes ("cannot override a binding
  feature value") — overridable fixture attributes use `default`. Aggregation redefinitions
  must be authored bare (`:>> x = …`), not `attribute :>> x = …` (AttributeUsage is skipped by
  the shared classifier — same as the solar fixture's authored form).

**Deviations:**
- **Screening is emit-only in Phase 1** (log warnings; no generation halt). Surfaced for the
  Phase-3 integration: D8's "unsupported forms fail before registry construction" cannot apply
  verbatim to every SRC-01 evidence hit — fusion_tea/ife_plant/solar (the pinned defect
  fixtures and 37-snapshot corpus members) are full of self-bindings and must keep producing
  their pinned topology and Phase-4 recaptures through Item 4. The exact fail-closed
  enforcement boundary (which dispositions halt which routes, and when) needs the owner's/
  Phase-3 ruling; the dispositions themselves are now machine-checkable either way.
- `ResolvedTargetFact` and the chain-fact builders live in `agentic-mbse` (single referent
  evidence type shared by binding and aggregation extraction) instead of duplicating a
  referent record in codegen; the identity-facing types stay in `analysis/source_identity.py`
  per plan.
- Added `SourceForm.REFERENCE_FORM_UNKNOWN` as the honest disposition when the CST written
  form is unrecoverable (never silently collapsed to bare or qualified).
- C15's child leg is realized bare-renamed (an upward feature chain does not exist in KerML);
  interpretation surfaced in the fixture PROVENANCE for Phase-5 key reconciliation.
- The full-suite run tripped `REQ-EXT-06` (extraction may not import `analysis/`): the evidence
  value types moved to `extraction/source_evidence.py`, re-exported by
  `analysis/source_identity.py` (which stays the public identity surface per plan). Four codegen
  dataclass-pin tests in `tests/conformance/test_data_models.py` updated for the additive
  snapshot-excluded fields. Full suite after fix: 3146 passed / 47 skipped, zero
  `no live syside license` skip lines.

### Phase 2 Completion

**Implementation pass completed:** 2026-08-07

**Audit:** Needs Work — diagnostic authored spelling participates in identity, global uniqueness
can replace consumer context, and aggregation scoping still joins through the legacy rendered path.
The maintained-fixture comparison shares that legacy eligibility oracle and skips five new
aggregation cases. See [audit.md](./audit.md).

**Actual Changes:**
- `analysis/source_identity.py` completed: frozen `SourceDeclarationIdentity` /
  `SourceOccurrenceIdentity` (structured anchor + relative member path) / `SemanticSourceIdentity`
  (no nullable half, no consumer coordinate in equality); typed consumer coordinates
  (`CalcInputCoordinate`, `ConstraintInputCoordinate`, `AggregationTermCoordinate`) and
  `ValueSiteCoordinate`; `SourceDemandRecord` (coordinate + referent + disposition + identity,
  no supplied value) and `ValueSiteRecord`; `SourceIdentityManifest` + `build_manifest`
  (deterministic structured sort, duplicate/missing coordinates rejected);
  `OccurrenceQueryRecorder` (per-phase union transcript; finalize does not seal; record after
  seal raises); `SourceIdentityAuthority` (implements `occurrences_of` as a recorded drop-in;
  `project_target` returns exactly unique/missing/ambiguous with sorted candidates;
  `resolve_identity` raises `SI_OCCURRENCE_MISSING`/`SI_OCCURRENCE_AMBIGUOUS`; redefinition remap
  makes the redefining feature the applicable declaration — usage override first, then the
  occurrence's specialized definition, mirroring the established three-tier merge).
- `analysis/part_instance_index.py`: exact reverse queries only — `occurrences_of_definition`
  (raw-QN keyed via the held definition elements), `occurrences_of_part_usage` (raw-QN keyed via
  the held usage elements, filtered to the producing usage; same atomic cycle/non-finite raises),
  and `redefining_target_on` (exact `owned_redefinitions` comparison on the memoized producing
  usage or the occurrence's own definition). No new walker; everything rides `_structured_paths`.
- Aggregation scoping (`pipeline_builder.py`): `_scope_aggregation_expressions`/`_scope_aggregation_list`
  and the Item-10 FORMULA reroute take a `source_authority`; the legacy helper still supplies the
  extracted-calc-usage eligibility set, and each eligible instance path must match a structured
  occurrence by its rendered path; a mismatch raises `CodeGenerationError`. The occurrence rides
  on the new snapshot-excluded
  `ScopedAggregationData.occurrence`. `build_pipeline_context` builds the index + authority once
  (Step 3.4) and threads it through Steps 3.5/4.7.
- Tests: `tests/unit/test_source_identity.py` (19 license-free cases over a stub index: identity
  equality/hash/frozen, projection outcomes incl. no-anchor global ambiguity, exact failure codes,
  dispositions incl. ABSENT_REFERENT, manifest order/duplicates/missing, value-site join, recorder
  phase/seal semantics); `tests/conformance/test_source_identity_occurrences.py` (11 live cases:
  C8 distinctness, C11 calc/aggregation shared identity, C25 def/usage-leg convergence via the
  remap, C9/C10 exact ambiguity with sorted candidates, constructed-context missing, C18 load
  refusal pin, C19 structured anchor, C20 nearest-scope, C21 specialized declaration, D3
  locate-not-identify); new-lookup unit + conformance index tests incl. the constraint-free
  fail-closed boundary (recursion + non-finite raise from a pure source-identity query);
  legacy-vs-structured scoping comparison from the same legacy eligible set plus a FORMULA-reroute
  leg; five new aggregation cases skip. New fixtures `source_identity_occurrence_ambiguity/` and
  `source_identity_absent_referent/`, each with PROVENANCE.md.
- Gates: full suite 3189 passed / 52 skipped (zero license-skip lines); ruff clean; mypy exactly
  at the 72-error baseline; agentic-mbse 1811 passed; `git diff --check` clean. Manual sweep: the
  only `instance_path` use in the authority is inside an error message; no split/rsplit anywhere
  in identity or projection logic.

**Issues:**
- **C18 premise surfaced (Surfacing law):** SysIDE refuses to load a model whose aggregation term
  targets a genuinely absent feature (`reference-error` at load). The published C18
  POLICY_DIAGNOSTIC outcome is unreachable live for this authored form; the fixture pins the load
  refusal, ABSENT_REFERENT is proven at the unit level as the honest policy input, and the
  PROVENANCE flags the cell for Phase-5/owner reconciliation.
- C21 oracle: the chain through a retyped usage resolves (SysIDE) to the *base* definition's
  attribute; the specialized `:>>` declaration is recovered by the authority's redefinition remap
  from the anchor occurrence's own most-specific definition — which is what makes the C21 key's
  "redefining feature is the declaration" hold.

**Deviations:**
- `ResolvedTargetFact` gained `element_name` (structural member-path names; never derived by QN
  splitting). Two fixtures in the plan's Phase-2 list needed no new fixture beyond the two added
  (C19–C21 reuse `nested_occurrence_override_probe`, `shadowed_reference`, `spec_chain_channel`).
- The scoping bridge matches legacy dotted paths to structured occurrences by rendered-path
  equality once, at the transitional seam only; the structured occurrence (not the string) is
  what the record carries forward. The C25 def/usage-leg convergence already lands in Phase 2
  via the redefinition remap (design's "redefining feature in that context"), one phase earlier
  than strictly required.

### Phase 3 Completion

**Completed:**
**Actual Changes:**
**Issues:**
**Deviations:**

### Phase 4 Completion

**Completed:**
**Actual Changes:**
**Issues:**
**Deviations:**

### Phase 5 Completion

**Completed:**
**Actual Changes:**
**Issues:**
**Deviations:**

---

**Status:** In Progress — phases 1–2 need correction; phases 3–5 are unstarted
