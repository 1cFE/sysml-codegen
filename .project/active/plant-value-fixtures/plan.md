# Implementation Plan: Plant-Value & Blind-Spot Fixtures (PIPELINE-TRUTH Item 1)

**Status:** Draft
**Created:** 2026-07-06
**Last Updated:** 2026-07-06
**Epic Item:** PIPELINE-TRUTH Item 1 (Track A head)

## Source Documents

- **Spec (the contract):** `.project/active/plant-value-fixtures/spec.md` — Decisions
  D1–D7 are settled; SC-1/2/3 and the deliberately-touched baseline set are the acceptance
  bar. Read D6 (capture-time probe gate) and D7 (`--fixtures` selective capture) closely.
- **Spec review + resolutions:** `.project/active/plant-value-fixtures/spec-review.md` —
  why D6/D7 exist (L1-1 V11-trip crux, L3-1 byte-identity not checkable).
- **Epic (Item 1 + consumers 2/4/5/9):** `.project/backlog/epic_pipeline_truth.md`.
- **Discovery §D6 / §D1-F6:** `.project/research/20260706_pipeline-truth-discovery.md` —
  the value-provision mechanism taxonomy and the fixture-gap remainder.
- **Template plan:** `.project/active/plant-fixtures/plan.md` (UPSTREAM-FINDINGS Item 8) —
  the author → capture → pin phasing and the live-probe-branch discipline this plan reuses.
- **No design.md** — this item is fixtures + captures; it goes spec → plan → implement
  (spec "Design: none"). Component references point at `spec.md#section` and the existing
  capture/test infrastructure directly.

## Scope Note (read first)

- **Zero `src/` production code.** Fixtures, snapshots, baselines, tests, capture-script
  registration, and the D7 `--fixtures` filter (a `scripts/` change, explicitly allowed by
  the spec) only. If a secondary shape cannot be captured without a `src/` change (extractor
  crash, not a mere degrade), it is **FILED to the fixture-gap register with crash evidence**,
  not fixed (spec L2-2 escape hatch).
- **"Done" for a blind-spot shape is a captured, labeled baseline** — correct, degraded, or
  diagnostic — pinned by a test asserting a **specific observed property** (SC-3 / L2-1), NOT
  a whole-snapshot byte-equality (the epic-R1 banned REQ-EXT-09 anti-pattern).
- **The headline `plant_values` is the exception with a hard bar:** it must **trip V11 today**,
  verified at capture by the D6 probe gate, with an offender set covering all three
  value-provision mechanisms. A non-tripping layout is reworked, never accepted.

**Mechanism labels (do not mis-map — spec label note):** this plan's (a)/(b)/(c) are the
discovery-§D6 value-provision mechanisms:
- **(a)** subtype-def literal `:>>` consumed cross-part through a usage-level retype.
- **(b)** bare no-retype `part :>> name { :>> attr = literal; }` override block (the shape
  **zero** current fixtures contain).
- **(c)** plain cross-part-attribute chain (the `driver.cost_per_joule` / twolevel shape).

They are NOT the memory note `plant-idiom-fixtures`' A/B/C/D partition of `ife_plant`.

## Implementation Strategy

**Phasing Rationale.** Three hard constraints drive the order:

1. **D7 tooling is a prerequisite.** Byte-identity of untouched baselines is only checkable
   if capture is selective. Both scripts today loop over all fixtures with no filter, so a
   full run rewrites everything — and the rider's own "path canonicalization" proves a full
   run changes committed bytes. So the `--fixtures` filter is **Phase 0**, license-free,
   test-first, landed before any capture.
2. **All live-license work is one contiguous window.** Authoring parse-iterates against the
   live syside license, and the captures need it too. Phases 1–3 run back-to-back in one
   license window (available, monthly renewal). No license-free phase is interleaved. The
   rider (Phase 3) is a distinct phase with its **own commit** inside that window (D3).
3. **Pins are written after the observed snapshots exist.** Per-shape property pins (SC-3)
   assert what was actually captured, so Phase 4 reads the committed snapshots first, then
   writes pins. License-free.

**Critical Path:**

`--fixtures` filter built + tested (Phase 0) → all new/extended fixtures parse clean and a
**rehearsal probe** shows the headline offender set covers all three mechanisms (Phase 1) →
committed captures via the filtered scripts + the **D6 probe gate on the committed headline
snapshot** + git-status byte-identity gate (Phase 2) → rider re-captures, own commit (Phase
3) → per-shape property pins + headline V11 offender-set pin + drift pins, read-then-write
(Phase 4) → agentic-mbse impact list + fixture-gap register + close-out (Phase 5).

**First Proof Point:**

Phase 0 — the `--fixtures` filter lands with a test proving a filtered run rewrites **only**
the named fixture and leaves every other committed snapshot byte-identical (`git status`
clean outside the named set). Without this, the whole byte-identity criterion is unverifiable
and every later capture is unsafe. It is first, cheap, and license-free.

**The load-bearing checkpoint (Phase 2, D6 gate):** the headline fixture is **not accepted**
until `collect_uncovered_params(build_full_graph_from_snapshot(plant_values))` returns a
non-empty offender set covering **all three** mechanisms. If a mechanism does not surface, the
fixture layout is reworked to route that literal cross-part — **the criterion is never
relaxed** (the D6 recipe confirms fusion-tea's real shapes DO trip V11; a non-tripping layout
means the fixture diverged from the exemplars).

**Overall Validation Approach:**

- Suite stays green at every phase boundary. `uv run pytest tests/` after each phase; a new
  fixture must never redden an existing test.
- Snapshot-reading tests authored before their capture are `xfail`-guarded (or landed in
  Phase 4) so the suite stays green meanwhile.
