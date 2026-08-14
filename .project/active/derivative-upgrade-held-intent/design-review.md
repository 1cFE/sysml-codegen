# Design Review: Derivative Upgrade Under Held Intent (CONSTRAINT-SEMANTICS Item 9)

**Design:** `.project/active/derivative-upgrade-held-intent/design.md`
**Spec:** `.project/active/derivative-upgrade-held-intent/spec.md`
**Review File:** `.project/active/derivative-upgrade-held-intent/design-review.md`
**Date:** 2026-08-13
**Reviewed at:** `item7-rebuild` @ `2c624cc` (fresh session; reviewer wrote neither spec nor design)

---

## The Point

`tests/fixtures/catf_mfe_gated` is the worked example of the ruled constraint policy. Its job is to
be the artifact someone opens to see what the policy actually produces. Three of its rows are not
the shape the owner ruled — they are the shape a defect allowed. Item 5 measured that A9's assert
band and 26 of 27 radius derivations refused against the projection, so those three rows landed as
visible plain usages marked `blocked-by-defect`, with their ruled target forms held as recorded
intent. Item 8 cured the defect at `62a07e5`.

So the fixture now misrepresents the policy it exists to demonstrate: it asserts by constraint what
the ruled basis says it should compute (A5, A6), it checks two independently authored numbers with
`==` when they already disagree by 0.16 m³/s (A9), and it carries `blocked-by-defect` markings whose
cause is gone.

The obligation is to make the worked example true again **without re-deciding anything**. Every
target form is already ruled — the A5/A6 basis (axis root radius + 14 layer thicknesses free, all
other radii derived) as `[AGENT] (ratified by owner, 2026-08-13)`, A9's 1% relative band as
`[OWNER 2026-08-13]`. Four properties carry that:

1. The owner decides dispositions, bases and tolerances; agents execute them.
2. Every accounting number is a mechanical consequence of the ruled table — never a re-decision,
   never read off a run.
3. A deletion is accepted only against outside evidence: the replacing derivation must exist in
   source and carry the undirected relation plus the chosen-basis statement.
4. Surfacing beats absorbing. A ruled form that cannot be built, or a number that moves when the
   arithmetic says it should not, is an owner event.

The failure this review is looking for is a ruled row quietly re-shaped to fit the tooling, an
identity closing on a citation alone because the prover cannot tell 27 near-identical derivations
apart, or a record whose stated cause is gone left standing as if still true.

---

## Fundamental Assessment

**Sound.** This is the right piece of work and the right approach, and the design is unusually
disciplined about the thing that most easily goes wrong here.

- **It is the right work.** Item 8's fix is what makes the held intent buildable; leaving the
  fixture as-is leaves the reference artifact contradicting the ruling it demonstrates. The
  product-lens ledger's existing epic-level finding (audit-F5) was disposed *onto* this item, and
  this design discharges it.
- **The approach is minimal.** Three mechanical source shapes, one prover extension, five
  expectation artifacts. There are no new abstractions, no new modules, no new vocabulary. The one
  piece of new mechanism (`DERIVATIONS` anchored by owning block) is the smallest thing that makes
  14 byte-identical lines individually gateable, and it *generalises away* the existing special case
  rather than adding a second matching rule. I could not describe a simpler design that still meets
  the spec's per-occurrence requirement.
- **The probe carries real weight.** It ran full generation through the public route, not
  elaboration, on throwaway copies. It found a non-obvious correctness requirement (unit text on
  the new declarations) and — critically — it did **not** adapt a ruled form to route around it. The
  first attempt refusing, and the design following the refusal to its actual cause rather than
  softening the form, is the behaviour the spec's Non-Goals demand.
- **The NOTE is a genuine surfacing, not a rubber stamp.** Row A9 says *"if the def-shape changes
  materially, design notes it rather than silently adapting."* It did change materially,
  `ProductWithinBand` really cannot be generic, and the design says so plainly including the cost
  (one definition per dimension) and the fact that `PROVENANCE.md:345-348` predicted that cost and
  is now false in its premise.

