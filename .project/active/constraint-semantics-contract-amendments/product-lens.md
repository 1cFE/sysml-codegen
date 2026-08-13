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
