# Design: Item 7 — REQ/Matrix Reconciliation (F2, F4, Divergent Rows)

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-07-06
**Branch:** pipeline-truth-epic
**Commit:** 6c8957e
**Epic:** PIPELINE-TRUTH, Item 7 (SC-F)

## Overview

Make the verification matrix tell the truth: run the three F4 kill probes and record the
verdict, fix F2's contract text to match the code, dispose every divergent-PASS and
UNTESTED row, reconcile the counts, and decide the 5 xfails. This design records the F4
verdict from evidence the probes produced (all three artifacts under `probes/`).

## Related Artifacts

- **Spec:** `.project/active/matrix-truth/spec.md` (approved post-review, `eee7e7f`)
- **Spec review:** `.project/active/matrix-truth/spec-review.md`
- **Probe artifacts (produced by this design):**
  - `probes/probe_i_extended_parity.py` + `probes/probe_i_run_log.txt`
  - `probes/probe_ii_strategy_d_dedup.py` + `probes/probe_ii_run_log.txt`
  - `probes/probe_iii_module_drift.md`
  - `probes/probe_iv_ep_key_divergence.md` (EP-key divergence evidence, per review M4)
- **Epic:** `.project/backlog/epic_pipeline_truth.md` (Item 7; R1/R4; SC-F)
- **Required Reading:** discovery §D7; `verification-matrix.md`; docs 03/04/05 (F4 intent),
  10 (F2); memory `verification-matrix-drift-modes`, `verify-then-fix-protocol`

---

## Core Concept

The matrix is a **derived artifact that drifted from its source** (the code). Every task in
this item is one shape of the same move: bring a claim back into line with what the code
actually does — by strengthening a test, correcting a text, or recording a decision — and
close the docs loop in the same change so no reader inherits a ghost.

The item has one genuinely open question, F4, and the spec made it answerable: run three
probes that each produce an artifact a reviewer can open, and let the evidence — not the
presumption — pick the verdict. **The probes ran. All three fired no kill.** So the module
(`input_resolver.py`) is not a corpse to excise; it is a parity-validated consolidation that
was never wired to the live path. That distinction drives everything downstream: we keep the
module and tell the truth about its status, rather than deleting it or pretending it is live.

Everything else is bounded reconciliation against a fixed reality: F2's registrations are
corpus-proven (fix the text), the divergent rows each pin less than their text (strengthen
or reframe), the counts are recomputable from rows, and the xfails lock a loud, unreachable
misclassification (reframe + file the fix).

---

## The F4 Verdict — LAND, with the cutover split out

**Verdict: LAND (do not excise). Split the code cutover into its own filed item.**

The presumption was "land the cutover (a)"; it flips to excise only if a probe fires a kill.
No probe fired a kill:

- **Probe (i) — extended parity.** `probe_i_run_log.txt`. The extended suite compares the
  **backtracker DFS** against `resolve_input(AGG_STRATEGIES)` over Item 1's fixtures
  (`plant_values`, `plant_value_shapes`, `spec_chain_twolevel`) — the fixtures the committed
  suite never covered. Result: **0 kills**, over an honestly thin extension: **1 MODULE_OUTPUT
  channel-equality check** (`spec_chain_twolevel`) + **5 entry-point fallback checks**. The
  module's *channel resolution* has not diverged **from the backtracker's** — not, on this
  evidence alone, from `_resolve_aggregation_input_channel` (see the sub-bet in B1 and the
  cutover filing). The load-bearing evidence is the **full** set: the committed 12-test suite
  over catf_mfe/solar_battery **plus** this extension.
- **Probe (ii) — Strategy D dedup.** `probe_ii_run_log.txt`. Computed the aggregation-EP
  key-set diff that *implementing* Strategy D (`DesignAttributeLookup`) would produce against
  the `catf_mfe` and `solar_battery` baselines. Result: **zero key churn on both.** catf_mfe
  has no aggregation surface at all; solar_battery's one leaf-matching term resolves to a
  channel before Strategy D is ever reached. No merge collisions, no consumer-depended key
  collapsed. **Behavior-change review:** implementing Strategy D as promised has no
  observable effect on the corpus — its trigger never co-occurs with a fall-through entry
  point. This argues **delete Strategy D** (a documented no-op with zero live surface), not
  implement it.
