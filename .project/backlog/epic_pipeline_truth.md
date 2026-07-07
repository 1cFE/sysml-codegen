# Epic: The Generated Package Is the Truth

**Epic ID**: PIPELINE-TRUTH
**Status**: Draft
**Priority**: High
**Created**: 2026-07-06
**Estimated Effort**: ~10.5–13.5 days (10 items; two parallel tracks)

---

## Executive Summary

UPSTREAM-FINDINGS fixed the verified findings and staged cross-part support; the
2026-07-06 fusion-tea validation confirmed the fixes hold on real models and measured
exactly what remains. This epic finishes it: a consumer's real model set generates,
wires, and executes end-to-end with zero bridges and zero hand-plumbing — and every
diagnostic demonstrably fires on the shape it claims to cover, verified by tests that
can actually fail.

**Critical Success Factor**: `generate` on fusion-tea's models emits the full package
with zero V11 offenders, run-C's lcoe ($270.1211779380445/MWh) reproduces through the
generated package alone, and every fusion-tea workaround in the retirement table is
deleted — not just deletable.

---

## Mandatory Reading (every item)

1. **The validation report** — `~/1cfe/fusion-tea/work/active/20260706_upstream-fix-verification/report.md`
   (per-SC matrix, the 10-offender gap, bridge methodology, retirement table,
   coordination checklist). Caveat: its line-74 capture-path observation is wrong —
   see the discovery register's correction.
2. **The discovery register** — `.project/research/20260706_pipeline-truth-discovery.md`
   (D1–D7 + adversarial findings with dispositions; the evidence base for every item).
3. **The supported-subset contract** — `docs/architecture/modeling-assumptions.md`
   (scrubbed 2026-07-06; trustworthy — but §8's "scans the whole model" overclaims
   until Item 4 lands).
4. **The prior epic** — `.project/backlog/epic_upstream_findings.md` (patterns,
   lessons learned, and the R1/R2/R3 requirements carried forward below).

## Cross-Cutting Requirements (carried forward from UPSTREAM-FINDINGS)

### R1 — Design-pattern consistency
Unchanged from the prior epic: ComputationGraph is the sole input to generation
(deliberate revs only); typed registries and NewType keys; compute-once-look-up;
diagnostics follow the V1–V11 pattern (nothing dropped silently); conformance tests
use real SysML fixtures, never mocks; REQ tags + docs + matrix rows move with code.
**Addition for this epic**: every new or changed diagnostic lands with (a) a test
proving it FIRES on the shape it claims, with an independently-anchored expectation,
and (b) a test proving it stays silent on clean input. The REQ-EXT-09 anti-pattern
(expectation computed by the code under test) is banned; Item 6 purges the existing
instances.

### R2 — agentic-mbse lockstep
Unchanged: every item ends by recording (and where trivial, implementing) matching
agentic-mbse changes; Item 9 executes the accumulated list; nothing silently dropped.
Note Item 4 is *inherently* cross-repo — the enumeration fix lives in agentic-mbse's
adapter and this repo consumes it; land as a coordinated pair (companion branch, like
`upstream-findings-sync`).

### R3 — Baseline discipline
Baseline/snapshot regeneration through `scripts/capture_*.py` only, with reviewed
diffs. The syside license is on **monthly renewal — no expiry pressure**; schedule
capture work on its merits (Item 1 early because Items 2/5 build on its fixtures, not
because of any license window).

### R4 — Verify-then-fix protocol (anti-whack-a-mole)

Discovery findings are **static-read verdicts, not confirmed bugs**. The register's
16 D3 sites, the D7 divergences, and every other agent finding were established by
reading code, not by executing it. No item writes a fix on the strength of the
register alone. For every finding an item picks up, in order:

1. **Check architectural intent first.** Read the component's reference doc and any
   REQ rows BEFORE diagnosing. A code-vs-doc divergence is a *decision point* — the
   doc may record the intended design the code failed to reach (F4 is exactly this:
   docs 03/04/05 describe `resolve_input()` as the intended consolidated resolver,
   with design rationale; the code never cut over). "Fix the code to the doc" and
   "fix the doc to the code" are both legal outcomes; picking one without reading the
   intent is not.
2. **Reproduce before fixing.** Each finding gets a failing test or live probe
   against real code (real fixtures, never mocks — R1) demonstrating the concrete
   failure scenario. A finding that does not reproduce is reclassified in the
   discovery register (with the probe evidence), not fixed. The prior epic's
   probe-first discipline is the precedent — it refuted a primary rule live and
   killed a false worksheet before code.
3. **Fix at the root, in the house style.** Findings cluster into families
   (blind-dispatch fall-throughs, gated-report silences, name-keyed lookup maps,
   exception swallows, exact-type queries). Design the fix per FAMILY at the cleanest
   choke point — the D4 model: one adapter parameter, not fifteen call-site patches.
   A proposed fix that patches a symptom site while siblings keep the same defect
   fails design review. New mechanisms follow the established patterns (typed
   registries, V-diagnostic style, compute-once-look-up).
4. **Close the loop in the docs.** The reference doc, modeling-assumptions section,
   and matrix rows for the touched component are updated in the same change (R1) —
   including *removing* the intent prose when the decision was "re-frame", so the
   next reader never inherits a doc describing code that doesn't exist.

Item specs make this protocol visible: a verification table (finding → probe →
CONFIRMED / NOT-REPRODUCED / RECLASSIFIED) is a required spec artifact for Items 5
and 7, and the register is updated as findings are confirmed or struck.

---

## Why This Epic?

**Current State**:
- `generate --models ~/1cfe/fusion-tea/models` aborts at V11 on exactly 10 plain
  subsystem-attribute → plant-calc-input references. The entry-point slots exist and
  are valueless; the values are literals sitting in the model; a 10-value bridge
  reproduces anchor C bit-exactly in a single pass with both feedback edges closed via
  generated wiring. The fix is measured, small, and the payoff is total.
- fusion-tea still carries every workaround: `hif_driver_instance`, the two-pass gamma
  feedback, hand-built input JSONs (`sanitize_names.py` is dead but not deleted).
- The constraint-drop report is silent for exactly the shape fusion-tea uses
  (`assert constraint` → `AssertConstraintUsage`, invisible to the exact-type query),
  its conformance test is structurally unable to fail, and the same subtype-blind
  enumeration pattern breaks agentic-mbse's Level-3 dataflow validation outright
  (queries abstract `Import`, matches nothing, always passes).
