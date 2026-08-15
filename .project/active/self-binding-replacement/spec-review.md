# Spec Review: Self-Binding Replacement — Establish, Document, Migrate

**Spec:** `.project/active/self-binding-replacement/spec.md` (rev 2)
**Contract:** `claude-pack/commands/_my_spec.md`
**Review File:** `.project/active/self-binding-replacement/spec-review.md`
**Date:** 2026-08-15

---

## Reality Check

**Sound, with one sequencing concern.** The work item is real, the problem statement is accurate,
and every code-facing count I checked reproduces: 15 self-bindings in `fusion-tea/models/`, 114 in
the stellarator, 0 in the codegen fixture, `SI_SELF_BINDING` raised at
`extraction/source_evidence.py:230` and `elaboration/elaborate.py:2005`, `SI_OCCURRENCE_AMBIGUOUS`
live in `elaboration/elaborate.py`, and the four `in x = x` examples in
`agentic-mbse/docs/patterns/plant-idiom.md` at `:79`, `:84`, `:85`, `:200` — including the `:200`
one presented as the supported EXPOSE idiom. The reverted patch is 15 right-hand sides across three
files, exactly as recorded. The errata about SysML Part 1 §7.17.2 is correct: `full_document.md:6355-6370`
is the action-parameter feature-value shorthand, with no shadowing prose.

This spec is careful and honest in a way most aren't — the surfaced premise conflict, the revert
record, and the "evidence to review, not fact to inherit" provenance note are all the right moves.
The findings below are about what it inherited wrong from upstream and what it silently pre-decided,
not about direction.

The one concern that could make it the wrong item *right now* is L2-1: the owner decided the Item-8
order on 2026-08-15 and this spec starts at B without A.

---

## Audit

### Lens 1 — Faithfulness

**L1-1 · Direct claim — the "two forms" count is not owner-verbatim, and it is locatable.**
The spec says the 2026-08-05 utterance enumerating "two" "has not been located" (`spec.md:57-58`)
and builds the whole surfaced premise conflict (`:47-63`) on reconciling two against three. I found
the 2026-08-05 utterance. It appears four times, identically, and it does not contain a count:

> "we MUST document allowable patterns in our `agentic-mbse` docs as well. This is a 'how do you
> model correctly' quesiton, not a 'what should sysml-codegen do' question…"

— `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md:444`,
`.project/backlog/epic_elaborate_first_architecture.md:71`,
`.project/completed/20260810_epic_semantic_source_identity.md:290`, and
`.project/active/source-identity-contract/spec.md:150-153` (SI-18, graded `[NEED]`).

The required-content elaboration of that obligation is **SI-19, graded `[INFERRED]`** (same file,
`:155-159`), and it lists **four** content items — positive nested-definition and named-occurrence
examples, the source-self-binding counterexample, the indexed-value-expression limitation, and the
definition/redefinition relationship. No "two replacement forms" anywhere.

So the clause "its two valid replacement forms with their distinct meanings" at
`epic:497-499`, stamped `[OWNER-VERBATIM obligation]`, is **agent-authored text carrying an
owner-verbatim grade**. That is a capture-fidelity law-1 defect upstream, and this spec inherits it
as settled and then spends its most prominent section trying to make an agent's count reconcile with
a ratified three-disposition policy. The conflict likely dissolves under a provenance correction
rather than an owner recall.

**What I need:** the owner to rule on the grade of `epic:497-499`. If it is agent-grade, the spec's
premise-conflict section should be rewritten as a provenance finding (and the epic line fixed), not
as an open question about what the owner meant. The success criterion "at least two forms whose
referents provably differ" survives either way — it's a good criterion — but its justification changes.

**L1-2 · Direct claim — the spec omits that D-5 already carries a ratified migration recommendation
for this exact model.** Known Requirements inherits D-4 through D-7 and says "These remain the
semantic authority; this item does not change them" (`spec.md:118-121`). But D-5's own text says:

> "Migration: **the customer migration uses this form in place** (checkpoint item 8; exact mixed-context
> acceptance in C25 and def-only acceptance in C2)."

and the contract's checkpoint block adds "This evidence correction does not change **the ratified
bare-renamed-form recommendation**." (`constraint-execution-authoritative-lifecycle-contract.md`,
D-5 row and the checkpoint paragraph above the dispositions).

