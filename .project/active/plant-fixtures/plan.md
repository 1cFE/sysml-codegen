# Implementation Plan: Plant-Idiom Conformance Fixtures

**Status:** Draft
**Created:** 2026-07-05
**Last Updated:** 2026-07-05
**Epic Item:** UPSTREAM-FINDINGS Item 8

## Source Documents

- **Spec (the contract):** `.project/active/plant-fixtures/spec.md`
- **Spec review + resolutions:** `.project/active/plant-fixtures/spec-review.md`
- **Epic (Item 8 + consumers 9/10/11):** `.project/backlog/epic_upstream_findings.md`
- **No design.md** — the epic budgets no design for this item (deliverables are
  `{spec,plan}.md`). Component references below point at `spec.md#section` and at
  the existing capture/test infrastructure directly.

## Scope Note (read first)

This item writes **no `src/` production code** (spec Non-Goals). Every deliverable
is a fixture, a capture artifact, a conformance test, or a recorded finding. "Done"
for the incomplete shapes means the *known-incomplete baseline is captured and
labeled*, not that the shape works. Three shapes are the exception — retyping
(shape 3) and the two sibling parts (shape 7) must produce **correct** snapshots;
that is the Item 4/5 win this item proves.

## Implementation Strategy

**Phasing Rationale:**

The order is authoring → capture → tests, with a hard grouping constraint: all
live-license work (parse checks during authoring, and the versioned snapshot
captures) must complete inside one license window (R3 — the single-seat license
expires **2026-08-06**). Fixtures are authored first, iterating parse→fix→parse
against the live license (Phases 0–2). The committed captures are then taken in
one pass (Phase 3). Tests and the license-free graph-build baselines close it out
(Phase 4), since they read committed snapshots and need no license.

The WI-014 toy goes first (Phase 0) because it is an *import*, not authoring — it
is the lowest-risk way to prove the license works and the fixture loader accepts
the library/design split, and it funds the REQ-CA-09 probe early. ife_plant
(Phase 1) is the largest authoring surface and the fixture all of Items 9–11
depend on. The self-named trap (Phase 2) is isolated and capture-guarded, so it
comes after ife_plant is stable and cannot poison it.

**Critical Path:**

live license → WI-014 imports & loads (Phase 0) → ife_plant parses with all six
shapes + ≥14 literals (Phase 1) → trap captured under timeout guard (Phase 2) →
all three snapshots committed (Phase 3) → graph-build baselines + conformance
tests + REQ-CA-09 discharge (Phase 4).

**First Proof Point:**

Phase 0 — `wi014_toy` loads through `SysMLDataExtractor` and produces an extraction
snapshot. This proves (a) the license is live, (b) the import procedure works, and
(c) the shape-A EXPOSE_PURE probe can be run to settle which warning the toy fires
(REQ-CA-09 fork). If Phase 0 fails, everything downstream is blocked — so it is
first and cheap.

**Overall Validation Approach:**

- Suite stays green at every phase boundary — a new fixture must never redden an
  existing test. Run `uv run pytest tests/` after each phase.
- Each fixture lands with two-layer tests (offline snapshot, license-free; live
  extractor, license-gated skip) mirroring `tests/conformance/test_type_indexing.py`.
- Three spec-declared **live probes** are settled during execution and their
  outcomes recorded (not pre-committed): which warning WI-014 fires (Phase 0/4),
  which capture surface the mechanism-B chain lands on (Phase 3), and the trap's
  failure mode (Phase 2). Each has both branches handled below.

---

## Phase 0: WI-014 Toy Import + Load Probe

### Goal

Import the fusion-tea WI-014 toy as `tests/fixtures/wi014_toy/`, confirm it loads,
and run the shape-A EXPOSE_PURE probe that forks the REQ-CA-09 discharge. First
because it is an import (low authoring risk) and it validates the license end-to-end.

### Assumption Under Test

That the WI-014 toy loads in isolation with only path/import adaptation (spec
Fixture 1, `spec.md` §"Fixture 1"), and that its shape-A EXPOSE_PURE surface fires
an identifiable warning at `graph_builder.py:689` (malformed-refs) or `:700`
(reworded name-drop) — the fork that decides the REQ-CA-09 test form.

