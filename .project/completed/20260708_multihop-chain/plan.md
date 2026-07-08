# Implementation Plan: Resolved Multi-Hop Chain Bindings

**Status:** Complete
**Created:** 2026-07-07
**Last Updated:** 2026-07-07
**Branch:** truth-debt-epic
**Epic:** TRUTH-DEBT — Item 2 (R1–R4)

## Source Documents
- **Spec:** `.project/active/multihop-chain/spec.md` (revised through spec-review)
- **Design:** `.project/active/multihop-chain/design.md` ← component details, Key Bets, invariants, D1–D5
- **Design review:** `.project/active/multihop-chain/design-review.md` (Revise-light; M-1/M-2/N-1/N-2 incorporated)
- **Epic:** `.project/backlog/epic_truth_debt.md` (Item 2; R1–R4)

## Implementation Strategy

**Phasing Rationale.** The design is two small additive code changes plus a forced diagnostic
relocation, but the *risk* is a silent mis-wire baked into a re-captured snapshot. So the pins land
**first** and stay red across the behavior phases, the two code changes land as **separately-verifiable**
steps (each provable by a synthetic unit test before the fixture ever re-captures), and the re-capture
is last — reviewed line-by-line against three known causes. This ordering means every hardcoded channel
QN is committed before the code that produces it, so a wrong wire shows up as a still-red pin, not a
green-looking baseline.

**Critical Path.**
1. Author pins (both channel-identity QNs + D5 fires-on-shape + silent-on-clean) — red.
2. Extraction stops rejecting → emits full-path CHAIN (D1). Provable in isolation.
3. Backtracker climb + ambiguity guard (D2/D4/M-1). Provable in isolation on a synthetic registry.
4. Loud Step-4 WARNING (D3/M-2) → D5 unit test goes green.
5. Re-capture `deep_cross_scope_probe` only → offline pins + parity go green; three-part diff reviewed.
6. R2 impact note + docs + final gates.

**First Proof Point.** Phase 3's synthetic-registry unit tests: the `data_point` shape resolves via the
climb to the exact expected channel, the `base_metric` shape resolves via the existing Step 1, and a
two-distinct-channel shape **refuses** (falls through). This proves the resolution mechanics before any
fixture is touched — the design's "de-risk first" (design.md#next-stage-handoff), done on synthetic
inputs so a surprise surfaces before the pins or the re-capture encode it.