The codegen fixture is already migrated that way — `tests/fixtures/fusion_tea/library/analyses/ife_lcoe.sysml:31`
declares `in attribute availability_in : Real;` and `designs/generic_ife/ife_plant.sysml:114` binds
`in availability_in = availability`. The customer repo's corresponding library still declares the
bare formal (`fusion-tea/models/library/analyses/ife_lcoe.sysml:31`).

The spec's Open Question "which replacement form is the recommended default" (`spec.md:178-180`)
therefore isn't open upstream — it was ratified 2026-08-05 as bare-renamed-in-place, and the
acceptance fixture is built on it. Design may still argue for changing it, but the spec must say
that a ratified recommendation exists and that reopening it is a deliberate act, not present the
question as untouched ground.

**L1-3 · Direct claim — the spec asserts an answer to a question the owner reserved.** Problem
strand 3 states flatly "Only the diagnostic half is discharged" (`spec.md:41`). `CURRENT_WORK.md:113-117`
records the opposite posture as of this morning:

> "**Whether that discharged the obligation is unknown and needs the owner** — an agent does not mark
> an owner-originated item done by inference."

and the top block (`:16`) still lists it under "Held for an owner call." The spec's reading is very
probably right — `plant-idiom.md` is the only agentic-mbse doc mentioning `SI_SELF_BINDING`, and it
names only D-5 spellings — but *partially discharged* is still a call on an owner-originated
obligation. It should be stated as the spec's finding put to the owner, with the evidence, not as a
premise.

**L1-4 · Direct claim — Problem strand 2 overstates what the published guidance does wrong.** The
spec says the guidance "names two replacements that mean the same thing" and that "an author can
follow it exactly and still get a refusal they cannot interpret" (`spec.md:32-36`). Reading
`plant-idiom.md:57-62`, the guidance names **three** things, not two:

- suffix the parameter — `in radius_in = radius` (D-5)
- give the attribute the qualifying name — `in length = plant_length` (D-5)
- "For a value that lives on another part, name the path: `in driver_cost = driver.cost`" (D-7-shaped)

The first two are indeed one idea twice. But the third is a genuinely different referent, published
in one sentence with no statement of what it resolves to — which is a *sharper* version of the spec's
complaint, and it is missing from the problem statement.

The "refusal they cannot interpret" clause is the part that doesn't hold: `SI_OCCURRENCE_AMBIGUOUS`
attaches to the owner-qualified form (D-6), which the published guidance never names. An author
following `plant-idiom.md` exactly writes D-5 and does not hit it. The uninterpretable-refusal risk
is real for the form the *reverted work* chose, not for the form the doc teaches.

**L1-5 · Question to the user — the guidance's inherited required content is four items, and this
spec scopes one.** SI-19 (`source-identity-contract/spec.md:155-159`) is what "publish the
allowable-modeling-pattern guidance" was expanded to mean: positive nested-definition and
named-occurrence examples, the self-binding counterexample, **the indexed-value-expression
limitation (D-8)**, and **the definition/redefinition relationship**. This spec claims sub-item 4
"in full" (`spec.md:269-271`) but its criteria cover only the self-binding half. The last two aren't
in scope and aren't in Non-Goals.

**Is sub-item 4 discharged by publishing the self-binding half, or does it require SI-19's four?**
If the latter, either scope them in or name them as a Non-Goal with an owner.

**L1-6 · Direct claim — the `[INFERRED]` formal-rename row is contradicted by the spec's own
evidence.** `spec.md:135-137` infers that migration should avoid renaming calc-def formals "because
a formal's name reaches generated schema field names and entry-point keys." The Change Record
(`:230-234`, confirmed by the independent audit at `:238-240`) records that the D-6 qualified
migration produced an entry-point key set **identical** to the D-5 `_in`-suffixed fixture's, apart
from the deleted workaround's four keys. Two migrations with different formal names, same keys —
which means these bindings key as `DESIGN_ATTRIBUTE` (by supplying-attribute display path, per
`CLAUDE.md`), so the formal name does not reach the key here.

