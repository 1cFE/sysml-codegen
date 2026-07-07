# Implementation Plan: F4 Aggregation-Resolution Cutover (+ graph_builder param-group typing)

**Status:** Draft
**Created:** 2026-07-06
**Last Updated:** 2026-07-06
**Branch:** truth-debt-epic
**Epic:** TRUTH-DEBT, Item 1 (SC-A, SC-G)

## Source Documents
- **Spec:** `.project/active/f4-cutover/spec.md`
- **Design:** `.project/active/f4-cutover/design.md` ← component details, D1–D5, INV-1..7, Sequencing
- **Design review:** `.project/active/f4-cutover/design-review.md` (Revise → all resolutions ADOPTED/CLOSED)
- **Epic:** `.project/backlog/epic_truth_debt.md` (Item 1; R1–R4)

## Implementation Strategy

**Phasing Rationale.** The design's sequencing is the plan's spine (`design.md#implementation-notes` →
"Sequencing (green-before-rewire)"). The one hard constraint that orders everything: the parity gates
must be **green before** the live path is touched, because the cutover deletes the very function the
old-comparand gate compiles against. So the plan front-loads the pure value-half changes (no behavior
change), stands up all three parity gates while the old code still runs, then lands the rewire and all
deletions in **one cutover commit**, proves byte-identity, and only then does the separable typing
cleanup and the docs/matrix move.

**Critical Path:**
1. Value-half plumbing (key fix, Strategy E, the helper) — no rewire, suite stays green.
2. Parity gates GREEN before rewire — M3 full-`InputSource` gate + LocalTerm reroute pin + MANUAL_REQUIRED test.
3. **Cutover commit** — rewire 3 call sites, delete inline blocks + old function + Strategy D + the M3 old-comparand half, migrate the ~11-test tail. All together.
4. Baseline byte-identity proof (aggregation is the HARD bar — any agg diff blocks pending root-cause).
5. param_groups typing cleanup (D4 rename + D4b dead-code delete).
6. R1 docs + matrix, final full gates.

**First Proof Point:** Phase 2 — the M3 full-`InputSource` gate green while the old path still runs.
That is the safety net; nothing downstream is safe to touch until it holds.

**Biggest Risks** (see `design.md#potential-risks`):
- Strategy E churns SumTerm/LocalTerm (B3 false) → caught by the M3 gate pre-rewire; fallback is D3.
- LocalTerm expose-alias reroute has **zero M3 coverage** → guarded by the D5 `module_output`-only
  guard + a dedicated reroute pin + byte-identity.
- Aggregation baseline churn → the whole point of the reconciliation is byte-identity; any agg diff is
  a defect to root-cause, not churn to accept (INV-4).

**Overall Validation Approach:**
- Each phase starts with tests (or, in Phase 4, a re-capture proof).
- Gate ceilings enforced where relevant: `ruff check src/` ≤ 17, `mypy src/` ≤ 104, targeted suite green.
- Final phase runs full gates + matrix recount from rows.

---

## Phase 0 — Pickup Re-Verification (R4 step 2; do first, no code change)

### Goal
A filed line number is a static-read verdict until reproduced. Baseline/typing edits in this same item
shift line numbers, so re-anchor every target before editing anything.

### Actions
- [x] Confirm the three call sites and the def. Spec filing: call sites `graph_builder.py:1444/1539/1640`,
  def at `:1212`. Re-grep and record the live line numbers — later phases reference them. **DONE — zero drift.**
- [x] Confirm baseline gate counts live: `mypy src/` == 104, `ruff check src/` == 17 at HEAD. **DONE.**
- [x] Reproduce the mypy typing error for D4: temporarily remove both `type: ignore`s at
  `graph_builder.py:408/412`, run `mypy src/`, confirm the exact two errors the design records
  (`:408 [assignment]` ParameterGroup vs DerivedParameterGroup; `:412 [attr-defined]` ParameterSource
  has no `qualified_name`), then restore the ignores. Do not fix yet (that is Phase 5). **DONE — verbatim match, restored.**
