# Implementation Plan: Cross-Part Channel Wiring (SC-5 stage 2)

**Status:** Draft
**Created:** 2026-07-05
**Last Updated:** 2026-07-05
**Epic Item:** UPSTREAM-FINDINGS Item 10 (the riskiest item — design went three review rounds, now stable)
**Complexity:** HIGH — 2-day item, two stages inside one item

## Source Documents
- **Spec:** `.project/active/cross-part-wiring/spec.md`
- **Design:** `.project/active/cross-part-wiring/design.md` ← component details, seams, invariants, the
  two-stage split. Every phase below references it by section rather than restating it.
- **Design review:** `.project/active/cross-part-wiring/design-review.md` (both rounds + resolutions —
  C1-C6, M1-M6 are the findings the phases below discharge)

---

## Implementation Strategy

**Phasing rationale.** The design splits the item into stage (a) (classification + confirm + registration
+ lookup, against committed fixtures, flips both V11 pins) and stage (b) (a new precedence resolver + three
companion fixtures, delivers gamma → lcoe). See `design.md#the-split-decision-first-and-loud`. The plan
mirrors that split and front-loads a **probe battery (Phase 0)** because the design's own round-2 review
(C4) showed the headline — "stage (a) flips both pins" — is *contradicted* by the committed extraction
snapshot unless D9's `reference_chain` capture is viable. Phase 0 licenses that viability in code before any
production edit, with two hard stops.

Inside stage (a), the order is dictated by data dependency: D9 capture (Phase 1) unblocks the leaf tag
(Phase 2), which the confirm pass (Phase 3) consumes, which the registration/lookup (Phase 4) reads, which
the baseline flips (Phase 5) prove. Stage (b) authors its three fixtures **current-incomplete first**
(Phase 6, the Item 8 pattern) so the resolver (Phase 7) shows each flip as a separately-attributable diff.
The live WI-015 anchor + docs close it out (Phase 8).

**Critical path:** Phase 0 (B7 viable) → Phase 1 (`reference_chain` in the data) → Phase 3 (confirm walk
flips a pin) → Phase 5 (both pins flip, suite green) is stage (a) shipped. Everything else hangs off that
spine.

**First proof point:** Phase 0's B7 probe — `extract_feature_chain_name`'s segment-list analog returns
`["tf_coil","volume_calc","volume"]` for the ife_plant pin and the two-segment alias chain for catf_mfe.
If that fails, D9 has no input on any path and stage (a) flips neither pin (hard stop, see
`design.md#B7`). This is the whole D9→confirm chain's foundation and it is cheap to check.

**Why 9 phases for a "6-8 phase" item:** Phase 0 is a non-code probe and Phase 8 is docs/anchor; the seven
implementation phases map 1:1 to the design's enumerated seams so the implementer never has to re-derive a
boundary. The count is deliberate, not scope creep.

**Overall validation approach:**
- Each phase starts red-first with real Pydantic/extraction objects — **no mocks** (spec [HARD], mocks
  masked SC-6/SC-3 historically).
- **Suite green at every phase boundary except the two enumerated regen steps** (Phase 5 recapture, Phase 6
  fixture capture), where the gate moves by a reviewed, attributable diff.
- Current gate to hold/advance from: **1932 passed / 4 skipped / 11 xfailed; ruff src/ 21; mypy src/ 109.**
- License note: live extraction needs the syside license, **expires 2026-08-06**. Phases 0, 5, 6, 8 have
  license-gated steps — do them inside the window or after renewal. Stage (a)'s pin-flip *gates* run on
  offline snapshots once Phase 5 has recaptured them.

---

## Phase 0: Probe Battery (license live, BEFORE any production code)

### Goal
Collapse the five design uncertainties that the reviews flagged as "resolve at implement, probe-first"
(`design.md#next-stage-handoff`) *before* writing production code, and enforce two hard stops. This is
"de-risk first" made executable.

### Assumption Under Test
That D9's `reference_chain` capture is producible for **both** pin shapes (B7), and that relaxing the
classifier reclassifies **only** the enumerated set (M1) — no surprise churn.

### Probes (each writes its result into "Probe Results" below; no `src/` edits)
- [x] **B7 — segment capture (the gating probe).** In a scratch script, load ife_plant + catf_mfe live and
  call the whole-chain walk `extract_feature_chain_name` (`expression_utils.py:250-280`) uses (`.operands[0]`
  + `.target_feature.name`). Confirm it yields `["tf_coil","volume_calc","volume"]` for ife_plant's
  `magnet_volume_total` (`subsystems.sysml:12`) and the alias chain for catf_mfe's `tf_coil.volume`
  (`radial_build.sysml:582`+`:458`). See `design.md#B7`.
- [x] **B1 re-confirm — both pins reason-one.** Trace both pins against the *live* registry (not just
  source): each resolves to a single canonical channel, instance-independent. See `design.md#B1`.
- [x] **`extract_feature_refs` truncation cause (probe 1, non-gating).** Read the agentic-mbse internal that
  truncates `tf_coil.volume_calc.volume` → `[tf_coil]`. Confirms D9's segment-list seam is the right one.
  Does **not** gate — D9 uses the in-repo chain walker, not `extract_feature_refs` (`design.md#D9`).
- [x] **M1 expected-churn table.** Enumerate **every** computed attribute on catf_mfe **and** ife_plant that
  the new leaf-tag rule (INV-E: `reference_chain` ≥ 2 segments, single terminal leaf) would re-tag
  FORMULA→tentative. Record each: attr name, source line, has-cross-part-consumer?, expected final
  classification. Confirm `first_wall_area`/`magnet_surface_area` are single-hop (sibling calc) and
  **unaffected** (`design.md#potential-risks`, M1 bullet).
- [x] **M2 aggregation-walker interaction.** Confirm which of the re-tagged exposes (if any) feed
  `_build_aggregation_module`'s alias map (`graph_builder.py:264-277,1172+`) and that INV-E keeps
  two-terminal chains out (`design.md#M2`).

### HARD STOPS (stop and report to orchestrator; do not proceed to Phase 1)
- **B7 fails** — no segments producible for either pin shape → D9 is unbuildable, stage (a) flips neither
  pin. Invoke the m1 fallback (`design.md#next-stage-handoff`): the pin moves to stage (b), split headline
  revised. **STOP and report.**
- **Churn table shows reclassification beyond the enumerated set** — the relaxation reaches an attribute the
  design did not anticipate → the Phase-5 capture diff is not attributable. **STOP and report** for a
  design amendment.

### Validation
**What we know after this phase:** D9 is buildable (or we stopped); the exact Phase-5 baseline churn is
written down and bounded; the m1 fallback is live-or-moot. **No production code exists yet — nothing to
run in the suite.**

---

## Phase 1: D9 `reference_chain` Capture (stage a — do this first, it unblocks everything)

### Goal
Add the additive full-chain-segments field the confirm walk reads. Nothing downstream can be built until the
segments exist as data on both the live and offline paths. See `design.md#D9` and `design.md#implementation-notes`
(first bullet).