This matters because that row is the main written argument steering design away from D-5 — the form
the contract ratified (L1-2) and the fixture already uses. If the inference is false for these sites,
it should be narrowed to the case it's actually true for (unbound formals falling back to
`LIBRARY_DEFAULT`, which key `{consumer}__{formal}`) or dropped.

**L1-7 · Note, no action needed.** The KerML citations in the `[HARD]` redefinition row
(`spec.md:126-130`) both check out. §7.3.4.5 carries "the local namespace of the owning type of the
redefining feature is not included in the name resolution … beginning instead with the direct
supertypes" and the otherwise-inherited requirement; §8.2.3.5.1 states the same rule in
abstract-syntax terms ("repeated with the general Type of each ownedSpecialization … as the local
Namespace"). The errata's implication that §8.2.3.5.1 is silent on the exclusion is slightly too
strong, but the row as written is accurate.

### Lens 2 — Problem & Approach

**L2-1 · Question to the user — this starts at B and skips A, which you decided this morning.**
`CURRENT_WORK.md:100-123` records `[OWNER 2026-08-15]`: Item-8 order is **A → B** — the bounded
scope scrub first (one scope table of each §C sub-item against what Items 1/7 delivered, plus the
reconciled doc list; zero repairs; ~half a day), *then* fusion-tea regeneration. Two alternatives
including straight-to-B were explicitly declined.

This spec is B plus sub-item 4, and the scrub appears nowhere in it — not in Related Artifacts, not
in Non-Goals, not in Open Questions. Worse, the spec performs the scrub's job by assertion: it rules
what sub-item 4 covers, splits sub-item 1 into halves, and decides which half stays with Item 8
(`spec.md:152-161`, `:269-271`). Three of my findings above (L1-1 provenance, L1-3 discharge status,
L1-5 content list) are exactly the reconciliation the scrub was chartered to produce.

**Two ways to resolve, and they lead to different work:**
- **Run the scrub first** as decided. It is half a day, it answers L1-1/L1-3/L1-5 as output rather
  than as review findings, and this spec gets re-cut against its result.
- **Or supersede the ordering deliberately** — record that this item absorbs the scrub's sub-item-4
  and sub-item-1 rows, and carry the doc-list reconciliation (12 vs 6, five overlapping) somewhere
  named.

What shouldn't happen is the ordering being dropped silently, which is what rev 2 does today.

**L2-2 · If-then tradeoff — the form choice decides whether the customer model and the codegen
fixture stay one artifact or become two.** The fixture is D-5 with `_in` formals; the reverted work
migrated the customer to D-6 qualified. `CURRENT_WORK.md:145-147` records that the two trees are
"byte-identical in 9 of 11 files after stripping the authorized `_in` suffixes" — a relationship
that exists precisely because both are D-5.

If design picks D-6 or D-7 for the customer repo, that relationship is gone permanently, and the
fixture (the certified acceptance artifact) and the customer model become structurally different
shapes forever. That cost isn't named anywhere in the spec, and it is a real argument for D-5 that
sits alongside the L1-6 argument that was pointing the other way on a false premise.

**Is the fixture meant to remain a faithful stand-in for the customer model?** If yes, D-5 is close
to forced and the open question is nearly closed. If the fixture is just a corpus entry, the forms
can diverge and design chooses freely.

**L2-3 · Direct claim — MEDIUM understates this.** As scoped, the item spans: a measurement campaign
over candidate forms on the licensed route; a guidance rewrite in `agentic-mbse`; repair of four
worked examples in `plant-idiom.md` including the EXPOSE idiom at `:200`; a 15-site customer
migration plus generate/seal/snapshot/mutation proof; possibly a **new readiness diagnostic in the
codegen generator** (criterion 2, `spec.md:71-76`); possibly 114 stellarator sites; possibly ADR-010.
Three repositories, and one of those legs is production generator code, which is a different risk
class from docs-and-models.

Epic Item 8 in total was budgeted 3–5 days for more than this. Either the complexity is HIGH, or the
diagnostic leg and the stellarator get pulled out with named vehicles.

### Lens 3 — Pipeline Risk

**L3-1 · Direct claim — the entry-point-key criterion has no baseline, and its stated rationale is
already falsified.** `spec.md:101-102`: "No public entry-point key changes name as a result of the
migration, **so downstream studies and input JSON keep working**."

Two problems. First, no baseline: the spec's own Problem strand 1 says the customer model cannot
generate at all on the exact route, so there is no current key set to compare against. The candidates
are the codegen fixture's key set, or July's legacy-route output — and the spec picks neither. Two
engineers would build different checks.

Second, whichever baseline is chosen, the rationale is known false: the Change Record (`:230-234`)
and the audit (`:238-240`) both record that the workaround-free model drops the four
`hif_driver_instance` keys and publishes 9 channels instead of 11. Studies naming those keys break.
The criterion's wording ("changes name") technically survives a key *disappearing*, but the promise
attached to it does not. Name the baseline, and state the known key deletions as an accepted
consequence rather than letting the rationale imply they don't happen.

**L3-2 · Question to the user — criterion 2 quietly authorizes a generator change.** "routed to a
loud failure, or to a filed and owned gap" (`spec.md:71-76`) means: if the measurement campaign finds
a second silently-inert form, this item may add a readiness diagnostic. Correct in principle — it's
the CSF, and product-lens spec-F3 asked for it. But it's unbounded: it doesn't say which repo
(codegen readiness vs the `agentic-mbse` L2 validator, which the contract also obliges), and it turns
a docs-plus-models item into one that can touch the generator and its fixture corpus mid-flight.

**Do you want a discovered new form to be fixed inside this item, or always filed?** If "always
filed unless trivial," say so — the criterion still satisfies the CSF and the item stays bounded.

**L3-3 · Rewrite request — "at least two forms whose referents provably differ" and the D-5 pair
don't sit right together.** The criterion (`spec.md:77-80`) is satisfiable by D-6 + D-7, whose
referents differ by construction. But the two forms the guidance currently publishes are both D-5,
and if D-5-in-place stays the ratified customer recommendation (L1-2), the guidance's *recommended*
form and its *distinctness-demonstrating* pair are different forms. The spec should say whether the
two provably-differing forms must include the recommended one, or whether the guidance teaches a
recommended form plus a distinct-referent pair. As written a reader can't tell how many forms end up
in the doc.

**L3-4 · Direct claim — the stellarator is simultaneously in scope and an open question.** Criterion
10 (`spec.md:103-104`) requires it to be migrated-and-elaborating or blockers-named-and-filed, which
forces at least a triage pass into this item. The Open Question (`:175-176`) asks whether it belongs
here at all, and notes its branch is on owner HOLD from July. The criterion has effectively decided
the minimum. That's a defensible answer, but it should be stated as the decision it is rather than
left as a question the criterion already answers.

**L3-5 · Question to the user — deferral accuracy on the ADR.** "Whether this warrants an ADR"
(`spec.md:181-182`) is filed as design-stage. "Which authored forms may supply a calculation input,
and what each resolves to" is a modelling ruling with lasting force, and D-4..D-7 already are that
ruling in a concepts document rather than in `modeling-assumptions.md`. Whether the project wants
that promoted to ADR-010 is your call, not design's — and it's cheap to answer now.

### Lens 4 — Hygiene

**L4-1 · Rewrite request:** The Change Record's "Errors the audit found in the reverted work"
(`spec.md:242-263`) is four items, of which #1 and #4 are load-bearing for design (drop the §7.17.2
authority; the def-qualified form is fragile at one occurrence) and #2 and #3 are footnotes. The two
load-bearing ones read as archaeology buried at the bottom of the document. Item #4 in particular —
that the migration used owner-qualified *from inside the part def*, a form/position combination the
probe table never measured — is a direct input to the measurement campaign in criterion 1 and should
be visible from there.

