# Spec: fusion-tea Acceptance & Workaround Retirement (PIPELINE-TRUTH Item 3)

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-07-06
**Complexity:** HIGH
**Branch:** pipeline-truth-epic (this repo) · fusion-tea branch per their norms (plan-time)

---

## Problem

fusion-tea's models are the epic's real-world proof: the point of PIPELINE-TRUTH is that a
consumer's model set generates, wires, and executes end-to-end from generated artifacts
alone, with zero bridges and zero hand-plumbing. Item 2 lands the last mechanism (whole-plant
value resolution), so the pieces now exist. But **the end state was never assembled**. The
fusion-tea validation report stopped at graph inspection; nobody has deleted the workarounds,
re-anchored the channels, regenerated, and run the anchors on the workaround-free models.

Three concrete gaps remain, each named by the adversarial discovery pass:

- **The SC-3 end state is untested (register §adversarial, SC-3 row).** The recommended world
  — `hif_driver_instance` deleted, channel EQNs re-anchored, anchors passing single-pass — was
  never built. The report's own bridge (`run_anchors_bridged.py`) *breaks* in that world (it
  hard-codes stale keys and an exactly-10-offender guard). Assembling and running it is this
  item's core.
- **Pre-filled values were never proven consumed (register §adversarial, SC-5 row).** Every
  run-C value happens to equal a baked schema default, so a JSON-ignoring executor reproduces
  the anchor bit-exactly. No test has ever moved an input and confirmed the output followed.
  That hole infects every prior anchor claim.
- **Full-emission live-vs-snapshot parity exists only on `solar_battery` (register
  §adversarial, SC-9/10 row).** None of fusion-tea's shapes are covered, and there is a
  documented offline mis-wire precedent (multi-hop EXPOSE) that abort-level checks cannot see.

fusion-tea also still carries every workaround — `sanitize_names.py` (dead but not deleted),
`hif_driver_instance`, the two-pass gamma feedback, hand-written input JSONs. The epic's
critical success factor is that these are **deleted**, not merely deletable.

### What Item 2 hands this item (the substrate)

- The **supplied-value materializer** (REQ-SVM family) resolves all ten V11 offenders on the
  committed fusion-tea snapshot to filled DESIGN_ATTRIBUTE entry points — mechanism is
  **value-fill**, not channel wiring (design D1). So the ten params **stay** JSON-fillable keys
  in the entry-point groups; only their values are carried from the model.
- Entry points key by **source-attribute QN**, so a fan-out (one attribute feeding several
  consumers) collapses to **one** JSON key even when the consumers are differently named
  (e.g. `driver.efficiency` → `lcoe_calc.driver_efficiency` AND `recirc_calc.eta` collapse to
  one source-QN key). This **changes the JSON key set** the report's harness assumed.
- A reusable executor: `run_pipeline(package_dir, inputs) -> dict[str, float]` — a minimal
  in-repo pipeline runner (imports the generated modules, executes them in pipeline-YAML
  dependency order, feeds the emitted JSON inputs, returns channel values). This item's
  acceptance run consumes it sight-unseen.

### Facts that post-date the epic text (baked into scope)

1. **Snapshot format is v2** (Item 4); the loader hard-rejects v1. Every fusion-tea snapshot in
   fusion-tea's `work/` dir is v1. The acceptance run **re-captures** the fusion-tea snapshot at
   v2 from the canonical models (live-license leg). Item 2's implement may already have committed
   one v2 fusion-tea capture for its SC-4 proxy — **coordinate, do not duplicate** (see Open
   Questions).
2. **The constraint report now fires on `assert` constraints** (Item 4). fusion-tea's `generate`
   output will include the constraint-drop report. The acceptance run **records** it as expected
   output, not a surprise.
3. **Offender #10 resolves without deletion.** With Item 2 landed, both in-part offenders (#9 on
   the canonical part, #10 on `hif_driver_instance`) resolve via mechanism (d), so the canonical
   models generate at **true zero** V11 offenders *even before* `hif_driver_instance` is deleted.
   Deleting the instance is still this item's cleanup job (it removes a dead workaround and lets
   the Meier channels re-anchor to the canonical driver path) — but zero-offenders does not
   depend on it. Both states get verified (see SC-A).

### Report access note (provenance)

The fusion-tea validation report
(`~/1cfe/fusion-tea/work/active/20260706_upstream-fix-verification/report.md`) is outside this
repo's sandbox and unreadable from the spec session. Its load-bearing content — the retirement
table, the residual-gap/offender-arithmetic breakdown, the coordination actions, and the
`run_anchors` reproduce recipe — is carried in-repo via the discovery register §adversarial,
RN-10, and Item 2's spec/design (the same precedent Item 2 set). The plan phase, which touches
the fusion-tea repo directly, re-reads the report in a session with fusion-tea access.

---

## Success Criteria

