# Spec Review: Authoritative Source-Identity Contract (SOURCE-IDENTITY Item 3)

**Spec:** `.project/active/source-identity-contract/spec.md`
**Contract:** `claude-pack/commands/_my_spec.md`
**Review File:** `.project/active/source-identity-contract/spec-review.md`
**Date:** 2026-08-05

---

## Reality Check

**Sound.** The spec is about the right work item (Item 3: the semantic contract before any fix
design), the Problem section is materially accurate, and the core requirements are directionally
correct. I verified the load-bearing claims against code and evidence rather than trusting them:
the L2 rescue-aware exemption exists exactly as described (`_owner_covers_name`,
`level2_structure.py:309-355`, applied at `:402`, suppressing on a same-named attribute or sibling
calc output); the cited verification rows REQ-IR-06/07, REQ-SVM-01/02/04, REQ-CL-05, REQ-VBR-10
all exist and are the right rows to supersede; the 40-of-75 reconstruction failure, 37-fixture
recapture, ~124 external + 91 fixture self-binding counts, and both owner-verbatim quotes
(including the preserved "quesiton" typo) all match their sources. Design would not be badly
misled by this spec. The findings below are about provenance grades and two silently pre-settled
owner rulings, not about direction.

---

## Audit

### Lens 1 — Faithfulness

**L1-1 · Question to the user:** SI-14 (blocking self-binding diagnostic in `agentic-mbse`
validation) is tagged `[NEED]` with "Source: owner request, 2026-08-05, to add the self-binding
pattern to the validation stack." I cannot find that request recorded anywhere: the epic's
ratified Item-3 decision list has seven entries and none is the validation-stack request, and the
SI-17 quote (which is owner-verbatim) is about documentation, ending in an ellipsis. `[NEED]` is
settled-eligible, so the grade matters. **Did you actually state this in the spec session?** If
yes, the spec should carry your words (or at least this confirmation) the way SI-01 and SI-17 do —
the elided part of the SI-17 quote may be exactly where it lives. If it's really an inference from
the epic's Item-3/Item-4 scope text, it should be `[INHERITED: epic Item 3 scope]` (agent-grade,
ratified), not `[NEED]`.

**L1-2 · Question to the user:** SI-04's closing sentence — "Equal inherited default values do not
collapse distinct concrete occurrences" — resolves a question both Item-2 artifacts explicitly
flag as an **open Item-3 owner ruling**: "whether an un-overridden def default is one source or
one per occurrence is an Item-3 ruling, not a census fact" (`corpus-census.md:114-116`;
`route-evidence findings.md:90-92` lists it first among "open rulings flagged for the
checkpoint"). The spec settles it under a `[HARD]` standards grade with no owner disposition and
no Open Questions entry. The standards genuinely do say a definition default applies per
constructed instance (Part 1 §7.13.4, quoted at `sysml_ruling.md:30`) — so the *instance
semantics* are `[HARD]`. But the step from "distinct instances" to "distinct runtime sources /
distinct public study inputs" is a product ruling about the generated boundary, which the
standards do not make. **Did you rule on this (e.g., in the spec session), or did the spec resolve
it silently?** If ruled, record the disposition with owner grade; if not, it belongs in the
decision checkpoint, not in a `[HARD]`.

