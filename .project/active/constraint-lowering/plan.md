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

- [x] **`analysis/constraint_lowering.py`** — `resolve_actual(*, reference, occ_scope, formal_name, usage_qualified_name, registry, design_attr_by_qn) -> ConcreteConstraintInput`: ordered ladder per design §Resolver-seam; `occurrence_scope()` transform (strip design-root prefix, join by `.`, keep `[i]` attached to its segment) + `_deindexed_scope()` strips brackets for the B1 fallback; both `scoped_lookup` and `alias_lookup` tried occ-key-first-then-deindexed, recording `bound_channel`. `guard_nullable_facts()` implements INV-8. Design-attr mint keyed by the reference's real target QN (INV-5, F4-safe) — no separate dedup needed here since Phase 3/4 dedupe against existing group params by QN (S4 pattern).
- [x] **Terminal-disposition switch (D1).** Extracted the divergent step out of `_resolve_binding_via_registry` (was `dependency_backtracker.py:594-604`) into module-level `terminal_disposition(*, usage_qualified_name, param_name, source_path, strict)` in the same file: `strict=False` synthesizes `{usage_qn}__{param}` fallback EP (byte-identical to the inline code it replaced — same warning/debug lines, same QN construction); `strict=True` raises `CodeGenerationError` naming the actual. Backtracker Step 4 calls it with `strict=False` (only call-site change: the inline block became a call). `resolve_actual`'s terminal step always calls `strict=True` — the `strict` toggle is not threaded through `resolve_actual` as a parameter (would make it return two structurally different things from one signature; the switch itself supports both dispositions, each caller hardcodes which one fits its own semantics). **The backtracker's ladder rungs above Step 4 are untouched** (D1 rejected-alternative; R2) — the diff to `dependency_backtracker.py` is exactly the Step-4 block replaced by a 5-line call plus the new module-level function.
- [x] **`tests/unit/test_constraint_resolver.py`** (NEW) — 11 tests: occurrence-scope transform, scoped-hit, occ-key-then-deindexed shared binding (B1), alias fallback, design-attribute fallback, strict-raises-naming-actual, switch lenient-still-synthesizes, switch strict-raises, nullable guard (3 cases).

### Validation
**Automated:**
- [x] `uv run pytest tests/unit/test_constraint_resolver.py` → 11 passed
- [x] **Mini byte-identity check on the extracted switch (R2):** regenerated the corpus via `scripts/capture_pipeline_baselines.py` (10 fixtures) immediately after landing the switch. `git diff --stat -- tests/fixtures` and `git diff -- tests/fixtures` were both **empty** — not even a timestamp changed (these baselines carry no timestamp field), so nothing needed reverting. The backtracker's lenient path is byte-identical to pre-extraction.
- [x] `uv run pytest tests/unit/test_dependency_backtracker.py` → 6 passed, no regressions
- [x] `uv run pytest tests/` → 2178 passed, 4 skipped (full suite, no regressions)
- [x] `uv run mypy src/` → 76 errors (baseline 77; improved by 1, unrelated pre-existing error resolved incidentally — none in touched files)
- [x] `uv run ruff check src/` → clean

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

- [x] **`analysis/constraint_lowering.py`** — `lower_constraints(facts, *, occ_index, registry, design_attrs, calc_usages) -> list[ConcreteConstraint]`: `_expand_owner_instances` dispatches on `owner.owning_definition.kind` — `part_def`→`occ_index.occurrences_of(owner_qn)` (catches `NonFiniteCardinalityError` → named `CodeGenerationError` with owner+feature), `calc_def`→matches `CalcUsageData.calc_def_qualified_name`, `package`→once at top scope, `requirement_def`/other→`unassessed` (D7, handled inline in `lower_constraints`, no expansion attempted). Predicate: **no selection logic needed** — `ConstraintUsageFact.predicate` already carries the source-form-selected effective predicate (extraction resolves it at fact-construction time, `constraint_extraction.py::_usage_fact`); Item 5 only serializes it (D5-IR) via `serialize_expression`. Each formal resolved via Phase 2 `resolve_actual`; `constraint_id` minted per instance; catalog sorted + `assert_unique_constraint_ids` run before returning.
- [x] **Fixtures (NEW)** — `tests/fixtures/constraint_multi_instance/`, `tests/fixtures/constraint_inline/`, `tests/fixtures/constraint_blocked_owner/`, each with a `PROVENANCE.md`. See Phase 3 Implementation Notes for the `constraint_multi_instance` deviation from the Appendix B prose sketch (assert nested in `Cell`, not `Container`) and the trivial calc-def additions needed to satisfy `build_pipeline_context`'s Step-2 requirement.
- [x] **`tests/conformance/test_constraint_lowering.py`** (NEW) — 6 tests: multi-instance (3 IDs/channels/shared binding), blocked-owner generation error (2 tests), inline predicate selection, offline `requirement_def`-unassessed, offline `package`-owned single-expand.

