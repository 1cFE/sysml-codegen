# Spec Review: Elaborator Downstream Remediation and Certification

**Spec:** `.project/active/elaborator-downstream/spec.md`
**Contract:** `~/.claude/commands/_my_spec.md`
**Review File:** `.project/active/elaborator-downstream/spec-review.md`
**Date:** 2026-08-16

---

## Reality Check

**Sound, with concerns.** The spec is about the right work item: it is genuinely ELABORATE-FIRST
Item 8's undischarged remainder, and the Problem section is materially accurate. I checked every
code-facing `[HARD]` claim and all of them hold — TEAx's eight-field store identity and
`IncompatibleStore` (`teax-simkit/simkit/study/compatibility.py:15-46`), the seal-before-load rail
(`simkit/evaluation/package_load.py:3-65`), the exact-route-only authority (`CLAUDE.md`), the
absent source-identity matrix family (`docs/architecture/verification-matrix.md` — 34 families,
zero `REQ-SI` rows), the four false README claims, and the 2,294/2,301 figure
(`.project/completed/20260713_epic_constraint_execution.md:39`). Nothing here is invented physics
or a hallucinated interface.

The concerns are about **size, provenance stamps, and entry-gate ambiguity**, not direction. Design
would not be misled about *what* to build; it would be misled about *how much* is one item and
about *which claims the owner actually made*.

---

## Audit

### Lens 1 — Faithfulness

**L1-1 · Question to the user:** Three requirements and the Problem's scope boundary carry
`[OWNER 2026-08-16]` stamps, and **no owner utterance for any of them exists anywhere on disk**. I
swept `.project/` for `OWNER 2026-08-16`: every other hit resolves to the *anchoring* certification
or the *arrayed scalar* policy from the sibling item, each of which has a quote or a review-file
path behind it. The three stamps in this spec — the Stellarator boundary (`:40-42`, `:89-91`), the
July census boundary (`:92-95`), and the epic's new Stellarator exclusion line
(`epic_elaborate_first_architecture.md:496`) — trace only to text this same session wrote (the
spec, the working-tree epic edit, and the `CURRENT_WORK.md:84` entry). Capture-fidelity asks that an
owner-grade settled item carry the quote or a path-cite. **Did you state these three on 2026-08-16,
and if so can we get the wording recorded somewhere durable?** A downstream agent currently has
three do-not-relitigate boundaries with no source.

**L1-2 · Question to the user:** Two of those rows say the owner *"accepted"* / *"approved"* a
boundary rather than originated it, which is the ratification shape, not the origination shape. The
Stellarator split was recorded as an **agent** recommendation on 2026-08-15
(`CURRENT_WORK.md`: *"Split the Stellarator out of scope item 1 `[recommended 2026-08-15]`"*), and
the July census widening came from this session's own product lens (`product-lens.md`, spec-F1).
Under the settled rule those should read `[AGENT] (ratified by owner, 2026-08-16)` and stay
challengeable by re-deriving against their reasoning; as `[NEED]` + "Scope boundary" they read as
owner-originated and un-relitigable. **Which is it — did you decide the Stellarator exclusion, or
approve the recommendation?** The practical difference is whether a later agent may reopen it with
new evidence.

