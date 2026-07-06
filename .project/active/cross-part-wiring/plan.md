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
- [ ] **B7 — segment capture (the gating probe).** In a scratch script, load ife_plant + catf_mfe live and
  call the whole-chain walk `extract_feature_chain_name` (`expression_utils.py:250-280`) uses (`.operands[0]`
  + `.target_feature.name`). Confirm it yields `["tf_coil","volume_calc","volume"]` for ife_plant's
  `magnet_volume_total` (`subsystems.sysml:12`) and the alias chain for catf_mfe's `tf_coil.volume`
  (`radial_build.sysml:582`+`:458`). See `design.md#B7`.
- [ ] **B1 re-confirm — both pins reason-one.** Trace both pins against the *live* registry (not just
  source): each resolves to a single canonical channel, instance-independent. See `design.md#B1`.
- [ ] **`extract_feature_refs` truncation cause (probe 1, non-gating).** Read the agentic-mbse internal that
  truncates `tf_coil.volume_calc.volume` → `[tf_coil]`. Confirms D9's segment-list seam is the right one.
  Does **not** gate — D9 uses the in-repo chain walker, not `extract_feature_refs` (`design.md#D9`).
- [ ] **M1 expected-churn table.** Enumerate **every** computed attribute on catf_mfe **and** ife_plant that
  the new leaf-tag rule (INV-E: `reference_chain` ≥ 2 segments, single terminal leaf) would re-tag
  FORMULA→tentative. Record each: attr name, source line, has-cross-part-consumer?, expected final
  classification. Confirm `first_wall_area`/`magnet_surface_area` are single-hop (sibling calc) and
  **unaffected** (`design.md#potential-risks`, M1 bullet).
- [ ] **M2 aggregation-walker interaction.** Confirm which of the re-tagged exposes (if any) feed
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

- [ ] **Test file** (`tests/unit/test_computed_attribute_extractor.py` or a new red-first test) — the two
  stencils above, on real objects.
- [ ] `extraction/data_models.py:214-217` — add `reference_chain: list[str] | None = None` as a **trailing
  defaulted** dataclass field (safe; verified the default block sits at the end).
- [ ] `extraction/computed_attribute_extractor.py` — at live extraction, populate `reference_chain` with the
  segment-list analog of `extract_feature_chain_name` (`expression_utils.py:250-280` — return the list
  instead of joining).
- [ ] `snapshot/serializer.py` — auto-included (loops `dataclasses.fields`, `:171`); confirm no field
  exclusion needed.
- [ ] `snapshot/loader.py:467-485` — add `reference_chain=d.get("reference_chain")` (`:474` region).
- [ ] **Do NOT bump `SNAPSHOT_FORMAT_VERSION`** (`snapshot/__init__.py`) — see M6.

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

- [ ] Add `EXPOSE_CHAIN_TENTATIVE` to `ComputedAttributeClassification`
  (`extraction/data_models.py`, enum).
- [ ] `extraction/computed_attribute_extractor.py:104-109` — when the root is a pure `FeatureChainExpression`
  (`:104-106`) AND `reference_chain` satisfies INV-E, return `EXPOSE_CHAIN_TENTATIVE` instead of dropping to
  FORMULA. Do **not** test terminal-is-an-output.