- Byte-identity is **checked, not asserted**: after each capture step, `git status --porcelain`
  must show changes only inside the deliberately-touched set (spec "Deliberately-touched
  baseline set"). Anything else is investigated before committing.
- Every capture is script-reproducible (`scripts/capture_*.py --fixtures NAME`).

---

## Phase 0: Selective-Capture Tooling (`--fixtures` filter) — D7

### Goal

Add a `--fixtures NAME[,NAME...]` name-filter to `capture_extraction_snapshots.py` and
`capture_pipeline_baselines.py` so each later capture step touches exactly the fixtures it
names, and byte-identity of the rest is checkable via `git status`. License-free
prerequisite — nothing else captures until this lands.

### Assumption Under Test

That a selective filter can be added to both scripts without changing what a full (unfiltered)
run produces — i.e. `--fixtures X` writes byte-identical output to what a full run writes for
`X`, and writes nothing else. (Guards against the filter itself perturbing capture.)

### Test Stencil (Write This First)

```python
# tests/unit/test_capture_fixtures_filter.py  (NEW)
import subprocess, sys
from pathlib import Path

def test_extraction_filter_touches_only_named(tmp_repo_snapshot_state):
    # Run the extraction capture with --fixtures on ONE already-committed fixture.
    subprocess.run([sys.executable, "scripts/capture_extraction_snapshots.py",
                    "--fixtures", "sample_model"], check=True)
    changed = _git_changed_paths()            # porcelain parse
    # Only sample_model's snapshot may have been rewritten (and it is byte-identical
    # to its committed form, since nothing about sample_model changed).
    assert all("sample_model" in p for p in changed), changed

def test_unknown_fixture_name_errors():
    r = subprocess.run([sys.executable, "scripts/capture_extraction_snapshots.py",
                        "--fixtures", "no_such_fixture"], capture_output=True, text=True)
    assert r.returncode != 0 and "no_such_fixture" in r.stderr
```

### Changes Required

**No `src/` change — `scripts/` only (spec D7, explicitly outside the zero-production-code
constraint).**

- [x] `scripts/capture_extraction_snapshots.py` — add an `argparse` `--fixtures` option
      (comma-split into a name set). In `main()`, filter both `MODELS` and
      `EXTRACTION_ONLY_MODELS` by the set before the capture loops. Unknown name → exit
      non-zero naming the offender (fail loud, do not silently no-op). No arg → current
      all-fixtures behavior (backward compatible).
- [x] `scripts/capture_pipeline_baselines.py` — same `--fixtures` option filtering `MODELS`
      (baseline-dir → snapshot-name) before the loop. Unknown name → exit non-zero. No arg →
      current behavior.
- [x] Factor the name-matching so a name can address either script's dict keys consistently
      (extraction keys are model names; baseline keys are baseline-dir names — document the
      distinction in `--help` so Phase 2 names the right key per script).
- [x] `tests/unit/test_capture_fixtures_filter.py` (NEW) — the stencils above, plus a test
      that no-arg invocation still enumerates all fixtures (guards backward compatibility).
      Use a committed fixture that is stable under re-capture; assert byte-identity after a
      filtered re-capture. If no committed fixture is byte-stable under re-capture (path
      canonicalization drift), assert instead that `git status` names **only** the filtered
      fixture's paths — the checkable property Phase 2 relies on.

### Validation

**Automated:**
- [ ] `uv run pytest tests/unit/test_capture_fixtures_filter.py` → passes.
- [ ] `uv run pytest tests/` → no regressions.
- [ ] `uv run ruff check scripts/ tests/` → clean.

**Manual:**
- [ ] `uv run python scripts/capture_extraction_snapshots.py --fixtures sample_model` then
      `git status --porcelain` → only `sample_model` paths appear (or none). Confirm the
      byte-identity gate is real.

**What We Know Works After This Phase:** Selective capture exists and is proven to touch only
named fixtures. Every later capture step can name its fixtures and gate on `git status` — the
byte-identity criterion (SC / cross-cutting `[HARD]`) is now checkable, not asserted.

---

## Phase 1: Author All Fixtures + Rehearsal V11 Probe (license)

### Goal

Author the headline `plant_values`, the secondary `plant_value_shapes`, the
`spec_chain_twolevel` extension, and confirm `deep_cross_scope_probe` still parses — all
parse-iterated against the live license until they load clean. Then run a **rehearsal probe**:
build the headline graph from a provisional capture and confirm `collect_uncovered_params`
already covers all three mechanisms, so Phase 2's committed capture is de-risked before it is
gated. No committed snapshots yet (provisional captures only, discarded before Phase 2).

### Assumption Under Test

That the headline's three mechanisms each route their literal **cross-part** into a
valueless plant-calc entry point (`default_value is None`) so `collect_uncovered_params`
(`graph_builder.py:810`) flags them — the L1-1 crux. A naive layout where a literal sits in a
plain-usage EP gets pre-filled by the prior epic's Item-9 capture and does **not** trip V11.
This phase collapses that uncertainty before the committed gate.

### Fusion-tea exemplars (re-read at execution, spec "Fusion-tea exemplars")

The implement session has the broader sandbox; **re-read these and diff the authored fixtures
against them before committing** (spec: "copied from reality"):
- `~/1cfe/fusion-tea/models/designs/hif_ife/hif_plant.sysml` — mechanism (b): bare no-retype
  `part :>> target_factory` / `part :>> chamber` blocks with literal `:>>`s incl. the
  quoted-enum `wall_type` override.
- `~/1cfe/fusion-tea/models/designs/hif_ife/hif_driver.sysml` — mechanism (a): subtype-def
  literal `:>>`s at lines 81, 83, 84.
- `~/1cfe/fusion-tea/models/designs/generic_ife/ife_plant.sysml` — base plant with the 10 V11
  offenders and the assert-constraint shape.
- `~/1cfe/fusion-tea/models/library/cost_structure/ife_cost_parameters.sysml` — the
  attribute-def-typed nested-`:>>` (14-econ-params) shape (for `plant_value_shapes`).

If the sandbox blocks these paths, the spec's "Fusion-tea exemplars (verified)" section
carries the shapes — author from there and record that the direct re-read was blocked.

### Test Stencil (Write This First — the rehearsal probe, run manually this phase)

```python
# scratch probe (NOT committed) — the D6 rehearsal
from sysml_codegen.snapshot import build_full_graph_from_snapshot
from sysml_codegen.resolution.graph_builder import collect_uncovered_params

graph, _ = build_full_graph_from_snapshot(PROVISIONAL_PLANT_VALUES_SNAPSHOT)
offenders = collect_uncovered_params(graph)
assert offenders, "V11 does not trip — layout is wrong, route the literal cross-part"
# Each of (a),(b),(c) must appear as at least one offender tuple. Map each
# (module, input, missing_key) back to the mechanism that fed it; all three present.
```

### Changes Required

**Headline `plant_values` (spec "The headline fixture", [HARD] items):**
- [x] `tests/fixtures/plant_values/{library.sysml,design.sysml}` (NEW; add a subsystems file
      if a cross-package half is needed, as `ife_plant` does). Carry, in one parseable model:
  - Mechanism **(a)**: a usage-level retype whose subtype def supplies attrs via literal
    `:>>`, consumed cross-part by a plant-calc input.
  - Mechanism **(b)**: a bare no-retype `part :>> sub { :>> attr = <literal>; }` override
    block (the shape no fixture contains), incl. one quoted-enum `:>>` — its literal fed
    cross-part to a plant-calc input.
  - Mechanism **(c)**: the headline's **own** `driver.cost_per_joule`-style chain (a
    self-contained copy of the twolevel shape, NOT a dependency on `spec_chain_twolevel`) —
    so SC-1's offender set is asserted over the headline **alone**.
  - The **assert constraint** carrying three binding sub-shapes in one place: a cross-part
    binding, a self-named binding (`in x = x`), and an unbound defaulted param (Item 4/5
    substrate; invisible to the drop report today — the CONSTRAINT-SILENCE bug).
