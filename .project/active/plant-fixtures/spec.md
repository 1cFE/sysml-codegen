# Spec: Plant-Idiom Conformance Fixtures

**Status:** Implementation Complete (2026-07-05) — awaiting audit
**Owner:** Reid W
**Created:** 2026-07-05
**Complexity:** MEDIUM
**Branch:** upstream-findings-epic
**Epic Item:** UPSTREAM-FINDINGS Item 8

---

## Problem

The plant idiom — a generic plant part def whose attributes are valued by `:>>`
on specialized subsystem defs, with retyped nested parts and cross-part calc
chains — was deferred once already on the evidence "0 cross-part refs found
across all models" (`epic_attribute_expression_capture.md:89,432`). That evidence
base is invalid: it only holds because **no fixture in the corpus contains the
idiom**. 1,500+ conformance tests caught none of SC-5 for the same reason — the
shapes that break were never modeled.

SC-5 (cross-part wiring) is staged across Items 9–11. Every one of them needs a
real SysML fixture to build against, snapshot, and diff — R1 forbids new behavior
without a real fixture, and the whole point of this epic is that the blind spot
never justifies a deferral again. Right now that substrate does not exist.

This item closes the blind spot **before** SC-5 implementation begins. It builds
the fixtures Items 9–11 need — the imported WI-014 toy, an authored ife_plant
carrying six of the plant idiom's structural shapes, and an isolated
self-named-binding trap — and captures
their known-incomplete baselines, so each later item's progress shows up as a
reviewed baseline diff against a committed starting point — not against nothing.

Two obligations ride along:

- **The REQ-CA-09 shape-A EXPOSE_PURE test, deferred from Item 1.** Item 1
  reworded the EXPOSE_PURE name-drop warning but could not test it against a real
  fixture: the only in-repo EXPOSE fixtures are shape B (part-*usage*), and a
  minimal shape-A probe fired the *malformed-refs* warning
  (`graph_builder.py:689`), not the reworded *name-drop* warning
  (`graph_builder.py:700`). Item 1 recorded the fallback: the real-fixture test
  waits for Item 8's imported toy. This item must discharge that obligation — land
  the test, or record precisely why the reworded warning still cannot be tested
  against a real fixture until the shape-A resolution path exists (Items 10/11).

- **agentic-mbse reference examples.** The fixture shapes become the canonical
  examples for MODELING_GUIDE plant-idiom guidance. That guidance is *authored* in
  Item 12 (once Items 9–10 define what is actually supported); this item only
  produces the fixtures the guidance will point at, and records the pointer.

## Success Criteria

- [ ] **All three fixtures exist and load.** `tests/fixtures/wi014_toy/` (imported
      from the fusion-tea WI-014 toy), `tests/fixtures/ife_plant/` (authored), and
      `tests/fixtures/self_named_binding_trap/` (the mechanism-D trap, isolated —
      see below) parse through `SysMLDataExtractor` and produce a versioned
      extraction snapshot.
- [ ] **Every fixture snapshots and runs the pipeline without crashing** via the
      graph-build capture path (below). Incomplete output — unresolved cross-part
      inputs falling to Step-4 fallback entry points, dropped plain-usage `:>>`
      overrides, the self-named-binding degenerate result — is *expected*,
      captured, and documented as the known-incomplete baseline. The strict CLI
      `generate` path is **not** the bar (it may raise V11; see below).
- [ ] **The retyping shape actually works in the snapshot.** ife_plant's retyped
      nested parts instantiate their subtype template calcs (virtual CalcUsages
      present in the snapshot) — proving the Item 4/5 win, distinct from the
      deliberately-unwired cross-part shapes.
- [ ] **CURRENT pipeline baselines are captured and committed** for every fixture
      whose graph builds — `computation_graph.json` + `registry_init.py` via
      `capture_pipeline_baselines.py`. The graph is *expected* to build for all
      three (an unresolved cross-part *input* falls to a Step-4 fallback, it does
      not stop graph assembly — catf_mfe proves this). **Fallback:** if a fixture's
      graph genuinely cannot build (a CHAIN override yielding an unresolvable
      source path, the way `chain_override_probe` needs), it gets an
      extraction-snapshot only and no pipeline baseline — with the reason recorded,
      and the cost noted (Items 9–10 lose that fixture's pipeline-diff substrate;
      see the capture-path section).
