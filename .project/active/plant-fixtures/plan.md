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
**Completed:** 2026-07-05

**Actual Changes:**
- `tests/fixtures/wi014_toy/{toy_library.sysml,toy_plant.sysml}` (NEW) — copied
  byte-for-byte from `~/1cfe/fusion-tea/exploration/construct_validation/`. **No
  path/import/shape adaptation needed** — the toy uses self-contained package
  imports (`ScalarValues::*`, `toy_library::*`).
- `tests/fixtures/wi014_toy/PROVENANCE.md` (NEW) — records fusion-tea HEAD
  `964d3ae4`, toy last-touched commit `dae3942a`, and the no-adaptation import note.
- `tests/fixtures/wi014_toy/extraction_snapshot.json` (NEW) — full-pipeline capture
  via `capture_snapshot`. 2 calc_usages (`area_calc`, `cost_calc`), 1 EXPOSE_PURE
  computed attribute (`total_cost`, `is_on_part_definition=True` — shape A), 0
  channel_aliases (the alias is dropped — see warning below), 7 design_attributes.
- `tests/conformance/test_wi014_toy.py` (NEW) — 2 offline + 2 live tests, all green.

**Live probe — WI-014 warning fired (`:689` malformed-refs / `:700` name-drop):**
**MALFORMED-REFS** (`graph_builder.py:783`, old `:689`). The shape-A
`total_cost = cost_calc.cost` fires
`EXPOSE_PURE total_cost: could not identify instance/output from refs ['cost', 'cost_calc']`.
On a part *def*, the calc-usage instance names are not in `calc_usage_names`, so
`_resolve_expose_pure` cannot separate instance ref (`cost_calc`) from output ref
(`cost`) and returns before reaching the reworded name-drop branch (`:794`). This
reproduces Item 1's minimal-probe finding exactly.

→ **REQ-CA-09 fork = recorded deferral.** Discharged in this file:
`test_wi014_toy_shape_a_fires_malformed_refs` pins the malformed-refs warning as the
current baseline and asserts the name-drop warning does NOT fire; the reworded-warning
test is handed to Items 10/11 (shape-A resolution path, `epic_upstream_findings.md:387`).
Handoff is explicit — not a silent third punt. (Phase 4 obligation satisfied early
since the probe settled it.)

**Issues:** The live warning test captures to `tmp_path` (not the committed snapshot
path) to avoid mutating the fixture on every run.

**Deviations:** REQ-CA-09 discharge (a Phase 4 item) landed here in Phase 0's test
file, since the Phase 0 probe already settled the fork. No functional deviation.

### Phase 1 Completion
**Completed:** 2026-07-05

**Actual Changes:**
- `tests/fixtures/ife_plant/library.sysml` (NEW) — plant part def + subsystem defs +
  6 calc defs (PlantLcoe, DriverPowerCalc, HifCostCalc, ChamberYieldCalc, CoilVolume,
  CryoLoad).
- `tests/fixtures/ife_plant/design.sysml` (NEW) — `Hif Plant` retype specialization,
  `hif_plant` + `baseline_plant` instances, and the shape-4 `magnet_system` cross-part
  calc.