- [x] **Cross-part consumption is the crux, not incidental** (spec [HARD] / D6): each
      mechanism's literal MUST feed a plant-calc input whose EP stays valueless. Author so,
      parse-iterate, and run the rehearsal probe until all three surface as offenders. If one
      does not, **rework the layout** (route it cross-part) — never relax.
- [x] Follow ADR-002 conventions and the `ife_plant` provenance-doc-comment style (source,
      reference, last-updated). Record **hand-computed expected values** for the headline's
      calc chain in the Phase-1 notes (spec [INFERRED]) so Item 2's after-state is anchorable
      independently of the resolver (SC-B lineage).

**Secondary `plant_value_shapes` (spec "Secondary shapes", D4):**
- [x] `tests/fixtures/plant_value_shapes/{library.sysml,design.sysml}` (NEW). Carry the
      high-value subset, each authored to load and capture (correct/degrade/diagnostic is
      empirically fine — SC-3): attribute-def-typed attr with nested `:>>` (the 14-econ-params
      shape); bare `default 10.0` (no `:=`); doc bodies inside calc usages and on `:>>`
      redefinitions; an in-binding referencing an inherited attr the same def redefines below
      it; a 5-deep specialization chain with abstract ends; quoted enum def + usage-level
      quoted enum `:>>`; a quoted OUTPUT parameter name (`out attribute 'net cost'`); a
      Style-E calc def (mixed `out attribute` + `return` inside a quoted def) and a
      return-in-quoted-def row; and the non-float EP shape (bool/string/enum-valued attr one
      hop from an EP — the `wall_type` idiom, Item 5 substrate).
- [x] **Split only if forced** (spec [INFERRED] / Open Question): if the quoted-enum, Style-E,
      and 5-deep-chain shapes cannot co-exist in one parseable model, split into a second
      fixture; record the reason. Prefer one fixture for legibility.
- [x] **Escape hatch (spec L2-2 [HARD]):** if a shape (likely `out attribute 'net cost'` or
      Style-E) **crashes the extractor** rather than degrading, do NOT fix it here — remove it
      from the fixture, capture the crash evidence, and mark it for the Phase-5 fixture-gap
      register filing. A captured degrade/diagnostic is the win; a required `src/` change is
      out of scope.

**Extend `spec_chain_twolevel` (spec "Extend `spec_chain_twolevel`", D2):**
- [x] `tests/fixtures/spec_chain_twolevel/{library.sysml,design.sysml}` — ADD the plain
      cross-part-attribute shape (a subsystem attr referenced by a plant-calc input, no
      calc-output in the chain — the P1 acceptance note, distinct from the existing
      calc-output-valued `driver.cost_per_joule`), and **one attribute consumed by two
      modules** (the fan-out collapse case). Preserve the existing `usage_type_map` retype
      shape and all existing pins. This stays the fixture Item 2's SC-B tolerance test and
      Item 3's SNAP-19 parity run against.

**`deep_cross_scope_probe` (spec "Capture hygiene", [HARD]):**
- [x] Confirm `tests/fixtures/deep_cross_scope_probe/{library,design}.sysml` still parse (no
      authoring change unless parse-broken). It has no committed snapshot today (D1-F6 drift);
      Phase 2 commits one.

### Validation

**Automated:**
- [x] `uv run pytest tests/` → no regressions (snapshot-reading tests for the new fixtures do
      not exist yet — they land in Phase 4).

**Manual (iterative, license-gated):**
- [x] Load each new/extended fixture live via `SysMLDataExtractor`; parse→fix→parse until it
      loads with no structural errors.
- [x] **Rehearsal probe** on a provisional `plant_values` capture: `collect_uncovered_params`
      returns a non-empty set covering all three mechanisms. Record the mechanism→offender
      map in the Phase-1 notes. Discard the provisional capture (Phase 2 commits the real one).
- [x] Diff the authored `plant_values` / `plant_value_shapes` shapes against the fusion-tea
      exemplars; note any deliberate divergence.