### Validation
**Automated:**
- [x] `uv run pytest tests/conformance/test_constraint_lowering.py` → 6 passed (live, licensed)
- [x] `uv run pytest tests/` → 2182 passed, 4 skipped (full suite, no regressions; deleted the now-obsolete Item-4 additive-guard test, see notes)
- [x] `uv run mypy src/` → 76 errors (unchanged from Phase 2 baseline, none in touched files)
- [x] `uv run ruff check src/` → clean
- [x] Corpus regenerate (`scripts/capture_pipeline_baselines.py`) → empty diff (Phase 3 doesn't touch `pipeline_builder`, as expected)

**Manual:**
- [x] Live-probed `constraint_multi_instance`: `occurrences_of("constraint_multi_instance__Cell")` returns 3; the occurrence-scoped key misses and the de-indexed scoped key is the only registry hit (matches `b1-probe-evidence.md`) — asserted by `test_multi_instance_three_ids_three_channels_shared_binding`.

**What We Know Works After This Phase:** `lower_constraints` produces the correct catalog for all four owner-kinds, multi-instance siblings with recorded shared bindings, inline predicate selection, and the blocked-owner error — all without touching `pipeline_builder`.

---

## Phase 4: Threading into `build_pipeline_context` + roots-before-pruning + P3 extension

**STATUS: BLOCKED — pipeline-builder wiring reverted after breaking the existing corpus.
`extend_graph_with_constraints` (P3) is implemented, tested, and committed. The P1/P2 call
sites in `pipeline_builder.py` are NOT wired — see "Blocking finding" below before resuming.**

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
- [x] **`analysis/constraint_lowering.py`** — `extend_graph_with_constraints(graph, concrete, group_deriver) -> ComputationGraph` (P3 body; mirror `s4_lib.py` `extend_graph`, `:475-570`; sort params by QN, groups by name for determinism). **Done, offline-tested. Not yet called from `pipeline_builder` — see STATUS/Blocked note above.**
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
- **Correction discovered during Phase 3 fixture probing, applied retroactively to Phase 2
  (surfaced, capture-fidelity law 4):** live extraction shows `ConstraintUsageFact.membership_kind`
  is `None` for every ordinary top-level `assert constraint` — including S4's own proven
  `wi014_toy::affordable` case — and is populated only for a `RequirementConstraintMembership`
  (the `requirement_def` / out-of-profile territory Item 5 already catalogs unassessed, D7).
  The design's INV-8 guard assumed `membership_kind` would read `"assert"` for in-profile
  usages (S4 hardcoded that literal rather than reading it live); guarding on it as designed
  would reject 100% of real in-profile input. Renamed `guard_nullable_facts` to `guard_polarity`,
  scoped to `is_negated` only; `membership_kind` passes through to `ConcreteConstraint`
  unguarded, carrying whatever the fact actually holds (normally `None`). Test file updated
  to match (`test_polarity_guard_*`, was `test_nullable_guard_*`).
- Used the repo's existing `CodeGenerationError` (`orchestration/pipeline_context.py`) instead
  of inventing a new `GenerationError` type — the plan's test stencils used `GenerationError`
  as a placeholder name; the repo already has exactly this class and every other item (Item 6,
  etc.) raises it for generation-time failures, so reusing it keeps one error type across the
  codebase rather than two doing the same job.
- No `_canonical_json` helper existed in this repo (design's R3 note assumed one); used
  `json.dumps(sort_keys=True, separators=(",", ":"))` inline, matching the idiom the landed
  `expression_ir._canonical_json` (agentic-mbse) already uses.

### Phase 2 Completion
**Completed:** 2026-07-12
**Changes Made:**
- `analysis/dependency_backtracker.py`: extracted `terminal_disposition()` (module-level,
  new `__all__` export); Step 4 of `_resolve_binding_via_registry` now calls it instead of
  inlining the fallback-synthesis block.
- `analysis/constraint_lowering.py`: added `occurrence_scope()`, `_deindexed_scope()`,
  `_reference_dotted()`, `resolve_actual()`, `guard_nullable_facts()`.
- `tests/unit/test_constraint_resolver.py` (NEW): 11 tests, all passing.

**Issues Encountered:**
- Ruff's `UP037` flagged the `TYPE_CHECKING`-guarded quoted annotations as redundant
  (the file already has `from __future__ import annotations`) — fixed via `ruff --fix`.

**Deviations from Plan:**
- `resolve_actual` does not take a `strict` parameter as the plan's stencil signature
  suggested. Threading `strict` through would make one function return two structurally
  different result shapes depending on a boolean (a `ConcreteConstraintInput` for the
  strict/constraint case; the calc path's bare fallback string is not that type at all) —
  exactly the "branching on a sentinel to select unrelated behavior" pattern the quality
  bar forbids. `resolve_actual` always resolves strictly (constraint lowering is never
  lenient, by design); it calls the shared `terminal_disposition(strict=True)` unconditionally.
  The switch itself still supports both dispositions and is tested directly in both modes
  (`test_switch_shared_lenient_path_still_synthesizes` / `test_switch_strict_raises_naming_actual`).

### Phase 3 Completion
**Completed:** 2026-07-12
**Changes Made:**
- `analysis/constraint_lowering.py`: added `_design_attr_index`, `_formal_default_index`,
  `_expand_owner_instances`, `_source_local_identity`, `_resolve_formal`, `lower_constraints`.
- `tests/fixtures/{constraint_multi_instance,constraint_inline,constraint_blocked_owner}/`
  (NEW): `model.sysml` + `PROVENANCE.md` each.
- `tests/conformance/test_constraint_lowering.py` (NEW): 6 tests.
- Deleted `tests/unit/test_part_instance_index_additive.py` — its entire assertion was "no
  production module imports `part_instance_index` yet" (Item 4's additive-boundary guard,
  explicitly scoped "until Item 5" in its own docstring). This item is exactly the wiring
  that test existed to forbid until now; its job is done, so it was removed rather than kept
  red or patched with an allowlist.

**Issues Encountered — two genuine findings surfaced during implementation, not deferred:**
1. **`membership_kind` premise conflict (see Phase 2 notes above for the fix).** Discovered
   here, while probing the fixtures live, and corrected retroactively in `guard_polarity`.
2. **The environment's syside license needs `SYSIDE_LICENSE_KEY` exported explicitly to make
   an isolated conformance-file pytest run see it** (`../agentic-mbse/.env` only auto-loads
   when something in the import graph pulls in `agentic_mbse.cli`, which the full suite's
   collection does incidentally but a single `pytest tests/conformance/test_constraint_lowering.py`
   run does not). Exported `SYSIDE_LICENSE_KEY` for this session's shell; no code change.
   One full-suite run showed a transient 23-failed/96-error flake (looked like resource
   contention on first cold model load); two subsequent full runs were clean — treated as a
   flake, not a regression (isolated re-runs of the same files were consistently green).

**Deviations from Plan:**
- `lower_constraints`'s signature drops `group_deriver` and `strict` from the plan's stencil.
  `group_deriver` is only needed to place *newly minted* entry points into their derived
  groups — that's Phase 4's `extend_graph_with_constraints` job (S4's own split: `lower_constraints`
  never took a deriver either). `strict` was never going to be called `False` from this function
  (constraint lowering IS the strict path); a parameter with exactly one legal value in
  production is not a real parameter. Both omissions keep `lower_constraints` to one job:
  expand + resolve + mint, nothing about downstream graph placement.
- `constraint_multi_instance`'s model differs from the Appendix B prose sketch (assert nested
  in `Cell`, self-scoped, not in `Container` referencing `cell.power_calc.p`) — see the
  fixture's `PROVENANCE.md` for the full reasoning (placing it in `Container` would expand to
  exactly one instance, not three, since `Container` itself is a singleton under `Design`).