- [x] Confirm the SingletonTerm "Try 2" channel construction (`~:1548-1560`) and the LocalTerm
  expose-alias branch (`~:1640`) still match `design.md#core-concept` / D5. **DONE — match.**

### Validation
- [x] Live line numbers recorded in this plan's Implementation Notes; any drift from the filing noted (none).
- [x] mypy = 104, ruff = 17 confirmed at HEAD.
- [x] The two D4 mypy errors reproduced verbatim, then ignores restored (working tree clean).

**What We Know After:** every edit target is anchored to live lines; the D4 fix is confirmed a
loop-variable problem, not a binding-site one.

---

## Phase 1 — Value-Half Plumbing (no rewire, no deletions)

### Goal
Land the three pure additions that carry no behavior change to the live path: the fallback key fix,
Strategy E, and the `_build_agg_input_source` helper. Nothing is wired to the aggregation call sites
yet, so the suite and baselines stay green/identical. This lets Phase 2's gates exercise the real
new-side code.

### Assumption Under Test
The value half is a one-line key fix (B1) and Strategy E is a no-op for SumTerm/LocalTerm refs (B3) —
i.e. these additions do not, by themselves, change any resolution result.

### Test Stencil (Write First)
```python
# tests/unit/test_input_resolver.py
def test_agg_fallback_key_is_dotted_underscored():
    # resolve_input fallback QN must be ref.replace('.', '_'), not leaf-only rsplit
    src = resolve_input("part_usage.cost", ctx, AGG_STRATEGIES)
    assert src.qualified_name == f"{ctx.module_eqn}__part_usage_cost"

def test_strategy_e_returns_channel_only_when_in_canonical():
    # Strategy E builds get_channel_name(instance_path__prefix, output) iff it exists
    assert strategy_e(dotless_local_ref, ctx) is None          # no-op for locals
    assert strategy_e(singleton_ref, ctx_with_channel) == expected_channel
```

### Changes Required
**See `design.md#component-overview` and `#key-decisions` (D1, D3).**

- [x] `input_resolver.py:~270` — fallback key `ref.rsplit(".",1)[-1]` → `ref.replace(".", "_")` (D1 value half; INV-1).
- [x] `input_resolver.py` — add Strategy E `DirectChannelConstruction`; append after A/C/B in `AGG_STRATEGIES`
  (D3; in-idiom with `ChainRedefinitionFollow`). **Strategy D kept** (removed in Phase 3). Appended at end → `[A,C,B,D,E]`.
- [x] `graph_builder.py` — add `_build_agg_input_source(...)` helper (dormant). Wraps `resolve_input`, owns the
  EP side effects, returns `(InputSource, manual_required: bool)`. Absorbs both literal-lookup shapes via
  `literal_lookup_key: tuple[str,str] | None` (None = dotless-SingletonTerm skip). ctx built by caller with
  `module_eqn = agg.module_eqn` (INV-7). Uses `resolve_input`'s reconciled `qualified_name` as the EP key.

### Validation
**Automated:**
- [x] New unit tests pass (`TestPhase1ValueHalf`, 2 tests).
- [x] `uv run pytest tests/` → green (2071 passed, 4 skipped, 5 xfailed; helper dormant).
- [x] `ruff check src/` == 17; `mypy src/` == 104 (helper + Strategy E add no new errors).
- [x] `git diff tests/fixtures/baseline_outputs/` → empty (no generation path change yet).

### Phase 1 Completion note
- Also updated `test_strategy_ordering_matches_agg_strategies` (4→5, E at index 4) — a necessary
  consequence of adding Strategy E while keeping D. Phase 3 revises it again to 4 (A/C/B/E) when D is deleted.
- `param_name` proven uniform: SumTerm `{pu}_{attr}` and SingletonTerm `source_path.replace('.','_')`
  both equal `ref.replace('.','_')`, so the single fallback rule reconciles both (B1 confirmed in code).