- [ ] **The REQ-CA-09 shape-A obligation is discharged** — either a real-fixture
      conformance test asserting the reworded EXPOSE_PURE name-drop warning fires
      on wi014_toy, or a recorded finding stating which warning the toy actually
      fires and why the reworded one cannot be tested until Items 10/11.
- [ ] **Fixtures pass agentic-mbse well-formedness, and their deliberately
      unsupported shapes are flagged-and-recorded, not fixed.** Two distinct bars:
      (a) SysML parse validity / structural well-formedness — the fixtures **must**
      pass; (b) supported-subset conformance — the deliberately-unsupported shapes
      (mechanisms A/C/D, cross-part chain B, self-named trap) are **expected** to be
      flagged. Each expected flag is enumerated with its reason and becomes an
      Item 12 negative-fixture reference. A flag is never "fixed" by altering the
      shape under test (Non-Goal).
- [ ] **agentic-mbse impact recorded** — the fixtures are named as the reference
      examples for Item 12's MODELING_GUIDE plant-idiom guidance.

## Known Requirements

### Fixture 1 — WI-014 toy (imported)

- **[HARD]** Import the fusion-tea WI-014 toy
  (`~/1cfe/fusion-tea/exploration/construct_validation/`) as a conformance fixture
  under `tests/fixtures/wi014_toy/`. It covers **part-def EXPOSE_PURE (shape A)**
  and the **REFERENCE-binding warning paths**. The source lives outside this
  session's sandbox, so this spec cannot enumerate its exact contents — the
  **import procedure** is the deliverable, executed from the implement session
  (which can read fusion-tea):
  1. Copy the toy's `.sysml` files into `tests/fixtures/wi014_toy/`, preserving
     the library/design split the fixture loader expects.
  2. Adapt package imports / paths only as needed to load in isolation; **do not**
     alter the modeling shapes under test (EXPOSE_PURE, REFERENCE bindings).
  3. Record the source commit/hash of the imported toy in the fixture so its
     provenance is traceable.
- **[INFERRED]** The toy is the shape-A EXPOSE_PURE case the research names as
  "the toy" (`total_cost`-style derived attribute on a part def with calcs,
  instantiated separately — `toy_plant__demo_plant__cost_calc`). It is the fixture
  that funds the deferred REQ-CA-09 test.

### Fixture 2 — ife_plant (authored)

- **[HARD]** Author `tests/fixtures/ife_plant/` shaped after the fusion-tea
  ife_plant idiom (reference shape: `~/1cfe/fusion-tea/models/`, sandbox-blocked
  from this session; the shape is enumerated below and in the epic). It must
  contain **six** shapes so the downstream items have their substrate. Each shape
  maps to the item that consumes it — the mapping is the completeness contract, so
  no consumer's success criterion is left without a fixture to build against:

  | # | Shape | SC-5 mech | Consumed by |
  |---|-------|-----------|-------------|
  | 1 | Generic plant part def with def-declared attribute **literals** (declared on the def, not the usage) — **≥14** of them (see richness floor) | — | Item 9 (def-literal pre-fill) |
  | 2 | `:>>`-valued specialized subsystem defs (specialize a base, set its def-declared attributes via `:>>`) | A | Item 9 (literal pre-fill) |
  | 3 | Retyped nested parts (`part :>> x : Subtype`) — the **working** shape via the Item 4/5 path; snapshot shows subtype template calcs instantiating | — | Item 10 (retype-honoring index) |
  | 4 | Cross-part calc-chain binding (a calc input bound to a calc output reached through a specialized nested part), left deliberately unwired | B | Item 10 (cross-part wiring) |
  | 5 | Plain-usage `:>>` overrides (`:>>` on plain part usages) — currently dropped at extraction | C | Item 9 (override capture) |
  | 7 | **Two same-type sibling parts** (≥2 usages of one part def side by side) — the instance-ambiguity case | — | Item 10 (per-instance binding rewrite) |

  Shape 6 (the self-named-binding trap, mechanism D) is deliberately **not** here —
  it moves to its own fixture (Fixture 3) so its failure mode cannot poison this
  snapshot; its consumers are Item 9 (the rewrite path that rescues self-named
  bindings) and Item 12 (the agentic-mbse check). Item 11's EXPOSE-surfacing
  consumer is served by `wi014_toy`'s shape A. All three fixtures together give
  Items 9–11 their full substrate.