**Product lens: CONCERNS** (verdict block appended to `product-lens.md`). Two findings, both
omissions against the point rather than contradictions of it, both carried into the list below
(D-F1 → Critical 1; D-F2 → Major 5 and Major 4c). No owner/`[HARD]` contradiction, so no Rework
gate fires.

**Structural smells:** one fired and is disclosed. `ProductWithinBand` must be dimension-specific
because the platform ties a constraint port's unit to the formal's own declaration — the fixture
pays a per-dimension definition cost for a platform modeling limit. That is a consumer absorbing a
platform gap, and it is escalated here rather than left in the rubric. It does **not** block:
the design discloses it as the substance of its NOTE, the ruled form is preserved, and fixing the
platform is correctly out of scope. Recommendation: one unowned backlog line so the cost is
findable outside an archived design doc (Minor 12).

Proceeding to the detailed review.

---

## Answers to the five orchestrator questions

**1. Ruled-cell fidelity — holds, with one checkability gap.** Every design decision traces. D1/D2/D3
are unit spellings (design-owned under O4/O6), D4/D6/D7 are edit shapes (design-owned under O6),
D5 is the prover (agent-grade by construction). Nothing re-decides owner payload: the bindings, the
`0.01`, the deletion membership, the basis, and the 53/3 split all match the ruled table. The A9
NOTE is faithful to the row's trigger and correctly refuses to adapt silently. **But** the note
asserts *"the relative form and the 1% value are all exactly as ruled"* without ever writing the
predicate that carries the relative form — see Critical 1. The ruled semantics *are* preserved by
the spelling the probe used; the design just doesn't record it.

**2. The out-of-27 edit — I agree with the ratification, and the reasoning is stronger than the
design states.** In the computed-attribute lane the consumed attribute's own declaration *is* the
formal, so authoring A6's ruled derivation is what turns `tf_coil.thickness` into a unit-bearing
port. It is the only one of the 14 thicknesses with a second lane (`magnet_surface_calc`, whose
calc-def formal carries `// m`), which is why 13 need nothing. No value moves, no ruled cell moves,
and the amended comment preserves the provenance payload (`from line 83 (= tf_dr)`) rather than
replacing it — capture-fidelity law 2 respected. The `m` is not invented: it matches the `[m]` on
the value at `radial_build.sysml:439` and the disposition table's own unit-check cell for A5/A6
("length, m"). That is a mechanical consequence in O6's sense, not a new disposition. The gap is
recording, not authority — see Major 4c.

**3. The prover extension — yes, both failure modes stay fail-closed per occurrence, subject to two
statements the design should add.** Verified against source: the anchor blocks are uniquely named
within their files (`radial_build.sysml` layers at `:57`–`:538`; `gamma_shield` at
`shield.sysml:82`; `catf_vacuum_vessel` at `vacuum.sysml:22`; `AlphaNeutronSplit` at
`power_balance.sysml:62`), and the 14 layers are siblings, not nested. So a search scoped to block X
never sees block Y's byte-identical line — deleting one layer's initializer yields zero matches in
its own block and is reported by name. Doc-stripped stays distinguishable from initializer-gone
because D5 correctly refuses to couple the anchor to the comment text; the rejected alternative
would have collapsed the two modes. The count checks out: 13 (A5) + 14 (A6) + 3 (existing) = 30.
The two additions needed are Minor 10 (what a missing/duplicate block header does) and Minor 9
(the falsification cases must be occurrence-scoped).

**4. SC-6 ordering — the ordering is right; one value breaks the section's own rule.** Source-first
is correctly argued (source is not an expectation; the ordering that binds is
expectations-before-confirmation-run), the module count is correctly refused as unpredictable and
marked re-measure-do-not-copy-62, and the headline counts were pre-committed in the spec before the
probe ran and then merely confirmed. The exception is the **26 keys leave / 16 arrive** figure: it
comes from probe Result 4, sits inside the section that claims *"every value below is derived from
the ruled table or read from authored source,"* and is then asserted as validation criterion 5. See
Major 3 — it is cheaply repaired, because those numbers genuinely are derivable from source.

