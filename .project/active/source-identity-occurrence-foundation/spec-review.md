# Spec Review: Semantic Identity and Occurrence Foundation (SOURCE-IDENTITY Item 4)

**Spec:** `.project/active/source-identity-occurrence-foundation/spec.md`
**Contract:** `claude-pack/commands/_my_spec.md`
**Review File:** `.project/active/source-identity-occurrence-foundation/spec-review.md`
**Date:** 2026-08-07

---

## Reality Check

**Sound.** The spec is about the right work item, and its factual base held up under
verification. Every code-facing claim checked true against the code, not the docs:
`SNAPSHOT_FORMAT_VERSION = 5` (`src/sysml_codegen/snapshot/__init__.py:30`), exactly 37 committed
extraction snapshots, the tripwire reports without repairing
(`resolution/supplied_values.py:622-682` — warning only, value falls through unapplied), capture
serializes post-rewrite state (`snapshot/capture.py:48` runs the full pipeline; `pipeline_builder.py:368`
clears `source_path`) while `graph_rebuild.py` has no rewrite stage, the loader already fails closed
on version mismatch (`snapshot/loader.py:731-736`), and the rescue-aware self-binding exemption
exists in `agentic-mbse` (`validation/level2_structure.py:358-370` — errors only when no same-named
covering feature exists, which is exactly the exemption SIF-13 reverses). The "40 of 75" figure
matches Item-2's census (35/75 reconstruct). SIF-12's cell list is exactly the set of Appendix C
cells whose certification says `BLOCKED(... → Item 4)` — I checked each one. The two owner-verbatim
quotes appear verbatim in the contract. Tags are honest and the settled items are owner-grade.

The findings below are boundary and wording defects, not direction defects.

---

## Audit

### Lens 1 — Faithfulness

**L1-1 · Direct claim:** The spec drops an obligation the authority states twice. Epic Item-4
scope 5 says "remove the current rescue-aware exemption **and reverse its wrong-oracle tests**,"
and the contract's L2 obligation says "the current rescue-aware exemption ... **and its
wrong-oracle tests are corrected**." SIF-13 and success criterion 8 capture the diagnostic outcome
(blocking, never suppressed by a same-named feature) but never mention correcting the existing
`agentic-mbse` tests that certify the rescue behavior as expected. One could argue reversing the
check forces the tests to change anyway — but "the tests are corrected" is a named deliverable in
the inherited authority, and a designer reading only this spec could satisfy it by xfailing or
deleting the old tests without replacing the oracle. Add the inherited obligation (or state
explicitly where it is owned if not here).