- [ ] **SC-A (assemble the end state; zero offenders both states).** On fusion-tea's canonical
  models, `generate` emits the full package with **zero V11 offenders, zero bridges, zero
  post-processing**, verified in **both** states: (i) *before* deleting `hif_driver_instance`
  (Item 2's mechanism (d) resolves both #9 and #10 in place → true zero); and (ii) *after*
  deleting `hif_driver_instance` and re-anchoring the Meier channel EQNs to the canonical driver
  path (`hif_plant_pkg__hif_plant__driver__meier_cost__*`) → still zero, with the workaround
  reference gone. This is the epic's SC-A live gate (its license-free proxy is Item 2's SC-4).

- [ ] **SC-B (run-C reproduces + is proven consumed).** fusion-tea's simplified `run_anchors.py`
  — no bridge, no two-pass gamma feedback — reproduces run-C's lcoe of
  **$270.1211779380445/MWh at rel 1e-6** through the generated package alone, with anchors A/B
  as module-level checks and C as the full pipeline run. **Plus** the perturbed-input proof:
  edit one key in the *emitted* JSON (e.g. `gain` 80→100), rerun, and assert the lcoe moves to
  the **hand-computed** target (computed independently of the executor, not read back from it).
  This closes the consumed-vs-baked-default hole.

- [ ] **SC-C (every workaround deleted).** The retirement table is all-deleted upstream, not just
  deletable: `sanitize_names.py`, `hif_driver_instance` (+ channel re-anchor), the two-pass gamma
  feedback, and the hand-written input JSONs for wired values. After the change, the fusion-tea
  repo has **zero references** to `sanitize_names.py`, `hif_driver_instance`, or the two-pass
  feedback. (The teax OutputRouter/WriteHandler — T-1/T-2 — stays; it is out of epic scope by
  design.)

- [ ] **SC-D (SNAP-19 parity parametrized + live leg).** The REQ-SNAP-19 live-vs-snapshot
  byte-parity test is parametrized over the shape-bearing fixtures — `retype_model`,
  `quoted_owner_formula`, `alias_agg_probe`, `ife_plant`, and Item 1's `plant_values` headline
  fixture — not `solar_battery` alone. Plus the fusion-tea live emission is byte-diffed against
  its v2 snapshot emission once. Parity is **channel-identity**, not merely "left
  `fallback_entry_points`" (the multi-hop EXPOSE mis-wire precedent — memory note
  `multihop-expose-offline-parity` — passed the weaker check).

---

## Known Requirements

### Acceptance run (SC-A / SC-B)

- **[HARD]** The acceptance run drives the generated package through Item 2's
  `run_pipeline(package_dir, inputs) -> dict[str, float]` runner (reused verbatim, not
  re-implemented). SC-B's tolerance and perturbation assertions run against the runner's output,
  never graph inspection.
- **[HARD]** The perturbed target is **hand-computed** from the model's arithmetic and
  transcribed as a literal in the test — never read back from the resolver or executor (the epic
  R1 anti-pattern ban; the SC-5 hole this closes).
- **[HARD]** Anchors A/B become **module-level** checks (each calc's own semantics, run in
  isolation); anchor C is the **full-pipeline** run through the generated package. The bridge and
  the two-pass gamma feedback are gone — anchor C passes single-pass.
- **[INFERRED]** The value-fill + source-QN fan-out collapse **changes the JSON key set** the
  report's `run_anchors` harness assumed (collapsed fan-out keys; params stay as input keys).
  The harness-coordination rows (which JSON key each anchor writes/reads, which channel each
  anchor asserts) are **re-derived** for the value-fill shape before `run_anchors.py` is
  simplified. The perturbed key must be a key that actually exists in the emitted JSON after
  collapse.

### Channel re-anchor (SC-A state ii)

- **[HARD]** Deleting `hif_driver_instance` from the canonical models re-points the Meier cost
  channels to the canonical driver path (`hif_plant_pkg__hif_plant__driver__meier_cost__*`). The
  channel EQNs in fusion-tea's `run_anchors.py` / `sweep_ife.py` are re-anchored to match. The
  post-deletion generate still emits zero offenders and the re-anchored anchors still pass.

### Snapshot re-capture (SC-D live leg; R3)

- **[HARD]** The fusion-tea snapshot is re-captured at **format v2** from the canonical models
  via the capture script (live license), as a reviewed diff (R3 baseline discipline). If Item 2
  already committed an equivalent v2 fusion-tea snapshot, reuse it and do not re-capture a second
  copy — the live leg is then the parity byte-diff, not a duplicate capture (see Open Questions).
- **[HARD]** SNAP-19 parity is a **channel-identity** comparison across the parametrized fixture
  set, plus a one-time fusion-tea live-vs-snapshot byte-diff. A mis-wire that still vacates
  `fallback_entry_points` must be caught — assert the wired channel's identity, per the offline
  mis-wire precedent.

### Cross-repo & tests (R1/R2)