**5. Completeness against spec — three of four are clean.** SC-3 side 2 (the BACKLOG amendment) is
present, correctly scoped as an amendment, correctly sequenced, and carries the concurrency
re-check. **Side 1 has no home** — Critical 2. The byte-untouched checks are present twice (Required
Invariant 4, Validation 4) and cover both frozen twins and the archived acceptance item. The
unexercised snapshot lane is present, named as the residual on bet B3, and correctly ordered first
in the de-risk. The one-ULP drift is analysed correctly and explicitly not absorbed, but is recorded
only in a document that archives with the item — Major 5.

---

## Dimensional Review

### 1. Spec Compliance
**Assessment:** Concerns

Every spec `[HARD]` and `[NEED]` maps to a design element, and the provenance grades survive the hop
faithfully: the design treats the A5/A6 basis and A9's tolerance as fixed (correct — owner-graded),
treats O6's edit shape and the unit spelling as its own (correct — design-owned), and does not
harden any `[INFERRED]` item into a constraint it isn't. The `[INHERITED]` axis-region item is
carried and executed rather than re-argued.

Gaps:

- **Spec deferred question 3 is not answered.** *"`ProductWithinBand`'s exact declaration — formal
  spelling and how the ±1% band is written over the formals"* is assigned to design; the design
  gives the formals' unit comments and the assert's bindings but never the predicate. (Critical 1)
- **SC-3 side 1 is unplaced.** Spec success criterion *"SC-3 is recorded on both sides as a
  not-fired conditional"* and N-4.1 require this item's records to mark it. The design mentions it
  only in a Non-Goals sentence; it appears in no artifact row and no validation step. (Critical 2)
- **The spec's `[HARD]` PROVENANCE list is executed; §5 is under-covered.** The design names §5's
  false sentence but not the two other §5 obligations that follow from asserting a third gate.
  (Major 4)
- **One spec `[INFERRED]` claim is corrected by measurement rather than by derivation.** The
  "free parameters stay keys" phrasing is rightly corrected, but the replacement number arrives
  from a run. (Major 3)

### 2. Pattern Consistency
**Assessment:** Pass

The design reuses rather than invents at every turn: Item 5's A8 derivation idiom
(`vacuum.sysml:53-58`) for the `//`-comment unit spelling; Item 8's `unit_lane_a9` fixture spelling
for the formal annotations; `physics.sysml:17-18`'s import idiom for A9's import; the existing
`renamed_from:` bridge for A9 rather than a new mechanism; the existing 12-line comment window
rather than a new documentation contract. D5 replaces one matching rule with one matching rule
instead of adding a second. D6 keeps declarations in place specifically to avoid churning the
population expectation. This is the strongest dimension in the design.

### 3. Abstraction Quality
**Assessment:** Pass

One new dataclass (`Derivation`) with three self-describing fields, replacing an anonymous
2-tuple. It earns its existence: the tuple is about to grow a third element and be used in a
sequence, and a bare `tuple[str, str, str]` in that position would be unreadable. Removing it would
make the prover harder to follow, not easier. Nothing else is introduced. The Core Concept section
gives a reader the one mental model the whole design turns on — a unit lives on a declaration, and
authoring a derivation adds a consumer lane to a design attribute — before any mechanism.

### 4. Duplication Avoidance
**Assessment:** Pass

D4's split (two/three-line block per derivation, full basis paragraph once at the
`catf_radial_build` level) is the right trade and the rejected alternatives are the real ones: a
repeated paragraph ×27 is unreadable, and a file-level statement alone would let the prover gate a
citation — precisely the A-1 gap. D3 explicitly refuses to annotate 13 declarations nothing
requires. D5's generalisation removes a would-be parallel structure rather than creating one.

### 5. Data Structure Clarity
**Assessment:** Concerns

The `DERIVATIONS` shape is explicit and typed, and the expectation table names every field that
moves with the value it moves to. Two problems:

- **Required Invariant 6 is false under the design's own D3.** It reads *"every free radial
  parameter and every A9 operand carries unit text that all its consumer lanes agree on."* Thirteen
  thicknesses and `axis_region.inner_radius` will carry no readable unit text at all — their
  comments are `// From line 74` and `from` is in the extractor's stop-word list
  (`extraction/feature_metadata.py:84-122`). D3 leaves them deliberately and correctly. An
  implementer following Invariant 6 literally annotates 13 declarations D3 forbids. (Major 6)