### Lens 5 — Reader Comprehension

**L5-1 · Rewrite request:** D-5/D-6/D-7 are glossed exactly once, parenthetically, inside the
premise-conflict paragraph (`spec.md:50-51`), then used as bare labels across the next 130 lines —
Non-Goals, Open Questions, the errata. A reader who skims past line 51 cannot decode "the reverted
work had already committed to the owner-qualified form" without scrolling back. Give the three forms
a compact named list near the top, with what each one's reference lands on, since the whole item is
about telling them apart.

**L5-2 · Rewrite request:** Ten success criteria, several of them multi-sentence with embedded
justification, and no signal of which one is the item's spine. Criterion 7 (an off-default mutation
reaches every and only its bound consumers on the migrated model) is the one that proves the point;
criterion 6 is explicitly labelled necessary-not-sufficient. That ordering should be visible without
reading all ten.

---

## Engagement Summary

**Overall take:** The spec is right about the problem and unusually honest about its own provenance —
every count and code claim I checked reproduces. But it starts at Item-8 step B when you decided
this morning to run A first, and the scrub it skips is exactly what would have caught the three
inheritance defects I found: the "two valid replacement forms" clause is stamped `[OWNER-VERBATIM]`
but is agent-authored, the contract already ratified bare-renamed-in-place as *the customer
migration form*, and the argument the spec uses to steer away from that form is contradicted by its
own recorded evidence.

