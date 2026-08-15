# Implementation Plan: Item 7 — ADR, Product Promise, and Agent-Facing Documentation Sync

**Status:** Complete (2 owner calls open — see Phase 4 and Phase 5 notes)
**Created:** 2026-08-14
**Last Updated:** 2026-08-14
**Epic:** CONSTRAINT-SEMANTICS — `.project/backlog/epic_constraint_semantics_contract.md` (`:1041-1150`)
**Branches:** codegen `item7-rebuild` · agentic-mbse worktree `/home/reid/1cfe/agentic-mbse-item7-rebuild` (`item7-rebuild`) · TEAx `/home/reid/1cfe/teax` (`constraint-semantics-item3`)

## Source Documents

- **Spec (the contract):** `.project/active/constraint-docs-agent-sync/spec.md`
- **Owner checkpoint (payload — verbatim rules apply):** `.project/active/constraint-docs-agent-sync/owner-checkpoint-20260813.md`
- **Product-lens ledger:** `.project/active/constraint-docs-agent-sync/product-lens.md` (Gate: DISPOSED, item7-F1..F3)
- **Design:** none. See "Design decisions" below — this item runs without a design stage by
  orchestrator decision, and the four calls the spec deferred are made here.
- **Method referent (Item 1's recorded sweep):**
  `.project/completed/20260813_constraint-semantics-contract-amendments/design.md:1191-1230` (Appendix D)
  and its executed record `.../verification.md` — copy that file's shape, not its contents.

---

## The Point

A design search only means something if the engineer can trust what it says about feasibility.
The owner stated the promise in their own words:

> **[OWNER-VERBATIM, 2026-08-13]**
> The system seeks to enable a design search where:
> - engineering design parameters can be freely varied, and viability and outcomes (like LCOE)
>   can be assessed
> - we differentiate from 1costingFE in that we do not embed the engineering logic:
>   predetermining the free variables and backing into all others

(`owner-checkpoint-20260813.md:9-13`. Payload under capture-fidelity law 2 — it survives verbatim,
never reworded, at the owner's emphasis.)

The enforcement-side companion, cited beside it and never merged into it, is the epic's `[OWNER]`
Critical Success Factor: a design search can trust the generated feasibility evidence to represent
every applicable asserted physics gate, while every other authored constraint remains **visibly
dispositioned**.

The CONSTRAINT-SEMANTICS epic built that. Items 1–6, 8 and 9 changed how constraints are cataloged,
executed, dispositioned, and reported. What did not change is the documentation that teaches it —
and "visibly dispositioned" is a documentation obligation as much as a code one. Three costs are
live today, each verified in this plan's Phase 1 sizing:

1. **The promise has no home.** No `.project/product/` directory exists (verified). The only ADR
   defined anywhere in this repo is ADR-009, as a section of `docs/architecture/modeling-assumptions.md:588`
   (verified: `grep "ADR-0[0-9][0-9]"` across `docs/`, `CLAUDE.md`, `.claude/` finds ADR-001 and
   ADR-003 *cited* but never defined). Item 3's audit filed this as `audit-F4` with "no home
   available."
2. **Shipped surfaces teach the superseded shape.** `.claude/skills/sysml-conventions/SKILL.md:136`
   is `assert constraint TempLimit { temperature < 1000 [K] }` — an inline predicate with a unit
   literal, exactly what the bindings-only blessed pattern supersedes (verified verbatim).
   agentic-mbse `docs/patterns/constraints.md` has **zero** occurrences of "inapplicable" (verified).
   TEAx `docs/evaluation-and-study.md:77` still teaches the three-state constraint map with
   `not_assessed` reserved, and no living TEAx doc mentions `full_satisfaction`, `partial_coverage`,
   the keep-for-boundary default, or the feed-strategy opt-in (verified).
3. **Four obligations have no other vehicle.** Item 1 is archived, so design-F2's Appendix C cell,
   the D9 authoring-time advisory, the item3-F2 ruling, and the Item 5 residual A-8 matrix
   reconciliation land here or nowhere.

The falsifier the work is checked against: a next authoring session — human or agent — reads a
shipped surface in any of the three repos and reproduces the superseded constraint shape; or the
promise is filed where its wording drifted, its tension with the A5/A6/A7 basis rulings reads as
silently resolved, or a reader cannot reach it from the product-lens trail.

This item documents what landed. It changes no behavior.

---

## Design decisions

Four calls the spec deferred to design. **[AGENT, orchestrator 2026-08-14]** ruled that no separate
design stage runs — this is documentation-only and the spec carries the requirements. The calls are
made here, each grounded in a fact verified at plan stage. They are agent-grade and challengeable by
re-deriving against the reasoning recorded with each.

### D-1 — Product/ADR home shape

**Decision.** Two homes, one authority each, and no new registry file for ADRs.

- **Product ledger (new):** `.project/product/INDEX.md`, one line per entry
  (`- [P-001 — Title](P-001-slug.md) — one-line hook`), with the entry body in a sibling file
  `.project/product/P-001-design-search-free-variation.md`. Id rule: `P-NNN`, zero-padded, minted in
  INDEX order, never reused, never renumbered.
- **ADR convention (kept where it is):** an ADR is a numbered section of
  `docs/architecture/modeling-assumptions.md` titled `## N. Title (ADR-0NN)`. Next free id is
  **ADR-010**. This item mints no ADR.
- **ADR-009 back-registers — as a citation, not a move.** `.project/product/INDEX.md` gains a row
  pointing at `modeling-assumptions.md:588`. The ADR text does not move.

**Why.** The default of record (ledger + per-repo ADR convention) is adopted, but the "convention"
already exists and inventing a second one would fork the authority. The evidence: exactly one ADR
is defined in the tree, as a modeling-assumptions section, while ADR-001 and ADR-003 are cited from
CLAUDE.md with no definition anywhere. Minting an `docs/adr/` directory now would leave three ADRs
in two places and two of them still undefined — worse than the condition audit-F4 complained about.
The product ledger is genuinely new because nothing plays its role, and `.project/product/INDEX.md`
is the path the global context-loading rule already names, so a future session finds it without
being told. Back-registering ADR-009 as a row costs one line and makes the ledger the single index a
lens run can resolve against; rewriting ADR-009 into the ledger would duplicate a settled decision
record and is out of scope.

**Where the lens-trail citation is wired** (spec's item7-F2 requirement — the enforceable half of
SC1). Three points, because the item's own ledger archives at close and a citation that archives
reproduces audit-F4 one directory over:

1. `.project/product/INDEX.md` — the durable home, in a live directory that is not archived.
2. `.project/backlog/epic_constraint_semantics_contract.md`, the epic's product-lens block
   (`:130-135`) — the durable **trail** node, where a future lens run for any item descended from
   this epic starts. This is the one that discharges "cited from the product-lens trail."
3. `.project/active/constraint-docs-agent-sync/product-lens.md` — a close-stage block recording
   that this run wired it. This is the run record, not the durable citation.

`completed/20260813_constraint-coverage-policy/product-lens.md` (audit-F4's own ledger) is archived:
**cited, never edited.**

### D-2 — Sweep-record home and format

**Decision.** One file, `.project/active/constraint-docs-agent-sync/verification.md`, covering all
three repos in one set of tables. Shape copied from Item 1's executed record
(`completed/20260813_constraint-semantics-contract-amendments/verification.md`): scope-and-exclusions
header, sweep-terms table, Table 1 pre-edit hits + dispositions, Table 2 post-edit re-run, then the
mechanical-check results. One row per raw hit; a summary does not discharge SC2. A hit left unchanged
is a disposition and gets its row.

**Why.** SC2's claim is a *three-repo* claim, so an auditor reading three separate per-repo files has
to join them to check it. Item 1 already proved the single-file shape works across two repos and its
record is in-tree to copy from, which also keeps the citation trail between the two items short.
Keeping the record in the codegen item home (not one file per repo) also means the agentic-mbse and
TEAx working trees take **no** `.project/` writes from this item beyond their in-scope doc edits.

**Vendored-corpora sub-exclusion, carried forward from Item 1's recorded precedent**
(`verification.md:32-40`). agentic-mbse's `docs/sysmlv2/` and `docs/syside/` trees are third-party
reference material — OMG SysML v2 specification documents, the standard library, and generated
SysIDE API docs. This item has no authority to amend them. Their hits are aggregated by directory
with counts and file lists rather than one row per line, and the aggregation is flagged so an auditor
sees exactly what was set aside. Every project-authored hit gets its own row. This is a recorded
deviation from one-row-per-hit, not a silent one, and it matters: the Phase 1 sizing shows the
vendored trees carry ~44 of agentic-mbse's ~80 raw hits.

### D-3 — Matrix row granularity

**Decision.** **One row per REQ tag**, filed into the existing family tables — not one row per
family, and not one row per landed gate.

**Why.** The matrix's unit is already one row per REQ tag; its own header calls it a "matrix mapping
every REQ-\* tag to its conformance test file and status," and the summary counts rows as
"Total requirements: 276" against "REQ families: 32." A per-family row would be a second, incompatible
row kind in the same tables. Per-gate is the same mistake from the other side: a gate without a REQ
tag has nothing for the Status column to be about.

**Surfaced count conflict — do not silently pick one.** The recount baseline the brief carries
(BACKLOG:464-466: "276 rows / 275 PASS / 32 families") **contradicts the matrix's own summary block**,
which reads Total 276 / PASS 133 / PARTIAL 3 / RETIRED 131 / UNTESTED 9 / families 32. Those sum to
276, so the matrix block is internally consistent and BACKLOG's "275 PASS" is stale — it predates the
Item 7 retirement re-cite (matrix header: "re-cited against the retired tree, Revise step 6d,
2026-08-12"). Phase 6 recounts from the tables (index totals **and** per-family counts, per project
memory `verification-matrix-drift-modes`), corrects whichever block the recount falsifies, and
records the correction in `verification.md`. It does not adopt either number on trust.

**No aspirational citations.** Verify which test pins which claim before citing it
(`[MATRIX-EPIC-SURFACE-ROWS]`, BACKLOG:447-466).

### D-4 — TEAx sweep scope boundary

**Decision.** S1–S5 transfer to TEAx **unchanged**; no local term is added. Scope, stated in the
sweep record:

- **In:** `docs/`, `README.md`, `CLAUDE.md`, `.claude/`, and `packages/*/` source and tests
  (`--include=*.md --include=*.py --include=*.sysml`).
- **Excluded, with reason:** `.venv/` and `node_modules/` (installed third-party code, not authored
  here); `.pytest_cache/` (generated); `thoughts/` and `.project/{completed,active,research}/`
  (dated records — the DD5 exclusion rule, same reasoning).
- Generated fixture trees under `packages/teax-simkit/simkit/tests/evaluation/fixtures/*/package_live/`
  stay **in scope** and are dispositioned as generated output, not excluded — they are what a reader
  of the test suite actually sees.

**Why no local term.** Adding is allowed, dropping is not (`design.md:1224-1225`), so the bar for
adding is a TEAx idiom the five terms miss. The plan-stage pre-run found none: S1, S2, S3, S5 all
return **zero** in TEAx, and S4 returns **9**, every one of which is TEAx's own migration text
naming `all_satisfied` as the *retired* token (e.g.
`packages/teax-simkit/simkit/evaluation/evidence.py:47` "``all_satisfied`` became
``full_satisfaction`` because state 3's meaning strengthened"). That is the S4 quoted-supersession
class, already correct as written. Item 3 corrected four TEAx sites and the sweep confirms it held.
The exclusions are the load-bearing part of the TEAx boundary, not the terms.

---

## Implementation Strategy

**Phasing rationale.** Two hard orderings drive everything.

- **Inventory before edits.** S4 hits the amended text this item writes, because amendment notes
  quote the superseded precedence verbatim. Item 1 resolved that collision in advance: run S4
  **pre-edit** (`design.md:1220-1222`). So the whole S1–S5 inventory runs first, in all three repos,
  and the raw output is recorded before a single doc line changes.
- **Amendments before the rewrites that cite them.** The item3-F2 contract amendment and the
  design-F2 Appendix C cell fix land before the cross-repo rewrites, because those rewrites cite the
  amended clauses. A rewrite citing an unamended clause is a stale citation the moment the amendment
  lands.

Everything after that is ordered by dependency: the ledger home exists before the trail cites it;
the matrix reconciliation runs after the edits it accounts for; verification is last because
archival and path breakage is a known failure mode at close.

**Critical path.** Phase 1 (inventory) → Phase 2 (amendments) → Phase 4 (rewrites) → Phase 6
(verification). Phase 3 (promise home) and Phase 5 (matrix) hang off the path and can run in either
order between Phase 2 and Phase 6.

**First proof point.** Phase 1's recorded pre-edit sweep. It is the only artifact that can
substantiate SC2, and it is the thing that tells us whether the item is 3 hours or 6 — the plan's
own sizing run says ~45 codegen hits, ~80 agentic-mbse hits (~44 of them vendored and aggregated),
and 9 TEAx hits.

**Validation approach.** This item writes prose, so each phase's "test" is the check written before
the edit: the exact grep or read whose output is recorded in `verification.md`. Phase 6 re-runs the
mechanical checks and adds the licensed elaboration run.

**Multi-session resumption.** Check the boxes as you go and fill "Implementation Notes" per phase.
A resuming session reads the last checked box and continues; it does **not** re-run Phase 1's
pre-edit sweep, because that record's value is that it predates the edits.

---

## Phase 1 — Recorded sweep inventory, all three repos (pre-edit)

### Goal

Produce the pre-edit half of `verification.md`: scope, exclusions, terms, and one dispositioned row
per raw hit across codegen, agentic-mbse, and TEAx. Nothing outside `.project/` is edited in this
phase, in any repo.

### Assumption Under Test

That the five terms over the stated three-repo scope actually surface the superseded teaching the
spec names — and that they surface nothing large and unexpected that would resize the item.

### Check to write first

```bash
# The five terms. Run per repo with that repo's scope. Record RAW output, then disposition.
SCOPE_CODEGEN="docs src tests scripts README.md CLAUDE.md .project/concepts .project/backlog .claude"
INC="--include=*.md --include=*.py --include=*.sysml"
grep -rn  "test_constraint_migration_mapping" $SCOPE_CODEGEN $INC                        # S1
grep -rn  "require constraint" $SCOPE_CODEGEN $INC                                        # S2
grep -rniE "constraint[s]? (are |is )?(enforced|checked|verified|evaluated|a gate|gates|blocks)|enforced (gate|constraint)|plain constraint.*(execut|enforc|gate|check|verif|evaluat|block)" $SCOPE_CODEGEN $INC   # S3
grep -rniE "all[_ ]satisfied|else any assessed|any assessed result" $SCOPE_CODEGEN $INC   # S4  ← MUST run pre-edit
grep -rnE "assume constraint|satisfy requirement" $SCOPE_CODEGEN $INC                     # S5
```

Pass condition: every raw hit appears as a row in Table 1 with a disposition. A summary does not
discharge the criterion.

### Changes required

- [x] Create `.project/active/constraint-docs-agent-sync/verification.md`, header shape copied from
      `.project/completed/20260813_constraint-semantics-contract-amendments/verification.md:1-55`
- [x] Record the **DD5 scope and its exclusions** verbatim in reasoning: in `docs/`, `src/`, `tests/`,
      `scripts/`, `README.md`, `CLAUDE.md`, `.project/concepts/`, `.project/backlog/`; excluded
      `.project/research/`, `.project/completed/`, `.project/active/` — dated records. Plus `.claude/`
      as a recorded scope addition (Item 1 added `claude/` in the companion for the same reason;
      adding is allowed).
- [x] Record the **TEAx scope per D-4**, with its exclusions and their reasons
- [x] Record the **vendored-corpora sub-exclusion per D-2**, flagged as an aggregation
- [x] Run S1–S5 in **codegen**; one row per raw hit. Sizing run 2026-08-14 (re-run, do not copy):
      S1→0, S2→13, S3→7, S4→20, S5→5
- [x] Run S1–S5 in **agentic-mbse** (`/home/reid/1cfe/agentic-mbse-item7-rebuild`); sizing:
      S1→0, S2→21, S3→8, S4→0, S5→51 — of which the vendored `docs/sysmlv2/` + `docs/syside/` trees
      carry roughly S2 15 / S3 4 / S5 33, aggregated per D-2
- [x] Run S1–S5 in **TEAx** (`/home/reid/1cfe/teax`); sizing: S1/S2/S3/S5→0, S4→9, all
      quoted-supersession
- [x] Table 1 complete: file:line, quoted hit, disposition, note

### Validation

- [x] Row count in Table 1 ≥ the raw hit count minus the aggregated vendored hits; the aggregation
      rows state their counts
- [x] `git status` in agentic-mbse and TEAx is clean (this phase writes only in codegen `.project/`)

**What we know after this phase:** exactly which surfaces teach the superseded semantics, and which
hits are correct as written. Phases 2–4 edit only what Table 1 marks for correction.

---

## Phase 2 — Amendments (must precede every rewrite that cites them)

### Goal

Land the item3-F2 contract amendment and the design-F2 Appendix C cell fix, and flip every parked
item3-F2 conflict record to RESOLVED-with-citation.

### Assumption Under Test

That the three named clause sites are the only live carriers of the blanket BLOCK clause, and the
three named parked-record sites the only live carriers of the unresolved conflict. If Phase 1's S3/S4
rows surface a fourth site, it flips too (spec `:281-285`).

### Check to write first

```bash
# Every live statement of the blanket BLOCK clause and of the parked conflict.
grep -rn "halts generation" .project/concepts/ docs/architecture/
grep -rn "item3-F2" .project/active/ .project/backlog/
```

### Changes required

Amendment mechanics follow the conventions Item 1 set: **provenance preserved and the original text
recorded, not overwritten.** Referent:
`.project/completed/20260813_constraint-semantics-contract-amendments/design.md:1202-1218`.

- [x] `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md:131` — invariant 1,
      blanket BLOCK clause → **reaching-gates scope**
- [x] `…lifecycle-contract.md:441` — "Headline states and coverage truth", same amendment
- [x] `…lifecycle-contract.md:794` — Appendix C "ADMIT + NON_NUMERICAL + BLOCK mix", same amendment
- [x] `…lifecycle-contract.md:793` — **design-F2**: the vacuous-gate cell over-permits in the
      degenerate case; add "…and at least one gate remains". Behavior is already settled by Item 3
      design D4's published RULING (*not assessed*); only the contract text is being fixed
- [x] Amendment note records the ruling grade verbatim: `[AGENT] (ratified by owner, 2026-08-13)`,
      citing `owner-checkpoint-20260813.md:38-53`
- [x] `.project/active/constraint-semantics-contract/spec.md:195` — the `[HARD]` blanket clause →
      RESOLVED-with-citation
- [x] `.project/active/constraint-semantics-contract/spec.md:294` — the Non-Goal "changing
      BLOCK-halts-generation semantics" → RESOLVED-with-citation
- [x] `.project/backlog/epic_constraint_semantics_contract.md:531-539` — the residual entry ("It
      stays a surfaced premise conflict in both directions until then") → RESOLVED-with-citation
- [x] Any fourth site Phase 1 surfaced → flipped, and named in `verification.md` — **none surfaced**
- [x] *(pulled forward from Phase 4)* `docs/architecture/modeling-assumptions.md:451` and its §8
      BLOCK bullet — the same blanket clause, reconciled here so Phase 2's own validation grep holds

**Do not edit** `completed/20260813_constraint-coverage-policy/product-lens.md:58-66` — archived,
cited only.

### Validation

- [x] `grep -rn "halts generation" .project/concepts/ docs/` returns no unqualified blanket statement
- [x] No live site still describes item3-F2 as an open or parked conflict
- [x] Each amended clause carries its original text in an amendment note

**What we know after this phase:** the clauses the Phase 4 rewrites cite say what the rewrites will
claim they say.

---

## Phase 3 — The promise, its home, and the lens-trail citation

### Goal

File the coverage-truth promise in its first durable home per D-1, and wire the citation from the
product-lens trail. Closes Item 3 `audit-F4` and epic SC1.

### Assumption Under Test

That a filed entry plus three citation points is reachable — that a future lens run starting from the
epic's ledger block lands on the promise without being told where to look.

### Check to write first

```bash
# The trail test: start where a lens run starts, and see if you reach the promise.
grep -n "product-lens\|product/INDEX" .project/backlog/epic_constraint_semantics_contract.md
cat .project/product/INDEX.md
# The payload test: the two owner bullets, byte-for-byte.
diff <(sed -n '9,13p' .project/active/constraint-docs-agent-sync/owner-checkpoint-20260813.md) \
     <(sed -n '/OWNER-VERBATIM/,/backing into all others/p' .project/product/P-001-*.md | grep '^>')
```

### Changes required

- [x] Create `.project/product/INDEX.md` — ledger header + row for P-001 + back-registration row for
      ADR-009 pointing at `docs/architecture/modeling-assumptions.md:588`
- [x] Create `.project/product/P-001-design-search-free-variation.md`:
  - [x] The `[OWNER-VERBATIM, 2026-08-13]` two bullets as the **core**, reproduced exactly, at the
        owner's emphasis, path-cited to `owner-checkpoint-20260813.md:9-13`. No rewording, no
        paraphrase, no "improved" version
  - [x] Supplementary material gleaned from the concepts, each marked `[INHERITED: <source>]` per
        source — start from `.project/concepts/constraint-execution-and-design-space-studies.md:15`
        (calculations compute a candidate state, constraints judge it, a study varies inputs and
        applies user-selected feasibility policy) and
        `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md`. It supplements;
        it never rewrites the core
  - [x] The epic's `[OWNER]` Critical Success Factor cited **beside** the promise as its
        enforcement-side companion, not merged into it
  - [x] The promise stated as **directional intent**, with `[ACAUSAL-RELATIONS-CAPABILITY]`
        (BACKLOG:439) named for the unbuilt half. The tension with the ratified A5/A6/A7 basis
        rulings is **surfaced in daylight in the entry itself** — carried from
        `owner-checkpoint-20260813.md:28-36`, not re-derived, and **not open for re-resolution here**
- [x] Wire citation point 2: a pointer in the epic's product-lens block,
      `.project/backlog/epic_constraint_semantics_contract.md:130-135`
- [x] Wire citation point 3: a close-stage block in
      `.project/active/constraint-docs-agent-sync/product-lens.md` recording that the trail was wired
- [x] Add a `.project/product/INDEX.md` pointer to codegen `CLAUDE.md` so the global context-loading
      rule resolves

### Validation

- [x] The verbatim diff above is empty
- [x] Every supplementary paragraph carries an `[INHERITED: <source>]` mark
- [x] The tension paragraph exists and resolves nothing in either direction
- [x] Starting from the epic ledger block, the promise is reachable in one hop

**What we know after this phase:** audit-F4's condition — a promise with no entry a lens run can
resolve against — no longer holds, and it does not hold one directory over either.

---

## Phase 4 — Cross-repo documentation, skills, and agent prompts

### Goal

Correct every hit Table 1 marks for correction, and add the missing teaching so the disposition
vocabulary, the six states, `@inapplicable:`, and the TEAx opt-in are where their users will find
them.

### Assumption Under Test

That the missing teaching has an obvious home in each repo, and that correcting the named stale sites
does not require touching the retiring-banner reference docs (which CLAUDE.md rules out as a separate
authorship pass).

### Check to write first

```bash
# Each of these must return a hit AFTER the phase, and returns none today (verified 2026-08-14).
grep -c "inapplicable" /home/reid/1cfe/agentic-mbse-item7-rebuild/docs/patterns/constraints.md     # 0 today
grep -cE "full_satisfaction|partial_coverage" /home/reid/1cfe/teax/docs/evaluation-and-study.md    # 0 today
grep -c "assert constraint TempLimit" .claude/skills/sysml-conventions/SKILL.md                    # 1 today → 0
```

### Changes required

**Codegen — `docs/architecture/modeling-assumptions.md` is the live authority; the reference docs
are not.** Doc 28 carries a retiring banner that already states the corrected vocabulary in summary
and whose rewrite is an explicitly separate authorship pass (CLAUDE.md, "Retired — read before
trusting a document"). Do not rewrite it. Doc 30 (`30-diagnostic-severity.md`) is Active and is the
home for severity-by-cause.

- [x] `modeling-assumptions.md` §8 (`:448`) — rewrite the **unit-on-binding** account. The current
      text "A unit on a constraint *binding* is carried, not checked" describes pre-Item-8 behavior
      and is false as written. Item 8's landed behavior: authored unit text on constraint-formal and
      computed-attribute ports, fail-closed `SI_RENDERING_COLLISION` on unequal metadata
      (`completed/20260813_unit-lane-port-metadata/`)
- [x] `modeling-assumptions.md` §8 — reconcile the blanket BLOCK statement with the Phase 2
      amendment (reaching-gates scope)
- [x] `modeling-assumptions.md` §8/§9 — the **disposition vocabulary**: `eligible` / `excluded` /
      `non_reaching`, the closed reason set per kind, precedence, carriers, and the totality gate.
      Citable source: `completed/20260813_constraint-catalog-totality/design.md`
- [x] `docs/architecture/reference/30-diagnostic-severity.md` — severity-by-cause
- [x] Every remaining codegen Table 1 row marked for correction

**Codegen agent surfaces**

- [x] `.claude/skills/sysml-conventions/SKILL.md:136` — replace the inline-assert-with-unit-literal
      example with the **bindings-only blessed pattern**; add a pointer to the equality-intent
      taxonomy and `@inapplicable:` usage
- [x] `CLAUDE.md` — swept for superseded constraint teaching
- [x] `.claude/agents/*.md` expert definitions — swept (agentic-mbse's `.claude/agents/sysml-expert.md`
      carried an S2 hit in the sizing run; check the codegen equivalents the same way)

**agentic-mbse — `/home/reid/1cfe/agentic-mbse-item7-rebuild`, branch `item7-rebuild`**

- [x] `docs/patterns/constraints.md` — `@inapplicable:` authoring; the eligible+inapplicable refusal
      (D9); and the **D9 authoring-time advisory** (the re-homed orphan — D9 already refuses the
      combination loudly at generation time, so nothing ships wrong; the advisory catches it a step
      earlier)
- [x] `docs/patterns/constraints.md`, `syntax-reference.md`, `semantic-operators.md`,
      `common-mistakes.md` — the project-authored S2/S3/S5 rows from Table 1
- [x] `CLAUDE.md` and `.claude/agents/sysml-expert.md` — swept
- [x] **Vendored `docs/sysmlv2/` and `docs/syside/` are not edited.** Aggregated and dispositioned
      out of class per D-2

**TEAx — `/home/reid/1cfe/teax`, branch `constraint-semantics-item3`. Never `main`. Nothing is ever
pushed.**

- [x] `docs/evaluation-and-study.md` — the **six report states**, the coverage block, the policy
      defaults, the **keep-for-boundary default with the feed-strategy opt-in config**, and the
      durable-record fields. `:77`'s three-state constraint map is the site to extend; `:115`
      already names the four dispositions and is the hook for the opt-in
- [x] TEAx `CLAUDE.md` — swept
- [x] TEAx's 9 S4 rows dispositioned as **correct as written** (quoted supersession) — a disposition
      is a row, not an omission

**Where an inapplicability marker actually works (Item 5 close obligation, both authoring repos)**

- [x] State plainly: an `@inapplicable:` marker on a **bindings-form** constraint reaches the domain;
      on an **inline-predicate** constraint SysIDE silently drops it, so until
      `[INLINE-PREDICATE-MARKER-DROP]` (BACKLOG:1152) closes, that disposition is recorded in the
      fixture's PROVENANCE instead of in source
- [x] Cite the worked case (`catf_mfe_gated` B1–B5: five markers written, zero carried) and the loud
      detector (`tests/conformance/test_constraint_population_oracle.py` rule 3). Item 5 owns those
      files — **cite, do not rewrite**
- [x] The test the text has to pass: a modeler can tell, **before authoring**, which mechanism
      carries their disposition

### Validation

- [x] The three post-phase greps above return the expected counts
- [x] Every Table 1 row marked for correction has a corresponding edit
- [x] `git status` in TEAx shows branch `constraint-semantics-item3`, no `main` involvement, nothing
      pushed

**What we know after this phase:** the falsifier is closed on the shipped surfaces — an authoring
session reading any of the three repos gets the landed policy.

---

## Phase 5 — Verification-matrix reconciliation (Item 5 residual A-8)

### Goal

File matrix rows for the constraint-semantics gates landed across Items 2–5 in **one pass**, with
the recount done. Per-item filing is how the matrix drifted; that is why this is one pass and not
five.

### Assumption Under Test

That the landed gates have REQ tags to file rows against, and that each cited test actually pins the
claim its row makes.

### Check to write first

```bash
# Recount from the tables, not the summary block (memory: verification-matrix-drift-modes).
grep -c "^| REQ-" docs/architecture/verification-matrix.md          # total rows
grep -oE "^\| REQ-[A-Z]+" docs/architecture/verification-matrix.md | sort -u | wc -l   # families
grep -oE "\| (PASS|PARTIAL|RETIRED|UNTESTED|DEFERRED) " docs/architecture/verification-matrix.md | sort | uniq -c
# For every row you file: run the cited test and watch it pass. No aspirational citations.
```

### Changes required

- [x] Identify the REQ tags for the gates landed in Items 2–5 from their closed-item records under
      `.project/completed/20260813_*`
- [x] File one row per REQ tag into the existing family tables (D-3)
- [x] Run each cited test before citing it; a row whose test does not pin its claim gets `UNTESTED`
      or `PARTIAL` with the gap named in the cell, not a PASS
- [x] Recount and correct the summary block: totals, per-status counts, family count, distinct test
      files cited
- [x] Resolve the surfaced count conflict per D-3 and record the resolution in `verification.md`;
      correct BACKLOG:464-466 if the recount falsifies it

### Validation

- [x] Per-status counts sum to the total row count
- [x] Family count matches the distinct REQ-prefix count from the tables
- [x] Every newly cited test file exists and was run

**What we know after this phase:** the epic's landed gates are traceable, and the matrix's own
numbers are true against its tables.

---

## Phase 6 — Verification and close-out

### Goal

Re-run the mechanical checks, run the one licensed check this item needs, and confirm nothing broke
in any of the three repos.

### Assumption Under Test

That the edits introduced no whitespace damage, no dead path, and no example that fails to elaborate
— and that a licensed toolchain is actually available.

### Check to write first

```bash
# The one licensed run. Exactly these terms — never `uv run`.
set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a
/home/reid/1cfe/item7-rebuild-venv/bin/python -m pytest tests/ 2>&1 | tee /tmp/item7-licensed.log
grep -c "no live syside license" /tmp/item7-licensed.log     # MUST be 0
```

### Changes required

- [x] **Post-edit sweep (Table 2).** Re-run S1–S5 in all three repos. Disposition any post-edit S4
      hit inside an amendment note as "quoted supersession, correct as written" — the collision
      Item 1 resolved in advance (`design.md:1220-1222`)
- [x] **Licensed elaboration check.** Verify the agent-facing examples (the corrected `SKILL.md`
      constraint example and any `@inapplicable:` snippet added to the authoring docs) elaborate
      cleanly under the current profile, using **exactly** the license source, interpreter, and
      zero-skip-line proof above. **Zero `no live syside license` lines is the only proof of a
      licensed run** — a green run with those skips present does not discharge this
  - [x] **If the license is unavailable at implement time:** record the check as a **named residual**
        in `verification.md`. Never silently skipped, never ticked unverified
- [x] **`git diff --check`** in all three repos — codegen, agentic-mbse worktree, TEAx
- [x] **Collect sanity check** in codegen: `/home/reid/1cfe/item7-rebuild-venv/bin/python -m pytest
      tests/ --collect-only -q | tail -3` — archival and path breakage is a known failure mode at
      close, and this catches it
- [x] Confirm branch discipline: TEAx on `constraint-semantics-item3`, agentic-mbse on
      `item7-rebuild`, codegen on `item7-rebuild`, **no `main` touched anywhere, nothing pushed**
- [x] Tick the six epic success criteria in `spec.md` against evidence, each with its
      `verification.md` reference
- [x] Update `.project/CURRENT_WORK.md`

### Validation

- [x] Table 2 complete; every post-edit hit dispositioned
- [x] `grep -c "no live syside license"` → **0**, or a named residual recorded
- [x] `git diff --check` clean in three repos
- [x] Collect count unchanged from pre-item baseline
- [x] All six SC boxes ticked with evidence, or explicitly not ticked with the reason recorded

**What we know after this phase:** the item is auditable end to end and safe to `close`.

---

## Working boundaries

- **[NEED, OWNER 2026-08-14]** The item runs through `close` (archive). The **epic stays open**:
  epic close, `pre_pr`, and any push are reserved to the owner.
- **[NEED, OWNER, standing]** All TEAx edits stay on `constraint-semantics-item3`. `main` is never
  touched in any repo. The agentic-mbse surface is the worktree
  `/home/reid/1cfe/agentic-mbse-item7-rebuild` (branch `item7-rebuild`) — the editable install reads
  it.
- **Non-goals** (spec `:246-253`): any code, fixture, or schema change; re-litigating the contract or
  re-resolving the promise-vs-basis tension; the derivative fixture docs (Item 5 owns its PROVENANCE
  and worked example — cite, do not rewrite); epic close, `pre_pr`, pushing.

---

## Risks

- **The licensed run is unavailable.** Highest-probability blocker, and the only requirement here
  that needs a toolchain. Mitigation: it is last, it blocks nothing else, and its fallback (a named
  residual) is pre-authorized by the spec (`:189-190`).
- **The vendored-corpora aggregation reads as a dodge.** ~44 of agentic-mbse's raw hits are in
  third-party spec mirrors. Mitigation: Item 1 set the precedent and recorded it
  (`verification.md:32-40`); this item copies the shape, states counts and file lists, and flags the
  aggregation so an auditor sees exactly what was set aside.
- **A fourth item3-F2 site turns up during the sweep.** Mitigation: the spec pre-authorizes the flip
  (`:281-285`); Phase 2's assumption-under-test names it, and Phase 1 runs first so it would be found
  before the amendments land.
- **Matrix count conflict resolved by picking a number.** Mitigation: D-3 forbids it — Phase 5
  recounts from the tables and records which block it corrected.
- **Cross-repo edits drift onto the wrong branch.** Mitigation: Phase 6 confirms branch state in all
  three repos explicitly, and Phase 1 verifies both companion repos are clean before any edit.

---

## Implementation Notes

[TO BE FILLED DURING IMPLEMENTATION]

### Phase 1 Completion

**Completed:** 2026-08-14

**Actual changes:** Created `.project/active/constraint-docs-agent-sync/verification.md` — scope and
exclusions for all three repos, the five sweep terms, the raw-count table, and Table 1 with 70
individual dispositioned rows plus 15 flagged aggregation rows covering the 64 vendored hits.
Nothing outside `.project/` was touched, in any repo.

**Raw counts (executed 2026-08-14, pre-edit).** codegen S1→0 S2→13 S3→7 S4→20 S5→5 (45);
agentic-mbse S1→0 S2→21 S3→8 S4→0 S5→51 (80, of which 64 vendored / 16 project-authored);
TEAx S1/S2/S3/S5→0 S4→9. Total 134 raw hits, all accounted for (70 rows + 64 aggregated).

**Issues:**

- **The sweep found zero fix-here hits in any of the three repos.** Item 1 corrected codegen and
  agentic-mbse with these same five terms and Item 3 corrected TEAx; nothing regressed. This is
  recorded explicitly in `verification.md` because it is easy to misread as "nothing needed
  fixing." The Phase 2–4 work is (a) named obligations the sweep terms do not match
  (`modeling-assumptions.md:530` unit-on-binding, `:451` blanket BLOCK) and (b) **absent** teaching,
  which no sweep can surface. Both verified independently: `grep -c "inapplicable"` on agentic-mbse
  `docs/patterns/constraints.md` → 0; `grep -cE "full_satisfaction|partial_coverage"` on TEAx
  `docs/evaluation-and-study.md` → 0.
- **No fourth item3-F2 site.** `grep -rn "halts generation" .project/concepts/ docs/` returns
  lifecycle contract invariant 1 plus three unrelated statements (extraction diagnostics, INV-2).
  The three named clause sites and three named parked-record sites stand as the complete set.

**Deviations:**

- **Vendored-hit sizing was low.** The plan estimated the vendored share of agentic-mbse at ~44
  (S2 15 / S3 4 / S5 33). The executed run measures **64** (S2 15 / S3 4 / S5 **45**) — 35 of the S5
  hits in `docs/sysmlv2/SysML_Spec_v2_Part1/full_document.md` alone. Recorded in `verification.md`.
  The project-authored counts (6/4/6) are what the item acts on and are unchanged in character, so
  this does not resize the item. Every other sizing number matched the executed run exactly.
- **Line-number drift in plan citations.** `modeling-assumptions.md`'s unit-on-binding paragraph is
  at `:530`, not the plan's `:448` (which is §8's heading); the §8 blanket-BLOCK headline is at
  `:451`. Actual line numbers are used from here on.

### Phase 2 Completion

**Completed:** 2026-08-14

**Actual changes:**

- `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md` invariant 1
  (`:130-153`) — BLOCK-halts scoped to asserted usages **that reach occurrences**, with a blockquote
  amendment note carrying the original clause text verbatim, the ruling grade
  `[AGENT] (ratified by owner, 2026-08-13)`, the checkpoint path-cite, and the three-way dependency
  (non-raising mint, vacuous-gate warning grade, derivative held-intent rows).
- Same file, "Headline states and coverage truth" (`:466-472`) — a new "When the `BLOCK`ed-asserted
  case is reachable" paragraph. This is what turns the denominator clause from dead text into live
  text: its reachable population is exactly the non-reaching case.
- Same file, Appendix C "ADMIT + NON_NUMERICAL + BLOCK mix" (`:820`) — the halt scoped in the cell.
- Same file, Appendix C "Asserted vacuous gate" (`:819`) — **design-F2**: "and at least one gate
  remains" inserted, with a ‡ note below the table recording the previous wording, the degenerate
  case it over-permitted (empty denominator → vacuously-true full satisfaction), and that Item 3
  design D4's RULING already settled the behavior as *not assessed*. No behavior change.
- `.project/active/constraint-semantics-contract/spec.md:195` — the `[HARD]` clause flipped to
  RESOLVED-with-citation and restated in scoped form, tagged so no later agent reads the blanket
  form as live.
- Same file `:303` — the Non-Goal annotated: it held for that spec's own work and still does; the
  clause it referred to was separately amended here.
- `.project/backlog/epic_constraint_semantics_contract.md:531-544` — the residual flipped from
  `[DEFERRED, surfaced not resolved]` to `[RESOLVED 2026-08-13, executed 2026-08-14 by Item 7]`,
  naming the ruling, the executed sites, and that it is no longer a conflict in either direction.
- `docs/architecture/modeling-assumptions.md:450-452` and the §8 BLOCK bullet — the same amendment
  (pulled forward from Phase 4; see below).

**Issues:**

- **`modeling-assumptions.md:451` carried the blanket clause too**, and Phase 2's own validation grep
  spans `docs/`. The plan filed that site under Phase 4. Reconciling it in Phase 2 was the only way
  Phase 2's validation could pass honestly, and it is the identical amendment. Recorded here and
  ticked in Phase 4's list rather than done twice.

**Deviations:**

- **Amendment notes are blockquotes attached to the clause, not a separate log.** Item 1's
  convention is "provenance preserved and the original text recorded, not overwritten," which it
  discharged by pairing an inline `(amended DATE, ITEM)` marker with the original text quoted in
  ADR-009's "What the contract said" block. This item mints no ADR (plan D-1), so there is no
  decision record to carry the original text. Attaching the note to the clause keeps the original
  wording one line from the amended wording, which is where a reader challenging the ruling needs it.
- **No fourth item3-F2 site.** The pre-authorized flip was not needed.

### Phase 3 Completion

**Completed:** 2026-08-14

**Actual changes:**

- **New:** `.project/product/INDEX.md` — the ledger. Header states the `P-NNN` id rule and the ADR
  convention (an ADR is a numbered section of `modeling-assumptions.md`; no `docs/adr/` directory;
  next free id ADR-010). One promise row (P-001) and one back-registration row (ADR-009 → `:588`).
- **New:** `.project/product/P-001-design-search-free-variation.md` — the owner's two bullets
  verbatim as the core, the epic's `[OWNER]` CSF cited beside them under its own heading, five
  `[INHERITED: <source>]` supplementary paragraphs, and a "surfaced, not resolved" tension section.
- `.project/backlog/epic_constraint_semantics_contract.md` Product-Lens section header — citation
  point 2, the durable trail node.
- `.project/active/constraint-docs-agent-sync/product-lens.md` — an implement-stage block recording
  the wiring. Gate CLEAR, no new finding.
- `CLAUDE.md` — a "Product Promises" section pointing at the ledger, so the global context-loading
  rule ("skim `.project/product/INDEX.md` if present") resolves for a future session. It also states
  the ADR convention where an agent looking for `docs/adr/` will hit it.

**Verification:**

- Payload diff — `diff <(sed -n '9,13p' owner-checkpoint-20260813.md) <(… P-001 …)` → **empty**.
  The two bullets are byte-identical.
- `grep -c "^\*\*\[INHERITED:" P-001-…md` → **5**. Every supplementary paragraph is marked with its
  source.
- Trail — `.project/backlog/epic_constraint_semantics_contract.md:120` links `../product/INDEX.md`
  and P-001 directly. One hop from where a lens run starts.

**Issues:** none.

**Deviations:**

- **The CSF is a section, not a sentence in the promise section.** The plan said "cited beside, not
  merged." Giving it its own heading with its own `[OWNER]` grade makes the separation structural
  rather than a matter of paragraph order — a later editor cannot fold them together by accident.
- **Five INHERITED paragraphs, not the two named starting sources.** The plan named
  `constraint-execution-and-design-space-studies.md:15` and the lifecycle contract as *starting*
  points. The glean pulled two paragraphs from the studies doc (`:15` three-responsibility split,
  `:17` layer split), two from the lifecycle contract (headline coverage truth; the disposition
  vocabulary from invariant 1 as amended in Phase 2), and one from ADR-009. Each carries its own
  source mark. This is the owner's "you could probably glean more from the concept docs"
  instruction (`owner-checkpoint-20260813.md:15-16`) executed, not scope creep.

### Phase 4 Completion

**Completed:** 2026-08-14

**Actual changes — codegen**

- `docs/architecture/modeling-assumptions.md` §8, unit-on-binding — **rewritten**. The old text
  ("carried, not checked") described pre-Item-8 behavior. New text: authored unit reaches
  `PortMetadata.unit` on constraint-formal and computed-attribute ports; two consumers of one shared
  value that disagree fail closed with `SI_RENDERING_COLLISION`; no conversion anywhere; the
  operand-category point is kept because it is still true.
- Same file, new **"The disposition vocabulary"** subsection — the three kinds with their closed
  reason sets as a table, the one-rule precedence, where each disposition sits relative to the
  feasibility denominator, the carriers, and the totality gate. Cited to
  `elaboration/graph.py:259-277` and `generation/coverage.py:57-71`, which is where the closed sets
  actually live.
- Same file, new **"Where an `@inapplicable:` marker actually works"** subsection — the
  bindings-vs-inline table, `[INLINE-PREDICATE-MARKER-DROP]`, the B1–B5 worked case and the rule-3
  detector (cited, not restated — Item 5 owns them), and D9.
- `docs/architecture/reference/30-diagnostic-severity.md`, new **"Severity by cause"** section —
  the reason × form severity table, why the same cause grades differently under an asserted form,
  and two explicit non-consequences: severity does not decide the halt, and it does not decide the
  denominator.

**Actual changes — agentic-mbse worktree**

- `docs/patterns/constraints.md`, new **"Marking a constraint inapplicable"** section — why the
  denominator matters, how to write the marker, the bindings-vs-inline table with the silent-drop
  warning, the worked case, and D9 with its authoring-time advisory framed as "D9 one step earlier."
- `claude/skills/sysml-conventions/SKILL.md` — the stale inline-assert-with-unit-literal example
  replaced with the bindings-only blessed pattern, three rules, the `@inapplicable:` block, and the
  four-intent equality taxonomy as a table.
- `.claude/agents/sysml-expert.md` — Item 1's D5-a settled-semantics sentence added. This copy had
  never received it (see Issues).

**Actual changes — TEAx (`constraint-semantics-item3`)**

- `docs/evaluation-and-study.md`, new **"The headline is a coverage claim"** subsection — the
  six states as a two-vocabulary table with the normalization seam, the unconstrained sixth state
  carried by report *absence*, and the `all_satisfied` refuse-by-name note. Replaces the
  three-state map at the old `:77`.
- Same file, new **"The coverage block"** — what `_coverage_of` copies and why (query off the case
  row without opening artifacts).
- Same file, new **"Policy defaults"** — the headline → disposition table, the reasoning behind the
  `keep-for-boundary` default for `partial_coverage`, the `feed-strategy` opt-in as a YAML line, and
  its three safety properties (identical path, stays visible, starts a new lineage).
- Same file, new **"What reaches the durable record"**.

**Issues — a premise conflict, surfaced not resolved (recorded in full in `verification.md`)**

- **Codegen has no agent surfaces of its own.** Every file under codegen `.claude/agents/` and
  `.claude/skills/sysml-conventions/` is a symlink resolving to `/home/reid/1cfe/agentic-mbse/claude/…`
  — the **main** agentic-mbse checkout, on branch `elaborate-first-salvage`. Not the authorized
  worktree. The plan's "check the codegen equivalents the same way" has no referent: they are the
  same files by a second path.
- **agentic-mbse tracks two divergent copies** of the agent definitions, `claude/` (37 files) and
  `.claude/` (23 files). `sysml-expert.md` differs: `claude/` has Item 1's D5-a correction, `.claude/`
  does not. Item 1 corrected `claude/` only. Fixed `.claude/` here.
- **Sweep-scope defect in Table 1.** `grep -r` does not follow symlinked files, so codegen's
  `.claude/` was swept as empty in Phase 1, and the worktree's `claude/` tree was outside the Phase 1
  agentic-mbse scope (that run used `.claude`). Both swept in Phase 4; two rows added (71, 72), both
  "correct as written" — one of them *is* Item 1's correction. Raw total 134 → 136.
- **Named residual: SC2/SC3 are not fully discharged for codegen agent readers.** A Claude session
  in the codegen checkout still reads the superseded example, because its symlinks resolve to a
  checkout this item may not edit. Post-edit evidence:
  `grep -c "assert constraint TempLimit" .claude/skills/…/SKILL.md` in codegen → **1**, where the
  plan's Phase 4 check expected 0. The in-bounds copy of the same file reads 0. The falsifier stays
  open on that one path until `item7-rebuild` reaches the branch the symlinks resolve to.
- **In-boundary excursion, caught and reverted.** Before the symlink topology was understood, one
  SKILL.md edit was written through the codegen path and landed in `/home/reid/1cfe/agentic-mbse` on
  `elaborate-first-salvage`. Reverted with `git checkout --` on discovery; that checkout verified
  clean (`git status --short` empty, branch unchanged), no commit, nothing pushed. Recorded because
  a silent revert is not a record.

**Deviations:**

- **The `modeling-assumptions.md` BLOCK reconciliation landed in Phase 2**, not here — see Phase 2's
  notes. Its box is ticked in both lists rather than the work being done twice.
- **The skill and agent edits went to the worktree copies**, not through the codegen symlink path
  the plan named. This is the hard boundary applied literally, and it is why the codegen-side check
  still reads 1.
- **TEAx's `CLAUDE.md` needed no edit.** Swept: two `constraint` mentions, one a TypeVar remark and
  one the `tracking_key` correlation rule, both correct. agentic-mbse `CLAUDE.md` likewise — one
  mention, an L4 validator-level label. Recorded as dispositions, not skips.

### Phase 5 Completion

**Completed:** 2026-08-14 — **partially. Read the surfaced conflict below before treating A-8 as
discharged.**

**Actual changes:**

- `docs/architecture/verification-matrix.md` — new **DIAG family**, four rows (REQ-DIAG-01..04), with
  an index entry and the filing reason stated in the family header.
- Same file, summary block **corrected by recount** and annotated with what the recount falsified.
- Same file, "Untested Requirements" — REQ-DIAG-04 added as the tenth, explicitly *not* retirement
  debt, with its own reason.
- `.project/backlog/BACKLOG.md:464-466` — the stale baseline corrected, with the correction stated
  rather than silently swapped.

**The recount (D-3: recount, do not adopt either number on trust).** Counting method matters here —
several cells carry a status word inside an explanatory note, and one row has an extra pipe, so a
naive `grep -c` returns 281 against 276 rows. Correct method: per row, take the **last** field
matching a status keyword.

| Metric | Summary claimed | Tables held | Verdict |
|---|---|---|---|
| PASS | 133 | **134** | block stale |
| PARTIAL | 3 | **2** | block stale |
| Distinct kept test files | 50 | **57** | block stale |
| Total / RETIRED / UNTESTED / families | 276 / 131 / 9 / 32 | same | agreed |

The drift is one row: `REQ-CL-04`, upgraded PARTIAL → PASS when audit-7 F2 closed without the
summary following. **BACKLOG's "275 PASS" was false against every reading** — not merely stale, as
the plan supposed. Both blocks corrected; neither adopted.

Post-filing: **280 / PASS 136 / PARTIAL 3 / RETIRED 131 / UNTESTED 10 / DEFERRED 0 / 33 families /
55 kept test files** (the file count was corrected from 59 at the audit resume; method in `verification.md`). Statuses sum to the total ✅; family count matches the distinct REQ-prefix
count ✅.

**No aspirational citations.** Every cited test was run first —
`test_extraction_diagnostic_screen.py` + `test_upstream_pins.py` → **11 passed**. Two rows
deliberately did not get a PASS: REQ-DIAG-01 is PARTIAL (the kept test pins the upstream schema
string, not the no-reader-side-table property), and REQ-DIAG-04 is UNTESTED (nothing would fail if
the envelope started carrying severity again). Both gaps are named in their cells.

**Issues — second premise conflict, surfaced not resolved:**

- **Phase 5's assumption under test is false.** It assumes the landed gates have REQ tags to file
  rows against. Items 3, 5, 8 and 9 carry **zero** REQ tags in their closed records; Item 2 carries
  four, and two of those (`REQ-CL-04`, `REQ-EXT-09`) were already filed. The only genuinely missing
  tag-backed rows were `REQ-DIAG-01`/`-03` — a family that lived in doc 30's prose with no matrix
  rows at all. Those are filed, plus `-02` and `-04` from the same table, since filing half a family
  reproduces the gap one row over.
- **Filing rows for the untagged gates would mean minting REQ tags first.** That is a requirements
  decision, not a matrix reconciliation, and D-3 rules out the alternative explicitly ("a gate
  without a REQ tag has nothing for the Status column to be about"). Minting an agent-authored tag
  family inside this item would put invented requirement ids into the one document whose value is
  that its rows trace to stated requirements. Parked for an owner call.
- **Item 5 residual A-8 is therefore PARTIALLY discharged**, not fully: recount done, tag-backed gap
  filed, untagged gates of Items 3/5/8/9 still untraced.

**Deviations:**

- **Four rows filed, not two.** The two missing tag-backed rows were `REQ-DIAG-01` and `-03`; `-02`
  and `-04` were filed alongside them so the family is whole. Recorded rather than silently rounded.

### Phase 6 Completion

**Completed:** 2026-08-14

**Post-edit sweep (Table 2).** Codegen is **identical hit for hit** to pre-edit (0/13/7/20/5) — only
line numbers moved, which is the expected result given the codegen sweep found zero fix-here rows.
agentic-mbse S2 +4 / S5 +1, TEAx S4 +1. All six new hits dispositioned individually in
`verification.md`; four are text this item authored and every one names a superseded token **in order
to retire it** — exactly the quoted-supersession class Item 1 pre-authorized, which is why S4 ran
pre-edit.

**Licensed elaboration check — DISCHARGED, no residual needed.**
`2070 passed, 34 skipped, 79 deselected` in 157s, and
`grep -c "no live syside license"` → **0**. All 34 skips accounted for and none license-related
(25 "no computed attributes in the golden", 9 "no calc output expressions in the golden").

**Other mechanical checks.** `git diff --check` clean in all three repos. Collect sanity
`2104/2183 tests collected (79 deselected)`, no collection errors — the archival/path-breakage
failure mode did not occur. Branch discipline verified: codegen `item7-rebuild`, agentic-mbse
worktree `item7-rebuild`, TEAx `constraint-semantics-item3`, agentic-mbse main checkout clean on
`elaborate-first-salvage`. **`main` untouched everywhere, nothing pushed.**

**Success criteria: 4 of 6 ticked.** SC1, SC3, SC4, SC6 met with evidence. SC2 and SC5 **explicitly
not ticked, with the reason recorded** in `spec.md` and `verification.md` — the two surfaced premise
conflicts from Phases 4 and 5. Both need an owner call; neither is more implementation work.

**Issues:**

- **One honest limit on the licensed check.** The suite proves the tree elaborates licensed. It does
  not elaborate the new SKILL.md snippet directly, because that snippet is illustrative and is not a
  fixture — making it one would be a fixture change the Non-Goals forbid. Recorded in
  `verification.md` rather than left as an implied stronger claim.

**Deviations:** none in this phase.

---

**Status:** Draft → In Progress → **Complete** (phases 1–6 executed 2026-08-14)
**Next:** owner decisions on the two surfaced conflicts, then `/_my_audit` → `/_my_close`
