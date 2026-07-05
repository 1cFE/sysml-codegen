# Spec: Plant-Idiom Conformance Fixtures

**Status:** Draft
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
the two fixtures Items 9–11 need and captures their known-incomplete baselines,
so each later item's progress shows up as a reviewed baseline diff against a
committed starting point — not against nothing.

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

- **agentic-mbse reference examples.** The two fixture shapes become the canonical
  examples for MODELING_GUIDE plant-idiom guidance. That guidance is *authored* in
  Item 12 (once Items 9–10 define what is actually supported); this item only
  produces the fixtures the guidance will point at, and records the pointer.

## Success Criteria

- [ ] **Both fixtures exist and load.** `tests/fixtures/wi014_toy/` (imported from
      the fusion-tea WI-014 toy) and `tests/fixtures/ife_plant/` (authored) parse
      through `SysMLDataExtractor` and produce a versioned extraction snapshot.
- [ ] **Both fixtures snapshot and run the pipeline without crashing** via the
      graph-level / collector capture path (below). Incomplete output — unresolved
      cross-part inputs falling to Step-4 fallback entry points, dropped
      plain-usage `:>>` overrides, the self-named-binding degenerate result — is
      *expected*, captured, and documented as the known-incomplete baseline. The
      strict CLI `generate` path is **not** the bar (it may raise V11; see below).
- [ ] **The retyping shape actually works in the snapshot.** ife_plant's retyped
      nested parts instantiate their subtype template calcs (virtual CalcUsages
      present in the snapshot) — proving the Item 4/5 win, distinct from the
      deliberately-unwired cross-part shapes.
- [ ] **CURRENT pipeline baselines are captured and committed** for both fixtures
      (computation_graph.json + registry_init.py, via the capture script), so
      Items 9–10 land as reviewed diffs against a known starting point.
- [ ] **The REQ-CA-09 shape-A obligation is discharged** — either a real-fixture
      conformance test asserting the reworded EXPOSE_PURE name-drop warning fires
      on wi014_toy, or a recorded finding stating which warning the toy actually
      fires and why the reworded one cannot be tested until Items 10/11.