**Here's what I need you to weigh in on:**

1. **[L2-1]** You decided A → B this morning. This spec is B. Run the scrub first and re-cut, or
   deliberately supersede the ordering and record that this item absorbs the scrub's sub-item-4 and
   sub-item-1 rows? Three of the findings below are scrub output arriving as review findings.

2. **[L1-1]** The "two valid replacement forms with their distinct meanings" clause at
   `epic:497-499` carries an `[OWNER-VERBATIM obligation]` grade, but the located 2026-08-05
   utterance contains no count, and the required-content expansion (SI-19) is `[INFERRED]` and lists
   four content items. Is that clause owner-grade or agent-grade? If agent-grade, the spec's whole
   two-vs-three premise conflict dissolves into a provenance fix.

3. **[L1-2, L1-6, L2-2]** The contract ratified **bare-renamed-in-place (D-5)** as the customer
   migration form, and the codegen fixture is built on it. The spec presents the form choice as
   untouched open ground, and the one `[INFERRED]` row arguing against D-5 (formals reach entry-point
   keys) is falsified by the spec's own evidence — the D-5 and D-6 migrations produced identical key
   sets. Do you want the form question genuinely reopened, or is D-5 the default that design must
   argue *out* of? Note the fixture and customer model stay one shape only under D-5.

4. **[L1-3]** The spec states "only the diagnostic half is discharged" as fact. `CURRENT_WORK`
   still holds that exact question for you. Is partial discharge your ruling, or does the spec need
   to put it to you with the evidence?

5. **[L3-1]** "No public entry-point key changes name" has no baseline — the model can't generate
   today — and its stated purpose (studies keep working) is already falsified by the four
   `hif_driver_instance` keys the workaround-free model drops. Which baseline, and do you accept the
   key deletions?

6. **[L3-2, L2-3]** Criterion 2 authorizes adding a readiness diagnostic to the generator if the
   measurement campaign finds a second silently-inert form. That plus 114 stellarator sites makes
   MEDIUM optimistic and mixes production generator work into a docs-and-models item. Fix-in-item, or
   always-file?

7. **[L1-5]** Sub-item 4's inherited content list (SI-19) has four items; this spec scopes the
   self-binding one. Is sub-item 4 discharged by the self-binding half, or do the indexed-expression
   limitation and the definition/redefinition relationship come with it?

---

## Resolutions

- **[L2-1] — narrow the stocktake, don't run it first.** `[OWNER 2026-08-15]` The spec proceeds
  now. It makes only the two stocktake calls it actually depends on: what the documentation
  obligation covers, and where the leftover regeneration work lives. **After the spec is approved,
  a research report runs the full stocktake and checks those two rows make sense.** The
  document-list conflict (twelve vs six, five overlapping) belongs to that report, not to this
  item. The morning's A → B ordering is not overridden — it is satisfied in a cheaper form, with
  the verification moved after approval instead of before drafting.