**Biggest Risks** (full analysis: design.md#potential-risks)
- A wrong ancestor scope wins → silent mis-wire. Mitigated: M-1 collect-all-and-refuse guard + exact-QN
  pins computed independently of the code (R1).
- The climb newly-resolves a chain in another fixture → INV-4 churn. Mitigated: D4 gate (`.count(".")>=2`),
  full-suite byte-identity gate in Phase 5.
- An offline snapshot bakes in a mis-wire that live resolution would not. Mitigated: B3 is structurally
  guaranteed (1-dot alias-key shape) + the @requires_license parity leg.

**Overall Validation Approach.** Each phase starts with tests. Behavior phases (2–4) are each provable
by a synthetic/unit test with **no dependence on the committed snapshot**, so they are green before
Phase 5. The offline channel-identity pins and the parity leg go green only after re-capture (Phase 5) —
each phase below states exactly which pins it turns green, so a red pin between phases is expected, not a
failure.

---

## Phase 1: Pins First (red-first expectations, no behavior change)

### Goal
Lock every expectation before any code moves: both channel-identity QNs, the D5 fires-on-shape unit
test, and the silent-on-clean sibling. This is the item's headline safety property (R1) — the exact
wired channel, computed independently of the code under test.

### Assumption Under Test
That the two target channel QNs can be derived **from the fixture source + `make_scoped_key` semantics
alone** (spec R1), independent of the resolution code. If the derivation is right, these pins are the
oracle; if wrong, the whole item is unanchored.

### Test Stencil (Write This First)
```python
# tests/conformance/test_deep_cross_scope_probe.py — rewrite the rejection pins.
# These read the COMMITTED snapshot via build_full_graph_from_snapshot, so they stay
# RED until Phase 5 re-capture. That is expected. They encode the target, not today.

_DATA_POINT_CHANNEL = (
    "DeepCrossScopeDesign__measurement_system__station__array__derived_calc__derived_value"
)
_BASE_METRIC_CHANNEL = (
    "DeepCrossScopeDesign__measurement_system__station__array__sensor__core__metric_value"
)

def test_pattern_a_deep_chain_resolves_to_derived_value_channel():
    # was test_pattern_a_deep_chain_falls_to_own_entry_point (rejection) — flip to wire
    qn = _input_source_qn(_graph(), f"{_ANALYZER}__chain_analysis", "data_point")
    assert qn == _DATA_POINT_CHANNEL

def test_base_metric_deep_chain_resolves_to_metric_value_channel():   # NEW pin (spec L2-2)
    qn = _input_source_qn(_graph(), f"{_DERIVED}__derived_calc", "base_metric")
    assert qn == _BASE_METRIC_CHANNEL
```
```python
# tests/unit/test_dependency_backtracker.py (or sibling) — D5 fires-on-shape, RED until Phase 4.
def test_multihop_fallback_warns_loud_and_untruncated(caplog):
    # synthetic 3+-dot CHAIN whose tail names a non-existent output; registry lacks it
    binding = BindingInfo(param_name="p", source_path="a.b.c.missing", binding_type=BindingType.CHAIN)
    usage = _synthetic_usage(qualified_name="Design__scope__consumer")
    with caplog.at_level(logging.WARNING, logger="...dependency_backtracker"):
        res = backtracker._resolve_binding_via_registry(binding, usage)
    assert res.resolution_type == BindingResolutionType.ENTRY_POINT
    assert res.qualified_name == "Design__scope__consumer__p"   # full, untruncated (M-2)
    assert any(r.levelno == logging.WARNING for r in caplog.records)   # loud (M-2), not DEBUG
    assert "a.b.c.missing" in caplog.text                              # names the full chain
```

### Changes Required

**See design.md for:** channel derivation → design.md#required-invariants (INV-1); the D5 test
shape → design.md#component-overview ("Fires-on-shape unit test"); the confirm-casing note → spec.md `:140`.

**Specific file changes:**

#### `tests/conformance/test_deep_cross_scope_probe.py` (REWRITE the rejection pins)
- [x] Flip `test_pattern_a_deep_chain_falls_to_own_entry_point` → `..._resolves_to_derived_value_channel` == `_DATA_POINT_CHANNEL`.
- [x] Add `test_base_metric_deep_chain_resolves_to_metric_value_channel` (new, hardcoded QN). NOTE: queries module `_DERIVED` directly (the plan stencil's `f"{_DERIVED}__derived_calc"` was a typo — `_DERIVED` already IS the derived_calc EQN; verified against the built graph's module names).
- [x] Rewrite `test_pattern_a_deep_chain_no_truncated_binding` → `..._full_path_chain_binding`: assert the snapshot carries exactly one **CHAIN** binding with full untruncated `source_path` `station.array.derived_calc.derived_value`.
- [x] Rewrite `test_offender_set_pinned` **docstring** (set stays `set()`, now because both are *wired*) — assertion re-verified GREEN offline (both currently EP → still no uncovered offenders; stays green post-recapture when both wire).
- [x] Leave `test_pattern_b_deep_reference_resolves_...` unchanged (Non-Goal; REFERENCE arm).
- [x] Confirm exact casing of both QNs against snapshot instance QNs (`core` `:359/:383`, `derived_calc` `:389/:402`) — R1 independent anchor done.

#### D5 fires-on-shape + silent-on-clean (NEW, unit-level) — `tests/unit/test_dependency_backtracker.py` (new file)
- [x] Add `test_multihop_fallback_warns_loud_and_untruncated` (RED until Phase 4).
- [x] Add silent-on-clean sibling `test_resolvable_multihop_chain_is_silent` → MODULE_OUTPUT, no backtracker-logger WARNING. GREEN by construction (Step 1 resolves).
- [x] Confirm `caplog` logger target = `sysml_codegen.analysis.dependency_backtracker` (module `__name__`). Silent assertion scoped to that logger name (an unrelated phantom_detector WARN fires on registry build; scoping keeps the sibling faithful to the multi-hop WARN).

### Validation
**Automated:**
- [x] `uv run pytest tests/conformance/test_deep_cross_scope_probe.py` → the two channel pins + full-path-binding RED (snapshot not re-captured), expected.
- [x] `uv run pytest -k multihop_fallback_warns` → RED (WARN not built), expected. Climb-resolve pin also RED (climb not built), expected.
- [x] Silent-on-clean sibling + base_metric-Step1 + refuse + 2-seg-gate → GREEN. ruff clean on both files.

**What We Know Works After This Phase:** the target QNs are committed and independently anchored; every
downstream phase now has a red pin it must turn green — no behavior can land unpinned.

---

## Phase 2: Extraction Emits Full-Path CHAIN (D1)

### Goal
Stop rejecting 3+-segment chains at extraction. Replace the `len(segments) > 2` reject
(`usage_extractor.py:717-739`) with a normal `BindingType.CHAIN` carrying the **full** dotted
source_path from `extract_feature_chain_segments`. No registry contact, no warning here.

### Assumption Under Test
That the full segment list from `extract_feature_chain_segments` is a usable `source_path` with no
truncation, and that omitting `source_instance_elem`/`source_attribute_elem`/`is_cross_file` (N-1) is safe
because the backtracker consumes none of them for CHAIN resolution.

### Test Stencil (Write This First)
```python
# tests/unit/test_usage_extractor.py — extraction-only, no registry.
def test_deep_chain_emits_full_path_chain_not_reject():
    # feed a synthetic 3-segment FeatureChainExpression param
    binding = _extract_binding(param_with_chain("station.array.derived_calc.derived_value"))
    assert binding.binding_type == BindingType.CHAIN
    assert binding.source_path == "station.array.derived_calc.derived_value"   # full, untruncated
    # N-1: element refs intentionally unset on the deep-chain arm
    assert binding.source_instance_elem is None
```

### Changes Required

**See design.md for:** the arm rewrite → design.md#component-overview ("CHAIN extraction arm"); N-1 note
→ design.md#component-overview and design-review N-1; D1 rationale → design.md#key-decisions.

**Specific file changes:**
- [x] `extraction/usage_extractor.py`: removed the `len(segments) > 2` reject block; the arm now builds `BindingInfo(binding_type=CHAIN, source_path=".".join(segments), raw_expression=...)` over the full segment list. The 2-segment `_parse_chain_expression` path is untouched.
- [x] Added the N-1 comment at the arm (only `source_path` set; do NOT reach into `_parse_chain_expression`).
- [x] Removed the dead reject `warnings.append(...)`; loud diagnostic moves to backtracker (Phase 4). Terminal-arm WARN stays; `usage_name` still used there.

### Validation
**Automated:**
- [x] New extraction unit test `test_deep_chain_emits_full_path_chain_not_reject` → GREEN (11/11 in test_extractor.py).
- [x] `@requires_license` DOES load in this env (the warn test actually ran + failed, not skipped). So removed `test_pattern_a_deep_chain_warns_on_extraction` NOW (its warning no longer fires); replacements are the Phase-4 D5 unit test + Phase-5 parity leg. Also dropped the now-unused `requires_license` import (Phase 5 re-adds it) to keep phases 2–4 lint-clean.
- [x] `ruff check src/` = 17 (unchanged), `mypy src/` = 97 (unchanged) — no new findings.

**What We Know Works After This Phase:** deep chains survive extraction as full-path CHAIN bindings. The
offline channel pins are still RED (committed snapshot not yet re-captured), but the extraction half of
the mechanism is proven in isolation.

---

## Phase 3: Backtracker Ancestor-Scope Climb + Ambiguity Guard (D2/D4/M-1)

### Goal
Add one gated step to `_resolve_chain_dispatch` (after Step 2, `dependency_backtracker.py:634`): when
`source_path.count(".") >= 2`, collect every `scoped_lookup(prefix + "." + source_path)` hit across
ancestor prefixes of `consumer_scope`; resolve iff exactly one distinct channel, refuse (fall through) on
two or more. This wires `data_point` (one-level climb); `base_metric` already resolves via Step 1 (no
climb).

### Assumption Under Test
That prefixing the whole path with the ancestor scope where the first segment resolves yields exactly the
registered scoped key (design Key Bet B1), and that collect-all-and-refuse turns a cross-scope collision
into a loud refusal rather than a silent pick (M-1 / INV-2b).

### Test Stencil (Write This First)
```python
# tests/unit/test_dependency_backtracker.py — synthetic OutputRegistry, no fixture.
def test_climb_resolves_one_level_up_data_point_shape():
    reg = registry_with({"measurement_system.station.array.derived_calc.derived_value": CHANNEL_D})
    usage = _synthetic_usage("Design__measurement_system__analyzer__chain_analysis")  # scope = m_s.analyzer
    ch = bt._resolve_chain_dispatch("station.array.derived_calc.derived_value", usage)
    assert ch == CHANNEL_D          # climbed one level (dropped `analyzer`)

def test_base_metric_shape_hits_step1_no_climb():
    reg = registry_with({"measurement_system.station.array.sensor.core.metric_value": CHANNEL_M})
    usage = _synthetic_usage("Design__measurement_system__station__array__derived_calc")
    ch = bt._resolve_chain_dispatch("sensor.core.metric_value", usage)
    assert ch == CHANNEL_M          # Step 1 direct hit, climb not needed

def test_climb_refuses_on_two_distinct_channels():   # M-1 / INV-2b
    reg = registry_with({"a.x.y.z": CH1, "a.b.x.y.z": CH2})   # two prefixes, different channels
    usage = _synthetic_usage("Design__a__b__consumer")
    assert bt._resolve_chain_dispatch("x.y.z", usage) is None   # refuse → falls to Step 4

def test_two_segment_chain_never_enters_climb():     # D4 gate
    # a 2-segment source_path must be byte-identical to today (no new route)
    ...
```

### Changes Required

**See design.md for:** the climb algorithm → design.md#component-overview ("Scope-climb step") +
design.md#architecture (the Step CLIMB pseudocode); the gate → D4; the guard → M-1/INV-2b; B3 key-shape
guarantee → design.md#key-bets (B3), design-review N-2.

**Specific file changes:**
- [ ] `analysis/dependency_backtracker.py` `_resolve_chain_dispatch`: after Step 2 (`:634-637`), before
      `return None`, add the gated climb. Algorithm:
      - gate `if source_path.count(".") >= 2:`
      - iterate ancestor prefixes of `consumer_scope` = full scope, then drop trailing segments one at a
        time down to empty (empty prefix → key is `source_path` alone);
      - for each, `scoped_lookup(ScopedKey(f"{prefix}.{source_path}"))` (bare `source_path` when prefix
        empty), skip `_is_self_reference` hits, collect into a `set` of distinct channels;
      - `len == 0` → fall through (`return None`); `len == 1` → return it; `len >= 2` → `return None`
        (refuse — Step 4 fires the loud fallback).
- [ ] Add the B2/M-1 code comment at the climb site naming the filed first-segment-shadowing assumption
      (design.md#non-goals: single-hit shadowing is documented, not built).
- [ ] Reuse the existing `_is_self_reference` guard (design.md#implementation-notes, "Self-reference guard").
- [ ] No change to Steps 1–2 — the climb is strictly additive (INV-A), ordered last, only adds a hit
      where the ladder fell through.

### Validation
**Automated:**
- [x] The four climb unit tests → GREEN (resolve, Step-1-hit, refuse, gate). First proof point met on synthetic registries.
- [x] `uv run pytest tests/` → 2075 passed; no regression on existing CHAIN resolutions (D4 gate keeps 2-segment byte-identical). Remaining RED = fallback WARN (Phase 4) + 3 offline pins (Phase 5).
- [x] `ruff check src/` = 17, `mypy src/` = 97 → no new findings.

**What We Know Works After This Phase:** the resolution mechanics are proven on synthetic registries —
the climb resolves the `data_point` shape to the exact channel, `base_metric` hits Step 1, and a
two-channel collision refuses. This is the **first proof point**; the fixture has not moved yet.

---

## Phase 4: Loud Step-4 WARNING (D3/M-2)

### Goal
Move the Item-5 loud contract to its forced home: a 3+-segment CHAIN that reaches the Step-4 fallback
(`dependency_backtracker.py:569-587`) emits a genuine `logger.warning` (level WARNING, distinct from the
sibling DEBUG line), names the full untruncated chain, and surfaces as an entry point — never truncated.
Turns the D5 fires-on-shape pin GREEN.

### Assumption Under Test
That the loudness leg of the Item-5 contract survives the relocation only if the new branch is a genuine,
distinct WARNING — not folded into the deliberately-DEBUG benign line it sits next to (design-review M-2).

### Test Stencil (Write This First — already authored red in Phase 1)
```python
# The Phase-1 test_multihop_fallback_warns_loud_and_untruncated goes GREEN here.
# Assertion locks: ENTRY_POINT, level=WARNING, full untruncated usage_qn__param, chain named in message.
```

### Changes Required

**See design.md for:** the WARN branch → design.md#component-overview ("Multi-hop fallback WARN") + D3;
level requirement → design-review M-2; the never-truncated `fallback_qn` → design-review move 6.

**Specific file changes:**
- [x] `analysis/dependency_backtracker.py` Step-4 fallback: before the existing `logger.debug`, added `if "::" not in source_path and source_path.count(".") >= 2:` → `logger.warning(...)` naming the full `source_path` + `usage.qualified_name|param_name`. DEBUG line stays for benign cases; `fallback_qn` unchanged.
- [x] Entry-point disposition + `_fallback_entry_points.add(...)` unchanged.

### Validation
**Automated:**
- [x] `test_multihop_fallback_warns_loud_and_untruncated` → GREEN (WARNING level, full untruncated `Design__scope__consumer__p`, chain named).
- [x] Silent-on-clean sibling → GREEN (resolvable chain, no backtracker-logger WARN).
- [x] `uv run pytest tests/` → 2076 passed; only the 3 offline channel pins RED (pre-recapture). No caplog test elsewhere broke.
- [x] `ruff check src/` = 17, `mypy src/` = 97 → no new findings.

**What We Know Works After This Phase:** the loud+never-truncated contract is preserved at its new home
and pinned at WARNING level. All behavior code is now in place; only the fixture re-capture remains to
flip the offline pins.

---

## Phase 5: Re-capture `deep_cross_scope_probe` (three-part diff, R3) + parity

### Goal
Re-capture the one fixture the change touches, via `scripts/capture_*.py --fixtures deep_cross_scope_probe`
only. Verify the diff line-by-line against three known causes, keep every other baseline byte-identical,
and flip the offline channel pins + the live/offline parity leg GREEN.

### Assumption Under Test
That the re-capture diff decomposes into exactly three parts (two wires + the known stale classification
flip) and nothing else moves — no other calc-usage baseline changes (INV-4), confirming the D4 gate held.

### Test Stencil (Write This First)
```python
# tests/conformance/test_deep_cross_scope_probe.py — NEW parity leg (@requires_license).
@requires_license
def test_live_offline_parity_both_chains():
    live_graph = _build_graph_live("deep_cross_scope_probe")   # extract + resolve live
    for module, param, expected in [
        (f"{_ANALYZER}__chain_analysis", "data_point", _DATA_POINT_CHANNEL),
        (f"{_DERIVED}__derived_calc",    "base_metric", _BASE_METRIC_CHANNEL),
    ]:
        assert _input_source_qn(live_graph, module, param) == expected == \
               _input_source_qn(_graph(), module, param)     # live == offline == pinned
```

### Changes Required

**See design.md for:** the three-part diff → design.md#implementation-notes ("Re-capture plan") +
INV-5; the byte-identity method → design.md#implementation-notes ("Byte-identity method") +
memory `byte-identity-captured-at-churn`; the stale flip → memory `deep-cross-scope-stale-baseline`.

**Specific file changes / steps:**
- [x] `capture_extraction_snapshots.py --fixtures deep_cross_scope_probe` → re-wrote `extraction_snapshot.json` (only that file; `--fixtures` scoped it, no captured_at churn elsewhere).
- [x] `capture_pipeline_baselines.py --fixtures deep_cross_scope_probe` → re-wrote `computation_graph.json` (only that file).
- [x] **Byte-identity gate**: `git status` — among fixtures/baselines, ONLY `deep_cross_scope_probe`'s snapshot + baseline changed. No churn to revert (the `--fixtures` filter scoped both captures). (Unrelated `.project/*/spec*.md` edits are from a parallel orchestrator stage, excluded by pathspec-limited commits.)
- [x] **Diff decomposition** — verified programmatically (module-by-module, EP-set delta):
      1. `chain_analysis.data_point`: unbound_params loses `data_point`×2; CHAIN binding `station.array.derived_calc.derived_value`; graph input flips entry_point → module_output `…__derived_calc__derived_value` (== `_DATA_POINT_CHANNEL`). ✓
      2. `derived_calc.base_metric`: unbound_params loses `base_metric`×2; CHAIN binding `sensor.core.metric_value`; input flips to module_output `…__sensor__core__metric_value` (== `_BASE_METRIC_CHANNEL`). ✓
      3. Stale entry-point-classification flip → **FULLY MOOTED, zero residue**: the two EPs it would reclassify are exactly the two now-wired params; both vanished from the EP groups (no `entry_type`/`source_calc_usage` flip on any surviving EP). R4 verdict: baseline-correct (the flip is superseded, not code-wrong — it reproduced on `ba3bca4` as non-aggregation staleness; here the wires remove its substrate).
      - Mechanical consequences: per-module `execution_order` index + exec-order sequence reorder (topological, same module set); extraction snapshot's `unhandled: false` field dropped across all bindings (serialization catch-up — BindingInfo removed the field before this session; not this item).
- [x] Added the `@requires_license` parity leg `test_live_offline_parity_both_chains` (in-process `build_pipeline_context(...).computation_graph`); re-added the `requires_license` import. Old warn-test already removed in Phase 2.

### Validation
**Automated:**
- [x] `uv run pytest tests/conformance/test_deep_cross_scope_probe.py` → 7/7 GREEN (both channel pins, offender set, full-path binding, pattern-b, parity leg).
- [x] `uv run pytest tests/` → 2080 passed, 4 skipped, 5 xfailed — full suite GREEN.
- [x] `git status` → only `deep_cross_scope_probe` snapshot + baseline changed among fixtures/baselines.

**Manual:**
- [x] Diff decomposed line-by-line (programmatic check); each maps to a named cause. Stale-flip verdict recorded above: fully mooted / baseline-correct.
- [x] License present here → parity leg ran GREEN (live == offline == pinned), not skipped. Confirms no offline mis-wire baked into the snapshot.

**What We Know Works After This Phase:** both wires resolve identically live and offline; the fixture
pins the resolved chains; no other baseline moved. The item's behavior is complete and guarded.

---

## Phase 6: R2 Impact Note + Docs + Final Gates

### Goal
Record the agentic-mbse MODELING_GUIDE impact (R2, sandbox-blocked → in-repo note for later sync), update
the CHAIN-dispatch reference doc (R1 close-the-loop), and clear the final gates.

### Assumption Under Test
None — this is close-out. The only judgment is the R2 disposition (likely "no change needed," but the
newly-supported chain shape is recorded either way).

### Changes Required

**See design.md for:** R2 → design.md#integration-strategy; docs → design.md#integration-strategy
("update `24-dual-resolution-architecture.md` CHAIN-dispatch section").

**Specific file changes:**
- [x] Wrote `.project/active/multihop-chain/agentic-mbse-impact.md` — R2 disposition "no change needed" (no new SysML construct/authoring rule; the deep chain is already valid SysML agentic-mbse parses). Shape recorded for a later sync.
- [x] Updated `docs/architecture/reference/24-dual-resolution-architecture.md` CHAIN-dispatch block: added Step CLIMB (with M-1 guard + first-segment-shadowing residual) and annotated Step 4 with the multi-hop loud WARN.
- [x] Verification matrix (recounted from rows): added REQ-BT-12 (climb + ambiguity guard) and REQ-BT-13 (Step-4 multi-hop loud WARN), both PASS. Bumped BT index 11→13, Total 253→255, PASS 249→251, Distinct test files 57→59 (two newly-cited: `test_dependency_backtracker.py`, `test_deep_cross_scope_probe.py`). Existing REQ-BT-11 still reads true (Step 1c unchanged).
- [x] Epic Item 2 SC-B flipped in `.project/backlog/epic_truth_debt.md` (committed isolated to only my SC-B hunk; sibling SC-A/SC-G working-tree flips left uncommitted for their stages).

### Validation (Final Gates)
**Automated:**
- [x] `uv run pytest tests/` → GREEN (2080 passed, 4 skipped, 5 xfailed).
- [x] `ruff check src/` → 17 (== ceiling, no regress).
- [x] `mypy src/` → 97 (== ceiling, no regress).
- [x] `git status` on baselines → only `deep_cross_scope_probe` snapshot + baseline changed.

**What We Know Works After This Phase:** the capability is documented, the agentic-mbse impact is
recorded for sync, and all gates hold. Item 2 is implement-complete → suggest `/_my_audit`.

---

## Environment Setup

**See CLAUDE.md for full environment rules.** Key: `uv run pytest tests/`; `mypy src/`;
`ruff check src/`; capture via `scripts/capture_*.py --fixtures deep_cross_scope_probe` (license needed
for live capture; the `--fixtures` filter is the byte-identity discipline). agentic-mbse is at
`/home/reid/1cfe/agentic-mbse` and sandbox-blocked (memory `agentic-mbse-repo-path`).

---

## Risk Management

**See design.md#potential-risks for the full analysis.** Phase-specific mitigations:
- **Phase 3 (climb):** the first-segment-shadowing single-hit shape is filed, not built (B2/M-1) — a code
  comment must name the assumption at the climb site; the corpus is safe (only one prefix hits `data_point`).
- **Phase 5 (re-capture):** the stale classification flip must be root-caused (code-correct vs
  baseline-correct) before commit; it reproduces on `ba3bca4`, so it is not this item's regression.
- **Phase 5 (parity):** the parity leg is `@requires_license`-gated and skipped in license-free CI —
  there the committed-snapshot channel pins are the only always-on guard; treat them as primary, the
  live parity as confirmation.

## Implementation Notes

[TO BE FILLED DURING IMPLEMENTATION]

### Phase 1 Completion
**Completed:** 2026-07-07
**Actual Changes:**
- `tests/conformance/test_deep_cross_scope_probe.py`: added `_DATA_POINT_CHANNEL`/`_BASE_METRIC_CHANNEL` constants (R1-anchored to snapshot instance QNs); flipped Pattern-A pin to resolves-to-channel; added base_metric channel pin; rewrote no-truncated-binding → full-path CHAIN assertion; rewrote offender-set docstring.
- `tests/unit/test_dependency_backtracker.py` (NEW): 4 climb tests (resolve/Step1-hit/refuse/2-seg-gate) + 2 Step-4 fallback tests (fires-on-shape WARN + silent-on-clean).
**Issues:** silent-on-clean initially caught an unrelated `phantom_detector` WARNING → scoped both silence assertions to the backtracker logger name.
**Deviations:** base_metric pin queries module `_DERIVED` directly, not the plan stencil's `f"{_DERIVED}__derived_calc"` (stencil typo; `_DERIVED` already is the full derived_calc EQN — verified against built graph module names).
**Red/green after phase:** RED (expected, flip in later phases) = Pattern-A channel pin, base_metric channel pin, full-path-binding pin, climb-resolve unit test, fallback-WARN unit test. GREEN = offender-set, pattern-b, silent-on-clean, base_metric-Step1, refuse, 2-seg-gate.

### Phase 2 Completion
**Completed:** 2026-07-07
**Actual Changes:**
- `extraction/usage_extractor.py`: 3+-segment FCE arm now emits full-path CHAIN (source_path only, N-1) instead of hard-reject UNBOUND; reject warning deleted.
- `tests/unit/test_extractor.py`: added `test_deep_chain_emits_full_path_chain_not_reject` (mock-based, mirrors existing OperatorExpression tests).
- `tests/conformance/test_deep_cross_scope_probe.py`: removed `test_pattern_a_deep_chain_warns_on_extraction` + `requires_license` import (see below).
**Issues:** `@requires_license` is NOT skipped in this environment (license loads for full pytest) — the extraction-warn test ran and failed after the D1 change. Removed it now rather than leave the suite red across phases 2–4.
**Deviations:** removed the license warn-test in Phase 2 (plan offered "remove here"); dropped `requires_license` import to avoid an unused-import lint window (Phase 5 re-adds both the import and a parity leg).
**Red/green after phase:** extractor tests all GREEN. Remaining RED (flip at Phase-5 re-capture) = the two offline channel pins + the full-path-binding pin. Gates: ruff 17, mypy 97 (unchanged).

### Phase 3 Completion
**Completed:** 2026-07-07
**Actual Changes:** `analysis/dependency_backtracker.py` `_resolve_chain_dispatch` — added the gated Step CLIMB after Step 2: for `source_path.count(".") >= 2`, iterate ancestor prefixes of `consumer_scope` (full → empty, dropping trailing segments), collect distinct non-self-reference `scoped_lookup` hits, resolve iff exactly one, refuse (return None) on ≥2. Reuses `_is_self_reference`. B2/M-1 filed-assumption comment at the site.
**Issues:** none.
**Deviations:** none. (Climb tests were authored/committed in Phase 1; this phase turns 3 of the 4 that were pending green — all 4 now green.)
**Red/green after phase:** climb resolve/Step1-hit/refuse/gate GREEN; full suite 2075 passed. Remaining RED = fallback-WARN (Phase 4) + 3 offline pins (Phase 5). Gates: ruff 17, mypy 97.

### Phase 4 Completion
**Completed:** 2026-07-07
**Actual Changes:** `analysis/dependency_backtracker.py` `_resolve_binding_via_registry` Step 4 — genuine `logger.warning` for a 3+-segment CHAIN (`"::" not in source_path and count(".") >= 2`) before the benign DEBUG line; names full untruncated chain + `usage_qn|param`. Entry-point disposition unchanged.
**Issues:** none. **Deviations:** none.
**Red/green after phase:** all 6 backtracker unit tests GREEN; full suite 2076 passed. Remaining RED = 3 offline pins (Phase 5). Gates: ruff 17, mypy 97.

### Phase 5 Completion
**Completed:** 2026-07-07
**Actual Changes:** Re-captured `deep_cross_scope_probe` extraction snapshot + computation_graph (both wires land: data_point→derived_value, base_metric→metric_value). Added `@requires_license` in-process parity leg. Fixed `_input_source_qn` helper to read `producer_channel` (a wired module_output stores its channel there, `qualified_name` is null) — this was latent in the Phase-1 helper and only surfaced once a real wire existed.
**Stale-flip root-cause verdict:** FULLY MOOTED — baseline-correct, not code-wrong. The stale classification flip's two target EPs (`chain_analysis.data_point`, `derived_calc.base_metric`) are exactly the two now-wired params; both vanish from the EP groups, so there is zero surviving residue and no reclassification on any remaining EP. (It reproduced on `ba3bca4` as non-aggregation staleness; the wires supersede it.)
**Issues:** the extraction diff also drops `unhandled: false` from every binding — pre-existing serialization catch-up (BindingInfo removed the field before this session), not this item. Verified BindingInfo has no `unhandled` field.
**Deviations:** `_input_source_qn` helper fix (producer_channel) — a Phase-1 helper bug, fixed here; faithful to the spec's "exact wired channel QN" intent.
**Red/green after phase:** conformance 7/7 GREEN; full suite 2080 passed. Byte-identity: only the target fixture's snapshot + baseline moved. Gates: ruff 17, mypy 97.

### Phase 6 Completion
**Completed:** 2026-07-07
**R2 disposition:** No agentic-mbse change required (recorded in `agentic-mbse-impact.md`) — the deep chain is already valid SysML agentic-mbse parses; no new construct or authoring rule. Shape recorded for a later sync.
**Docs:** doc 24 CHAIN-dispatch updated (Step CLIMB + Step-4 WARN); matrix gains REQ-BT-12/REQ-BT-13 (both PASS), counts recounted from rows.
**Final gate numbers (ruff / mypy):** ruff 17 (ceiling), mypy 97 (ceiling) — no regression. Full suite 2080 passed.
**Deviations:** committed the epic SC-B flip isolated to my hunk (git checkout HEAD + re-apply + commit + restore), because the epic file carried pre-existing sibling SC-A/SC-G flips at session start; left those uncommitted for their stages.

---

**Status**: Draft → In Progress → **Complete**
</content>
</invoke>