- **[HARD]** *Richness floor (shape 1).* The plant part def carries **at least ~14
  def-declared attribute literals**, mirroring the Hawker parameter count Item 9
  measures against (`epic_upstream_findings.md:334,340` — WI-015 evidence went from
  2/16 and 0 keys to a meaningful pre-fill). A 1–2-literal fixture satisfies the
  letter of Item 8 but starves Item 9: you cannot demonstrate a 16-key JSON filling
  from a 2-key fixture. The floor is a spec-time contract, not an authoring detail.

- **[HARD]** *Instance-ambiguity (shape 7).* Item 10's success criterion is
  "Instance-ambiguity case (two same-type sibling parts) covered by a test"
  (`epic_upstream_findings.md:370`). A single retyped part (shape 3) does not
  exercise per-instance binding rewrite — two same-type siblings do. ife_plant must
  contain ≥2 sibling usages of one part def so that test has its fixture.

- **[INFERRED]** The fixture is a deliberate mix of working and known-incomplete
  shapes. The spec/plan/close-out must state, per shape, whether its snapshot is
  the *correct* result (retyping; sibling parts instantiate) or a *known-incomplete*
  baseline to be improved by a later item (mechanisms A, C and the cross-part chain
  B). This per-shape labeling is what makes the later baseline diffs legible.

### Fixture 3 — self-named-binding trap (authored, isolated)

- **[HARD]** Author `tests/fixtures/self_named_binding_trap/` — a minimal fixture
  containing exactly the mechanism-D trap: a self-named binding
  (`in availability = availability`, SC-5 mechanism D), which resolves to the
  calc's own parameter rather than an outer attribute. It is a **negative /
  diagnostic case**: capture whatever the current pipeline does with it as the
  baseline that Items 9/12 later correct.
- **[HARD]** *Isolation is mandatory, not deferred.* The epic's Item 12
  out-of-scope list names "**self-named-binding recursion** (register A-1 vendor
  note)" (`epic_upstream_findings.md:420`) — a known syside-level recursion concern,
  not a guaranteed-benign resolve. If `in availability = availability` triggers
  syside recursion during *extraction*, a co-located trap would hang or crash the
  entire ife_plant snapshot — the one fixture Items 9–11 all depend on. The trap
  therefore lives in its **own fixture directory with its own snapshot**. The
  asymmetry is decisive: if the trap is benign, a separate dir costs nothing; if it
  recurses, co-location loses all of ife_plant.
- **[HARD]** *Capture with a timeout guard and a recorded outcome either way.* The
  trap's extraction/snapshot capture step runs under a bounded timeout. Record the
  observed failure mode: (a) a finite degenerate resolution (binds to the calc's
  own parameter) — capture it as the baseline; (b) a diagnostic — capture the
  diagnostic; (c) a hang/recursion up to the timeout — record it and route it to
  the syside vendor note Item 12 files (register A-1). The outcome is settled by a
  live probe; all three are acceptable spec outcomes as long as the result is
  recorded and does not touch ife_plant.

### Capture path (three surfaces, three sensitivities)

The capture story is the spec's riskiest content, so read the three surfaces
first, then the mechanics. They differ in what they depend on and what "success"
means:

1. **Extraction snapshot** (`sysml-codegen snapshot` CLI /
   `capture_extraction_snapshots.py`). Always produced. Needs a live syside
   license. Item-7-independent.
2. **Graph-build pipeline baseline** (`capture_pipeline_baselines.py` →
   `build_full_graph_from_snapshot` → `computation_graph.json` +
   `registry_init.py`). Reads the committed snapshot; **needs no license and does
   not invoke Item 7's collector.** Order-independent — works whether or not
   Item 7 has landed. This is the success bar: "runs without crashing" = the graph
   builds here.