**L1-2 · Question to the user:** SIF-12 says Item 4 owns "C14's identity-authority derivation."
The contract cell says `UNPROVEN — authority derivation owed (→ Items 4/5)`, and adjacent-work
register row 6 assigns "make synthesis derive from the one semantic identity" to **Items 4/5**
jointly — because C14's convergence is carried today by SVM occurrence-attribute synthesis, and
rerouting that synthesis is cutover-shaped work. Does Item 4 own the full derivation (pulling part
of Item 5's cutover forward), or only the identity input that Item 5's cutover then consumes? As
written, a designer could read SIF-12 as license to rework `enrich_graph_design_attributes` inside
Item 4.

**L1-3 · Rewrite request (tag precision):** SIF-13 is tagged `[NEED]` on the strength of the
owner's 2026-08-05 quote — which supports "add both patterns to the agentic-mbse validation
stack." The non-suppression clause ("a same-named outer attribute or sibling output never
suppresses the diagnostic") is not in the quote; it comes from contract invariant 59. The clause
is correct and uncontested, but under capture-fidelity it is `[INHERITED]` content riding inside a
`[NEED]` item, and `[NEED]` is settled-eligible. Either split the clause out with its own source
tag or note inline that the suppression clause inherits from invariant 59. Low stakes; structural.

### Lens 2 — Problem & Approach

**L2-1 · If-then tradeoff:** Item 4 bundles a lot that must land atomically: snapshot format
migration + atomic 37-snapshot recapture + the occurrence bridge + the nested-override behavioral
repair + roughly 15 fixture coordinates + validation changes in a second repository. The epic
ratified this boundary (2026-08-07 sequencing correction), so I am not relitigating it — the
single-version loader genuinely forces the recapture to ride the format change. But **if** the
cross-repo `agentic-mbse` validation work has no hard dependency on the snapshot format cutover
(and I see none — the diagnostics are authoring-side), **then** the spec could say so, giving
design/plan license to phase it independently rather than inside the atomic cutover. Worth one
sentence; otherwise the plan inherits a bigger atomic unit than the loader actually forces.

### Lens 3 — Pipeline Risk

**L3-1 · Question to the user:** Success criterion 7 says the work must "leave one
occurrence-to-definition bridge and **no second part-structure walker**." That is end-state
phrasing, and it collides with the upstream evidence: adjacent-work register row 3 says "the three
concrete-instance walkers are still present" and explicitly leaves their consolidation to
`[CONSTRAINT-ARCH-UNIFY]` — which the spec's own Non-Goals exclude. (My code check found one true
occurrence-walking index, `analysis/part_instance_index.py`, plus a frozen replay stand-in and the
Item-10 binding rewrites in `pipeline_builder.py` — so the count depends on what you call a
"walker.") Read literally against the register's counting, SC 7 is unsatisfiable without doing the
ARCH-UNIFY consolidation; read charitably, it means "introduce no second one." An auditor will
read it literally. Which do you mean? SIF-06 already has the right phrasing ("no parallel walker
or bridge may be **introduced**"); SC 7 should match it.

**L3-2 · Question to the user:** Success criterion 9 requires "no unreviewed generated-output
change," while success criterion 6 requires atomically recapturing all 37 snapshots and the
Non-Goals defer the recaptured snapshots' semantic-diff review to Item 6. If recaptured snapshots
count as generated output, SC 9 and SC 6 contradict each other; if they don't, SC 9 never says
what "generated output" covers (graph baselines? generated packages? parameter schemas?). One
sentence defining SC 9's scope — e.g. "committed graph baselines and generated-package outputs are
byte-stable except reviewed changes; the snapshot recapture is exempt per the ratified 2026-08-07
sequencing decision, with review owed to Item 6" — closes the hole the audit stage would otherwise
fall into. (Related known wrinkle: a full recapture rewrites every `captured_at` timestamp; the
byte-identity gate discipline for that is established but unreferenced here — fine to leave to
design.)

**L3-3 · If-then tradeoff:** For cells whose behavioral flip lands *after* Item 4, the spec fixes
the fixture keys but not the expectation policy. C26 is `CONTRADICTED_AT_HEAD` and its resolution
repair is Item 5's cutover; C14's derivation likewise straddles 4/5 (see L1-2). Does an Item-4
fixture for such a cell assert the corrected topology (failing/xfail until Item 5) or pin the
current defect (flipping later, as Item 2's kept tests deliberately do)? **If** the Item-2
precedent (defect pins that flip in Items 4–6) is the intended policy, one sentence saying so
removes a real two-engineers-build-different-things ambiguity; **if not**, this is a spec-stage
decision, not a design one, because it defines what "has a concrete fixture" in success
criterion 5 means for those cells.

### Lens 4 — Hygiene

**L4-1 · Rewrite request:** SIF-09 is a statement of current-state fact ("Current version-5
snapshots cannot satisfy the new identity contract ... 40 of 75"), not a requirement — nothing in
it says what must be true of the work. Its content also restates Problem paragraph 3 nearly
clause-for-clause, and "40 of 75" now appears in two homes. Every fact in it verified true, so
nothing is lost by fixing the shape: either fold it into the Problem section (its natural home) or
rewrite it as the obligation it implies ("the design must not derive identity from version-5
evidence; the format advances" — which SIF-10 already mostly says). One home per idea.

### Lens 5 — Reader Comprehension

**L5-1 · Rewrite request (minor):** The Problem section uses "model-derived mint cells" without
anchoring "mint" — the term is Item-2 vocabulary for "per-consumer entry-point minting," and a
reader outside that thread cannot decode it from this document. One parenthetical at first use
("cells where the pipeline mints a per-consumer public input") fixes it. The rest of the spec's
density is earned — the vocabulary is the contract's own and is anchored by citation.

---

## Engagement Summary

**Overall take:** This spec is faithful to a demanding authority chain — every code claim, cell
assignment, and quote I checked was exact, and the tags are honest. What it needs is boundary
sharpening, not rework: two success criteria are phrased in ways an auditor would read against
you (SC 7's walker end-state, SC 9's output-change scope), one Item-4/Item-5 seam is ambiguous
(C14/C26 expectation policy), and one inherited deliverable was dropped (the wrong-oracle test
correction).

**Here's what I need you to weigh in on:**

1. **[L3-1]** SC 7: does "no second part-structure walker" mean *introduce none* (matching SIF-06
   and the register's sequencing) or *end with one* (which drags in the CONSTRAINT-ARCH-UNIFY
   consolidation your Non-Goals exclude)? Pick one; the spec agent aligns the wording.
2. **[L3-2]** SC 9 vs SC 6: define what "no unreviewed generated-output change" covers, given the
   37-snapshot recapture lands here with its semantic review deferred to Item 6.
3. **[L1-2, L3-3]** The Item-4/Item-5 seam on C14 and C26: does Item 4 deliver defect-pinning
   fixtures that flip at the cutover (Item-2 precedent), or corrected-topology expectations — and
   does "C14's identity-authority derivation" include rerouting SVM synthesis or only feeding it?
4. **[L1-1]** Confirm the wrong-oracle-test correction in `agentic-mbse` belongs in this item and
   have the spec agent add it (the epic and contract both assign it alongside the exemption
   removal).
5. **[L2-1]** Optional: state whether the `agentic-mbse` validation work may phase independently
   of the atomic snapshot cutover, so the plan doesn't inherit a larger atomic unit than the
   loader forces.

Findings L1-3, L4-1, and L5-1 are wording/structure fixes the spec agent can apply without a
decision from you.

---

## Resolutions

- **L1-1 — Resolved.** Revised success criterion 8 and SIF-13 require the rescue-aware
  wrong-oracle tests to be replaced with positive and negative oracle tests. Deletion, skipping,
  and expected-failure markers do not satisfy the requirement.
- **L1-2 — Resolved.** SIF-11 now limits Item 4 to publishing C14's canonical identity input to the
  existing synthesis route. Item 5 owns synthesis rerouting, authority reduction, and cutover.
- **L1-3 — Resolved.** The owner-requested validation coverage is isolated in SIF-12 `[NEED]`.
  Blocking behavior, non-suppression, and test-oracle correction are now SIF-13 `[INHERITED]` from
  lifecycle invariant 59 and the epic's L2 obligation.
- **L2-1 — Resolved.** SIF-16 permits the `agentic-mbse` validation leg to phase independently.
  Only the codegen format/capture/rebuild/37-snapshot migration is atomic; Item 4 still requires
  both legs to complete. This is an agent recommendation ratified by owner, 2026-08-07.
- **L3-1 — Resolved.** Success criterion 7 now prohibits introducing a parallel bridge or walker.
  It does not require general consolidation of existing machinery; that remains with
  `[CONSTRAINT-ARCH-UNIFY]`.
- **L3-2 — Resolved.** Success criteria 9 and 10 now separate Item 4's required recapture review
  from Item 6's final post-cutover semantic certification. Item 4 checks schema/identity
  correctness, live/relocated parity, and unrelated capture drift. Graph baselines, parameter
  schemas, and generated-package outputs remain stable unless an explicit foundation change is
  separately reviewed. The snapshots are not exempt from review.
- **L3-3 — Resolved.** Success criterion 5 and SIF-11 require Item 4 to prove the canonical
  pre-resolution identity and retain an explicit current-defect pin for C14/C26. Item 5 flips the
  downstream expectation. Item 4 neither asserts corrected public topology early nor weakens the
  defect pin with deletion, skipping, or an expected-failure marker.
- **L4-1 — Resolved.** The current-version snapshot fact remains only in the Problem section. The
  duplicate former SIF-09 was removed and the following requirements were renumbered.
- **L5-1 — Resolved.** The first use of “mint” now defines it as creation of a consumer-local public
  input.

**Spec-agent resolution status:** All findings incorporated on 2026-08-07. Product-lens rev 3 is
CLEAR with no findings or smells.

---

**Verdict:** Revise
**Next Steps:** Owner approval of the revised spec, then design.
