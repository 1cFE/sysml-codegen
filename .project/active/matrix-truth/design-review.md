# Design Review: Item 7 — REQ/Matrix Reconciliation (F2, F4, Divergent Rows)

**Design:** `.project/active/matrix-truth/design.md`
**Spec:** `.project/active/matrix-truth/spec.md`
**Review File:** `.project/active/matrix-truth/design-review.md`
**Date:** 2026-07-06

---

## Fundamental Assessment

**Sound.** The approach is right and appropriately lightweight for a matrix-truth item: mostly
documentation reconciliation, one test-assertion restoration, a few row re-frames, and one filed
follow-on. No over-engineering — the design does not invent abstractions, it removes ghosts.

The F4 posture is correct. The three probes ran, none fired a kill, so the presumption (LAND)
holds by the spec's own decision rule. The split is authorized by the spec once the both-directions
diff sizes the rewire past budget, and it does (fallback refactor + baseline re-capture). I
independently re-verified the load-bearing evidence and it mostly holds:

- **Probe (iii) git archaeology — CONFIRMED.** Exactly two commits touched `graph_builder.py`
  since `d6c725f` (21273b5, 89e6f80); `_resolve_aggregation_input_channel` is byte-identical
  (114 lines; the design says 115 — an off-by-one, trivial); `_build_aggregation_module`
  unchanged; `d6c725f` is genuinely the birth commit of `input_resolver.py`; 21273b5 touched only
  `_find_literal_redefinition` (literal-default propagation, not channel resolution). No drift.
- **Count recount — CONFIRMED.** 249 REQ rows = 236 PASS + 12 UNTESTED + 1 PENDING. The 12
  UNTESTED rows match the design's list exactly (CA-08, DM-08, GEN-03, GEN-07, RES-01..08).
- **B2 EP-key divergence — CONFIRMED REAL.** Both keys the design names coexist in
  `tests/fixtures/baseline_outputs/solar_battery/computation_graph.json`:
  `…site_infra__raw_material_cost__permitting_raw_material_cost` (live format) and
  `…site_infra__raw_material_cost__raw_material_cost` (module/leaf format). A naive drop-in would
  collapse them. The split is genuinely justified.
- **F2 direction — CONFIRMED.** The `instance_attr_to_channel` dict feeds only guarded
  `register_alias` calls (Phase 3 line 279, Phase 4 line 365). The flip condition is genuinely
  unmet; fix-text-to-code is right.

So this is **not a Rework**. Two findings below are Critical because, if left as written, they
reproduce the exact failure this item exists to kill — a green row that pins nothing, and a PASS
whose text still lies. The rest are Major/Minor sharpenings. Proceeding to the dimensional review.

---

## Dimensional Review

### 1. Spec Compliance
**Assessment:** Concerns

Every spec requirement has a design element, and the [HARD] items are addressed: R4 protocol,
F4 atomicity, F2 fix-text-to-code + ORCH-04 restoration + two docstrings, the leashed sweep,
PGD-06/AST-10, byte-identity, the R1 ban. The consequence set is complete (DRA-03 and BT-09
included — I confirmed both cite `test_dual_resolution.py` at matrix:166 and matrix:120).

