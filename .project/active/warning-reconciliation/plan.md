# Implementation Plan: Resolution Matcher Fixes & Warning Reconciliation (SC-8)

**Status:** Draft
**Created:** 2026-07-05
**Last Updated:** 2026-07-05
**Epic Item:** UPSTREAM-FINDINGS Item 7
**Branch:** upstream-findings-epic

## Source Documents

- **Spec:** `.project/active/warning-reconciliation/spec.md`
- **Design:** `.project/active/warning-reconciliation/design.md` ← component details, seams, invariants, appendices
- **Design review + resolutions:** `.project/active/warning-reconciliation/design-review.md` (C1/C2/M1/m1/m2 all applied in design)
- **Epic (R1/R2/R3):** `.project/backlog/epic_upstream_findings.md`

**Read the design first.** This plan does not restate the mechanism, the six flip
sites, the partition table, or the worksheet — it references them. It adds only
phasing, ordering rationale, test stencils, and per-phase validation.

---

## Implementation Strategy

**Phasing rationale.** The three defects compound in a fixed order (resolve benign
misses → make residue loud → regen the churn they produce), so the phases follow
that order. Phase 0 must run *before any code change* because the before→after
behavioral diff is the R3 audit deliverable and is unrecoverable once a matcher
lands (design-review m1). The matcher fixes (Phase 1) are the behavioral root: they
reclassify entry points and change what the collector sees, so they precede the
collector/summary work (Phases 2–3) and the regen (Phase 4) that captures their
output.

**Critical path.**
Phase 0 (capture before-state) → Phase 1 (two matcher fixes + atomic six-site flip)
→ Phase 2 (V11 collector + strict boundary + summary + seeded fixture)
→ Phase 3 (warning demotion + alias summary + zero-WARNING assertions)
→ Phase 4 (behavioral baseline regen + three-part review) → Phase 5 (docs/matrix/notes).

**First proof point.** Phase 0's captured worksheet plus the Phase 1 unit test that
asserts `pack_count` resolves to the single design-attribute QN (leaf-unique branch,
Bug B) — that is the earliest signal the matcher fix behaves as the design predicts.

**Overall validation approach.**
- Each phase starts with tests (test-first).
- Suite green at every phase boundary. **Documented exception:** Phase 4 only, where
  the enumerated catf_mfe E2E tests move to `xfail` as an intended, tracked outcome.
- Baselines regenerate via capture scripts only (R3) — never hand-edited.

**Gate baseline (post Item 6, re-confirm at implement):** 1894 passed / 4 skipped /
5 xfailed; ruff 21; mypy 109. Ruff/mypy must end at or below these counts.