### Test Stencil (Write This First)

```python
# tests/conformance/test_wi014_toy.py
from tests.conftest import snapshot_fixture, requires_license
from sysml_codegen.snapshot import load_extraction_snapshot

def test_wi014_toy_snapshot_loads():
    snap = load_extraction_snapshot(snapshot_fixture("wi014_toy"))
    assert snap["calc_usages"]              # shape-A EXPOSE_PURE calc present
    # shape-A EXPOSE_PURE marker (a derived-attribute alias on a part def)
    assert snap["computed_attributes"] or snap["channel_aliases"]

@requires_license
def test_wi014_toy_loads_live():
    from sysml_codegen.extraction.extractor import SysMLDataExtractor
    ex = SysMLDataExtractor([FIXTURES_DIR / "wi014_toy"])
    assert ex.load_models()
```

### Changes Required

**Import procedure (executed from the implement session, which can read fusion-tea
— see `spec.md` §"Fixture 1"):**

- [ ] Copy the toy's `.sysml` files from
      `~/1cfe/fusion-tea/exploration/construct_validation/` into
      `tests/fixtures/wi014_toy/`, preserving the library/design split the fixture
      loader expects (see `retype_model/{library,design}.sysml` for the two-file
      shape).
- [ ] Adapt package imports / paths **only** as needed to load in isolation. Do
      **not** alter the EXPOSE_PURE or REFERENCE-binding shapes under test
      (Non-Goal, `spec.md` §Non-Goals).
- [ ] Record the source commit/hash of the imported toy in the fixture (a
      `PROVENANCE` note or header comment) so provenance is traceable.
- [ ] `tests/conformance/test_wi014_toy.py` (NEW) — the load stencil above.

**REQ-CA-09 probe (settle the fork, record the outcome — full discharge in Phase 4):**

- [ ] Load the toy live and drive the EXPOSE_PURE path in
      `resolution/graph_builder.py` (the `_resolve_expose_pure`-style path around
      lines 680–705). Record **which** warning fires: `:689` malformed-refs, or
      `:700` reworded name-drop. This is the live probe the spec names (`spec.md`
      §"Conformance tests", Open Question 2). Do not pre-commit the branch.

### Validation

**Automated:**
- [ ] `uv run pytest tests/conformance/test_wi014_toy.py` → passes (live test skips
      without license)
- [ ] `uv run pytest tests/` → no regressions

**Manual:**
- [ ] Load `wi014_toy` live; confirm it parses without structural errors.
- [ ] Record the fired-warning identity in the Phase 0 implementation notes.

**What We Know Works After This Phase:**
The license is live, the import procedure produces a loadable fixture, and the
REQ-CA-09 fork is settled — Phase 4 knows whether to write a real name-drop test
or a recorded deferral.

---

## Phase 1: Author ife_plant (six shapes, ≥14 def-literals)

### Goal

Author `tests/fixtures/ife_plant/` carrying the six structural shapes from the
spec's shape table, iterating parse→fix→parse against the live license until it
loads clean. This is the fixture Items 9–11 all build against.

### Assumption Under Test

That all six shapes (`spec.md` §"Fixture 2" table — shapes 1, 2, 3, 4, 5, 7)
co-exist in one parseable, structurally well-formed model, and that the **working**
shapes (retyping 3, siblings 7) actually instantiate their subtype template calcs
in extraction — proving the Item 4/5 path, distinct from the deliberately-unwired
shapes.

### Test Stencil (Write This First — asserts against the Phase 3 snapshot)

