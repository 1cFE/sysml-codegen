# Implementation Plan: Part-Usage Type Indexing (SC-3)

**Status:** Draft
**Created:** 2026-07-05
**Last Updated:** 2026-07-05
**Epic:** UPSTREAM-FINDINGS — Item 4

## Source Documents
- **Spec:** `.project/active/type-indexing/spec.md`
- **Design:** `.project/active/type-indexing/design.md` ← component details, bets, decisions, invariants
- **Design review:** `.project/active/type-indexing/design-review.md` (resolutions applied to design)
- **Epic R1/R3:** `.project/backlog/epic_upstream_findings.md`

---

## Implementation Strategy

**The change in one line.** Two extraction sites pick a usage's type by list position
(`next(iter(usage.types))`); replace both with a heritage-walk over owned `FeatureTyping`
relationships, index the usage under *all* its user-model types, and tiebreak the one genuine
collision (`design.md#core-concept`).

**Phasing Rationale — de-risk hardest-first, then license-free foundation, then behavior, then invariance:**

- **Phase 0 (probe gate)** runs first because the whole approach rests on two bets the sandbox
  could not test: heritage is owned-only (**B1**) and plain-subtype `.types` excludes user
  supertypes (**B2-plain**). Both are **hard stops** if false — see `design.md#key-bets`. No code
  is written until the probe clears them.
- **Phase 1 (helpers + `most_specific` unit test)** builds the three shared primitives and unit-tests
  the specialization comparison. This is **license-free** and is the first proof point — it collapses
  the D2/V10 logic risk without a live parser.
- **Phase 2 (three fixes + fixture + snapshot + conformance)** applies FIX 1/2/3 at the two sites and
  the dedup, backed by the six-shape retype fixture and its live snapshot.
- **Phase 3 (baseline zero-diff + docs)** proves the 4 baselines are byte-identical (the hard gate that
  backstops B2-plain + B3) and lands docs/matrix/REQ tags + the agentic-mbse impact record.

**Critical Path:** Phase 0 probe clears B1/B2-plain → helpers → three fixes → live snapshot →
baseline zero-diff. A false B1 or B2-plain halts the item at Phase 0.

**First Proof Point:** `most_specific` unit test (Phase 1) — comparable pair returns the chain sink,
incomparable pair returns sorted-first + signals the V10 path. Proves the core comparison before any
license-gated work.

**Overall Validation Approach:** Suite green at every phase boundary. Extraction assertions run against
the committed snapshot (no mocks — R1). Baseline invariance is a **runtime re-run**, not inspection
(`design.md#validation-approach` step 4).

**Concurrency note (Item 3 in flight).** Item 3 is editing `extractor.py` in the working tree and has
already added **V8** (anonymous-return diagnostic) to `modeling-assumptions.md` and `return_styles` to
the snapshot CLI. Item 4 touches **different files** (`usage_extractor.py`, `hierarchy_resolver.py`) —
no code overlap. Two sequencing rules:
- The `modeling-assumptions.md` §5 / V-table edit (Phase 3) **appends** V9/V10 after whatever V-rows
  are committed at execution time. V8 is Item 3's; do not renumber it.
- If Item 3 has not yet committed when you reach Phase 3, still claim **V9/V10** (V8 is spoken for).

---

## Phase 0: Probe Gate (no code)

### Goal
Execute the design's node-shape probe to settle the two load-bearing bets (B1, B2-plain), the
multi-typing branch (D2/V10), and the two open mechanism questions (heritage accessor, user filter).
Record outcomes in Implementation Notes. **B1-false and B2-plain-false are HARD STOPS.**

### Assumption Under Test
- **B1** — `usage.heritage` yields *owned* FeatureTyping targets, not typings inherited up the
  supertype chain (`design.md#key-bets` B1; gated by **Q2**, escalates to **Q3**).
- **B2-plain** — a plain `part x : Subtype` usage's `.types` excludes its user supertype (`design.md#key-bets`
  B2; gated by **Q1** on the `plain_hif` shape).
- **D2 incomparable branch** — a usage with two unrelated owned typings yields two targets (Q2b).
- **Q4** — `elements_of_type(model,"PartDefinition")` excludes the standard library (decides the user filter).