**Anchor.** Re-anchor line numbers and baseline bytes to the currently committed
state at implement (Item 6 landed; HEAD is `82df057`). Design line numbers are HEAD
`88115b8` — re-verify each before editing (design.md#appendix-a). The baseline regen
(Phase 4) diffs against whatever is committed when implement runs, not today's bytes.

**License note (R3).** Baseline regen and the Phase 0 warning capture are
**snapshot-driven** (`scripts/capture_pipeline_baselines.py` builds from
`extraction_snapshot.json`; `run_codegen` has a `--from-snapshot` path,
`cli/__init__.py:758-761`). No live syside license is needed for this item — confirm
the snapshots exist for solar_battery and catf_mfe before starting.

---

## Phase 0: Before-Baseline Capture & Leaf-Uniqueness Confirmation

### Goal
Capture the exact before-state so the behavioral diff (Phase 4, R3) is recoverable,
and confirm the one bet the design can be wrong on (B1 / leaf-uniqueness, D2).
Mandated as Phase 0 by design-review m1. **No code changes in this phase.**

### Assumption Under Test
B1 (design.md#key-bets): every design-attribute leaf that a binding reclassifies to
is **unique across the model's design attributes**, so leaf-name alone identifies the
def-owned target. If a real leaf collides, the D2 refuse-branch keeps it loud (safe),
but we need to know before we trust the mechanism.

### Test Stencil (Write This First)
This phase produces a captured worksheet, not code. The "test" is the recorded
before-state that later phases diff against. Record into the design's Appendix B.

```
# Phase 0 capture — run against the currently committed state, BEFORE any edit.
# 1. Warning lines (verbatim), snapshot-driven:
uv run sysml-codegen generate --from-snapshot tests/fixtures/solar_battery_model/extraction_snapshot.json ... 2>&1 | grep -E "Registry unresolved|alias collision"
uv run sysml-codegen generate --from-snapshot tests/fixtures/catf_mfe_model/extraction_snapshot.json     ... 2>&1 | grep -E "Registry unresolved|alias collision"
# 2. Params-JSON key+value sets: capture generated *_params.json per model (keys AND values).
# 3. Leaf-uniqueness (D2/B1): for each reclassification-target leaf, count design attributes carrying it.
assert count(design_attrs with name == "pack_count")  == 1   # unique → safe
assert count(design_attrs with name == "p_net_mw")    == 1
# 4. catf_mfe collector target confirmation: magnet_volume falls through, valueless, wired.
```

### Changes Required

**See `design.md` for:** the worksheet structure → `design.md#appendix-b`; the
Validation Approach's Phase-0 item → `design.md#validation-approach`; the de-risk
note → `design.md#next-stage-handoff`.

- [ ] Confirm `extraction_snapshot.json` exists for solar_battery and catf_mfe.
- [ ] Run `run_codegen` (snapshot-driven) on solar_battery and catf_mfe; record the
      **verbatim** "Registry unresolved" line set (~10 solar_battery) and the
      alias-collision line count (~25 of catf_mfe's 29).
- [ ] Capture the current `*_params.json` **key set AND default values** per model
      (this is the "before" half of B3's value-diff regression guard).
- [ ] Confirm leaf-uniqueness for every reclassification-target leaf
      (`pack_count`, `p_net_mw`, and any others surfaced by the run). Exactly one
      design attribute per leaf → B1 holds. If any leaf collides, STOP and record
      it — the design's escalation (usage→def plumbing) is out of this item's scope
      and needs a decision.
- [ ] Confirm the catf_mfe D4 target: `magnet_volume` is in `fallback_entry_points`,
      `default_value is None`, and wired into `cryo_load` (the INV-4 target).
- [ ] Confirm **V11 is free** at implement (V1–V10 in `modeling-assumptions.md`;
      verified free at plan time — V10 is the last used).
- [ ] Write all of the above into `design.md#appendix-b` (fill the "To fill at
      implement" list).

### Validation
**Automated:** none (capture-only phase).
**Manual:**
- [ ] Appendix B worksheet is filled: before key/value sets, verbatim warning lines,
      leaf-uniqueness table, catf_mfe fall-through confirmation.
- [ ] Leaf-uniqueness holds for every reclassification target (or a collision is
      recorded and escalated).

**What We Know Works After This Phase:**
The before-state is captured and recoverable; B1 is confirmed (or a collision is
surfaced before any code depends on it).

---

## Phase 1: Two Matcher Fixes + Atomic Six-Site Lockstep Flip

### Goal
Resolve the benign first-pass misses at the source: the `::`-QN per-segment
sanitize (Bug A) and the def-owned leaf-unique match (Bug B), and flip the FORMULA
sysml-QN registry to sanitized keys across all six sites in one change. This is the
behavioral root — entry points reclassify and Step-3 dedup returns here.

### Assumption Under Test
- B1/D2: the leaf-unique branch resolves `pack_count` to the single design-attribute
  QN and refuses on ambiguity (never cross-wires) — design.md#d2.
- B2: exactly six flip sites, no seventh — design.md#appendix-a, INV-1.
- B3: a correctly-resolving key keeps its value (value only moves where the
  design-attribute default genuinely differs from the usage literal) — design.md#key-bets.

### Test Stencil (Write This First)
Real fixtures, no mocks (R1). Unit-level on the backtracker; snapshot deferred to
Phase 4.

```
# tests/unit/analysis/test_dependency_backtracker.py (extend)
def test_def_owned_leaf_unique_resolves(solar_battery_snapshot):
    bt = backtracker_for(solar_battery_snapshot)
    qn = bt._resolve_to_design_attribute(attr_name="pack_count", parent_part="cost_model", ...)
    assert qn == "SolarBatteryLibrary__Battery_System__pack_count"   # def-name segment, PascalCase

def test_def_owned_leaf_ambiguous_refuses():
    # two design attrs sharing a leaf → None (fall to Step-4, kept loud), never a guess
    assert bt._resolve_to_design_attribute(attr_name="<colliding_leaf>", ...) is None

def test_quoted_owner_reference_matches_after_flip(quoted_owner_formula_snapshot):
    # Bug A: quoted-segment owner resolves through the sanitized FORMULA REFERENCE path
    result = bt.backtrack(...)
    assert kind_of(result, param) == "DESIGN_ATTRIBUTE"
```

### Changes Required

**See `design.md` for:**
- Def-owned branch shape (pseudo, ~6 lines) → `design.md#implementation-notes`
- The two matcher fixes at the resolution seam → `design.md#research-findings`
- D2 precedence (exact-first → leaf-unique → refuse) → `design.md#key-decisions`
- Six-site table (exact before → after) → `design.md#appendix-a`
- INV-1 (completeness grep), INV-2 (no cross-wire) → `design.md#required-invariants`

**Specific file changes** (re-verify line numbers against committed state first):

#### 1. Tests (write first)
**File:** `tests/unit/analysis/test_dependency_backtracker.py`
- [ ] Leaf-unique resolve test (`pack_count` → single design-attr QN, def-name segment).
- [ ] Leaf-ambiguous refuse test (returns None, no cross-wire — INV-2).
- [ ] Quoted-owner REFERENCE match test (Bug A, sanitized path).

#### 2. Matcher fix — def-owned leaf-unique branch (Bug B)
**File:** `src/sysml_codegen/analysis/dependency_backtracker.py` (`_resolve_to_design_attribute`, ~`:642`)
- [ ] After the existing exact `parent_part` match returns nothing, add the
      leaf-unique branch: gather candidates by `attr.name == attr_name` across all
      design attributes; exactly one → return its `qualified_name`; else return None.
      Per `design.md#implementation-notes` pseudo-code. **No QN-suffix guard** (C2:
      it was dead). **No same-file tiebreak** (C2: it can cross-wire).

#### 3. Matcher fix — `::`-QN per-segment sanitize (Bug A) + six-site flip
**Files (all six, one atomic change — `design.md#appendix-a`):**
- [ ] Site 1 — `orchestration/output_registry_builder.py:130` (registration): wrap key in `sanitize_qualified_name`.
- [ ] Site 2 — `analysis/dependency_backtracker.py:595` (primary REFERENCE consumer): sanitize `source_path` before `sysml_qn_lookup`.
- [ ] Site 3 — `analysis/dependency_backtracker.py:660` (`_resolve_to_design_attribute` `::` branch): `sysml_to_python_qualified_name` → `sanitize_qualified_name` (this is Bug A).
- [ ] Site 4 — `orchestration/pipeline_builder.py:70` (`_remove_formula_from_design_attrs` twin): bare swap → `sanitize_qualified_name`.
- [ ] Site 5 — `resolution/input_resolver.py:120` (Strategy B, 2nd consumer): sanitize `ref` before `sysml_qn_lookup`.
- [ ] Site 6 — `analysis/parameter_groups.py:439` (`_find_source_file` twin): bare swap → `sanitize_qualified_name`.

#### 4. [HARD] Completeness grep stop (INV-1)
- [ ] After the flip, grep the whole `src/` for any remaining bare
      `sysml_to_python_qualified_name` on a comparison-bound QN and any raw
      `sysml_qn_lookup(SysMLQN(...))` without a `sanitize_qualified_name` wrap. **Zero
      hits at the six sites is the gate.** A leftover raw site silently re-breaks
      quoted-owner matching (B2). This is a hard stop — do not proceed to Phase 2
      until clean.

### Validation
**Automated:**
- [ ] New backtracker unit tests → pass.
- [ ] Full suite → green **except** the catf_mfe/solar_battery snapshot-baseline
      tests, which now diff (reclassification churn is expected; they are regenerated
      in Phase 4). Record exactly which baseline tests go red here so Phase 4 closes
      the same set — no other test should regress.
- [ ] ruff / mypy → at or below baseline (21 / 109).

**Manual:**
- [ ] Completeness grep → zero hits (INV-1).
- [ ] The set of newly-red tests is exactly the baseline-comparison tests, nothing else.

**What We Know Works After This Phase:**
Benign misses resolve at the right stage with the right ADR-001 kind; the FORMULA
REFERENCE path works on quoted owners; the flip is byte-invariant on baselines
(INV-6 — only the matcher fixes churn bytes, and those are Phase-4 regen targets).

---

## Phase 2: V11 Collector + Always-Strict Boundary + Reconciliation Summary + Seeded Fixture

### Goal
Make the genuine residue loud and precise. Add the pure `collect_uncovered_params`
collector, the always-strict V11 raise at the generation boundary, the post-assembly
reconciliation summary (the M1 partition: wired → V11 abort, unwired → WARNING), and
a seeded fixture that proves V11 fires independently of catf_mfe.

### Assumption Under Test
- D4: V11's population is `fallback_entry_points` ∩ valueless ∩ wired — it catches
  the genuine dangle without aborting valid required-user-fill models (design-review
  C1, the narrowed predicate) — design.md#d4.
- INV-3: the collector is pure (returns a list, raises nothing); only the boundary
  raises — design.md#required-invariants.
- INV-4: catf_mfe collector returns exactly `[cryo_load.magnet_volume]`.

### Test Stencil (Write This First)
```
# tests/unit/resolution/test_uncovered_params.py (new)
def test_collector_is_pure_on_clean_graph(solar_battery_graph):
    assert collect_uncovered_params(solar_battery_graph) == []   # no raise (INV-3)

def test_collector_pins_catf_mfe_dangle(catf_mfe_graph):
    result = collect_uncovered_params(catf_mfe_graph)
    assert [ (u.module, u.input) for u in result ] == [("cryo_load", "magnet_volume")]  # INV-4

def test_seeded_fixture_raises_v11(seeded_uncovered_snapshot):
    # strict generation aborts on exactly the one seeded input
    with pytest.raises(GenerationError, match="V11"):
        run_codegen(config_for(seeded_uncovered_snapshot))
```

### Changes Required

**See `design.md` for:**
- Collector = fell-through ∩ valueless ∩ wired → `design.md#d4`
- Partition table (V11 wired-abort vs summary WARNING) → `design.md#architecture` (V11 vs. summary)
- Generation-boundary placement (after `build_pipeline_context`, beside
  `_check_duplicate_output_paths`; summary logged first, then V11 raised) → `design.md#architecture` seam 4
- V11 message (V-style) and summary format → `design.md#implementation-notes`
- Seeded-fixture shape (real SysML, must NOT collide with leaf-unique matcher) → `design.md#implementation-notes`

**Specific file changes:**

#### 1. Tests (write first)
**File:** `tests/unit/resolution/test_uncovered_params.py` (new)
- [ ] Collector purity on a clean graph (INV-3).
- [ ] catf_mfe collector-list pin `== [cryo_load.magnet_volume]` (INV-4).
- [ ] Seeded-fixture strict generation raises V11.

#### 2. `fallback_entry_points` field
**File:** `src/sysml_codegen/analysis/dependency_backtracker.py` (`BacktrackingResult`, ~`:74`; Step-4 site ~`:555`)
- [ ] Add `fallback_entry_points` set field on `BacktrackingResult`; populate it at
      the Step-4 fallback site.
**File:** `src/sysml_codegen/resolution/graph_builder.py` (`build_computation_graph`)
- [ ] Propagate `fallback_entry_points` onto `ComputationGraph` so the collector is
      pure over the graph alone (deliberate schema rev — R1; REQ-GA-08 / doc 07/09).

#### 3. Collector
**File:** `src/sysml_codegen/resolution/graph_builder.py` (sibling to `_validate_channel_references:612`)
- [ ] `collect_uncovered_params(graph) -> list[UncoveredInput]`: an `entry_point`
      input is a violation when its `qualified_name` is in `fallback_entry_points`,
      its EP `default_value is None`, and a surviving module input references it. Pure
      (INV-3). `UncoveredInput` names module, input, missing key.

#### 4. Strict boundary + summary
**File:** `src/sysml_codegen/cli/__init__.py` (`run_codegen`, after `build_pipeline_context`, beside `_check_duplicate_output_paths:773`)
- [ ] Log the reconciliation summary (WARNING, unwired remainder) **first**, then
      call `collect_uncovered_params` and **raise V11** on any non-empty result
      (always strict, no escape-hatch flag). Ordering ensures the digest reaches the
      operator even when generation aborts.

#### 5. Seeded fixture
**File:** `tests/fixtures/<seeded_uncovered>/...` (new, real SysML)
- [ ] Minimal model (2–3 defs): one calc usage binds an input (non-literal) to a
      dotted reference matching no resolution strategy and no design attribute → one
      EP in `fallback_entry_points`, `default_value=None`, wired. **The referenced
      leaf must NOT name a real design attribute** (or the leaf-unique matcher would
      resolve it). Capture its extraction snapshot.
- [ ] Confirm the fall-through path at implement (the design session could not run
      codegen).

#### 6. V11 diagnostic registration
**File:** `docs/architecture/modeling-assumptions.md` (Validation Rules) — full doc pass in Phase 5, but reserve V11 now.
- [ ] Reserve V11 (confirm still free — done at plan time).

### Validation
**Automated:**
- [ ] Collector unit tests → pass (purity, catf_mfe pin, seeded raise).
- [ ] Full suite → green except the Phase-1 baseline-comparison tests (still pending
      Phase 4 regen) and the catf_mfe E2E generate path (which now raises V11 — this
      becomes the Phase 4 xfail; confirm no *other* test regresses).
- [ ] ruff / mypy → at or below baseline.

**Manual:**
- [ ] Seeded fixture: `collect_uncovered_params` returns exactly its one seeded input;
      strict generation raises V11 with the module/input/key named.
- [ ] catf_mfe collector list is exactly `[cryo_load.magnet_volume]` (INV-4).

**What We Know Works After This Phase:**
The genuine dangle hard-fails precisely (V11), a valid required-user-fill model does
not (narrowed predicate, C1), and the check fires independently of catf_mfe (seeded
fixture, B4). The collector is pure and does not trip strict enforcement (INV-3).

---

## Phase 3: Warning Demotion + Alias Count-Summary + Zero-WARNING Assertions

### Goal
Silence the benign per-binding noise and collapse the repetitive alias-collision
lines, then lock the result: clean fixtures generate with zero WARNING lines.

### Assumption Under Test
INV-5: after the matcher fixes and demotions, the clean fixtures (solar_battery,
chain_spike, attr_expr_probe — confirm the set against Phase 0 live output) emit
**zero** WARNING lines over a full `run_codegen` — design.md#validation-approach.

### Test Stencil (Write This First)
```
# tests/unit/test_warning_reconciliation.py (new) — capture logs at WARNING level
def test_clean_fixture_zero_warnings(caplog, solar_battery_config):
    with caplog.at_level(logging.WARNING):
        run_codegen(solar_battery_config)
    assert [r for r in caplog.records if r.levelno >= logging.WARNING] == []  # INV-5

def test_alias_collisions_collapse_to_one_summary(caplog, catf_mfe_config):
    # 25 per-collision lines → one count-summary line
    warnings = [r.message for r in caplog.records if r.levelno == logging.WARNING]
    assert sum("alias collision" in m for m in warnings) == 0            # per-line gone
    assert sum(m.startswith("OutputRegistry:") for m in warnings) == 1   # one summary
```

### Changes Required

**See `design.md` for:**
- D5 (per-binding → DEBUG, summaries at WARNING when non-empty) → `design.md#key-decisions`
- Alias count-summary format and Step-4 demotion → `design.md#implementation-notes`
- Registry-build seam (alias accumulator on `OutputRegistry`) → `design.md#architecture` seam 1
- INV-5 (zero-WARNING clean fixtures) → `design.md#required-invariants`

**Specific file changes:**

#### 1. Tests (write first)
**File:** `tests/unit/test_warning_reconciliation.py` (new)
- [ ] Zero-WARNING assertion per clean fixture (INV-5; set confirmed in Phase 0).
- [ ] Alias per-collision lines gone; exactly one count-summary line.

#### 2. Per-binding Step-4 demotion
**File:** `src/sysml_codegen/analysis/dependency_backtracker.py` (Step-4 line ~`:555`)
- [ ] Demote the per-binding "Registry unresolved" line from WARNING to DEBUG (the
      summary in Phase 2 replaces it as the operator digest).

#### 3. Alias-collision accumulator + count-summary
**File:** `src/sysml_codegen/core/output_registry.py` (`register_alias`, per-collision line ~`:112`)
- [ ] Record collisions on `OutputRegistry`; demote per-collision line to DEBUG.
**File:** `src/sysml_codegen/orchestration/output_registry_builder.py`
- [ ] Emit one WARNING count-summary after Phase 1a–4:
      `OutputRegistry: N alias collision(s) resolved first-wins (M distinct keys).`

### Validation
**Automated:**
- [ ] Zero-WARNING clean-fixture tests → pass (INV-5).
- [ ] Alias count-summary test → pass.
- [ ] Full suite → green except the still-pending Phase-1 baseline tests and the
      catf_mfe E2E (Phase 4). No new regressions.
- [ ] ruff / mypy → at or below baseline.

**Manual:**
- [ ] Run `run_codegen` on each clean fixture at WARNING level → no line emitted.
- [ ] catf_mfe: the ~25 alias lines are one summary; the surviving WARNING is the
      reconciliation summary + (on the E2E path) V11.

**What We Know Works After This Phase:**
Clean fixtures are silent (INV-5); the alias noise is one line; the SC-5 cross-part
cases stay loud (summary/V11), not demoted to INFO (D5).

---

## Phase 4: Behavioral Baseline Regen + Three-Part Review

### Goal
Capture the intended behavioral churn into regenerated baselines and produce the R3
audit deliverable: the three-part before→after review (keys, values, release-notes
enumeration). Move the enumerated catf_mfe E2E tests to `xfail`.

### Assumption Under Test
B3: every correctly-resolving key keeps its value; only genuinely-different values
move — and the review procedure *catches* any that shouldn't. This is the regression
class the procedure exists for, not an assumption to trust (design.md#key-bets).

### Test Stencil (This Phase Regenerates, Then Asserts)
```
# One-item regen discipline (R3): capture scripts only, never hand-edit.
uv run python scripts/capture_pipeline_baselines.py     # computation_graph.json per model
uv run python scripts/capture_baseline_yaml.py          # pipeline YAML (if churned)
# Then the three-part review against Phase 0's captured before-state:
#   1. keys:   diff before→after params-JSON key sets (dedup collapses enumerated)
#   2. values: diff before→after default values at key level (B3 — silent value change is the target)
#   3. notes:  enumerate reclassified EPs + collapsed keys + value moves in release notes
# xfail exactly the enumerated catf_mfe E2E set:
@pytest.mark.xfail(reason="catf_mfe magnet_volume cross-part gap — Items 9–11; V11 fires by design")
```

### Changes Required

**See `design.md` for:**
- Reclassification worksheet (before anchors, value column = B3) → `design.md#appendix-b`
- catf_mfe E2E xfail set (enumerate live) → `design.md#validation-approach`
- Behavioral-review procedure (keys, values, notes) → `spec.md` "Behavioral-review procedure"
- One-item-regen discipline, capture scripts only → `design.md#potential-risks` (Item 6 baseline drift), R3

**Specific changes:**

#### 1. Regenerate baselines (capture scripts only — R3)
- [ ] Run the capture scripts for the affected models (solar_battery, catf_mfe, and
      any other model whose keys reclassified). Review each diff deliberately — the
      diff is expected non-empty and *correct*.
- [ ] Confirm the Phase-1 red baseline tests now pass against regenerated bytes, and
      that no *unexpected* baseline (a clean fixture that shouldn't have moved) churned.

#### 2. catf_mfe E2E xfail (enumerate live)
**Files:** `tests/e2e/test_computed_attributes_e2e.py::test_catf_mfe_still_works`, and
each test consuming the class-scoped `catf_mfe_output` fixture in
`test_expression_compilation_e2e.py::TestCATFMFEValidation`.
- [ ] Enumerate the exact set at implement (spec-review L2-1: the class-scoped fixture
      cascades). Prefer structuring the check so generation still completes for the
      non-coverage assertions if cheap; otherwise `xfail` each with a reason tracked
      to Items 9–11.
- [ ] Keep the collector-list test (`== [cryo_load.magnet_volume]`) as a **green**
      assertion (it does not trip strict enforcement — INV-3).

#### 3. Three-part review deliverable
- [ ] Keys: before→after params-JSON key-set diff per model; enumerate every dedup
      collapse (e.g. `battery_bos__cost_model__pack_count` + `battery_system__pack_count`
      → `battery_system__pack_count`).
- [ ] Values: before→after default-value diff at key level (B3). Confirm no clean
      fixture value moved; enumerate every value that *did* move with its cause
      (USAGE_LITERAL → DESIGN_ATTRIBUTE default-source switch).
- [ ] Notes: write the enumeration into this item's release notes (Phase 5 lands the
      file; this phase produces its content).

### Validation
**Automated:**
- [ ] Full suite → green **except** the enumerated catf_mfe E2E xfails (the one
      documented exception, this phase only). All Phase-1 baseline tests now green.
- [ ] `test_live_vs_snapshot_byte_identical` (if present) → green post-regen.
- [ ] ruff / mypy → at or below baseline.

**Manual:**
- [ ] Three-part review complete: key diff, value diff, enumeration all recorded.
- [ ] Every reclassified key's value change is explained; no silent value change (B3).
- [ ] The xfail set is exactly the enumerated catf_mfe E2E tests — nothing broader.

**What We Know Works After This Phase:**
The behavioral churn is captured, reviewed, and correct; the known catf_mfe gap is a
tracked xfail (not a suppressed test); the value-level regression guard passed.

---

## Phase 5: Docs, Verification Matrix, Release Notes, agentic-mbse Impact

### Goal
Move docs with code (R1), add verification-matrix rows for the new REQs, land the
release notes (three-part enumeration from Phase 4), and record the agentic-mbse
impact (R2).

### Assumption Under Test
None (documentation phase). Validates completeness against R1/R2.

### Changes Required

**See `design.md` for:** Integration Strategy doc list → `design.md#integration-strategy`;
`spec.md` "Diagnostics & Requirement Numbering" for REQ IDs and doc targets.

- [ ] Doc 11 (analysis-backtracker) + Doc 24 (dual-resolution-architecture): the two
      matcher fixes + dispatch (REQ-BT-09, REQ-BT-10).
- [ ] Doc 10 (output-registry): FORMULA sysml-QN registered sanitized (REQ-OR-09).
- [ ] Doc 17 (parameter-group-deriver): def-owned ownership note; REQ-PGD-08 reframe
      to "confirmed no deriver change required" (D1) or retire.
- [ ] Doc 07 (graph-assembly): V11 collector, sibling to REQ-GA-03 (REQ-GA-08).
- [ ] `modeling-assumptions.md`: V11 in Validation Rules + the SC-8 behavioral note.
- [ ] Verification-matrix rows: REQ-BT-09/10, OR-09, PGD-08, GA-08, V11.
- [ ] m2 correction: README null-key note at `entry_point.py:118` — the JSON template
      **omits** null-default keys; the schema declares them required for user fill.
- [ ] Release notes: the three-part enumeration (reclassified EPs, collapsed keys,
      value moves) from Phase 4.
- [ ] agentic-mbse impact list in the (future) close-out: expected minor/none; record
      the Level-6 candidate check (a design-attribute binding whose `*_params` key is
      never covered — the model-side mirror of V11) as an Item-12 candidate; confirm
      whether the def-owned shape needs a MODELING_GUIDE guidance note.

### Validation
**Automated:**
- [ ] Full suite → green except the Phase-4 catf_mfe xfails.
- [ ] ruff / mypy → at or below baseline.
- [ ] Doc-link / verification-matrix consistency check (if the repo has one).

**Manual:**
- [ ] Every touched component has a doc + matrix row (R1).
- [ ] Release notes enumerate keys, values, and reclassifications (spec success
      criterion).
- [ ] agentic-mbse impact recorded (R2).

**What We Know Works After This Phase:**
Docs and REQs move with code; the behavioral churn is enumerated in release notes;
the agentic-mbse impact is filed for Item 12.

---

## Environment Setup

**See CLAUDE.md for full environment rules.** Key commands:
- Tests: `uv run pytest tests/`
- Single test: `uv run pytest tests/unit/... -k test_name`
- Type check: `uv run mypy src/`  (baseline 109)
- Lint: `uv run ruff check src/`  (baseline 21)
- Codegen (snapshot-driven, no license): `uv run sysml-codegen generate --from-snapshot ...`
- Baseline regen (R3, capture scripts only): `uv run python scripts/capture_pipeline_baselines.py`

---

## Risk Management

**See `design.md#potential-risks` for detailed risk analysis.**

**Phase-Specific Mitigations:**
- **Phase 0**: B1/leaf-uniqueness de-risked first (design's "de-risk first"). A real
  leaf collision → the D2 refuse-branch keeps it loud (safe), but STOP and record —
  usage→def plumbing is out of scope and needs a decision.
- **Phase 1**: the six-site flip is atomic; the [HARD] completeness grep (INV-1) is a
  hard stop against a leftover raw site (B2). No same-file tiebreak (C2 — cross-wire risk).
- **Phase 2**: V11 predicate narrowed to fell-through ∩ valueless ∩ wired (C1) — it
  does not abort valid required-user-fill models. Seeded fixture must not collide with
  the leaf-unique matcher.
- **Phase 4**: one-item-regen discipline; capture scripts only (R3); re-anchor to the
  committed post-Item-6 state (baseline-drift risk). The value-level diff (B3) is the
  regression guard, not a rubber stamp. The xfail footprint is wider than one mark
  (class-scoped fixture cascade — spec-review L2-1); enumerate the full set.

---

## Implementation Notes

[TO BE FILLED DURING IMPLEMENTATION]

### Phase 0 Completion
**Completed:** [Timestamp]
**Actual:** [Verbatim warning lines, before key/value sets, leaf-uniqueness result]

### Phase 1 Completion
**Completed:** [Timestamp]
**Actual / Issues / Deviations:** [...]

### Phase 2 Completion
### Phase 3 Completion
### Phase 4 Completion
### Phase 5 Completion

---

**Status**: Draft → In Progress → Complete