3. **Strict CLI `generate`.** *Expected to raise V11* on the deliberately-unwired
   cross-part inputs once Item 7 lands (that is V11 working, not a crash). It is
   **not** the bar. Any end-to-end generate expectation is written as an inverted
   assertion (generation raises V11) or `xfail` tracked to Items 9–11 — mirroring
   Item 7's catf_mfe decision.

Mechanics:

- **[HARD]** Extraction snapshots are captured via the versioned snapshot path —
  the `sysml-codegen snapshot` CLI subcommand or
  `scripts/capture_extraction_snapshots.py` (both call `snapshot.capture_snapshot`
  on the full-`MODELS` path). Requires a **live syside license** (R3 — schedule
  before the 2026-08-06 expiry, or after renewal).
- **[HARD]** CURRENT pipeline baselines are captured via
  `scripts/capture_pipeline_baselines.py` (`build_full_graph_from_snapshot` →
  `computation_graph.json` + `registry_init.py`), reading the committed extraction
  snapshot. The graph is *expected* to build for all three fixtures: this is the
  same path catf_mfe uses, and catf_mfe carries a real dangling cross-part input
  (`cryo_load.magnet_volume`) yet still captures a clean graph baseline — unresolved
  *inputs* fall to Step-4 fallback entry points rather than tripping the
  graph-internal producer-channel check (`_validate_channel_references`).