- **[L1-1, L1-5] — the count was never yours; the obligation is restated.** `[OWNER-VERBATIM
  2026-08-15]`:

  > "honestly, the epic is old and that statement was taken out of context. I was just working
  > with the other agent on refining it in this spec. all I care about is: We know what the RIGHT
  > pattern(s) are for the given situation / We document those right patterns / We fix the models
  > to use the right patterns. `in R = R` is the wrong pattern. I would like to detect the use of
  > it so we avoid it in the future. that's it, that's all I care about."

  Consequences, all settled:
  - The "two valid replacement forms" count is **agent-authored**, was carrying an owner-verbatim
    stamp it never earned, and is now corrected at source.
  - **The spec's surfaced premise conflict (`spec.md:47-63`) is dissolved, not answered.** There is
    no two-versus-three question. Delete the section; replace it with one line recording that the
    count was agent-authored and corrected. The success criterion "at least two forms whose
    referents provably differ" is no longer justified by the obligation — see L3-3, it now needs to
    stand on its own reasoning or be restated as "the right pattern for each situation."
  - **The four-item inherited content list (SI-19) does not govern.** The obligation is the owner's
    three lines plus detection. Indexed expressions and definition/redefinition teaching are not
    required by it.
  - **Owner asked for the epic to be updated; done 2026-08-15.** Both
    `epic_elaborate_first_architecture.md:70-77` (source-documents quote) and `:495-503`
    (scope sub-item 4) now carry the restated obligation with a provenance-correction note.

- **[L1-3] — moot, withdrawn.** Whether CONSTRAINT-SEMANTICS Item 7 partially discharged the old
  obligation stops mattering once the owner restates the obligation fresh. The question to answer is
  now "does the shipped guidance satisfy the three lines above," which this item answers by doing
  the work. `CURRENT_WORK.md`'s held-for-owner-call entry on this should be closed as superseded.

- **[L1-2, L2-2, L3-3] — situational rule, with make-the-names-differ for the blocking case.**
  `[OWNER-VERBATIM 2026-08-15]` "agreed with the recommendation — it is situational and the
  agentic-mbse agents should know and understand the difference."

  The rule the guidance states:
  - **Attribute on the part that owns the calculation → make the names differ.** This is the form
    the contract ratified 2026-08-05 and the form the codegen fixture already uses (`_in` suffix).
    It is the answer for all 15 fusion-tea sites.
  - **Value on a different part → name the path** (`in driver_cost = driver.cost`).
  - **Qualifying by owner name works, but is only safe while that definition has exactly one
    instance.** The guidance says this plainly rather than hiding the form or recommending it. This
    is why the reverted work's choice is not being restored: it resolves today only because
    `'IFE Power Plant'` has one usage, and ten of its bindings would refuse with an ambiguity
    diagnostic the moment a second plant of that type exists.

  Consequences: the migration renames parameters in two shared library files
  (`fusion-tea/models/library/analyses/{ife_lcoe,hif_economics}.sysml`), matching the fixture; the
  customer model and the codegen fixture stay the same shape; **L3-3 is answered** — the guidance
  is organised by situation, not by a form count.

- **[NEW, from the same answer] — the guidance must reach the agent-facing surfaces, and today it
  reaches none of them.** The owner's "the agentic-mbse agents should know and understand the
  difference" is a scope addition, and it is not satisfied by `docs/patterns/plant-idiom.md`.
  Verified 2026-08-15:
  - `agentic-mbse/claude/skills/sysml-conventions/SKILL.md` is the surface agents read when writing
    SysML (it is symlinked into this repo at `.claude/skills/sysml-conventions`). It carries a
    calculation-binding guidance table (`:123`) and a binding example (`:210`) and **says nothing
    about self-named bindings being refused**. An agent following it can author the broken shape.
  - No file under `agentic-mbse/claude/` or `agentic-mbse/.claude/` mentions `in R = R`,
    `self-named`, or `SI_SELF_BINDING` at all. `plant-idiom.md` is referenced only from
    `claude/skills/sysml-conventions/references/stencils.md`.
  - **The two-copies trap applies** (Item-7 residual A-1): agentic-mbse tracks divergent
    `claude/` (10 skills) and `.claude/` (4 skills) trees, and `sysml-conventions` exists only in
    `claude/`. A fix to one is not a fix to both.

  This should become an explicit deliverable and a success criterion in the spec, not a side effect
  of the docs pass.

- **[L1-6] — factual correction, no decision needed.** The `[INFERRED]` row at `spec.md:135-137`
  (avoid renaming calc-def formals because formal names reach entry-point keys) is falsified by the
  spec's own Change Record: the bare-renamed and owner-qualified migrations produced identical key
  sets, so these bindings key by supplying attribute, not by formal. Delete the row — the owner has
  since chosen the form it was arguing against (see the situational-rule resolution above), so it
  has no remaining function.