**What We Know Works After This Phase:** Every fixture parses clean; the headline's three
mechanisms provably trip the collector on a provisional build; the twolevel extension and the
secondary shapes load. The committed capture in Phase 2 is de-risked — the gate should pass
first try.

---

## Phase 2: Committed Captures + D6 Probe Gate + Byte-Identity Gate (license, contiguous with Phase 1)

### Goal

Commit the versioned extraction snapshots (and pipeline baselines where the graph builds) for
`plant_values`, `plant_value_shapes`, `deep_cross_scope_probe`, and the extended
`spec_chain_twolevel`, each via the D7 `--fixtures` filter. **The phase does not check off
until the D6 probe gate passes on the committed `plant_values` snapshot** and the git-status
byte-identity gate is clean.

### Assumption Under Test

That the committed headline snapshot reproduces the rehearsal result — `collect_uncovered_params`
on the graph built from the **committed** snapshot returns the same non-empty, three-mechanism
offender set (guards against a capture-serialization boundary silently changing the offenders).
And that the byte-identity gate holds: nothing outside the deliberately-touched set changes.

### Changes Required

**Registration (additive — spec "Deliberately-touched baseline set"):**
- [ ] `scripts/capture_extraction_snapshots.py` `MODELS` — add `"plant_values"`,
      `"spec_chain_twolevel"` is already present. Add `"plant_value_shapes"` to `MODELS` if it
      builds a full graph, else to `EXTRACTION_ONLY_MODELS` (determined at capture). Add
      `"deep_cross_scope_probe"` to `MODELS` if its graph builds, else `EXTRACTION_ONLY_MODELS`
      (spec Open Question — determined at capture).
- [ ] `scripts/capture_pipeline_baselines.py` `MODELS` — add `"plant_values": "plant_values"`
      (spec deliberately-touched set lists a pipeline baseline for it). Add
      `"plant_value_shapes"` and `"deep_cross_scope_probe"` **only if** each builds a full
      graph. `spec_chain_twolevel` re-captures via its existing registration.

**Captures (each named via `--fixtures`, then git-status gate after each):**
- [ ] `uv run python scripts/capture_extraction_snapshots.py --fixtures plant_values` →
      commits `tests/fixtures/plant_values/extraction_snapshot.json`.
- [ ] **D6 PROBE GATE (checkpoint — phase blocks here until it passes):**
  ```
  graph, _ = build_full_graph_from_snapshot(snapshot_fixture("plant_values"))
  offenders = collect_uncovered_params(graph)
  assert offenders and _covers_all_three_mechanisms(offenders)
  ```
  Accept the fixture **only** when the offender set is non-empty AND covers (a), (b), (c). If a
  mechanism is missing, return to Phase 1, rework that mechanism's layout to route it
  cross-part, re-capture — **never relax the criterion** (spec D6). Record the exact offender
  `(module, input, missing_key)` tuples for the Phase-4 pin.
- [ ] `uv run python scripts/capture_pipeline_baselines.py --fixtures plant_values` → commits
      `tests/fixtures/baseline_outputs/plant_values/{computation_graph.json,registry_init.py}`
      (the graph builds — V11 fires only at the generation boundary, not at graph build, like
      `chain_override_probe`; the baseline is the valueless-fallback "before" state Item 2
      flips).
- [ ] `uv run python scripts/capture_extraction_snapshots.py --fixtures plant_value_shapes` →
      commit its snapshot; pipeline baseline **only if** its graph builds (record which).
- [ ] `uv run python scripts/capture_extraction_snapshots.py --fixtures deep_cross_scope_probe`
      → commit its snapshot (register full-pipeline if the graph builds, else extraction-only —
      record which, spec Open Question).
- [ ] `uv run python scripts/capture_extraction_snapshots.py --fixtures spec_chain_twolevel`
      then `--fixtures spec_chain_twolevel` on the pipeline-baseline script → re-capture the
      extended twolevel snapshot + baseline as a reviewed diff.
- [ ] **Byte-identity gate after each capture:** `git status --porcelain` shows changes only
      inside the deliberately-touched set (`plant_values`, `plant_value_shapes`,
      `deep_cross_scope_probe`, `spec_chain_twolevel`, the two capture scripts). Any other path
      changing → investigate before committing (the filter or a shared-state leak).

### Validation

**Automated:**
- [ ] `uv run pytest tests/` → no regressions (new-fixture pins land Phase 4; existing
      `spec_chain_twolevel` pins must still pass against the re-captured snapshot).
- [ ] `uv run python scripts/capture_pipeline_baselines.py --fixtures plant_values` reports
      `syntax: valid` for `registry_init.py`.

**Manual:**
- [ ] Confirm the D6 gate passed with all three mechanisms in the offender set; paste the
      offender tuples into the Phase-2 notes (Item 2's before-pin substrate).
- [ ] Confirm `git status` shows only deliberately-touched paths (paste the porcelain output).
- [ ] Record, per fixture, whether it captured full-pipeline or extraction-only, and whether a
      pipeline baseline was taken.

**What We Know Works After This Phase:** The headline fixture is committed and **proven to trip
V11 today** with all three mechanisms — the pinned "before" state Item 2 flips. Every capture is
inside the deliberately-touched set; everything else is byte-identical. The extended twolevel
snapshot re-captured cleanly with its existing pins intact.

---

## Phase 3: Stale-Fixture-Refresh Rider — Own Commit (license, contiguous with Phase 2, D3)

### Goal

Re-capture `wi014_toy`, `self_named_binding_trap`, and `quoted_owner_formula` to the canonical
script form, as a **separate commit with a reviewed diff** (spec D3). Isolated from the Phase-2
commit so the rider's churn is separately attributable.

### Assumption Under Test

That the three rider re-captures produce only the **expected** changes: path canonicalization
for `wi014_toy` and `self_named_binding_trap`, and path canonicalization **plus** the
`net_margin`/`total_payout` design-attr → computed-attr reclassification for
`quoted_owner_formula`. Any **other** field changing is an unintended shift to investigate
before committing.

### Changes Required

**See spec "Capture hygiene" [HARD] and D3.**

- [ ] `uv run python scripts/capture_extraction_snapshots.py --fixtures wi014_toy,self_named_binding_trap,quoted_owner_formula`
      → re-captures the three snapshots. (`quoted_owner_formula` is already registered in
      `MODELS`; confirm the other two are registered — `wi014_toy` is in `MODELS`,
      `self_named_binding_trap` is in `EXTRACTION_ONLY_MODELS`.)
- [ ] **Review the `quoted_owner_formula` diff deliberately** (spec D3): confirm the two attrs
      (`net_margin`, `total_payout`) move design-attr → computed, and that this reflects
      behavior that **already landed in the PRIOR epic (UPSTREAM-FINDINGS Item 7, computed-
      attribute classification)** — NOT a forward dependency on this epic's Item 7 (matrix
      reconciliation, which runs after Item 1). Confirmed correct → commit. If the diff hides a
      real question rather than confirming the known reclassification → **file it, do not wave
      it through**.