- Formal names for `modeled_default` inputs are recovered from the omitted formal's QN leaf
  (`sanitize_name(formal_qn.rsplit("::", 1)[-1])`) since `omitted_default_formals` is
  `list[str]` (QNs only, per the landed `constraint_facts.py` schema), not `FormalFact` objects;
  the default IR itself is looked up via a QN index built from `facts.definitions` up front.

### Phase 4 Completion — PARTIAL, blocked before final wiring

**Completed 2026-07-12:**
- `analysis/constraint_lowering.py`: `extend_graph_with_constraints` (P3), `_constraint_module_type`,
  `_literal_float`, `_group_for_qn` — landed, offline-tested (`tests/unit/test_constraint_graph_extension.py`,
  8 tests, all passing without a live model — pure data transformation over
  `ComputationGraph`/`ConcreteConstraint`/`ParameterGroupDeriver`).
- **Real bug fixed in `resolve_actual` (Phase 2's design-attribute rung):** `reference.target
  .qualified_name` is SysML `::`-form (e.g. `"toy_plant::'Toy Plant'::plant_budget"`); the
  design-attribute index is keyed by EQN `__`-form (`attr.qualified_name`, e.g.
  `"toy_plant__Toy_Plant__plant_budget"`). The original code compared them directly and never
  matched anything with a `::` in it. Fixed by applying `sanitize_qualified_name` before the
  lookup — verified against `wi014_toy`'s own `plant_budget` actual (this is exactly the case
  S4 proved worked; it was broken in my Phase 2 code, not a limitation of the approach).
  `tests/unit/test_constraint_resolver.py::test_ladder_falls_to_design_attribute` updated to
  use a realistic `::`-form `target_qn` (it had been silently testing the wrong input shape).

**Attempted and reverted — the P1/P2 threading into `pipeline_builder.build_pipeline_context`:**
Wiring `lower_constraints` unconditionally into the shared pipeline entry point broke the
existing corpus. This is not the QN bug above (fixed and verified separately, still applied);
after that fix, two more failures remained, tracked to two genuine, unresolved gaps the design
itself names as risks but that only bite at whole-corpus scale:

1. **Item 3 (executable-profile eligibility) does not exist in this codebase.**
   `epic_constraint_execution.md` Item 3 ("Executable Profile — Eligibility Gates") is a
   separate, unimplemented epic item (agentic-mbse + sysml-codegen preflight hook,
   ~1.5 days). Design's B3 explicitly names this: *"Every fact reaching lowering is
   profile-admitted (Item 3 upstream)... If false → lowering meets requirement_def/
   out-of-profile forms or None polarity on the normal path; the defensive branches (D7,
   nullable-guard) fire as errors, which is correct behavior but means Item 3 has a gap."*
   That gap is not hypothetical: `catf_mfe`'s `RadiusConsistency` assertion (owner-kind
   `part_def`, but not an `AssertConstraintUsage` subtype that carries `is_negated`) hits
   `guard_polarity` and correctly raises — but nothing upstream filtered it out first, so an
   ordinary `catf_mfe` codegen run now fails outright. Item 5's own Non-Goals disclaim this
   ("Profile eligibility decisions — Item 3 has already gated what reaches lowering") — true
   of the design's assumption, false of this codebase's current state.
2. **The strict ladder (D1, scoped_lookup → alias_lookup → design-attr-by-QN) is narrower
   than the calc backtracker's full ladder, exactly as risk R5 predicts.** `fusion_tea`'s
   `hif_plant.eta` assertion references `driver.efficiency` through a structured
   part-def-EXPOSE alias the calc path resolves via `scoped_alias_lookup` (backtracker Step
   1c) — a rung the strict ladder deliberately omits (D1's amendment added only
   `alias_lookup`). R5's own mitigation note says growing the ladder is a legitimate response
   *if evidence shows an omitted rung is in-profile* — but D1's rejected-alternative already
   weighed and declined "fully unifying the backtracker's ladder" for byte-identity-risk
   reasons. Deciding whether/how far to grow the strict ladder for real corpus models is a
   design-level call, not a Phase-4 implementation detail.

Both are premise conflicts between the design (written assuming Item 3 exists and assuming
the strict ladder's coverage was sufficient) and the evidence (neither holds once wired
across every existing fixture, not just the three new ones). Chasing each corpus failure by
further widening the strict ladder ad hoc would recreate exactly the "unified ladder" D1
explicitly rejected; silently catching lowering errors at the call site to keep the corpus
green would violate INV-2, the invariant Item 5 exists to establish. Neither is a call I
should make unilaterally.

**Reverted:** the `pipeline_builder.py` P1/P2 call sites and the `PipelineContext
.concrete_constraints` field (git-checked-out back to the pre-Phase-4 committed state — clean
diff, verified via `git status`/`git diff`). The P3 function they would have called
(`extend_graph_with_constraints`) stays landed and tested; only the *wiring* is reverted.
Full suite green (2190 passed / 4 skipped) and corpus regenerate is an empty diff with the
revert in place.

**Options for the owner (next step before resuming Phase 4/5):**
- (a) Land Item 3 first (its own spec/design/plan cycle), then re-attempt P1/P2 wiring.
- (b) Scope P1/P2 to run only for models known to be in-profile (e.g. an opt-in flag on
  `build_pipeline_context`, or restrict to the three new Item-5 fixtures) until Item 3 lands —
  a narrower, reversible wiring that doesn't touch the shared default path.
- (c) Deliberately widen the strict ladder (add `scoped_alias_lookup` at minimum) as a
  scoped Item-5 design amendment, accepting the byte-identity re-verification cost D1 flagged.
None of these are Phase-4 implementation calls; they change the item's scope or sequencing.

### Phase 5 Completion
**Not started — blocked on Phase 4's owner decision above** (Phase 5 is the corpus-wide
success-criteria + byte-identity gate, which cannot be meaningfully attempted while P1/P2
threading is unresolved).

---

**Status:** Draft → In Progress (Phases 1–3 complete; Phase 4 partial — P3 landed, P1/P2
wiring blocked on an owner decision, see Phase 4 Completion notes; Phase 5 not started)