### Run
```bash
uv run --env-file ~/1cfe/agentic-mbse/.env \
  python .project/active/type-indexing/probe/probe.py
```
Probe files: `probe/probe.py` + `probe/model.sysml` (already prepared; shapes cover
`Variant.driver` retyped, `plain_hif` plain-subtype, `multi` two-unrelated-typing).

### Gate — read each answer against `design.md#implementation-notes`

- [ ] **Q1** — `Variant.driver` `.types` has declared type (`HIF Driver`) **last**; `plain_hif` `.types`
      **excludes** `IFE Driver`. → confirms B2-plain. **If `plain_hif` includes `IFE Driver` → B2-plain
      false → HARD STOP: report, do not proceed** (superset indexing would shift every baseline).
- [ ] **Q2** — `Facility.driver` → one owned typing `IFE Driver`; `Variant.driver` → `HIF Driver`
      **only** (not also `IFE Driver` via inheritance). → confirms B1 (heritage is owned-only). **If
      heritage climbs the chain → go to Q3.**
- [ ] **Q3** (gating *iff* Q2 shows climbing) — is there an owned-only accessor
      (`owned_relationships`/`declared_type`/`owned_typings`)? **If none → B1 false → HARD STOP: report
      and halt pending a new approach; do NOT improvise a heritage filter** (`design.md#implementation-notes`).
- [ ] **Q2b** — `multi` yields two owned FeatureTyping targets (`IFE Driver`, `Other Driver`); record
      their order → locks D2's incomparable branch + V10 wording.
- [ ] **Q4** — `PartDefinition` list excludes `Part`? **Yes** → `user_qn_set` intersection is the whole
      filter. **No** → fall back to source-document filtering (`design.md#implementation-notes` Q4).

### Validation
- [ ] All five answers recorded verbatim in **Implementation Notes → Phase 0**.
- [ ] B1 and B2-plain both confirmed (or the item is halted with a written report).

**What We Know After This Phase:** the exact heritage accessor, the user-filter mechanism, the
multi-typing order — the three things the helper is otherwise written blind against.

---

## Phase 1: Shared Helpers + `most_specific` Unit Test

### Goal
Build the three shared primitives (`design.md#component-overview`) and unit-test the specialization
comparison. License-free; first proof point.

### Assumption Under Test
That most-specific comparison over PartDef heritage (D2) returns the chain sink for comparable QNs and a
deterministic sorted-first for incomparable QNs — the logic behind both V10 and the V9 tiebreak.

### Test Stencil (Write This First)
```python
# tests/unit/test_type_indexing_helpers.py  (NEW)
def test_most_specific_returns_chain_sink():
    # HIF :> IFE ; qn_to_partdef built from the two PartDef elements
    winner, incomparable = most_specific(["...IFE_Driver", "...HIF_Driver"], qn_to_partdef)
    assert winner == "...HIF_Driver"
    assert incomparable is False

def test_most_specific_incomparable_is_sorted_first():
    winner, incomparable = most_specific(["...Other_Driver", "...IFE_Driver"], qn_to_partdef)
    assert incomparable is True
    assert winner == sorted(["...Other_Driver", "...IFE_Driver"])[0]

def test_most_specific_single_target_no_warning():
    assert most_specific(["...IFE_Driver"], qn_to_partdef) == ("...IFE_Driver", False)
```
(Build the tiny `qn_to_partdef` lookup from a live-loaded probe model, or a minimal fixture; the two
PartDefs suffice. Skip cleanly without a license, mirroring `_load_live_extractor` in
`test_return_style_extraction.py`.)

### Changes Required

**See `design.md#component-overview` for signatures and `design.md#key-decisions` D1/D2/D4.**

#### 1. Test file
**File:** `tests/unit/test_type_indexing_helpers.py` (NEW — write first)
- [ ] Implement the three stencil cases above (comparable, incomparable, single).
- [ ] Add zero-target case (`most_specific([], …)` → skip/None per `design.md#implementation-notes`).

#### 2. Shared helpers
**File:** `src/sysml_codegen/extraction/usage_extractor.py` (home of the primitives; importable by `hierarchy_resolver.py`)
- [ ] `owned_feature_typing_targets(usage) -> list[Any]` — walk `usage.heritage`, filter `FeatureTyping`,
      return targets in heritage order. Mirrors `_get_calc_def_name` (`extractor.py:354-364`) but returns
      **all** targets, not the first name. **Use the accessor Phase 0 confirmed** (raw `heritage` if B1
      held on it; the owned-only accessor if Q3 was promoted).