**L1-3 · Direct claim:** The spec cites `.project/backlog/epic_elaborate_first_architecture.md` as
the `[INHERITED]` source for its scope, Stellarator boundary, and fourteen-document list — but
**that epic text is uncommitted working-tree content written by this spec session**
(`git diff` shows sub-items 1, 2, 3, the success criteria, and the dependencies block all rewritten
today; only 6 lines are staged). Inheriting from a document you just authored is circular
provenance: the `[INHERITED]` grade claims a document's authority, and here the document's authority
is this spec. The doc-list swap is the sharpest case — the epic's own six-document list
(`11/12/13/16/24/25`) was replaced by the stocktake's fourteen **with no provenance-correction
note**, while the neighbouring sub-item 4 correction carries exactly such a note. The substance is
right (the stocktake's reconciliation is well-evidenced), but the epic now asserts a scope its
record can't explain.

**L1-4 · Direct claim:** Epic Item 8's second success criterion is *"Certification and guidance
obligations from the Item-3 contract discharged"*
(`epic_elaborate_first_architecture.md:522`). **The spec never mentions the Item-3 contract.** Its
`[INHERITED]` scope row enumerates seven inherited portions and that is not one of them, and no
success criterion references it. Either those obligations were discharged elsewhere (say so and
cite it), or they are silently dropped from an item that claims to own Item 8's remainder. The
matrix's `Contract disposition — REQ-…` machinery
(`docs/architecture/verification-matrix.md:35`) suggests there is live surface behind this.

**L1-5 · Confirmed, use it:** The Problem's premise that the workaround-free shape is unmeasured is
true, and SC2's "measure it" is the right call — but the open owner question CURRENT_WORK has been
carrying (*"re-anchor the pin to 9 channels, or restore the instance and contradict R-2"*) is
now answerable from the sealed graph without a capture run. I checked
`tests/fixtures/fusion_tea/instance_graph_snapshot.json`:
`meier_capital_calc.driver_cost` and `.reactor_cost` both resolve to producers on the **hif_plant**
occurrence (`a9ff1597…`), and the standalone `hif_driver_instance` occurrence (`5db38fc2…`) feeds
**nothing downstream** — its only edges are its own four inputs. So the deletion removes exactly the
two `hif_driver__hif_driver_instance__meier_cost__*` channels (11 → 9) and **cannot move LCOE**.
SC1, SC2, and SC3 are mutually consistent, and no owner call is needed to choose between
re-anchoring and restoring.

### Lens 2 — Problem & Approach

**L2-1 · Question to the user — the headline:** **This is not one item.** The epic budgets Item 8 at
3–5 days. This spec's nine criteria span: cross-repo package regeneration and TEAx execution; a new
study lineage; acceptance-pin re-anchoring; a composed proof; a forensic impact audit across
repositories plus owner attestation; minting a verification-matrix requirements family; a README
rewrite; and **rewriting or retiring fourteen architecture reference documents** — roughly 4,200
lines that `CLAUDE.md` itself calls "a separate authorship pass that has not run." The stocktake you
commissioned recommended splitting one piece out explicitly (*"File the July IFE impact audit as its
own item. It has no artifact and no vehicle"* — Recommendation 6). **The spec silently declines that
recommendation without saying why.** The natural seams are three: (a) regeneration + lineage +
composed proof, (b) the July impact audit, (c) certification + documentation repair. Each has a
different subject, a different failure mode, and a different reviewer. **Do you want this as one
item, or split?** Keeping it whole means ELABORATE-FIRST cannot close until a documentation
authorship pass finishes.

**L2-2 · Question to the user:** SC2 permanently freezes the divergence between the codegen fixture
(11 channels, keeps `hif_driver_instance`) and the customer model (9 channels, deleted it): *"The
codegen fixture's intentionally different 11-channel topology remains a separate acceptance surface
rather than an oracle."* That is a defensible call, but it locks in the exact smell the
self-binding audit just fired on — *"Two live representations require manual synchronization"*
(`self-binding-replacement/audit.md:38`, product-drift smells 1 and 6). And the fixture's own
docstring says the instance exists only *"so codegen template expansion emits the meier_cost
module"* — a workaround for a defect the exact route no longer has (the graph emits
`hif_plant_pkg__hif_plant__driver__meier_cost__*` on its own). **Should the fixture keep a dead
codegen workaround as a permanent second acceptance surface, or should it converge on the customer
shape?** The spec settles this by assertion; it deserves a stated reason either way.

**L2-3 · Direct claim:** The spec's entire subject — "the migrated, workaround-free Fusion Tea
customer model" — exists **only on two unmerged local branches in another repository**, and the
spec never says so. `/home/reid/1cfe/fusion-tea` is on `item8-fusion-embedded-catalog` at
`be1ee7c0` and still carries all **15** self-named bindings; the migration is `9e1ff87b` on branch
`self-binding-replacement` in the isolated worktree `/home/reid/1cfe/fusion-tea-self-binding`.
Meanwhile the Non-Goals forbid pushing branches or opening PRs. So this item will regenerate and
commit a customer package on top of a two-deep stack of unmerged local branches, in a repo outside
this checkout, with no requirement stating the base, the branch topology, or how the fusion-tea and
codegen halves stay coordinated. Open Question 5 asks about "owning locations and naming" — that is
the filing-cabinet half of the question, not the branch half.

**L2-4 · If-then tradeoff:** SC4 requires that "opening the prior store against the changed identity
refuses rather than silently rebinding old cases." That is **already TEAx's behavior**, not
something this item builds — the eight-field `Compatibility` record and its `IncompatibleStore`
rail are shipped (`compatibility.py:15-46`), and the spec's own `[HARD]` row says so. If the intent is *prove
it holds on our new lineage*, that's a fine criterion and should say "demonstrates"; if the intent is
*build lineage linking*, then the new thing is the **linked** part (an explicit pointer from the new
store to the old), and that is what the criterion should name. As written the sentence restates the
`[HARD]` row, which also breaks the one-home-per-idea rule.

### Lens 3 — Pipeline Risk

**L3-1 · Direct claim — the entry gate has no home.** The Problem says the downstream record
"cannot rely on those claims until that audit is closed or its findings are visibly dispositioned,"
and the Non-Goals carve an exception for "where the current self-binding audit's blocking findings
must be closed before this item can rely on them." But there is **no success criterion and no
`[HARD]`/`[NEED]` row for the gate** — only an `[INFERRED]` row at `:134-136`. Two strong engineers
would split here: one treats closing the five audit findings (the false-greening mutation oracle,
`make_d5_variant.py`'s destructive `--scratch`, the `except Exception: continue` in the agentic
validator, the F-4 disposition, the single-tree spine) as this item's Phase 0; the other treats them
as the sibling item's homework and blocks. Those are materially different plans. **Which item fixes
`audit.md` findings 1–5?**

**L3-2 · Rewrite request:** The success criteria are compound to the point of being hard to
falsify. SC1 bundles regenerate + seal + contract + stock-API load + execute + five distinct
negatives into one checkbox. SC5 bundles census-root enumeration + consumer naming + four-way status
recording + two preservation clauses. A criterion that can fail six independent ways can't be ticked
honestly, and an audit against it will produce exactly the partial-verification mess the sibling
item's audit is in now (seven of ten verified, three open, four plan checkboxes reopened). Ask the
spec agent to split each compound criterion into independently checkable outcomes — same content,
one failure mode per box.

**L3-3 · Direct claim — deferral accuracy.** Open Question 2 defers to design *"whether the
source-identity matrix family mints a new `REQ-SI` namespace or re-anchors existing requirements."*
The stocktake already ruled on the class of that question: minting REQ tags *"is a requirements
decision, not a matrix reconciliation. Same shape as the parked `[CONSTRAINT-GATES-UNTAGGED]`
precedent"* — and that precedent was **parked with the owner**, twice
(`CURRENT_WORK.md`, Item 7 residual A-2). Deferring an owner-grade requirements call to design
contradicts the precedent this repo just set. This is a spec-stage question you can answer now.

**L3-4 · If-then tradeoff:** SC8 makes "document 25 follows its separate owner disposition" a
completion criterion, while the Non-Goals forbid deciding it without an owner and Open Question 4
files it as unobtained. **The item therefore cannot complete without an owner action it does not
control.** That's fine *if* you intend to make the call during the item — then say the disposition
is an input, not an outcome. It's a problem if the item is expected to close on its own steam. Same
shape, lower stakes, applies to the `extraction/hierarchy_resolver.py` deletion question.

**L3-5 · Rewrite request:** SC9's "introduces no new unexplained regression, and records exact
repository commits and licensed-test status" mixes an outcome with bookkeeping. Worth noting the
concrete trap it will hit: this repo's licensed suite reads as a fake baseline unless
`SYSIDE_LICENSE_KEY` is sourced from `/home/reid/1cfe/agentic-mbse/.env`, and the full default suite
currently shows **17 pre-existing ordering-dependent failures at clean HEAD**
(`CURRENT_WORK.md`, 2026-08-15 dead-worktree-pins entry). "No new regression" needs a stated
baseline or it will be argued about at audit time.

### Lens 4 — Hygiene

**L4-1 · Rewrite request:** The `[NEED]` at `:84-88` ("one modeled source occurrence becomes exactly
one runtime source…") and the `[INHERITED]` at `:96-101` (the Item 8 scope) overlap: the first is
the epic's mission invariant, the second is the epic's item scope, and both cite the same file. Not
wrong, but the reader has to work out that one is the *goal* and one is the *work list*. One
sentence of framing on each would fix it.

### Lens 5 — Reader Comprehension

**L5-1 · Rewrite request:** The Problem's four paragraphs each open with mechanism and reach the
point last. Paragraph 1 spends three sentences on ELABORATE-FIRST and `self-binding-replacement`
history before landing on "the downstream record cannot rely on those claims." Paragraph 3 runs
through the July study's design before saying the thing that matters: **swept-row LCOE and
recirculation numbers are design-point numbers, and nobody knows who used them.** A tired engineer
should get each paragraph's conclusion in its first sentence. Ask for a lead-with-the-point pass —
the content is right, the ordering buries it.

**L5-2 · Rewrite request:** "Every-and-only mutation oracle" (`:16`) is load-bearing and never
explained in this document. It arrives as a coined phrase in the second sentence of the spec and
the reader has to reach the sibling item's audit to decode it. One plain clause — *a public
mutation reaches every consumer bound to that source and no others* — anchors it. Same for
"post-R-2" at `:21` and `:50`, which assumes the reader knows R-2 is July's duplicate-field
workaround retirement.

---

## Engagement Summary

**Overall take:** The spec is pointed at the right work and its factual spine holds — I checked
every `[HARD]` code claim and all of them are true at HEAD. But it is at least three items wearing
one hat, three of its boundaries carry owner stamps with no recorded owner utterance, and the
entry gate onto the sibling item's `Needs Work` audit is stated in the Problem and nowhere in the
contract. Fix those and this is a good contract.

**Here's what I need you to weigh in on:**

1. **[L2-1]** Is this one item or three? Regeneration + proof, the July impact audit, and the
   certification/documentation repair have different subjects and different failure modes, and the
   fourteen-document rewrite alone is an authorship pass. Your stocktake recommended splitting the
   July audit out; the spec declines without saying so.
2. **[L1-1, L1-2]** Confirm the three `[OWNER 2026-08-16]` boundaries (Stellarator exclusion, July
   census bounds), and tell me whether you *originated* them or *ratified* an agent
   recommendation. No utterance for any of them exists on disk, and the grade decides whether a
   later agent may reopen them.
3. **[L3-1]** Who closes the five `self-binding-replacement` audit findings — this item as Phase 0,
   or that item before this one starts? The spec makes it an `[INFERRED]` aside with no criterion,
   and the two readings produce different plans.
4. **[L2-3]** How do the fusion-tea branches work? The migrated model is unmerged local work on
   `self-binding-replacement`, stacked on the also-unmerged `item8-fusion-embedded-catalog`, in a
   repo outside this checkout — while the Non-Goals forbid pushing or opening PRs.
5. **[L2-2]** Should the codegen fixture keep `hif_driver_instance` forever as a second acceptance
   surface? SC2 freezes it; the fixture's own docstring says it exists to work around a defect the
   exact route no longer has, and the sibling audit just flagged dual-tree synchronization as a
   product smell.
6. **[L3-3]** The `REQ-SI` namespace question is deferred to design, but minting REQ tags is the
   requirements decision you parked with yourself twice as `[CONSTRAINT-GATES-UNTAGGED]`. Answer it
   now or park it the same way — design is the wrong home.
7. **[L1-3, L1-4]** Two epic-provenance items: the epic's scope was rewritten by this session and
   then cited back as `[INHERITED]` (the six→fourteen doc-list swap carries no correction note,
   unlike its neighbour), and epic Item 8's second success criterion — the Item-3 contract's
   certification and guidance obligations — appears nowhere in the spec.

**Free finding, no decision needed [L1-5]:** the 9-vs-11 channel question is settled from the sealed
graph without a capture run. `meier_capital_calc` takes both its cost producers from the hif_plant
occurrence, and the standalone `hif_driver_instance` feeds nothing. Deleting it drops exactly two
channels and cannot move the LCOE anchor — so SC1, SC2, and SC3 are consistent, and the "restore the
instance vs re-anchor the pin" owner call CURRENT_WORK has been carrying is moot.

---

## Resolutions

**[L2-1] Rejected — one item. `[OWNER 2026-08-16]`** The owner ruled the scope stays whole:
regeneration + proof, the July impact audit, and the certification/documentation repair are one
work item. No split. The reviewer's sizing objection is recorded and closed; the fourteen-document
authorship pass rides inside Item 8.

**[L1-1, L1-2] Confirmed as ratified agent recommendations.** The owner accepted the three
boundaries — Stellarator exclusion, the July census bounds, and the owner-attestation requirement
for external consumers — but did not originate their wording. Under the settled rule they remain
`[AGENT] (ratified by owner, 2026-08-16)` and map to `[INFERRED]` spec requirements, not `[OWNER]`
and `[NEED]`. The owner confirmed this correction after review on 2026-08-16. This resolution is
the durable path-cite for the ratification; the decisions remain challengeable by re-deriving
against their recorded reasoning.

**[L3-1] Out of scope. `[OWNER 2026-08-16]`** The five `self-binding-replacement` audit findings
are **not this item's work** — that remediation is in progress in its own item. The spec agent
should make this explicit rather than leaving it as an `[INFERRED]` aside: the audit closure is an
**entry gate on a sibling item**, not a Phase 0 of this one. The Non-Goals' conditional carve-out
("except where the current self-binding audit's blocking findings must be closed before this item
can rely on them") should be rewritten to say plainly that this item performs none of that
remediation and waits on it.

**[L2-3] Resolved — new branch. `[OWNER 2026-08-16]`** Check out a new branch for this item's
fusion-tea work. The spec agent should record the branch requirement and its base so the stack is
not left implicit; the Non-Goals against pushing and PRs are unchanged.

**[L2-2] Resolved — converge the fixture. `[OWNER 2026-08-16]`** The owner chose option (b): delete
`hif_driver_instance` from the codegen fixture so the fixture and the customer model carry **one
shape**. SC2's "the codegen fixture's intentionally different 11-channel topology remains a separate
acceptance surface" is **overturned** and must be rewritten — there is no separate acceptance
surface; there is one measured post-R-2 topology that both the fixture and the customer package
carry.

The context behind the call, for the spec agent:

- `hif_driver_instance` (`tests/fixtures/fusion_tea/designs/hif_ife/hif_driver.sysml:100-119`) is a
  package-level duplicate of the plant's own driver at the same Osiris operating point. Its doc
  comment records its purpose: it exists so the **legacy** string route would emit the `meier_cost`
  module, because that route indexed the redefining `part :>> driver` usage inside `hif_plant` under
  its inherited type. It is a workaround for a defect the exact route does not have.
- The exact route emits `hif_plant_pkg__hif_plant__driver__meier_cost__*` on its own, and
  `tests/execution/test_fusion_tea_real_teax.py:214-221` asserts both channel prefixes against the
  *same* hand values — they are duplicates by construction.
- The standalone occurrence is inert in the graph: `meier_capital_calc` takes both cost producers
  from the `hif_plant` occurrence, and nothing consumes the standalone's outputs.
- Four codegen sites pin it, all fixture-shape pins rather than behavior:
  `tests/conformance/test_projection_wiring_contract.py:41-44` (four `DESIGN_ATTRIBUTE` entry-point
  keys), `tests/conformance/test_elaboration_fail_closed.py:133` (one of seven resolved
  enum-literal rows), and `tests/execution/test_fusion_tea_real_teax.py:59-60,215` (two of the
  eleven pinned channels plus the duplicate-arithmetic loop).
- No coverage is lost: a package-level part usage typed by a definition and carrying `:>>` value
  redefinitions is covered by `tests/fixtures/costed_cart_d5/design.sysml:22-23`.

The deletion is in this item's scope and re-anchors the same pins the item was already re-anchoring.

**[L2-4] Accepted.** The spec distinguishes the two lineage outcomes. The item creates and records
the new link to the predecessor; a separate proof demonstrates TEAx's already-shipped refusal of a
prior store whose bound identity differs. The item does not claim to implement that refusal rail.

**[L3-3] Accepted — `[AGENT]` (ratified by owner, 2026-08-16).** The `REQ-SI` namespace question does not go to design. It
follows the `[CONSTRAINT-GATES-UNTAGGED]` precedent. The owner ratified the agent recommendation to
mint an independently anchored `REQ-SI` family derived from the durable `LC-SI-*` requirements and
Item-3 acceptance matrix. The existence of the family is fixed here; its exact row mapping remains
design work.

**[L3-4] Resolved — retain document 25's subject.** The owner ratified the agent recommendation to
retain `extraction/hierarchy_resolver.py` as a test-only, off-shipped-route legacy extractor. This
item corrects document 25 and related assurance claims to that bound. Deletion requires a later
equivalence-backed retirement decision and is not a completion dependency here.

**[L3-5] Accepted.** Regression evidence names a pre-work baseline with exact commits, commands,
environment, licensed-test status, and known failures. Final results compare like-for-like against
that baseline; an unlicensed skip or the known ordering-dependent failures cannot become a fake
green baseline.

**[L1-3] Accepted — `[AGENT]` (ratified by owner, 2026-08-16).** The epic's six→fourteen document-list swap gets a
provenance-correction note in the same shape as the neighbouring sub-item 4 correction, and the
spec's `[INHERITED]` rows should cite the stocktake
(`.project/research/20260815-103905_item8-bounded-stocktake.md`) as the originating authority for
the reconciled list rather than resting on the epic text this session wrote.

**[L1-4] Accepted — `[AGENT]` (ratified by owner, 2026-08-16).** Epic Item 8's second success criterion — "certification
and guidance obligations from the Item-3 contract discharged" — must be addressed: either absorbed
into this spec's scope with a matching success criterion, or explicitly recorded as discharged
elsewhere with a citation. It cannot stay unmentioned.

**[L1-5] Informational, no decision needed.** Carried into the spec as measured fact: the
9-vs-11 channel question is settled from the sealed graph and the "restore the instance vs
re-anchor the pin" owner call is moot.

**[L3-2, L4-1, L5-1, L5-2] Accepted.** The revised spec splits independently checkable outcomes,
leads each Problem paragraph with its point, distinguishes the mission invariant from the work
list, and defines both the every-and-only public mutation and post-R-2 shape on first use.

---

**Verdict:** Revise addressed 2026-08-16 — the spec agent incorporated the resolutions above and
recorded the edits below.
This record does not self-certify the revised spec. The required product-lens rerun is separately
recorded as `CLEAR`; a fresh independent spec review has not run.
**Next Steps:** Proceed from the revised spec's gate after owner confirmation. Design may begin;
implementation waits for the sibling `self-binding-replacement` entry gate.

The spec-agent incorporation record:

1. **SC2 is rewritten** — one measured post-R-2 topology; the fixture converges (L2-2). The fixture
   deletion and its four pin sites are in scope.
2. **The self-binding entry gate is stated plainly** — this item performs none of that remediation and
   waits on the sibling item; the gate is owner-stated and the conditional Non-Goal carve-out is
   removed (L3-1).
3. **Branch requirement is recorded** — a new branch for the fusion-tea work, based on the certified
   `self-binding-replacement` head (L2-3).
4. **`REQ-SI` is decided** — mint the family; only its exact authority-preserving map remains for
   design (L3-3).
5. **Item-3 contract obligations are addressed** — the spec requires a complete reconciliation and
   carries the still-owed guidance projection (L1-4).
6. **Provenance is repaired** — the epic carries a correction note for the six→fourteen doc-list
   swap, and the `[INHERITED]` rows cite the stocktake rather than epic text this session wrote
   (L1-3).
7. **The prose pass is complete** — compound criteria are split into independently checkable outcomes
   (L3-2), each Problem paragraph leads with its point (L5-1), and "every-and-only mutation" and
   "post-R-2" are defined on first use (L5-2). L1-5's measured channel finding is carried as fact.
8. **Lineage wording is corrected** — linking is new work; refusal is demonstrated shipped TEAx
   behavior (L2-4).
9. **Document 25 is dispositioned** — retain and accurately bound its test-only role (L3-4).
10. **Regression evidence is bounded** — compare named, licensed, like-for-like pre/post baselines
    and preserve known failures honestly (L3-5).