- The predicate that defines `ProductWithinBand`'s data contract is absent (Critical 1).

### 6. Route Safety
**Assessment:** Concerns

Read as "does anything fall through to a permissive default": the identity join is fail-closed in
both directions today and the design does not weaken it. The one unstated default is in the new
block scanner — the design says how a block is found and closed but not what happens when the header
is absent or appears twice. A "block not found → skip this derivation" default would silently
un-gate a row. (Minor 10)

Related implementation caution, not a design fault: brace-depth block closing is safe for
`radial_build.sysml` (no braces appear in its doc comments — verified), but the other three anchored
files should be spot-checked at implement.

### 7. Bets & Decisions Integrity
**Assessment:** Pass

The bets are genuine claims about reality, not mechanism choices in disguise, and each has a real
"if false" consequence. B1 is the sharpest one in the design: it is stated, confirmed decimally, and
then **explicitly qualified at the bit level** rather than left clean — the design volunteers
evidence against its own bet, which is the behaviour capture-fidelity law 4 wants. B4 is honestly
labelled as a reading of an owner ruling rather than a measurement, and nominated as the item most
worth disagreement. B3's residual (the snapshot lane) is named and drives the de-risk ordering.

Decisions each name a rejected alternative with a reason, and the reasons are load-bearing rather
than decorative — D5's rejection of comment-coupled matching is the one that actually preserves a
pinned property.

**Hidden bet, surfaced:** the design rests on *"there is exactly one owning block per derivation and
it can be found textually."* That is true here (verified above) but it is a property of this
fixture's authoring, not a general one — a nested or re-declared layer would break it silently. It
belongs beside the other bets, with "if false → the anchor resolves to the wrong block and a
deleted derivation passes on a sibling's line" as its consequence. Recording it costs two lines and
makes Minor 10 self-evident.

### 8. Reader Comprehension
**Assessment:** Pass

A reader can skim this once and come away with the model. The Point states the problem before any
mechanism; Core Concept gives the one insight the design turns on in plain words before naming
`SI_RENDERING_COLLISION`; the concrete 27-derivation shape is shown as code rather than described.
The NOTE section is the clearest thing in the document — it states what changed, why it could not be
otherwise, what it costs, and what did *not* change.

The one comprehension trap is a name collision the implementer will hit: this design's **D3** (the
`tf_coil.thickness` comment) and the fixture PROVENANCE §5's **"(D3)"** (Item 5's design decision)
are unrelated, and the design's edit list sends someone into §5 to amend text under a heading that
reads as its own D3. (Minor 11)

---

## Issues by Severity

### Critical

1. **`ProductWithinBand`'s predicate body is written nowhere in the design.** — Spec Compliance /
   Ruled-cell fidelity.
   The design gives the formals and their unit comments (D2), the assert's bindings and
   `rel_tol = 0.01` (Component Overview), and asserts in the NOTE that *"the relative form and the
   1% value are all exactly as ruled"* — but never the predicate. Spec deferred question 3 assigned
   exactly this to design. The consequence is concrete: the ruled semantics are *relative* — band =
   `count * each_capacity ± 1%`, chosen *"over absolute so the band scales under design-search
   resizing"* (`owner-disposition.md:106`, **[OWNER 2026-08-13]**) — and an implementer working from
   this design could author an absolute band that still reads as "1% relative" in the change list
   and still passes generation. The spelling already exists in the probe
   (`probes/apply_item9_edits.py:132-139`) and it *does* preserve the ruled semantics:
   `observed > count * each_capacity * (1.0 - rel_tol) and observed < count * each_capacity *
   (1.0 + rel_tol)` — two-sided, multiplicative on the product, so the band scales with any
   resizing. Carry it into the design verbatim and check it against the row there, so the NOTE's
   preservation claim is verifiable rather than asserted. Confirm in the same place that it is
   bindings-only over formals with no `[unit]` literal in the body (spec `[HARD]`) — it is.