- Discovery found 16 more real-bug-likely silent-failure sites, 25 tests that cannot
  fail, ~11 divergent-PASS matrix rows beyond the filed F2/F4 (F4 is worse than filed:
  the whole IR family pins a dead module), and 11 fusion-tea model shapes no fixture
  covers.

**Future State**:
- The generated package is the truth: fusion-tea's models generate, wire, and execute
  end-to-end from generated artifacts alone; every workaround deleted upstream.
- Diagnostics are trustworthy: subtype-aware enumeration, loud extraction failures,
  zero-found sentinels on the pattern-3 family, and every V-rule pinned by a test that
  fires on the claimed shape with an independently-anchored count.
- The verification matrix tells the truth: no PASS row pins less than its text, the
  dead resolver path is excised or landed, and the docs-scrub certification still
  holds at epic close.

---

## Success Criteria

- [ ] **SC-A**: `generate --models ~/1cfe/fusion-tea/models` emits the full package —
  zero V11 offenders, zero bridges, zero post-processing. (Gate: fusion-tea acceptance
  run, Item 3; license-free proxy: the committed fusion-tea snapshot generates clean.)
- [ ] **SC-B**: Run-C's lcoe reproduces through the generated package alone. Gates in
  two places: an in-repo tolerance test on the extended `spec_chain_twolevel` fixture
  (Item 2), and the fusion-tea acceptance run against $270.1211779380445/MWh at
  rel 1e-6 (Item 3) — including one perturbed-input rerun proving the JSON is
  consumed, not the baked schema defaults.
- [ ] **SC-C**: Every fusion-tea workaround in the report's retirement table is
  **deleted** upstream (`sanitize_names.py`, `hif_driver_instance` + channel
  re-anchor, two-pass gamma feedback, hand-written input JSONs), not just deletable
  (Item 3).
- [ ] **SC-D**: Every V-diagnostic and every extraction/resolution warning
  demonstrably fires on every syntactic shape it claims — assert and require
  constraints included — with independently-anchored expected counts (Items 4, 5).
- [ ] **SC-E**: Zero self-referential diagnostic tests remain; the 25 flagged tests
  are re-anchored; the pass-or-skip test fails when its assertion fails (Item 6).
- [x] **SC-F**: REQ text, tests, and code agree — F2 and F4 resolved by decision (land
  or excise/re-frame), every divergent-PASS row from discovery fixed, the UNTESTED-12
  dispositioned, no PASS row pins less than its text (Item 7). ✅ Certified 2026-07-06.
- [ ] **SC-G**: Full suite green; ruff/mypy counts not worse than the 21/109 baseline;
  all baseline churn via capture scripts with reviewed diffs.
- [ ] **SC-H**: agentic-mbse teaches and checks everything this epic changes (Item 9);
  the docs-scrub certification still holds at epic close — every retired caveat
  removed from docs, matrix, and the explainer prompt (Item 10).

---

## Backlog Items

### Item 1: Plant-Value & Blind-Spot Fixtures [0.5–1 day]

**Type**: Modeling / Testing
**Effort**: 0.5–1 day (spec 1h, plan 0.5h, execute 3–5h) — fit: high (prior Item 8 is
the template); lift: low (fixture authoring + capture); risk: low.
**Dependencies**: None — do first on Track A (Items 2 and 5 build on these fixtures).
Needs live license for capture (available; monthly renewal).

**Objective**: Close the fixture blind spot for the whole-plant value shapes before the
mechanism work starts — the D6 recipe reproduces 9 of the 10 V11 offenders in one
fixture.

**Scope**:
1. **The headline fixture** (`plant_values` or extension of `ife_plant`), per the D6
   recipe: base plant def declaring `part sub : AbstractBase` + calc AND
   assert-constraint usages binding `sub.<plain_attr>`; a plant part USAGE containing
   both (a) a bare no-retype `part :>> sub { :>> attr = <literal>; }` block — a shape
   **zero** fixtures currently contain — and (b) a usage-level retype whose subtype def
   supplies other attrs via literal `:>>`; plus an assert constraint with a cross-part
   binding, a self-named binding, and an unbound defaulted param.
2. **Extend `spec_chain_twolevel`** with the plain cross-part-attribute shape (the P1
   acceptance note), including one attribute consumed by TWO modules (the fan-out
   collapse case the bridge never exercised).
3. **High-value secondary shapes** from D6 (cheap rows in the same or a small second
   fixture): attribute-def-typed attribute with nested `:>>` (the 14-econ-params
   shape), bare `default 10.0` (no `:=`), doc bodies inside calc usages and on `:>>`
   redefinitions, an in-binding referencing an inherited attr the same def redefines,
   a 5-deep specialization chain with abstract ends, quoted enum def + usage-level
   quoted enum `:>>`, a quoted OUTPUT parameter name (`out attribute 'net cost'`),
   and Style-E calc def (mixed `out attribute` + `return` in one def, in a quoted def).
4. Capture extraction snapshots + current (known-incomplete) baselines so Item 2's
   progress shows as reviewed diffs; capture `deep_cross_scope_probe` while at it
   (D1-F6 — currently drifts silently with no committed snapshot). Spec-time decision:
   run the BACKLOG stale-fixture-refresh chore (wi014_toy, self_named_binding_trap,
   quoted_owner_formula path canonicalization) as a rider in the same live-capture
   session — own commit, reviewed diff, per its BACKLOG entry.
5. agentic-mbse impact: fixture shapes become the plant-value reference examples
   (recorded for Item 9).

**Out of Scope**:
- Any production-code change (fixtures + captures only).
- Fixture rows for shapes this epic defers (conditionals, non-uniform arrays,
  EXPOSE_COMPUTED).

**Success Criteria**:
- [ ] Headline fixture loads, snapshots, and trips V11 with an offender list that
  reproduces all three value-provision mechanisms (subtype-def literal via retype;
  bare no-retype `part :>>` block; twolevel chain) — the pinned "before" state.
- [ ] Secondary-shape fixtures load and snapshot; each shape's current behavior
  (correct, degraded, or diagnostic) is pinned by a test, not assumed.
- [ ] All captures script-reproducible; existing baselines byte-identical.

**Required Reading**: discovery register §D6 (the full shape diff with fusion-tea
file:line exemplars); `docs/architecture/reference/25-hierarchy-extraction.md`;
`modeling-assumptions.md` §5; memory note `plant-idiom-fixtures`.

**Deliverables**: `.project/active/plant-value-fixtures/{spec,plan}.md`, fixtures +
snapshots + baselines.

---

