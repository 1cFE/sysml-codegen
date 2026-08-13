# Spec Review: Coverage Report and TEAx Policy (CONSTRAINT-SEMANTICS Item 3)

**Spec:** `.project/active/constraint-coverage-policy/spec.md`
**Contract:** `claude-pack/commands/_my_spec.md`
**Review File:** `.project/active/constraint-coverage-policy/spec-review.md`
**Date:** 2026-08-12

---

## Reality Check

**Sound.** The spec is about the right work item, the Problem section is accurate against the
code I could read, and the inherited rulings are captured faithfully — the six states, the
precedence, the form-not-predicate denominator test, the two-tier split, and the vacuous-gate
consequence all match the lifecycle contract's "Headline states and coverage truth" subsection
and invariants 32/33/48/61 word for word in substance. All seven epic Item 3 success criteria
are carried, plus two the epic did not state (the LC-E12 asserted-vacuous zero-input case and
the M-1 four-assertion hand-off). Design would not be misled by treating this as the contract.

What I verified in code this session (all confirmed unless noted):

- `report_aggregator.py.jinja2:44-51` — headline ladder is violation → indeterminate →
  `all_satisfied` on any non-empty `results` → `not_assessed`. Never consults exclusions. ✓
- `constraint_types.py.jinja2:23-29` — `ConstraintReport` carries exactly
  `catalog_fingerprint` / `assessed_count` / `headline` / `results`. ✓
- `project.py:893-894` — `if not constraint_outputs: return`, before the aggregator is minted. ✓
- The template's zero-input shape (`{% if not constraint_ids %} pass`, `else: "not_assessed"`)
  already exists, as the spec claims. ✓
- `resolution/models.py` — `has_executable_content` (`:597-613`) and
  `ships_constraint_machinery` (`:644`), with the Item-3-supersession note in the docstring
  exactly as the spec describes. ✓
- `tests/execution/` — four `all_satisfied` sites, at
  `test_constraint_verdicts_exact_route.py:171,416,540` and `test_fusion_tea_real_teax.py:245`. ✓
- `SI_CONSTRAINT_BLOCKED` is raised inside the `for scope in scopes:` loop, so the spec's
  inference (a BLOCKed asserted usage that expands to nothing emits no halt) is **correct** —
  but the line cite is stale. See L1-1.

Findings below are refinements and two real internal tensions, not a challenge to the item.

---

## Audit

### Lens 1 — Faithfulness

**L1-1 · Direct claim:** The `SI_CONSTRAINT_BLOCKED` cite is wrong. The spec's `[INFERRED]`
bullet under "What the report must say" cites `elaborate.py:1018-1029`; the diagnostic is raised
at `elaborate.py:1097-1108`, inside the `for scope in scopes:` loop that opens at `:1083`. The
*claim* is right — that's exactly why a non-reaching BLOCKed asserted usage produces no halt —
so this is a citation fix, not a logic fix. It matters because this bullet is the spec's stated
reason a whole fixture class cannot be built, and design will re-grep it.

**L1-2 · Direct claim (the TEAx flag is honest, and I could not do better):** The "Surfaced, not
resolved" note says TEAx is outside the author's sandbox. **My session is sandboxed the same
way** — `/home/reid/1cfe/teax` is not readable here, so I could not spot-verify
`CANONICAL_HEADLINE` in `evaluation/projection.py`, the `study/policy.py` dispatch, or
`ACCEPTED_CATALOG_SCHEMA_VERSIONS`. The flag is accurate and the instruction to re-grep before
relying on a line number is the right disposition. Two things soften the risk, worth stating so
the reader can size it: the `policy.py:65-68, 112-116` citation traces to the research record
(`…20260812-101200_constraint-semantics-end-to-end.md:142, 334`), which is in-repo and says what
the spec says it says; and the two-vocabulary obligation itself rests on contract authority
(umbrella spec-review L1-1, "Headline states and coverage truth" → "Both vocabularies"), not on
the code cite. So a wrong TEAx line number costs design a re-grep, not the requirement.