- [ ] `user_partdef_types(usage, user_qn_set) -> list[str]` — map `usage.types` to `__`-form QNs via
      `build_element_qualified_name`, keep those in `user_qn_set`. Index-only projection.
- [ ] `most_specific(qns, qn_to_partdef) -> tuple[str, bool]` — pairwise specialization-chain reduction
      (D2); returns `(winner, incomparable)`. Driven by a prebuilt `{qn: PartDefElement}` lookup — **never**
      an O(partdefs) scan per call (m5).
- [ ] Keys/values are plain `__`-form `str` — **not** `SysMLQN` (that is the `::`-form; D4 / M1).

### Validation
- [ ] `uv run pytest tests/unit/test_type_indexing_helpers.py` → pass.
- [ ] `uv run pytest tests/` → no regressions (helpers are additive; no call site changed yet).
- [ ] `uv run mypy src/` and `uv run ruff check src/` → clean.

**What We Know After This Phase:** the comparison logic is correct and deterministic, verified without a
license. The two fix sites can now consume it.

---

## Phase 2: Three Fixes + Retype Fixture + Snapshot + Conformance

### Goal
Wire the helpers into the two sites (FIX 1, FIX 2) and the dedup (FIX 3), backed by the six-shape retype
fixture and its committed live snapshot. This is where the bug is actually fixed.

### Assumption Under Test
That superset indexing makes the retyped usage instantiate both its subtype- and supertype-owned
templates (shapes 1/2), differently-named templates both survive (shape 4), same-named collide to the
most-specific winner + V9 (shape 3), and the plain sibling is untouched (shape 5).

### Test Stencil (Write This First)
```python
# tests/conformance/test_type_indexing.py  (NEW)
# Offline assertions on the committed retype_model snapshot (license-free layer).
def test_retyped_usage_indexed_under_both_types(retype_snapshot):
    # INV-1: driver keyed under {IFE Driver, HIF Driver}
    assert index_keys_for(retype_snapshot, "driver") == {"...IFE_Driver", "...HIF_Driver"}

def test_subtype_and_supertype_templates_both_instantiate(retype_snapshot):
    # shapes 1 + 2
    assert has_virtual(retype_snapshot, "...__hif_calc")
    assert has_virtual(retype_snapshot, "...__ife_calc")

def test_same_named_collision_tiebreak_and_v9(retype_snapshot):
    # shape 3: HIF (most-specific) wins the shared virtual QN; V9 names both owners
    assert winner_owner(retype_snapshot, "...__shared_calc") == "...HIF_Driver"
    assert any("Template collision" in w for w in retype_snapshot["warnings"])

def test_plain_sibling_not_reached_by_supertype_template(retype_snapshot):
    # shape 5 negative — Non-Goal guard
    assert not has_virtual(retype_snapshot, "...plain_x__ife_calc")

def test_usage_type_map_resolves_retyped_to_declared(retype_snapshot):
    assert usage_type(retype_snapshot, "driver") == "...HIF_Driver"
```
(Follow the offline-snapshot pattern in `test_return_style_extraction.py`: `load_extraction_snapshot`
+ a `snapshot_fixture` from `tests/conftest.py`.)

### Changes Required

**See `design.md#architecture` (three fix points), `design.md#required-invariants` INV-1..5, and
`design.md#validation-approach` step 1 (fixture shapes).**

#### 1. Fixture (shapes 1–5, one file per D5)
**File:** `tests/fixtures/retype_model/*.sysml` (NEW — write first)
- [ ] Facility/Variant retype design carrying: shape 1 (subtype-owned template on `:>> driver`),
      shape 2 (supertype-owned template, flow preserved), shape 3 (same-named calc on both → collision),
      shape 4 (differently-named calcs on both → both instantiate), shape 5 (plain `part x : 'HIF Driver'`
      sibling — supertype template must not reach it). Shapes 1–4 compose in one Facility/Variant;
      shape 5 is a sibling plain usage (D5).

