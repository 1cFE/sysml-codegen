# Spec Review: Numerical Constraint Executable Profile

**Spec:** `.project/active/numerical-constraint-profile/spec.md`
**Contract:** `claude-pack/commands/_my_spec.md`
**Review File:** `.project/active/numerical-constraint-profile/spec-review.md`
**Date:** 2026-07-18

---

## Reality Check

**Sound.** The spec is about the right work item (the audit's finding-1/2 premise conflict, resolved
by the owner's 2026-07-18 D5 decision to preserve the float data path and narrow admission), and its
Problem section is materially accurate. Every code-facing claim checked out against the code:
profile v2 admits Boolean/string/integer/same-enum equality
(`../agentic-mbse/src/agentic_mbse/sysml/executable_profile.py:64-70`); the generated data path is
float-shaped (audit findings 1–2, re-confirmed at `src/sysml_codegen/analysis/constraint_lowering.py:944`);
codegen preflight halts generation on any blocked assert
(`src/sysml_codegen/analysis/constraint_lowering.py:726-740`); `PROFILE_SEMANTIC_VERSION =
"executable-profile/v2"` exists and codegen hard-pins it (`constraint_lowering.py:720`); the cited
D8, S1 §5, and Design Principle 4 sources all say what the spec says they say. The tags are honest —
the ratified agent recommendations are correctly `[INFERRED]` with the ratification date, not
smuggled into `[NEED]`. The audit findings below are about one real ambiguity, not about direction.

---

## Audit

### Lens 1 — Faithfulness

**L1-1 · Question to the user:** The third `[NEED]` says *both* agentic-mbse model checks *and*
sysml-codegen warn, tagged as an owner statement. The remediation design addendum
(`.project/active/constraint-exec-code-quality-remediation/design.md`, D5) records "warning/continue
behavior stated by owner" but marks the surrounding mechanism as an `[AGENT]` recommendation the
owner ratified. I can't verify from the artifacts whether "warn in both tools" specifically came
from you or was part of the agent's proposal. **Did you state the both-tools placement, or just
warn-and-continue?** If the latter, this item should be `[INFERRED]` (ratified) — it changes
nothing downstream, but the tag should not overclaim.

**L1-2 · Direct claim (minor):** `[HARD]` #1 presents "generated constraint values are
float-shaped" as a fixed fact forcing the totality requirement. It is fixed — but by your ratified
D5 decision, not by physics; the audit explicitly offered the opposite direction (type the data
path). The tag is defensible since D5 is settled, but the requirement should carry D5's
ratification as part of its authority (it currently cites only the audit findings). One citation
addition; no behavior change.

### Lens 2 — Problem & Approach

**L2-1 · Question to the user:** The spec's organizing frame is *numerical purpose*: statements
outside the executor's numerical purpose warn and continue. But the actual admitted set is carved by
*executability through the float path*, and the two don't coincide. Integer equality
(`n_modules == 4`) and same-unit quantity equality are numerically meaningful validity checks —
exactly the owner-stated purpose — excluded for data-path and tolerance reasons (the spec's
`[INFERRED]` #2 is honest about this). That's the right *decision*, but an author who writes
`n_modules == 4` and gets told their statement is "non-numerical" will reasonably think the tool is
wrong. **Confirm the framing intent:** the warning vocabulary (Open Question 1) needs to
distinguish "not a numerical statement" from "a numerical statement this executor cannot evaluate
faithfully" — or deliberately collapse them, but that should be a choice, not an accident of the
Problem section's wording.

### Lens 3 — Pipeline Risk

**L3-1 · Question to the user:** The spec establishes three families — numerically executable /
valid but outside this executor / malformed-or-unsafe — but never states the assignment rule for
the concrete block families that exist today, and the cases that matter fall in the gap. Profile v2
currently has ~17 block reasons. The spec clearly assigns two poles: Boolean/string equality →
"valid but outside" (warn, continue); malformed facts → the failure family (SC 6). Unassigned:

- **Construct blocks** — feature chains, invocations, `xor`/`implies`, assert-by-reference. These
  are valid SysML with numerical *intent*. Warn-and-continue, or do they keep today's halt?
- **Unit-unsafe comparisons** — `block_unit_conversion_required`, `block_unknown_exact_unit`,
  `block_incompatible_dimensions`. SC 6 lists "unsafe unit relationships" in the *failure* family,
  but `mass <= 5 [kg]` over a dimension-only quantity is also "a valid statement this executor
  can't prove safe." Which family — and which behavior?
- **Excluded equalities** — integer, real, quantity. SC 3 puts them outside the executable subset,
  which reads as the warn family, but see L3-3.

Two strong engineers would build materially different things from this: one keeps generation
halting on a unit-unsafe comparison (today's behavior, forces the author to fix), one downgrades
everything non-malformed to a warning (generation almost never halts on constraints again). **State
the rule per family, or explicitly file the per-family assignment as an owner-decision open
question — right now it isn't even filed.**

**L3-2 · Question to the user:** Related but distinct: may generation still *halt* at all? The only
place halting survives is the last `[INFERRED]` item's "may prevent trustworthy generation," and
severity mapping is deferred to design. Whether the generator can ever refuse to generate because
of a constraint is the same class of contract decision you just made for non-numerical statements —
it's an owner call, not a design detail. **Answer now:** e.g., "malformed facts and unresolvable
executable inputs may still halt; everything else warns" — or explicitly delegate the whole
severity question to design with that guardrail stated.

**L3-3 · Direct claim:** The spec contradicts itself on who gets warnings. Problem ¶3: statements
outside the subset — all of them — "must remain visible and produce warnings in both" tools.
SC 4: only "a non-numerical asserted statement" is required to warn. Under SC 4 as written, an
excluded integer-equality or feature-chain assert has *no* warning requirement at all — no success
criterion would catch a design that silently catalogs it. Once L3-1's family rule is decided, SC 4
needs to cover every non-executed family, not just the non-numerical pole.

**L3-4 · If-then tradeoff:** SC 1 requires every admitted assertion to execute "without changing
its numerical meaning," but the meaning of "numerical meaning" is undefined at exactly the point
the spec leans on it. Integer operands stay admitted for ordering and arithmetic
(`integer <= real` admits), and the float path represents integers as IEEE doubles — above 2^53,
ordering comparisons silently lose precision, the same unpreservable-semantics problem the spec
uses to exclude integer equality. **If** the intended contract is "the numerical domain is IEEE
double, and 'numerical meaning' means float semantics," say so in one sentence — SC 1 becomes
well-defined and integer ordering is honestly in-domain. **If not**, integer ordering has the same
problem as integer equality and the admitted matrix needs a caveat. The first option matches the
D5 decision; it just isn't written down.

### Lens 4 — Hygiene

Nothing material.

### Lens 5 — Reader Comprehension

**L5-1 · Rewrite request (minor):** "Source-specific warning" carries SC 4's whole meaning and is
never defined. I read it as "one warning per offending statement, naming its source location" — as
opposed to the retired blanket warning. If that's right, say it once where the term first appears;
if it means something weaker, that materially changes SC 4.

---

## Engagement Summary

**Overall take:** The spec is faithful, honestly tagged, and every code claim survives checking —
this is a well-captured contract for a decided direction. Its one real defect is load-bearing: it
names three statement families but never assigns today's actual block reasons to them, and the
success criteria contradict each other about who warns and whether generation may still halt. That
gap is precisely where a design agent would silently pick a behavior you haven't chosen.

**Here's what I need you to weigh in on:**

1. **[L3-1, L3-2]** The headline decision: for each existing block family (construct blocks,
   unit-unsafe comparisons, excluded equalities), does it warn-and-continue or may it still halt
   generation — and may generation *ever* halt on a constraint again? Answer per family, or
   delegate to design with an explicit guardrail.
2. **[L3-3]** Once #1 is decided, SC 4 must require warnings for every non-executed family, not
   just "non-numerical" statements — as written, an excluded integer-equality assert could be
   silently cataloged and still pass every success criterion.
3. **[L3-4]** Decide whether the contract states "the numerical domain is IEEE double" — one
   sentence that makes SC 1 well-defined and keeps integer ordering honestly admissible.
4. **[L2-1]** Confirm the warning vocabulary should distinguish "not numerical" from "numerical
   but not faithfully evaluable" (feeds Open Question 1).
5. **[L1-1]** Confirm the both-tools warning placement in `[NEED]` #3 was your statement, or
   retag it `[INFERRED]`.
6. **[L1-2]** Minor: add the D5 ratification to `[HARD]` #1's cited authority.

---

## Resolutions

*(Filled in during finalization — one entry per resolved finding, keyed by ID. This is what the
spec agent reads to incorporate the review.)*

- **[L3-1, L3-2]** Resolved by the owner, 2026-07-18: a three-way rule. (1) A numerical claim the
  profile admits must execute. (2) A numerical claim that is not correctly formed — the
  unit-unsafe family, unresolved operands, numerical (integer/real/quantity) equality, and
  unsupported constructs inside an ordering/arithmetic predicate — is "numerical but malformed"
  and **raises a generation error**, as today. (3) Non-numerical statements (boolean/string/enum
  equality, `xor`/`implies` over boolean terms) warn, are cataloged, and never prevent
  generation. Both agent recommendations ratified: (a) numerical equality errors; (b) numerical
  intent is classified structurally (ordering/arithmetic root = numerical claim), with classifier
  mechanics left to design. Malformed facts and admitted-but-untranslatable statements are always
  errors.

- **[L3-3]** Resolved 2026-07-18, superseding an earlier two-bucket reading in this session: the
  owner's final rule is the three-way split above. SC coverage now assigns every non-executed
  family a required outcome — non-numerical statements get the SC 4 warning; excluded numerical
  equality and other malformed numerical claims get a new generation-error success criterion. No
  statement can be silently cataloged and still pass the criteria.

- **[L3-4]** Resolved by ratification, 2026-07-18: the numerical domain is IEEE double;
  "preserving numerical meaning" means float semantics. Stated in `[HARD]` #1, keeping integer
  ordering honestly admissible and excluding exact-integer equality.

- **[L2-1]** Dissolved by the three-way rule: a numerically meaningful but excluded shape
  (integer equality) is now a generation error with rewrite guidance, never a "non-numerical"
  warning, so the vocabulary confusion cannot arise. Label spellings remain Open Question 1.

- **[L1-1]** Resolved by retag: the warn-and-continue outcome stays owner-stated (`[NEED]`); the
  both-tools placement is now `[INHERITED]` from the concept's executable-profile paragraph (the
  profile runs at design review and at codegen preflight).

- **[L1-2]** Resolved: `[HARD]` #1 now cites the owner-ratified D5 decision (remediation design
  addendum) as the authority for the fixed float data path, alongside the audit findings.

- **[L5-1]** Resolved: SC 4 now defines "source-specific" inline (one warning per offending
  statement, naming its source location).

All resolutions were incorporated into `spec.md` in-session at the owner's explicit direction
(the owner directed the reviewer to edit the spec — the review-not-spec boundary was waived).

---

**Verdict:** Revise — resolved. All findings were settled with the owner in-session and
incorporated into the spec on 2026-07-18; the revised spec is approved to proceed.
**Next Steps:** Proceed to `/_my_design`.
