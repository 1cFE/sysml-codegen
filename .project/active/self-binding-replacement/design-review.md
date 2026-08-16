# Design Review: Self-Binding Replacement (rev 2, re-reviewed against HEAD)

**Design:** `.project/active/self-binding-replacement/design.md` (rev 2, written at `7e95285`)
**Spec:** `.project/active/self-binding-replacement/spec.md` (rev 5, 2026-08-16)
**Review File:** `.project/active/self-binding-replacement/design-review.md`
**Date:** 2026-08-16
**Prior review:** `design-review-20260815-rev1.md` (rev-1 Revise verdict, six must-fix; its
resolutions live in the design's Revision Record, which still cites the old filename — repoint on
revision). This is a fresh re-review: the design has not changed since rev 2, but the ground under
it has.

---

## The Point

A modelled value bound as `in availability = availability` never reaches the calculation — the name
resolves to the calculation's own input, so the calculation computes on a default and returns a
confident wrong number. That negates the product promise (`P-001`: vary parameters freely, trust
the viability answer). The owner's obligation, verbatim and count-free (epic `:71-78`): know the
right pattern for each situation, document it, fix the models to use it, and detect `in R = R`.
This item is that obligation: one authoritative teaching document, the rule pushed to every human
and agent surface, the 15 fusion-tea sites migrated with a mechanical bounded-diff proof, a
mutation spine proving arrival at every and only the bound consumers, and a one-run stellarator
triage.

## Fundamental Assessment

**Fail at Stage 0 — but on staleness, not on architecture. Verdict: Rework, and the rework is one
bounded axis.**

The product-lens gate returned **BLOCKED** on two owner-grade findings (`design-F8`, `design-F9` in
`product-lens.md`, 2026-08-16 design block), and structural smell 7 (an invariant changed owners
without the design saying so) fired. Under this review's own rules, either alone controls the
verdict; detailed dimensional review is skipped.

What happened, plainly: the design was finalized one step before its own central open question was
answered. Its D-6 section teaches owner qualification as a **two-step positional search**, and its
D11 decision parks all 13 published qualified examples on a "pending spike addendum." The addendum
then landed, found the qualifier was being destroyed by our own resolver, the owner spun that out
as the `qualified-reference-occurrence-anchoring` item, and the repair shipped (`98970c9`,
2026-08-15). At today's HEAD:

- A one-segment reference whose leaf is **usage-owned** anchors its exact owner
  (`_resolve_direct_reference`, `elaborate.py:2294-2357`). The positional rule no longer runs for
  that lane — which is the lane all 13 published D-6 examples use.
- The positional two-step rule **survives** for definition-, package-, enum- and calc-owned leaves
  (`_resolve_leaf`, `elaborate.py:2359-2407`) — so the design's definition-qualified measurements
  and its three promoted fixtures (`s4b`, `s8`, `s6`) remain meaningful, but only for that lane,
  and nothing in the design says so.
- A new authoring situation exists that the design's three-situation rule does not cover: for an
  arrayed owner, `sum(comp_a::length)` refuses `SI_OCCURRENCE_AMBIGUOUS` while `sum(comp_a.length)`
  silently aggregates both occurrences (anchoring re-audit, 2026-08-16, `independent-audit-F1`).

Publishing the design's D-6 teaching as written would ship a document stating a resolution rule the
product does not implement — the exact failure class this item exists to end. That is why the gate
blocks rather than merely asking for edits.