```python
# tests/conformance/test_ife_plant.py — the Item-7-INDEPENDENT assertions
from tests.conftest import snapshot_fixture
from sysml_codegen.snapshot import load_extraction_snapshot

def test_ife_plant_def_literals_present():
    snap = load_extraction_snapshot(snapshot_fixture("ife_plant"))
    # shape 1 richness floor: >=14 def-declared attribute literals
    lits = _def_declared_literals(snap)     # design_attributes / redefinitions
    assert len(lits) >= 14, len(lits)

def test_retyped_part_instantiates_subtype_calcs():
    snap = load_extraction_snapshot(snapshot_fixture("ife_plant"))
    qns = {cu.qualified_name for cu in snap["calc_usages"]}
    assert any(q.endswith("<subtype_template_calc>") for q in qns)   # shape 3 works

def test_two_sibling_parts_each_produce_own_virtual_calc():
    snap = load_extraction_snapshot(snapshot_fixture("ife_plant"))
    qns = {cu.qualified_name for cu in snap["calc_usages"]}
    # shape 7: two same-type siblings -> two distinct instance-scoped virtual QNs
    assert sum(q.endswith("<sibling_calc>") for q in qns) >= 2
```

### Changes Required

**See `spec.md` §"Fixture 2" for the shape table (the completeness contract) and
the ≥14-literal richness floor. Reference shape:** `~/1cfe/fusion-tea/models/ife_plant`
(read it from the implement session to inform concrete subsystem/attribute names —
`spec.md` Open Question 4). Use the `sysml-conventions` skill and existing fixtures
(`retype_model`, `catf_mfe_model`) as the syntax reference.

- [ ] `tests/fixtures/ife_plant/library.sysml` (NEW) — plant part def + subsystem
      defs + calc defs. Carry the six shapes:
  - Shape 1: generic plant part def with **≥14** def-declared attribute literals
    (declared on the def, not the usage). The richness floor is a HARD contract
    (`spec.md` §"Fixture 2", richness floor) — mirrors the ~14 Hawker parameters
    Item 9 measures against.
  - Shape 2: `:>>`-valued specialized subsystem defs (specialize a base, set its
    def-declared attributes via `:>>`). Mechanism A — known-incomplete.
  - Shape 3: retyped nested parts (`part :>> x : Subtype`) — **working** via Item
    4/5; snapshot must show subtype template calcs instantiating.
  - Shape 4: cross-part calc-chain binding (calc input bound to a calc output
    reached through a specialized nested part), left **deliberately unwired**.
    Mechanism B — known-incomplete.
  - Shape 5: plain-usage `:>>` overrides (`:>>` on plain part usages). Mechanism C
    — currently dropped at extraction, known-incomplete.
  - Shape 7: **two same-type sibling parts** (≥2 usages of one part def side by
    side) — the instance-ambiguity case Item 10's SC names
    (`epic_upstream_findings.md:370`).
- [ ] `tests/fixtures/ife_plant/design.sysml` (NEW) — the design part instantiating
      the plant and its subsystems (mirror `retype_model/design.sysml`).
- [ ] `tests/conformance/test_ife_plant.py` (NEW) — the Item-7-independent stencils
      above, plus a **per-shape label docstring** stating whether each shape's
      snapshot is *correct* (3, 7) or a *known-incomplete baseline* (2, 4, 5)
      (`spec.md` §"Fixture 2", INFERRED per-shape labeling). This labeling is what
      makes the later baseline diffs legible.

**Note — shape 6 (self-named trap) is deliberately NOT here.** It moves to Fixture 3
(Phase 2) so its failure mode cannot poison this snapshot.

### Validation

**Automated:**
- [ ] `uv run pytest tests/` → no regressions (tests that read the snapshot will
      fail until Phase 3 captures it — mark them `xfail(reason="awaits Phase 3
      capture")` or land them in Phase 4; keep the suite green meanwhile).

**Manual (iterative, license-gated):**
- [ ] Load `ife_plant` live via `SysMLDataExtractor`; iterate parse→fix→parse until
      it loads with no structural errors.
- [ ] Confirm the def carries ≥14 literals (count them) and the retyped part +
      both siblings appear in the live calc-usage extraction.

**What We Know Works After This Phase:**
ife_plant parses clean, carries all six shapes and the ≥14-literal floor, and its
working shapes (retyping, siblings) instantiate their template calcs live —
verified before the committed snapshot is taken.

---

## Phase 2: Author the Isolated self_named_binding_trap (timeout-guarded)

### Goal