#### 2. Conformance test
**File:** `tests/conformance/test_type_indexing.py` (NEW — write with the fixture, before the fixes)
- [ ] Implement the five stencil assertions above (offline snapshot layer).
- [ ] Add a live-extractor layer (skips without license) if a shape needs raw-extraction detail.
- [ ] Tag REQ-EXT-13 (superset index), REQ-EXT-14 (collision policy), REQ-LVP-08 (`usage_type_map`).

#### 3. FIX 1 — superset index
**File:** `src/sysml_codegen/extraction/usage_extractor.py:144-170` (`_build_part_usage_index`)
- [ ] Build `user_qn_set` and the `qn_to_partdef` lookup **once** from `elements_of_type(model,"PartDefinition")`
      (filter per Phase 0 Q4).
- [ ] Key each usage under the **set union** of `owned_feature_typing_targets(usage)` (as QNs) and
      `user_partdef_types(usage, user_qn_set)` — build the per-usage key set as a `set` (INV-1 / m7): the
      declared type is in both, naive concat would double-list it.
- [ ] Update the docstring (it currently says "resolves its typed PartDefinition via `usage.types`").

#### 4. FIX 2 — most-specific `usage_type_map` + V10
**File:** `src/sysml_codegen/extraction/hierarchy_resolver.py:526-533`
- [ ] Replace `next(iter(member.types))` with
      `most_specific([qn for t in owned_feature_typing_targets(member)], qn_to_partdef)`.
- [ ] Build `qn_to_partdef` once in `extract_hierarchy_data` (not per member).
- [ ] On `incomparable is True`, append **V10** to `warnings` and `logger.warning` (text in
      `design.md#implementation-notes`; dedup natural, one per `(owning_qn, name)`).
- [ ] Zero targets → no map entry (as today); import the helpers from `usage_extractor`.

#### 5. FIX 3 — collision tiebreak + V9
**File:** `src/sysml_codegen/extraction/usage_extractor.py:306,328-332` (`_expand_template_calc_usages`)
- [ ] Change `seen_qns: set[str]` → `seen_qns: dict[str, CalcUsageData]` (virtual QN → winning virtual, D3).
- [ ] On a second arrival at an existing QN: if the stored virtual's `owning_part_def_qn` (line 266)
      equals the incoming owner → silent (idempotent multi-path). If owners differ → `most_specific`
      picks the keeper, replace if needed, append **V9** once per collision class
      (dedup key `(owner_a, owner_b, calc_name)`; text in `design.md#implementation-notes`).
- [ ] **Do NOT touch** the `no PartUsage instantiations — dropped` warning (line 318-326) — Level-6
      check depends on it (`design.md#implementation-notes`).

#### 6. Snapshot capture
**File:** `scripts/capture_extraction_snapshots.py:41-50` (MODELS)
- [ ] Add `"retype_model": FIXTURES_DIR / "retype_model"` to `MODELS`.
- [ ] Run live: `uv run --env-file ~/1cfe/agentic-mbse/.env python scripts/capture_extraction_snapshots.py`.
- [ ] Commit the versioned `tests/fixtures/retype_model/extraction_snapshot.json`.

### Validation
- [ ] `uv run pytest tests/conformance/test_type_indexing.py` → all five assertions pass.
- [ ] `uv run pytest tests/` → green (regressions surface here; the *baseline* diff is Phase 3).
- [ ] `uv run mypy src/` + `uv run ruff check src/` → clean.
- [ ] Manual: inspect the V9 warning line names both owners + winner; V10 line names the incomparable set.

**What We Know After This Phase:** the retyped usage instantiates both template families, the collision
resolves deterministically with V9, differently-named both survive, and the plain sibling is untouched —
all pinned by a committed snapshot.

---

## Phase 3: Baseline Zero-Diff (Hard Gate) + Docs / Matrix / agentic-mbse

### Goal
Prove the 4 pipeline baselines are byte-identical after the fix (the backstop for B2-plain + B3), then
land docs, matrix rows, REQ tags, and the recorded agentic-mbse impact.

### Assumption Under Test
That superset indexing added **no** consequential key to any existing baseline — i.e. no baseline holds a
plain subtype-typed usage whose `.types` includes a user supertype (B2-plain), and none holds a retyping
shape (B3). Reasoning-by-inspection is *not* accepted (it is what let SC-3 survive 1,500 tests).

### Changes Required