**L1-3 · Question to the user:** Under "Cross-repository and scope", *"All TEAx work happens on
a branch. TEAx `main` is never committed to"* is tagged **[HARD]** with the parenthetical
"(owner instruction, align record 2026-08-12)". By the grade table an owner instruction is
`[NEED]`; `[HARD]` is reserved for what an interface, physics, or the existing system forces.
Both are settled-eligible so nothing downstream breaks — but do you want the grade corrected, or
is your read that the pinned-`main` working agreement is a system constraint here?

**L1-4 · Rewrite request:** LC-E05 and LC-E06 are listed in Required Reading but no requirement
cites either. LC-E06 ("excluded, unassessed, and non-reaching usages … never masquerade as
executed constraints **or vanish from coverage**") is the natural source for the compact
accounting's excluded/non-reaching counts and reason histogram, which the spec currently sources
only to umbrella Q5. Ask the spec agent to carry LC-E06 into that requirement's provenance, or
to drop E05/E06 from Required Reading if nothing in this item consumes them.

**L1-5 · Direct claim:** The M-1 success criterion understates one of the four sites. It says the
four `all_satisfied` assertions are "moved to the new vocabulary and each now asserts a coverage
claim." Three are bare headline asserts. The fourth,
`tests/execution/test_fusion_tea_real_teax.py:244-259`, is a **whole-dump equality** whose own
docstring says "a field the report starts carrying has to be accounted for here before this
passes." Moving that one means hand-writing the expected coverage block for the real-TEAx route —
which is precisely the "capture expected outputs before running confirmation tests" obligation
in the Sequencing `[NEED]`. The criterion as phrased reads like a token swap.

### Lens 2 — Problem & Approach

**L2-1 · Question to the user:** The spec parks invariant 50's durable-study-store transition
("a migration that proves old and new artifact equivalence, or the old store archived as lineage
with a new store begun") in Open Questions as design's call. Those two routes have different
consequences for **your existing study results**: one keeps them queryable in place, the other
retires them to lineage and starts an empty store. That looks like an owner disposition wearing a
design label. **Do you want to pick the route now, or explicitly delegate it to design?** If the
answer is "there is no durable store with results worth keeping yet," say so and the question
evaporates — but the spec should record that, because design cannot check it from this repo.

**L2-2 · If-then tradeoff:** This is one item spanning two repositories, a generated-schema
version bump, a package-contract change, a TEAx re-vendor with a fail-closed window, a new
per-study config surface, and a durable-store transition — at the epic's 2-day estimate. That is
fine **if** the durable store is small or empty and the TEAx config surface is a one-line policy
override. It is undersized **if** L2-1 turns into a real migration. The spec does not have to
resize itself; it should note which way L2-1 resolves as a sizing input.

### Lens 3 — Pipeline Risk

**L3-1 · Question to the user (highest stakes):** **Is coverage one axis with the headline, or
two?** The spec inherits both of these without noticing they pull apart:

- Precedence (invariant 33, LC-E11): violation → indeterminate → full satisfaction → partial
  coverage → not assessed. So a model with one violated gate and sixty unassessed ones reads
  `violation`, and the coverage gap is invisible in the headline.
- The compact accounting requirement lists "**the coverage state**" as one of the embedded
  fields, alongside the totals — implying a coverage value that exists *independently* of the
  headline.

Umbrella Q6 pushes toward the two-axis reading: "coverage numbers land in durable case records
**regardless**." But Success Criterion 1 pushes the other way: "five report headline values …
each proven by a test that no other state satisfies" treats the headline as the whole state
space. Design will pick one by accident. Concretely, the decision is: **can TEAx tell "rejected
on physics, fully covered" from "rejected on physics, and sixty gates were never checked"?** If
yes, the report carries a coverage state field that survives a violation headline, and SC-1's
"no other state satisfies" phrasing needs rewording. This is the same class as the
all-gates-inapplicable crossing the spec *did* surface, and it deserves the same treatment.

**L3-2 · Direct claim:** The name `assessed_count` is about to mean two different things in one
model. Today `ConstraintReport.assessed_count` is `len(results)` — a count of **concrete
occurrences** (`report_aggregator.py.jinja2`, `assessed_count=len(results)`). The spec's compact
accounting requires an "assessed count" at the **usage** tier, next to the authored-usage total.
The spec's own two-tier requirement says the tiers "are never conflated in one number" — but it
does not notice that the existing field name is already claimed by the other tier. Either the
old field is renamed (schema break, which this item is already versioning) or the new one needs a
distinguishing name. Flagging it in the spec keeps design from shipping two `assessed_count`s.

**L3-3 · Direct claim:** Three obligations have no success criterion that would catch a
violation. (a) Invariant 41's freeze / defensive isolation of the **new** nested coverage block —
the spec requires it and explicitly declines to inherit the pre-existing nested-model violation,
but no criterion tests it. (b) Invariant 50's durable-store route (see L2-1) — a requirement with
no proof obligation. (c) "Never bump TEAx first" — the landing order is `[HARD]` and the only
thing that would catch a violation is the cross-repo compatibility test *after* the fact. Not all
three need criteria, but (a) is cheap to pin and (b) is the one that silently reassigns identity
if it goes wrong.

**L3-4 · Question to the user:** The `[INFERRED]` bullet superseding `ships_constraint_machinery`
ends with "and it stays in one place, so the three generation seams that read it cannot drift
apart again." The *rule* (report required whenever any constraint usage is authored) is spec-level
and correct. "Stays in one place" is a design decision about code shape. Harmless if you intend
it as a constraint design must honor; worth demoting to a design note if not.

**L3-5 · Direct claim (the parking is correct):** Both deliberately surfaced items are parked the
right way. The epic scope-4 vs LC-E10 divergence is real — I confirmed LC-E10's amendment text
says the trigger is "the absence of an applicable asserted gate, not the absence of eligible
concrete assertions," and the epic's scope 4 still says "no executable assertions" — and
following the later, more specific contract while flagging the epic for correction at close is
exactly capture-fidelity law 4. The all-inapplicable precedence crossing is likewise genuine:
Appendix C's "Asserted vacuous gate" cell and state 5 of the contract both describe the same
model, and neither yields. Assigning it to design is right *provided* design treats it as a
ruling to publish, not a coin flip.

### Lens 4 — Hygiene

**L4-1 · Rewrite request:** The companion-out-of-scope statement lives under "Cross-repository and
scope" as an `[INFERRED]` requirement, not in Non-Goals. A reader scanning Non-Goals for what this
item won't touch will miss it. The brief asked for it as a stated scope boundary; it should be
visible where boundaries are listed.

### Lens 5 — Reader Comprehension

**L5-1 · Rewrite request:** Two terms carry the whole study half of this item and are never
explained: **keep-for-boundary** and **feed-strategy**. They appear first in a success criterion,
already doing load-bearing work ("Partial coverage defaults to keep-for-boundary; feed-strategy
… only with an explicit config line"), and a reader who does not already know the TEAx study
layer cannot tell whether the default is conservative or permissive. One plain-language clause
at first use is enough.

**L5-2 · Rewrite request:** Success Criterion 1's arithmetic gloss — "Six report states minus one
(state 6 is report-absent by construction) means five report headline values and their six runtime
dispositions" — needs a second read to parse, and it is the criterion that defines the item's
whole test matrix. State the matrix plainly: five report headlines, six runtime dispositions,
each pinned by a test no other state satisfies. (See also L3-1, which may change what this
criterion claims.)

---

## Engagement Summary

**Overall take:** This is a faithful, well-provenanced capture — the inherited rulings survive
intact, the epic's success criteria are carried in full plus two the epic missed, and the two
deliberate surfacings are handled exactly per capture-fidelity. Two real internal tensions
remain, both cheap to fix: whether coverage is a second axis alongside the headline (L3-1), and
an `assessed_count` name that is about to mean two tiers at once (L3-2). Nothing here challenges
the work item.

**Here's what I need you to weigh in on:**

1. **[L3-1]** Can a `violation` report still say how much was covered? If yes, the report has a
   coverage state field independent of the headline, and Success Criterion 1's "five headline
   values, no other state satisfies" phrasing has to change. If no, say so and design stops
   guessing.
2. **[L2-1, L3-3]** Invariant 50's durable study stores: migrate-with-equivalence-proof, or
   archive-as-lineage and start fresh? This has owner-visible consequences and is currently
   filed as design's call. If no store with results worth keeping exists yet, say that instead.
3. **[L3-2]** Confirm that the existing occurrence-tier `assessed_count` gets renamed (or that
   the new usage-tier count gets a distinct name) so the two-tier rule holds in the field names,
   not just in the prose.
4. **[L1-5]** Note that the fourth `all_satisfied` site is a whole-dump comparison on the
   real-TEAx route, so "move the four assertions" includes hand-capturing an expected coverage
   block there — the sequencing `[NEED]` in action.
5. **[L1-3]** Grade call: is "TEAx `main` is never committed to" `[HARD]` or `[NEED]`?
6. **[L1-1]** Accept the `elaborate.py` line-cite correction (`:1018-1029` → `:1097-1108`); the
   inference itself is confirmed correct.

**On TEAx verification:** I could not read `/home/reid/1cfe/teax` either — same sandbox
boundary. The spec's second-hand flag is honest and its re-grep instruction stands. The
load-bearing two-vocabulary requirement rests on contract authority rather than on the
unverified line numbers, so the exposure is a re-grep in design, not a requirement at risk.

---

## Resolutions

Recorded 2026-08-12 by the spec agent, with orchestrator guidance on the four judgment calls
(L3-1, L3-2, L2-1, L1-5). All nine findings resolved in `spec.md`; no finding was declined.

**L1-1 — FIXED.** Cite corrected. Re-grepped this session: `SI_CONSTRAINT_BLOCKED` is raised at
`elaborate.py:1103`, inside the `for scope in scopes:` loop that opens at `:1083`. The spec's
`[INFERRED]` bullet now carries those two line numbers and marks the correction. The inference
itself is unchanged, as the review confirmed.

**L1-2 — ACKNOWLEDGED, no change.** The reviewer independently hit the same sandbox boundary and
reached the same disposition, which is the strongest available confirmation that the flag is
honest rather than a shortcut. The softening the review supplies (the `policy.py` citation traces
to the in-repo research record, and the two-vocabulary requirement rests on contract authority, not
on the line numbers) is already the reason the spec grades that requirement `[HARD]` from the
interface rather than from the cite. Nothing to change; recorded so a later reader knows two
sessions checked.

**L1-3 — FIXED, regraded to `[NEED]`.** The reviewer's read of the grade table is right: `[HARD]`
is for what an interface, physics, or an existing system forces, and "TEAx `main` is never
committed to" is a working agreement the owner stated at launch. Regraded with the reasoning
written beside it, and the note that both grades are settled-eligible so nothing downstream
weakens.

**L1-4 — FIXED.** Both companion requirements are now consumed rather than merely listed. LC-E06
is carried into the compact-accounting requirement's provenance — it is the obligation the excluded
and non-reaching counts discharge ("never … vanish from coverage"). LC-E05 is carried into the
"adds no usage-tier field" requirement, as the obligation that put those fields in the catalog and
that makes this item their consumer rather than a second author. Neither was dropped from Required
Reading.

**L1-5 — FIXED.** The M-1 success criterion now separates the three bare headline asserts
(`test_constraint_verdicts_exact_route.py:171,416,540`) from the fourth
(`test_fusion_tea_real_teax.py:244-259`), names it as a whole-dump equality on the real-TEAx route,
quotes its docstring obligation, and states that moving it means hand-writing the expected coverage
block. Per orchestrator guidance the same fact is recorded in the Sequencing `[NEED]` as its
concrete instance — capture the expected block from the settled semantics first, then run the
route.

**L2-1 — FIXED as a bounded requirement plus an owner-visible escape.** Per orchestrator guidance,
behavior-changing schema migration of durable stores stays out of this item's silent scope: a new
`[AGENT] (orchestrator-ratified, 2026-08-12)` requirement says whichever invariant-50 route design
takes must be **additive or versioned**, and that if design finds neither can be, that is an
owner-visible decision to surface at close, not a design call. The reviewer's "or say no such store
exists" alternative is captured as a new Open Question that design answers first on the TEAx side,
since it cannot be checked from this repo.

**L2-2 — FIXED as a sizing note.** The spec does not resize itself. The new Open Question states
which way it cuts: no durable store worth keeping → the epic's 2-day estimate holds; a real
transition → the estimate is undersized and design flags it then rather than absorbing it.

**L3-1 — RESOLVED as TWO axes** (orchestrator ruling, `[AGENT]` orchestrator-ratified 2026-08-12).
The reviewer is right that the spec inherited both readings without noticing they pull apart. The
ruling, now written into Known Requirements: the **headline** is the single precedence-ordered
summary token, and the **coverage account** is an orthogonal embedded fact, always present and
always reaching the durable case record whatever the headline says. The partial-coverage headline
value is the *summary projection* of the coverage axis, emitted when nothing above it in precedence
fires. So yes — TEAx can tell "rejected on physics, fully covered" from "rejected on physics, and
sixty gates were never checked." It is graded `[AGENT]` rather than `[INHERITED]` because it
derives from Q5's compact accounting and Q6's "regardless" read together rather than restating
either. Success Criterion 1's phrasing was rewritten accordingly (L5-2), and a new criterion pins
the case the tension was really about: a `violation` headline carrying a non-full coverage account.

**L3-2 — FIXED, requirement stated.** The no-conflation constraint is now in the field names, not
just the prose: the compact block's usage-tier count takes a **new, distinct field name**, and the
existing occurrence-tier `ConstraintReport.assessed_count` either keeps its meaning or is renamed
with the schema bump this item already pays. Exact spellings stay design's; shipping two
`assessed_count`s, or one field serving both tiers, does not.

**L3-3 — FIXED for (a) and (b); (c) left as-is, deliberately.** (a) A success criterion now pins
that the new nested coverage block is unmutable from downstream code to invariant 41's standard.
(b) A success criterion now requires the durable-store transition to be *proven* — equivalence
proof, or archived store plus new lineage — with no silent rebind. (c) "Never bump TEAx first" gets
no separate criterion: it is a landing-order instruction, and the honest catch is the cross-repo
compatibility test plus the fail-closed window itself, which is the intended direction. Adding a
criterion would pin a process step, not an outcome.

**L3-4 — FIXED by splitting the bullet.** The spec-level rule (a report is required whenever any
constraint usage is authored) stays as the `[INFERRED]` supersession. "Stays in one place" moved to
its own `[INHERITED: Item 2 audit cure A4]` line: it is Item 2's landed constraint, not this spec
inventing code shape — `constraint_catalog is not None` had already meant three different things
across those seams, which is why A4 collapsed them. Superseding what the rule says does not reopen
where it lives.

**L3-5 — FIXED with one added clause.** The review confirms both parkings are correct, with the
proviso that design treat the all-inapplicable crossing as a ruling to publish rather than a coin
flip. That proviso is now written into the surfaced item.

**L4-1 — FIXED.** The companion-out-of-scope statement moved to Non-Goals, where boundaries are
listed, keeping its "if design finds a companion surface, that is a surfacing event, not a quiet
edit" clause.

**L5-1 — FIXED.** Both terms are glossed at first use in the success criterion: keep-for-boundary
is the conservative disposition (candidate retained to inform the feasible boundary, results not
fed back to steer the search); feed-strategy is the permissive one (what a fully-covered satisfied
candidate gets today).

**L5-2 — FIXED.** The arithmetic gloss is gone. The criterion now states the matrix plainly: five
report headline values (the sixth state is report-absent by construction) and six runtime
dispositions, each pinned by a test no other state satisfies.

---

**Verdict:** Revise
**Next Steps:** Record resolutions above by finding ID, then re-run `/_my_spec` (or return to the
spec-agent session) pointed at this review to incorporate. The reviewer does not edit the spec.