Author `tests/fixtures/self_named_binding_trap/` — a minimal fixture with exactly
the mechanism-D trap (`in availability = availability`) — and capture whatever the
pipeline does with it under a **bounded timeout**. Isolated so its failure mode
cannot touch ife_plant.

### Assumption Under Test

The trap's failure mode is unknown and settled by a live probe (`spec.md` §"Fixture
3", Open Question 3): (a) finite degenerate resolution (binds to the calc's own
parameter), (b) a diagnostic, or (c) syside recursion up to the timeout. **All
three are acceptable spec outcomes** as long as the result is recorded and does not
touch ife_plant. Isolation and the timeout guard are already-decided (not open) —
only the observed outcome is open.

### Test Stencil (Write This First)

```python
# tests/conformance/test_self_named_binding_trap.py
from tests.conftest import snapshot_fixture
from sysml_codegen.snapshot import load_extraction_snapshot

def test_trap_baseline_recorded():
    # Runs ONLY if the trap survived capture (benign / diagnostic branch).
    # If capture recursed to the timeout, this fixture ships without a snapshot
    # and this test is skipped with the recorded reason (see Phase 3 outcome).
    snap = load_extraction_snapshot(snapshot_fixture("self_named_binding_trap"))
    # Degenerate baseline: self-named binding resolves to the calc's own param,
    # NOT an outer attribute. Pin whatever the current pipeline produced.
    assert snap is not None
```

### Changes Required

**See `spec.md` §"Fixture 3" for the isolation rationale and the three-branch
capture outcome.**

- [ ] `tests/fixtures/self_named_binding_trap/{library,design}.sysml` (NEW) — a
      minimal model containing exactly the self-named binding
      (`in availability = availability`, SC-5 mechanism D). Nothing else that could
      confound the diagnostic.
- [ ] The capture step (executed in Phase 3) runs under a **bounded timeout** (e.g.
      wrap the extraction call with `timeout`/subprocess guard). Record the observed
      failure mode:
  - (a) finite degenerate resolution → capture it as the baseline;
  - (b) diagnostic → capture the diagnostic;
  - (c) hang/recursion up to the timeout → record it, ship **no** snapshot for this
    fixture, and route the observation to the syside vendor note Item 12 files
    (register A-1). ife_plant is untouched either way.
- [ ] `tests/conformance/test_self_named_binding_trap.py` (NEW) — the stencil above,
      skipping cleanly if the trap recursed and shipped no snapshot.

### Validation

**Automated:**
- [ ] `uv run pytest tests/` → no regressions.

**Manual:**
- [ ] Run the trap's extraction under the timeout guard; record which of the three
      branches occurred in the Phase 2 implementation notes.
- [ ] Confirm ife_plant's snapshot (Phase 3) is byte-identical whether or not the
      trap fixture exists — proving isolation held.

**What We Know Works After This Phase:**
The trap's failure mode is observed and recorded, and its isolation is proven — the
one fixture Items 9–11 depend on (ife_plant) is provably unaffected.

---

## Phase 3: Captures — Extraction Snapshots + Pipeline Baselines

### Goal

Commit the versioned extraction snapshots for all three fixtures, and the
graph-build pipeline baselines for every fixture whose graph builds. Grouped here
so all license-gated capture happens in one window (R3).

### Assumption Under Test

That the graph **builds** for all three fixtures — an unresolved cross-part *input*
falls to a Step-4 fallback entry point rather than tripping the graph-internal
producer-channel check (`_validate_channel_references`), exactly as `catf_mfe`'s
dangling `cryo_load.magnet_volume` input does (`spec.md` §"Capture path"). The
mechanism-B chain (shape 4) is the candidate to watch — the plan-time probe below
settles which surface it lands on.

### Changes Required

**Registration is additive — no `src/` changes (`spec.md` §"Capture path",
mechanics). Pattern: the `MODELS` dict additions Items 3/4 used for `return_styles`
and `retype_model`.**

- [ ] `scripts/capture_extraction_snapshots.py:41` — add to `MODELS`:
      `"wi014_toy"`, `"ife_plant"` (full-pipeline path via `capture_snapshot`).
