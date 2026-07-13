# Implementation Plan: Concrete Constraint Lowering

**Status:** Draft
**Created:** 2026-07-12
**Last Updated:** 2026-07-12
**Epic:** CONSTRAINT-EXEC — Item 5
**Branch:** constraint-exec-epic

## Source Documents
- **Spec:** `.project/active/constraint-lowering/spec.md`
- **Design:** `.project/active/constraint-lowering/design.md` ← component details, decisions (D1–D8), invariants (INV-1..8), architecture, fixtures. **Reference it; this plan does not restate it.**
- **B1 probe evidence:** `.project/active/constraint-lowering/b1-probe-evidence.md` — the settled multi-instance semantics + working model skeleton (`probe_b1_channels.py`).
- **Proven shape:** `.project/active/spike-vertical-slice-constraint-execution/s4_lib.py` (`lower_constraints`, `targeted_graph`, `extend_graph`, `capture_constraint_facts`, `_resolve_actual_strict`, `generate_s4_package`).

## Grounding Facts (verified this session, so the implementer doesn't re-derive)

- **Where facts enter.** The neutral facts are produced by `agentic_mbse.sysml.constraint_extraction.extract_constraint_facts(model) -> ConstraintFacts` (reference: `.project/reference/agentic-mbse-landed/constraint_extraction.py:113`; schema: `constraint_facts.py`). `ConstraintFacts.usages` is the `list[ConstraintUsageFact]` lowering consumes. The design's `lower_constraints(facts, ...)` takes these usages — this call is **not yet wired** into `pipeline_builder`; today the pipeline only sweeps a drop-report manifest (`pipeline_builder.py:744`). Phase 4 adds the extraction+guard.
- **Threading seams are exactly where the spec pins them** (verified in `pipeline_builder.py`): `graph_design_attrs` finalized at Step 5.65 (`:815-827`); `group_deriver` built at Step 5.7 (`:831`); backtracker target list at Step 6 (`:840-843`); `build_computation_graph` at Step 7 (`:888-903`). No restructuring needed.
- **Registry lookups** are plain exact-match dict gets: `scoped_lookup(ScopedKey)` (`output_registry.py:186`), `alias_lookup(ScopedKey)` (`:194`). The B1-real key is dotted, design-prefix-stripped, **no occurrence index** (`the_design.c.cell.power_calc.p`).
- **Index API** (`part_instance_index.py`): construct via `build_part_instance_index(model)`; `occurrences_of(qn)` (`:291`) returns `InstanceOccurrence`s (each `.instance_path`, per-step `occurrence_index`) and **raises** `NonFiniteCardinalityError`; bulk `all_occurrences()`/`all_source_owners()` carry `blocked: dict[qn→reason]` (`AllOccurrencesResult`, `:238`).
- **Graph models** (`resolution/models.py`): `ModuleKind.CONSTRAINT` / `REPORT_AGGREGATOR` exist (`:169-170`); `PipelineModule.module_kind` required (`:193`); `calc_def_qualified_name` optional (`:198`). `ConcreteConstraint` does **not** exist yet — Phase 1 adds it here.
- **IR (de)serialization**: `serialize_expression(ir) -> str` / `parse_expression(text) -> ExpressionIR` in `agentic_mbse.sysml.expression_ir` (reference `:133,:220`).
- **Live-test pattern**: fixtures load live via `SysMLDataExtractor([FIXTURES_DIR / "name"])` under `@requires_license`; example `tests/conformance/test_part_instance_index.py`. **The syside license is present in this repo's venv this run** — live tests run here, not only the sibling env.
- **Corpus gate**: `scripts/capture_pipeline_baselines.py` regenerates; `tests/conformance/test_baselines.py` compares. Gate discipline = regenerate → timestamp-only diff check → revert (memory `byte-identity-captured_at-churn`). **Never run the snapshot-capture script for this item** (memory `byte-identity-captured_at-churn`).

## Implementation Strategy

**Phasing rationale — de-risk the data contract and the resolver before touching the shared pipeline.** Phases 1–3 are independently unit-testable *offline* (hand-built `ConstraintUsageFact`s + live fixtures for expansion) and never touch the byte-identity-sensitive calc path. Phase 4 is the only phase that edits `pipeline_builder` and `dependency_backtracker`; it carries the corpus-regression risk (R2) and gets its own mini byte-identity check the moment the shared switch is extracted. Phase 5 proves the four success criteria end-to-end and runs the full corpus gate.