**What We Know After:** the reconciled value half and the helper exist and typecheck; the live path is
untouched, proving these additions are behavior-neutral.

---

## Phase 2 — Parity Gates GREEN Before Rewire (the safety net)

### Goal
Stand up all three parity guards **while the old path still runs**, so they capture the executed old
behavior as the comparand. This is INV-3 and the load-bearing sequencing constraint.

### Assumption Under Test
The new-side helper reproduces the executed old inline block's **full `InputSource`** (source_type,
producer_channel, qualified_name, param_group) over the aggregation fixtures — and the LocalTerm
expose-alias reroute is safe under the D5 guard.

### Test Stencil (Write First)
```python
# tests/unit/test_input_resolver.py :: TestRegression  (extend the existing gate → M3)
def test_regression_full_inputsource_parity(agg_fixture):
    for term in sum_terms + singleton_terms:
        old = old_inline_block(term)              # calls _resolve_aggregation_input_channel + fallback
        new, _manual = _build_agg_input_source(term.ref, ctx, ...)
        assert new.source_type == old.source_type
        assert new.producer_channel == old.producer_channel
        # NEW-SIDE (survives cutover): the reconciled EP key
        assert new.qualified_name == f"{term.module_eqn}__{term.ref.replace('.','_')}"

# LocalTerm expose-alias reroute pin (Major 3) — over alias_agg_probe / solar_battery
def test_localterm_reroute_module_output_only():
    r = resolve_input(alias_source, ctx, AGG_STRATEGIES)
    if r.source_type == "module_output":
        assert r.producer_channel == old_channel
    else:  # D5 guard: fall through, LocalTerm key unchanged
        assert local_term_ep_key == f"{module_eqn}__{attribute_name}"
```

### Changes Required
**See `design.md#component-overview` (M3 gate, LocalTerm reroute pin) and D2, D5, Major 1/2/3.**

- [x] Extend `TestRegression` into the M3 gate: two halves, clearly marked with `Phase-3 DELETE
  START/END` fences. `test_m3_full_inputsource_parity` (old-comparand, calls the deleted function +
  reproduces the old fallback, compares FULL InputSource tuple incl param_group) over
  `solar_battery_model`+`issue22_model`; `test_m3_reconciled_ep_key_survives` (permanent new-side, asserts
  `_build_agg_input_source(...).qualified_name == formula` + param_group) over `solar_battery_model`.
- [x] LocalTerm expose-alias reroute pin (Major 3) — `TestLocalTermExposeAliasReroutePin`: channel parity
  when a channel exists + D5 `module_output`-only guard. Exercised the real case
  (`misc_hardware_cost → allocation_model.total_allocation → channel`, channel_hits=1).
- [x] MANUAL_REQUIRED preservation test (INV-2) — `TestManualRequiredPreserved`: unresolved no-default
  term → `manual_required=True`; channel-resolving term → `False`.

**DEVIATIONS (fixture scoping, recorded per plan):**
- `test_m3_reconciled_ep_key_survives` scoped to `solar_battery_model` only — issue22's agg inputs ALL
  resolve to channels (zero fallback EPs), so the new-side assertion is legitimately vacuous there.
  issue22 stays in the full-parity (old-comparand) test, covering the channel branch.
- LocalTerm reroute pin scoped to `solar_battery_model` only — verified `alias_agg_probe`'s snapshot
  carries NO EXPOSE_PURE computed_attributes (empty `expose_aliases`, no `local_terms`), so it cannot
  exercise the reroute through the factory-inputs path. solar_battery is the covering fixture.

### Validation
**Automated:**
- [x] `uv run pytest tests/conformance/test_input_resolver.py` → 32 passed (all gates green).
- [x] Old-comparand half compiles and runs (function not yet deleted) — captured the executed old block
  before Phase 3 removes it (INV-3).
- [x] `ruff check src/` == 17; `mypy src/` == 104. Full suite 2075 passed; baselines byte-identical.

**What We Know After (INV-3):** the reconciled path matches the executed old block over the aggregation
fixtures, and the LocalTerm reroute is safe. The rewire is now de-risked.