#### 1. Baseline invariance (hard gate — run FIRST in this phase)
- [ ] Re-run live: `uv run --env-file ~/1cfe/agentic-mbse/.env python scripts/capture_extraction_snapshots.py`
      and `python scripts/capture_pipeline_baselines.py` (or the project's baseline capture script).
- [ ] `git diff` on the 4 baselines' snapshot/baseline files (`attr_expr_probe`, `catf_mfe`,
      `chain_spike`, `solar_battery`) is **empty**. **Any non-empty diff → STOP and investigate**
      (do not force-recapture) — it means B2-plain leaked (`design.md#potential-risks`).
- [ ] `uv run pytest tests/conformance/test_factory_purity.py` → offline graphs byte-identical.

#### 2. Docs (`design.md#docs--matrix-plan`)
- [ ] `docs/architecture/modeling-assumptions.md` §5 — add retyping to the Redefinition Types framing;
      **append V9, V10** to the Validation table (after the committed V-rows; V8 is Item 3's).
- [ ] `docs/architecture/reference/25-hierarchy-resolver.md` — `usage_type_map` most-specific rule
      (REQ-LVP-08) + its one behavioral consumer (`_find_literal_redefinition`).
- [ ] `docs/architecture/reference/01-extraction.md` — all-user-types index rule (REQ-EXT-13) + collision
      policy (REQ-EXT-14).
- [ ] `docs/architecture/verification-matrix.md` — rows for REQ-EXT-13, REQ-EXT-14, REQ-LVP-08 → the
      Phase 1/2 tests.

#### 3. agentic-mbse impact record (recorded, not executed — Item 12 runs it)
- [ ] Confirm the two impact items are captured in spec §"agentic-mbse impact": (1) teach retyping as a
      supported pattern; (2) update the Level-6 "calc-bearing part def with no instantiation" check so
      retyped usages count as an instantiation. No inline agentic-mbse change this item.

### Validation
- [ ] Baseline `git diff` empty (hard gate).
- [ ] `test_factory_purity` green.
- [ ] `uv run pytest tests/` → full suite green.
- [ ] Docs render; matrix rows resolve to real test IDs.

**What We Know After This Phase:** existing output is provably unchanged (runtime, not inspection); the
new behavior is documented, tagged, and matrix-linked; the agentic-mbse carry-through is on record for
Item 12.

---

## Environment Setup

**See CLAUDE.md for full environment rules.** Live extraction (probe, snapshot capture, baseline re-run)
needs the syside license: prefix with `uv run --env-file ~/1cfe/agentic-mbse/.env`. License expires
2026-08-06 (R3) — this item's live steps are Phase 0 (probe), Phase 2 (fixture snapshot), Phase 3
(baseline re-run). License-free work: Phase 1 helpers + unit test, all offline snapshot assertions,
`test_factory_purity`.

---

## Risk Management

**See `design.md#potential-risks` for the full analysis.**

**Phase-Specific Mitigations:**
- **Phase 0:** B1-false and B2-plain-false are HARD STOPS, fully gated before any code — report and halt,
  do not improvise (`design.md#implementation-notes`). Q4 decides the user-filter mechanism before it is written.
- **Phase 1:** `most_specific` sorts by QN string for the incomparable tiebreak — never rely on
  `heritage`/`types` iteration order, or snapshots go machine-dependent (`design.md#potential-risks`).
- **Phase 2:** per-usage key set is a `set` union (INV-1); the tiebreak compares the *stored* virtual's
  `owning_part_def_qn`, never re-derives it (D3). 3-owner collision is a known limitation, out of the
  2-owner fixture matrix — do not build for it (m6).
- **Phase 3:** baseline diff is a runtime re-run, not inspection; a non-empty diff halts for investigation
  rather than a force-recapture.

## Implementation Notes

[TO BE FILLED DURING IMPLEMENTATION]

### Phase 0 Completion (probe outcomes — record verbatim)
**Q1:** …
**Q2:** …
**Q2b:** …
**Q3:** … (only if Q2 showed heritage climbs the chain)
**Q4:** …
**B1 / B2-plain verdict:** …
**Chosen heritage accessor / user-filter mechanism:** …

### Phase 1 Completion
**Completed:** …

### Phase 2 Completion
**Completed:** …

### Phase 3 Completion
**Completed:** …

---

**Status:** Draft → In Progress → Complete