- [ ] `scripts/capture_pipeline_baselines.py:51` — add to `MODELS`
      (`baseline_dir -> snapshot_name`): `"wi014_toy": "wi014_toy"`,
      `"ife_plant": "ife_plant"`. Naming: keep the bare name for both dirs (the
      corpus convention is mixed — `return_styles`/`alias_agg_probe` are bare;
      `spec.md` review L4-1 leaves this to the plan — bare chosen for consistency
      with the spec's fixture paths).
- [ ] Run `uv run python scripts/capture_extraction_snapshots.py` → commits
      `extraction_snapshot.json` for `wi014_toy` and `ife_plant`. **Requires live
      license (R3).**
- [ ] **Mechanism-B surface probe:** run `capture_pipeline_baselines.py` for
      `ife_plant`.
  - *Expected (graph builds):* commit `baseline_outputs/ife_plant/{computation_graph.json,
    registry_init.py}`. This is the success bar — "runs without crashing" = the
    graph builds here (`spec.md` §"Capture path", surface 2).
  - *Fallback (graph genuinely cannot build — e.g. a CHAIN override yielding an
    unresolvable source path, the way `chain_override_probe` needs):* move
    `ife_plant` to `EXTRACTION_ONLY_MODELS` in `capture_extraction_snapshots.py`,
    take **only** an extraction snapshot, and **record the cost explicitly**: no
    pipeline baseline, no graph-level conformance assertions against it, weaker
    Item 9/10 diff substrate (`spec.md` §"Capture path", extraction-only fallback).
    The fallback is the recorded exception, **not** the plan.
- [ ] **Self-named trap capture** (from Phase 2, under timeout guard): if benign,
      add `"self_named_binding_trap"` to `EXTRACTION_ONLY_MODELS` and commit its
      extraction snapshot. If it recursed, ship no snapshot and record the reason.

### Validation

**Automated:**
- [ ] `uv run pytest tests/` → no regressions after committing snapshots/baselines.
- [ ] `uv run python scripts/capture_pipeline_baselines.py` → the added fixtures
      report `syntax: valid` for `registry_init.py`.

**Manual:**
- [ ] Diff the committed `ife_plant` `computation_graph.json`: confirm the
      unresolved cross-part inputs (shapes 2/4/5) landed on Step-4 fallback entry
      points, not a graph-build crash — the known-incomplete baseline.
- [ ] Record, per shape, whether its captured result is *correct* (3, 7) or a
      *known-incomplete baseline* (2, 4, 5) in the Phase 3 notes.
- [ ] Record the mechanism-B surface outcome (baseline vs extraction-only) and the
      trap outcome.

**What We Know Works After This Phase:**
All three fixtures have committed, versioned snapshots; every buildable fixture has
a committed pipeline baseline; and each shape's snapshot is labeled correct vs
known-incomplete — the reviewed starting point Items 9–10 diff against.

---

## Phase 4: Conformance Tests + REQ-CA-09 Discharge + agentic-mbse Validation + Close-out

### Goal

Land the remaining conformance assertions (the Item-7-conditional collector pin,
the REQ-CA-09 discharge), run (or defer) agentic-mbse validation with an enumerated
expected-flag list, and close out CURRENT_WORK. License-free — reads committed
snapshots.

### Assumption Under Test

That the Item-7-independent assertions pass against the committed snapshots, and
that the two order-sensitive obligations (the collector pin, REQ-CA-09) are
satisfiable at **either** Item 7 landing order and **either** warning-fires outcome
— the conditional forms the spec specifies.

### Test Stencil (Write This First — the conditional collector pin)

```python
# in tests/conformance/test_ife_plant.py
import sysml_codegen.resolution.graph_builder as gb
from sysml_codegen.snapshot import build_full_graph_from_snapshot
from tests.conftest import snapshot_fixture

def test_cross_part_inputs_pinned_or_baseline():
    graph, _ = build_full_graph_from_snapshot(snapshot_fixture("ife_plant"))
    collector = getattr(gb, "collect_uncovered_params", None)
    if callable(collector):
        # Item 7 landed: pin the EXACT expected uncovered cross-part inputs
        # (the way Item 7 pins catf_mfe's [cryo_load.magnet_volume]).
        assert collector(graph) == EXPECTED_UNCOVERED   # Items 9-10 flip these
    else:
        # Item 7 not landed: assert only that the graph built, and record the
        # warning set verbatim as the baseline expectation (upgrade when Item 7 lands).
        assert graph.modules   # built without raising; warnings recorded in notes
```

### Changes Required

**See `spec.md` §"Conformance tests" and §"Item 7 sequencing".**

- [ ] `tests/conformance/test_ife_plant.py` — add the conditional cross-part-input
      assertion above. Written so it is satisfiable whether or not Item 7's
      `collect_uncovered_params` (`resolution/graph_builder.py`) exists. **No Item 7
      `src/` code is written here** (Non-Goal). If Item 7 has **not** landed, record
      the verbatim warning set in the Phase 4 notes as the baseline to upgrade later.
- [ ] `tests/conformance/test_wi014_toy.py` — **discharge REQ-CA-09** using the
      Phase 0 probe result:
  - *If the toy fires the reworded name-drop warning (`graph_builder.py:700`):*
    write a real conformance test asserting it fires on `wi014_toy`. Obligation
    discharged with a passing test.
  - *If it fires the malformed-refs warning (`graph_builder.py:689`, as Item 1's
    minimal probe did):* write a recorded finding naming the warning that actually
    fires and why the reworded one cannot be tested until the shape-A resolution
    path exists (Items 10/11), and assert the malformed-refs warning fires as the
    current baseline. Obligation discharged as a recorded deferral — **and the
    handoff to Items 10/11 is explicit** (spec review L3-4: Item 11 scope already
    owns shape A, `epic_upstream_findings.md:387`), so this is not a silent third
    punt.
- [ ] **agentic-mbse validation** (`spec.md` §"agentic-mbse validation"):
  - [ ] From the implement session, identify and **name** the agentic-mbse checking
        entry point / command in `~/1cfe/agentic-mbse` (the spec session could not).
  - [ ] If runnable, run it against all three fixtures. Split the outcome into two
        bars: **(a) well-formedness** — SysML parse validity / structural
        well-formedness; the fixtures **must** pass (a failure here means the
        fixture is genuinely broken — fix the fixture). **(b) supported-subset
        conformance** — the deliberately-unsupported shapes (mechanisms A/C/D,
        cross-part chain B, self-named trap) are **expected** to be flagged; each
        flag is enumerated with its reason and becomes an Item 12 negative-fixture
        reference. **Never** silence a flag by altering the shape under test
        (Non-Goal).
  - [ ] If the scripts are sandbox-blocked from the implement session, record that
        and **defer the run to Item 12**, carrying the enumerated expected-flag list
        forward.
- [ ] **Close-out** — update `.project/CURRENT_WORK.md` with: the three live-probe
      outcomes (WI-014 warning, mechanism-B surface, trap failure mode), the
      per-shape correct/known-incomplete labeling, the REQ-CA-09 disposition, and
      the agentic-mbse impact record (`spec.md` §"agentic-mbse Impact"): the three
      fixtures named as the reference examples for Item 12's MODELING_GUIDE
      plant-idiom guidance, and the enumerated expected-flag list.

### Validation

**Automated:**
- [ ] `uv run pytest tests/conformance/test_ife_plant.py tests/conformance/test_wi014_toy.py
      tests/conformance/test_self_named_binding_trap.py` → all pass (live tests skip
      without license).
- [ ] `uv run pytest tests/` → full suite green (no existing test reddened).
- [ ] `uv run ruff check` and `uv run mypy src/` → clean (test files only; no `src/`
      changes, so mypy scope is unchanged).

**Manual:**
- [ ] Confirm the REQ-CA-09 obligation is discharged in one of the two specced forms
      and the disposition is recorded.
- [ ] Confirm the agentic-mbse expected-flag list is enumerated (or the run is
      deferred to Item 12 with the list carried forward).

**What We Know Works After This Phase:**
Items 9–11 have their full committed substrate — three loadable fixtures, labeled
known-incomplete baselines, conditional collector pins ready to flip, and a
discharged REQ-CA-09 obligation. The blind spot that justified the SC-5 deferral is
closed.

---

## Environment Setup

**See CLAUDE.md for full environment rules.** Key commands:
- Install: `uv pip install -e ~/agentic-mbse && uv pip install -e ".[dev]"`
- Tests: `uv run pytest tests/`
- Single test: `uv run pytest tests/conformance/test_ife_plant.py -k <name>`
- Capture extraction snapshots (live license): `uv run python scripts/capture_extraction_snapshots.py`
- Capture pipeline baselines (license-free): `uv run python scripts/capture_pipeline_baselines.py`
- **License window (R3):** the single-seat syside license expires **2026-08-06** —
  schedule Phases 0–3 inside that window (or after renewal). Phase 4 is license-free.

## Risk Management

**Phase-Specific Mitigations:**

- **Phase 0 (import fidelity):** the toy's source is outside this session's sandbox
  — the import procedure is the deliverable, executed from the implement session
  which can read fusion-tea. Risk: adapting shapes instead of just paths. Mitigation:
  the Non-Goal forbids altering EXPOSE_PURE/REFERENCE shapes; record the source
  commit for a traceable diff.
- **Phase 1 (six shapes in one model):** the shapes interact, and a parse error in
  one can mask another. Mitigation: iterate parse→fix→parse against the live
  license; add shapes incrementally, re-parsing after each; use `sysml-conventions`
  + `retype_model`/`catf_mfe_model` as the syntax reference.
- **Phase 2 (trap recursion poisoning ife_plant):** the register flags syside-level
  recursion for `in availability = availability`. Mitigation: the trap is in its
  own fixture dir with its own timeout-guarded capture — decided, not deferred. If
  it recurses, ife_plant is provably untouched.
- **Phase 3 (mechanism-B surface unknown):** the cross-part chain may or may not
  build a graph. Mitigation: both surfaces are handled — pipeline baseline
  (expected, like catf_mfe's dangling input) or extraction-only fallback (recorded
  cost). Not a free choice; the fallback is the recorded exception.
- **Phase 4 (Item 7 order + REQ-CA-09 fork):** both obligations are order/probe
  sensitive. Mitigation: the collector pin is written conditionally on
  `collect_uncovered_params` existing; REQ-CA-09 is written to discharge in either
  warning-fires branch. Both are satisfiable without writing Item 7 `src/` code.

**Suite-green invariant:** a new fixture must never redden an existing test. Run
`uv run pytest tests/` at every phase boundary. Snapshot-reading tests authored
before their Phase 3 capture are `xfail`-guarded until the snapshot lands.

## Implementation Notes

[TO BE FILLED DURING IMPLEMENTATION — Leave empty now]

### Phase 0 Completion
**Completed:**
**Actual Changes:**
**Live probe — WI-014 warning fired (`:689` malformed-refs / `:700` name-drop):**
**Issues:**
**Deviations:**

### Phase 1 Completion
**Completed:**
**Actual Changes:**
**Def-literal count (≥14):**
**Per-shape labels (correct: 3,7 / known-incomplete: 2,4,5):**
**Issues:**
**Deviations:**

### Phase 2 Completion
**Completed:**
**Actual Changes:**
**Trap failure mode (degenerate / diagnostic / recursion-to-timeout):**
**Isolation proof (ife_plant snapshot unaffected):**
**Issues:**
**Deviations:**

### Phase 3 Completion
**Completed:**
**Actual Changes:**
**Mechanism-B surface (pipeline baseline / extraction-only fallback + cost):**
**Trap capture surface:**
**Issues:**
**Deviations:**

### Phase 4 Completion
**Completed:**
**Actual Changes:**
**Item 7 landed at implement time? (collector pin vs baseline-record):**
**REQ-CA-09 disposition (real test / recorded deferral to Items 10/11):**
**agentic-mbse run outcome (run in-session / deferred to Item 12) + expected-flag list:**
**Issues:**
**Deviations:**

---

**Status:** Draft → In Progress → Complete