- `tests/fixtures/ife_plant/subsystems.sysml` (NEW) — separate-package `radial_build`
  (the shape-4 cross-part source half; mirrors catf's `CATFMFERadialBuild`).
- `tests/fixtures/ife_plant/extraction_snapshot.json` (NEW) — full-pipeline capture.
- `tests/conformance/test_ife_plant.py` (NEW) — 9 tests, all green (8 offline + 1 live).

**Def-literal count (≥14):** **16** numeric def-declared literals on the plant def
(14 Hawker params + `net_power_target` + `capacity_factor`). Floor met with margin.

**Per-shape labels (correct: 3,7 / known-incomplete: 2,4,5):**
- Shape 1 (**correct**): 16 def literals — richness floor.
- Shape 2 (**known-incomplete**, mech A): `Shielded Core :>> scope_multiplier = 3.0`
  captured as a redefinition (`hierarchy_data.redefinitions`) but unwired (no
  consumer) — Item 9 improves.
- Shape 3 (**correct**): retyped `driver → Hif Driver` instantiates the subtype-owned
  `hif_cost_calc` AND preserves the supertype `base_power_calc`. The Item 4/5 win.
- Shape 4 (**known-incomplete**, mech B): `magnet_system.cryo_load.magnet_volume` bound
  cross-package to `radial_build.magnet_volume_total` (an EXPOSE_PURE/FORMULA reaching a
  calc output through nested `tf_coil`). The chain does not resolve; `magnet_volume`
  falls to a valueless wired Step-4 fallback EP — `collect_uncovered_params` reports
  exactly `[cryo_load.magnet_volume]`, the definitive pin (mirrors catf's
  `[cryo_load.magnet_volume]`). Items 9-10 flip it.
- Shape 5 (**known-incomplete**, mech C): `baseline_plant :>> capacity_factor = 0.95`
  is DROPPED at extraction — only the def default (0.90) survives. Pinned as an
  absence.
- Shape 7 (**correct**): `chamber_a` + `chamber_b` each produce their own virtual
  `yield_calc` — the instance-ambiguity substrate for Item 10.

**Mechanism-B surface probe (Phase 3 open question, settled here):** the graph
**BUILDS** (8 modules) — the expected/success path (like catf's dangling input), NOT
the extraction-only fallback. Pipeline baseline is takeable.

**Issues:**
- Getting shape 4 to actually trip the collector took two iterations. A plant-internal
  parent→child binding (`driver.exposed_power`) and a same-package sibling both
  *resolved* to non-fallthrough valueless EPs (collector = 0, treated as legitimate
  user-fill). The catf shape requires the target to be an EXPOSE reaching a calc output
  **cross-package** so the chain stays unresolvable and falls through. Reaching the
  calc output through the nested part (`tf_coil.volume_calc.volume`) classified the
  source attr as FORMULA (feature-chain-in-formula is unsupported — a captured WARNING),
  which removes it from `design_attributes` and forces the fall-through. Net: collector
  = 1, matching intent.
- Asymmetry (captured baseline detail): the retyped `hif_plant` shows only its driver
  calcs, not its inherited chambers/lcoe; `baseline_plant` shows the chambers/lcoe.
  Shape 7's two siblings come from `baseline_plant`. Both working-shape assertions hold.

**Deviations:** Shape 4's source attr lands as a failed-FORMULA rather than a clean
EXPOSE_PURE (a 2-hop chain to the calc output through the nested part). Net effect
matches catf's known-incomplete cross-part gap; the FORMULA-compile-fail is a captured
known-incomplete surface, not a fixture defect.

### Phase 2 Completion
**Completed:** 2026-07-05

**Actual Changes:**
- `tests/fixtures/self_named_binding_trap/{library,design}.sysml` (NEW) — a minimal
  `'Trap Plant'` with exactly the mechanism-D self-named binding
  `in availability = availability` and nothing else.
- `tests/fixtures/self_named_binding_trap/extraction_snapshot.json` (NEW) —
  extraction-only capture under the timeout guard.
- `tests/conformance/test_self_named_binding_trap.py` (NEW) — 3 tests, all green.

**Trap failure mode (degenerate / diagnostic / recursion-to-timeout):**
**(a) FINITE DEGENERATE RESOLUTION.** The trap extracts cleanly — no recursion, no
hang, no diagnostic (probed under `timeout 150`, exit 0). The self-named binding
resolves to the calc usage's OWN parameter
(`TrapLib::'Trap Plant'::avail_calc::availability`, a REFERENCE self-reference), NOT
the outer part attribute. Captured as the baseline (branch a).
→ The recursion the toy's comments document is an *evaluation-time* syside behavior
(expression evaluation to the step limit), on a different path than *extraction*.
Extraction is finite. **No register A-1 recursion vendor note is triggered** by this
probe. Recorded for Item 12.

**Isolation proof (ife_plant snapshot unaffected):** The trap lives in its own fixture
directory and is captured extraction-only, independently of ife_plant. ife_plant's
snapshot is produced by a separate `capture_snapshot` call on its own directory — the
trap fixture is never in scope, so ife_plant's snapshot is byte-identical whether or
not the trap exists (isolation holds by construction).

**Issues:** None.
**Deviations:** None — benign branch, trap ships with a snapshot as planned.

### Phase 3 Completion
**Completed:** 2026-07-05

**Actual Changes:**
- `scripts/capture_extraction_snapshots.py` — registered `wi014_toy`, `ife_plant` in
  `MODELS` (full-pipeline path); `self_named_binding_trap` in `EXTRACTION_ONLY_MODELS`.
- `scripts/capture_pipeline_baselines.py` — registered `wi014_toy`, `ife_plant` in
  `MODELS`.
- `tests/conformance/conftest.py` — added all three to `SNAPSHOT_MODELS`.
- Committed pipeline baselines:
  `tests/fixtures/baseline_outputs/{wi014_toy,ife_plant}/{computation_graph.json,registry_init.py}`
  (wi014_toy: 2 modules; ife_plant: 8 modules; both `registry_init.py` syntax valid).

**Mechanism-B surface (pipeline baseline / extraction-only fallback + cost):**
**PIPELINE BASELINE** — ife_plant's graph BUILDS (8 modules). The unresolved cross-part
input (shape 4) falls to a Step-4 fallback entry point, exactly as catf_mfe's dangling
`cryo_load.magnet_volume` does. No extraction-only fallback needed; full graph-level
conformance substrate available to Items 9-10.

**Trap capture surface:** extraction-only (`EXTRACTION_ONLY_MODELS`) — the degenerate
self-reference is fully visible in extraction; no pipeline baseline needed.

**Per-shape correct/known-incomplete labeling:** recorded in Phase 1 notes and in
`test_ife_plant.py`'s module docstring (shapes 3,7 correct; 2,4,5 known-incomplete).

**Issues:** None.
**Deviations:** None.

### Phase 3 Completion
**Completed:**
**Actual Changes:**
**Mechanism-B surface (pipeline baseline / extraction-only fallback + cost):**
**Trap capture surface:**
**Issues:**
**Deviations:**

### Phase 4 Completion
**Completed:** 2026-07-05

**Actual Changes:**
- `tests/conformance/test_ife_plant.py` — the conditional collector pin
  (`test_cross_part_inputs_pinned_or_baseline`) + shape 2/5 baseline pins (added in
  Phase 1's file).
- `tests/conformance/test_wi014_toy.py` — REQ-CA-09 discharge (added in Phase 0's file).
- Fixed 6 E501 in `test_ife_plant.py` (wide docstring table → compact list) so the new
  test files are ruff-clean (existing conformance tests carry no E501).

**Item 7 landed at implement time? (collector pin vs baseline-record):**
**LANDED.** `collect_uncovered_params` exists (`resolution/graph_builder.py:664`). The
pin asserts the EXACT expected uncovered set —
`{(ifeplantdesign__magnet_system__cryo_load, magnet_volume,
design_params.IfePlantDesign__magnet_system__cryo_load__magnet_volume)}` — the
definitive assertion form. Items 9-10 flip this. The `else` (Item-7-absent) branch is
retained so the test is satisfiable at either landing order. No Item 7 `src/` code was
written (Non-Goal).

**REQ-CA-09 disposition (real test / recorded deferral to Items 10/11):**
**RECORDED DEFERRAL.** The WI-014 toy's shape-A `total_cost = cost_calc.cost` fires the
**malformed-refs** warning (`graph_builder.py:783`), not the reworded name-drop warning
(`:794`). `test_wi014_toy_shape_a_fires_malformed_refs` pins the malformed-refs warning
as the current baseline and asserts the name-drop warning does NOT fire. The
reworded-warning test is handed to **Items 10/11** (which own the shape-A part-def
resolution path, `epic_upstream_findings.md:387`) — an explicit named handoff, not a
silent punt. Full rationale in `test_wi014_toy.py`'s module docstring.

**agentic-mbse run outcome (run in-session / deferred to Item 12) + expected-flag list:**
**RUN IN-SESSION** (not deferred). Entry point:
`agentic_mbse.validation.runner.run_all_checks(models_path, fail_fast=False)` — a 6-level
SysML quality validation (L1 syntax, L2 structure, L3 dataflow, L4 constraints, L5
traceability, L6 architecture). Run against all three fixture directories.

- **Well-formedness bar (MUST PASS): ALL THREE PASS.** Every fixture passes L1 Syntax
  (0 errors, 0 warnings) plus L2-L5. The fixtures are genuinely well-formed SysML.
- **L6 Architecture & Pipeline Readiness: all three flagged (expected, recorded, NOT
  fixed).** These are agentic-mbse's architecture-readiness findings, not fixture
  defects — the verbatim-imported toy triggers the same, confirming they are the
  checker's view. Enumerated expected-flag list (→ Item 12 negative-fixture / L6-check
  refinement inputs):
  1. **Derived-expression-in-calc-def-output** (all 3): L6 flags `out attribute X =
     <expr over in params>` inside `calc def`s (toy `toy_library.sysml:23,40`; ife_plant
     `library.sysml:36,51,64,77,90`; trap `library.sysml:16`). Per ADR-002 derived
     expressions belong in calc defs, so this is L6 scanning library files over-broadly.
     Recorded; not fixed (altering would break the calc defs).
  2. **Quoted-name EQN-derivation** (toy + trap): L6 cannot derive an EQN from quoted
     multi-word names — `'Panel Area'`, `'Panel Cost'`, `'Toy Plant'`
     (`toy_plant.sysml:36`); `'Trap Plant'` (`library.sysml:31`). ife_plant uses
     unquoted calc-def names and is NOT flagged. Recorded; not fixed (toy is imported
     verbatim — Non-Goal; trap uses a quoted name deliberately for minimalism).
- The mechanism-specific negative checks the spec anticipates (self-named-binding
  Level-2 check, mechanism-A/C/D flags) do **not** exist in agentic-mbse today — that is
  exactly what Item 12 builds against these fixtures. The fixtures are the substrate; the
  checks are Item 12's deliverable.

**Issues:** None that block. The L6 "derived expression" check firing on calc-def
outputs (including the validated verbatim toy) suggests the L6 scan is over-broad — an
input for Item 12 to refine, recorded not fixed here.

**Deviations:** REQ-CA-09 discharge and the collector pin were authored in Phases 0/1's
test files rather than added fresh in Phase 4, since their probes settled earlier. No
functional deviation from the plan.

---

**Status:** Draft → In Progress → **Complete (2026-07-05)** — all 5 phases landed;
gate 1928/4/11; ruff src/ 21; mypy src/ 109; not committed (awaiting audit).