- **[L3-1] — drop the criterion.** `[OWNER 2026-08-15]` "Honestly I don't care about this
  criterion." Delete "No public entry-point key changes name as a result of the migration"
  (`spec.md:101-102`) outright, with no replacement wording and no compensating note. The
  mutation-reaches-every-and-only-its-consumers criterion is the stronger check and already covers
  what matters; nothing load-bearing goes with the deletion. The four absent `hif_driver_instance`
  keys and the 9-vs-11 channel mismatch are a July workaround deletion, not this migration, and stay
  with the regeneration work at `.project/active/elaborator-downstream/`.

- **[L3-4] — stellarator: triage only.** `[OWNER-VERBATIM 2026-08-15]` "triage is good." Migrate
  fusion-tea. Run the stellarator through the pipeline **once**, record what breaks, fix nothing,
  and do not reverse the July hold. Rewrite criterion 10 to say this plainly, and close the
  corresponding open question — it is decided, not deferred.

  Sizing evidence gathered for the decision (2026-08-15, `/home/reid/1cfe/fusion-tea-stellarator-mbse-demo`,
  branch `feat/stellarator-mbse-demo`): of the 114 self-named bindings, **15 are the same
  fusion-tea files copied in** (`generic_ife/ife_plant.sysml` ×10, `hif_ife/hif_plant.sysml` ×3,
  `hif_ife/hif_driver.sysml` ×2 — matching fusion-tea exactly). The stellarator's own work is **99
  sites in two files**: `generic_mfe/mfe_plant.sysml` ×94 (including the literal `in R = R` at
  `:117`) and `stellarator_09/stellarator_plant.sysml` ×5. Triage answers whether those 99 are
  mechanical edits or a different problem wearing the same shape.

- **[L3-2] — file, don't fix, unless small.** `[AGENT]` recommendation, put to the owner alongside
  the triage question and not objected to — **not owner-originated, and challengeable on evidence.**
  If the measurement work finds a *different* pattern that also resolves silently and wrongly, this
  item files it with a name and an owner rather than adding generator detection mid-migration,
  unless the fix is small. Rationale: adding production code changes to a docs-and-models item
  changes its risk class. Note the owner's stated detection ask is already met for the pattern they
  named — `in R = R` is refused by codegen (`extraction/source_evidence.py:230`) and failed by the
  `agentic-mbse` level-2 check.

- **[L2-3] — sizing.** With the stellarator reduced to triage and new-form fixes filed rather than
  built, MEDIUM is defensible. Reassess if the agent-surface work (see the new finding above) turns
  out to mean reconciling the two divergent `claude/` and `.claude/` trees.

- **[L4-1, L5-1, L5-2] — accepted as rewrite requests**, no owner input needed. Surface the two
  load-bearing errata (drop the SysML §7.17.2 authority; the owner-qualified form is fragile at one
  occurrence) where design will read them; name the three authoring shapes once near the top in
  plain words; make clear which success criterion is the spine.

---

**Verdict:** Revise — **all findings resolved 2026-08-15; the review is final and ready to incorporate.**

**Next Steps:** Re-run `/_my_spec` (or return to the spec-agent session) and point it at this
review's Resolutions section. The substantive rewrites it must make:

1. Delete the surfaced premise conflict (`spec.md:47-63`) — dissolved, not answered.
2. State the situational rule as the spec's core requirement, and close the "which form is the
   default" open question.
3. Add the agent-facing surfaces as a deliverable with its own criterion.
4. Delete the entry-point-key criterion and the falsified `[INFERRED]` formal-rename row.
5. Rewrite criterion 10 as stellarator triage-only, and close its open question.
6. Record the narrowed stocktake and the research report that follows approval.

Then a fresh product-lens run to clear the rev-1 `BLOCKED` gate, and `/_my_design`.

**Upstream edits made during this review** (owner-directed, outside the spec):
`.project/backlog/epic_elaborate_first_architecture.md` — the source-documents quote (`:70-77`) and
scope sub-item 4 (`:495-503`) now carry the owner's 2026-08-15 restatement with a provenance
correction, per `[OWNER-VERBATIM]` "please update the epic as this continues to cause confusion."
This reviewer did not edit `spec.md`.