- **[HARD]** *Extraction-only fallback (separate script, honest cost).* The two
  scripts are **not** two tiers of one script — the pipeline-baseline script has a
  single `MODELS` dict and no fallback: a fixture is either in it (gets a pipeline
  baseline) or absent (gets none). The extraction-only path
  (`_capture_extraction_only` / `EXTRACTION_ONLY_MODELS`) lives only in
  `capture_extraction_snapshots.py` and produces **only** an extraction snapshot —
  a thinner one (it runs `SysMLDataExtractor` directly, so no `compilation_results`
  / CalcUsage auto-impl). If a fixture's graph genuinely cannot build (a CHAIN
  override yielding an unresolvable source path, the way `chain_override_probe`
  needs), it takes this path — and the cost is explicit: **no pipeline baseline for
  that fixture, no graph-level conformance assertions against it, weaker Item 9/10
  diff substrate.** The mechanism-B cross-part chain is the candidate to watch;
  which surface it lands on is a plan-time probe. The expectation is that it builds
  the graph (like catf_mfe's dangling input); the extraction-only outcome is the
  recorded fallback, not the plan.
- **[HARD]** Registration is additive to the existing capture infrastructure: add
  the fixtures to the `MODELS` dict in `capture_extraction_snapshots.py` and
  `capture_pipeline_baselines.py` (the pattern Items 3/4 used for `return_styles`
  and `retype_model`); the self-named trap, if it survives capture, joins
  `capture_extraction_snapshots.py`. **No `src/` production code changes.**

### Item 7 sequencing (soft, not a dependency)

- **[INFERRED]** The orchestrator's intent is that Item 7 commits **before** Item 8
  implements, so the collector-pin assertion (below) is available. But the epic
  gives Item 8 **no hard dependency on Item 7** (`epic_upstream_findings.md:300,452`)
  and both are in flight. This spec is therefore **self-sufficient at either
  order** — no HARD requirement depends on Item 7's unlanded `src/` code:
  - **Baseline capture** (surface 2) never touches the collector — always works.
  - **The collector-pin conformance assertion** is written conditionally (see
    Conformance tests): *if* Item 7's collector exists, assert the exact expected
    violation list; *else* assert the graph builds without raising and record the
    warning set verbatim as the baseline expectation, to be upgraded to the
    collector assertion when Item 7 lands.
  - If the collector pin is wanted at first pass, schedule Item 7 first — a soft
    sequencing note, not a blocker.

### Conformance tests

- **[HARD]** Every fixture lands with conformance tests (R1 — real fixtures, never
  mocks): assert each loads, snapshots, and **builds its graph without raising**;
  assert the retyping shape instantiates its subtype template calcs; assert the two
  same-type sibling parts each produce their own virtual CalcUsage (the
  instance-ambiguity substrate). These assertions are Item-7-independent.
- **[HARD]** The uncovered-cross-part-input assertion is **conditional on Item 7**,
  so it is satisfiable at either landing order:
  - *If Item 7's collector exists:* assert the collector reports the **exact
    expected** set of uncovered cross-part inputs (pinning the known gap the way
    Item 7 pins catf_mfe's `[cryo_load.magnet_volume]`), so Items 9–10 flip those
    assertions as they wire.
  - *If it does not:* assert only that the graph builds without raising, and
    **record the warning set verbatim** as the baseline expectation. When Item 7
    lands, upgrade this to the collector-pin assertion.
  Either way the requirement is met without writing Item 7's `src/` code (Non-Goal).
- **[HARD]** The REQ-CA-09 shape-A EXPOSE_PURE test (or its recorded
  impossibility) lands against `wi014_toy`. Whether the toy fires the reworded
  name-drop warning (`graph_builder.py:700`) or the malformed-refs warning
  (`graph_builder.py:689`, as Item 1's minimal probe did) is a **live probe** the
  implement session settles. The obligation is discharged either way: a passing
  test on the reworded warning, or a recorded finding naming the warning that
  actually fires and deferring the reworded-warning test to Items 10/11.

### agentic-mbse validation

- **[HARD]** Run the agentic-mbse checking scripts (`~/1cfe/agentic-mbse`) against
  all fixture models if accessible from the implement session — first identifying
  and naming the checking entry point / command from the agentic-mbse repo, since
  this spec session cannot (sandbox-blocked). Distinguish **two bars**:
  - **Well-formedness (must pass).** SysML parse validity and structural
    well-formedness. A fixture that fails this is genuinely broken — fix the
    fixture.
  - **Supported-subset conformance (expected to flag, record don't fix).** The
    fixtures deliberately exceed the supported subset, and agentic-mbse's job is to
    catch exactly those shapes. So a flag on a mechanism-A/C/D, cross-part-chain-B,
    or self-named-trap shape is **success, not failure**. Enumerate each expected
    flag with its reason; each becomes an Item 12 negative-fixture reference.
    **Never** silence a flag by altering the shape under test (Non-Goal).
- **[HARD]** If the scripts are sandbox-blocked from the implement session (as
  fusion-tea and agentic-mbse are from this spec session), record that and defer
  the validation run to Item 12 (which executes in the agentic-mbse repo), carrying
  the enumerated expected-flag list forward.

## Non-Goals

- **Any production `src/` code change.** No matcher fixes, no `:>>`-capture, no
  cross-part wiring, no alias surfacing — those are Items 7, 9, 10, 11. This item
  produces fixtures, captures, and tests only.
- **Fixing the known-incomplete shapes.** Mechanisms A/C/D and the cross-part
  chain B are captured as known-incomplete baselines here; Items 9–11 improve them.
- **Authoring MODELING_GUIDE plant-idiom guidance.** That is Item 12, gated on
  Items 9–10 defining the supported subset. This item only names the reference
  fixtures.
- **Altering the imported WI-014 modeling shapes.** Import adapts paths/imports
  only, never the shapes under test.

## Open Questions / Deferred to plan/implement

- **Which capture surface the cross-part chain (mechanism B) lands on** — the
  graph-build pipeline baseline (expected) or the extraction-only fallback (if the
  graph cannot build). A plan-time probe settles it; both outcomes are handled and
  their costs recorded (see the capture-path section). *Not* a free choice — the
  fallback is the recorded exception, not the plan.
- **Which EXPOSE_PURE warning the WI-014 toy fires** — the reworded name-drop
  (`:700`) or malformed-refs (`:689`). A live probe selects the REQ-CA-09 test
  form (real test vs. recorded deferral). Do not pre-commit.
- **The self-named trap's failure mode** — finite degenerate resolution,
  diagnostic, or syside recursion up to the timeout. Settled by a live probe; all
  three are acceptable and recorded (recursion routes to Item 12's syside vendor
  note). The trap's isolation (own fixture dir) and the timeout guard are **already
  decided** (Fixture 3) — only the observed outcome is open.
- **Exact ife_plant module content beyond the shape+floor contract** — the
  specific subsystem/attribute names and the exact calc chain. The ife_plant
  shape table and the ≥14-literal richness floor are the contract; the concrete SysML
  within them is an authoring detail for implement, informed by reading the real
  `~/1cfe/fusion-tea/models/ife_plant` shape from a session that can access it.

## agentic-mbse Impact

Recorded for Item 12; **not built here** (R2).

- **Reference examples.** `wi014_toy` (part-def EXPOSE_PURE / shape A,
  REFERENCE bindings), `ife_plant` (def-declared attribute literals, `:>>`-valued
  specialized subsystem defs, retyped nested parts, cross-part calc chains,
  plain-usage `:>>` overrides, two same-type sibling parts), and
  `self_named_binding_trap` (mechanism D) become the canonical reference shapes for
  the MODELING_GUIDE plant-idiom guidance Item 12 authors, once Items 9–10 define
  what is supported.
- **Self-named-binding check.** The isolated mechanism-D trap fixture is the
  negative fixture for the agentic-mbse Level-2 self-named-binding check the
  register (A-1) proposes; Item 12 builds the check against it. If the trap
  recursed during capture, that observation is the vendor-note payload Item 12
  files (register A-1 syside note).
- **Expected-flag list.** The enumerated supported-subset flags from the
  agentic-mbse validation run (each deliberately-unsupported shape and its reason)
  are the negative-fixture references Item 12 builds checks against.
- **Validation run.** If the agentic-mbse checking scripts could not run against
  these fixtures from the implement session (sandbox), Item 12 runs them in-repo
  and records the result.
- **No guidance authored in this item.** The guidance content itself is Item 12's
  deliverable; this item hands it the substrate.

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_upstream_findings.md` (Item 8 + R1/R2/R3 +
  Items 9/10/11 — the consumers of these fixtures)
- **Required Reading:**
  - `.project/research/20260705_upstream-findings-deep-research.md` (§SC-5 four
    mechanisms A–D; §SC-7 shape A vs. B)
  - `~/1cfe/fusion-tea/.project/reports/2026-07-05-upstream-findings-register.md`
    (findings register)
  - `docs/architecture/modeling-assumptions.md` (§5 retyping — the now-supported
    path; §3 EXPOSE; supported subset the fixtures deliberately exceed)
  - `~/1cfe/fusion-tea/exploration/construct_validation/` (WI-014 toy — import
    source, sandbox-blocked from this session)
  - `~/1cfe/fusion-tea/models/` (ife_plant reference shape, sandbox-blocked)
- **Upstream obligation:** `.project/active/baseline-diagnostics/` (Item 1 — the
  deferred REQ-CA-09 shape-A EXPOSE_PURE test this item discharges)
- **Downstream consumers:** `.project/active/plant-prefill/` (Item 9),
  `.project/active/cross-part-wiring/` (Item 10),
  `.project/active/alias-surfacing/` (Item 11) — to be created
- **In-flight sibling:** `.project/active/warning-reconciliation/spec.md` (Item 7
  — the two-layer V11 collector/strict design; the collector-pin conformance
  assertion is *conditional* on Item 7, not a hard dependency — see Item 7
  sequencing)

---

**Next Steps:** After approval, proceed to `/_my_plan` (the epic budgets no
separate design for this item — deliverables are `{spec,plan}.md`). The plan
sequences: fixture authoring/import (ife_plant with the shape table and the
≥14-literal floor; the isolated trap under a timeout guard) → live extraction
snapshot capture (license window, R3) → graph-build baseline capture, with the
mechanism-B surface probe and the trap-failure-mode probe → conformance tests
(Item-7-independent assertions plus the conditional collector pin, and the
REQ-CA-09 discharge) → agentic-mbse validation split into well-formedness vs.
supported-subset flags, run or deferred to Item 12.
