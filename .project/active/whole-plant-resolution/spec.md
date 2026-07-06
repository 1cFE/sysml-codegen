# Spec: Whole-Plant Cross-Part Value Resolution (PIPELINE-TRUTH Item 2)

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-07-06
**Complexity:** HIGH
**Branch:** pipeline-truth-epic

---

## Problem

`generate --models ~/1cfe/fusion-tea/models` aborts at V11 on 10 plain
subsystem-attribute → plant-calc-input references. A plant calc (`lcoe_calc`,
`recirc_calc`) binds each input to an attribute on a subsystem part cross-part
(`driver.efficiency`, `chamber.blanket_energy_multiple`,
`target_factory.cost_per_target`, …). The referenced attributes have their values in
the model — as subtype-def literals, as bare-override-block literals, or as plain
user-fill attributes — but the current pipeline cannot carry those values across the
part boundary to the consumer calc. Each reference falls to a valueless entry point
that a module input still wires, so the generated JSON never mints the key while the
pipeline references it — a guaranteed `KeyError` at TEAx load. V11 catches it and
aborts the whole emission.

This is the last thing standing between fusion-tea and a generated-package-is-the-truth
run. UPSTREAM-FINDINGS Item 10 wired the calc-output cross-part shapes (the `gamma →
lcoe` edge) but explicitly left these 10 plain-value references as pre-existing plant
gaps (RN-10 "the full fusion-tea YAML does NOT yet emit"). A 10-value bridge proved the
semantics reproduce anchor C bit-exactly, so the values are known-correct and the fix is
measured.

Item 1 landed the in-repo before-state. The headline fixture `plant_values` reproduces
all three value-provision mechanisms and trips V11 with exactly three offenders on
module `plantvaluesdesign__plant__cost_calc`
(`test_plant_values.py::test_plant_values_trips_v11_all_three_mechanisms`):

- **(a)** `driver_efficiency` — a subtype-def literal `:>> efficiency = 0.35` reached
  cross-part through a usage-level retype (`part :>> driver : 'Hif Driver'`).
- **(b)** `target_cost` — a bare no-retype override block `part :>> target_factory {
  :>> cost_per_target = 10.0; }` (a shape zero prior fixtures contained).
- **(c)** `chamber_cost` — a plain one-hop cross-part attribute `chamber.cost_per_unit`,
  genuinely valueless (no model literal; user supplies it).

The extended `spec_chain_twolevel` fixture carries the value-carrying cross-part shape
plus the fan-out case (one `scale` attribute → two `ScaleCalc` consumers). This item
flips the before-state: `plant_values` generates clean, and the mechanism it lands wires
fusion-tea's 10 references too.

## Success Criteria

