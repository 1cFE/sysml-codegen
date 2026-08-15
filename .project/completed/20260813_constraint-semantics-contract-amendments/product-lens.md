# Product-lens ledger — constraint-semantics-contract-amendments (CONSTRAINT-SEMANTICS Item 1)

Append-only. Verdict blocks land verbatim; dispositions are recorded in the spec/design they amend.

## spec — 2026-08-12 — rev 137e021 (+ untracked `.project/active/constraint-semantics-contract-amendments/spec.md`)
Epic: CONSTRAINT-SEMANTICS, Item 1

**Epic gate reference (not restated):** the epic's own product-lens gate is **CLEAR** with no
findings — `.project/backlog/epic_constraint_semantics_contract.md` §Product-Lens, epic-plan
2026-08-12, point graded **owner**. The epic file stays the source of truth.

**Runner note:** the reviewing agent could not read `/home/reid/.claude/scripts/product-lens.md` or
its pack source (both outside this session's sandbox). It recovered the §3 ledger format from the
sibling ledger `.project/active/constraint-semantics-contract/product-lens.md` and followed that.
`/home/reid/1cfe/agentic-mbse-item7-rebuild` is also unreadable here, so D3/D4/D5 locations were
not verified against the companion repository.

**Point** (re-derived from SOURCES; the WORK was read after the sources were pulled, not before the source read):

1. Every authored constraint usage stays visible with exactly one disposition, the assert family alone enforces, and no durable authority — contract, companion, ADR, or modeling doc — may still teach a rule the settled contract replaced. [source: contract invariants 1, 28, 32, 33, 48 + rulings Q1/Q3/Q5; grade: agent/ratified]
2. No headline or coverage statement may claim more coverage than was assessed; the feasibility denominator is applicable **asserted** gates, separate from inventory totality. [source: umbrella spec Report-and-coverage section, refinements L2-1/L2-2; grade: agent/ratified]
3. Documentation is made correct *first*, from settled semantics, never reverse-engineered from current behavior. [source: rulings-20260812.md:19-21; grade: **owner**]
4. The concept must instruct **when** equalities should be used at all, beyond what codegen supports; tolerances are modeler-chosen modeled values. [source: rulings-20260812.md:16-18; grade: **owner-verbatim**]
5. Every hop preserves the grade of what it carries: Q1–Q8 and L-refinements stay `[AGENT] (ratified 2026-08-12)`; only owner-*originated* payloads are owner-grade. [source: capture-fidelity law 1; grade: **HARD**, user-global rule]

**Falsifier:** after Item 1 lands, a reader of any durable authority in either repository still meets a statement of the superseded coverage/disposition rule, or an owner-grade marker sits on content the owner did not originate, or an amendment softens a settled rule toward today's behavior.

### Findings

- **item1-F1 [DO] — the closed amendment set leaves one superseded statement standing.** The spec says "Anything not listed here is not amended by this item" (`spec.md:123-124`) and lists invariants 1, 8/9, 28, 32, 33, 46/46a, 48 plus three Appendix C cells. Appendix B's correction register carries the same superseded claim the Appendix C "Excluded-only usages" cell does: "No usages is inert; excluded-only usages retain `not_assessed` visibility" (`constraint-execution-authoritative-lifecycle-contract.md:660`). Under the ruled semantics an *asserted* excluded usage yields partial coverage, not `not_assessed`. The spec amends the Appendix C cell (`:682`) and forecloses the Appendix B twin. — source: contract Appendix B:660 vs Appendix C:682; umbrella spec headline ruling (agent/ratified) — **disposition:** add Appendix B's row to the amendment set, or change the closing clause from a closed set to "at minimum", matching the wording the companion section already uses.

- **item1-F2 [DO] — "applicable asserted gate" is the load-bearing term and is never defined.** All six published state meanings, the invariant-33 precedence, the invariant-32 restatement, and the inventory-vs-feasibility split turn on which gates are "applicable" (`spec.md:171-191`). The spec states the vacuous-gate case inside state 4 but never publishes the membership rule itself. Item 1 owns meaning and Item 3 owns only spellings, so no later item has the mandate to define it, while Item 2's totality gate and Item 5's all-65 dispositions both key off it. — source: umbrella refinements L2-1 / L2-2 (agent/ratified); epic Item 1 scope item 5 (agent/ratified) — **disposition:** publish "applicable" as an explicit definition: an asserted, in-scope usage counts in the feasibility denominator, including a vacuous one, until it carries an explicit inapplicability disposition.

- **item1-F3 [DON'T] — the equality taxonomy is promoted to owner grade.** The R-POL-4 four-class taxonomy is graded **[NEED] (owner-stated, 2026-08-12)** at `spec.md:230-237`. The umbrella grades that content "**R-POL-4, the instruction content (agent-drafted, owner-reviewed in session)**" (`constraint-semantics-contract/spec.md:152-158`); only the *need* for the instruction and the reason ("narrow bands of viability…") are owner-originated. The spec contradicts its own provenance rule three sections earlier, which lists the owner-grade payloads as the two verbatim quotes, the tolerance need, the **equality-usage-instruction need**, and the sequence (`spec.md:90-94`). — source: capture-fidelity law 1 (**HARD**, user-global); umbrella spec:152-158 (agent/ratified) — **disposition:** split the requirement — the need stays `[NEED]` with the verbatim quote; the four-class taxonomy carries `[AGENT] (drafted, owner-reviewed 2026-08-12)`. Same split when it is published in the concept, so a later reader cannot treat the taxonomy as unchallengeable.

- **item1-F4 [DO] — severity-by-cause is published only at its top and bottom tiers.** Q3 rules three tiers: asserted + structurally unattachable = generation error; asserted + vacuous = warning-grade visible disposition **plus an authoring-time advisory** ("part def with asserted constraint has no typed occurrences"); plain/out-of-scope forms = records, never errors. The spec's invariant 8/9 amendment publishes the error tier and the Q1/Q7 requirement publishes the never-errors tier, but the middle tier's severity and advisory have no amendment home, and the closed-set clause forecloses one. Invariant 28's "non-reaching-with-reason" gives the disposition kind, not the severity or the advisory. — source: rulings Q3; umbrella Pipeline-invariants "Severity by cause" (agent/ratified) — **disposition:** name the amendment target for the warning tier and the authoring advisory (invariant 15 or 28, or the companion's diagnostics requirement), since Items 2–3 implement against it.

- **item1-F5 [DO] — the companion's mirror of the invariant-48 change is unnamed.** The spec amends invariant 48 to make the embedded catalog "the authority for coverage truth… derived in one direction" (`spec.md:145-147`). Its companion counterpart LC-G07 (`constraint-execution-lifecycle-requirements.md:362-366`, **[NEED]**, owner-sourced quote) states the sole-catalog-authority rule without the coverage-truth clause, and the companion amendment list stops at LC-E05/E06/E10/E11/E12. The companion header makes it the only place forward requirement amendments may land, so an un-mirrored invariant 48 leaves the two authorities disagreeing. Note LC-G07 is owner-sourced ("100% Option A. We need to purge this mess.") — the amendment adds to it, and must not re-grade it. — source: companion:362-366 (owner-sourced NEED); contract invariant 48 (agent/ratified) — **disposition:** name LC-G07 in the companion set, or state in the spec why the coverage-truth clause needs no companion mirror.

- **item1-F6 [DO] — Item 1 writes "totality proof pending" into a repo whose matrix still reads PASS.** The D7 correction removes the retired-test citation and states the totality proof is pending (`spec.md:218-221`), while `docs/architecture/verification-matrix.md:336` keeps REQ-EXT-09 at **PASS**. Deferring the re-grade to Item 2 is right (lens spec-F7, and the row's own evidence is already re-anchored away from the retired test, so nothing is stranded), but the item's non-goal list is the only place the resulting in-repo contradiction is recorded — a reader of the matrix meets the green row with no pointer. — source: verification-matrix:336 (INHERITED); lens spec-F7 (agent/ratified) — **disposition:** low priority; either park the conflict visibly at the matrix row (a dated "re-grade pending, CONSTRAINT-SEMANTICS Item 2" note is an addition, not a re-grade, so it stays inside the non-goal), or accept the window explicitly in design.

**Not findings (checked, clean):**
- The owner's equality quote at `spec.md:47-49` reproduces `rulings-20260812.md:16-18` verbatim, at the owner's emphasis, and is carried into a requirement rather than paraphrased.
- The documentation-before-testing sequence appears twice, `[OWNER]`-graded, and the Sequencing requirement explicitly forbids softening an amendment to match today's code — the strongest single piece of the spec.
- Invariant 11 ("no equality executes") is correctly *not* amended: bands are two inequalities, and first-class `==` tolerance stays a non-goal.
- The invariant list matches lens spec-F2 exactly, and the three Appendix C cells match; the invariant-8/9 amendment correctly refuses a fifth profile outcome.
- The D-2 vs D-4/SRC-01 conflict is parked in both directions, citing law 4 — no silent resolution.
- Q1/Q7 scope precision (predicate-body-only; binding-position chains stay supported per D-7/invariant 20; inline asserted forms stay admitted per invariant 12) is published as spec-F6 required.
- Grep of both ratified authorities for enforcement claims about plain/`require` constraints returns nothing — the D1–D7 sweep is correctly scoped to the modeling docs, and no eighth defect hides in the contract or companion.
- The ADR home/number decision is `[INFERRED]` and marked revisable in design but not un-fileable — agent grade, not marked settled.
- Item 1 correctly leaves catalog/report/policy/fixture implementation, calc-def attachment, and the REQ-EXT-09 re-grade to Items 2–6.

**Gate: DISPOSED (item1-F1..item1-F6)** — no ruling and no owner-grade statement is contradicted, so nothing blocks approval. **item1-F3 is the one that must be fixed in the spec text itself** (capture-fidelity law 1 grade promotion; it is a two-line edit). F1, F2, F4, and F5 are amendment-set completions the design stage must absorb before drafting; F6 is optional. The recurring shape across F1/F4/F5 is the same: the contract amendment set is stated as closed while the obligations it must carry are still being enumerated — closing that clause the way the companion section already words it ("at minimum") resolves all three at once.

**Spec-side disposition record (2026-08-12, same session):**

- **item1-F1 → resolved in spec.** The closing clause now reads "at minimum … design may add a
  statement it finds carrying the superseded rule; it may not drop one from this list", and
  Appendix B's twin row is named explicitly in the amendment set.
- **item1-F2 → resolved in spec.** "Applicable asserted gate" is published as an explicit
  definition ahead of the six state meanings, including the vacuous case and the inapplicability
  exit.
- **item1-F3 → resolved in spec.** Split into a `[NEED]` for the instruction's existence and the
  owner's reason, and an `[INFERRED]` (agent-drafted, owner-reviewed 2026-08-12) for the
  four-class taxonomy content, with the grade required to survive publication.
- **item1-F4 → resolved in spec.** The warning tier and its authoring advisory are named as an
  amendment-set member; design names the specific amendment target.
- **item1-F5 → resolved in spec.** LC-G07 is named in the companion amendment set, with its
  owner-sourced grade explicitly preserved and an escape only if design records why no mirror is
  needed.
- **item1-F6 → deferred to design**, recorded in the spec's Open Questions with the two options
  (dated pointer at the matrix row vs. accepting the window). Both stay inside the non-goal, since
  neither re-grades the row.

---

## close — 2026-08-13 — rev `76e3ab7` (codegen item tip, branch `item7-rebuild`) / `dcb187b` (companion, `/home/reid/1cfe/agentic-mbse-item7-rebuild`)

No new lens pass was run at close, and none is claimed. This block records where every open
ledger item and audit residual was homed, so a later reader does not reconstruct it from a
DISPOSED gate.

**Gate at close: DISPOSED, no standing BLOCK anywhere in this ledger.** This ledger holds one
stage block (spec, item1-F1..item1-F6). Every block was re-read at close, not just the latest:
F1, F2, F3, F4 and F5 were resolved in the spec text; F6 was deferred to design and landed as the
dated matrix pointer (`docs/architecture/verification-matrix.md:336`). The umbrella ledger's
`spec-F1` INTENDED-CHANGE disposition now resolves against a live document — ADR-009, cited at
`.project/active/constraint-semantics-contract/product-lens.md:35`. The epic's own Product-Lens
gate is **CLEAR** with no findings.

**M-3 dispositioned at close: the vendored-corpora aggregation is RATIFIED as final.** The audit
accepted it as an orchestrator execution-detail call and marked it reversible here
(`audit.md:473-478`); this is the reversal decision, and it is not to reverse.

- What the spec asked for: "The named search terms, the directories covered, and the raw hit list
  are part of the record; a summary is not."
- What shipped: 52 companion hits in `docs/sysmlv2/` and `docs/syside/` aggregated into four rows
  by term and corpus, each naming every file with its per-file count and one uniform disposition
  (`verification.md:114-121`). Every project-authored hit is still one row each
  (`verification.md:123-139`) — the aggregation covers only the vendored class.
- Why it stands: the aggregated class is the OMG SysML specification, the standard library, and
  generated SysIDE API documentation. This item has no authority to amend any of it, so the
  disposition is uniform by construction ("out of class — vendored upstream reference corpus"),
  the files are named, and the audit reproduced all five sweep terms independently and got the
  recorded result term for term. Expanding the four rows to 52 would add rows, not information,
  and would not change a single disposition.
- The deviation from the spec's imperative wording is recorded as a decision, not a gap. The
  underlying criterion — the universal claim is checked, not asserted — is met.

**The two deliberate hand-offs Item 1 left open are DISCHARGED.** Both were left open on purpose
(executable text and replacement evidence are not this item's to write), and both were landed by
the items that owned them:

- **The four `all_satisfied` assertions** (`tests/execution/test_fusion_tea_real_teax.py:245`,
  `tests/execution/test_constraint_verdicts_exact_route.py:171,416,540`) were corrected by **Item
  3**'s token migration — `all_satisfied` became `full_satisfaction` in both vocabularies, with
  `UnknownHeadlineToken` failing closed at all three TEAx seams. Item 3 is archived at
  `.project/completed/20260813_constraint-coverage-policy/`. The audit's M-1 cure had recorded the
  four sites in the epic's Item 3 section, which is where Item 3's implementer met them.
- **REQ-EXT-09's replacement totality proof** was landed by **Item 2**: the retired
  `test_constraint_migration_mapping` citation Item 1 removed is replaced by
  `tests/conformance/test_constraint_population_oracle.py` and its 42 reviewed expected-population
  files, and the re-grade/re-anchor of REQ-EXT-09 and REQ-CL-04 was performed there. Item 2 is
  archived at `.project/completed/20260813_constraint-catalog-totality/`. The dated
  "re-grade pending, CONSTRAINT-SEMANTICS Item 2" pointer Item 1 added at
  `verification-matrix.md:336` has served its window.

**Residuals other closes homed against "Item 1's authoring guidance" are NOT reabsorbed here —
they belong to epic Item 7** (ADR, Product Promise, and Agent-Facing Documentation Sync, filed
2026-08-13 at owner direction, `.project/backlog/epic_constraint_semantics_contract.md:888`).
Item 1 is closed and has no execution vehicle; Item 7's scope item 4 re-homes them explicitly:

- **Item 3 design-F2** — Appendix C's vacuous-gate cell over-permits in the degenerate case and
  wants "…and at least one gate remains". Behaviour is settled by Item 3's D4 ruling; the contract
  text is not. → Item 7.
- **Item 3's D9 follow-on** — the authoring-time advisory for the eligible-plus-`@inapplicable:`
  combination, for companion authoring guidance. D9 already refuses the combination loudly at
  generation time. → Item 7.
- **Item 3's item3-F2 (surfaced, not resolved)** — the inherited "a `BLOCK`ed asserted usage stays
  in the denominator" clause is unreachable under invariant 1 as amended. It stays a surfaced
  premise conflict in both directions; Item 7's scope item 1 carries the owner disposition. → Item 7.

**The parked D-2 vs D-4/SRC-01 premise conflict stays parked, and is confirmed untouched.** It
lives at the umbrella level (`.project/active/constraint-semantics-contract/spec.md:325`, lens
spec-F6) and this item's non-goals forbade touching either statement in either direction. Verified
at close, not assumed: `git diff 4678cd5..HEAD -- <lifecycle contract>` matching `D-2|D-4|SRC-01`
is empty, and the umbrella spec has no diff at all across the item range. Not resolved here, and
not resolvable by an agent — it needs the owner.

**The D5-a accepted deviation survives archival.** At `claude/agents/sysml-expert.md:124` the
implementer kept `require constraint` inside the `requirement def` example and added a
settled-semantics sentence, rather than swapping the form as the design instructed. The audit
judged the deviation **sounder than the design's instruction** (`audit.md:226-243`): a
`require constraint` nested in a `requirement def` is the SysML v2 idiom that makes a constraint
requirement-side at all, so substituting `assert constraint` would have taught invalid requirement
modeling and deleted the visible requirement-side form that umbrella ruling Q7 exists to preserve.
The published rule never says "don't write `require constraint`" — it says the form never executes
and the assert family is the sole enforcement opt-in. The deviation was recorded with its
reasoning *before* being taken (`verification.md:178-195`), which is the correct handling. Probe
P-2 confirmed the landed wording, including that no surrounding prose still frames the example as
a check.

**No product-promise entry was filed, and no id was hand-minted.** The gap recorded at Items 2 and
3's closes is unchanged: this repo has no `.project/adr/` or `.project/product/` ledger and no
`adr.sh`/`product.sh` (`.project/scripts/` holds only `get-metadata.sh`). Item 1's decision record
is ADR-009 itself, hand-authored into `docs/architecture/modeling-assumptions.md` §9 at
`[AGENT] (ratified by owner, 2026-08-12)` — filed, discoverable, and cited from the umbrella lens
trail. The coverage-truth *promise* needs an owner-originated statement, which epic Item 7's scope
item 1 makes its first beat. Manufacturing one at close would be the provenance failure the ledger
exists to prevent.

**No retroactive stage entries were written.** This ledger has a spec block only; it has no
design, plan, implement, or audit block, and none was backfilled. A judgment made with the outcome
in hand is not stage-time evidence. Same disposition as Item 2's R5 and Item 3's close block, and
the same reason.

**Success-criteria checkboxes were ticked at close** in `spec.md` and in the epic's Item 1 section,
each against evidence that already existed at audit or in the orchestrator's probe addendum
(P-1: `check_doc_distinctness.py` 31/0; P-3: companion `git diff --check` clean). No criterion was
ticked on evidence produced by the close pass itself, and no suite was re-run at close.