### Item 2: Whole-Plant Cross-Part Value Resolution [1.5–2 days] ✅

**Type**: Implementation — **the headline item; first-class, gates fusion-tea**
**Effort**: 1.5–2 days (spec 2h, design 3h, plan 1h, execute 8–11h) — fit: high (the
entry-point slots already exist in the derived groups; the values are literals in the
model; the bridge proved the semantics); lift: medium; risk: **medium-high** (the
epic's riskiest item — design decides the mechanism and whether to split).
**Dependencies**: Item 1 (fixtures pin before/after).

**Objective**: The 10 plain subsystem-attribute → plant-calc-input references resolve
from generated artifacts alone — fusion-tea's full YAML emits with zero V11 offenders.

**Scope**:
1. **The design decision (spec/design phase, not pre-committed): value propagation vs
   channel wiring.** The bridge proved value-propagation sufficient for anchor
   semantics (all 10 sources are literals). But note the adversarial findings: if it
   lands as wiring, the 10 params leave the entry-point groups (schemas/JSON keys
   change and fusion-tea's harness re-anchors); if as value-fill, a future
   re-redefinition in a deeper specialization diverges in value, and fan-out (one attr
   feeding 3 consumers) stays N independent keys instead of one shared channel. The
   precedence chain (usage override > specialized-def `:>>` > base def, REQ-VBR-10)
   must hold identically for whichever mechanism lands.
2. Implement for all three mechanisms from Item 1's fixture: subtype-def literal
   through usage-level retype; bare no-retype `part :>>` override block; and confirm
   the twolevel chain still wires.
3. In-repo tolerance test: the extended `spec_chain_twolevel` computes its lcoe-analog
   through the generated package (executor-level, not just graph-level) within
   tolerance — SC-B's in-repo gate.
4. Regenerate plant-fixture baselines (reviewed diffs); catf_mfe/existing four
   baselines byte-identical or justified.
5. License-free acceptance proxy: `generate --from-snapshot` on the committed
   fusion-tea snapshot emits full YAML, zero offenders.
6. agentic-mbse impact recorded: the newly supported value shapes for MODELING_GUIDE.

**Out of Scope**:
- fusion-tea repo changes (Item 3).
- Supertype-chain template inheritance for *plain* usages (still deferred — see
  Deferred).
- Non-literal RHS in the bare `part :>>` block (CHAIN/EXPRESSION overrides beyond
  what Item 10 already wired) unless design shows it falls out free.

**Success Criteria**:
- [ ] Headline fixture generates clean — zero V11 offenders, values/edges correct per
  hand-computed expectations (independently anchored, not derived from the resolver).
- [ ] fusion-tea snapshot generates the full package, zero offenders.
- [ ] Extended-twolevel tolerance test passes through the teax executor path.
- [ ] Existing baselines byte-identical or reviewed; V11 raise-proof survives on a
  still-uncovered fixture (re-anchor it deliberately, as Item 9 of the prior epic did).

**Required Reading**: discovery register §D6 + adversarial "Anchors" attack;
fusion-tea report §"The residual gap"; `reference/11-analysis-backtracker.md`,
`reference/24-binding-resolution.md`, `reference/07-graph-builder.md`; RN-10
(`.project/active/cross-part-wiring/release-notes.md`); memory note
`cross-part-binding-v11-fallthrough`.

**Deliverables**: `.project/active/whole-plant-resolution/{spec,design,plan}.md`,
mechanism + tests, regenerated baselines, docs 11/24/25 + modeling-assumptions §5
updates (R1).

---

### Item 3: fusion-tea Acceptance & Workaround Retirement [1–1.5 days] ✅

**Type**: Execution / cross-repo coordination
**Effort**: 1–1.5 days (spec 1h, plan 1h, execute 5–8h) — fit: high (the report's
coordination checklist is the map; `run_anchors_bridged.py` is the working template);
lift: low-medium; risk: medium (cross-repo; the SC-3 end state was never assembled).
**Dependencies**: Item 2. Needs live license for the live-vs-snapshot parity leg.

**Objective**: fusion-tea runs on the generated package alone — every workaround
deleted, anchors green, and the evidence gaps the adversarial pass named are closed.

**Scope**:
1. **Assemble the end state the report never tested**: delete `part
   hif_driver_instance` from the canonical models, re-capture the snapshot, re-anchor
   channel EQNs in `run_anchors.py`/`sweep_ife.py` (Meier channels →
   `hif_plant_pkg__hif_plant__driver__meier_cost__*`), regenerate, and run anchors
   single-pass on the 9-offender-free world.
2. **Retire per the table**: delete `sanitize_names.py`, the two-pass gamma feedback,
   hand-written input JSONs for wired values; keep the teax OutputRouter/WriteHandler
   (T-1/T-2, out of scope by design). Anchors A/B become module-level checks (the
   model's own semantics).
3. **Perturbed-input proof (SC-B rider)**: edit one key in the emitted JSON (e.g.
   `gain` 80→100), rerun, assert lcoe moves to the hand-computed value — closes the
   "consumed vs baked-default" hole that infects every prior anchor claim.
4. **Live-vs-snapshot full-emission parity** on shape-bearing fixtures: parametrize
   the REQ-SNAP-19 byte-parity test over `retype_model`, `quoted_owner_formula`,
   `alias_agg_probe`, `ife_plant`, and the Item-1 headline fixture (currently
   solar_battery-only — against a documented offline mis-wire precedent). Live
   fusion-tea emission byte-diffed against the snapshot emission once.
5. Coordination notes: revert of the six `out attribute` conversions is optional
   (verified safe); `sweep_ife.py`'s ηG>10 stays until constraint execution.

**Out of Scope**:
- teax T-1/T-2 (harness router stays — out of epic scope).
- Constraint execution (the ηG viability check stays harness-side).

**Success Criteria**:
- [x] fusion-tea `run_anchors.py` (simplified, no bridge, no two-pass) passes A/B
  module-level + C full-pipeline at rel 1e-6, on the workaround-free canonical models.
- [x] Perturbed-input rerun moves the output to the hand-computed value.
- [x] Retirement table all-deleted; fusion-tea repo has no reference to
  `sanitize_names.py` / `hif_driver_instance` / two-pass feedback.
- [x] SNAP-19 parity green over the parametrized fixture set, live leg included.

**Required Reading**: fusion-tea report §"Coordination actions" + §"Reproduce";
discovery register §adversarial (SC-3, SC-5, SC-9/10, Anchors rows);
`reference/27-snapshot-generation.md`; memory note `multihop-expose-offline-parity`.

**Deliverables**: `.project/active/fusiontea-acceptance/{spec,plan}.md` + a run
report; fusion-tea PR(s); parametrized parity test in this repo.

---

### Item 4: Subtype-Aware Enumeration & Constraint-Report Truth [1–1.5 days]

**Type**: Implementation (coordinated pair with agentic-mbse)
**Effort**: 1–1.5 days (spec 1.5h, design 1h, plan 1h, execute 5–7h) — fit: high (the
fix surface is ONE adapter choke point: syside's `include_subtypes=True` exists and is
never passed); lift: low-medium; risk: medium (semantics decision: what appears in a
subtype-aware sweep — e.g. RequirementUsage under ConstraintUsage — must be decided,
not defaulted).
**Dependencies**: None (Track B, parallel with Items 1–2).

**Objective**: Every model-wide enumeration sees what it claims to see; the
constraint-drop report fires on assert constraints; its test can fail.

**Scope**:
1. **agentic-mbse adapter**: add subtype-aware enumeration
   (`elements_of_type(..., include_subtypes=...)` or equivalent); decide per-call-site
   semantics from the D4 verdict table (e.g. do RequirementUsages count as "dropped
   constraints"? do EnumerationUsages count as attributes for entry points?). Record
   the decision table in the adapter docs.
2. **Fix the CONFIRMED-BLIND sites**: `report_dropped_constraints` (extractor.py:108),
   `extract_all_constraints` (constraint_extractor.py:50 — and its false docstring),
   agentic-mbse `level6_architecture.py:602`, `level4_constraints.py:113`, and the
   **Level-3 abstract-`Import` bug** (`level3_dataflow.py:48` — a validator that can
   never fail; also fix its `imported_namespace` guard for MembershipImports).
3. **Zero-found sentinel** on the report (per R1-addition): "scanned N constraint
   usages (M assert, K require), matched 0" replaces silence.
4. **Re-anchor REQ-EXT-09 independently**: hardcoded expected count for catf_mfe (or
   a grep of the fixture source), plus the missing part-usage-owner leg, plus a
   wi014_toy pin that the `assert constraint` at `toy_plant.sysml:51` is reported —
   making Item 1-of-UPSTREAM-FINDINGS' success criterion true for the first time.
5. **Certify `require constraint`** (statically: plain ConstraintUsage under
   RequirementConstraintMembership — visible; add a fixture row + pin to make it
   permanent).
6. **Constraint serialization decision (spec-time)**: constraints are never serialized
   into snapshots (`_deserialize_constraint_info` is dead code) so `generate
   --from-snapshot` can never report them. Recommend: serialize + run the report on
   the from-snapshot path (small; prerequisite for the deferred constraint-execution
   epic and for snapshot-first truthfulness). If deferred, file explicitly.
7. Docs: modeling-assumptions §8 reworded to match reality; EnumerationUsage decision
   pinned by a test on the existing enum-bearing fixtures.

**Out of Scope**:
- Constraint execution (deferred epic — this item makes the drop loud and true).
- Enabling connection/view/case-def extraction (no supported model uses them; the
  decision table records the deliberate choice).

**Success Criteria**:
- [ ] Generating wi014_toy and the fusion-tea snapshot emits the constraint report
  including assert-shaped constraints, with independently-anchored counts.
- [ ] agentic-mbse Level 3 produces a non-empty dependency graph on a fixture with
  imports; a seeded circular-import fixture FAILS it (first time it can).
- [ ] REQ-EXT-09's test fails when the query is deliberately broken (mutation check
  documented in the test).
- [ ] Adapter decision table published; both repos' suites green (R2 pair).

**Required Reading**: discovery register §D4 (verdict table + TYPE_MAP audit) and the
orchestrator's snapshot-path corrections; BACKLOG `[CONSTRAINT-SILENCE]` entry;
`reference/01-extraction.md`; modeling-assumptions §8.

**Deliverables**: `.project/active/subtype-enumeration/{spec,design,plan}.md`;
agentic-mbse companion branch; fixture rows + pins; docs updates.

---

### Item 5: Silent-Failure Hardening — Loud Extraction & Resolution [1.5–2 days]

**Type**: Implementation
**Effort**: 1.5–2 days (spec 2h, design 2h, plan 1h, execute 8–11h) — fit: high (V1–V11
diagnostic pattern is established; D3 gives file:line for every site); lift: medium
(16 sites + sentinel family); risk: medium (new diagnostics on existing corpora can
regress the Item-7-of-prior-epic "clean fixtures generate with zero WARNINGs" property
— triage noise deliberately).
**Dependencies**: Item 1 (fixtures to pin several shapes); parallel with Item 2
otherwise.

**Objective**: A model shape the pipeline cannot handle produces a diagnostic, never a
silent drop, mis-wire, or vanished parameter.

**Positioning (R4 applies in full)**: the 16 D3 findings are static-read verdicts.
This item's spec phase is a **verification pass first**: reproduce each floor finding
with a failing test or live probe (the verification table is a required spec
artifact); check each against the component's reference doc for intended behavior
before calling it a bug; strike or reclassify what doesn't reproduce. Only confirmed
findings proceed to design — and design fixes them by FAMILY at the cleanest choke
point (blind-dispatch fall-throughs; gated-report silences; name-keyed lookup maps;
exception swallows), not site-by-site. Expect the confirmed list to be shorter than
16; that is the protocol working, not scope slippage.

**Scope** (from D3; the verified subset of this floor):
1. **Extraction silences → loud** (D3-1..3, 16): unknown binding-expression type
   (InvocationExpression et al.) warns instead of silently classifying UNBOUND;
   3+-segment chain bindings either parse via `extract_feature_chain_segments` or
   hard-diagnose (never truncate to root); unresolvable references surface in the
   unbound ledger, never vanish; EXPOSE classification/alias-production disagreement
   warns.
2. **The discarded report** (D3-4): stop discarding the usage-extraction warning
   report on the live path; its "usage dropped from pipeline" warnings surface.
3. **Registry/lookup silences** (D3-5, 6): Phase-1a unknown-calc-def gets a warning;
   the snapshot-loader `except: pass` on `usage_type_map` becomes a loud
   skip-with-warning (offline-parity guard).
4. **Wrong-math silences** (D3-8): aggregation `transformed_expression` uses the
   Python operator map or sets `has_unsupported`; `^` never silently XORs.
5. **Name-keyed resolution maps** (D3-7, 10, 11): QN-key the attribute resolution
   map; leaf-name redefinition matches require uniqueness or warn; ambiguous target
   index warns at lookup. (Design may split these to a follow-on if churn is large —
   decide explicitly.)
6. **Sanitize injectivity** (adversarial SC-4): fail-fast when two sibling names
   sanitize to one channel/EP key; `sanitize_name(x).isidentifier()` unit pin
   (leading-digit case fails today — fix the sanitizer).
7. **Non-float entry-point literals** (adversarial SC-5): bool/string/enum-valued
   entry points get a diagnostic or typed pre-fill — never a silent `None`-omission
   (fusion-tea's `wall_type` enum is one hop from this hole).
8. **Pattern-3 zero-found sentinels**: the sites in the register's pattern-3 list get
   "scanned N, matched 0" observability (a summary DEBUG/INFO shape is fine; the
   point is zero-found ≠ silence).
9. Every new diagnostic: fires-on-shape test + silent-on-clean test (R1 addition);
   clean fixtures still generate with zero WARNINGs.
10. Triage residue: whatever spec de-scopes from the D3 hygiene tail is filed as one
    consolidated BACKLOG entry at close (register discipline).

**Out of Scope**:
- Implementing support for the shapes made loud (InvocationExpression execution,
  conditionals — see Deferred; loud rejection is this item's contract).
- The `--smart-regen` preservation fix (D3-14) if design shows it needs its own item —
  decide, don't drop.

**Success Criteria**:
- [ ] Verification table complete: every floor finding CONFIRMED (with its failing
  probe) or RECLASSIFIED (with evidence) in the discovery register — before design.
- [ ] Each CONFIRMED finding's family has one root-cause fix, and a test where the
  bad shape produces its diagnostic (independently anchored) plus a
  silent-on-clean test.
- [ ] All existing baselines byte-identical (diagnostics only — no output change for
  valid models).
- [ ] The D3 register's disposition column is fully discharged (fixed /
  reclassified / split-filed / hygiene-filed).
- [ ] Touched components' reference docs updated in the same change (R4 step 4).

**Required Reading**: discovery register §D3 (all 16 + pattern-3 list); RN-7
(`warning-reconciliation/release-notes.md` — the noise-discipline precedent);
`reference/12-usage-extraction.md`, `reference/10-output-registry.md`.

**Deliverables**: `.project/active/silent-failure-hardening/{spec,design,plan}.md`;
diagnostics + tests; doc updates per touched component.

---

### Item 6: Self-Referential Test Remediation [0.5–1 day]

**Type**: Testing
**Effort**: 0.5–1 day (spec 1h, plan 0.5h, execute 3–5h) — fit: high (mechanical fix
pattern: every flagged test has a correctly-anchored sibling in the same suite); lift:
low; risk: low.
**Dependencies**: None (Track B; REQ-EXT-09 itself is Item 4's).

**Objective**: Every conformance test can fail — the 25 flagged tests get
independently-anchored expectations.

**Scope**:
1. Fix the 7 HIGH (tautological len==len over 1:1 loops; expected-computed-by-
   production-helper) and 10 MEDIUM per the D5 list — hand-transcribed literal
   expectations per known fixture element, on-disk checks where the REQ says "file".
2. Convert `test_localterm_sibling_agg_output` from pass-or-skip to
   pass-or-FAIL.
3. Fix the mis-anchored REQ-REG-02 test (points at the wrong requirement AND
   re-implements the selection rule).
4. LOW tier: judgment call per test — fix where a literal is one line; document the
   sibling-pin reliance otherwise.
5. Add the SC-6 render-contract pins the adversarial pass named (scientific-notation
   normalized form; one positive `sum(...)` render) — cheap, same style of work.
6. A short "how to anchor a conformance expectation" note in the tests README so the
   anti-pattern doesn't regrow (R1 addition is the enforcement; this is the teaching).

**Out of Scope**:
- Behavior changes — if re-anchoring a test EXPOSES a real bug, file/absorb it
  explicitly (likely candidates: none known; D5 verified current behavior matches).
- The matrix-row updates (Item 7 owns the matrix).

**Success Criteria**:
- [ ] All 25 register entries dispositioned; each fixed test demonstrably fails under
  a deliberate production mutation (spot-check three, note in close-out).
  <!-- audit 2026-07-06: all 25 dispositioned ✓; mutation spot-check recorded in close-out
       (3 RED→revert→GREEN) but NOT independently reproduced at audit (pytest gated in stage
       context). Statically corroborated. Left unchecked pending one licensed reproduction. -->
- [x] Suite green, count changes explained (no test deleted without a replacement).
  <!-- audit: orchestrator live gate 2005/4/5; −26 = parametrization reduction + 4 new fns; no fn deleted. -->

**Required Reading**: discovery register §D5 (incl. the cleared-non-findings list —
do not re-flag); `docs/architecture/verification-matrix.md` PASS definition.

**Deliverables**: `.project/active/test-truth/{spec,plan}.md`; re-anchored tests;
tests README note.

---

### Item 7: REQ/Matrix Reconciliation — F2, F4, and the Divergent Rows [1.5–2 days]

**Type**: Implementation / Documentation
**Effort**: 1.5–2 days (spec 2h, design 1.5h, plan 1h, execute 8–10h) — fit: medium
(decisions, not just edits); lift: medium (grows to 2+ days if F4 lands as the
cutover — design decides and may split the cutover into its own item); risk: medium
(F2 touches registry contract prose AND a weakened test; F4 moves either a module 24
skipif-gated tests point at, or the production aggregation path).
**Dependencies**: Items 4–6 ideally land first (their matrix rows move); hard dep:
none.

**Objective**: The verification matrix tells the truth — REQ text, tests, and code
agree everywhere, and the 12 UNTESTED rows are deliberately dispositioned.

**Scope**:
1. **F4 (extended) — an intent-vs-reality decision, per R4 step 1.** This is not a
   dead-code deletion call. Docs 03/04/05 present `resolve_input()` as the *intended*
   architecture with recorded design rationale (doc 03's motivation table:
   consolidated resolver, typed strategies, testable in isolation — vs the "3
   term-specific functions + mutation" it was designed to replace); the code never
   cut over, and docs-scrub deliberately left the prose pending this reconciliation.
   The two legal outcomes: **(a) land the cutover** — honor the documented intent,
   wire `resolve_input()`/`AGG_STRATEGIES` into `graph_builder`'s aggregation path
   (the `test_dual_resolution.py` parity suite is the safety net: 12 tests already
   prove the two implementations agree on the committed corpus), implement or delete
   Strategy D's promised aggregation-EP dedup; or **(b) excise** — delete the module
   AND rewrite doc 03's design rationale so no reader inherits an architecture
   description of code that doesn't exist. Evidence for (a): the intent docs, the
   parity suite, the testability argument. Evidence for (b): zero production callers
   ever materialized, the live path is proven on real corpora, Strategy D is a no-op.
   History (git-verified 2026-07-06): the module and its intended call site were born
   in the same COST-PATTERN commit (`d6c725f`) — the resolver was built, tested (26
   conformance + 20 parity tests), and the final rewire of the factory call sites was
   the one step skipped. It replaced nothing, so nothing broke; production still runs
   the pre-refactor inline logic the parity suite proves equivalent on the corpus.
   **Presumption: land the cutover (a)** — the design rationale was deliberate, doc 24
   defines the structural boundary it honors (post-DFS resolution is consolidatable;
   DFS-time is not), and excising enshrines the less-clean implementation at greater
   doc-surgery cost. The presumption flips to (b) only if design finds a kill: (i)
   parity FAILS when extended over the Item-1 plant fixtures / shapes beyond the
   committed corpus, (ii) Strategy D's promised aggregation-EP dedup turns out to be
   an unwanted behavior change on review, or (iii) the module drifted materially
   behind the live path's UPSTREAM-FINDINGS-era fixes and re-syncing costs more than
   it buys. Cutover preconditions: extend the parity suite over the new fixtures
   BEFORE the swap; implement-or-delete Strategy D explicitly (dedup churns
   params-JSON key sets — reviewed baselines); diff the module against the live
   path's post-COST-PATTERN fixes both directions. Whichever lands: the IR family (7
   rows), DRA-02/04/05, REQ-RES-02/07/08 text, the 24 skipifs, and
   `test_dual_resolution.py` all move consistently in the same change.
2. **F2**: decide the Key_A/Key_F registration contract (REQ-OR-05/06/08 + doc 10 +
   the `instance_attr_to_channel` construction-time dict vs "through typed lookup");
   fix REQ text or code to match; restore REQ-ORCH-04's real phase-order assertion
   (currently weakened to first-call-only); fix the two test docstrings that misstate
   their own bodies.
3. **Divergent-PASS rows** (D7 list): REQ-CA-05, PY-01/03/05, GEN-02, SR-07 (behavioral
   test, not source grep), DM-06/07, GA-07, PGD-08, EXT-09's part-usage leg (Item 4
   may have landed it — verify). Fix test or re-frame REQ per row; no row left pinning
   less than its text.
4. **UNTESTED-12**: convert REQ-CA-08 and REQ-GEN-07 (risky-cheap); REQ-RES-08 via
   Item 1's cross-part fixtures (riskiest row — consumer scoping across all
   resolution paths); rewrite REQ-RES-02 for the real architecture; cross-cite
   RES-01..06; static-check REQ-DM-08; cross-cite GEN-03.
5. **Marker hygiene**: add the missing REQ markers (7 rows); fix the matrix footer
   (33 vs 45 files; the 9 out-of-conformance citations) or re-frame the PASS
   definition honestly.
6. **The 5 xfails decision**: fix the inherited-attr classifier (supertype-namespace
   QN defeats the Step-2b prefix check) or re-frame REQ + xfails as documented
   contract. Argue at spec; the misclassification is loud (EXPOSE_COMPUTED rejection),
   so re-frame is acceptable if the fix doesn't fit the item.
7. **Complete the deep-read sweep** over the ~175 PASS rows discovery triaged but did
   not read, using the D7 heuristics (strong-words REQs, diagnostics, structural
   counts); fix or file what it finds.

**Out of Scope**:
- New feature work surfaced by re-framed REQs (file it).
- The self-referential fixes themselves (Item 6).

**Success Criteria**:
- [ ] F2 and F4 closed by recorded decision; BACKLOG entries retired.
- [ ] Zero divergent-PASS rows from the register remain; sweep-found ones fixed or
  filed with a pointer.
- [ ] UNTESTED count deliberately dispositioned (target: ≤ the rows argued
  untestable-as-written, each with its argument in the matrix).
- [ ] Matrix recount matches row-by-row reality (memory note: recount from rows, not
  the summary block).

**Required Reading**: discovery register §D7; BACKLOG DOCS-SCRUB-F2/F4;
`docs/architecture/verification-matrix.md`; `reference/10-output-registry.md`,
`reference/03/04/05` (the REQ-mirroring prose deliberately left pending this
reconciliation); memory note `verification-matrix-drift-modes`.

**Deliverables**: `.project/active/matrix-truth/{spec,design,plan}.md`; decisions
recorded in docs; matrix updated.

---

### Item 8: Dead Code & Cleanup Debt [1 day]

**Type**: Implementation
**Effort**: 1 day (spec 1h, plan 0.5h, execute 4–6h) — fit: high (every target has a
verified zero-callers or known-bug citation); lift: low; risk: low-medium (the
aggregation-literal fix touches an executable path — byte-identity gate).
**Dependencies**: None (Track B). Schedule before PUSH-DOWN (see Deferred).

**Objective**: The filed cleanup debt and discovery's unfiled residue are cleared in
one reviewed pass.

**Scope**:
1. **DOCS-SCRUB-F1**: delete the two dead templates + verify-then-delete the four
   candidates (`map_sysml_type_to_rootmodel_wrapper`, `get_default_value` (re-frame
   REQ-PGD-06 if removed — coordinate with Item 7), `generate_derived_group_json`
   (still emits null-default keys — the shape Item 7-of-prior-epic corrected),
   `binding_to_entry_point` + its 7 DEPRECATED sites).
2. **DOCS-SCRUB-F3**: the four stale docstrings.
3. **Aggregation-literal dispatch bug** (from Ideas — a bug, not an idea):
   `_walk_aggregation_ast` literal-after-invocation ordering; fix with a
   literal-bearing aggregation fixture row and a byte-identity gate on existing
   corpora; retire the doc-19 known-deviation note (coordinate with Item 10).
4. **Dotted-leaf alias edge**: the cheap unit pin that retires doc 25's "no current
   model triggers this" hedge.
5. **D1 unfiled residue**: two-sanitizer consolidation (F-2), catf-cleanup fallback-EP
   chore (F-3), snapshot `param_groups` type-ignore (F-4), dead `out = subprocess.run`
   (F-5); dead `_deserialize_constraint_info` (unless Item 4 wires it — coordinate);
   dead `_check_semantic_match` (D3).
6. **SC-11 AST-based import rewrite** (D1-F1): assess against the registry
   alias-rewrite no-not-found branch (D3 hygiene); implement if small, else file it
   properly (it is currently filed nowhere despite close-out claims).
7. The 4 vacuous typed-API skipif guards in `test_output_registry.py` (API exists;
   guards never fire — simplify).

**Out of Scope**:
- `resolve_input` excision (Item 7 owns that decision).
- Anything requiring a ComputationGraph rev.

**Success Criteria**:
- [ ] Zero grep hits for each deleted symbol; suite green; ruff/mypy not worse.
- [ ] Aggregation-literal fix: existing corpora byte-identical; new fixture row shows
  the corrected dispatch.
- [ ] Every D1 finding dispositioned (done or properly filed).

**Required Reading**: discovery register §D1/§D2; BACKLOG DOCS-SCRUB-F1/F3;
`reference/19-expression-reconstruction.md` (the known-deviation note to retire).

**Deliverables**: `.project/active/cleanup-debt/{spec,plan}.md`; deletions + fixes +
pins.

---

### Item 9: agentic-mbse Sync — Guidance, Validation, and the Companion Audit [1–1.5 days] ✅

**Type**: Code/Integration + Documentation (agentic-mbse repo)
**Effort**: 1–1.5 days (spec 1.5h, plan 1h, execute 5–8h) — fit: high (Item 12 of the
prior epic is the template, including its traceability-table close-out); lift: medium;
risk: low-medium (cross-repo session sandboxing cost the prior epic round-trips —
plan for a code-side pass in the agentic-mbse repo).
**Dependencies**: Items 1–5 impact lists (accumulates; executes late).

**Objective**: agentic-mbse teaches and checks everything this epic changed; the
cross-repo debt from the prior epic is verified closed, not just recorded.

**Scope**:
1. Execute the accumulated per-item impact lists (R2): plant-value shapes from Items
   1–2 (MODELING_GUIDE + reference fixtures), subtype-aware validation semantics from
   Item 4, new diagnostics from Item 5.
2. **Build the D-F validation warning** (recorded in the prior epic, never built):
   WARN when `attribute :>> attr = <expression>` carries an expression RHS (the
   silently-dropped shape) — with its negative fixture.
3. **Prior-epic residue verification**: confirm the companion PR
   (`upstream-findings-sync`) merged (it was awaiting a human `gh pr create` — check
   and close the loop); C7/C8/F6 backlog items dispositioned; the syside vendor note
   (self-named-binding recursion) filed with Sensmetry or explicitly declined.
4. **SYNC-F3/F4/F5** (P2, filed here): implement or re-file with argument — F5
   (positive unresolvable-warning test) is absorbed by Item 5's fires-on-shape rule;
   F3/F4 get a decision each.
5. **Companion audit** (D3 pointer): `extract_feature_refs` traversal coverage and
   `str(direction)` repr stability — the two agentic-mbse primitives sysml-codegen's
   extraction silences bottom out in.
6. Close-out traceability table (every impact-list row → done/filed), prior-epic
   style.

**Out of Scope**:
- sysml-codegen code changes (they land in their own items).

**Success Criteria**:
- [x] Every impact-list row implemented or filed; traceability table complete.
- [x] New checks each have a negative fixture and catch their trap on the Item-1
  fixtures.
- [x] Prior-epic cross-repo residue (companion PR, C7/C8/F6, vendor note) verified
  closed or explicitly re-filed.

**Required Reading**: discovery register §D4 (agentic-mbse rows) + cross-repo
pointers; prior epic Item 12 + its audit (`validation-sync/audit.md` — the designated
clearing path); `AGENTIC_MBSE_PR_BODY.md`.

**Deliverables**: agentic-mbse `.project/active/pipeline-truth-sync/{spec,plan}.md`;
checks + fixtures + guide updates; close-out table.

---

### Item 10: Docs Refresh & Explainer-Prompt Revision (Epic Close) [0.5–1 day]

**Type**: Documentation
**Effort**: 0.5–1 day (spec 0.5h, plan 0.5h, execute 3–5h) — fit: high (docs-scrub
established the method: fact sheet → verify → matrix recount); lift: low; risk: low.
**Dependencies**: All prior items (last).

**Objective**: The docs-scrub certification still holds at epic close — every doc,
assumption, and matrix row this epic touched is re-verified at post-epic HEAD, and
every retired caveat is actually retired everywhere it appears.

**Scope**:
1. **End-of-epic docs pass**: every reference doc, modeling-assumptions section, and
   verification-matrix row touched by Items 2–8, re-verified against post-epic HEAD
   (fact-sheet method; recount matrix from rows).
2. **Retire the caveats** everywhere they appear (docs, matrix, BACKLOG, fact sheet):
   the V11 10-offender abort, the assert-constraint silence, "four specific cross-part
   shapes" (now broader), F2/F4 divergences, doc-19 known-deviation (if Item 8
   landed), doc-25 dotted-leaf hedge, §8 overclaim (Item 4 rewrote it — verify).
3. **Revise `.project/active/EXPLAINER_PROMPT.md`**: it hard-codes facts this epic
   changed — the `docs-scrub` branch anchor (now merged to main), the entire "Honest
   caveats" section (10 V11 bindings, four shapes, open F2/F4), the cross-part story
   (add the value-resolution mechanism from Item 2), the reading list (add the
   discovery register + this epic's release notes). Gate its execution on Item 3's
   acceptance run being green — the explainer is built from true facts only.
4. Update CURRENT_WORK.md and BACKLOG.md (retire absorbed entries; epic close-out).

**Out of Scope**:
- Building the explainer (its own prompt, its own session — this item only makes the
  prompt true).

**Success Criteria**:
- [ ] A docs-scrub-style audit spot-check (3 docs, matrix recount) passes at post-epic
  HEAD.
- [ ] Zero occurrences of the retired caveats outside historical documents.
- [ ] EXPLAINER_PROMPT.md contains no claim contradicted by post-epic HEAD, and its
  execution gate names the acceptance run.

**Required Reading**: `.project/active/docs-scrub/{fact-sheet,audit}.md` (the method);
`.project/active/EXPLAINER_PROMPT.md`; memory note `verification-matrix-drift-modes`.

**Deliverables**: `.project/active/epic-close-docs/{spec,plan}.md`; doc/matrix
updates; revised EXPLAINER_PROMPT.md; updated CURRENT_WORK/BACKLOG.

---

## Deferred (explicitly not in this epic — argued each way)

- **Constraint execution (SC-1 full epic).** For: fusion-tea's viability gate stays
  harness-side until it lands; Item 4 serializing constraints removes a prerequisite.
  Against: it needs an ADR (boolean-output modules, annotate-vs-halt), no consumer is
  blocked (the harness check works), and this epic's mission is truth-of-what-exists,
  not new execution semantics. **Deferred**; re-weigh after the MFE epic, per the
  prior ruling. Item 4 makes the drop loud and true in the meantime.
- **Supertype-chain template inheritance for plain usages.** For: blocks part of the
  MFE idiom. Against: no current fusion-tea model needs it (D6 confirmed the 10
  offenders don't touch it); it needs a deliberate specialization walk. **Deferred to
  the MFE epic** (standing note from prior Item 4).
- **Function calls / conditionals (InvocationExpression, SelectExpression).** For:
  Item 5 makes their current silent mis-handling loud, which will surface demand.
  Against: whitelist semantics need design; no anchor depends on them. **Deferred**;
  Item 5's loud rejection is the contract until then.
- **EXPOSE_COMPUTED, non-uniform arrays, body-assignment capture, hierarchical
  output.** Unchanged from prior epic — no new evidence moved them. **Deferred.**
- **PUSH-DOWN epic (design ready).** Its Item-6 prerequisite landed, so it is
  unblocked — but this epic's Items 5 and 8 modify the same `extraction/` surfaces
  PUSH-DOWN would move (`expression_utils`, `hierarchy_resolver`). **Sequencing
  ruling: PUSH-DOWN starts after PIPELINE-TRUTH Items 5 and 8 land**, so the moved
  code is born correct and loud. Recorded in BACKLOG.
- **generation-boundary item (In Progress, Step 7.6).** Independent workstream on
  `generation/` imports; low collision risk with this epic (Items 5/8 touch
  extraction/resolution). Coordinate at Item 8's spec if both are active.

---

## Dependencies

**External**:
- syside license (monthly renewal, no expiry pressure) — Items 1, 3 capture/live legs.
- fusion-tea coordination (Item 3 is the vehicle; their report's checklist is the map).
- agentic-mbse coordinated pair for Item 4; accumulated sync in Item 9.

**Item Dependency Graph**:
```
Track A (the headline)                Track B (truth, parallel)
Item 1 (fixtures, license)            Item 4 (subtype enumeration, x-repo pair)
  └─> Item 2 (whole-plant resolution) Item 5 (silent-failure hardening) ← uses Item 1 fixtures
        └─> Item 3 (fusion-tea        Item 6 (self-referential tests)
             acceptance + retirement) Item 8 (cleanup debt)
                                      Item 7 (matrix reconciliation) ← after 4/5/6 rows settle
Item 9 (agentic-mbse sync) ← accumulates from 1–5; executes late
Item 10 (docs + explainer prompt) ← last, after all
```

---

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Item 2's mechanism decision (wiring vs value-fill) reshapes fusion-tea's harness contract | High | Decision at design with the adversarial findings as input; Item 3 re-anchors whichever way; the bridge script is the value-fill oracle |
| Subtype-aware enumeration default flips semantics (RequirementUsage in constraint sweeps, double-processing) | Med | Item 4 decides per-site with a published decision table; opt-in flag, not a global default flip |
| New Item-5 diagnostics create warning noise on real corpora (relitigating Item 7-of-prior-epic) | Med | Fires-on-shape + silent-on-clean is a per-diagnostic success criterion; count-summary style for repetitive classes |
| F4 decided against the documented intent without weighing it (or the cutover destabilizes the proven aggregation path) | Med | R4 step 1: doc-03 rationale is a required design input; the 12-test dual_resolution parity suite gates a cutover; an excise rewrites doc 03's rationale in the same change |
| Discovery findings fixed without reproduction (whack-a-mole; "fixes" for non-bugs) | Med | R4 protocol: per-finding verification table required at Item 5/7 spec; families fixed at choke points, not sites; register updated in place |
| Baseline churn masks a regression during Items 2/5/8 regens | Med | One item's regen at a time; capture scripts only; reviewed diffs (R3) |
| Cross-repo sessions lose permissions (prior-epic pattern) | Med | Item 9 plans an explicit agentic-mbse-repo code-side pass; Item 4 lands as a coordinated pair with its own branch |
| Item 2 exceeds 2 days | Med | Design phase explicitly decides split (mechanism vs fan-out/edge cases); Item 1's fixtures land value independently |

---

## Timeline

**Total Effort**: ~10.5–13.5 days

| Item | Effort | Dependencies |
|------|--------|--------------|
| 1. Plant-value & blind-spot fixtures | 0.5–1 d | None (first, Track A) |
| 2. Whole-plant value resolution | 1.5–2 d | Item 1 |
| 3. fusion-tea acceptance & retirement | 1–1.5 d | Item 2 |
| 4. Subtype enumeration & constraint truth | 1–1.5 d | None (Track B) |
| 5. Silent-failure hardening | 1.5–2 d | Item 1 (soft) |
| 6. Self-referential tests | 0.5–1 d | None |
| 7. Matrix reconciliation | 1.5–2 d | Items 4–6 (soft) |
| 8. Cleanup debt | 1 d | None (before PUSH-DOWN) |
| 9. agentic-mbse sync | 1–1.5 d | Items 1–5 lists |
| 10. Docs & explainer prompt | 0.5–1 d | All (last) |

---

## Source Documents

- `~/1cfe/fusion-tea/work/active/20260706_upstream-fix-verification/report.md`
  (validation report — with the line-74 correction noted in the discovery register)
- `.project/research/20260706_pipeline-truth-discovery.md` (discovery register, D1–D7
  + adversarial, 2026-07-06)
- `.project/backlog/epic_upstream_findings.md` (prior epic + lessons learned)
- `.project/backlog/BACKLOG.md` (CONSTRAINT-SILENCE, DOCS-SCRUB-F*, SYNC-F*, Ideas)
- `docs/architecture/modeling-assumptions.md` + `docs/architecture/reference/` +
  `verification-matrix.md` (scrubbed 2026-07-06)
- `.project/active/docs-scrub/fact-sheet.md`; release notes RN-7/9/10/11
- `.project/active/NEXT_EPIC_PROMPT.md` (the shaping brief this epic answers)

---

## Lessons Learned (Post-Completion)

*Fill in after epic is complete*

---

**Last Updated**: 2026-07-06
**Next Action**: User review of scope and decomposition; then spec Item 1 (fixtures)
and Item 4 (subtype enumeration) — the two no-dependency track heads.