### Assumption Under Test
That an additive `reference_chain: list[str] | None = None` serializes/deserializes cleanly with **no
`SNAPSHOT_FORMAT_VERSION` bump**, and old snapshots degrade to `None` → FORMULA (today's behavior).

### Test Stencil (Write This First)
```python
def test_reference_chain_captured_live():
    # live-extract ife_plant; magnet_volume_total carries the full chain
    ca = extract_ca(ife_plant, "magnet_volume_total")
    assert ca.reference_chain == ["tf_coil", "volume_calc", "volume"]

def test_old_snapshot_degrades_to_none():
    # a committed pre-Item-10 snapshot: field absent → None (no crash, no version fail)
    ca = load_ca_from_snapshot(old_snapshot_json)
    assert ca.reference_chain is None
```

### Changes Required
**See `design.md` for:** D9 decision, the segment-list analog rationale, the no-version-bump precedent
(SC-10 additive-degrade).

- [x] **Test file** (`tests/unit/test_computed_attribute_extractor.py` or a new red-first test) — the two
  stencils above, on real objects.
- [x] `extraction/data_models.py:214-217` — add `reference_chain: list[str] | None = None` as a **trailing
  defaulted** dataclass field (safe; verified the default block sits at the end).
- [x] `extraction/computed_attribute_extractor.py` — at live extraction, populate `reference_chain` with the
  segment-list analog of `extract_feature_chain_name` (`expression_utils.py:250-280` — return the list
  instead of joining).
- [x] `snapshot/serializer.py` — auto-included (loops `dataclasses.fields`, `:171`); confirm no field
  exclusion needed.
- [x] `snapshot/loader.py:467-485` — add `reference_chain=d.get("reference_chain")` (`:474` region).
- [x] **Do NOT bump `SNAPSHOT_FORMAT_VERSION`** (`snapshot/__init__.py`) — see M6.

### Validation
**Automated:** red-first tests pass; full suite green (this field is inert until Phase 2 reads it); mypy/ruff
clean. **Manual:** load one committed pre-Item-10 snapshot → no version-gate failure, `reference_chain is
None`. **What we know works:** the walk's input exists as data on both paths; the offline gate has what it
needs (this closes C4's "no segments to follow").

---

## Phase 2: Leaf Tentative Tag + INV-E Gate (stage a)

### Goal
Have the leaf tag `EXPOSE_CHAIN_TENTATIVE` structurally — **without** deciding EXPOSE-ness (it cannot, B5).
See `design.md#D6`, `design.md#INV-E`, and Component Overview (`_classify_attribute_expression`).

### Assumption Under Test
That the INV-E gate (`reference_chain` ≥ 2 segments rooted at a part-typed waypoint, single terminal leaf)
tags **both** pin shapes and **over-tagging is safe** — an unresolvable tentative reverts later (INV-D).

### Test Stencil (Write This First)
```python
def test_multihop_chain_tagged_tentative():
    ca = classify(reference_chain=["tf_coil", "volume_calc", "volume"], root_is_feature_chain=True)
    assert ca == EXPOSE_CHAIN_TENTATIVE

def test_arithmetic_over_chain_stays_formula():
    # OperatorExpression root fails the FeatureChainExpression gate → never tagged (INV-D negative)
    ca = classify(reference_chain=[...], root_is_feature_chain=False)
    assert ca == FORMULA
```

### Changes Required
**See `design.md` for:** the tentative-state representation (a distinct enum value no downstream consumer
reads, D6), why the leaf cannot decide (B5), the round-1 "one ref after removing waypoints" rule that gave
**zero** for the real pin and is replaced (C4).

- [x] Add `EXPOSE_CHAIN_TENTATIVE` to `ComputedAttributeClassification`
  (`extraction/data_models.py`, enum).
- [x] `extraction/computed_attribute_extractor.py:104-109` — when the root is a pure `FeatureChainExpression`
  (`:104-106`) AND `reference_chain` satisfies INV-E, return `EXPOSE_CHAIN_TENTATIVE` instead of dropping to
  FORMULA. Do **not** test terminal-is-an-output.
- [x] Red-first tests above + a two-terminal-chain case that **stays FORMULA** (never tagged — the INV-E
  guard that keeps ambiguous aliases out of the resolvers, M2).

### Validation
**Automated:** tests pass; **full suite green** — the tentative is inert until the Phase-3 confirm pass reads
it, and Phase 3 also adds the INV-F asserts, so no reader sees a survivor yet. mypy/ruff clean.
**What we know works:** both pin shapes get tagged; genuine formulas do not.

> **Ordering note:** Phases 2 and 3 are a tight pair — the leaf tag is only safe once the confirm pass +
> INV-F asserts exist to consume/trap it. If a boundary between them leaves a tentative readable by a silent
> `if`/`elif`, do them in one working session and land them together. The suite-green boundary is *after*
> Phase 3.

---

## Phase 3: Confirm Pass (Phase 3b) + INV-F Asserts + INV-G Ordering (stage a — the heart)

### Goal
Finalize every tentative to EXPOSE (+register) or revert to FORMULA by a transitive walk over
`reference_chain`, add the four `else: raise` asserts that make INV-F real, and fix the removal ordering so a
reverted tentative produces no false entry point. This is the design's C2/C6 fix and the mechanism that
actually flips both pins. See `design.md#D6`, `design.md#INV-F`, `design.md#INV-G`, and the Architecture
phase diagram.

### Assumption Under Test
Three at once: (i) the walk resolves ife_plant's direct calc-output terminal AND catf_mfe's alias terminal
one hop further (C1's unifying claim); (ii) a reverted tentative leaves **no** JSON entry point (C6b/INV-G);
(iii) a surviving tentative **raises** at every reader (C6a/INV-F).

### Test Stencil (Write This First)
```python
def test_confirm_flips_both_pin_shapes():
    reg = build_output_registry(...)  # real registry, both fixtures
    assert classification_after_confirm("ife_plant", "magnet_volume_total") == EXPOSE_PURE
    assert classification_after_confirm("catf_mfe", "magnet_volume_total") == EXPOSE_PURE  # alias hop

def test_reverted_tentative_no_entry_point():
    # a tentative that does NOT resolve reverts to FORMULA and is removed from design_attrs
    ctx = build_pipeline_context(fixture_with_unresolvable_multihop)
    assert "the_reverted_attr" not in json_entry_points(ctx)  # C6b/INV-G

def test_surviving_tentative_raises_at_each_reader():
    # synthetic tentative that escapes confirm → each of the 4 readers raises
    for reader in (registry_phase1c, module_build, agg_alias_map, attr_resolution_map):
        with pytest.raises(...):
            reader(ca_with_surviving_tentative)
```

### Changes Required
**See `design.md` for:** the confirm-pass Implementation Note (transitive walk, `_visited` cycle guard
modeled on `_resolve_aggregation_input_channel` `graph_builder.py:1043-1079` — the **real** recursive analog,
M5), the exact reader sites (INV-F), and the phase-order evidence (INV-G).

- [x] **Confirm pass (Phase 3b)** in `build_output_registry` (`resolution/output_registry_builder.py`) —
  runs **after** Phase 3 single-hop aliases, **before** Phase 4. Per tentative: walk `reference_chain`
  left-to-right building an instance path from waypoint segments; at the terminal look up a scoped channel
  (direct — ife_plant) or an alias, following one alias hop to its channel (catf_mfe); carry the M5 `_visited`
  guard. Resolve → register alias + set `EXPOSE_PURE` **in place**; else → set `FORMULA` in place.
- [x] **INV-F asserts** — add `else: raise` on a surviving `EXPOSE_CHAIN_TENTATIVE` at all four readers:
  `output_registry_builder.py:120` (Phase 1c), `graph_builder.py:253` (module build), `:274` (aggregation
  alias map), `:834` (`_build_attribute_resolution_map`).
- [x] **INV-G ordering** in `orchestration/pipeline_builder.py` — a **second** `_remove_formula_from_design_attrs`
  pass at Step 5.6 (twin of the Step-4.5 removal at `:133`); move `group_deriver` construction from `:528`
  to Step 5.7, **after** that removal, so it consumes final `design_attrs`. The Step-4.5 removal stays
  (genuine FORMULAs).
- [x] Red-first tests above; plus an aggregation-fixture regression (M2 guard at the walker entry).
- [x] **M6 in-place constraint:** the confirm pass must mutate the **shared** `computed_attrs` objects in
  place — an implementer who rebuilds from copies serializes live tentatives. State this in a code comment.

### Validation
**Automated:** all three stencils pass; **full suite green** (both pins now flip in-graph, but committed
snapshots/baselines are recaptured in Phase 5 — until then, snapshot-driven tests that assert the *old*
FORMULA classification will need the recapture; keep offline pin-flip assertions gated on the Phase-1 field
being present). mypy/ruff clean. **What we know works:** the confirm walk flips both pin shapes; a reverted
tentative is a true no-op (no false EP); no tentative can escape silently.

---

## Phase 4: #4 Part-Def Expose Expansion + #1 Structured Scoped-Alias Lookup + Shape-A Test (stage a)

### Goal
Populate `_scoped_alias` (#4 registration) and read it (#1 lookup) with a structured `ScopedAliasKey`, so a
consumer of a part-def EXPOSE resolves — landing the SC-7 shape-A test on wi014_toy. See `design.md#D7`,
`design.md#D4`, `design.md#INV-B`.

### Assumption Under Test
That #4 writes `("demo_plant","total_cost")` into `_scoped_alias` and #1 reads it by splitting the consumer's
`source_path` at the **last** dot — they meet by construction. The **inertness gate** proves #4 actually
wrote something.

### Test Stencil (Write This First)
```python
def test_scoped_alias_populated_after_wi014(registry):
    assert ("demo_plant", "total_cost") in registry._scoped_alias  # inertness gate (C5)

def test_shape_a_consumer_resolves(registry):
    ch = resolve_chain_dispatch(source_path="demo_plant.total_cost")
    assert ch == "demo_plant__..__cost_calc__cost"  # SC-7 shape-A; REQ-CA-09 pin flips PASS

def test_tuple_key_no_collapse():
    assert ("a", "b.c") in reg._scoped_alias and ("a.b", "c") not in reg._scoped_alias  # C3 closed
```

### Changes Required
**See `design.md` for:** the ScopedAliasKey NewType + `_scoped_alias` namespace (Component Overview),
part-def expansion timing (`is_on_part_definition=True` template → expand per instance path via the same
`find_instance_paths_for_partdef` helper `_build_chain_aliases` uses), the split-at-last-dot lookup.

- [x] `core/identifier_types.py` — `ScopedAliasKey = NewType("ScopedAliasKey", tuple[str, str])`.
- [x] `core/output_registry.py` — a dedicated `_scoped_alias: dict[ScopedAliasKey, ...]` namespace, distinct
  from the flat `_alias`; register/lookup methods storing the tuple **unjoined**.
- [x] `extraction/computed_attribute_extractor.py:245` — drop the `not is_part_def` guard; emit a template
  expose alias for part-def EXPOSE. (Deviation: guard kept; iterate `computed_attrs` in the helper instead —
  same D7 outcome, no template-alias warning noise. See Phase-4 completion note.)
- [x] `orchestration/pipeline_builder.py` — new helper mirroring `_build_chain_aliases` (`:338-391`): expand
  the part-def expose per instance path, writing `(instance_path, exposed_leaf)` into `_scoped_alias`
  (Phase-3 alias walk).
- [x] `analysis/dependency_backtracker.py:592-615` — insert the structured `_scoped_alias` lookup step in
  `_resolve_chain_dispatch`, split `source_path` at the last dot → `ScopedAliasKey((prefix, leaf))`, ordered
  **after** Step 1b, **before** the unscoped Step 2 (INV-A). Reuse `_is_self_reference` unchanged.
- [x] Red-first: inertness gate, shape-A resolution, tuple-key no-collapse. Flip wi014_toy's REQ-CA-09
  recorded-deferral pin to PASS.

### Validation
**Automated:** tests pass; **full suite green**; mypy/ruff clean. **Manual:** `_scoped_alias` non-empty after
registering wi014_toy. **What we know works:** #4 populates and #1 reads the same key by construction (C5
closed); the shape-A consumer resolves; no stringly-typed scope boundary (C3 closed).

---

## Phase 5: Stage (a) Baseline Flips + Enumerated Recapture (stage a close — REGEN BOUNDARY)

### Goal
Recapture the multi-hop-carrier snapshots and flip both committed V11 pins to clean strict generation, with
the M1 churn matching Phase 0's table. This is stage (a) shipped. See `design.md#validation-approach` (stage
(a) executable gate) and `design.md#integration-strategy`.

### Assumption Under Test
That exactly the enumerated set changes: ife_plant shape-4 pin + catf_mfe pin + catf_mfe's enumerated
multi-hop re-tag set + wi014_toy shape-A — and the three non-flipping baselines stay **byte-identical**.

### Changes Required (this phase MOVES the gate by a reviewed diff — suite-green exception)
**See `design.md` for:** the recapture set (M6: catf_mfe, ife_plant), the byte-identity regression net.

- [x] **Recapture (license-gated)** catf_mfe + ife_plant (+ wi014_toy) extraction snapshots — per-fixture,
  writing into each fixture's own dir so `source_file` stays model-relative (the prior session's "path drift"
  was a wrong `output_dir`, not a real problem). They now carry `reference_chain`. Other snapshots untouched.
- [x] Regenerate the catf_mfe pipeline baseline; the diff is ONE wiring flip (cryo_load.magnet_volume →
  tf_coil channel) + execution_order reindex. (ife baseline needed no regen — its graph structure held.)
- [x] Assert **ife_plant** `EXPECTED_UNCOVERED` in `test_ife_plant.py` shrinks by `cryo_load.magnet_volume`
  (now empty).
- [x] Assert **catf_mfe** `[cryo_load.magnet_volume]` flips via the alias-terminal hop, clean strict
  generation.
- [x] Confirm the non-flipping baselines are **byte-identical** — only the 4 enumerated fixtures changed
  (catf/ife/wi014 snapshots + catf baseline); `git status` clean otherwise.

### Validation
**Automated:** targeted pin-flip assertions pass; the recapture diff matches the M1 table exactly; mypy/ruff
clean. **Suite gate:** re-run `uv run pytest tests/` — the churned baselines/snapshots are expected deltas;
everything else green. **What we know works:** stage (a) is a real, shippable, executable win — both V11 pins
wired, license-free offline snapshots henceforth.

---

## Phase 6: Stage (b) Fixtures — Authored + Captured Incomplete FIRST (stage b — REGEN BOUNDARY)

### Goal
Author the three companion fixtures (one novel mechanism each, D8) and capture their **current-incomplete**
baselines *before* the resolver lands, so Phase 7 shows each flip as a separately-attributable diff (the Item
8 pattern). See `design.md#D8`, `design.md#D3`.

### Assumption Under Test
That three minimal single-mechanism fixtures reproduce SC-2/SC-3/SC-4 cleanly and each captures as an
isolated incomplete baseline.

### Changes Required (REGEN BOUNDARY — captures land current-incomplete)
- [ ] `tests/fixtures/spec_chain_channel/` — a retyped nested part whose calc **output** wires into a
  cross-part consumer (the gamma → lcoe analog, SC-2).
- [ ] `tests/fixtures/sibling_channel_ambiguity/` — two same-type siblings where a consumer binding
  disambiguates to the correct instance-scoped channel (SC-3).
- [ ] `tests/fixtures/self_named_rescue/` — a self-named `in x = x` with a **resolvable** upstream (the
  positive companion to `self_named_binding_trap`, SC-4).
- [ ] **Capture (license-gated)** each fixture's extraction snapshot + current-incomplete pipeline baseline
  via `scripts/capture_*.py` (R3). These carry `reference_chain` (recapture set, M6).
- [ ] Conformance tests per fixture, red-first, asserting the current-incomplete state (the pin the resolver
  will flip in Phase 7).

### Validation
**Automated:** each fixture extracts + graph-builds; conformance tests assert the incomplete state; mypy/ruff
clean. **Suite gate:** re-run — new fixtures redden no existing test. **What we know works:** stage (b) has
its required committed substrate; each mechanism is isolated (attribution guaranteed).

---

## Phase 7: Stage (b) Precedence Resolver + Pin Flips (stage b — ESCALATION-GUARDED)

### Goal
Build the per-instance precedence resolver in `_rewrite_virtual_bindings` and flip each Phase-6 fixture's pin
as a reviewed diff. See `design.md#implementation-notes` (#3 precedence resolver, M4 scope) and the
Architecture #3 bullet.

> ### ESCALATION GUARD (design-mandated, M4)
> **If stage (b) exceeds a single day at implement, STOP and report to the orchestrator for a split-out
> ruling — do not push through.** The estimate is against the true scope below, not "one seam."

### Assumption Under Test
That the resolver — second index + type-select + three-tier merge + two branches — rewrites per instance
behind INV-2 without corrupting same-type siblings (B3).

### Test Stencil (Write This First)
```python
def test_gamma_to_lcoe_edge_present(pipeline_yaml):
    assert edge(gamma_output, lcoe_input) in pipeline_yaml  # SC-2

def test_sibling_disambiguates_to_correct_channel(graph):
    assert consumer_binding_resolves_to("chamber_b__..__output")  # SC-3, not a collision

def test_self_named_rescued_to_upstream(graph):
    assert self_named_binding_source == "upstream_channel"  # SC-4
```

### Changes Required
**See `design.md` for:** the four resolver pieces (M4), the INV-2 safety (B3, `usage_extractor.py:399`
`[copy.copy(b) ...]`), the M5 cycle guard, mechanism D's home (REQ-VBR-10).

- [ ] `orchestration/pipeline_builder.py:190-266` — in `_rewrite_virtual_bindings`:
  - a **second index** over `hierarchy_data.redefinitions` keyed by specializing-def QN (Item 9's index at
    `:202-216` is `design_overrides`-only — this is new);
  - a **type-select** step consuming `usage_type_map` (threaded, not yet read by the rewrite) to pick the
    applicable specializing def per virtual instance;
  - the **three-tier merge** (usage override > specialized-def `:>>` > base def);
  - extend the **CHAIN branch** (`:262-264`) and the **bare-name/mechanism-D branch** (`:242-251`) — self-named
    `in x = x` rewritten to the upstream channel; no resolvable upstream → leave as-is (the negative
    `self_named_binding_trap` case);
  - `_visited` cycle guard per M5.
- [ ] Flip each Phase-6 fixture's pin; re-capture each baseline as a separate reviewed diff.
- [ ] Red-first tests above.

### Validation
**Automated:** all three fixture pins flip; **full suite green** (fixture baselines re-captured as attributed
diffs); mypy/ruff clean. **What we know works:** the gamma → lcoe edge, sibling disambiguation, and
mechanism-D rescue all resolve from generated wiring alone.

---

## Phase 8: WI-015 Live Anchor + Docs + Release Notes + Handoff (close)

### Goal
Prove the end-to-end fusion-tea anchor, move the docs/matrix/REQ IDs with the code, and record the Item-12 +
fusion-tea handoffs. See `spec.md#wi-015-anchor-verification-procedure` and `design.md#agentic-mbse-impact`.

### Assumption Under Test
That generated wiring alone reproduces WI-015 run-C's lcoe within the register's tolerance — no
hand-plumbing, no two-pass feedback.

### Changes Required
- [ ] **WI-015 anchor (license-gated, needs fusion-tea read access):** generate the fusion-tea IFE set with no
  hand-plumbing; assert the gamma → lcoe edge in the artifact; run run-C end-to-end; **record run-C's lcoe
  number** and confirm it matches the register's anchor within tolerance. Record gamma's **moved** EQN/channel
  name for the coordination note.
- [ ] **Docs lockstep:** `reference/11-analysis-backtracker.md`, `24-dual-resolution-architecture.md`,
  `25-hierarchy-resolver.md`, `16-computed-attributes.md`, `12-virtual-binding-rewrite.md`; **REQ-CA-03
  revised in place**; new REQ IDs (REQ-BT-11 #1, REQ-CA-10 #2, REQ-VBR-10 #3; REQ-HR-09 released);
  verification-matrix rows (V12 multi-hop-EXPOSE, V13 specialization-chain).
- [ ] **Release notes:** channel renames (gamma EQN moves — before/after from the live run); fusion-tea
  coordination note (`hif_driver_instance` deletable, two-pass gamma feedback removable — deletion is
  upstream, recorded here).
- [ ] **agentic-mbse MODELING_GUIDE content list for Item 12** (`design.md#agentic-mbse-impact`): supported
  cross-part shapes + the redefinition-precedence rule + the self-named-binding FAIL check + its
  `self_named_binding_trap` negative fixture.
- [ ] **Update `.project/CURRENT_WORK.md`** — Item 10 status, gate numbers, what shipped in each stage.

### Validation
**Automated:** full suite green; mypy/ruff clean; verification-matrix rows present. **Manual:** WI-015 run-C
lcoe matches the register within tolerance; docs reviewed against the code. **What we know works:** the
epic's real end-to-end anchor reproduces from generated wiring; the Item-12 and fusion-tea handoffs are
recorded.

---

## Environment Setup

**See CLAUDE.md for full environment rules.** Test: `uv run pytest tests/`; type: `uv run mypy src/`;
lint: `uv run ruff check src/`. Capture/regen: `scripts/capture_*.py` (never hand-edit baselines, R3).
Live extraction / capture needs the syside license (**expires 2026-08-06**) — Phases 0, 5, 6, 8.

## Risk Management

**See `design.md#potential-risks` for the full analysis (M1, M2, C6b, M6, license, catf collision).**

**Phase-specific mitigations:**
- **Phase 0:** the two hard stops (B7 fail, churn beyond enumerated) are the gate; nothing builds on an
  unproven D9.
- **Phase 3:** confirm-or-revert makes over-tagging safe (INV-D); the no-false-EP and fail-fast tests are
  red-first; the M6 in-place-mutation constraint is a code comment.
- **Phase 5/6:** regen boundaries — every diff attributed against the Phase-0 M1 table / captured incomplete
  first; three non-flipping baselines byte-identical.
- **Phase 7:** the escalation guard (one day → STOP) is enforced; INV-2 per-instance copy protects siblings.

## Implementation Notes

### Probe Results (Phase 0 — COMPLETE, 2026-07-05, license live)

Run live via `scratch_probe_phase0.py` / `scratch_ast_inspect.py` / `scratch_probe_b1.py`
(all non-`src/` scratch; deleted after recording).

**HARD-STOP OUTCOMES — neither fired. Cleared to proceed.**
- B7: **PASS** (segments producible for both pins — see deviation D-A below).
- Churn table: **within the enumerated set** (exactly 3 attrs, no surprise reach).

**B7 — segment capture (gating).** Both pins produce full segments, BUT NOT via the design's
named mechanism. Raw AST (via `scratch_ast_inspect.py`):
- ife_plant `radial_build.magnet_volume_total = tf_coil.volume_calc.volume` (3-deep):
  `FeatureChainExpression(operands[0]=FeatureRef 'tf_coil', target_feature=<anon Feature with
  chaining_features=[CalcUsage 'volume_calc', AttrUsage 'volume']>)`. `target_feature.name` is
  **None** — the deeper segments live in `target_feature.chaining_features`.
- catf_mfe `catf_radial_build.magnet_volume_total = tf_coil.volume` (2-deep):
  `FeatureChainExpression(operands[0]='tf_coil', target_feature=AttrUsage 'volume')` —
  `target_feature.name='volume'`.
- **DEVIATION D-A (absorbable, Phase 1 seam):** the design's D9/B7 said
  `extract_feature_chain_name` (operands[0] + `.target_feature.name`) "already walks the whole
  chain — return the list instead of joining." **It does NOT** for 3-deep chains: it yields
  `['tf_coil']` (1 segment) for the ife pin, which fails the INV-E ≥2 gate → the ife pin would
  NOT be tagged → the "flips BOTH pins" headline would fail. Fix: the segment walk must expand
  `target_feature.chaining_features` when present (fall back to `.name` when absent). With that
  correction both pins yield the right segments:
  - ife: `['tf_coil','volume_calc','volume']` → INV-E tentative ✓
  - catf: `['tf_coil','volume']` → INV-E tentative ✓
  This is a strictly-more-correct implementation of the SAME D9 seam (capture full segments); no
  architecture/phase/invariant change. Recorded, absorbed into Phase 1. NOT a hard stop (B7's
  underlying bet — "segments are producible as data" — holds; only the named API was incomplete).

**M1 expected-churn table (INV-E gate = pure FeatureChainExpression ∧ ≥2 segments ∧
`reference_chain[0]` ∉ calc_usage_names).** Exactly **3** attributes re-tag FORMULA→tentative
across both fixtures (49 FeatureChain attrs scanned):

| Fixture | Attr | Line | Segments | Cross-part consumer? | Expected final |
|---|---|---|---|---|---|
| ife_plant | `radial_build.magnet_volume_total` | subsystems.sysml:12 | `[tf_coil,volume_calc,volume]` | **yes** (`cryo_load.magnet_volume`) | EXPOSE (resolves) |
| catf_mfe | `catf_radial_build.magnet_volume_total` | radial_build.sysml:582 | `[tf_coil,volume]` | **yes** (`cryo_load.magnet_volume`) | EXPOSE (resolves) |
| catf_mfe | `catf_radial_build.blanket_volume_total` | radial_build.sysml:583 | `[blanket,volume]` | no | EXPOSE (resolves; collateral re-tag) |

The design anticipated `magnet_volume_total` + `blanket_volume_total` on catf ("and others") —
probe shows there are **no others** (a subset of the anticipated set). `first_wall_area` /
`magnet_surface_area` confirmed calc-usage-rooted (already EXPOSE_PURE) → **unaffected**. All
other 46 FeatureChain attrs are calc-usage-rooted (root_is_calc=True) → simple EXPOSE_PURE, not
re-tagged. **No churn beyond the enumerated set → no hard stop.**

**B1 — both pins reason-one (live registry).** Both resolve to a single, instance-independent
canonical channel:
- ife: `_scoped['radial_build.tf_coil.volume_calc.volume']` →
  `IfePlantSubsystems__radial_build__tf_coil__volume_calc__volume`. Clean direct resolution.
- catf: terminal channel `CATFMFERadialBuild__catf_radial_build__tf_coil__volume_calc__volume`
  is unique in `_scoped`. **BUT** the flat `_alias['tf_coil.volume']` is collision-corrupted →
  points to `...plasma_region__volume_calc__volume` (25 first-wins collisions, 3 distinct keys —
  every nested part's `volume` EXPOSE alias collides on `volume_calc.volume`).
- **DEVIATION D-B (absorbable, Phase 3 confirm-walk):** the confirm walk must resolve the alias
  terminal (catf's `volume`) by re-resolving the alias's canonical (`volume_calc.volume`) in the
  current instance scope via `_scoped` → `catf_radial_build.tf_coil.volume_calc.volume` →
  correct channel. It must **NOT** read the flat `_alias` value (that mis-wires to plasma_region —
  exactly bet B2's false-positive-resolution failure). This is consistent with the design's
  "follow one alias hop to its channel" (D6/#2); it sharpens *how*: through the scoped
  calc-output channel, sidestepping the first-wins corruption. Recorded for Phase 3.

**`extract_feature_refs` truncation cause (probe 1, non-gating).** Confirmed: for the 3-deep
chain, `extract_feature_refs` returns `['tf_coil']` — it reads operands/arguments (both just
`tf_coil`) and does not descend `target_feature.chaining_features`. So `references` cannot feed
the walk → D9's dedicated `reference_chain` capture (reading `chaining_features`) is the right
seam. Does not gate (D9 uses the in-repo chain walker).

**M2 — aggregation-walker interaction.** No aggregation (`sum(...)`) references either
`magnet_volume_total` or `blanket_volume_total` in the fixtures — none feed
`_build_aggregation_module`'s alias map. INV-E (single terminal leaf) keeps them eligible; the
INV-F assert at the walker entry is still added defensively (a surviving tentative must raise).

### Phase 1 Completion
**Completed:** 2026-07-05

**Changes Made:**
- `extraction/expression_utils.py` — new `extract_feature_chain_segments(expr_node)`: the
  corrected segment-list walk (absorbs DEVIATION D-A). Expands
  `target_feature.chaining_features` so 3-deep chains yield every segment; falls back to
  `.name` for 2-deep; recurses a nested FeatureChainExpression root. Returns `[]` for non-chain.
- `extraction/data_models.py` — added trailing `reference_chain: list[str] | None = None` to
  `ComputedAttributeData` + docstring.
- `extraction/computed_attribute_extractor.py` — populate `reference_chain =
  extract_feature_chain_segments(expr) or None` and pass it into the CAD.
- `snapshot/loader.py` — `reference_chain=d.get("reference_chain")` (additive-degrade).
- `snapshot/serializer.py` — no change needed (auto-included via `dataclasses.fields`; a
  `list[str]` serializes through `_serialize_value`). **No `SNAPSHOT_FORMAT_VERSION` bump.**
- `tests/unit/test_computed_attribute_extraction.py` — new `TestReferenceChainCapture`
  (4 tests): non-chain→empty; old-snapshot→None degrade; serialize/deserialize roundtrip;
  `@requires_license` live capture asserting **both** pin shapes
  (ife `[tf_coil,volume_calc,volume]`, catf `[tf_coil,volume]`).

**Deviations from Plan:** DEVIATION D-A absorbed here (see Probe Results). The design named
`extract_feature_chain_name` (operands[0] + `.target_feature.name`) as the segment source; that
truncates 3-deep chains to `[tf_coil]`. Introduced a dedicated corrected walker instead. Same
D9 seam and intent; strictly-more-correct. No architecture/invariant change.

**Gate:** suite **1936 passed / 4 skipped / 11 xfailed** (baseline 1932 + 4 new; field inert,
no existing test moved); ruff src/ **21**, mypy src/ **109** — both unchanged from baseline.
Live capture confirmed under the license.

### Phase 2 Completion
**Completed:** 2026-07-05

**Changes Made:**
- `extraction/data_models.py` — `EXPOSE_CHAIN_TENTATIVE` enum value + docstring (INV-F note).
- `extraction/computed_attribute_extractor.py` — new `_is_wellformed_multihop_chain`
  (INV-E gate: root is FeatureChainExpression ∧ `reference_chain` ≥ 2 ∧ `reference_chain[0]`
  ∉ calc_usage_names). `_classify_attribute_expression` gains a `reference_chain` param and
  returns tentative at the FORMULA drop point when the gate passes. Caller threads
  `reference_chain` (computed before classify).
- Tests: `TestMultiHopTentativeGate` (3 tests: tagged tentative; arithmetic-over-chain stays
  FORMULA; calc-rooted chain stays EXPOSE_PURE). Updated 6 existing classify callers +
  `test_all_five_values_defined` + `test_req_dm_02_enum_values` for the additive value.

**Note:** Landed together with Phase 3 (the plan's tight-pair requirement). Between them the
tentative leaks; the suite-green boundary is after Phase 3.

### Phase 3 Completion
**Completed:** 2026-07-05

**Changes Made:**
- `orchestration/output_registry_builder.py` — new `_resolve_reference_chain` (the transitive
  N-segment walk with the M5 `visited` cycle guard; direct `_scoped` hit for ife, alias-hop via
  the terminal attr's own `reference_chain` for catf — absorbs DEVIATION D-B, resolving through
  `_scoped` not the corrupted flat `_alias`). Phase 3b confirm loop: resolve → register alias +
  set EXPOSE_PURE in place (M6), else → FORMULA in place; runs after Phase 3, before Phase 4
  (INV-G). Terminal INV-F raise on any surviving tentative.
- `resolution/graph_builder.py` — INV-F `elif tentative: raise` at all three post-confirm
  readers (module build :253, aggregation alias map :274, attribute resolution map :834).
- `orchestration/pipeline_builder.py` — INV-G: second `_remove_formula_from_design_attrs`
  (Step 5.6, after confirm) + moved `group_deriver` to Step 5.7 (after removal). Step-4.5
  removal stays.
- **INV-F Phase-1c note:** output_registry_builder Phase 1c runs BEFORE the confirm pass, so a
  tentative there is legitimate (pre-confirm) and correctly skipped — it is not a leak. The
  registry-side INV-F guarantee is the confirm loop's terminal raise; the three graph_builder
  readers (post-confirm) carry the defensive raises. Faithful to INV-F's intent (no silent
  misuse of a tentative), placed where the invariant actually applies.

**Live verification:** both pins flip correctly — ife `radial_build.magnet_volume_total` →
EXPOSE_PURE, alias → `...tf_coil__volume_calc__volume` (direct); catf
`catf_radial_build.magnet_volume_total` → EXPOSE_PURE, alias → the RIGHT
`...tf_coil__volume_calc__volume` via the alias-hop (NOT the first-wins-corrupted plasma_region);
catf `blanket_volume_total` → its blanket channel. The 6 previously-xfailed CATFMFEValidation
tests now PASS (18 impls, q_eng=7.5, p_net=1300 — clean). Flipped `test_catf_mfe_aborts_with_v11`
→ `test_catf_mfe_wired_after_item10` (SC-1).

**Gate:** suite **1945 passed / 4 skipped / 5 xfailed** (baseline 1932/4/11 → +13 passed,
−6 xfailed as CATF un-xfails). NOTE: catf/ife COMMITTED SNAPSHOTS are still stale (FORMULA, no
`reference_chain`) — the live pins flip, the snapshot-based pin tests still see the old gap.
Phase 5 recapture makes them consistent (proven reproducible: recapture serializes EXPOSE_PURE +
`reference_chain`; on reload `cryo_load.magnet_volume` drops out of `fallback_entry_points`).

### Phase 4 Completion
**Status: VERIFIED + COMPLETE (2026-07-05, fresh session with execution).** The UNVERIFIED code
had one real bug, now fixed; all 5 wi014 tests pass, full gate holds (1946/4/5, ruff 21, mypy 109).

**BUG FOUND + FIXED (the 2 failing wi014 tests):** `_register_partdef_expose_scoped_aliases` passed
the CA's raw `owning_part_qualified_name` (`::` form, `toy_plant::'Toy Plant'`) straight into
`find_instance_paths_for_partdef`, but that helper indexes calc usages by their **sanitized** EQN
(`owning_part_def_qn = toy_plant__Toy_Plant`). The two never matched → `find_instance_paths_for_partdef`
returned `[]` → nothing registered → `_scoped_alias` stayed empty → both new tests failed on the
inertness gate. Fix: convert once at the boundary with `sanitize_qualified_name` (already imported +
used identically at `pipeline_builder.py:75`) before the instance-path lookup. Live-debugged per the
orchestrator's guidance (fresh extract, inspected total_cost in memory: EXPOSE_PURE ✓, on_partdef ✓,
ref_chain `['cost_calc','cost']` ✓, owning `toy_plant::'Toy Plant'` — the format mismatch was the
only gap). This was **not** a stale-snapshot issue and **not** a classification bug — the classifier
tags total_cost correctly; only the registration helper's QN format was wrong.

**Gate after fix:** suite **1946 passed / 4 skipped / 5 xfailed**; ruff src/ **21**; mypy src/ **109**
— all unchanged from the Phase-3 baseline except the +1 pass (the two rewritten wi014 shape-A tests
replace the one old malformed-refs deferral pin). Phase 4 is additive (INV-A held — no existing
baseline moved).

**(Prior UNVERIFIED note, retained for provenance):** CODE WRITTEN — UNVERIFIED (code execution was
gated in the implement session).**

**Changes Made:**
- `core/identifier_types.py` — `ScopedAliasKey = NewType("ScopedAliasKey", tuple[str, str])`
  (D7, stored unjoined — C3 no-collapse).
- `core/output_registry.py` — `_scoped_alias: dict[ScopedAliasKey, CanonicalChannel]` namespace
  + `register_scoped_alias` (raise-on-collision, unique by construction) + `scoped_alias_lookup`;
  `__len__` includes it.
- `orchestration/pipeline_builder.py` — new `_register_partdef_expose_scoped_aliases`: for each
  EXPOSE_PURE CA with `is_on_part_definition`, expand per instance via
  `find_instance_paths_for_partdef` and write `(instance_path, python_name) -> channel` (from
  `scoped_lookup(f"{inst}.{'.'.join(reference_chain)}")`). Called at new Step 5.55 (after
  registry, before backtracker). Part *usage* exposes (the two V11 pins) are
  `is_on_part_definition=False` → untouched.
- `snapshot/graph_rebuild.py` — same helper call in `build_classifier_inputs_from_snapshot`
  (local import) so `_scoped_alias` is populated on the OFFLINE path too.
- `analysis/dependency_backtracker.py` — #1 lookup in `_resolve_chain_dispatch` (new Step 1c):
  split `source_path` at the LAST dot -> `ScopedAliasKey((prefix, leaf))` -> `scoped_alias_lookup`,
  ordered after Step 1b, before the unscoped Step 2 (INV-A). Reuses `_is_self_reference`.
- `tests/conformance/test_wi014_toy.py` — REQ-CA-09 DISCHARGED: rewrote the malformed-refs
  deferral pin into `test_wi014_toy_shape_a_resolves_via_scoped_alias` (@requires_license:
  `("demo_plant","total_cost")` in `_scoped_alias` -> `...cost_calc__cost` channel) +
  `test_wi014_toy_scoped_alias_tuple_no_collapse` (C3). Updated module docstring.

**Decisions / deviations:**
- Did NOT drop the `not is_part_def` guard at `computed_attribute_extractor.py:245` (the design's
  literal instruction). Dropping it makes the extraction EXPOSE block emit a template ChannelAlias
  that Phase 3 of `build_output_registry` cannot register (no instance) -> warning noise. Iterating
  `computed_attrs` directly in the helper (the CA carries `is_on_part_definition`) is equivalent,
  cleaner, and avoids that noise. Same D7 outcome.
- **wi014 shape-A resolves LIVE only right now:** the committed wi014 snapshot predates Item 10
  (no `reference_chain`), so `#4` skips it offline; the wi014 tests are `@requires_license`.
  **Fold a wi014 recapture into Phase 5** so shape-A resolves offline too (add an offline
  inertness assertion then). wi014 is tiny; adding it to the recapture set is justified.
- The benign `_resolve_expose_pure` malformed-refs warning for the part-def EXPOSE still fires
  from the per-def resolution map (cannot pick an instance) — resolution now flows through
  #1/`_scoped_alias`, so it is unused noise, not a resolution failure.

**VERIFY (execution was blocked — run these):**
- `uv run --env-file ~/1cfe/agentic-mbse/.env pytest tests/conformance/test_wi014_toy.py -q`
  (the two new tests must pass; channel ends `cost_calc__cost`).
- Full gate `uv run pytest tests/` — expect prior green (1945 / 4 / 5) UNCHANGED (Phase 4 is
  additive; INV-A: #1 only adds hits where the ladder fell through). Any baseline churn = a
  consumer `source_path` now matches a `_scoped_alias` key that previously fell through -> INV-A
  regression, investigate.
- `uv run ruff check src/` (21) and `uv run mypy src/` (109) — watch the new tuple NewType.

### Phase 5 Completion (SUPERSEDED — see "Phase 5 COMPLETE" below)
**Status: ATTEMPTED then REVERTED — recapture surfaced non-attributable path-drift; handed
off as a reviewed-diff regen boundary.** (2026-07-05)

**What was verified (recapture works, pins flip offline):**
- Recaptured catf + ife via `capture_snapshot` (license live). Byte-identity hard gate PASSED:
  only the two enumerated snapshots changed (`git status` clean otherwise).
- Classification churn matched the Phase-0 M1 table EXACTLY — **3** `formula → expose_pure`
  flips (catf `magnet_volume_total`, catf `blanket_volume_total`, ife `magnet_volume_total`),
  no others. `reference_chain` added additively. M6 held: the serialized classification is the
  post-confirm EXPOSE_PURE (never a tentative — `capture_snapshot` runs the full
  `build_pipeline_context`, so the in-place mutation is what serializes).
- On reload the pins wire offline: `cryo_load.magnet_volume` drops out of
  `fallback_entry_points`; `EXPECTED_UNCOVERED` shrinks by exactly it.

**Why reverted (the blocker for a clean autonomous recapture):**
- The recapture diff is **polluted by environmental path-drift**: committed snapshots store
  `source_file` model-relative (`"library.sysml"`); the recapture produced repo-relative
  (`"tests/fixtures/ife_plant/library.sysml"`), plus a fresh `captured_at`. Net churn was
  ~955/751 (catf) and ~80/56 (ife) lines — far more than the 3 flips + `reference_chain` adds.
  This is the SAME drift class Item 9's audit flagged for ife_plant ("~90 lines of path
  canonicalization"). It makes the diff non-attributable, which the R3 reviewed-diff discipline
  forbids landing without review.
- Reverted both snapshots → restored the clean post-Phase-3 green boundary (suite 1945/4/5).

**HANDOFF for Phase 5 (do with diff review):**
1. Resolve the path-drift first — determine the canonical `source_file` relativization
   (model-relative vs repo-relative). Most committed snapshots appear model-relative; the
   recapture invocation/cwd or the serializer's relativization needs to match that so the diff
   is ONLY `reference_chain` + the 3 flips + `captured_at`. Check `snapshot/serializer.py`
   relativization vs `scripts/capture_extraction_snapshots.py` invocation.
2. Then recapture catf + ife, confirm byte-identity of the other ~15 snapshots.
3. Update the 5 entangled snapshot-based pin tests (they FLIP once snapshots carry the data):
   - `tests/conformance/test_ife_plant.py::test_cross_part_inputs_pinned_or_baseline` —
     EXPECTED_UNCOVERED shrinks by `cryo_load.magnet_volume` (shape-4 flip).
   - `tests/unit/test_uncovered_params.py::test_collector_pins_catf_mfe_dangle` — catf
     `[cryo_load.magnet_volume]` flips.
   - `test_reconcile_raises_v11_on_wired_gap`, `test_seeded_strict_generation_aborts_independently_of_catf_mfe`
     — catf no longer aborts on magnet_volume.
   - `test_fallback_entry_points_populated_in_memory_but_not_serialized` — **verify catf's
     RESIDUAL dangle** (`CATFMFEVacuum__catf_vacuum_pumping__pump_load__pumping_speed_total`):
     after the recapture the observed fallback set had this entry but `collect_uncovered_params`
     returned `[]` — reconcile whether the collector should still fire on the residual dangle
     (this may be an independent pre-existing catf gap, not an Item-10 regression — investigate
     before editing the assertion).
4. Assert `output_registry.alias_collision_count` as the residual-noise target (catf D5).

### Phase 5 COMPLETE (2026-07-05, fresh session with execution — supersedes the reverted attempt)

**Stage (a) is now fully SHIPPED and correct on BOTH the live and offline paths.** Gate:
**1947 passed / 4 skipped / 5 xfailed; ruff src/ 21; mypy src/ 109.**

**1. Path-drift resolved (it was never real).** The prior session's ~955-line drift came from
capturing with the wrong `output_dir`. Fix: capture per-fixture, writing into the fixture's OWN
directory (`capture_snapshot([model.resolve()], model/"extraction_snapshot.json")`), so the serializer
relativizes `source_file` model-relative — exactly the committed form. Verified diffs:
- ife_plant: 1 classification flip (`magnet_volume_total` FORMULA→EXPOSE_PURE) + `reference_chain` on 3
  attrs + `magnet_volume_total` appears as a design attr. **Matches the M1 table.**
- catf_mfe: 2 flips (`magnet_volume_total`, `blanket_volume_total`) + `reference_chain` on 46 attrs + 2
  design-attr appearances. **Matches the M1 table exactly** (46 ref_chain + 2 flips + 2 attrs = the whole diff).
- wi014_toy: `reference_chain` on `total_cost` + path CANONICALIZATION (committed was repo-relative;
  recapture → canonical: absolute design_attributes keys, model-relative source_file, `file:///` doc paths).
  **Accepted per the orchestrator ruling** (wi014 migrates; BACKLOG drift chore — see below).

**2. REAL BUG FOUND + FIXED: offline path mis-wired the catf pin (M6 vs D9 reconciliation).**
This is the significant find of the phase — the prior session's "wires offline" check was INSUFFICIENT
(it only verified `magnet_volume` left `fallback_entry_points`; it did NOT verify the channel identity).
- **Symptom:** LIVE resolves `cryo_load.magnet_volume` → correct `tf_coil__volume_calc__volume`; OFFLINE
  (snapshot rebuild) resolved → WRONG `plasma_region__volume_calc__volume` (the first-wins collision — bet
  B2's false-positive resolution, a lying sim).
- **Root cause:** M6 serializes the POST-confirm `EXPOSE_PURE` state, but the Phase-3b confirm walk — the
  ONLY code that resolves a multi-hop chain to its correct transitive channel — runs only on
  `EXPOSE_CHAIN_TENTATIVE` CAs. So on reload the pin arrives `EXPOSE_PURE`, the confirm walk skips it, and
  the naive Phase-3 path registers the collision. The live path never hits this (the CA is still tentative
  when Phase 3 runs, so Phase 3 skips it and 3b registers the correct channel first). This **contradicts D9's
  explicit intent** — `reference_chain` was captured precisely so the walk can run on the offline path.
- **Fix (`output_registry_builder.py`, top of `build_output_registry`):** reconstruct the pre-confirm
  tentative state for exactly the multi-hop candidates — an already-`EXPOSE_PURE` CA whose `reference_chain`
  is a part-rooted chain of ≥2 segments (`reference_chain[0]` not a calc-usage short name). Then the existing
  confirm pass reproduces the live registration order identically on both paths. Live CAs are still tentative
  here → no-op on the live path. This resolves the M6/D9 tension: M6's serialization stays EXPOSE_PURE (no
  reader ever sees a tentative — the confirm pass always finalizes before any reader; INV-F's terminal raise
  still guards), and D9's offline walk now actually runs.
- **DESIGN NOTE for the orchestrator:** this is a small design amendment (faithful to D9's stated intent, but
  it reconciles a real M6/D9 inconsistency the design did not anticipate). Verified: OFFLINE now == LIVE for
  BOTH pins (catf alias-terminal → tf_coil; ife direct-calc-output → tf_coil). Pinned by the regenerated catf
  baseline (the `cryo_load` module's `producer_channel` is now the tf_coil channel).
  - Discriminator gotcha (also fixed): `CalcUsageData.instance_name` is the short name in some fixtures but
    the full QN in others — used the last `__` segment of `qualified_name` for a robust short-name set.

**3. Entangled tests updated (11 failures → all green), each attributed to the pin flips:**
- `test_ife_plant.py::test_cross_part_inputs_pinned_or_baseline` — `EXPECTED_UNCOVERED` → empty set.
- `test_uncovered_params.py` — catf collector → `[]` (renamed `test_catf_mfe_dangle_wired_after_item10`);
  the two V11 strict-boundary proofs (`_reconcile` raise + `run_codegen` abort) and the
  fallback-in-memory test **RE-ANCHOR to `chain_override_probe`** — after Item 10 wired catf+ife, it is the
  ONLY committed full-graph-buildable fixture whose gap stays valueless-and-loud (A1). Verified by a corpus
  scan: no other full-pipeline fixture fires the collector. Module docstring rewritten.
- `test_backtracker.py` — catf counts: cross-package alias hits 18→19, MODULE_OUTPUT 30→31, Phase-4
  transitive aliases 44→46 (the 2 catf flips).
- `test_computed_attribute_extraction.py::test_old_snapshot_degrades_to_none` — re-anchored off catf (now
  carries `reference_chain`) to **solar_battery_model** (a non-recaptured baseline, genuine None-degrade case).
- `test_gen_json_templates.py` — dropped the catf non-vacuity guard (catf's None-default EP is now wired);
  `not violations` still runs.
- `test_pipeline_e2e.py::test_baseline_comparison_catf_mfe` — passes against the regenerated baseline.
- `test_wi014_toy.py` — added `test_wi014_toy_shape_a_resolves_offline_via_scoped_alias` (license-free), so
  stage (a)'s wi014 win is provable offline (the Phase-4-note offline inertness assertion).

**4. Residual catf dangle — OWNED.** catf's one remaining fallback EP,
`CATFMFEVacuum__catf_vacuum_pumping__pump_load__pumping_speed_total`, is `USAGE_LITERAL 200.0` — fell-through
but **VALUED**, so it is NOT a V11 violation and the collector correctly skips it. It is a benign pre-existing
catf gap (a valued literal), NOT an Item-10 regression. **BACKLOG owner: a follow-up catf-cleanup chore**
(record in BACKLOG alongside the wi014/catf path-canonicalization drift chore).

**5. BACKLOG drift chore:** wi014_toy migrated from repo-relative to canonical snapshot paths this phase
(catf/ife were already canonical). Record the wi014 path canonicalization as done; note catf_mfe snapshot
now also carries the reference_chain field.

### Phase 6 Completion
_[TO BE FILLED — stage (b): 3 companion fixtures authored + captured incomplete FIRST]_

### Phase 7 Completion
_[TO BE FILLED — escalation-guard outcome: did stage (b) fit one day?]_

### Phase 8 Completion
_[TO BE FILLED — WI-015 run-C lcoe number + match; gamma's moved channel name]_

---

**Status:** In Progress — **STAGE (a) COMPLETE and green (Phases 0–5).** Both V11 pins flip on the
LIVE *and* OFFLINE paths (channel identity verified: tf_coil, not the plasma_region collision); wi014
shape-A resolves live and offline; suite **1947 passed / 4 skipped / 5 xfailed; ruff src/ 21; mypy src/
109**; only the 4 enumerated fixtures changed. Phase 5 found+fixed a real offline-parity bug (M6/D9
reconciliation — see Phase 5 COMPLETE #2; a small design amendment for orchestrator review).
**Remaining: stage (b) — Phase 6 (3 companion fixtures, captured incomplete FIRST), Phase 7 (precedence
resolver, ONE-DAY escalation guard), Phase 8 (WI-015 anchor + docs/matrix/REQ IDs + release notes +
agentic-mbse MODELING_GUIDE list + CURRENT_WORK).**

### Deviations absorbed (all within design intent, no architecture change)
- **D-A (Phase 1):** the D9 segment walk must expand `target_feature.chaining_features` — the
  design's named `extract_feature_chain_name` (operands[0] + `.target_feature.name`) truncates
  3-deep chains to `[tf_coil]`. Fixed with a dedicated corrected walker.
- **D-B (Phase 3):** the confirm walk resolves the alias terminal through `_scoped` (re-substitute
  the terminal's own `reference_chain`), NOT the flat `_alias` (first-wins-corrupted to
  plasma_region). Sharpens the design's "follow one alias hop."
- **D-C (Phase 5, offline-parity — the significant find):** M6 serializes post-confirm EXPOSE_PURE, but
  the confirm walk gates on the tentative marker, so the offline path skipped the walk and mis-wired to the
  plasma_region collision. `build_output_registry` now reconstructs the tentative state for multi-hop
  part-rooted EXPOSE_PURE CAs before Phase 3, so the confirm pass runs identically live and offline. Faithful
  to D9's explicit "the walk runs on the offline path" intent; reconciles a real M6/D9 inconsistency.

### INV-F placement note (faithful interpretation)
The design lists Phase-1c (`output_registry_builder.py:120`) as an INV-F reader. Phase 1c runs
BEFORE the confirm pass (3b), so a tentative there is legitimate (pre-confirm) and correctly
skipped — not a leak. Enforcement is the confirm loop's terminal raise (registry-side) + the
three post-confirm graph_builder readers (:253/:274/:834) with `elif tentative: raise`. This
enforces INV-F's intent (no silent misuse) at the sites where it actually applies.