- **Probe (iii) — module drift.** `probe_iii_module_drift.md`. The live function
  `_resolve_aggregation_input_channel` (graph_builder.py:1205) is **byte-identical** to its
  COST-PATTERN birth (`d6c725f`); `_build_aggregation_module` unchanged. Zero post-COST-
  PATTERN live-path fixes exist, so none can be absent from the module. Item 8's
  `_walk_aggregation_ast` reorder is extraction-layer (upstream of both paths); Item 5's
  graph_builder change is literal-default propagation (`_find_literal_redefinition`), a
  responsibility the module never mirrored. **No material drift, no kill.**

### Why the cutover splits out (the load-bearing decision)

The probes prove the module's channel resolution matches the **backtracker**. They do **not**
make `resolve_input` a drop-in for the live path, because the live call sites do far more than
the module's fallback:

- The SumTerm/SingletonTerm call sites (graph_builder.py:1437, 1532, 1633) build entry points
  with `_find_literal_redefinition` default propagation, `param_group` classification,
  `DESIGN_ATTRIBUTE` typing, multiplicity EPs, and a SingletonTerm "Try 2" direct-channel
  construction. `resolve_input`'s fallback does none of this — it emits a bare
  `{module_eqn}__{leaf}` entry point.
- The EP *key* differs: live builds `{module_eqn}__{part_usage}_{attr}` (e.g.
  `…site_infra__raw_material_cost__permitting_raw_material_cost`, an input EP); the module's
  leaf-only fallback would build `…__raw_material_cost` — which already exists in the same
  graph as the module's own **output channel**. A naive drop-in would collide an input EP with
  an output channel name and drop the part-usage disambiguator. Captured with the concrete
  coexisting baseline lines in `probes/probe_iv_ep_key_divergence.md` (M4).

So a real cutover is a refactor: reconcile the module's fallback to the live path's richer
one (or move that logic into the module), rewire 3 call sites, and re-capture baselines
byte-identically or as a reviewed capture diff. That exceeds Item 7's 1.5–2 day budget, and
the spec's Open Question explicitly authorizes design to split it "once the both-directions
diff sizes the rewire." It does. **Split.**

### What Item 7 lands for F4 (the atomic, mutually-consistent change)

The [HARD] atomicity requirement's end-state — "no row pins a module the code doesn't call;
no doc describes an architecture the code doesn't have" — is satisfied by reframing to the
**true** state, not by doing the cutover. In one change:

- **IR rows (REQ-IR-01..07):** reframe from "PASS, pins the live resolver" to pinning the
  module as a **backtracker-parity-validated, not-yet-wired** consolidation. **REQ-IR-05
  (matrix:274) and REQ-IR-07 (matrix:276) carry the false live-usage claim in their
  requirement text** ("Aggregation modules SHALL **use** `AGG_STRATEGIES`…", "SumTerm and
  SingletonTerm inputs SHALL **use** `resolve_input()`…") — production runs
  `_resolve_aggregation_input_channel`, which never calls `resolve_input`. **Rewrite both
  texts** to module-capability claims ("`resolve_input` SHALL…"), not live-usage claims — a
  status re-label is not enough (C2, INV-A). Evidence cited is the **committed** parity suite
  (`test_dual_resolution.py`, extended in place at implement — see below), plus the pointer to
  the cutover item. The 22 `test_input_resolver.py` skipifs stay (they test real, correct
  code); their framing stops implying the code is live.
- **REQ-DRA-02/03/04/05, REQ-BT-09:** DRA-03 and BT-09 also cite `test_dual_resolution.py`;
  the suite is **extended in place, not deleted** (LAND keeps it as the safety net), so their
  citations already point at the right file and survive untouched (no re-pointing needed).
  DRA-04 stops claiming a live comparand.
- **Commit the parity extension (M6).** Probe (i)'s logic lands in `test_dual_resolution.py`
  as a **permanent parametrization** over the three Item 1 fixtures — the reframed IR/DRA rows
  must cite a **committed, CI-running** test, never the `.project/` probe script. This is the
  one test edit F4 makes in Item 7 (the spec's atomicity set already names this file as moving).
- **REQ-RES-02:** rewritten to describe the real three-mechanism architecture (backtracker
  DFS for CalcUsage; attribute-resolution-map for FORMULA; `_resolve_aggregation_input_channel`
  for aggregation) — deleting the dead-path name it currently carries.
- **REQ-RES-07/08 text:** corrected to the live consumer-scope derivation.
- **Docs 03/04/05:** rewrite the "intended consolidated architecture" prose to state the
  honest status — the consolidation exists, is parity-validated over the extended corpus, and
  the live-path cutover is filed as `[ITEM7-F4-CUTOVER]` with the three probe artifacts as
  its safety-net evidence. No reader inherits "this is the architecture" when it is not yet.
- **Strategy D:** delete it (probe ii: zero surface — it is a `return None` stub). Deferred to
  the cutover item, which also corrects the stub's own docstring ("included… for future
  extensibility") — a residual ghost Item 7 leaves noted, not fixed (m7).

**Backlog:** retire DOCS-SCRUB-F4; file `[ITEM7-F4-CUTOVER]` carrying, explicitly:

1. **The correct comparand (M3).** The cutover's safety-net parity suite must compare
   `resolve_input(AGG_STRATEGIES)` against **`_resolve_aggregation_input_channel`** — the
   function it replaces — not only the backtracker DFS that probe (i) and the committed suite
   use. Backtracker parity is general-correctness evidence, not parity-with-the-replaced-
   function.
2. **The EP-key reconciliation (M4).** `probes/probe_iv_ep_key_divergence.md` — the concrete
   coexisting-key baseline lines the fallback reconciliation must resolve before rewiring.
3. **Scope:** reconcile `resolve_input`'s fallback to the live richer EP construction, rewire
   the 3 call sites (graph_builder.py:1437, 1532, 1633), re-capture baselines byte-identically,
   delete Strategy D + fix its docstring.

---

## F2 — Fix the text to the code (presumption holds)

**Flip condition NOT met → fix text, not code.** The spec's one design check: does the
construction-time `instance_attr_to_channel` dict genuinely bypass the typed-registry
validation contract? It does not:

- The dict is declared "NOT persisted in registry — exists only during construction"
  (`output_registry_builder.py:161`). It is a build-time helper mapping Key_A-format names to
  canonical channels.
- At Phase 3/4 the dict is consulted only to *resolve* a Key_A name, then the result is
  registered through the guarded `register_alias` (line 279, Phase 3; line 365, Phase 4),
  which warns+skips when the target is not yet in `_canonical`; on a miss it falls back to
  `registry.scoped_lookup` (line 277). The dict **feeds only guarded `register_alias` calls**;
  it does not itself register anything. (Phases 1b/1c do call `registry._canonical.add`
  directly at lines 213/237, but those are not dict-fed and do not bear on F2.)

So the registrations are real and validated. **Fix REQ-OR-05/06/08 text and doc 10's
"Eliminated Key Formats"** to describe the actual state: Phase 1a registers Key_A as an alias
(`register_alias`), Phase 1c registers Key_F as a scoped key (`register_scoped`, line 241),
and the construction-time `instance_attr_to_channel` consult is a build-time helper that
still feeds typed registration (REQ-OR-06's "through typed lookup" is reframed to *resolution-
time* lookups, not the build-time helper).

**Non-negotiable either way:**

- **REQ-ORCH-04 restored — must assert PRESENCE (C1).** The weakened
  `min(phase1_calls) < min(alias_calls)` (`test_orchestrator.py:474`) is vacuous: Phase 1a
  interleaves `register_scoped` (line 183) and `register_alias` (line 186) in one loop, so the
  first-scoped-before-first-alias check passes trivially. The naive "behavioral" alternative —
  `test_all_aliases_target_canonical_channels_solar_battery` iterating `registry._alias` and
  asserting each survivor is canonical — is **the same vacuity in a new costume**:
  `register_alias`'s guard warns+skips any mis-ordered alias, so it never enters `_alias`, so
  the check holds by construction. A phase-order regression passes both.
  **The restoration must assert EXPECTED aliases are PRESENT**, not that survivors are
  canonical. Build a **hand-transcribed, fixture-anchored expected-alias list** (the Item-6
  anchoring rule: the expectation is written independently, never computed by the code under
  test) and assert each expected Key_A alias resolves to its canonical channel on the corpus.
  **The mutation that must turn it red:** swap the Phase-1a order so `register_alias` runs
  before its canonical target is registered — the guard then drops the alias, the expected
  alias vanishes from the registry, and the presence assertion **fails**. A survivors-are-
  canonical check stays green under that mutation; a presence check does not.
- **Two lying docstrings fixed.** `test_output_registry.py:329` ("Key_A … Key_F … NOT in any
  registry") contradicts its own reality — Key_A is an alias and Key_F is scoped-registered.
  The second is the ORCH-04 static-analysis docstring (`test_orchestrator.py:449`, "Phase 1
  registration calls appear before Phase 2/3/4"), which describes a contract the `min<min`
  body does not check. Confirm the exact second docstring at implement against the corrected
  bodies.

**Backlog:** retire DOCS-SCRUB-F2.

---

## Divergent-PASS Rows — disposition (spec §3)

Each row is fixed (strengthen the test or reframe the REQ text) or, if it surfaces feature
work, filed with a matrix pointer. Verify against the **current** row at implement.

- **REQ-EXT-09 (matrix:213):** part-usage leg landed by Item 4 (`test_extractor.py:888-934`,
  anti-pattern-free). Confirm and mark PASS honestly. Done — no action beyond confirm.
- **REQ-PGD-08 (matrix:382):** row moved since D7; now cites `test_matcher_fixes_item7.py` +
  `test_parameter_group_deriver.py`. Re-verify coverage against the **current** row. If
  coverage is genuinely absent → genuine test or reframe (not a marker — you cannot tag a
  test that doesn't pin the claim). This resolves the §3/§5 double-listing: PGD-08 is routed
  through this disposition only, never the "add markers to all 7" path. Decide on fresh
  evidence at implement.
- **The rest** (REQ-CA-05 vacuous-on-empty, REQ-PY-01/03/05 blacklist/rebuilt-map, REQ-GEN-02
  in-memory-only, REQ-SR-07 grep-only, REQ-DM-06/07 tests-something-else, REQ-GA-07
  identifier-grep): each strengthened to pin its text, or the REQ text reframed to what the
  test actually checks. Where strengthening needs a real new behavior, file it. Per-row
  strength decision at implement; the pattern is fixed (no PASS pins less than its text).

---

## UNTESTED-12 — deliberate disposition

The 12 `— | UNTESTED` rows: **CA-08, DM-08, GEN-03, GEN-07, RES-01..08.** Target: ≤ the rows
argued untestable-as-written, each carrying its argument in the matrix.

- **Risky-cheap converts:** REQ-CA-08 (FORMULA-doesn't-resolve-sibling — a static/behavioral
  check), REQ-GEN-07 (registered-in-`__init__` — filesystem check), REQ-GEN-03 (MultiOutput
  schema — cross-cite), REQ-DM-08 (NewType wrappers — static check).
- **Cross-citation discharges:** RES-01/03/04/05/06 discharge by citing existing component
  tests that already pin the claim (resolution-completeness, factory-return-shape, canonical-
  channel, orchestrator-sequence, binding-source-of-truth).
- **REQ-RES-02:** rewritten for the real architecture (see F4), then cross-cited.
- **REQ-RES-07/08:** RES-08 is the riskiest (cross-cutting scoping); Item 1's cross-part
  fixtures are now substrate. Convert with an independently-anchored expectation (R1 ban).
- Any row that stays UNTESTED carries a one-line argument for why, in the matrix.

---

## Marker Hygiene, Counts, and the 5 Xfails

**Six missing row→test markers** (BASE-05, BT-11, CA-10, LVP-09, OR-09, VBR-11): the matrix
test-file cells are populated; add the `# REQ-*` tag in the **test source** the traceability
generator greps. **PGD-08 is excluded** (routed through §3). Verify each tag lands on a test
that actually pins the claim.

**Count reconciliation** (derived-last, per memory `verification-matrix-drift-modes`):

- Recount from rows: 249 REQ rows = 236 PASS + 12 UNTESTED + 1 PENDING (REQ-PGD-06,
  matrix:380). The summary block (248) omits the PENDING row. Regenerate summary to match
  row reality after all dispositions land.
- Footer "33 test files" vs the `tests/conformance/test_*.py` count (**59 today** — the design's
  own earlier "57" already drifted, which is exactly the point: recount at implement, do not
  carry a hand-count) vs index "54 distinct cited": pick one honest definition. Some cited
  files live outside `tests/conformance/`. Either correct the count or reframe the PASS
  definition to admit cited-outside-conformance files. State the definition next to the number.
- **REQ-PGD-06 (matrix:380):** Item 8 deleted `get_default_value` (verified: 0 hits in `src/`
  and `tests/`); pinning tests gone. Re-frame or retire the PASS row and confirm PGD-08's
  `get_default_value` mention (doc-17) was cleared. **REQ-AST-10** (Item 8, pinned by
  `test_agg_literal_dispatch.py`) is a legitimate new row — do not treat as orphan.

**The xfails — RE-FRAME (confirmed).** These are **one parametrized `pytest.xfail` site**
(`test_computed_attributes.py:787`) producing N xfailed cases, not 5 distinct markers — so the
contract to document is one, not five. It xfails an inherited-attr classified EXPOSE_COMPUTED
where FORMULA is correct (a supertype-namespace QN defeats the Step-2b prefix check). The
misclassification produces a **loud** EXPOSE_COMPUTED rejection (not silent wrong output), no
fusion-tea model hits it, and the classifier fix is out of proportion to a matrix-truth item.
Re-frame the REQ + document the one parametrized xfail contract as known; **file the classifier
fix as its own backlog item** with a matrix pointer.

---

## The ~175-Row Sweep — execution shape (leashed)

Runs at implement, not design. Operationalized heuristics — a row qualifies for deep-read if:

- **Strong word:** text contains SHALL / ALL / every / never / exactly, OR
- **Diagnostic:** asserts a warning/error fires on a shape, OR
- **Structural count:** asserts a numeric/structural count.

**Stopping rule:** sweep until EITHER the qualifying list is exhausted OR 0 new findings in
40 consecutive rows after the first 60 examined. Whatever stays unswept is **named in the
close-out with its count** (register discipline — silent truncation reads as "swept
everything"). Findings are fixed or filed with a matrix pointer.

---

## Item-5 Doc-Staleness Fold-in

The handoff asks which of docs 01/10/12/13/14/16/17/23/27 Item 5's changes made stale.
**Finding: Item 5 updated its own directly-affected docs (08/09/11/19) and the candidate list
is largely already reconciled.** Spot-checks:

- **doc 10 (output-registry):** already describes the D5 alias-collision demotion (per-line
  DEBUG + one WARNING count-summary), REQ-OR-09, `_alias_collisions`,
  `alias_collision_count`. Not stale on Item 5 grounds. (It IS the F2 target — corrected there.)
- **doc 01 (extraction):** already carries the full REQ-EXT-09 elaboration (calc-def/part-def/
  part-usage owners, INFO/WARN). Not stale.
- **doc 13 (aggregation-scoping):** already has the zero-scoped-modules WARNING (REQ-AS-08).
  Not obviously stale on Item 5's INV-3/non-float changes; verify at implement.

**Implement-time step (bounded):** verify docs 12/14/16/17/23/27 against Item 5's landed
behavior changes (INV-3 require-unique-or-warn, INV-5 EP-key uniqueness, hazard-scoped
non-float EP warn, Family-1/2 dispatch/sentinels). Touch only where text contradicts code.
Most were not behaviorally touched by Item 5; this is a check, not a rewrite pass.

---

## Key Bets

- **B1.** The three probes' verdicts are the real correctness signal for F4. *If false → we
  land a cutover (later) on a module that silently mis-wires a shape the corpus doesn't
  cover.* Mitigated: probe (i) enumerates Item 1's fixtures (no open-ended hole).
  **Hidden sub-bet (M3):** *parity against the backtracker DFS is an adequate proxy for parity
  against `_resolve_aggregation_input_channel`, the function the cutover actually replaces.*
  For the LAND verdict this is safe (LAND keeps the module unwired). But it is unproven, so
  `[ITEM7-F4-CUTOVER]`'s own gate must re-run parity against `_resolve_aggregation_input_channel`
  directly — stated in the filing, not assumed here.
- **B2.** `resolve_input`'s fallback diverging from the live path's richer fallback is the
  true cost that makes the cutover a refactor. *If false (fallbacks are equivalent) → the
  cutover is a trivial 3-line rewire and should stay in Item 7.* Refuted directly: the EP-key
  format differs and both keys coexist in the baseline (baseline-collapse risk shown).
- **B3.** The `instance_attr_to_channel` dict feeds only guarded `register_alias` calls rather
  than bypassing the typed contract. *If false → F2 flips to a code fix.* Refuted by reading
  the builder: helper is build-time, its results register through guarded `register_alias`.
- **B4.** The matrix's derived numbers can be regenerated from row reality. *If false → the
  count reconciliation chases a moving target.* Mitigated: recount from rows last, per the
  memory note.

## Key Decisions

- **D1.** LAND the F4 verdict; **split** the code cutover into `[ITEM7-F4-CUTOVER]`. *Rejected:
  excise (probes fired no kill — the module is validated, not dead; excising enshrines the
  less-clean inline path at greater doc-surgery cost). Rejected: full cutover inside Item 7
  (fallback refactor + baseline re-capture exceeds the 1.5–2 day budget; spec authorizes the
  split).* 
- **D2.** F2 fixes text to code. *Rejected: fix the code (flip condition unmet — the
  construction-time dict does not bypass the typed-registry contract).* 
- **D3.** ORCH-04 restored via a **presence** assertion — a fixture-anchored expected-alias
  list; a dropped-alias regression makes an expected alias vanish and fails the test.
  *Rejected: the static `min<min` check (Phase-1a interleave defeats it) AND the survivors-
  are-canonical behavioral check (the guard drops mis-ordered aliases before they are seen, so
  it holds by construction — vacuous in a new costume).* 
- **D4.** 5 xfails re-framed + classifier fix filed. *Rejected: fix the classifier now (loud
  not silent, no model hits it, disproportionate to a matrix-truth item).* 
- **D5.** Strategy D deletion rides the cutover item, not Item 7. *Rejected: delete in Item 7
  (it touches the module `resolve_input` iterates; cleaner to bundle with the wiring change
  that gives the module a live consumer).* 

## Required Invariants

- **INV-A.** After Item 7, no PASS row **text** asserts live usage of unwired code — including
  REQ-IR-05/07, whose "SHALL use `resolve_input`" wording is rewritten to a capability claim.
  The code does not call `resolve_input` on the live path until the cutover item.
- **INV-B.** No PASS row pins less than its text; every UNTESTED row carries its argument.
- **INV-C.** Summary/footer/index counts reconcile to the row-by-row recount (249 = 236 + 12
  + 1, updated as dispositions land).
- **INV-D.** Every code touch (ORCH-04 assertion, any F2 test edit) keeps baselines
  byte-identical or lands as a reviewed capture diff. ruff/mypy not worse than 21/109.
- **INV-E.** No re-anchored test computes its own expectation (R1 anti-pattern ban).

## Non-Goals

- The F4 code cutover itself (filed as `[ITEM7-F4-CUTOVER]`).
- The inherited-attr classifier fix behind the 5 xfails (filed separately).
- Item 6's self-referential test-body re-anchoring; Item 4's constraint serialization; Item
  8's other dead-symbol deletions.
- Strategy D as a *new* capability (implement-or-delete only; probe ii → delete).

## Potential Risks

- **Items 2/5 churn the IR/RES/LVP rows** while Item 7 runs. *Mitigation:* re-verify the
  divergent/untested lists at implement start (spec [INFERRED]); note which rows are theirs.
- **The split reads as "F4 not finished."** *Mitigation:* the reframed rows + docs 03/04/05 +
  the filed cutover item with probe artifacts make the state explicit and honest — the matrix
  stops lying, which is Item 7's actual charter.
- **Count definition churn** (33/57/54). *Mitigation:* pick one definition, state it beside
  the number, regenerate derived counts last.

## Integration Strategy

This item edits the matrix, docs 03/04/05/10, and a small set of test files (ORCH-04
assertion, 2 docstrings, marker tags, UNTESTED converts). It complements — does not replace —
the code paths. The one filed follow-on (`[ITEM7-F4-CUTOVER]`) carries the executable change.
The tree stays clean for Item 2's implement (queued next): probe artifacts stay uncommitted
under `probes/` for the orchestrator; no production/test edits land at design.

## Validation Approach

- **Probes:** all three ran; artifacts under `probes/` (parity: 1 MO + 5 EP checks, 0 kills;
  dedup 0-churn; drift 0) + the M4 EP-key evidence artifact.
- **Suite green:** full `pytest` after implement; baselines byte-identical or reviewed diff.
- **Recount:** row-by-row recount matches regenerated summary/footer/index.
- **Register:** R4 verification table produced (finding → probe → CONFIRMED/NOT-REPRODUCED/
  RECLASSIFIED); discovery register updated in place for F2/F4/divergent findings.

## Next-Stage Handoff

- **Fixed:** the F4 verdict (LAND + split); F2 direction (fix text); ORCH-04 behavioral
  restoration; xfail re-frame; the sweep leash; the count-recount method.
- **Open at implement:** per-row divergent/UNTESTED strength decisions on fresh evidence;
  PGD-08 coverage verdict; the footer count definition; the second lying docstring's exact
  identity; docs 12/14/16/17/23/27 staleness check.
- **De-risk first:** re-verify the divergent/UNTESTED lists against the current matrix (Items
  2/5 may have moved rows) before touching anything.

---

## Appendix A — Probe command reference

```
PYTHONPATH=. uv run python .project/active/matrix-truth/probes/probe_i_extended_parity.py
PYTHONPATH=. uv run python .project/active/matrix-truth/probes/probe_ii_strategy_d_dedup.py
# probe_iii is a git-archaeology writeup: probes/probe_iii_module_drift.md
```

## Appendix B — F4 consequence-set row inventory (matrix line refs)

REQ-IR-01..07 (270–276; IR-05 at 274 and IR-07 at 276 get **text** rewrites, C2);
REQ-DRA-02 (165), -03 (166), -04 (167), -05 (168); REQ-BT-09 (120);
REQ-RES-02 (447), -07 (452), -08 (453). 22 skipifs in `test_input_resolver.py` stay.
`test_dual_resolution.py` extended **in place** — DRA-03/BT-09 already cite it, no re-pointing.

---
Next Step: After approval → `/_my_plan` or `/_my_implement`.