**GATE — CLEARED (all parity gates green before rewire).**

---

## Phase 3 — Cutover: Rewire + Deletions (ONE commit)

### Goal
Move fallback ownership to the helper, rewire the three call sites, and delete everything the cutover
retires — in a single commit, because the deletions are mutually entangled (the M3 old-comparand half
cannot compile against the deleted function).

### Assumption Under Test
The rewire is behavior-preserving: the live path now runs through `resolve_input`/`_build_agg_input_source`
and produces the identical `InputSource` and `MANUAL_REQUIRED` decisions the inline blocks did.

### Test Stencil (adjust existing)
```python
# tests/unit/test_graph_builder_aggregation.py — the ~11 direct-call tests
# Each currently calls _resolve_aggregation_input_channel(...). Per case, either:
#   migrate → assert resolve_input(ref, ctx, AGG_STRATEGIES) / _build_agg_input_source(...)
#   delete  → if already covered by test_dual_resolution.py
def test_sum_term_resolves_to_channel_via_resolve_input():
    src, manual = _build_agg_input_source(ref, ctx, ...)
    assert src.source_type == "module_output"
    assert manual is False
```

### Changes Required
**See `design.md#architecture`, D5, and `#implementation-notes` (test-surgery tail).**

Rewire:
- [x] SumTerm call site — replaced inline block with `_build_agg_input_source(...)`; `MANUAL_REQUIRED`
  applied from the returned flag; multiplicity EP append kept inline. ctx built once per agg (INV-7).
- [x] SingletonTerm call site — same; helper absorbs the dotless case (Minor 4); Try-2 now Strategy E.
- [x] LocalTerm channel call — rewired with the **D5 `source_type == "module_output"`-only guard**;
  else falls through to LocalTerm's own inline fallback (`{module_eqn}__{attribute_name}`, unchanged).

Delete (same commit):
- [x] The SumTerm + SingletonTerm inline `else:` blocks (collapsed into the helper).
- [x] `_resolve_aggregation_input_channel` (def + the `__all__` export). Added `_build_agg_input_source`
  to `__all__`. Fixed the dangling docstring in `_find_literal_redefinition` + `output_registry_builder`.
- [x] Strategy D `DesignAttributeLookup` — from `AGG_STRATEGIES`, the function, and its docstring.
- [x] The M3 gate's **old-comparand half** (`test_m3_full_inputsource_parity`, DELETE-fenced). **Kept the
  new-side assertion** (`test_m3_reconciled_ep_key_survives`) as the permanent EP-key guard (D2, Major 1).
  Deleted `TestStrategyD`; converted the LocalTerm reroute pin to a permanent new-side form (no old fn).

Test-surgery tail:
- [x] `tests/unit/test_graph_builder_aggregation.py` — migrated the 10 `TestResolveAggregationInputChannel`
  direct-call tests via a `_resolve_channel` shim (channel-or-None over `resolve_input`/AGG_STRATEGIES),
  preserving every assertion against the NEW strategy code. `TestBuildAggregationModule` (+ toposort/orphan/
  compilation classes) call `_build_aggregation_module` and now exercise the rewired path — kept as-is, all pass.

### Validation
**Automated:**
- [x] `uv run pytest tests/` → full suite green (2072 passed, 4 skipped, 5 xfailed).
- [x] `ruff check src/` == 17; `mypy src/` == **101** (deletions removed 3 errors; well under ≤104).
- [x] `grep -rn "_resolve_aggregation_input_channel\|DesignAttributeLookup" src/` → no live references
  (one intentional historical docstring mention in input_resolver.py). Baselines byte-identical (empty diff).

**What We Know After:** the live aggregation path runs through `resolve_input(AGG_STRATEGIES)`; the old
function, Strategy D, and the inline fallbacks are gone; INV-1/2/5 hold in code. Baselines are checked
next.

---

## Phase 4 — Baseline Byte-Identity Proof (R3; aggregation = HARD bar)

