# Spec: Whole-Plant Cross-Part Value Resolution (PIPELINE-TRUTH Item 2)

**Status:** Draft (revised after spec-review — see Resolutions)
**Owner:** Reid W
**Created:** 2026-07-06
**Complexity:** HIGH
**Branch:** pipeline-truth-epic

---

## Problem

`generate --models ~/1cfe/fusion-tea/models` aborts at V11 on 10 subsystem-attribute →
plant-calc-input references. A plant calc (`lcoe_calc`, `recirc_calc`) binds each input to
an attribute the value for which lives in the model — as a subtype-def literal, a
bare-override-block literal, a usage-level dotted-override literal, or an inherited
attribute the def redefines — but the current pipeline cannot carry that value to the
consumer calc. Each reference falls to a valueless entry point that a module input still
wires, so the generated JSON never mints the key while the pipeline references it — a
guaranteed `KeyError` at TEAx load. V11 catches it and aborts the whole emission.

This is the last thing standing between fusion-tea and a generated-package-is-the-truth
run. UPSTREAM-FINDINGS Item 10 wired the calc-output cross-part shapes (the `gamma → lcoe`
edge) but left these plain-value references as pre-existing plant gaps (RN-10 "the full
fusion-tea YAML does NOT yet emit"). A 10-value bridge proved the semantics reproduce
anchor C bit-exactly, so the values are known-correct and the fix is measured.

### The value shapes (the taxonomy, stated once)

There are **four** value-provision shapes, three cross-part and one in-part. Item 1's
fixtures pin each as substrate:

- **(a) subtype-def literal via usage-level retype** — `:>> efficiency = 0.35` on a
  subtype def, reached cross-part through `part :>> driver : 'Hif Driver'`.
- **(b) bare no-retype override block** — `part :>> target_factory { :>> cost_per_target =
  10.0; }` (a shape zero prior fixtures contained).
- **(c) plain one-hop cross-part attribute with a usage-level dotted override** —
  `chamber.cost_per_unit`, valued by `:>> chamber.cost_per_unit = 7.0` on the plant
  instance (distinct from (b)'s override *block* — a dotted override on the usage).
- **(d) in-part consumption of an inherited attr the def redefines** — a calc usage binds
  `in flow_rate = throughput`, an inherited attribute, and the same def redefines `:>>
  throughput = 8.0` below the binding. The value and the consumer are in *one* part; no
  boundary is crossed. This is the fusion-tea offender-#9/#10 shape (`hif_driver.sysml:74`
  bound, `:81` redefined). Item 1 pins it as `'Flow Sub'` in `plant_value_shapes`
  (`test_plant_value_shapes.py`), observed **DEGRADED** — a valueless EP.

The headline `plant_values` fixture carries (a)/(b)/(c) and trips V11 with exactly three
offenders on module `plantvaluesdesign__plant__cost_calc`
(`test_plant_values.py::test_plant_values_trips_v11_all_three_mechanisms`). Shape (d) lives
in `plant_value_shapes` `'Flow Sub'`. The extended `spec_chain_twolevel` carries the
value-carrying cross-part chain plus a fan-out case. This item flips the before-state:
`plant_values` and `'Flow Sub'` resolve, and the mechanism wires fusion-tea's references.

### Offender arithmetic (the load-bearing acceptance count)

The discovery register's tidy `(a) 5 + (b) 4 + (c) 1 = 10` cross-part decomposition is
**superseded** by the orchestrator's live read of the fusion-tea residual-gap table. The
authoritative breakdown of the 10 committed-snapshot offenders:

| Offenders | Count | Shape | Mechanism | Cleared by |
|-----------|-------|-------|-----------|-----------|
| Cross-part on `lcoe_calc`/`recirc_calc` | 8 | (a)/(b)/(c) | a/b/c | **Item 2** |
| In-part on the canonical part (#9) | 1 | (d) inherited-attr-redefine | **d** | **Item 2** |
| In-part on the workaround instance (#10) | 1 | (d), same shape on `hif_driver_instance` | **d** | **Item 2** (resolves) |
| **Total** | **10** | | | **all → true zero** |

With shape (d) in scope, **all 10 resolve under Item 2** and the committed fusion-tea
snapshot reaches **true zero** offenders. Offender #10 exists only because the workaround
instance `hif_driver_instance` is still present in the committed snapshot — but it is the
same (d) shape as #9, so mechanism (d) resolves it too; it does not trip V11 once (d)
lands. **Deleting** the instance is still Item 3's separate cleanup job, but it is *not*
required to hit zero offenders. This makes SC-4/SC-A's "zero offenders on the committed
snapshot" a well-defined, achievable bar for this item.

## Success Criteria

- [ ] **SC-1 (the headline flip)**: `plant_values` generates clean — zero V11 offenders.
  The three-offender pin in `test_plant_values.py` flips to empty **as a behavior-observing
  pin** (not deleted). The resolved values/edges match the hand-computed expectations,
  anchored independently of the resolver: with (a) `0.35`, (b) `10.0`, and (c) `7.0` all
  carried from the model, the plant calc computes `plant_cost = (10 + 7) / 0.35 =
  48.571…`. The `48.571` anchor is hand-derived (recorded in Item 1's provenance), never
  read back from the resolver output. **Anchor provenance (F1/F2 cure):** all three inputs
  are now model literals — the Item-1 audit F1/F2 cure (in flight on `plant_values/design.sysml`)
  restores (c)'s literal via `:>> chamber.cost_per_unit = 7.0`, so (c) is a *carried value*
  like (a)/(b), not a test-supplied user-fill. The authoritative value is the cure commit's:
  if the cure lands a chamber literal other than `7.0`, this anchor follows it. This spec
  cites `48.571` on the in-flight cure; the plan pulls the final number from the landed cure.
- [ ] **SC-1d (the in-part flip)**: `'Flow Sub'` in `plant_value_shapes` resolves — its
  `flow_calc.flow_rate` input carries `8.0` (from the `:>> throughput = 8.0` redefinition),
  and the DEGRADED valueless-EP pin (`test_plant_value_shapes.py`) flips to the resolved
  value as a behavior-observing pin. This is the in-part shape (d); it is the in-repo proxy
  for fusion-tea offenders #9/#10.
- [ ] **SC-2 (precedence holds)**: The plain-value redefinition precedence — usage override
  > specialized-def `:>>` > base def — resolves correctly, pinned by a fixture that
  exercises all three tiers with **distinct** values at each tier (including the
  usage-override tier, currently unexercised in any fixture — design authors it). A
  tier-skip or tier-reorder regression fails the test. The existing calc-output precedence
  pins (`test_spec_chain_channel.py`, `test_spec_chain_twolevel.py`) stay green.
- [ ] **SC-3 (SC-B in-repo gate, executed)**: The extended `spec_chain_twolevel` computes
  its lcoe-analog by **executing the generated package** (importing the generated modules,
  running them in pipeline-YAML dependency order, feeding the emitted JSON inputs) within
  `rel 1e-6` of the hand-computed value. Graph-level inspection does **not** satisfy this —
  the value must be produced by execution. Standing up the minimal in-repo runner is a
  deliverable of this item (see Known Requirements).
- [ ] **SC-4 (license-free acceptance proxy)**: `generate --from-snapshot` on the committed
  fusion-tea snapshot emits the full YAML package with **true zero** V11 offenders — all 10
  cleared by mechanisms (a)/(b)/(c)/(d) per the offender-arithmetic table. This is the
  license-free stand-in for the fusion-tea acceptance run (Item 3's live gate).
- [ ] **SC-5 (baseline discipline + V11 raise-proof)**: The four existing plant-idiom /
  cross-part baselines are byte-identical or every change is a justified reviewed diff;
  `plant_values` and `'Flow Sub'` baselines regenerate to the resolved zero-offender state
  via the capture scripts. The V11 raise-proof is preserved by re-anchoring it to a
  **genuinely-deferred** shape (NOT `'Flow Sub'` — this item dissolves it; see SC-1d), so
  V11 can still fire after this item clears the plant offenders.
- [ ] **SC-6 (docs + agentic-mbse impact)**: Reference docs 11/12/25 and
  modeling-assumptions §5 record the four supported value shapes and the plain-value
  precedence REQ (R4 step 4); the newly supported shapes are recorded for Item 9's
  agentic-mbse impact list as a concrete block (R2).

## Known Requirements

### The mechanism (decided at design, not here)

- **[HARD]** The mechanism resolves **all four** value shapes: (a) subtype-def literal via
  usage-level retype; (b) bare no-retype `part :>>` override block; (c) plain one-hop
  cross-part attribute with usage-level dotted override; and **(d) in-part consumption of
  an inherited attr the def redefines** (offenders #9/#10, anchored on `'Flow Sub'`). Shape
  (d) is a **fourth [HARD] target**, not optional: the epic CSF requires zero V11 offenders
  on the fusion-tea generate, and #9/#10 are (d). All four clear V11 either by carrying a
  value into the entry point ((a)/(b)/(c)/(d) all carry a model literal) or, where a
  reference is genuinely valueless, by resolving it to a real user-fill key that leaves
  `fallback_entry_points`.
- **[HARD]** Whichever mechanism lands (value propagation or channel wiring — see Open
  Questions), the plain-value precedence contract holds identically: **usage override >
  specialized-def `:>>` > base def**. This is a **new requirement this item defines for
  plain values** — it is NOT REQ-VBR-10 (which doc 12 scopes to `:>> attr = calc.output`
  CHAIN rewrites and the self-named rescue, the calc-output shape Item 10 already wired).
  Carrying a plain literal `:>> efficiency = 0.35` is a *different* operation than the
  VBR-10 chain rewrite; overloading VBR-10 would misdescribe both. Design assigns the new
  REQ its ID and matrix row; it does not edit REQ-VBR-10's scope. (If design finds the
  plain-value path genuinely IS a VBR-10 extension, it says so explicitly and edits the REQ
  text + matrix row — the ban is on silent overloading, not on a reasoned extension.)
- **[HARD]** The `gamma → lcoe` calc-output cross-part edge (UPSTREAM-FINDINGS Item 10)
  stays wired; the twolevel chain still resolves. This item adds plain-value resolution
  without regressing calc-output resolution.
- **[HARD]** Fan-out collapses by **shared source-attribute QN**, for **differently-named**
  consumers too. Fusion-tea's real fan-out renames per consumer (`driver.efficiency` →
  `lcoe_calc.driver_efficiency` AND `recirc_calc.eta`; `chamber.blanket_energy_multiple` →
  two differently-named consumers). Both readers reference the same source QN, so both
  collapse onto one shared entry point / channel regardless of the differing input names.
  The existing in-repo fan-out fixture (`spec_chain_twolevel`, `scale` → `s`/`s`) covers
  only the *same*-input-name case. This item adds a **renamed-consumer leg** to the fixture
  expectations — a small Item-1-style capture rider it owns at implement: extend
  `spec_chain_twolevel` (or a sibling) with one source attribute feeding two
  differently-named inputs, and pin that both collapse to the one shared source EP/channel.

### The executor-path runner (SC-3 deliverable)

- **[HARD]** No executor test harness exists in the repo today (only baseline
  `registry_init.py` files, no runner). This item stands up a **minimal in-repo pipeline
  runner** as a deliverable: it imports the generated modules, executes them in
  pipeline-YAML dependency (execution) order, feeds the emitted JSON inputs, and returns
  the computed outputs. It is written to be **reusable by Item 3's acceptance run** (the
  fusion-tea live gate runs the same runner). If teax is importable in-repo the runner may
  drive the generated `registry_init` registry through it; if not, it is a fixture-local
  driver over the generated modules. SC-3 asserts against the runner's output, not the
  graph.

### Tests (R1 addition — fires-on-shape + silent-on-clean, independently anchored)

- **[HARD]** The headline after-state pins assert the resolved offender set is empty AND
  the three inputs carry their expected sources/values (a specific-property pin per
  mechanism, `test_plant_values.py` style), never a bare `snapshot == committed`
  byte-equality (the epic-R1-banned REQ-EXT-09 anti-pattern). The `48.571` value is a
  hand-transcribed literal in the test.
- **[HARD]** The (d) after-state pin flips `'Flow Sub'`'s DEGRADED valueless-EP pin to the
  resolved `8.0`, as a behavior-observing pin.
- **[HARD]** The plain-value precedence test on a fixture exercising all three tiers with
  distinct values (design authors the usage-override tier).
- **[HARD]** The SC-3 executor test runs the generated `spec_chain_twolevel` package
  through the in-repo runner and asserts the computed lcoe-analog within tolerance of the
  hand-computed value.
- **[HARD]** The V11 raise-proof re-anchored to a genuinely-deferred shape (not `'Flow
  Sub'`), so the diagnostic still fires after this item clears the plant offenders.

### Baselines, capture, sequencing

- **[HARD]** `plant_values`, `'Flow Sub'`/`plant_value_shapes`, and `spec_chain_twolevel`
  baselines regenerate via `scripts/capture_*.py` with the `--fixtures` name-filter (Item 1
  D7), as reviewed diffs. The four existing cross-part baselines (`catf_mfe`, `ife_plant`,
  `spec_chain_channel`, `spec_chain_twolevel` for the untouched pins) stay byte-identical
  unless a change is deliberately justified as flowing from this mechanism (e.g. the fan-out
  collapse reshaping a channel).
- **[HARD]** The committed fusion-tea snapshot's from-snapshot emission is the SC-4 gate,
  exercised in-repo (license-free), distinct from Item 3's live acceptance run.
- **[HARD]** This item's implement runs **after Item 4's**. Item 4 bumps the snapshot format
  (currently `snapshot_format_version: 1` on the fixtures) to v2 and re-captures every
  snapshot — including `plant_values`, `plant_value_shapes`, `spec_chain_twolevel`, and the
  fusion-tea snapshot. Item 2's before-pins, after-pins, and regenerated baselines are all
  authored against **format v2**. The spec writes no baseline bytes; the plan captures
  against whatever format is live when Item 2 implements.

### Docs and cross-repo (R1/R2/R4)

- **[HARD]** Docs 11 (backtracker), 12 (virtual-binding-rewrite), 25 (hierarchy-resolver),
  and modeling-assumptions §5 record the four supported value shapes, the plain-value
  precedence REQ, and the fan-out-by-source-QN rule (R4 step 4). The matrix rows the
  mechanism touches (the new plain-value precedence REQ, REQ-RES-08, REQ-VBR-10/11 if
  extended) move with the code.
- **[HARD]** The agentic-mbse impact — the four supported whole-plant value shapes for
  MODELING_GUIDE — is recorded for Item 9 as a concrete block (per Item 1's precedent).

## Non-Goals

- **fusion-tea repo changes** (Item 3): deleting `hif_driver_instance`, retiring the
  two-pass gamma feedback / `sanitize_names.py`, re-anchoring channel EQNs, the
  perturbed-input rerun, and the live acceptance run. This item's fusion-tea gate is the
  license-free from-snapshot proxy (SC-4) only. Note: resolving offender #10 (so it does
  not trip V11) IS this item's, via mechanism (d); *deleting* the workaround instance is
  Item 3's.
- **Supertype-chain template inheritance for *plain* usages** — still deferred to the MFE
  epic. **This is a different shape than (d).** Shape (d) is *in-part* consumption of an
  inherited attribute the same def redefines — one part, resolved within its own
  specialization hierarchy, and IN scope here. The deferred shape is *cross-part* supertype
  *template expansion* across a plain typed usage (the calc template itself inherited down a
  supertype chain and expanded per instance). Do not read (d) as the deferred shape: (d) is
  in scope, the template-expansion shape is not.
- **Non-literal RHS in the bare `part :>>` block** (CHAIN/EXPRESSION overrides beyond what
  Item 10 wired) — out unless design shows it falls out free.
- **Constraint resolution/execution** — the `plant_values` assert constraint is Item 4's
  substrate (visibility) and a deferred epic's (execution).
- **The teax OutputRouter/WriteHandler harness** (T-1/T-2) — stays fusion-tea-side.

## Open Questions / Deferred to design

### The mechanism decision — value propagation vs channel wiring (design owns this)

The epic assigns this decision to design (R4 step 1: read the intent, then decide). The
spec states the decision inputs; design decides. The two candidates and what each costs:

**Value propagation ("value-fill").** Carry each literal into the consumer entry point's
`default_value`, so the plant-calc input becomes a pre-filled DESIGN_ATTRIBUTE-style entry
point (the shape the 10-value bridge validated). Costs:

- The params **stay** in the entry-point groups as JSON keys. fusion-tea's harness contract
  (schema field names, JSON key set) is preserved; Item 3 re-anchors values but not keys.
- **Fan-out**: the register frames value-fill as "N independent keys." In the actual repo
  the same-source fan-out already collapses to **one** entry point by shared source QN
  (`test_fanout_collapses_to_one_producer_channel`: both `scale_a`/`scale_b` point at
  `TwoLevelLib__IFE_Power_Plant__scale`). So value-fill filling that one shared EP does
  **not** regress the collapse — provided the mechanism keys EPs by **source-attribute QN**,
  not by per-consumer input name. That constraint is a `[HARD]` requirement above; it
  resolves the register's "N keys" warning: N keys only arises if a mechanism keys
  per-consumer-input, which this item forbids.
- **Diverges on deep re-redefinition**: a value re-redefined in a deeper specialization
  than the one read is not followed (out of scope, but the mechanism must be loud, not
  silently-wrong, if it hits one).

**Channel wiring.** Wire the consumer input to the subsystem attribute as a source (the
shape `_rewrite_specialized_chain` uses for calc-output chains). Costs:

- The params **leave** the entry-point groups (become module_output / shared-source
  channels). Schemas and JSON key sets change; fusion-tea's harness **re-anchors** on the
  new keys, and the report's `run_anchors_bridged.py` breaks (hard-coded old keys, an
  exactly-10 guard). Item 3 absorbs the re-anchor either way — wiring makes it mandatory,
  value-fill makes it optional.
- **Fan-out collapses to one shared channel** — the same source-QN collapse, at the channel
  level.
- Shape (c) is now a carried literal (post-cure), but shapes that ARE genuinely valueless
  need wiring to a user-fill source that carries no value — closer to reference-resolution
  than a producer edge. Design decides whether that is the same operation.

**Shape (d) as a mechanism input.** Whether the chosen mechanism subsumes (d) for free
depends on the mechanism: a value-fill mechanism that walks the specialization chain to find
the literal may cover (a) and (d) in one operation; a channel-wiring mechanism keyed on
*cross-part* source parts may not touch the in-part (d) case. Design must consciously decide
how its mechanism reaches (d) — not pick a mechanism, satisfy (a)/(b)/(c), and ship #9/#10
broken. (d) is named a first-class mechanism target above so this cannot happen silently.

**The invariant that holds either way:** plain-value precedence (usage override >
specialized-def `:>>` > base def), the new REQ above.

**Decision-input provenance:** discovery register §"Anchors REPRODUCED" (the bridge
validates value-propagation semantics only; wiring breaks the bridge; fan-out untouched by
the bridge; feedback-edge ordering un-tripped); the orchestrator's live residual-gap read
(the offender-arithmetic table; #9/#10 are in-part (d); renamed-consumer fan-out); RN-10
(the residual 10-offender gap and the calc-output edge already wired); doc 12 (the
three-tier merge and REQ-VBR-10's calc-output scope).

### Escalation rule for shape (d)

Shape (d) is a **[HARD]** target. If design concludes (d) needs a genuinely distinct
mechanism that is un-landable inside this item's budget, the item does **not** quietly
re-scope (d) out. It returns to the orchestrator and the epic re-plans (d) — e.g. as its
own item, with SC-4/SC-A restated against a documented non-zero interim. The one
unacceptable outcome is (d) silently dropped and fusion-tea still aborting on #9/#10.

### Split decision (design owns this)

The epic's risk table flags Item 2 may exceed 2 days. With (d), the renamed-fan-out rider,
and the executor-path runner added, the lift grew. The split line: **mechanism + headline
flip (a)/(b)/(c) + (d) + precedence** as the core, vs **fan-out-rename + deep-chain edge +
the executor runner** as a possible follow-on. Design decides. Item 1's fixtures pin the
value independently, so a split loses no coverage. Note the executor runner is a hidden
cost the 8–11h estimate did not show — it feeds this decision.

### Smaller design calls

- Whether the chosen mechanism reaches (c) (carried literal) and (d) (in-part) via the same
  path as (a)/(b), or as sibling steps.
- Which fixture anchors the three-tier precedence test (design authors the usage-override
  tier — no existing fixture has it).
- Which genuinely-deferred shape becomes the new V11 raise-proof anchor after `'Flow Sub'`
  clears (candidates: a fixture-gap-register deferred shape, or a deliberately-authored
  still-valueless-wired shape — NOT one this item's mechanism dissolves).

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_pipeline_truth.md` (Item 2; R1–R4; SC-A/SC-B; Risks rows
  on the mechanism decision and the 2-day limit)
- **Spec review:** `.project/active/whole-plant-resolution/spec-review.md` (Revise; the nine
  must-fixes resolved in the Resolutions section below)
- **Required Reading:** discovery register §D6 + §"Anchors REPRODUCED"
  (`.project/research/20260706_pipeline-truth-discovery.md`); fusion-tea report §"The
  residual gap" (`~/1cfe/fusion-tea/work/active/20260706_upstream-fix-verification/report.md`
  — outside the repo sandbox; RN-10 and the orchestrator's live residual-gap read carry its
  essence, including the offender-arithmetic table above);
  `docs/architecture/reference/11-analysis-backtracker.md`,
  `reference/12-virtual-binding-rewrite.md` (the binding-rewrite/precedence content the epic
  cites as `24-binding-resolution.md`; `24-dual-resolution-architecture.md` is the
  resolver-architecture doc), `reference/07-graph-assembly.md` (the epic cites it as
  `07-graph-builder.md` — renamed); RN-10 (`.project/active/cross-part-wiring/release-notes.md`);
  memory notes `cross-part-binding-v11-fallthrough`, `multihop-expose-offline-parity`,
  `plant-idiom-fixtures`.
- **Before-state (Item 1):** `tests/fixtures/plant_values/` (3-offender headline; the F1/F2
  cure restoring (c)'s `7.0` literal is in flight on `design.sysml`);
  `tests/fixtures/plant_value_shapes/` (`'Flow Sub'` = shape (d), DEGRADED);
  `tests/fixtures/spec_chain_twolevel/` (value-carrying cross-part + same-name fan-out);
  Item-1 audit `.project/active/plant-value-fixtures/audit.md` (F1/F2).
- **Research:** `.project/research/20260706_pipeline-truth-discovery.md`
- **Downstream:** Item 3 (`fusiontea-acceptance` — re-anchors and retires whichever
  mechanism lands; deletes `hif_driver_instance`; reuses this item's executor runner); Item
  4 (bumps snapshot format v2 before this item implements); Item 9 (agentic-mbse impact).
- **Design:** `.project/active/whole-plant-resolution/design.md` (to be created — owns the
  mechanism decision, the (d) subsumption call, and the split).

---

## Resolutions

Keyed by the spec-review's Must-Fix IDs (which cite the Lens findings).

- **Must-fix 1 [L1-1, L2-1] — offender #9 in-part.** RESOLVED by orchestrator ruling 1:
  scoped **IN** as a fourth **[HARD]** mechanism target, shape (d), anchored on
  `plant_value_shapes` `'Flow Sub'` (Known Requirements → mechanism; SC-1d). Named as a
  design decision input (Open Questions → "Shape (d) as a mechanism input"). Escalation rule
  recorded (Open Questions → "Escalation rule for shape (d)"): if (d) proves un-landable, the
  item returns to the orchestrator and the epic re-plans — it does not quietly re-scope.
- **Must-fix 2 [L1-2, L5-1] — offender arithmetic.** RESOLVED by orchestrator ruling 2: the
  offender-arithmetic table is now stated in Problem (10 = 8 cross-part a/b/c + 2 in-part d,
  #9 canonical + #10 workaround-instance). With (d) in scope, #10 resolves by the same
  mechanism, so the committed snapshot hits **true zero** — SC-4 is achievable by this item.
  Instance *deletion* stays Item 3's; instance *resolution* is Item 2's (Non-Goals clarifies).
- **Must-fix 3 [L2-2] — renamed-consumer fan-out.** RESOLVED by orchestrator ruling 3:
  fan-out collapses by shared source-QN for differently-named consumers too, now a **[HARD]**
  requirement anchored on the fusion-tea rows (efficiency → driver_efficiency AND eta;
  blanket_energy_multiple → two names). The extended twolevel covers only the same-name case,
  so this item owns a small Item-1-style capture rider adding a renamed-consumer leg.
- **Must-fix 4 [L1-3, L1-4] — VBR-10 scoping.** RESOLVED by orchestrator ruling 4: plain-value
  precedence is defined as **this item's new REQ** (usage override > specialized-def `:>>` >
  base def), NOT an overload of REQ-VBR-10 (doc-12-scoped to calc-output CHAIN rewrites +
  self-named rescue). Design assigns the REQ ID and matrix row and authors the
  currently-unexercised usage-override tier fixture (SC-2, precedence test requirement).
- **Must-fix 5 [L3-1] — executor-path harness.** RESOLVED by orchestrator ruling 5: SC-3 now
  requires **executing** the generated package via a minimal in-repo pipeline runner (import
  generated modules, execute in pipeline-YAML dependency order, feed emitted JSON), stood up
  as a deliverable of this item and reusable by Item 3. Graph-level assertions explicitly do
  not satisfy SC-B. Flagged as a hidden cost feeding the split decision.
- **Must-fix 6 [L2-3] — value-fill fan-out contradiction.** RESOLVED (orchestrator ruling 6):
  the existing `test_fanout_collapses_to_one_producer_channel` collapses by **source QN**
  (both readers → `...__scale` EP). Value-fill fills that one shared EP and does **not**
  regress the collapse, *provided the mechanism keys EPs by source-attribute QN, not
  per-consumer input name* — now a `[HARD]` constraint. The register's "N independent keys"
  warning applies only to a per-consumer-input keying, which this item forbids. The earlier
  spec's contradictory "stays N independent keys" framing is removed.
- **Must-fix 7 [L3-3] — V11 re-anchor entanglement.** RESOLVED: since (d) is IN scope,
  `'Flow Sub'` clears (SC-1d) and can no longer be the V11 raise-proof anchor. SC-5 now
  requires a **genuinely-deferred** shape; candidates listed under "Smaller design calls."
- **Must-fix 8 [L3-4] — supertype-chain non-goal vs (d).** RESOLVED: Non-Goals now
  distinguishes in-part inherited-attr-redefine (d) [IN scope] from cross-part supertype
  *template expansion* for plain usages [deferred] — an explicit sentence so the non-goal
  does not silently dispose of (d).
- **Must-fix 9 [L3-2] — (c) anchor provenance.** RESOLVED and superseded by the Item-1 F1/F2
  cure: (c) is now a **carried literal** (`:>> chamber.cost_per_unit = 7.0`, a usage-level
  dotted override), not a test-supplied user-fill. All three headline inputs are model
  literals; the `48.571` anchor is stated with that provenance and its dependency on the cure
  commit (SC-1). The reviewer's pre-cure "presence-and-fill" framing no longer applies.
- **Non-blocking L4-1 — taxonomy restated three times.** ADDRESSED: the four-shape taxonomy
  is now stated once in Problem ("The value shapes") and referred back to, rather than
  re-listed in SC-1 and the mechanism `[HARD]`.

---

## agentic-mbse Impact (Item 9 accumulation)

The four whole-plant value-provision shapes the materializer supports, for the
MODELING_GUIDE (concrete-block style, Item-1 precedent). Each is a pattern a modeler may
author and expect to resolve cross-part/in-part:

- **(a) subtype-def literal via usage-level retype** — `:>> driver : 'Hif Driver'` where
  `Hif_Driver` carries `:>> efficiency = 0.35`. Reaches the consumer through the retype;
  resolved via `usage_type_map` (tier 2a).
- **(b) bare no-retype override block** — `part :>> target_factory { :>> cost_per_target = 10.0; }`.
  Owner QN is the sub-part instance; resolved via `design_overrides` (tier 1).
- **(c) plain one-hop cross-part attribute with a usage-level dotted override** —
  `:>> chamber.cost_per_unit = 7.0` on the plant instance. Resolved via `design_overrides`
  `target_path` (tier 1).
- **(d) in-part inherited-attr redefine** — `in flow_rate = throughput` reading an
  inherited attribute the same def redefines below the binding (`:>> throughput = 8.0`).
  Resolved via a direct-owner LITERAL redefinition (tier 2b), no `usage_type_map` needed.

Guidance the guide should teach: precedence is **usage override > specialized-def `:>>` >
base def**; entry points key by the **source attribute QN**, so renaming an input per
consumer still collapses to one parameter; only LITERAL values propagate — a CHAIN/EXPRESSION
supplied value falls through to the uncovered-parameter diagnostic, not silently.

---

**Next Steps:** After approval, proceed to `/_my_design`. Design owns the mechanism decision
(value propagation vs channel wiring), whether that mechanism subsumes shape (d), and the
split decision, with the decision inputs above and the discovery §"Anchors" attack as
primary input.