**L1-3 · Question to the user:** Same shape for SI-10's second sentence. The unbound-formal
per-usage `LIBRARY_DEFAULT` class (58 entry points, e.g. solar's 8× `fab_factor`) was handed up as
"a distinct, currently-legitimate class (ADR-001 per-usage), **for Item 3 to ratify or overturn**"
(`route-evidence findings.md:66-67`). SI-10 states the ratification as an accomplished fact under
`[INHERITED]` — but inherited items are by definition not settled, and the cited sources
(discriminator evidence, invariant 22) support the *overridable-default* part, not the *per-usage
vs shared* part. **Is per-usage minting for unbound formals your ruling?** If yes, it needs owner
grade in the decision register; if it's still open, it should appear as a checkpoint decision.

**L1-4 · Rewrite request:** SI-08 under-grades its strongest source. The epic's mission invariant
("one semantic source occurrence maps to exactly one runtime source across all consumers") is
`[OWNER]`-graded in the epic — owner-originated, settled. The capture-fidelity absorb mapping
sends `[OWNER]` → `[NEED]`, but SI-08 carries `[INHERITED]`, which reads as
challengeable-on-evidence — the opposite of its actual authority. The spec's central invariant
should wear its real grade. (Under-grading is the safe direction, but here it weakens the one
requirement everything else hangs from.)

### Lens 2 — Problem & Approach

**L2-1 · Question to the user:** The **bare-renamed form** (`in r_in = R` — form 1c) is never
mentioned in the spec, yet it is the most common *working* spelling in the corpus: 103 external +
45 fixture occurrences, more external use than the qualified form (zero) and the chain form
combined. SI-03 names only owner-qualified and chain forms as supported; a strict reader of the
contract could conclude bare-renamed is undispositioned or unsupported. It also shares the
qualified form's def-level-referent problem (the referent is the definition attribute; the
concrete occurrence must be recovered from context — `authoring-form-table.md`, form 1c row).
**Should SI-03 (or the decision-register obligation) explicitly cover it?** Success Criterion 1's
"every observed authoring form" arguably nets it, but the requirement text is where designers will
look.

**L2-2 · If-then tradeoff:** SI-03 supports both correct forms "according to their actual,
distinct meanings," and the def-level referent's meaning at a concrete occurrence is exactly the
normatively *unsettled* cell: the SysML ruling's residual ambiguity (`sysml_ruling.md:32`) says
Part 1 never illustrates what value an externally-held def-level reference observes under a given
occurrence — and that gap is the same def-vs-occurrence split that produces Path B. This is fine
**if** "occurrence behavior … for every supported form" in Success Criterion 3 is understood to
force the acceptance matrix to define the def-level-referent-at-occurrence cell explicitly (for
the qualified form *and* bare-renamed, per L2-1). It's a real pipeline gap **if** the matrix
author reads "occurrence behavior" narrowly. One clause in SC-3 or SI-03 naming this cell would
close it.

### Lens 3 — Pipeline Risk

**L3-1 · Direct claim:** An epic obligation is dropped. Epic Item-3 scope 4 requires publishing
"the authoritative source-identity matrix **and evidence coordinate** that downstream item specs
must inherit rather than restate." The evidence-coordinate concept (from the lifecycle contract's
proof standard) appears nowhere in the spec — not in SC-3, not in the requirements. Items 4–8
inherit their acceptance anchoring from it; if Item 3 doesn't publish it, each downstream spec
re-invents its own evidence standard, which is the failure mode the proof standard exists to
prevent.

**L3-2 · Direct claim (one decision with L1-2/L1-3):** The pre-settled rulings also create a
process contradiction inside the spec. Success Criterion 1 requires the decision register to
disposition "every remaining source class without treating approval of an agent recommendation as
owner origin" — but SI-04 and SI-10 already hard-code the answers to the two classes the spikes
flagged as open, so the checkpoint for those classes becomes a rubber stamp of the spec's own
text. Resolving L1-2/L1-3 resolves this.

**L3-3 · Rewrite request:** SI-16's sentence "Codegen independently verifies these conditions and
fails closed if authoring validation was not run" can be read as requiring codegen to *detect
whether validation ran* — a run-order dependency the lifecycle contract deliberately doesn't have
(validation is diagnostics-only; codegen enforces independently, always). What needs to be true:
codegen's enforcement is unconditional and does not depend on validation having run at all. Ask
the spec agent to remove the "if … was not run" conditional framing.

### Lens 4 — Hygiene

No material findings.