- [ ] Byte-identity gate: `git status --porcelain` shows only the three rider fixtures'
      snapshot paths. Nothing else.
- [ ] **Own commit** — commit the rider separately from the Phase-2 captures, message naming it
      the stale-fixture-refresh rider and the reviewed reclassification.

### Validation

**Automated:**
- [ ] `uv run pytest tests/` → no regressions (any existing rider-fixture pins must still pass;
      the `quoted_owner_formula` reclassification may require a pin update — do it here, in the
      rider commit).

**Manual:**
- [ ] Diff each rider snapshot; confirm only the expected canonicalization/reclassification
      changes. Paste the `quoted_owner_formula` field-level diff and the review verdict
      (confirmed vs filed) into the Phase-3 notes.

**What We Know Works After This Phase:** The committed corpus is fully script-reproducible in
one pass; the three drifting snapshots are canonicalized; the `quoted_owner_formula`
reclassification is reviewed against the prior epic's landed behavior and recorded. The rider
is its own reviewable commit.

---

## Phase 4: Per-Shape Property Pins (license-free — read observed, then write)

### Goal

Read the committed snapshots and write the pinning tests. Each secondary-shape pin asserts a
**specific observed property** (SC-3 / L2-1), NOT a whole-snapshot byte-equality. Land the
headline V11 offender-set pin, the twolevel new-shape pins, the assert-constraint substrate
recording, and the `deep_cross_scope_probe` drift pin. License-free — reads committed
snapshots only.

### Assumption Under Test

That every shape's captured behavior is expressible as a concrete, meaningful property (an EP
with `default_value is None`; a shape dropped — no module input references it; a redefinition
with a specific `literal_value`), so no pin degrades into the banned `snapshot == committed`
byte-equality (epic-R1 REQ-EXT-09).

### Test Stencil (Write This First — headline V11 pin + one property pin)

```python
# tests/conformance/test_plant_values.py  (NEW)
from sysml_codegen.snapshot import build_full_graph_from_snapshot
from sysml_codegen.resolution.graph_builder import collect_uncovered_params
from tests.conftest import snapshot_fixture

EXPECTED_UNCOVERED = { ... }   # exact (module, input, missing_key) tuples read from capture

def test_plant_values_trips_v11_all_three_mechanisms():
    """SC-1 before-state pin. Item 2 flips this as it wires cross-part values."""
    graph, _ = build_full_graph_from_snapshot(snapshot_fixture("plant_values"))
    actual = set(collect_uncovered_params(graph))
    assert actual == EXPECTED_UNCOVERED, actual        # non-empty, covers (a),(b),(c)

def test_shape_b_override_literal_valueless_ep():
    """Mechanism (b): the bare `part :>>` literal feeds a valueless plant-calc EP
    (default_value is None) — it is NOT pre-filled, so the collector flags it."""
    # assert the specific EP for the (b) offender has default_value is None
```

### Changes Required

**Read first, then write** (SC-3 empirical discipline — determine the property from the
observed snapshot, do not pre-judge):

- [ ] Read the committed `plant_values`, `plant_value_shapes`, `deep_cross_scope_probe`, and
      re-captured `spec_chain_twolevel` snapshots; record each shape's observed label
      (correct / degraded / diagnostic) in the Phase-4 notes, following the `ife_plant`
      shape-by-shape precedent.
- [ ] `tests/conformance/test_plant_values.py` (NEW):
  - The **V11 offender-set pin** (`EXPECTED_UNCOVERED` = the exact tuples from Phase 2). This
    is the SC-1 before-state pin Item 2 flips. Retain a structure that still fires if the set
    later goes empty (so a regression re-dropping it fails loudly), per the `ife_plant`
    `test_cross_part_inputs_pinned_or_baseline` precedent.
  - One **property pin per mechanism** (a)/(b)/(c): assert the specific EP is valueless
    (`default_value is None`) or the specific redefinition/override carries the expected
    literal — the observed property, not the bytes.
  - The **assert-constraint substrate recording**: pin that the assert constraint's three
    binding sub-shapes (cross-part, self-named `in x = x`, unbound-defaulted) are visible to
    the binding resolver, and record that the assert constraint itself is invisible to the
    drop report today (Item 4 fires-on-shape substrate; the CONSTRAINT-SILENCE bug). Assert
    the observed absence explicitly (Item 4 flips it).
- [ ] `tests/conformance/test_plant_value_shapes.py` (NEW) — one property pin per secondary
      shape (SC-3). Each asserts a concrete observed property, e.g. "quoted-output shape yields
      EP Y", "bare `default 10.0` yields default_value 10.0", "non-float `wall_type` shape:
      EP omitted / value None (Item 5 substrate)". Any shape removed under the L2-2 escape hatch
      is NOT pinned here — it is filed in Phase 5.