- [ ] **agentic-mbse validation is run or its absence recorded.** Fixture models
      pass the agentic-mbse checking scripts, or each failure is understood and
      recorded (with the reason, e.g. the check is sandbox-blocked and deferred to
      Item 12's in-repo run).
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
  contain **all six** shapes so Items 9–11 have their full substrate:
  1. A **generic plant part def with def-declared attributes** (attributes
     declared on the part def, not the usage).
  2. **`:>>`-valued specialized subsystem defs** — subsystem part defs that
     specialize a base and set the base's def-declared attributes via `:>>`
     (SC-5 mechanism A).
  3. **Retyped nested parts** — `part :>> x : Subtype` through the now-supported
     Item 4/5 path; its snapshot must show the subtype template calcs
     instantiating (the working shape).
  4. **Cross-part calc-chain bindings** — a calc input on one part bound to a calc
     output reached through a specialized nested part (SC-5 mechanism B); left
     deliberately unwired (Items 9–10 wire it).
  5. **Plain-usage `:>>` overrides** — `:>>` on plain part usages (SC-5
     mechanism C), currently dropped at extraction; captured as known-incomplete.
  6. **One self-named-binding trap** — `in availability = availability` (SC-5
     mechanism D), as a **negative/diagnostic case**: capture the current
     degenerate resolution (binds to the calc's own parameter) as the baseline
     that Items 9/12 later correct.
- **[INFERRED]** The fixture is a deliberate mix of working and known-incomplete
  shapes. The spec/plan/close-out must state, per shape, whether its snapshot is
  the *correct* result (retyping) or a *known-incomplete* baseline to be improved
  by a later item (mechanisms A, C, D and the cross-part chain B). This is what
  makes the later baseline diffs legible.

### Capture path (the V11 / non-strict interaction)

- **[HARD]** Extraction snapshots are captured via the versioned snapshot path —
  the `sysml-codegen snapshot` CLI subcommand or `scripts/capture_extraction_snapshots.py`
  (both call `snapshot.capture_snapshot`). Requires a **live syside license**
  (R3 — schedule before the 2026-08-06 expiry, or after renewal).
- **[HARD]** CURRENT pipeline baselines are captured at the **graph level** via
  `scripts/capture_pipeline_baselines.py` (`build_full_graph_from_snapshot` →
  `computation_graph.json` + `registry_init.py`), reading the committed extraction
  snapshot. This is the same path catf_mfe uses today — catf_mfe carries a real
  dangling cross-part input (`cryo_load.magnet_volume`) and still captures a clean
  graph baseline, because unresolved *inputs* fall to Step-4 fallback entry points
  rather than tripping the graph-internal producer-channel check
  (`_validate_channel_references`).
- **[HARD]** The success bar is the **graph-level / collector path, not strict CLI
  generation.** Item 7 adds a two-layer params-coverage check: a pure *collector*
  (returns the violation list, raises nothing) and *strict enforcement* (raises
  V11 at the generation boundary). Deliberately-unwired cross-part inputs in these
  fixtures are exactly the uncovered-key case V11 catches. So:
  - "Runs through the pipeline without crashing" means the **graph builds and the
    collector runs** — the path every graph-level conformance test and baseline
    capture uses. This does **not** trip strict V11.
  - The strict `generate` CLI path is *expected* to raise V11 on these fixtures
    (that is V11 working correctly). If an end-to-end generate expectation is
    written at all, it is an inverted assertion (generation raises V11) or an
    `xfail` tracked to Items 9–11 — mirroring Item 7's catf_mfe decision. It is
    not a crash and not a failure of this item.
- **[HARD]** Registration is additive to the existing capture infrastructure: add
  the two fixtures to the `MODELS` dict in `capture_extraction_snapshots.py` and
  `capture_pipeline_baselines.py` (the pattern Items 3/4 used for `return_styles`
  and `retype_model`). **No `src/` production code changes.**
- **[INFERRED]** Capture is **tiered** with a recorded fallback. Attempt the
  full graph-level baseline first. If a fixture's bindings cannot build the graph
  at all — e.g. a CHAIN override producing an unresolvable source path, the way
  `chain_override_probe` / `unresolvable_attr_probe` already need it — fall back to
  the **extraction-only** capture path (`_capture_extraction_only` /
  `EXTRACTION_ONLY_MODELS`) and record which fixture took which tier and why. The
  cross-part chain (mechanism B) is the likely candidate for this fallback; which
  tier it lands in is a plan-time probe, not a spec-time guess.

### Conformance tests

- **[HARD]** Both fixtures land with conformance tests (R1 — real fixtures, never
  mocks): assert each loads, snapshots, and builds its graph (collector path)
  without raising; assert the retyping shape instantiates its subtype template
  calcs; assert the collector reports the *expected* set of uncovered cross-part
  inputs (pinning the known gap the way Item 7 pins catf_mfe's
  `[cryo_load.magnet_volume]`), so Items 9–10 flip those assertions as they wire.
- **[HARD]** The REQ-CA-09 shape-A EXPOSE_PURE test (or its recorded
  impossibility) lands against `wi014_toy`. Whether the toy fires the reworded
  name-drop warning (`graph_builder.py:700`) or the malformed-refs warning
  (`graph_builder.py:689`, as Item 1's minimal probe did) is a **live probe** the
  implement session settles. The obligation is discharged either way: a passing
  test on the reworded warning, or a recorded finding naming the warning that
  actually fires and deferring the reworded-warning test to Items 10/11.

### agentic-mbse validation

- **[HARD]** Run the agentic-mbse checking scripts (`~/1cfe/agentic-mbse`) against
  both fixture models if accessible from the implement session. Record each result;
  understand and record any failure. If the scripts are sandbox-blocked (as
  fusion-tea and agentic-mbse are from this spec session), record that and defer
  the validation run to Item 12 (which executes in the agentic-mbse repo).

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

- **Which capture tier the cross-part chain (mechanism B) lands in** — full
  graph-level baseline vs. extraction-only fallback. Settled by a plan-time probe
  once the fixture is authored; both outcomes are acceptable and recorded.
- **Which EXPOSE_PURE warning the WI-014 toy fires** — the reworded name-drop
  (`:700`) or malformed-refs (`:689`). A live probe selects the REQ-CA-09 test
  form (real test vs. recorded deferral). Do not pre-commit.
- **Exact ife_plant module content** — how many subsystems, which attribute
  names, the specific calc chain. The shape list above is the contract; the
  concrete SysML is an authoring detail for implement, informed by reading the
  real `~/1cfe/fusion-tea/models/ife_plant` shape from a session that can access it.
- **Whether the self-named-binding trap needs a separate isolated fixture** vs.
  living inside ife_plant. Deferred to implement; the requirement is only that the
  degenerate baseline is captured and legible.

## agentic-mbse Impact

Recorded for Item 12; **not built here** (R2).

- **Reference examples.** `wi014_toy` (part-def EXPOSE_PURE / shape A,
  REFERENCE bindings) and `ife_plant` (the full plant idiom — def-declared
  attributes, `:>>`-valued specialized subsystem defs, retyped nested parts,
  cross-part calc chains, plain-usage `:>>` overrides, self-named-binding trap)
  become the canonical reference shapes for the MODELING_GUIDE plant-idiom
  guidance Item 12 authors, once Items 9–10 define what is supported.
- **Self-named-binding check.** The mechanism-D trap is the negative fixture for
  the agentic-mbse Level-2 self-named-binding check the register (A-1) proposes;
  Item 12 builds the check against it.
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
  — the two-layer V11 collector/strict design this item's capture path relies on)

---

**Next Steps:** After approval, proceed to `/_my_plan` (the epic budgets no
separate design for this item — deliverables are `{spec,plan}.md`). The plan
sequences: fixture authoring/import → live extraction snapshot capture (license
window, R3) → graph-level baseline capture with the tier probe → conformance
tests including the REQ-CA-09 discharge → agentic-mbse validation run or recorded
deferral.