- [ ] Red-first tests above + a two-terminal-chain case that **stays FORMULA** (never tagged — the INV-E
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

- [ ] **Confirm pass (Phase 3b)** in `build_output_registry` (`resolution/output_registry_builder.py`) —
  runs **after** Phase 3 single-hop aliases, **before** Phase 4. Per tentative: walk `reference_chain`
  left-to-right building an instance path from waypoint segments; at the terminal look up a scoped channel
  (direct — ife_plant) or an alias, following one alias hop to its channel (catf_mfe); carry the M5 `_visited`
  guard. Resolve → register alias + set `EXPOSE_PURE` **in place**; else → set `FORMULA` in place.
- [ ] **INV-F asserts** — add `else: raise` on a surviving `EXPOSE_CHAIN_TENTATIVE` at all four readers:
  `output_registry_builder.py:120` (Phase 1c), `graph_builder.py:253` (module build), `:274` (aggregation
  alias map), `:834` (`_build_attribute_resolution_map`).
- [ ] **INV-G ordering** in `orchestration/pipeline_builder.py` — a **second** `_remove_formula_from_design_attrs`
  pass at Step 5.6 (twin of the Step-4.5 removal at `:133`); move `group_deriver` construction from `:528`
  to Step 5.7, **after** that removal, so it consumes final `design_attrs`. The Step-4.5 removal stays
  (genuine FORMULAs).
- [ ] Red-first tests above; plus an aggregation-fixture regression (M2 guard at the walker entry).
- [ ] **M6 in-place constraint:** the confirm pass must mutate the **shared** `computed_attrs` objects in
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

- [ ] `core/identifier_types.py` — `ScopedAliasKey = NewType("ScopedAliasKey", tuple[str, str])`.
- [ ] `core/output_registry.py` — a dedicated `_scoped_alias: dict[ScopedAliasKey, ...]` namespace, distinct
  from the flat `_alias`; register/lookup methods storing the tuple **unjoined**.
- [ ] `extraction/computed_attribute_extractor.py:245` — drop the `not is_part_def` guard; emit a template
  expose alias for part-def EXPOSE.
- [ ] `orchestration/pipeline_builder.py` — new helper mirroring `_build_chain_aliases` (`:338-391`): expand
  the part-def expose per instance path, writing `(instance_path, exposed_leaf)` into `_scoped_alias`
  (Phase-3 alias walk).
- [ ] `analysis/dependency_backtracker.py:592-615` — insert the structured `_scoped_alias` lookup step in
  `_resolve_chain_dispatch`, split `source_path` at the last dot → `ScopedAliasKey((prefix, leaf))`, ordered
  **after** Step 1b, **before** the unscoped Step 2 (INV-A). Reuse `_is_self_reference` unchanged.
- [ ] Red-first: inertness gate, shape-A resolution, tuple-key no-collapse. Flip wi014_toy's REQ-CA-09
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

- [ ] **Recapture (license-gated)** catf_mfe + ife_plant extraction snapshots via `scripts/capture_*.py`
  (never hand-edited, R3) — they now carry `reference_chain`. The ~15 non-multi-hop snapshots load unchanged
  (no version bump).
- [ ] Regenerate the catf_mfe + ife_plant pipeline baselines; each diff attributed line-by-line against the
  Phase-0 M1 churn table.
- [ ] Assert **ife_plant** `EXPECTED_UNCOVERED` in `test_ife_plant.py` shrinks by `cryo_load.magnet_volume`
  (direct-calc-output shape).
- [ ] Assert **catf_mfe** `[cryo_load.magnet_volume]` flips via the alias-terminal hop, clean strict
  generation; `output_registry.alias_collision_count` is the assertion target for residual noise (reviewed,
  not silent).
- [ ] Confirm the three non-flipping baselines (incl. solar_battery) are **byte-identical**.

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

### Probe Results (fill in Phase 0)
_[TO BE FILLED — B7 segments for both pins; B1 live re-confirm; truncation cause; the M1 expected-churn
table (attr, line, consumer?, final classification); M2 walker interaction. Record the two hard-stop
outcomes explicitly.]_

### Phase 1 Completion
_[TO BE FILLED — actual changes, issues, deviations]_

### Phase 2 Completion
_[TO BE FILLED]_

### Phase 3 Completion
_[TO BE FILLED]_

### Phase 4 Completion
_[TO BE FILLED]_

### Phase 5 Completion
_[TO BE FILLED — the recapture diff vs the M1 table]_

### Phase 6 Completion
_[TO BE FILLED]_

### Phase 7 Completion
_[TO BE FILLED — escalation-guard outcome: did stage (b) fit one day?]_

### Phase 8 Completion
_[TO BE FILLED — WI-015 run-C lcoe number + match; gamma's moved channel name]_

---

**Status:** Draft → In Progress → Complete