**Critical path:** ConcreteConstraint model + `constraint_id` minter (Phase 1) → strict resolver seam with the unreachable-fallback switch (Phase 2) → four-kind expansion + blocked-owner error + multi-instance binding (Phase 3) → three threading points wired, roots-before-pruning (Phase 4) → fixtures + corpus gate (Phase 5).

**First proof point:** Phase 1's offline determinism test — the same canonical tuple mints a byte-identical `constraint_id` across repeated calls, and two anonymous asserts on one instance get distinct IDs via `LocationFact`. This collapses the D3/INV-4 encoding risk with zero model dependency.

**De-risk-first note (design Next-Stage Handoff):** the one transform the whole resolver depends on is occurrence-scope→`ScopedKey` against the registry's real dotted, de-indexed keying. It is exercised first inside Phase 2 (unit) and pinned live in Phase 3 (`constraint_multi_instance`). B1 is already probe-settled — no blocking spike remains.

**Validation approach:** every phase starts with tests; offline unit tests where possible; `@requires_license` live tests for expansion/threading; the corpus gate is the final regression backstop.

---

## Phase 1: `ConcreteConstraint` model + `constraint_id` minting + serialization

### Goal
Land the serializable data contract (D4, D5-IR) and the deterministic `constraint_id` minter (D3, N1) with offline unit tests. Nothing here touches the pipeline. Item 7/8 import these types, so pinning the shape first de-risks every later phase.

### Assumption Under Test
`constraint_id` is deterministic and collision-visible from a canonical tuple, and `ConcreteConstraint` round-trips through Pydantic JSON with `predicate_ir` as a plain serialized string (no `arbitrary_types_allowed`) — INV-4, D5-IR.

### Test Stencil (Write This First)
```python
# tests/unit/test_concrete_constraint_model.py
def test_constraint_id_deterministic_and_collision_distinct():
    tup = ("Design__c__cell__nonneg", "Design__c__cell", "assert", False)
    a = mint_constraint_id(instance_path="Design__c__cell", source_local="nonneg", tuple_=tup)
    b = mint_constraint_id(instance_path="Design__c__cell", source_local="nonneg", tuple_=tup)
    assert a == b                       # byte-identical across calls
    assert a.split("__")[-1] == a.split("__")[-1] and len(a.rsplit("__",1)[1]) == 16  # sha256[:16]
    # two anonymous asserts on one instance -> LocationFact disambiguates
    anon1 = mint_constraint_id(instance_path="Design__c", source_local="anon", tuple_=("file:10:2", "Design__c", "assert", False))
    anon2 = mint_constraint_id(instance_path="Design__c", source_local="anon", tuple_=("file:20:2", "Design__c", "assert", False))
    assert anon1 != anon2

def test_concrete_constraint_json_roundtrip():
    cc = ConcreteConstraint(constraint_id="X__a__deadbeefdeadbeef", predicate_ir=serialize_expression(ir), eligible=True, ...)
    assert ConcreteConstraint.model_validate_json(cc.model_dump_json()) == cc

def test_unassessed_shape_carries_kind_and_no_node():
    cc = ConcreteConstraint(..., eligible=False)   # D7
    assert cc.eligible is False and cc.evaluation_channel is None
```

### Changes Required

**See design.md for:** `#key-decisions` (D3, D4, D5-IR), `#required-invariants` (INV-4, INV-8), `#implementation-notes` (canonical-tuple stability, `sha256[:16]` width N1), `#appendix-a` (`constraint_id` encoding row).