- **[HARD]** fusion-tea changes land in the fusion-tea repo (`~/1cfe/fusion-tea`, a git repo) as
  a PR or branch per that repo's conventions (checked at plan time). This repo (sysml-codegen)
  receives only the parametrized SNAP-19 parity test.
- **[HARD]** A run report captures the assembled end state: both offender states, the run-C
  reproduction, the perturbed-input delta, the recorded constraint report, and the retirement
  checklist. It lives in this item's active dir.
- **[INFERRED]** The parametrized SNAP-19 parity test follows R1: it fires on the shape it claims
  (a deliberate mis-wire or format-drift on any parametrized fixture fails it) and stays green on
  faithful round-trips; its expectations are independently anchored, not computed by the code
  under test.
- **[INFERRED]** R2 (agentic-mbse lockstep): this item changes no executable SysML subset and no
  auditor behavior — agentic-mbse impact is **none new**. Recorded explicitly for Item 9's
  accumulation rather than left implicit.

---

## Non-Goals

- **teax OutputRouter/WriteHandler (T-1/T-2).** The harness router stays fusion-tea-side — out of
  epic scope by design. Not retired.
- **Constraint execution.** The ηG>10 viability check in `sweep_ife.py` stays harness-side until
  the deferred constraint-execution epic lands. Item 4 makes the constraint drop loud and true
  (the acceptance run records the report); executing it is not this item's job.
- **The Item 2 mechanism itself.** This item consumes the landed materializer and runner; it does
  not build or change resolution code. If the acceptance run surfaces a mechanism gap, it escalates
  to Item 2, it does not patch resolution here.
- **Building the fusion-tea snapshot fixtures / Item 4's format bump.** Those are Items 1/2/4;
  this item captures the live fusion-tea snapshot for the parity leg and consumes the committed
  fixtures.

---

## Open Questions / Deferred to plan

- **fusion-tea branch/PR convention.** The fusion-tea repo is outside this session's sandbox, so
  its branch naming and PR norms could not be inspected. The plan phase (with fusion-tea access)
  checks and follows them. Recommendation until then: a dedicated branch mirroring this epic's
  `pipeline-truth-epic` naming, PR per fusion-tea's norm.
- **Reuse vs re-capture of the v2 fusion-tea snapshot.** Whether Item 2's implement already
  committed an equivalent v2 fusion-tea snapshot (making a second live capture redundant) depends
  on what Item 2 actually landed. Plan reconciles: reuse the committed snapshot for the snapshot
  leg if present; the live leg is then only the re-capture + parity byte-diff. Do not commit two
  fusion-tea snapshots.
- **The exact perturbed-input target value.** `gain` 80→100 is the named example; the resulting
  hand-computed lcoe is derived from the model arithmetic at implement and transcribed as a
  literal. Which emitted JSON key to perturb must also survive the fan-out collapse (an existing
  post-collapse key).
- **The six `out attribute` conversions.** Reverting them is optional and verified-safe either
  way (epic coordination note). Deferred to plan/implement: default recommendation is to revert
  for cleanliness (the mission is zero workarounds), but only if they are not load-bearing for a
  genuine output — plan confirms before touching them.
- **Where the SNAP-19 parametrization + fusion-tea byte-diff harness live in-repo** (extend the
  existing `test_snapshot_generation::test_live_vs_snapshot_byte_identical` vs a new parametrized
  test) — a plan-time structuring call.

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_pipeline_truth.md` (Item 3; SC-A/SC-B/SC-C; R1/R2/R3;
  Risks row on Item 2's mechanism reshaping the harness contract)
- **Required Reading:** fusion-tea report §"Coordination actions" + §"Reproduce" + retirement
  table + residual-gap table (`~/1cfe/fusion-tea/work/active/20260706_upstream-fix-verification/report.md`
  — outside the sandbox; essence carried by the register §adversarial, RN-10, and Item 2's
  artifacts, per the provenance note above); discovery register §adversarial (SC-3, SC-5,
  SC-9/10, Anchors rows) (`.project/research/20260706_pipeline-truth-discovery.md`);
  `docs/architecture/reference/27-snapshot-generation.md` (REQ-SNAP-19); memory note
  `multihop-expose-offline-parity`
- **Upstream (Item 2, consumed):** `.project/active/whole-plant-resolution/{spec,design,plan}.md`
  — value-fill mechanism, source-QN fan-out collapse, the `run_pipeline(package_dir, inputs)`
  runner contract (design §"SC-3 runner interface"), offender-arithmetic table (10 → true zero)
- **Research:** `.project/research/20260706_pipeline-truth-discovery.md`
- **Memory:** `multihop-expose-offline-parity`, `cross-part-binding-v11-fallthrough`,
  `plant-idiom-fixtures`
- **Plan:** `.project/active/fusiontea-acceptance/plan.md` (to be created)

---

**Next Steps:** After approval, proceed to `/_my_plan` (this item is spec → plan, no design —
it assembles and retires against landed mechanisms; the plan phase re-reads the fusion-tea
report with repo access and resolves the plan-time opens above).