### Goal
Prove the cutover changed **no** generated output. The reconciliation is designed to reproduce the live
EP construction exactly, so the expected outcome is zero churn. Any aggregation diff **blocks** the
cutover pending root-cause (INV-4) — it is a defect to explain, not a diff to accept.

### Assumption Under Test
The reconciled part-usage EP key and the rewired channel resolution reproduce every baseline byte-for-byte.

### Changes Required
**See `design.md#implementation-notes` (Baseline scope) + memory `byte-identity-captured-at-churn`.**

- [x] Re-captured the generated baselines through `scripts/capture_pipeline_baselines.py` +
  `capture_baseline_yaml.py` (both snapshot-driven, license-free). Snapshot fixtures (extraction inputs)
  need no re-capture — the cutover only touched the generation path, not extraction.
- [x] Timestamp-churn method: baseline_outputs/yaml carry no `captured_at` (that lives in the extraction
  snapshots, which I did not re-capture), so there was **zero timestamp churn** to revert.
- [x] `solar_battery` (the aggregation fixture, sole divergent-key carrier) inspected specifically.

### Validation
- [x] `git diff tests/fixtures/baseline_outputs/` after full re-capture → **BYTE-IDENTICAL for
  solar_battery and every other aggregation-bearing/generation baseline** (INV-4 HARD bar met). The
  cutover's own output churn is **zero**.
- [x] `uv run pytest tests/` → green against the unchanged baselines (2072 passed in Phase 3).

**FINDING (orthogonal, does NOT block — recorded per gate protocol):** the ONLY fixture that diffed on
re-capture was `deep_cross_scope_probe/computation_graph.json` (4 lines: two entry points flip
`entry_type` `usage_literal`→`library_default` and gain a `source_calc_usage`). Root-caused:
- `deep_cross_scope_probe` has **zero aggregation expressions** — it is NOT an aggregation fixture, so it
  is outside the F4 [HARD] aggregation byte-identity bar.
- The identical 4-line diff **reproduces when re-capturing on the pre-cutover source (`ba3bca4`, before
  any F4 code)** — so it is a **pre-existing stale baseline**, an entry-point-classification churn
  unrelated to and not caused by the F4 cutover.
- Left the committed baseline unchanged (reverted the re-capture): fixing an unrelated stale baseline in
  this item would be scope creep and would muddy the "cutover is byte-identical" claim. Filed for
  follow-up (memory `deep-cross-scope-stale-baseline`).

**What We Know After (INV-4):** the cutover is provably byte-identical on every generated output it
touches; the aggregation HARD bar holds. The one orthogonal diff is pre-existing, non-aggregation debt.

**GATE — CLEARED. No cutover-attributable diff; the single diff is pre-existing non-aggregation churn.**

---

## Phase 5 — param_groups Typing Cleanup (D4 + D4b; SC-G)

### Goal
Clear the two `param_groups` `type: ignore`s via the loop-variable rename (D4, evidence-backed in
Phase 0) and delete the dead Step-5 computation (D4b). Separable from the cutover; done after the
byte-identity proof so the cutover stayed isolated.

### Assumption Under Test
The rename clears both ignores without raising mypy; the Step-5 deletion loses no value or warning (B4).

### Test Stencil (Write First)
```python
# The gate here is mypy itself + suite; add a guard only if warning behavior is in question:
def test_no_nonfloat_warning_lost_after_step5_delete(caplog):
    build_computation_graph(fixture_with_nonfloat_ep)
    # non-float warning still fires at Step 6.6 via derive_groups(), not the deleted Step-5 path
    assert any("non-float" in r.message for r in caplog.records)
```

### Changes Required
**See `design.md#component-overview` (param_groups typing fix), D4, D4b, B4.**

- [x] Renamed the `raw_groups` loop variable (`for group in raw_groups` → `for dg in raw_groups`, body
  updated) so the `param_groups` sort loop binds a clean `group` typed `ParameterGroup`. **Both
  `type: ignore`s removed** (D4) — mypy reports no error at those lines.