- [ ] **SC-1 (the headline flip)**: `plant_values` generates clean — zero V11 offenders.
  The three-offender pin in `test_plant_values.py` is flipped to empty **as a
  behavior-observing pin**, not deleted. The resolved values/edges match the
  hand-computed expectations, anchored independently of the resolver: with (a) `0.35` and
  (b) `10.0` carried from the model and (c) `chamber_cost` supplied as `7.0` by input JSON,
  the plant calc computes `plant_cost = (10 + 7) / 0.35 = 48.571…`. The `48.571` anchor is
  hand-derived (recorded in Item 1's provenance), never read back from the resolver output.
- [ ] **SC-2 (precedence holds under the mechanism)**: The redefinition precedence chain
  — usage override > specialized-def `:>>` > base def (REQ-VBR-10) — resolves identically
  whichever mechanism lands, pinned by a fixture-anchored test that fails if any tier is
  skipped or reordered. The existing `spec_chain_twolevel`/`spec_chain_channel`
  precedence pins stay green (the calc-output chain still wires).
- [ ] **SC-3 (SC-B in-repo gate)**: The extended `spec_chain_twolevel` computes its
  lcoe-analog through the **generated package executed on the teax executor path** (not
  just graph-level inspection) within tolerance of the hand-computed value. This is the
  in-repo half of the epic's SC-B.
- [ ] **SC-4 (license-free acceptance proxy)**: `generate --from-snapshot` on the
  committed fusion-tea snapshot emits the full YAML package with zero V11 offenders — the
  license-free stand-in for the fusion-tea acceptance run (which is Item 3's).
- [ ] **SC-5 (baseline discipline)**: The four existing plant-idiom / cross-part baselines
  are byte-identical or every change is justified as a reviewed diff; `plant_values`'s
  graph baseline regenerates to the wired/pre-filled zero-offender state via the capture
  scripts. The V11 raise-proof is preserved by deliberately re-anchoring it to a
  still-uncovered fixture (as UPSTREAM-FINDINGS Item 9 did) — V11 must still be able to
  fire after this item clears the plant_values offenders.
- [ ] **SC-6 (docs + agentic-mbse impact)**: Reference docs 11/12/25 and
  modeling-assumptions §5 record the newly supported value shapes (R1/R4 step 4); the
  agentic-mbse impact for the shapes is recorded for Item 9 (R2).

## Known Requirements

### The mechanism (decided at design, not here)

- **[HARD]** The mechanism resolves all three value-provision shapes from `plant_values`:
  subtype-def literal through usage-level retype (a); bare no-retype `part :>>` override
  block (b); plain one-hop cross-part attribute (c). Mechanism (c) is genuinely valueless
  — the fix makes its reference resolve to the real subsystem-attribute entry point (a
  legitimate user-fill key the JSON mints), so it leaves `fallback_entry_points` and stops
  tripping V11 even though it stays user-fill. Mechanisms (a) and (b) carry a real model
  literal to the consumer, so their entry points stop being valueless. Both outcomes clear
  V11; the design must cover both (they are not the same operation).
- **[HARD]** Whichever mechanism lands (value propagation or channel wiring — see Open
  Questions), the REQ-VBR-10 precedence chain holds identically: usage override beats
  specialized-def `:>>` beats base def. The precedence is the invariant; the mechanism is
  the implementation. This is not deferrable — it is a correctness contract on the fix.
- **[HARD]** The `gamma → lcoe` calc-output cross-part edge already wired by UPSTREAM-FINDINGS
  Item 10 stays wired (the twolevel chain still resolves). This item adds plain-value
  resolution; it does not regress calc-output resolution.

### Tests (R1 addition — fires-on-shape + silent-on-clean, independently anchored)

- **[HARD]** The headline after-state pin asserts the resolved offender set is empty AND
  the three inputs carry their expected sources/values (a specific-property pin per
  mechanism, in the `test_plant_values.py` style), not a bare `snapshot == committed`
  byte-equality (the epic-R1-banned REQ-EXT-09 anti-pattern). The `48.571` value is a
  hand-transcribed literal in the test, not computed by the code under test.
- **[HARD]** A precedence test on a fixture that exercises all three tiers (usage override,
  specialized-def `:>>`, base def) with distinct values at each tier, so a
  precedence-order regression fails it. Reuse or extend an Item-1 fixture rather than
  inventing a shape.
- **[HARD]** The SC-B executor test runs the generated `spec_chain_twolevel` package
  through the teax executor and asserts the computed lcoe-analog within tolerance
  (`rel 1e-6` or the fixture's documented tolerance) of the hand-computed value — proving
  the value is consumed through execution, not merely present in the graph.
- **[HARD]** The V11 raise-proof: after `plant_values` clears, a test still proves V11
  fires — re-anchored to a fixture that remains uncovered (a deliberately-authored or
  existing still-valueless-wired shape), so the diagnostic is not silently disarmed.

### Baselines and capture

- **[HARD]** `plant_values` baselines (`computation_graph.json`, `registry_init.py`, and
  the full generation output set the flip now produces) regenerate via `scripts/capture_*.py`
  with the `--fixtures` name-filter (D7 from Item 1), as reviewed diffs. The four existing
  cross-part baselines (`catf_mfe`, `ife_plant`, `spec_chain_channel`, `spec_chain_twolevel`)
  stay byte-identical unless a change is deliberately justified as flowing from this
  mechanism (e.g. a fan-out collapse that reshapes a channel).
- **[HARD]** The committed fusion-tea snapshot's from-snapshot emission is the SC-4 gate;
  it is exercised in-repo (license-free), distinct from the live fusion-tea acceptance run
  that Item 3 owns.

### Sequencing (snapshot format v2)

- **[HARD]** This item's implement runs **after Item 4's**. Item 4 bumps the snapshot
  format version (currently `snapshot_format_version: 1` on the committed fixtures) and
  re-captures every snapshot — including `plant_values`, `spec_chain_twolevel`, and the
  fusion-tea snapshot — on format v2 (it serializes constraints). Item 2's before-pins,
  after-pins, and regenerated baselines are all authored against **format v2**. The spec
  writes no baseline bytes; it names the fixtures and the observed properties, and the
  plan captures against whatever format is live when Item 2 implements.

### Docs and cross-repo (R1/R2/R4)

- **[HARD]** Docs 11 (backtracker), 12 (virtual-binding-rewrite), 25 (hierarchy-resolver),
  and modeling-assumptions §5 are updated in the same change to describe the plain-value
  cross-part resolution — including whichever mechanism lands and the precedence it honors
  (R4 step 4: close the loop in docs). The verification-matrix rows the mechanism touches
  (REQ-VBR-10/11, REQ-RES-08, any new REQ) move with the code.
- **[HARD]** The agentic-mbse impact — the newly supported whole-plant value shapes for
  MODELING_GUIDE — is recorded for Item 9 as a concrete block (per Item 1's precedent), not
  a vague "record it."

## Non-Goals

- **fusion-tea repo changes** (Item 3): deleting `hif_driver_instance`, retiring the
  two-pass gamma feedback / `sanitize_names.py`, re-anchoring channel EQNs, the
  perturbed-input rerun, and the live acceptance run. This item's fusion-tea gate is the
  license-free from-snapshot proxy (SC-4) only.
- **Supertype-chain template inheritance for *plain* usages** — still deferred to the MFE
  epic (D6 confirmed the 10 offenders don't touch it).
- **Non-literal RHS in the bare `part :>>` block** (CHAIN/EXPRESSION overrides beyond what
  Item 10 already wired) — out unless design shows it falls out free from the chosen
  mechanism.
- **Constraint resolution/execution** — the `plant_values` assert constraint is Item 4's
  substrate (visibility) and a deferred epic's (execution); this item does not resolve it.
- **The teax OutputRouter/WriteHandler harness** (T-1/T-2) — stays fusion-tea-side by
  design.

## Open Questions / Deferred to design

### The mechanism decision — value propagation vs channel wiring (design owns this)

The epic assigns this decision to design, not spec (R4 step 1: read the intent, then
decide). The spec's job is to state the decision inputs precisely so design decides with
full information. The two candidates and what each costs:

**Value propagation ("value-fill").** Carry each literal into the consumer entry point's
`default_value`, so the plant-calc input becomes a pre-filled DESIGN_ATTRIBUTE-style entry
point (the shape the 10-value bridge validated). What it costs:

- The 10 params **stay** in the entry-point groups as JSON keys. fusion-tea's harness
  contract (schema field names, JSON key set) is preserved; Item 3 re-anchors values but
  not keys.
- **Fan-out stays N independent keys**: one attribute feeding 3 consumers mints 3 separate
  entry points with the same value, not one shared channel. The extended `spec_chain_twolevel`
  fan-out (`scale` → `scale_a`/`scale_b`) currently collapses to one shared entry point
  (`test_fanout_collapses_to_one_producer_channel`); value-fill must preserve that collapse
  or justify divergence.
- **Diverges on deep re-redefinition**: a value re-redefined in a deeper specialization
  than the one read is not followed — value-fill snapshots the literal it can see, so a
  5-deep chain that overrides again below the read point diverges in value. (Out of scope
  per Non-Goals, but the mechanism must not silently produce a wrong value — loud is
  acceptable, silent-wrong is not.)

**Channel wiring.** Treat the subsystem attribute as a source and wire the consumer input
to it (the shape `_rewrite_specialized_chain` uses for calc-output chains). What it costs:

- The 10 params **leave** the entry-point groups (become module_output or shared-source
  channels). Schemas and JSON key sets change; fusion-tea's harness **re-anchors** on the
  new keys, and the report's `run_anchors_bridged.py` breaks (it hard-codes the old keys
  and an exactly-10 guard). Item 3 absorbs the re-anchor either way — but wiring makes it
  mandatory, value-fill makes it optional.
- **Fan-out collapses to one shared channel** — the "right" data shape (one source, N
  readers), matching the existing twolevel fan-out behavior.
- Mechanism (c) is genuinely valueless, so wiring it means wiring to a **user-fill source**
  that carries no value — closer to reference-resolution than to a producer edge. Design
  must decide whether (c) is the same operation as (a)/(b) or a sibling.

**The invariant that holds either way:** REQ-VBR-10 precedence (usage override >
specialized-def `:>>` > base def). This is a `[HARD]` requirement above, not a deferred
question — it constrains whichever mechanism design picks.

**Decision-input provenance:** discovery register §"Anchors REPRODUCED" (the bridge
validates value-propagation semantics only; wiring breaks the bridge; fan-out untouched by
the bridge; feedback-edge ordering un-tripped); RN-10 (the residual 10-offender gap and
the calc-output edge already wired); doc 12 (the three-tier merge and where precedence
lives).

### Split decision (design owns this)

The epic's risk table flags Item 2 may exceed 2 days and names the split line: **mechanism
(the three value shapes) vs fan-out/edge-cases**. Design decides whether to split the
fan-out collapse and the deeper-chain edge handling into a follow-on, landing the mechanism
+ headline flip first. Item 1's fixtures pin the value independently, so a split loses no
coverage.

### Smaller design calls

- Whether mechanism (c)'s reference-resolution reuses the (a)/(b) path or is a distinct
  step (it carries no value, so it may be resolve-the-reference rather than carry-the-value).
- Which existing fixture anchors the three-tier precedence test, or whether a small
  extension is needed.
- Where the V11 raise-proof re-anchors after `plant_values` clears (which still-uncovered
  fixture becomes the new fires-on-shape substrate).

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_pipeline_truth.md` (Item 2; R1–R4; SC-A/SC-B; Risks rows
  on the mechanism decision and the 2-day limit)
- **Required Reading:** discovery register §D6 + §"Anchors REPRODUCED"
  (`.project/research/20260706_pipeline-truth-discovery.md`); fusion-tea report §"The
  residual gap" (`~/1cfe/fusion-tea/work/active/20260706_upstream-fix-verification/report.md`
  — outside the repo sandbox; RN-10 carries its residual-gap essence);
  `docs/architecture/reference/11-analysis-backtracker.md`,
  `reference/12-virtual-binding-rewrite.md` (the epic cites it as `24-binding-resolution.md`
  — the binding-rewrite/precedence content lives in doc 12; `24-dual-resolution-architecture.md`
  is the resolver-architecture doc), `reference/07-graph-assembly.md` (the epic cites it as
  `07-graph-builder.md` — renamed); RN-10 (`.project/active/cross-part-wiring/release-notes.md`);
  memory notes `cross-part-binding-v11-fallthrough`, `multihop-expose-offline-parity`,
  `plant-idiom-fixtures`.
- **Before-state (Item 1):** `tests/fixtures/plant_values/` (3-offender headline);
  `tests/fixtures/spec_chain_twolevel/` (value-carrying cross-part + fan-out);
  `.project/active/plant-value-fixtures/spec.md` §"agentic-mbse impact".
- **Research:** `.project/research/20260706_pipeline-truth-discovery.md`
- **Downstream:** Item 3 (`fusiontea-acceptance` — re-anchors and retires whichever
  mechanism lands); Item 4 (bumps snapshot format v2 before this item implements); Item 9
  (agentic-mbse impact accumulation).
- **Design:** `.project/active/whole-plant-resolution/design.md` (to be created — owns the
  mechanism decision).

---

**Next Steps:** After approval, proceed to `/_my_design`. Design owns the mechanism
decision (value propagation vs channel wiring) and the split decision, with the decision
inputs above and the discovery §"Anchors" attack as primary input.