### Lens 5 — Reader Comprehension

No findings beyond L3-3's ambiguity. The spec is dense, but its reader has the full epic context,
every coined term resolves to a cited artifact, and the Problem section builds the frame before
the requirements use it.

---

## Engagement Summary

**Overall take:** This spec is faithful where it counts — every code-facing claim, count, and
verbatim quote checked out, and the requirements trace cleanly to the spikes and the ratified epic
decisions. The real faults are provenance faults: two rulings the spikes explicitly reserved for
you are silently settled in requirement text (one as `[HARD]`, one as `[INHERITED]`), and one
`[NEED]` rests on an owner request that isn't recorded anywhere. Those are exactly the failure
modes an authority-contract item exists to prevent.

**Here's what I need you to weigh in on:**

1. **[L1-2, L1-3, L3-2]** The two open owner rulings the spec pre-settles: multi-occurrence
   def-default sharing (SI-04: distinct occurrences = distinct sources) and per-usage minting for
   unbound formals (SI-10: ADR-001 stands). Confirm each as your ruling — then they get owner
   grade in the decision register — or reopen them as checkpoint decisions.
2. **[L1-1]** Did you actually ask for the self-binding pattern in the validation stack (SI-14's
   `[NEED]`)? Confirm (and ideally supply the words) or re-grade to `[INHERITED]`.
3. **[L2-1]** The bare-renamed form (`in r_in = R`, 103 external occurrences) is undispositioned
   in the requirement text. Should SI-03 cover it explicitly?
4. **[L3-1]** The epic requires Item 3 to publish an evidence coordinate alongside the acceptance
   matrix; the spec dropped it. Add the obligation?
5. **[L1-4, L3-3, L2-2]** Three smaller edits for the spec agent: re-grade SI-08 to `[NEED]`
   (owner mission invariant), fix SI-16's "if validation was not run" phrasing, and name the
   def-level-referent-at-occurrence cell in SC-3 or SI-03.

---

## Resolutions

- **L1-1 — Accepted.** SI-15 (formerly SI-14) now carries the owner's exact validation-stack request.
  The request existed in chat; the defect was its omission from the durable artifact.
- **L1-2 — Accepted and resolved.** SI-04 now contains only the standards-forced instance behavior.
  SI-05 separately records the product ruling: concrete occurrences remain distinct sources unless
  the model explicitly binds them to one shared source. The recommendation was ratified by the
  owner on 2026-08-05 and remains agent-grade under the capture-fidelity rule.
- **L1-3 — Open.** The per-usage `LIBRARY_DEFAULT` behavior has been removed from settled requirement
  text and placed in the owner checkpoint under Open Questions.
- **L1-4 — Accepted.** The mission invariant is now SI-09 `[NEED]`, absorbed from the epic's
  `[OWNER]` criterion.
- **L2-1 — Accepted with count correction.** SI-03 now dispositions `in r_in = R` explicitly. The
  measured count is 58 external-corpus occurrences plus 45 fixture occurrences, 103 total.
- **L2-2 — Accepted.** SI-03 and SI-05 jointly name the definition-level referent at a concrete
  occurrence and its public-source behavior.
- **L3-1 — Accepted.** The Success Criteria and SI-23 now require the acceptance matrix's evidence
  coordinates and enumerate their fields.
- **L3-2 — Partially resolved.** The definition-default ruling is recorded with exact provenance;
  the unbound-formal ruling remains visibly open instead of being pre-settled.
- **L3-3 — Accepted.** SI-17 now requires unconditional codegen enforcement independent of whether
  authoring validation ran.

Provenance note: owner approval of an agent recommendation remains agent-grade. It does not become
owner-originated merely because the owner ratified it.

---

**Verdict:** Revise
**Next Steps:** Once resolutions are recorded here, re-run `/_my_spec` (or return to the
spec-agent session) and point it at this review to incorporate. The reviewer does not edit the
spec.