- [x] Confirmed B4 by reading the code (not just grep): `derive_groups_filtered` DOES call
  `derive_groups()` (`parameter_groups.py:575`) — so the design's B4 *mechanism* ("does not reach
  derive_groups") was **wrong**, but its *conclusion* holds: Step 6.6 (`:329`) calls `derive_groups()`
  unconditionally, so the non-float warning still fires there; Step-5's firing was a DUPLICATE. Pinned by
  the existing `test_silent_failure_sc5.py` (calls `derive_groups()` directly). Then deleted the dead
  Step-5 call and the orphan `_group_entry_points_via_deriver` (D4b) — confirmed zero remaining callers,
  and `param_groups` is not read between Step 5 and the Step 6.6 rebuild.

### Validation
**Automated:**
- [x] `mypy src/` == **97** with both ignores removed and **no new errors** (was 101 after Phase 3;
  −2 from the cleared ignores' underlying errors, −2 more from the orphan-function deletion). ≤ 104.
- [x] `ruff check src/` == 17 (BacktrackingResult still used elsewhere — no F401).
- [x] `uv run pytest tests/` → green (2072 passed); Step-5 deletion loses no warning/value; baselines
  byte-identical.

**DEVIATION (B4 mechanism):** the design said `derive_groups_filtered` "does not reach `derive_groups()`";
it does (`:575`). Deletion is still safe because Step 6.6 independently fires the warning and the SC-5
test pins it. No caplog test added — the existing SC-5 test + the structural guarantee cover it (adding
one would duplicate coverage).

**What We Know After (INV-6, SC-G):** the double-binding is untangled, both ignores cleared, mypy no worse.

---

## Phase 6 — R1 Docs + Matrix (docs move with code) + Final Gates

### Goal
Move the IR-family matrix rows and reference docs in the same change that wired the path, so no reader
inherits the "not-yet-wired" note or the re-lie. Then run the full gates.

### Assumption Under Test
Every doc/row that described `resolve_input` as validated-but-unwired now pins live code, and the matrix
recount from rows still holds the gate counts.

### Changes Required
**See `spec.md` "R1 docs-move-with-code" + `design.md#integration-strategy`.**

- [x] Verification matrix: IR-family status blocks (DRA + IR) rewritten to "F4 cutover LANDED" pinning
  live code; REQ-IR-05 (strategy list now `[A,C,B,E]`, D deleted / E added), REQ-IR-07, REQ-DRA-02,
  REQ-RES-02, REQ-RES-08 reframed to the live `resolve_input(AGG_STRATEGIES)` via `_build_agg_input_source`
  path. Recounted **from rows**: 253 total / 249 PASS / 4 UNTESTED / 30 families — matches the summary
  block exactly, **no drift** (memory `verification-matrix-drift-modes`).
- [x] REQ tags in source: the IR-family tests (`test_input_resolver.py`) carry their `@pytest.mark.req`
  markers and now pin the live path (M3 new-side, reroute pin, MANUAL_REQUIRED). No marker needed to move.
- [x] Reference docs — `03-resolution-overview`, `04-input-resolver`, `05-module-factory` updated to the
  landed state (Strategy D→E, old function deleted, D5 guard, byte-identity). `07-graph-assembly` and
  `24-dual-resolution-architecture` confirmed CLEAN (no not-yet-wired claim). `modeling-assumptions.md:450`
  left untouched (its "not yet wired" is about V11 cross-part refs / Items 9-11, unrelated to F4).

### Validation (FINAL FULL GATES)
- [x] `uv run pytest tests/` → full suite green (2072 passed, 4 skipped, 5 xfailed).
- [x] `ruff check src/` == 17 (≤17).
- [x] `mypy src/` == 97 (≤104; both ignores cleared).
- [x] Matrix index counts recounted from rows (253/249/4/30, no drift); no "not-yet-wired" note survives
  for the IR family (the one remaining doc hit is REQ-PGD-06, an unrelated Item-8 dead-accessor note).
- [x] `grep -rn "_resolve_aggregation_input_channel\|DesignAttributeLookup" src/ docs/` → only intentional
  "deleted" historical notes remain; no live references.

**What We Know After (SC-A, SC-G, SC-H):** the matrix and the code agree; the item's success criteria hold.

---

## Environment Setup

**See CLAUDE.md.** Key commands: `uv run pytest tests/`, `uv run mypy src/`, `uv run ruff check src/`.
Baseline re-capture: `scripts/capture_*.py` only (R3). Snapshot generation is license-free via
`--from-snapshot`; live re-capture needs the syside license (monthly renewal — no expiry pressure).

## Risk Management

**See `design.md#potential-risks`.** Phase-specific mitigations:
- **Phase 2:** if the M3 gate reddens for SumTerm/LocalTerm (B3/E churn), fall back to a SingletonTerm-only
  strategy list (D3) — do not proceed to rewire on a red gate.
- **Phase 3:** the LocalTerm reroute is the least-covered route (zero M3 coverage) — the D5
  `module_output`-only guard + Phase 2 reroute pin + Phase 4 byte-identity are its three guards.
- **Phase 4:** any aggregation diff is a blocking defect, not accepted churn — root-cause before signing off.
- **Phase 5:** re-confirm mypy ≤ 104 live after the rename; the fix is evidence-backed (Phase 0 repro) but
  re-verify rather than trust the count.

## Implementation Notes

[TO BE FILLED DURING IMPLEMENTATION]

### Phase 0 Completion
**Completed:** 2026-07-06
**Live line numbers (re-verified):**
- `_resolve_aggregation_input_channel` def: `graph_builder.py:1212`; `__all__` export: `:1925`.
- Call sites: SumTerm `:1444` (inline `else:` `1453-1493`), SingletonTerm `:1539` (Try-2 `1548-1560`,
  fallback `1562-1608`), LocalTerm expose-alias `:1640` (own fallback `1650-1666`).
- Internal recursion call at `:1282` (inside the def itself — dies with the def).
- All match the spec filing (1444/1539/1640, def 1212) — **zero drift** from filing at HEAD.
- param_groups: Step-5 call `:228-233`; `raw_groups` loop var `group` `:325`; `ParameterGroup` loops
  `:335/:373/:408`; ignores `:408` `[assignment]` / `:412` `[attr-defined]`; orphan
  `_group_entry_points_via_deriver` (D4b delete target).
- Established agg ctx mapping (from `test_dual_resolution.py:425-434`, `test_input_resolver.py:107-128`
  `_build_resolution_context_for_agg`): `consumer_scope = ".".join(module_eqn.split("__")[1:-1])`,
  `module_eqn = agg.module_eqn`, `instance_path = agg.instance_path`. Reproduce this in the helper.
- `resolve_input`/`ResolutionContext`/`AGG_STRATEGIES` constructed ONLY in tests, never in `src/` —
  confirms "built + parity-validated, never wired" (spec).

**mypy/ruff baseline at HEAD:** `mypy src/` = **104** errors / 22 files; `ruff check src/` = **17**. Confirmed live.

**D4 mypy errors reproduced:** removed both ignores → mypy = **106** with exactly:
- `:408 Incompatible types in assignment (expression has type "ParameterGroup", variable has type "DerivedParameterGroup") [assignment]`
- `:412 "ParameterSource" has no attribute "qualified_name" [attr-defined]`
Verbatim match to design D4. Ignores restored; working tree clean. Confirmed a loop-variable problem
(`group` bound `DerivedParameterGroup` at `:325`), not a binding-site one — the D4 rename fix is correct.

### Phase 1 Completion
### Phase 2 Completion
### Phase 3 Completion
### Phase 4 Completion
### Phase 5 Completion
### Phase 6 Completion

---

**Status:** Draft → In Progress → **COMPLETE** (all 7 phases landed 2026-07-06; final gates green:
2072 passed, mypy=97, ruff=17; aggregation baselines byte-identical)
</content>
</invoke>