The concern is **atomicity honesty**, two places (Critical #1 and #2 below):

- The [HARD] atomicity end-state is "no row pins a module the code doesn't call; no doc describes
  an architecture the code doesn't have." The design satisfies this by *reframe*, which is a
  legitimate reading — but the reframe as described re-labels status/framing without committing to
  rewrite the two IR-row **texts** that assert live usage. REQ-IR-05 (matrix:274) and REQ-IR-07
  (matrix:276) read "Aggregation modules SHALL **use** `AGG_STRATEGIES`…" and "SumTerm and
  SingletonTerm inputs SHALL **use** `resolve_input()`…". Those are false live-path claims
  (production runs `_resolve_aggregation_input_channel`, which never calls `resolve_input`). A
  status re-label leaves the text lying and violates INV-A.

### 2. Pattern Consistency
**Assessment:** Pass

The design follows the codebase's established discipline: derived counts recomputed last (per the
`verification-matrix-drift-modes` memory), R4 verify-then-fix, byte-identity gate, R1 anti-pattern
ban. The ORCH-04 restoration reuses an existing behavioral test rather than inventing a new
pattern — the right instinct, though the specific test it reuses is too weak (Critical #1).

### 3. Abstraction Quality
**Assessment:** Pass

No new abstractions introduced. The filed `[ITEM7-F4-CUTOVER]` item is the correct boundary — it
carries the executable change and its safety-net evidence, keeping Item 7 to reconciliation.

### 4. Duplication Avoidance
**Assessment:** Pass

Keeping the module (not excising) avoids re-enshrining the inline path; extending the parity suite
rather than forking it avoids a parallel test structure. Good.

### 5. Data Structure Clarity
**Assessment:** Concerns

One evidence-traceability gap (Major #4): the cutover-divergence rationale (B2) rests on the
baseline JSON, but no probe artifact captures it. The concrete key pair is real (I verified it),
but a person picking up the cutover item would have to re-derive that both keys coexist. The
filing should point at the two coexisting keys in
`tests/fixtures/baseline_outputs/solar_battery/computation_graph.json`, not just assert them in
prose.

### 6. Route Safety
**Assessment:** Concerns

The F4 verdict's evidence path has one indirection the design doesn't flag (Major #3): probe (i)
and the committed parity suite compare `resolve_input` against the **backtracker DFS**, not against
`_resolve_aggregation_input_channel` — the function the cutover would actually replace. For the
LAND verdict this is safe (LAND keeps the module unwired). But the design's line 64 ("not diverged
from the live path's correctness") overstates it, and the cutover filing must name the correct
comparand or the eventual cutover ships its safety net against the wrong function.

### 7. Bets & Decisions Integrity
**Assessment:** Concerns

The bets are genuine claims about reality, each with an "if false" — good form. B2 and B3 I
confirmed true against the code/baseline. B1 ("the three probes are the real correctness signal")
is the load-bearing bet, and it has a **hidden sub-bet the design doesn't state**: *that parity
against the backtracker is an adequate proxy for parity against the live aggregation function.*
That proxy is stated nowhere and is the thing a cutover would actually depend on (Major #3).

D3 (ORCH-04 via the behavioral assertion) is presented as "the strongest honest restoration." It
is not — the chosen assertion is vacuous against the runtime guard (Critical #1). The decision
records the right *goal* (pin the real contract) but picks a check that doesn't pin it.

### 8. Reader Comprehension
**Assessment:** Pass

The design reads well. Core Concept states the model plainly (the matrix is a derived artifact that
drifted), the F4 section leads with the verdict then the mechanism, and the split rationale is
concrete. The probe evidence is cited by name. No jargon wall. The one place a reader could be
misled is the bare "100% parity" headline (Major #5), which is a precision issue, not a voice one.

---

## Issues by Severity

### Critical (must address before implementation)

- **[C1] The ORCH-04 behavioral restoration is vacuous against the guard.** — Dim 2/7
- **[C2] REQ-IR-05 and REQ-IR-07 texts assert live usage; reframe must rewrite the text.** — Dim 1

### Major (should address)

- **[M3] Probe (i) validates parity against the backtracker DFS, not against
  `_resolve_aggregation_input_channel` — the cutover's real comparand.** — Dim 6/7
- **[M4] Cutover-divergence evidence (B2) lives only in prose; no probe artifact captures it.** — Dim 5
- **[M5] "100% parity" overstates thin coverage — the extended corpus exercised MODULE_OUTPUT
  channel-equality exactly once.** — Dim 8
- **[M6] The reframed IR rows cite probe (i); the design must state that implement commits the
  probe-(i) extension into `test_dual_resolution.py` (a durable pin), not leave it uncommitted.** — Dim 6

### Minor (consider)

- **[m7] Strategy D's disposition is sound, but its own docstring is left as a residual ghost.**
- **[m8] F2 registry-guard evidence slightly overclaims (direct `_canonical.add` writes exist).**
- **[m9] The design's own cited counts are already drifting (57 conformance files → 59 today; "5
  xfails" is one parametrized `pytest.xfail` site).**
- **[m10] Appendix B "re-pointed at the extended file" is a misnomer if the extension lands in place.**

---

## Detail — the numbered must-fix list

### [C1] The ORCH-04 behavioral restoration is vacuous against the guard

**What the design says (D3, lines 162-168, 311-313):** restore ORCH-04 via "the **behavioral**
form (build the registry on the corpus; assert no alias ever targets an unregistered channel),
which `test_all_aliases_target_canonical_channels_solar_battery` already models… the strongest
honest restoration."

**Why it fails.** That test (`test_orchestrator.py:495-500`) does:

```python
for alias_key, channel in registry._alias.items():
    assert channel in canonical_set
```

It iterates the aliases that **survived** into `_alias`. But `register_alias`'s guard warns+skips
any alias whose target is not yet in `_canonical` (the design itself states this at line 146). So a
mis-ordered alias — the exact ORCH-04 phase-order violation — never enters `_alias`; it is dropped
silently. The assertion then holds **by construction**. A mutation that registered Phase-1a aliases
before their canonical targets would pass this test just as trivially as it passed `min<min`. It is
the same vacuity in a new costume — and shipping a green-but-vacuous check is precisely the failure
Item 7 exists to kill.

**The one mutation it does catch** is "someone deletes the guard so bad aliases get stored" — weak,
and not the phase-order contract.

**Fix.** The restored assertion must verify **expected aliases are PRESENT**, not just that
survivors are canonical. Assert a count (`len(registry._alias) == expected` for the corpus) or that
specific known Key_A aliases resolve to their canonical channels — something a dropped-alias
regression fails. Pin presence, not the tautology.

### [C2] REQ-IR-05 and REQ-IR-07 texts assert live usage — reframe must rewrite the text

**Current rows.** REQ-IR-05 (matrix:274): "Aggregation modules SHALL **use** `AGG_STRATEGIES`
with `ChainRedefinitionFollow` at position…". REQ-IR-07 (matrix:276): "Aggregation SumTerm and
SingletonTerm inputs SHALL **use** `resolve_input()` with `AGG_STRATEGIES`." Both are claims that
the **live** aggregation modules use the module — which is false.

**The design's reframe (lines 112-114)** describes changing what the rows *pin* ("parity-validated,
not-yet-wired consolidation") but does not call out that IR-05/07 **requirement text** itself
asserts live usage and must change. Contrast RES-02, where the design *does* explicitly say
"rewritten… deleting the dead-path name it currently carries" (line 120). IR-05/07 need the same
explicit text rewrite (to module-capability claims: "`resolve_input` SHALL…", not "aggregation
modules SHALL use `resolve_input`"). Otherwise a status re-label leaves the text lying and violates
INV-A. Name IR-05 and IR-07 specifically in the reframe.

### [M3] Probe (i) compares against the backtracker, not the function the cutover replaces

Probe (i) (`probe_i_extended_parity.py:62-97`) iterates `result.binding_resolutions` — the
**CalcUsage backtracker DFS** — and compares `resolve_input` to it. The committed
`test_dual_resolution.py` does the same. But the live path `resolve_input(AGG_STRATEGIES)` is meant
to replace is `_resolve_aggregation_input_channel` (probe iii names it as the mirror target).
Parity-with-the-backtracker is evidence of general channel-resolution correctness; it is **not**
parity-with-the-replaced-function. Consequences:

- Design line 64 ("not diverged from the live path's correctness") should read "not diverged from
  the backtracker's channel resolution."
- The IR reframe should say "parity-validated against the backtracker," not "against the live path."
- **[ITEM7-F4-CUTOVER] must specify** its safety-net parity suite compares against
  `_resolve_aggregation_input_channel`, or the cutover validates against the wrong comparand.

This is also the hidden sub-bet under B1 — surface it as a stated bet.

### [M4] The cutover-divergence evidence lives only in prose

B2 and the split rest on "both keys already exist in the solar_battery baseline" (line 96). I
verified this is **true** — both keys are in `tests/fixtures/baseline_outputs/solar_battery/
computation_graph.json`. But none of the three probe artifacts captures it: probe (ii)'s log shows
only the module-format key. For the filing to be "executable without re-discovery," capture the
concrete coexisting-key pair as a named pointer into that baseline file, not just the hand-built
example in prose.

### [M5] "100% parity" overstates thin coverage

`probe_i_run_log.txt` totals, across all three extended fixtures: **one** MODULE_OUTPUT
channel-equality comparison (`spec_chain_twolevel: mo_verified=1`) and 5 entry-point fallback
checks. The EP checks pass if `resolve_input` returns entry_point **or** module_output (probe
lines 92-97) — a weak bar ("strictly more capable, not a divergence"). The parity suite's
load-bearing check is MODULE_OUTPUT channel agreement, and the extended corpus exercised it once.
"100% parity, 0 kills" is literally true but reads as broad coverage. State the actual counts
(1 MO + 5 EP over the extension) and anchor the IR reframe on the **full** evidence set — the
committed 12-test suite over catf_mfe/solar_battery **plus** the extension — not probe (i) alone.

### [M6] Commit the probe-(i) extension, or the reframe cites a throwaway script

Integration Strategy (line 354) keeps probes uncommitted under `.project/` and says no test edits
land at design. The IR reframe cites "the extended parity suite (probe i) as the evidence" (line
114), and B1 says "the cutover item re-runs the extended suite as its safety net" — which only
works if the suite is committed. The IR rows keep their committed skipif pins (so they are not
unpinned), but the *parity* evidence they cite would be an uncommitted script that never runs in
CI. State explicitly that **implement commits the probe-(i) parity logic into
`test_dual_resolution.py`** (the durable safety net the spec's atomicity set already names as
moving), so the reframed rows cite a running test, not a `.project/` artifact.

### [m7] Strategy D disposition is sound; its docstring is a residual ghost

Probe (ii) is **not vacuous** — it enumerated every agg term, the simulation faithfully mirrors the
documented Strategy-D intent (leaf → design-attr QN at fallthrough, per the stub docstring at
`input_resolver.py:200-213`), and it genuinely shows the trigger fires on 0 terms. "Delete" is
well-supported, reinforced by the code fact that `DesignAttributeLookup` is a `return None` stub
(zero live surface independent of corpus). Deferring the deletion to the cutover item (D5) is
defensible. But Item 7 rewrites docs 03/04/05 to the honest status while leaving the stub's own
docstring ("included in AGG_STRATEGIES for future extensibility and to document the design intent")
in the code — a small ghost. Add a one-line doc-comment marking it a probe-proven no-op, or note
in the filing that the stub's docstring is corrected by the cutover item.

### [m8] F2 registry-guard evidence slightly overclaims

B3 says "Every channel [the dict] holds was already registered via the typed
`register_scoped`/`register_alias` methods." The dict specifically feeds only guarded
`register_alias` calls (verified) — F2's conclusion holds. But the broader implication that all
registrations go through guarded typed methods is not literally true: Phase 1b
(`output_registry_builder.py:213`) and Phase 1c (line 237) call `registry._canonical.add(canonical)`
directly. Not dict-fed, doesn't flip F2. Tighten the phrasing to "the dict feeds only guarded
`register_alias` calls."

### [m9] The design's own cited counts are already drifting

The design cites "57 in `tests/conformance/`" (line 232); today `ls test_*.py` is **59**. This
*reinforces* the design's own method (pick one definition, recount at implement) — but the design
carries a stale number while making that point. Also, "the 5 xfails" is one parametrized
`pytest.xfail` site (`test_computed_attributes.py:787`) producing N xfailed cases, not 5 distinct
markers. "Document the xfails as a known contract" means documenting one parametrized contract —
state it that way so implement doesn't hunt for five.

### [m10] Appendix B "re-pointed at the extended file" is a misnomer

If `test_dual_resolution.py` is extended **in place** (Appendix B: "extended (not deleted)"), then
DRA-03/BT-09 already cite it and need no re-pointing (design line 117 says "re-pointed at the
extended file"). Clarify to avoid implying a citation move that doesn't happen.

---

## Recommendations

1. **[C1]** Replace the vacuous end-state assertion with a presence/count check that a
   dropped-alias regression actually fails. This is the single most important fix — it is the item's
   own charter turned on itself.
2. **[C2]** Name REQ-IR-05 and REQ-IR-07 in the reframe and rewrite their texts from "aggregation
   modules SHALL use `resolve_input`" to module-capability claims.
3. **[M3, M6]** In one pass: correct "live path" → "backtracker" in the IR framing; state that
   implement commits the probe-(i) extension into `test_dual_resolution.py`; and specify the cutover
   filing's parity suite compares against `_resolve_aggregation_input_channel`.
4. **[M4, M5]** Make the F4 evidence honest: state probe (i)'s real case counts (1 MO + 5 EP), and
   point the cutover filing at the concrete coexisting-key pair in the solar_battery baseline JSON.
5. **[m7–m10]** Housekeeping: doc-comment or file Strategy D's stub docstring; tighten the F2
   guard phrasing; drop/annotate the stale 57 and "5 xfails" numbers; fix the Appendix B wording.

---

## Resolutions

*(To be filled during Stage 4 as the user resolves each issue. The design agent reads this section
to incorporate the review; the reviewer does not edit `design.md`.)*

- **[C1]**
- **[C2]**
- **[M3]**
- **[M4]**
- **[M5]**
- **[M6]**
- **[m7]** / **[m8]** / **[m9]** / **[m10]**

---

**Overall:** **Revise.** The approach is sound, the F4 verdict is correctly reached (no kill →
LAND), the split is genuinely justified (B2 confirmed against the baseline), and the git/count
evidence holds. It is not Approve-ready because two Critical findings reproduce the item's own
target failure — a restored assertion that pins nothing (C1) and a PASS whose text still asserts
live usage (C2) — plus four Major precision/evidence gaps in the F4 verdict's chain. All are
targeted edits; none touch the design's direction.

**Next Steps:** Record resolutions above, then re-run `/_my_design` (or return to the design-agent
session) and point it at this review to incorporate. The reviewer does not edit the design.