2. **SC-3's first side has no artifact, no change-list row, and no validation step.** — Spec
   Compliance / Completeness.
   Spec N-4.1 requires *"this item's records mark SC-3 as a not-fired conditional, naming the open
   defect as the trigger,"* and the spec lists it as a success criterion. The design covers side 2
   (the `BACKLOG.md` amendment) thoroughly — own step, correct amendment framing, concurrency
   re-check — but side 1 appears only as a Non-Goals sentence (*"SC-3 is a conditional that does not
   fire; only its trigger is recorded, on both sides"*). The PROVENANCE edit list touches SC-3 only
   to restate the identity in the Authority block, which is a different obligation. Name the home —
   PROVENANCE §3b already holds the B1–B5 markers and their held intent, so it is the natural one —
   add it to the expectation table, and add a validation line. Without this, a mechanical
   implementer ships the item with a stated success criterion half-met.

### Major

3. **The 26/16 key-movement figure is probe-measured but presented as pre-committed and used as a
   pass/fail check.** — SC-6 discipline.
   It sits under *"Expected-output derivation plan (SC-6)"*, whose opening sentence claims every
   value is derived from the ruled table or read from authored source, and reappears as Validation
   criterion 5 (*"the recorded key movement is exactly the 26/16 sets above"*). Its actual source is
   probe Result 4. That is the inversion SC-6 exists to stop, even though it lands on an
   `[INFERRED]` spec item rather than a ruled one. The repair is cheap because the numbers are
   genuinely derivable from source: only 13 of the 14 layers carry geometry calc usages consuming
   their radii (`axis_region` has none — `radial_build.sysml:57-75`), so 13 × 2 = **26**
   `DESIGN_ATTRIBUTE` keys exist today and leave; **16** arrive = 13 thicknesses +
   `axis_region.inner_radius` (`tf_coil.thickness` was already a key) + `pump_capacity_each` +
   `pumping_speed_agrees__rel_tol`. Either state that derivation in the design, or demote 26/16 to
   measured-and-recorded alongside module count. Do not leave it presented as derived.
   Two riders: (a) the design's phrase *"14 radial free parameters"* is loose — there are 15 free
   radial parameters, 14 of which arrive; (b) add one line saying the snapshot bytes are a
   **capture, not an expectation**, so committing them before the expectations does not read to a
   later auditor as a run feeding an expectation.

4. **The PROVENANCE edit list under-covers §5, and the item's one out-of-27 source edit has no live
   record.** — Spec Compliance / Surfacing.
   §5 is the fixture's live home for the human unit claim. The design names only *"§5's now-false
   claim that a constraint formal cannot carry unit text"* (`PROVENANCE.md:345-348`). Three things
   are needed there and only one is listed:
   - (a) The sentence *"Both gates take the dimensionless, unit-blind library band"* (`:345`) goes
     stale — there are three gates after A9.
   - (b) §5 carries one subsection per gate (A2 at `:350`, A3 at `:359`). A9 needs one, carrying the
     ruled unit-check cells: m³/s on both compared sides, `count` dimensionless,
     `rel_tol` dimensionless (`owner-disposition.md` A9 unit-check column). This is the human
     checkpoint the ruled table says design review is responsible for — it is met in this review
     against the authored source, and it needs a live home.
   - (c) **D3's `tf_coil.thickness` comment edit.** It is the item's only source edit outside the
     ruled 27, the design flags it for the reviewer, and the orchestrator ratified it — but it is
     recorded only in `design.md`, which archives with the item. §5 is exactly where a
     unit-annotation edit belongs. Record what changed, that the provenance text was preserved
     inside the amendment, and why it was necessary (the computed-attribute lane reads the consumed
     attribute's own declaration).

5. **The one-ULP float drift is surfaced only in a document that archives with the item.** —
   Surfacing / capture-fidelity law 4.
   The analysis is right and I have no disagreement with it: decimal equality holds, four layers
   drift by −8.88e-16, the chain re-converges at `ht_shield.outer_radius`, `bioshield.outer_radius`
   is exactly `8.55`, the `tf_coil` legs are exact so the manifest's 16-digit `cooling_power` is
   untouched, and no generated byte moves. The problem is placement. Law 4 wants it loud where a
   later reader finds it, and that reader opens `PROVENANCE.md`, not an archived design. Add it to
   the PROVENANCE edit pass: which four layers, that the chain re-converges, that no generated byte
   changes, and that an execution expectation moving is the surfacing event rather than a number to
   absorb.

6. **Required Invariant 6 contradicts D3.** — Data Structure Clarity.
   As written (*"every free radial parameter … carries unit text that all its consumer lanes agree
   on"*) it is false for 13 thicknesses and `axis_region.inner_radius`, which will carry no readable
   unit text, and following it literally would produce the 13 edits D3 explicitly refuses as
   unauthorised churn. Restate it as the property that is actually true and actually load-bearing:
   *every attribute reached by more than one consumer lane carries unit text those lanes agree on.*

### Minor

7. **D4 says "a two-line `//` block"; the concrete shape shows three lines** for both the
   `inner_radius` and the `outer_radius` derivation. Reconcile — an implementer copies the concrete
   block.

8. **`expected_study_outcomes.gate_feasible_candidate._note` goes stale and is not in the edit
   list.** It reads *"A2 alone turns satisfied at p_fusion >= 16000; both gates satisfy at 20000"*;
   with A9 asserted there are three. The design's row 2 names `gates_satisfied` but not the note.
   Same pass, same file.

9. **Make the new falsification cases occurrence-scoped, and say which occurrence.** Each layer
   will carry *two* comment blocks (one per derivation), so *"strip one layer's comment block →
   exactly one problem"* needs to name which. And the existing missing-derivation case uses an
   unbounded `str.replace` (`test_gated_manifest_identity.py:143-147`), which against
   `radial_build.sysml` would remove all 14 identical A6 lines and produce 14 problems, not one.
   The new cases need a count-scoped or block-scoped replacement.

10. **State what a missing or duplicated owning-block header does.** The design specifies the happy
    path (header line, brace depth, exactly one match inside) but not the failure. It must be a
    reported problem, not a skip or a file-wide fallback — otherwise the fail-closed property rests
    on an unstated default. Related: record the hidden bet named in Dimension 7 (one findable
    owning block per derivation) beside the other bets.

11. **Name collision with the fixture's own D3.** `PROVENANCE.md` §5 is headed *"Per-gate unit
    reasoning (D3)"* — Item 5's design decision, unrelated to this design's D3. Disambiguate in the
    edit instruction so the implementer edits the right thing.

12. **File one unowned backlog line for the per-dimension band cost.** `ProductWithinBand` must be
    authored per dimension because a constraint port's unit comes from the formal's own declaration.
    The design records this in the NOTE; the NOTE archives with the item. One backlog line makes the
    cost findable when someone next wants a product band over a different dimension. Phrase as a
    decision record, not an instruction (capture-fidelity law 3).

---

## Recommendations

1. Write `ProductWithinBand`'s predicate into the design (Critical 1) — it is the single change that
   converts the A9 NOTE from an assertion into something a reader can check against the ruled row.
2. Give SC-3 side 1 a named artifact, a change-list row, and a validation line (Critical 2).
3. Fix the SC-6 provenance of the 26/16 figure (Major 3) — derive it from source in the design, or
   demote it to measured-and-recorded. Do not leave a run-measured number inside the
   derived-not-measured section and then check against it.
4. Extend the PROVENANCE edit pass to cover §5's three obligations, the float drift, and D3
   (Majors 4 and 5). All of it lands in the single pass the design already plans, so this is scope
   the design has already priced.
5. Restate Required Invariant 6 so it stops contradicting D3 (Major 6).
6. Sweep the minors into the same revision — they are all one-or-two-line edits, and 9 and 10 are
   the ones that protect the per-occurrence fail-closed property the whole prover extension exists
   to buy.

Nothing here requires re-probing, re-measuring, or re-deciding anything. Every fix is an edit to the
design document.

---

## Resolutions

*(Stage 4 — filled in as the owner/orchestrator resolves each issue. Empty at first write.)*

---

**Overall:** Revise
**Next Steps:** Once resolutions are recorded here, re-run `/_my_design` (or return to the
design-agent session) and point it at this review to incorporate. The reviewer does not edit the
design. No fix in this list is blocking in the sense of needing new evidence — all six of the
Critical/Major items are document edits — so `/_my_plan` can follow immediately after the design is
updated.