**What survives untouched — do not re-derive on revision** (product-lens `design-F12`, plus this
review's independent code-claim verification): the one-authoritative-copy architecture (D1/D2), the
fixture-provenance drift gate (D3), the mechanized migration with its four preconditions and strip
check (D4/D5), the D-5 teaching and all 15 migration targets (the corpus adjudication proves the
D-5/D-7 lanes unchanged by the repair: 404 of 409 sites untouched, all identity stable), the F-3
repair design (verified still valid at HEAD: the unguarded `validate()` call at `elaborate.py:631`
and the boolean-DFS cycle checker at `graph.py:862-892` are both unchanged), the mutation site
(`hif_plant.sysml:87`), D8's R-2 reasoning, and D10's triage-only stellarator scope.

---

## High-Level Issues (what the rework must address)

### Critical

1. **[design-F8 · lens BLOCK] The D-6 teaching describes a deleted behavior.** Core Concept
   (`design.md:246-254`) and teaching item 3 (`:429-431`) present the two-step position rule as the
   semantics of owner qualification. Post-repair that is true only for definition-owned leaves.
   The revision must state the behavior at the landing commit: exact usage-owner anchoring for
   usage-owned leaves; `_resolve_leaf`'s positional rule scoped explicitly to the definition-owned
   route, with the sideways-reach (F-4) sentence scoped the same way. Spec rev 5 (`spec.md:53-61`,
   the amended `[HARD]` row) is the contract text to design against.

2. **[design-F9 · lens BLOCK] D11 is resolved by events and must be replaced, not awaited.** The
   addendum it waits on landed and was superseded by a production repair; neither pre-decided
   branch describes the outcome. Replace D11 with the landed fact: usage-qualified references now
   resolve exactly; the 13 published sites get rewritten or caveated against the *repaired*
   behavior; `MODELING_PROCESS.md.template:349-350` is rewritten, not caveated (D11's own branch-2
   consequence, now fired as fact). Repoint the D-6 measured authority from `spike/findings.md`
   (pre-repair rows superseded) to `tests/conformance/test_usage_owned_reference_anchoring.py`.

3. **The Spine's expected-answer arithmetic is falsified at the oracle.** Verified against
   `test_projection_wiring_contract.py:40-70` at HEAD: the fixture oracle holds **27 total keys of
   three classes — 22 `DESIGN_ATTRIBUTE`, 2 `USAGE_LITERAL`, 3 `LIBRARY_DEFAULT`** — not "27
   DESIGN_ATTRIBUTE keys"; the `hif_driver__hif_driver_instance__*` family is **4 keys**, not "the
   two" assertion 1 subtracts; the `…__driver__*` family is **6 keys**, not two. Assertion 1's
   expected set ("the authored oracle's, minus the two `hif_driver_instance` keys") must be
   re-derived from the oracle's actual partition before the plan hard-codes a wrong enumeration.
   The concept (B5, enumeration over all 11 formals) stands; the arithmetic does not.

### Major

4. **[design-F10 · lens DISPOSE] The arrayed-owner situation has no taught pattern.** The
   `::`-vs-`.` aggregation split is measured fact the spec's `[HARD]` row now carries. The revised
   design either teaches it (which spelling, and the indexed form) or excludes it in words with
   `independent-audit-F1` cited as the named owner. Note the lens's forward flag: if the
   disposition is "tell authors to write the dotted spelling," that is smell 2 (documentation
   compensating for a product inconsistency) and escalates then. Cross-ref: spec-review L2-2 puts
   the scope question to the owner.

5. **[design-F11 · lens DISPOSE] Label the evidence by owner class.** The three promoted fixtures
   and every qualified Appendix-B row pin the **definition-owned** route only. Say so per fixture,
   and add a usage-owned/arrayed row to Appendix B sourced from the anchoring conformance test —
   otherwise Invariant 3 re-creates the overclaim it was narrowed to prevent.

6. **D9 (ADR-010 "is filed") presumes an owner decision the spec still lists as open.** Same
   contradiction as spec-review L3-1; the owner's answer resolves both documents. Do not carry D9
   into the plan until it exists.

7. **Re-establish the two dispositioned repairs' evidence post-repair.** F-3's traceback
   (`s5_sibling_formal`) and F-2's validator false positive were measured pre-repair. The code
   paths verifiably still exist at HEAD, so both likely reproduce — but "likely" is what this
   project's own discipline forbids; one cheap licensed run each, before the plan budgets them.

### Minor

8. Stale pointers to fix in the same pass: "Spec (rev 3)" → rev 5; "the orchestrator has the spike
   re-running now" / "addendum is in flight" / Next Step "the D11 addendum" — all overtaken;
   "codegen's working tree carries uncommitted `dead-worktree-pins` edits" — landed since;
   the design-review citation → `design-review-20260815-rev1.md`.
9. Small line-number drift found by verification (substance holds): `make_d5_variant.py` split call
   at `:225` not `:224`, strip-undo/compare at `:265/:268` not `:261-262`; `formal_identity`
   populated at `project.py:536` (the `:543` cite is the helper's def); oracle table spans
   `:40-70`.
10. The MF-7 disagreement's stated reason overstates: `hif_driver.sysml` *in the fixture* still
    declares `part hif_driver_instance` at `:100` (the design's own D8 says so). The reason is true
    only for the customer tree post-R-2 — scope it there (lens `design-F1` correction).

---

## Recommendations

1. One design revision (rev 3) against HEAD `8bea4b8`+, rewriting the D-6/D11 material from the
   repaired resolver and the anchoring item's conformance tests; carry everything `design-F12`
   endorses unchanged.
2. Re-derive the Spine assertion-1 expected set from the oracle's actual DESIGN_ATTRIBUTE
   partition (issue 3) in the same revision.
3. Before revising, get the two owner answers already queued in the spec review: ADR-010 (L3-1)
   and arrayed-guidance ownership (L2-2). Both change design text.
4. Two cheap licensed probes to re-establish F-2/F-3 on the repaired resolver; attach results to
   the revision.

---

## Resolutions

*(Filled in as the owner resolves issues; keyed by number.)*

---

**Overall:** Rework — mandated by the product-lens BLOCK (owner-grade) and the fired smell 7, and
honest about its shape: the architecture is endorsed; the rework is the D-6/D11 axis plus the
falsified spine arithmetic, one revision's worth of work with two owner rulings as inputs.
**Next Steps:** Record resolutions here (and the two owner answers in the spec review), then re-run
`/_my_design` pointed at this review, the product-lens design block of 2026-08-16, and spec rev 5.
The reviewer does not edit the design.