- [x] **`resolution/models.py`** — add `ConcreteConstraintInput` (resolution-tagged `module_output` | `design_attribute` | `modeled_default`; for `module_output` carries the recorded `bound_channel`, INV-3) and `ConcreteConstraint` (`constraint_id`, source identity/form, owner-instance identity, `membership_kind`, `polarity`/`expected_value`, `predicate_ir: str` per D5-IR, `inputs: list[ConcreteConstraintInput]`, `evaluation_channel: str | None`, `eligible: bool`, optional `tracking_key`). Pydantic scalar/str fields only — **no** `arbitrary_types_allowed`.
- [x] **`analysis/constraint_lowering.py`** (NEW) — `mint_constraint_id(...)`: prefix `{instance_path}__{source_local}` sanitized (`source_local` = usage simple name, else `anon`) + `__` + `sha256[:16]` of the canonical tuple `(source_local_full, owner_instance_identity, membership_kind, polarity)`. Canonicalize with `json.dumps(sort_keys=True, separators=(",", ":"))` (the same idiom `expression_ir._canonical_json` uses; this repo has no pre-existing local helper of that name — R3). Added `assert_unique_constraint_ids(concrete)` raising `CodeGenerationError` (the repo's existing generation-error class — no new exception type invented) on any duplicate `constraint_id` (D3, INV-4).
- [x] **`tests/unit/test_concrete_constraint_model.py`** (NEW) — 5 tests: determinism + collision-distinct IDs, JSON round-trip, unassessed shape, duplicate-raises, distinct-passes.

### Validation
**Automated:**
- [x] `uv run pytest tests/unit/test_concrete_constraint_model.py` → 5 passed
- [x] `uv run mypy src/` → 77 errors (baseline unchanged, none in new files)
- [x] `uv run ruff check src/` → clean

**What We Know Works After This Phase:** the catalog record shape, deterministic collision-checked IDs, and JSON round-trip — the contract Items 7/8 import. No pipeline touched.

---

## Phase 2: Strict resolver seam + shared terminal-disposition switch

### Goal
Implement the ordered strict resolution procedure (`scoped_lookup` → `alias_lookup` → design-attr-by-QN → terminal) and extract the single terminal-disposition switch (D1) so the fallback-synthesis branch is **physically unreachable** in strict mode (INV-2). Includes the occurrence-scope→`ScopedKey` transform (the de-risk-first target).

### Assumption Under Test
The strict ladder covers every rung an in-profile actual hits (B4), and the shared switch makes fallback synthesis unreachable when `strict=True` (INV-2, D1). The occurrence-scoped key is tried first and, when only the de-indexed channel exists, that channel is bound and recorded (`bound_channel`) — not an error (design Implementation Notes retraction).

### Test Stencil (Write This First)
```python
# tests/unit/test_constraint_resolver.py  (offline: hand-built facts + a stub OutputRegistry)
def test_ladder_scoped_then_alias_then_design_attr():
    # scoped hit wins; on miss, alias hit; on miss, design-attr mint; else terminal
    ...
def test_occurrence_key_first_then_deindexed_shared_binding():
    # registry holds only "the_design.c.cell.power_calc.p"; occurrence key "...cell[0]..." misses
    inp = resolve_actual(actual, occ_scope="the_design.c.cell[0]", registry=reg, strict=True)
    assert inp.resolution == "module_output"
    assert inp.bound_channel == "MultiChan__the_design__c__cell__power_calc__p"   # recorded, INV-3
def test_strict_terminal_raises_never_synthesizes():
    with pytest.raises(GenerationError) as e:
        resolve_actual(unresolvable_actual, ..., strict=True)
    assert "unresolvable_actual_name" in str(e.value)   # names the actual, INV-2
def test_switch_shared_lenient_path_still_synthesizes():
    # same terminal switch, strict=False -> synthesizes fallback EP (calc path unchanged)
    ...
```

### Changes Required

**See design.md for:** `#the-resolver-seam-p1-heart` (steps 1a–1d, 2, 3), `#key-decisions` (D1 + amendment + surfacing note), `#key-bets` (B4), `#required-invariants` (INV-2, INV-3, INV-8), `#implementation-notes` (occurrence-scope→ScopedKey, the retraction).

- [ ] **`analysis/constraint_lowering.py`** — `resolve_actual(actual, occ_scope, registry, design_attr_index, *, strict) -> ConcreteConstraintInput`: ordered ladder per design §Resolver-seam; occurrence→`ScopedKey` transform (strip design-root prefix, join by `.`; try `[i]` key first, then de-indexed) recording `bound_channel`; nullable-fact guard (INV-8: `None` `is_negated`/`membership_kind` → generation error naming field+usage). Design-attr mint keyed by real QN, deduped by QN (INV-5, F4-safe).
- [ ] **Terminal-disposition switch (D1).** Extract the one divergent step out of `_resolve_binding_via_registry` (`dependency_backtracker.py:594-604`) into a small shared helper parameterized by `strict`: `strict=False` synthesizes `{usage_qn}__{param}` fallback EP (existing behavior, byte-identical); `strict=True` raises naming the actual. Backtracker Step 4 calls it with `strict=False`; lowering's terminal calls with `strict=True`. **Do not touch the backtracker's ladder rungs above Step 4** (D1 rejected-alternative; R2).
- [ ] **`tests/unit/test_constraint_resolver.py`** (NEW) — stencil above, all four ladder rungs, both switch modes, nullable guard.

### Validation
**Automated:**
- [ ] `uv run pytest tests/unit/test_constraint_resolver.py` → pass
- [ ] **Mini byte-identity check on the extracted switch (R2, do this the moment the switch lands):** regenerate the corpus (`scripts/capture_pipeline_baselines.py` against fixtures), confirm **only timestamps** differ, then **revert** the regenerated bytes (memory `byte-identity-captured_at-churn`). The backtracker's lenient path must be byte-identical to pre-extraction.
- [ ] `uv run pytest tests/unit/test_dependency_backtracker.py` → no regressions
- [ ] `uv run mypy src/` / `ruff check src/` → clean

**What We Know Works After This Phase:** the strict ladder and the unreachable-fallback switch, verified structurally and by the mini corpus check — before any expansion or pipeline wiring.

---

## Phase 3: Expansion — four-kind dispatch, blocked-owner error, multi-instance

### Goal
Implement `lower_constraints(facts, occ_index, registry, graph_design_attrs, group_deriver, *, strict=True) -> list[ConcreteConstraint]`: expand per owner-kind (all four landed values), select the effective predicate per source-form, resolve each formal via Phase 2, mint IDs. Prove the multi-instance and blocked-owner surfaces S4 never ran.

### Assumption Under Test
Expansion dispatches on `owning_definition.kind` (D5, B2): `part_def` → `occurrences_of` (N per occurrence, own id/entry/evaluation channel, INV-3); `calc_def` → per calc usage; `package` → once; `requirement_def`/out-of-profile → `unassessed` (D7, eligible=False), never dropped (INV-1). A blocked constraint-owning def → **named generation error**, never a skip (spec `[HARD]`; design Blocked-owner surfacing).

### Test Stencil (Write This First)
```python
# tests/conformance/test_constraint_lowering.py  (@requires_license, live fixtures)
@requires_license
def test_multi_instance_three_ids_three_channels_shared_binding(constraint_multi_instance_model):
    concrete = lower_constraints(facts, occ_index, registry, gda, deriver)
    assert len({c.constraint_id for c in concrete}) == 3
    assert len({c.evaluation_channel for c in concrete}) == 3
    # B1-settled: each entry records the shared de-indexed producer binding (not 3 distinct)
    bound = {inp.bound_channel for c in concrete for inp in c.inputs if inp.resolution=="module_output"}
    assert len(bound) == 1

@requires_license
def test_blocked_owner_named_generation_error(constraint_blocked_owner_model):
    with pytest.raises(GenerationError) as e:
        lower_constraints(...)
    assert "<owner>" in str(e.value) and "<feature>" in str(e.value)   # never a skip

@requires_license
def test_inline_source_form_selects_usage_predicate(constraint_inline_model):
    concrete = lower_constraints(...)
    assert concrete[0].predicate_ir == serialize_expression(usage_predicate_ir)

def test_requirement_def_owner_cataloged_unassessed():   # offline hand-built fact
    cc = lower_constraints([req_def_owned_fact], ...)[0]
    assert cc.eligible is False and cc.evaluation_channel is None
```

### Changes Required

**See design.md for:** `#core-concept` (two orthogonal axes), `#key-decisions` (D5, D5-IR, D6, D7), `#the-resolver-seam-p1-heart` (predicate selection, blocked-owner surfacing), `#key-bets` (B2), `#required-invariants` (INV-1, INV-3), `#appendix-b` (fixtures).

- [ ] **`analysis/constraint_lowering.py`** — `lower_constraints(...)`: (1) expand on `owner.owning_definition.kind` — `part_def`→`occ_index.occurrences_of(owner_qn)` (per-owner call raises `NonFiniteCardinalityError`; catch → named generation error with owner+feature), `calc_def`→existing calc-usage discovery, `package`→once, `requirement_def`/other→`unassessed`; (2) select predicate via `source.effective_predicate_source` (`inline`→`usage.predicate`, `definition_typed`→`ConstraintDefinitionFact.predicate`), serialize the *effective* IR (D5-IR); (3) resolve each formal via Phase 2 `resolve_actual`; (4) mint id, set `evaluation_channel`; (5) sort catalog by `constraint_id` (INV-4); (6) `_assert_unique_ids`.
- [ ] **Fixtures (NEW)** — `tests/fixtures/constraint_multi_instance/` (per design Appendix B + `probe_b1_channels.py` skeleton: `Cell{power_calc{out p}}`; `Container{part cell:Cell[3]; assert constraint <bound>(cell.power_calc.p)}`; **package-level design instance** `part def Design{part c:Container;}`), `tests/fixtures/constraint_inline/` (assert owning predicate inline; single instance), `tests/fixtures/constraint_blocked_owner/` (MF2: constraint-owning def reached through non-finite multiplicity `[*]`/parameterized/ranged; keep blocked leaf a disjoint type per design model-shape note). Each with a `PROVENANCE.md`.
- [ ] **`tests/conformance/test_constraint_lowering.py`** (NEW) — stencil above; add offline `requirement_def`-unassessed + `package`-owned single-expand cases with hand-built facts.

### Validation
**Automated:**
- [ ] `uv run pytest tests/conformance/test_constraint_lowering.py` → pass (live tests run in this venv)
- [ ] `uv run mypy src/` / `ruff check src/` → clean

**Manual:**
- [ ] Load `constraint_multi_instance` and confirm `occurrences_of` returns 3 and the de-indexed scoped key is the only registry hit (matches `b1-probe-evidence.md`).

**What We Know Works After This Phase:** `lower_constraints` produces the correct catalog for all four owner-kinds, multi-instance siblings with recorded shared bindings, inline predicate selection, and the blocked-owner error — all without touching `pipeline_builder`.

---

## Phase 4: Threading into `build_pipeline_context` + roots-before-pruning + P3 extension

### Goal
Wire the three guarded threading points (P1 resolve, P2 inject roots, P3 extend) into `pipeline_builder`, extract facts via `extract_constraint_facts`, and add `extend_graph_with_constraints`. Guarded so P1–P3 no-op when no constraint facts are admitted (INV-7).

### Assumption Under Test
The three insertions are purely additive (spec `[HARD]` phase placement); resolved input channels join the Step-6 roots via `_find_usage_for_channel` **before** pruning (spec Roots-before-pruning, S4-proven); the extended graph passes `_validate_channel_references` + zero V11 uncovered params (INV-6); and when nothing lowers, the corpus is byte-identical (INV-7).

### Test Stencil (Write This First)
```python
# tests/conformance/test_constraint_pipeline_threading.py  (@requires_license)
@requires_license
def test_roots_before_pruning_retains_producer(wi014_toy_model):
    # include_all=False: control prunes cost_calc; lowered run retains it ONLY via constraint root
    control = build_pipeline_context([wi014], include_all=False)          # no lowering path hit? see note
    assert "cost_calc" not in {m.name for m in control.computation_graph.modules}   # S4 control
    lowered = build_pipeline_context([wi014_with_assert], include_all=False)
    assert "cost_calc" in {m.name for m in lowered.computation_graph.modules}

@requires_license
def test_extended_graph_passes_v11_and_channel_refs(constraint_multi_instance_model):
    ctx = build_pipeline_context([multi_instance], include_all=True)
    # +3 CONSTRAINT nodes, +1 REPORT_AGGREGATOR, minted EPs QN-deduped
    assert sum(m.module_kind==ModuleKind.CONSTRAINT for m in ctx.computation_graph.modules) == 3
    # V11 + channel-ref validation already run inside build; assert zero uncovered
```

### Changes Required

**See design.md for:** `#architecture` (P1/P2/P3 diagram), `#implementation-notes` (P3 mirrors `s4_lib.py:487-525`, reuse the Step-5.7 `group_deriver` N3, reuse `_find_usage_for_channel` unchanged, guard on presence), `#required-invariants` (INV-5, INV-6, INV-7), `#validation-approach` (S4 reproduction under `include_all=False`).

- [ ] **`orchestration/pipeline_builder.py`** —
  - New step (~after Step 2.5, `:744`): `constraint_facts = extract_constraint_facts(extractor.model)`; filter to the executable-profile assert usages; if empty, skip all of P1–P3 (INV-7 guard).
  - **P1** after Step 5.7 (`:831`): `concrete = lower_constraints(facts, occ_index, output_registry, graph_design_attrs, group_deriver)` where `occ_index = build_part_instance_index(extractor.model)`.
  - **P2** at Step 6 (`:840`): append each `module_output`-resolved input channel to the `find_required_modules` target list via `_find_usage_for_channel` (`dependency_backtracker.py:466`, unchanged), **before pruning**.
  - **P3** after Step 7 (`:888-903`): `extend_graph_with_constraints(computation_graph, concrete, group_deriver)` → +1 CONSTRAINT node per concrete (own evaluation channel), +1 REPORT_AGGREGATOR, mint DESIGN_ATTRIBUTE EPs (QN-keyed, QN-deduped, placed in derived groups; reuse the existing deriver, N3), re-run `_validate_channel_references` + `collect_uncovered_params`.
  - Thread `concrete` / constraint data onto `PipelineContext` (for tests to assert `ConcreteConstraint` records until Item 7's catalog runtime exists, D7).
- [ ] **`analysis/constraint_lowering.py`** — `extend_graph_with_constraints(graph, concrete, group_deriver) -> ComputationGraph` (P3 body; mirror `s4_lib.py` `extend_graph`, `:475-570`; sort params by QN, groups by name for determinism).
- [ ] **`tests/conformance/test_constraint_pipeline_threading.py`** (NEW) — stencil above. Note: the `wi014_toy` reproduction needs an assert-carrying variant; if `wi014_toy` has no assert, add the assert to the fixture copy used for the lowered run per design `#validation-approach` (S4's model).

### Validation
**Automated:**
- [ ] `uv run pytest tests/conformance/test_constraint_pipeline_threading.py` → pass
- [ ] `uv run pytest tests/` → full suite, no regressions
- [ ] `uv run mypy src/` / `ruff check src/` → clean

**What We Know Works After This Phase:** end-to-end lowering inside the real pipeline — roots-before-pruning retention (S4 criterion), the extended graph passing V11 + channel-ref validation, and the inert guard when no constraints are present.

---

## Phase 5: Success-criteria fixtures locked + corpus byte-identity gate

### Goal
Turn the six spec Success Criteria into committed, asserting tests, and prove the full corpus regenerates byte-identically (INV-7, spec Byte-identity discipline). This is the acceptance phase — no new production logic, only test assertions + the gate.

### Assumption Under Test
All six success criteria hold on committed fixtures, and the existing corpus (no constraints admitted) is byte-identical under the established gate.

### Test Stencil (Write This First)
```python
# Consolidate/complete the criterion assertions (some already written in Phases 3-4):
#  1. S4 reproduction (wi014_toy, include_all=False) — control prunes, lowered retains via root
#  2. Strict resolution — V11 + channel-refs pass; unresolvable actual -> GenerationError naming it, no synth EP
#  3. Deterministic identity — constraint_ids + catalog ordering byte-identical across two live loads
#  4. Corpus byte-identity — see gate below
#  5. Multi-instance — 3 ids / 3 channels / recorded shared binding (constraint_multi_instance)
#  6. Inline — inline-form assertion lowers selecting usage predicate (constraint_inline)
def test_determinism_repeated_live_load(constraint_multi_instance_model):
    a = [c.constraint_id for c in lower_constraints(...)]
    b = [c.constraint_id for c in lower_constraints(...)]   # fresh load
    assert a == b
```

### Changes Required

**See design.md for:** `#validation-approach` (all six bullets + inheritance cross-check), `#success-criteria` mapping (spec), `#appendix-b` (fixture roles + `instance_index_probe` oracle-must-not-move).

- [ ] **Strict-resolution probe** — a committed unresolvable-actual case asserting `GenerationError` names the actual and **no** synthesized EP appears (spec S2).
- [ ] **Determinism test** — `constraint_id`s + catalog ordering byte-identical across two fresh live loads (spec S3; stencil above).
- [ ] **Inheritance cross-check** — `instance_index_probe`'s inherited `[3]` assert expands correctly; **assert its Item-4 oracle count is unchanged** (design Appendix B; must-not-move).
- [ ] **Corpus byte-identity gate** — regenerate the full fixture corpus, run the **timestamp-only diff check**, then **revert** (memory `byte-identity-captured_at-churn`). **Do not run the snapshot-capture script.** Confirm `tests/conformance/test_baselines.py` green.

### Validation
**Automated:**
- [ ] `uv run pytest tests/conformance/ tests/unit/` → all six criteria green
- [ ] `uv run pytest tests/conformance/test_baselines.py` → corpus green
- [ ] Corpus regenerate → timestamp-only diff → revert → clean `git status` (only the new fixtures/tests staged)

**What We Know Works After This Phase:** the epic acceptance bar (first four criteria) plus the two new surfaces (multi-instance, inline), with the corpus proven inert.

---

## Environment Setup

**See CLAUDE.md for full environment rules.** Key points for this item:
- Live tests run in **this repo's venv** (syside license present this run — verified). `@requires_license` tests execute here; they skip in an unlicensed venv.
- Corpus gate: regenerate → **timestamp-only diff** → **revert**. Never run the snapshot-capture script for this item (memory `byte-identity-captured_at-churn`).
- **Do not `git commit`** — the orchestrator commits.
- agentic-mbse (the `extract_constraint_facts` / `expression_ir` source) is at `/home/reid/1cfe/agentic-mbse`, outside this sandbox; the reference copies under `.project/reference/agentic-mbse-landed/` mirror the landed APIs (memory `agentic-mbse-repo-path`).

## Risk Management

**See `design.md#potential-risks` (R1–R5).** Phase-specific mitigations:
- **Phase 1 (R3):** canonicalize the ID tuple with `_canonical_json` (sort_keys/fixed separators); `sha256[:16]` (N1). Determinism test is the first proof point.
- **Phase 2 (R2, R5):** extract only the terminal branch of the backtracker (D1); run the **mini byte-identity check** the moment the switch lands, before proceeding. `alias_lookup` in the ladder closes the B4 gap (R5).
- **Phase 3 (R1):** the occurrence→`ScopedKey` transform is pinned live against `constraint_multi_instance`; assert the recorded shared binding, not three distinct producer channels (B1-settled).
- **Phase 4 (R2, R4):** guard all three call-sites on presence of constraint facts (INV-7); `constraint_inline` exercises inline scope-binding (R4).
- **Phase 5 (R2):** the full corpus gate is the regression backstop; `instance_index_probe`'s Item-4 oracle count must not move.

## Implementation Notes

[TO BE FILLED DURING IMPLEMENTATION — leave empty now]

### Phase 1 Completion
**Completed:** 2026-07-12
**Changes Made:**
- `resolution/models.py`: added `ConstraintInputResolution`, `ConcreteConstraintInput`,
  `ConcreteConstraint` (plain str/scalar Pydantic fields, no `arbitrary_types_allowed`);
  exported in `__all__` alongside `ModuleKind` (was missing from `__all__` before this item).
- `analysis/constraint_lowering.py` (NEW): `mint_constraint_id()`, `assert_unique_constraint_ids()`.
- `tests/unit/test_concrete_constraint_model.py` (NEW): 5 tests, all passing.

**Issues Encountered:** None.

**Deviations from Plan:**
- Used the repo's existing `CodeGenerationError` (`orchestration/pipeline_context.py`) instead
  of inventing a new `GenerationError` type — the plan's test stencils used `GenerationError`
  as a placeholder name; the repo already has exactly this class and every other item (Item 6,
  etc.) raises it for generation-time failures, so reusing it keeps one error type across the
  codebase rather than two doing the same job.
- No `_canonical_json` helper existed in this repo (design's R3 note assumed one); used
  `json.dumps(sort_keys=True, separators=(",", ":"))` inline, matching the idiom the landed
  `expression_ir._canonical_json` (agentic-mbse) already uses.

### Phase 2 Completion
### Phase 3 Completion
### Phase 4 Completion
### Phase 5 Completion

---

**Status:** Draft → In Progress → Complete