- [ ] `tests/conformance/test_spec_chain_twolevel.py` — ADD pins for the two new shapes (plain
      cross-part attr; the fan-out attr consumed by two modules — assert the collapse to one
      producer channel wired to both consumers), preserving the existing `usage_type_map`
      retype pin and all current assertions (spec D2).
- [ ] `tests/conformance/test_deep_cross_scope_probe.py` (NEW) — a drift pin over the newly
      committed snapshot (patterns A/B/C observed shapes) so future silent drift fails (spec
      D1-F6). Assert observed properties (e.g. "pattern B: the 6-segment REFERENCE resolves
      to / is dropped as X"), not byte-equality.
- [ ] Register the new fixtures in `tests/conformance/conftest.py` `SNAPSHOT_MODELS` (mirrors
      the Item-8 registration).

### Validation

**Automated:**
- [ ] `uv run pytest tests/conformance/test_plant_values.py tests/conformance/test_plant_value_shapes.py tests/conformance/test_spec_chain_twolevel.py tests/conformance/test_deep_cross_scope_probe.py`
      → all pass.
- [ ] `uv run pytest tests/` → full suite green; no existing test reddened.
- [ ] `uv run ruff check tests/` and `uv run mypy src/` → clean (mypy scope unchanged — no
      `src/` change).

**Manual:**
- [ ] Confirm no pin is a whole-snapshot byte-equality (grep the new test files for
      `== committed` / raw-snapshot compares). Each pin names a specific property.
- [ ] Confirm the V11 pin's `EXPECTED_UNCOVERED` matches the Phase-2 recorded tuples exactly.

**What We Know Works After This Phase:** Every captured shape has a property pin documenting its
current behavior; the headline's V11 trip is pinned as the before-state Item 2 flips; the
twolevel fan-out and plain-attr shapes are pinned; `deep_cross_scope_probe` is drift-guarded.
The corpus is legible shape-by-shape.

---

## Phase 5: agentic-mbse Impact List + Fixture-Gap Register + Close-out (license-free)

### Goal

Accumulate the concrete agentic-mbse impact list Item 9 consumes, file the deferred D6 shapes
into the fixture-gap register, and close out CURRENT_WORK. License-free.

### Changes Required

**agentic-mbse impact list (spec "agentic-mbse impact — Item 9 accumulation list", L3-3):**
- [ ] Finalize the spec's "agentic-mbse impact — Item 9 accumulation list" block with the
      **exact fixture names/locations captured** (the spec left these to "the plan finalizes
      at capture"). One line per shape: mechanism/shape name + fixture path + purpose. This is
      the artifact Item 9 reads — a bare "recorded for Item 9" is insufficient (L3-3). Update
      the block in `spec.md` (or a co-located `agentic-mbse-impact.md` if the spec is frozen —
      **decision:** update the spec's block in place, since it is the named artifact and the
      spec is the durable record). Include the non-float EP shape → agentic-mbse D-F
      expression-RHS warning (Item 9 §2) and the assert-constraint visibility check.

**Fixture-gap register (spec SC / D4 — deferred shapes filed with a pointer to §D6):**
- [ ] **Decision (autonomous — the register file does not yet exist):** create
      `.project/active/plant-value-fixtures/fixture-gap-register.md` as the register. It
      records: the deferred D6 shapes (D4's filed remainder — selective import of quoted
      names; standalone package-level `:>>`-fed calc bindings; constraint def consuming a
      defaulted param → filed to Item 4's scope; the standalone retyped-child consumer variant)
      with a **pointer to discovery §D6**; and any secondary shape removed under the Phase-1
      L2-2 escape hatch, **with its captured crash evidence**. One entry per shape: shape name,
      why deferred, pointer. Note in the register that it is promotable to `BACKLOG.md` if the
      epic wants it tracked corpus-wide.

**Close-out:**
- [ ] Update `.project/CURRENT_WORK.md`: Item 1 status → complete; the D6 gate outcome (offender
      tuples + three-mechanism coverage); the per-shape observed labels; the rider review
      verdict (`quoted_owner_formula` confirmed vs filed); the capture-surface decisions
      (full-pipeline vs extraction-only per fixture); and the two downstream handoffs (Item 2
      before-pin location; Item 4/5 assert-constraint + non-float-EP substrate location).
- [ ] Suggest `/_my_audit` (spec/plan are the contract; the audit catches placeholder pins and
      gaps the implementing session misses).

### Validation

**Automated:**
- [ ] `uv run pytest tests/` → full suite green.
- [ ] `uv run ruff check` and `uv run mypy src/` → clean.

**Manual:**
- [ ] Confirm the agentic-mbse impact block names concrete fixture paths (Item 9 can read it
      without re-deriving).
- [ ] Confirm the fixture-gap register exists, points at §D6, and carries any escape-hatch
      crash evidence.
- [ ] Confirm CURRENT_WORK records the two downstream substrate handoffs.

**What We Know Works After This Phase:** Item 2 has a pinned, reviewed before-state on one
fixture; Items 4/5 have their assert-constraint and non-float-EP substrate; Item 9 has a
concrete impact list; deferred shapes are filed, not lost. Item 1 is closed.

---

## Environment Setup

**See CLAUDE.md for full environment rules.** Key commands:
- Install: `uv pip install -e ~/agentic-mbse && uv pip install -e ".[dev]"`
- Tests: `uv run pytest tests/`
- Single test: `uv run pytest tests/conformance/test_plant_values.py -k <name>`
- Capture extraction snapshots (live license, selective): `uv run python scripts/capture_extraction_snapshots.py --fixtures NAME[,NAME...]`
- Capture pipeline baselines (license-free, selective): `uv run python scripts/capture_pipeline_baselines.py --fixtures NAME[,NAME...]`
- **License window (R3):** the live syside license is available (monthly renewal). Phases 1–3
  are contiguous inside one window; Phases 0, 4, 5 are license-free. `agentic-mbse` and
  `fusion-tea` live outside this repo's sandbox at `/home/reid/1cfe/{agentic-mbse,fusion-tea}`
  — the implement session reads the fusion-tea exemplars by absolute path if the sandbox allows;
  otherwise it authors from the spec's verified-exemplars section and records the block.

## Risk Management

**Phase-Specific Mitigations:**

- **Phase 0 (filter perturbs capture):** the filter must not change what a full run produces.
  Mitigation: test byte-identity (or `git status`-scoping) of a filtered re-capture against a
  committed fixture before trusting it for real captures.
- **Phase 1 (headline generates clean — the L1-1 crux):** the obvious layout puts (a)/(b)
  literals where the Item-9 pre-fill values them, so V11 does not trip and Item 2 gets an empty
  pin. Mitigation: the rehearsal probe forces all three mechanisms cross-part **before** the
  committed gate; a mechanism that doesn't surface triggers a layout rework, never a relaxed
  criterion (D6).
- **Phase 1 (escape hatch collision):** a secondary shape may crash the extractor, colliding
  "load and capture" with zero-production-code. Mitigation: the L2-2 escape hatch — remove and
  file with crash evidence, do not fix.
- **Phase 2 (capture boundary changes offenders):** the serialization boundary could alter the
  offender set vs the rehearsal. Mitigation: the D6 gate re-runs on the **committed** snapshot,
  not the provisional one; the pin uses the committed tuples.
- **Phase 2/3 (byte-identity leak):** a full or mis-filtered run rewrites untouched baselines.
  Mitigation: every capture is `--fixtures`-scoped and gated by `git status --porcelain`;
  anything outside the deliberately-touched set is investigated before committing.
- **Phase 3 (rider hides a real change):** `quoted_owner_formula`'s reclassification could mask
  an unexpected shift. Mitigation: field-level diff review against the PRIOR epic's landed
  behavior; confirmed → commit, questionable → file, never wave through.

**Suite-green invariant:** a new fixture must never redden an existing test. Run
`uv run pytest tests/` at every phase boundary. Snapshot-reading tests authored before their
capture are `xfail`-guarded until the snapshot lands (or written in Phase 4).

## Implementation Notes

[TO BE FILLED DURING IMPLEMENTATION — Leave empty now]

### Phase 0 Completion
**Completed:** 2026-07-06
**Actual Changes:**
- NEW `scripts/capture_filter.py` — pure `select_fixtures(available, requested)`: returns the
  name set to capture (all names if `requested is None`), raises `ValueError` naming unknown
  names. Factored out so both scripts share one decision and it is unit-testable license-free.
- `scripts/capture_extraction_snapshots.py` — `--fixtures` argparse option; `main(requested)`
  filters `MODELS` + `EXTRACTION_ONLY_MODELS` by the selected set (validated against the union
  of both key spaces); unknown name → `sys.exit(2)` with the offender in stderr. No arg → all.
- `scripts/capture_pipeline_baselines.py` — same `--fixtures` option filtering `MODELS`
  (baseline-dir keys). `--help` on each script documents which key space `--fixtures` addresses.
- NEW `tests/unit/test_capture_fixtures_filter.py` — 4 pure-selection tests (all/subset/
  whitespace/unknown-raises), 2 subprocess fail-loud tests (both scripts, license-free —
  validation precedes any model load), and 1 `@requires_license` byte-identity test that
  re-captures `sample_model` and asserts `git status` names only sample_model paths, then
  restores the bytes.
**License finding (IMPORTANT — corrects a false start):** the syside license is NOT visible to
a bare `uv run python -c "... SysMLDataExtractor ..."` probe (that path never loads
`../agentic-mbse/.env`), but IS available through the real capture scripts and under a full
`uv run pytest` session — `uv run python scripts/capture_extraction_snapshots.py --fixtures
chain_spike_model` produced real extraction data (3 calc_defs/3 usages/6 bindings) and the
`@requires_license` byte-identity test ran (not skipped) and passed. Conclusion: **captures work;
Phases 1–3 are unblocked.** Always verify license via the actual capture path, not an isolated
extractor import.
**Issues:** The `sys.path`-hack import pattern tripped ruff I001 in the test; resolved by
importing `scripts.capture_filter` as a namespace package (repo root is pytest's rootdir) — no
path hack, test file ruff-clean. The two capture scripts retain 2 pre-existing-pattern I001
warnings each from the `sys.path.insert`-then-import idiom (scripts/ is at a 493-error ruff
baseline, outside the src-only 21-error gate; not worsened in kind).
**Deviations:** None. Filter factored into a shared `capture_filter.py` module (plan said
"factor the name-matching"); implemented as a pure function rather than duplicated per script.
**Validation:** `uv run pytest tests/` → 1996 passed, 4 skipped, 5 xfailed (green). Test file
ruff-clean; src/ untouched (mypy/ruff src baseline unchanged).

### Phase 1 Completion
**Completed:** 2026-07-06
**Actual Changes (source only — no committed snapshots, per phasing):**
- NEW `tests/fixtures/plant_values/{library,design}.sysml` — headline. `PlantCostCalc`
  reads three subsystem attrs cross-part; the 'Power Plant' base owns the calc + an
  `assert constraint viability : 'Viability Threshold'` (copied from fusion-tea
  fusion_cycle.sysml:29). Design is a part USAGE of the base with usage-level
  overrides/retypes (fusion-tea hif_plant shape).
- NEW `tests/fixtures/plant_value_shapes/{library,design}.sysml` — 9 secondary shapes.
- MODIFIED `tests/fixtures/deep_cross_scope_probe/{library,design}.sysml` — renamed the
  calc usage `derived` → `derived_calc` (parse-broken fix: `derived` is a reserved KerML
  feature modifier; the plan permits authoring changes when parse-broken). Now loads.
- MODIFIED `tests/fixtures/spec_chain_twolevel/library.sysml` — SC-2 extension: `MaintCalc`
  (plain cross-part attr, no calc output) + two `ScaleCalc` instances (fan-out) reading one
  shared `scale` attr; existing MeierCost→gamma→lcoe retype shape preserved untouched.
- MODIFIED `tests/conformance/test_spec_chain_twolevel.py` — the live-load calc-def-set
  guard now includes `MaintCalc` + `ScaleCalc` (the only existing pin the source growth
  touched; the retype/gamma-channel pins are unchanged and still pass).
- NEW `scripts/probes/_plant_values_rehearsal.py` — parametric rehearsal probe (kept
  uncommitted this phase; used again for the Phase-2 committed gate).

**Rehearsal probe — mechanism→offender map (ALL THREE PRESENT — gate de-risked):**
`plant_values` provisional capture → `collect_uncovered_params` = 3 offenders, all on module
`plantvaluesdesign__plant__cost_calc`, each a valueless (`default=None`) fallback EP:
- **(a)** input `driver_efficiency` → EP `PlantValuesDesign__plant__cost_calc__driver_efficiency`
  — subtype-def literal `:>> efficiency = 0.35` on 'Hif Driver', consumed cross-part via the
  usage-level retype `part :>> driver : 'Hif Driver'`.
- **(b)** input `target_cost` → EP `PlantValuesDesign__plant__cost_calc__target_cost` — bare
  no-retype override block `part :>> target_factory { :>> cost_per_target = 10.0; }`.
- **(c)** input `chamber_cost` → EP `PlantValuesDesign__plant__cost_calc__chamber_cost` —
  two-hop plain cross-part chain `chamber.liner.cost_per_unit`, value 7.0 supplied via a nested
  override block (distinct from (b)'s one-hop block; the plain-attribute twolevel variant).

Design iteration on (c): a base-def literal (`cost_per_unit = 7.0`) resolved to a VALUED EP
(didn't trip); an attr-reference redefinition (`:>> cost_per_unit = liner_rate`) also resolved
(to 7.0). Only usage-level values the current pipeline cannot propagate to an inherited calc
input stay valueless. The two-hop nested-override chain both carries a value (Item 2 wires it)
and stays valueless today → trips. Criterion never relaxed (D6).

**Hand-computed headline expected values (Item 2 SC-B anchor):**
`plant_cost = (target_cost + chamber_cost) / driver_efficiency = (10.0 + 7.0) / 0.35 = 48.5714…`
Assert constraint `viability`: `eta * gain >= threshold` → `0.35 * 40.0 = 14.0 >= 10.0` → holds.
(eta = driver.efficiency = 0.35 cross-part; gain = 40.0 self-named; threshold = 10.0 default.)

**Capture-surface findings (Phase-2 registration inputs):**
- `plant_values`: full graph (3 modules incl. cost_calc), 3 V11 offenders → MODELS + pipeline baseline.
- `plant_value_shapes`: full graph, 6 modules, NO crash (even `out attribute 'net cost'` and the
  Style-E `Mixed Output Style` loaded) → MODELS + pipeline baseline. Observed valueless EPs:
  `rated_cost.rate` (shape-1 nested `:>>` doesn't reach the cross-part input), `flow_calc.flow_rate`
  (shape-4 inherited-attr-redefined-below), `chamber_unit.select.wall` (shape-9 non-float enum EP,
  Item 5 substrate). `revenue=200`, `base=4`, `amount=6`, `footprint=12` valued.
- `deep_cross_scope_probe`: full graph after the rename, 5 modules, 2 V11 offenders → MODELS +
  pipeline baseline (Open Question resolved: full-pipeline).
- `spec_chain_twolevel` extended: 5 modules, 0 offenders; fan-out CONFIRMED collapsed — both
  `scale_a.s` and `scale_b.s` wire to the one EP `TwoLevelLib__IFE_Power_Plant__scale`;
  `maint_calc.rate` → the plain `maintenance_rate` attr; `lcoe_calc.cost_per_joule` → module_output
  (retype shape preserved).

**Assert-constraint substrate (Item 4/5):** authored in the `plant_values` source; its usage
bindings (eta/gain) are currently ABSENT from the extraction snapshot (constraints are not
serialized — the CONSTRAINT-SILENCE bug). Phase 4 pins this observed absence; Item 4 flips it.

**Escape-hatch removals (shape + crash evidence):** NONE. No secondary shape crashed the
extractor — the two only parse fixes were reserved-keyword collisions (`flow` param, `derived`
usage name) and an over-a-bound-value `:>>` (base attr made valueless), not extractor crashes.
**Issues:** `flow` and `derived` are reserved KerML tokens; `:>>` cannot override an already-bound
value. All fixed in the fixture source (no `src/` change).
**Deviations:** (c) is a two-hop nested-override chain rather than a one-hop plain attr, chosen so
it both trips today and carries an Item-2-wireable value (the plain one-hop base-def literal
resolved to a value and did not trip). Faithful to the plan's "plain cross-part-attribute chain,
no calc output" intent.

### Phase 2 Completion
**Completed:**
**D6 gate — committed offender tuples + three-mechanism coverage:**
**Capture surfaces (full-pipeline vs extraction-only per fixture):**
**Byte-identity gate (git status porcelain):**
**Issues:**
**Deviations:**

### Phase 3 Completion
**Completed:**
**quoted_owner_formula field-level diff + review verdict (confirmed / filed):**
**Byte-identity gate:**
**Issues:**
**Deviations:**

### Phase 4 Completion
**Completed:**
**Per-shape observed labels (correct / degraded / diagnostic):**
**V11 pin EXPECTED_UNCOVERED (matches Phase 2?):**
**Issues:**
**Deviations:**

### Phase 5 Completion
**Completed:**
**agentic-mbse impact list (final fixture paths):**
**Fixture-gap register entries filed:**
**Downstream handoffs recorded (Item 2 pin / Item 4/5 substrate):**
**Issues:**
**Deviations:**

---

**Status:** Draft → In Progress → Complete
