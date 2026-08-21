# Epic: Repo Cleanup — Keep the Decisions, Delete the Exhaust

**Epic ID**: REPO-CLEANUP
**Status**: In Progress
**Priority**: P1
**Created**: 2026-08-20
**Estimated Effort**: ~8-11 days (8 items)

---

## Executive Summary

The repository is 880k lines, of which the product is 15k. `.project/` is 78% of the tree and
109,720 of its lines are byte-exact duplicates of other committed files. This epic extracts the
durable decisions and product promises out of that archive into the two load-bearing registers
(`.project/adr/`, `.project/product/`), then deletes the archive, then turns the same discipline
on the test suite and the code — asking of each, not "does it exist" but "what does it defend".

**Critical Success Factor**: Every settled decision that a future agent would otherwise
re-derive wrongly survives as a cited ADR or product promise entry — *before* anything is
deleted. Deletion is the last beat of each track, never the first.

---

## Why This Epic?

**Current State** (measured 2026-08-20, `.project/research/20260820-201945_line-count-anatomy-and-salvageability.md`):

- `.project/` is **675,740 lines / 1,781 files — 78% of the repo, 30.5× `src/`**. Durable
  decision content is ~23%; the rest is raw logs (156k), JSON dumps (138k), plans (89k),
  and audit prose (79k). `ruff_all.log` alone is committed 10 times for 120,736 lines.
- **Exactly one `.project` file is read by any tool** (`ledger/ledger-4a.json`). 25 of the 48
  distinct `.project` paths cited from `src/` and `tests/` no longer exist — the archive is
  already failing its own citation contract.
- **40 of 48 `.project/active/` directories are closed items never archived** (74,233 lines),
  shadowing copies already in `completed/`.
- The two durable registers are half-installed: `.project/product/` holds 4 promises but
  `.project/scripts/product.sh` is absent, and **`.project/adr/` does not exist at all** — this
  repo instead keeps ADRs as numbered sections of `docs/architecture/modeling-assumptions.md`.
- `tests/` is 148,391 lines but only 30,824 are Python. ~73,400 lines are vestigial committed
  data. 32% of test functions are license-gated and the execution lane is excluded by default,
  so a default run exercises about two-thirds of the suite. **Nothing measures whether the
  2,492 test functions actually defend anything.**
- `src/` is well-factored (2.0% duplication, median function 15 lines) but carries **~2,370
  lines (15%) of dead code** — the elaborate-first cutover deleted the consumers and left the
  producers standing, pinned in place by test families that outlived their subject. A further
  ~11,400 lines outside `src/` verify the *process* rather than the model.

**Future State**:

- Two durable registers carry the settled knowledge: `.project/adr/` for decisions ("use the
  parser, do not write custom patches"; the elaborate-first insights) and `.project/product/`
  for promises. Both script-managed, indexed, append-only.
- `.project/` is roughly 60-90k lines of decision record, research, and live work — no console
  scrollback, no machine-generated JSON, no un-archived shadow copies.
- A written coverage inventory says which meaningful functions, invariants, and end-to-end
  flows are actually defended, backed by an objective signal rather than a test count.
- Dead code is gone, and every remaining non-production surface (`verification/`,
  `scripts/archive/`, process tests) has an owner ruling: durable, or retired with its item.

---

## Register Boundary — Owner Ruling (settled)

`[OWNER, 2026-08-20]` **Split by subject.** Two registers, divided by who the decision binds:

- **`docs/architecture/modeling-assumptions.md`** keeps decisions that bind the **model author** —
  how SysML models must be written and interpreted. Its nine existing ADRs are of this kind
  (library/design separation, input parameter classification, aggregation via redefinition,
  template instantiation, arrayed-children enumeration, constraint profiles). It stays
  product-facing documentation with its existing `ADR-0NN` ids; next free is ADR-010.
- **`.project/adr/`** takes decisions that bind the **toolchain builder** — how we build this
  product. "Use the parser, do not create custom patches" is this kind. So are the
  elaborate-first insights.

Owner note: *"we have a similar challenge with all our claude commands."* The criterion must
therefore be written to generalize — one statable line, not a bespoke list of subjects — so the
same ruling can be cited by that work rather than re-derived. `[OWNER, 2026-08-20]`

Consequences for Item 1:

- **Id namespaces are already distinct and must stay that way.** `adr.sh` allocates four-digit
  ids and filenames (`0001-slug.md`); the modeling-assumptions register uses `ADR-0NN`. No
  collision exists, but the citation forms are confusable in prose — Item 1 settles how each is
  cited so `ADR-009` and pack entry `0009` can never be mistaken for each other.
- **Existing ADRs default to staying put.** Pack entries are append-only and a body is immutable
  after filing, so re-homing an ADR is a supersession, not a move. Item 1 triages the nine against
  the criterion and only files a successor where one is genuinely builder-facing rather than
  author-facing; churn is not the goal.
- `CLAUDE.md` and `.project/product/INDEX.md` both currently state there is one ADR home. Both
  paragraphs are wrong under this ruling and Item 1 corrects them.

---

## Success Criteria

- [ ] The subject-split criterion is recorded as a `.project/adr/` entry, stated generally
      enough to be cited by the claude-commands work rather than re-derived there
- [ ] `.project/` scaffolding matches the current `agentic-project-init` pack, including the
      product-intent-ledger docs and both `adr.sh` and `product.sh` engines
- [ ] A written harvest inventory lists every candidate decision and promise found in the
      archive, with its source path, and the owner has ruled each one in or out
- [ ] Every ruled-in decision exists as an ADR entry with a `Why` section a future challenge
      can re-derive against; every ruled-in promise exists as a product ledger entry with
      graded Authority citations
- [ ] `.project/` is under 100k lines, with zero committed `.log`/`.console` files, zero
      byte-exact duplicate files over 2KB, and zero stale `active/` directories
- [ ] Zero broken `.project` path citations remain in `src/`, `tests/`, or `docs/`
- [ ] A coverage inventory document maps meaningful functions, invariants, and end-to-end
      flows to the tests that defend them, and names the gaps — backed by a measured signal,
      not a test count
- [ ] Tests that defend nothing are deleted, and every deletion names what it was believed to
      defend and why that belief was wrong
- [ ] The ~2,370 lines of dead `src/` code are deleted, together with the test families that
      pinned them, in commits that retire both at once
- [ ] `verification/`, `scripts/archive/`, and the retired reference docs each have a recorded
      disposition: durable, relocated, or deleted
- [ ] The full test suite is green at every item boundary, with the license loaded

---

## Epic Strategy

**Value delivery path.** The value is not the deleted lines — it is that after this epic a cold
agent can learn what was settled, and why, in an afternoon instead of by reading 675k lines of
archive. Every item is therefore ordered so that *extraction precedes deletion*. Nothing is
deleted in Items 1-4; nothing is extracted in Item 5. The same shape repeats on the code side:
Item 6 measures and reports, Items 7-8 act on the report.

**Decomposition rationale.** Two tracks with one principle.

- **Knowledge track (1-5)** moves durable content out of a disposable archive into two
  script-managed registers, then empties the archive. It is sequential because each beat's
  output is the next beat's input, and because the purge is only safe once the harvest has
  been ruled on.
- **Code track (6-8)** asks what the tests and code actually defend, then removes what defends
  nothing. It is sequential because the audit must not grade its own homework: Item 6 produces
  a report the owner rules on, and only then does Item 7 delete.

The tracks are technically independent and could run in parallel, halving the calendar. The
owner's stated order runs them sequentially and that is the default. The one coupling that
survives parallelization runs knowledge → code: Item 3's ADRs record *why* code was written,
which is the input Item 8 needs to judge one-time-use code. If the tracks are parallelized,
Item 8 still lands after Item 3.

**Critical path**: 1 → 2 → 3 → 5 → 6 → 7 → 8. Item 4 runs alongside Item 3 and is not on it.

**De-risking.** Two bets are tested before dependents build on them.

- *Item 6, Phase 1 is a spike.* The whole coverage audit rests on the assumption that real
  coverage can be distinguished from test volume by measurement rather than opinion. Mutation
  testing on two representative modules answers that in half a day, and if the tooling cannot
  run against this codebase we learn it before committing two days to the item.
- *Item 2 is itself the de-risk for Item 5.* The purge is the least reversible-feeling step in
  the epic. Item 2 exists so that what would be lost is enumerated and owner-ruled before
  anything is removed.

---

## Backlog Items

### Item 1: Scaffolding Reinstall and Register Boundary

**Type**: Code/Integration
**Effort**: 1 day (spec 1h, design 1h, plan 1h, execute 5h)
**Dependencies**: None
**Implementation Status**: Phase 4 complete 2026-08-21; awaiting Phase 5. The audience-based
criterion is `.project/adr/0001`, all nine existing decisions are triaged, and the two-register
convention is documented. Sections 1–6 and 8 are author-facing; ADR-007 and ADR-009 are
builder-facing and carried to Item 3 for re-homing. The safe documentation contract passed 12/12,
and the runnable licensed suite passed 2,371 with 9 policy skips. The exact full-suite gate remains
unavailable because this checkout has no current five-repository artifact manifest.

**Objective**: Bring `.project/` scaffolding up to the current `agentic-project-init` pack,
install both decision registers with their engines, and record the subject-split criterion so
the boundary between them is settled once rather than re-derived per entry.

**Current State**:
- ✅ `.project/product/` has four `000N` entries, generated index reachability, and truthful provenance
- ✅ `.project/scripts/` contains the installed `adr.sh` and `product.sh` engines
- ✅ `.project/adr/0001` carries the owner-grade routing criterion and its generated index is stable
- ✅ `CLAUDE.md` and `.project/product/README.md` describe both registers and path-qualified citations
- ✅ All nine existing decisions are triaged; ADR-007 and ADR-009 are carried to Item 3
- ⏳ The four product entries still have `checked: null`; Phase 5 owns their verification stamps

**Scope**:
1. **Install the pack**: `project-pack/adr/`, `project-pack/product/README.md`,
   `scripts/adr.sh`, `scripts/product.sh`, and the refreshed `EPIC_GUIDE.md` /
   `epic_template.md`. Verify against the pack's own `test_adr.sh` and `test_product.sh`.
2. **File the criterion** as the first `.project/adr/` entry, `[OWNER]` provenance, settled.
   State it as one line that generalizes — the owner has the same boundary problem in the
   claude commands and must be able to cite this rather than re-derive it.
3. **Settle the citation forms.** `adr.sh` allocates four-digit ids (`0001-slug.md`); the
   modeling-assumptions register uses `ADR-0NN`. They do not collide mechanically but read
   confusably in prose. Fix the convention and apply it in the two docs below.
4. **Triage the nine existing ADRs** against the criterion and **record the outcomes — move
   nothing** `[OWNER, 2026-08-21]`. Sections 1–6 and 8 are author-facing and stay. `ADR-007`
   (Compute Once, Look Up Thereafter) and `ADR-009` (Coverage Truth and Headline Semantics) are
   builder-facing and recorded as misfiled; **Item 3 performs both re-homes** (step 2a there), so
   this item keeps to scaffolding.
5. **Correct the convention in `CLAUDE.md` and relocate the generated index's durable guidance to
   `.project/product/README.md`**.
6. **Back-register** the existing four promises' `checked` stamps through `product.sh` so the
   ledger's frontmatter is script-managed from here on.
**Out of Scope**:
- Authoring any decision or promise content beyond the criterion entry (Items 3 and 4)
- Deleting anything from `.project/` (Item 5)
- Changing `agentic-project-init` itself, or applying the criterion to the claude commands
- The `contracts/serialize.py` `allow_nan` defect and the false V11 preflight claims. Briefly
  parked here by product-lens `epic_plan-F6`; they are unrelated to scaffolding and are now
  standalone backlog items `[SERIALIZE-NAN-SEAL]` and `[V11-DEAD-GATE-DOCS]` `[OWNER, 2026-08-20]`

**Success Criteria**:
- [x] `.project/adr/` exists with a generated `INDEX.md`; `adr.sh` and `product.sh` are
      installed and their pack test suites pass against this checkout
- [x] The criterion entry is filed, `[OWNER]` graded, and states the boundary in one line that
      does not name this repo's specific subjects
- [x] Each of the nine existing ADRs has a recorded triage outcome; ADR-007 and ADR-009 are
      recorded as builder-facing with their moves carried to Item 3, and nothing is moved by this
      item
- [x] `CLAUDE.md` and `.project/product/README.md` describe the two-register convention and the
      citation forms, with no remaining claim of a single home
- [ ] `.project/product/` frontmatter is script-managed; a `product.sh index` regeneration
      produces the committed `INDEX.md` byte-for-byte, and Phase 5 stamps all four checks
- [x] Licensed runnable suite green with the license loaded under the accepted missing-manifest
      limitation; exact full-suite validation remains unavailable rather than green

**Location**: `.project/active/scaffolding-register-boundary/`

**Required Reading**:
- `agentic-project-init/project-pack/adr/README.md` and `product/README.md` — the two registers'
  contracts, including append-only lifecycle and the promise-vs-decision boundary
- `agentic-project-init/project-pack/scripts/adr.sh`, `product.sh` — id allocation, status flips
- `.project/product/INDEX.md` and its four entries — what must survive unchanged
- `docs/architecture/modeling-assumptions.md` — the nine ADRs being triaged
- `claude-pack/rules/capture-fidelity.md` — provenance grades and the settled rule

**Deliverables**:
- `.project/active/scaffolding-register-boundary/{spec,design,plan}.md`
- `.project/adr/` with the criterion entry and a generated `INDEX.md`
- `.project/scripts/{adr.sh,product.sh}`
- `.project/active/scaffolding-register-boundary/adr-triage.md` — the nine, with outcomes

---

### Item 2: Decision Harvest Inventory

**Type**: Research
**Effort**: 1.5 days (spec 1h, design 1h, plan 1h, execute 9h)
**Dependencies**: Item 1 (needs the criterion to classify candidates)

**Objective**: Read the archive once and produce a single candidate register of every decision
and promise worth keeping, so the owner can rule each in or out before anything is deleted.

**Current State**:
- ✅ 124 completed item directories, 63 research documents, 55 concept documents, 2 epic files
- ⚠️ The knowledge is real but unindexed — semantic redundancy is high (one item is re-narrated
      across spec → design → design-review → plan → audit → phase-audits → briefs, 47 files)
- ❌ No inventory exists of what is settled versus what was merely discussed
- ❓ Whether the owner-named seeds ("use the parser, do not create custom patches"; the
      elaborate-first insights) already have durable homes or exist only in archive prose

**Scope**:
1. **Sweep the archive** — `.project/completed/` (124 dirs), `.project/research/` (63),
   `.project/concepts/` (55), `.project/backlog/` epics, `.project/reports/`,
   `.project/CURRENT_WORK.md` history.
2. **Produce one candidate register**, one row per candidate: the claim in one line, its source
   path, the proposed home (ADR / product promise / neither), the provenance grade the source
   supports, and a one-line "what a future agent would re-derive wrongly without this".
3. **Seed the register with the owner's named items** and find their authority: "use the
   parser, do not create custom patches"; the elaborate-first insights (exact identity over
   string matching, occurrence enumeration over qualified-name matching, refuse rather than
   work around). These are the acceptance test for the harvest — if the sweep does not surface
   them independently, the sweep is not thorough enough.
4. **Apply the density bar from each register's README**, not a lower one. The ADR bar is
   "without this a future agent would re-derive the wrong thing or relitigate"; the promise bar
   is "a major use case, public surface, or cross-cutting contract that a cold agent could miss
   or undo". Sparseness is the point; most rows should be ruled out.
5. **Harvest the test-and-code rationale too** (product-lens `epic_plan-F5`). Items 7 and 8
   must answer "what was this test believed to defend, and why was that belief wrong" and "why
   was this dead code left standing" — and that rationale lives in the `active/` and
   `completed/` material Item 5 removes first. Under the owner's sequential order the archive
   would be destroyed one item before it is needed. So this item also captures: the retirement
   records behind the ~2,370 dead `src/` lines, and what each vestigial test family and fixture
   corpus was built to defend. Recorded as a separate register so it survives the purge.
6. **Flag the archive's own broken citations** — 25 of 48 `.project` paths cited from `src/`,
   `tests/`, and `docs/` no longer exist. Record which cited content is durable (and so must be
   harvested) versus which is already lost.
7. **Owner rules each row** in or out. That ruling is the gate for Items 3, 4, and 5.

**Out of Scope**:
- Writing any ADR or promise body (Items 3 and 4)
- Deleting anything (Item 5)
- Re-verifying that recorded decisions are still true in code — the registers record what was
  decided and when, not current state

**Success Criteria**:
- [ ] The candidate register covers every directory in `.project/completed/`, `research/`, and
      `concepts/`, with coverage demonstrable by directory count
- [ ] Each row carries claim, source path, proposed home, provenance grade, and the
      re-derivation risk it guards against
- [ ] The owner's three named seeds appear with located authority, or are explicitly recorded
      as having no durable source (making them first-capture entries in Item 3)
- [ ] Every row has an owner ruling: in, out, or deferred
- [ ] The count of ruled-in rows is small relative to candidates — a register that keeps most
      of what it finds has failed the density bar
- [ ] Broken-citation triage recorded: which durable content is at risk, which is already lost
- [ ] A test-and-code rationale register exists, covering every dead `src/` lane named in the
      research and every vestigial test family and fixture corpus — so Items 7 and 8 can be
      executed after Item 5 has deleted the archive

**Location**: `.project/active/decision-harvest/`

**Required Reading**:
- `.project/adr/README.md` and `.project/product/README.md` (installed by Item 1) — the two
  density bars, verbatim; do not soften them
- The Item 1 criterion entry — how to classify a candidate into a home
- `claude-pack/rules/capture-fidelity.md` — provenance grading and the absorb mapping
- `.project/research/20260820-201945_line-count-anatomy-and-salvageability.md` §8 — the
  `.project` category table, which says where durable content is concentrated

**Deliverables**:
- `.project/active/decision-harvest/{spec,design,plan}.md`
- `.project/active/decision-harvest/candidate-register.md` — the rows, with owner rulings
- `.project/active/decision-harvest/citation-triage.md` — the 25 broken citations, dispositioned
- `.project/active/decision-harvest/test-code-rationale.md` — why each dead lane and vestigial
  test family exists, harvested before Item 5 destroys its sources

---

### Item 3: Author the Decision Records

**Type**: Implementation
**Effort**: 1.5 days (spec 1h, design 1h, plan 1h, execute 9h)
**Dependencies**: Item 2 (needs the ruled register)

**Objective**: Write every ruled-in decision as an ADR in its correct register, each with a
`Why` section that a future challenge re-derives against rather than relitigates.

**Current State**:
- ✅ Nine ADRs exist in `docs/architecture/modeling-assumptions.md`, triaged by Item 1
- ✅ The ruled register from Item 2 names what to write
- ❌ The owner's named decisions have no durable home — "use the parser, do not create custom
      patches" exists today only as archive prose and as the negative space around `0003` and
      `0004`
- ⚠️ Elaborate-first's insights are recorded across `CLAUDE.md`'s retirement paragraph, an
      epic file, and 175k lines of cutover-recovery archive — accurate but not citable

**Scope**:
1. **Author the builder-facing decisions** into `.project/adr/` via `adr.sh new`, one entry per
   decision, filed at the register the criterion assigns.
2. **Author the author-facing decisions** as new numbered sections of
   `docs/architecture/modeling-assumptions.md`, continuing from ADR-010.
2a. **Re-home ADR-007 and ADR-009** `[OWNER, 2026-08-21]`, deferred here from Item 1's design (D6).
   Compute Once, Look Up Thereafter binds the builder implementing downstream identifier reuse.
   Coverage Truth and Headline Semantics binds report token spellings, generation templates,
   TEAx's `CANONICAL_HEADLINE`, and a normalization seam. File each as a `.project/adr/` entry,
   reduce §§7 and 9 to pointers, and re-derive and repoint their citations in the same change.
   ADR-009's move must include `0001`'s owner-verbatim Authority citation. Item 1's
   `adr-triage.md` carries both recorded outcomes.
3. **Write a real `Why` in each.** This is the section that decides whether the entry works.
   An entry whose `Why` is "it was decided" has failed and must be reworked or dropped.
4. **Record rejected alternatives as decision records**, never as instructions to future
   agents — per capture-fidelity law 3, "Out of scope: X is not required because Y", not
   "we must not X".
5. **Grade provenance honestly.** Owner-originated decisions are `[OWNER]` and settled; agent
   recommendations the owner approved are `[AGENT] (ratified by owner, date)` and are
   challengeable by re-deriving against the recorded `Why`.
6. **Cite, do not restate.** Where an entry rests on archive content that Item 5 will delete,
   the entry must carry the substance, not a path into deleted material. This is the specific
   failure mode Item 5 depends on Item 3 avoiding.

**Out of Scope**:
- Product promises (Item 4)
- Verifying the decisions still hold in current code — these are historical records
- Rewriting the twelve retired reference docs (Item 8 dispositions them)

**Success Criteria**:
- [ ] Every ruled-in decision from Item 2 exists as an entry in the register the criterion
      assigns, with no entry in both
- [ ] Every entry has a `Why` that states reasoning, not authority
- [ ] The owner's three named decisions are filed and readable without reference to
      `.project/completed/`
- [ ] No entry's authority depends on a path scheduled for deletion in Item 5 — verified by
      resolving every citation in every new entry
- [ ] Provenance grades match what the source actually supports; no `[AGENT]` item is marked
      settled
- [ ] `adr.sh index` regenerates `INDEX.md` cleanly; ids are script-allocated throughout
- [ ] ADR-007 and ADR-009 are re-homed, `modeling-assumptions.md` §§7 and 9 are pointers, every
      citation resolves, and `0001`'s ADR-009 Authority points to the new entry

**Location**: `.project/active/decision-records/`

**Required Reading**:
- `.project/active/decision-harvest/candidate-register.md` — the ruled rows
- `.project/adr/README.md` — entry format, density bar, amendment care, cross-seam placement
- `claude-pack/rules/capture-fidelity.md` — laws 1 and 3 especially
- `.project/research/20260820-201945_line-count-anatomy-and-salvageability.md` — the
  elaborate-first outcome in measured terms (src −1,544 net), useful `Why` material
- `CLAUDE.md` "Retired — read before trusting a document" — the cutover's recorded scope

**Deliverables**:
- `.project/active/decision-records/{spec,design,plan}.md`
- `.project/adr/NNNN-*.md` entries plus regenerated `INDEX.md`
- New numbered sections in `docs/architecture/modeling-assumptions.md` where author-facing
- `.project/active/decision-records/citation-resolution.md` — proof no entry cites doomed paths

---

### Item 4: Author the Product Promises

**Type**: Implementation
**Effort**: 0.75 day (spec 1h, design 1h, plan 0.5h, execute 4h)
**Dependencies**: Item 2 (needs the ruled register). Runs parallel to Item 3.

**Objective**: Extend the product ledger with the promises the harvest surfaced, so the ledger
is the orientation surface a cold agent and the product-lens can both resolve against.

**Current State**:
- ✅ Four entries exist: `0001` (design search, owner-stated), `0002` (exact owner
      anchoring), `0003` (no workarounds for bad models, `[OWNER-VERBATIM]`), `0004` (product
      identity: parse, walk, emit, `[OWNER-VERBATIM]`)
- ✅ `.project/product/README.md` carries the two-register convention; generated `INDEX.md` contains
      product rows only
- ❌ Promises settled since — snapshot/license decoupling, refusal contracts, the sealed-graph
      guarantee — have no entries
- ⚠️ Existing `checked` stamps remain `null`; Item 1 Phase 5 owns the first script-managed stamp

**Scope**:
1. **Author the ruled-in promises** via `product.sh new`, one entry per promise, titled as the
   promise's one-liner rather than as a surface label.
2. **Write graded Authority citations** for each. Implementation evidence establishes that
   behavior exists; it never creates product authority. An entry resting only on test paths has
   failed and must find a durable source or become a first-capture owner quote.
3. **Stamp `checked`** on new and existing entries via `product.sh check`, with the git ref.
4. **Preserve the four existing entries' visible prose and owner payload unchanged** — they are
   append-only, and two are `[OWNER-VERBATIM]`. The five hidden Markdown destinations ratified for
   Item 1's rename are the sole existing body-byte exception. Any material change is a supersession
   filed as a new entry.

**Out of Scope**:
- Decisions (Item 3) — cite them, do not restate them
- Re-verifying promises hold in code beyond what a `check` stamp honestly asserts
- Any further change to `0001`…`0004` bodies

**Success Criteria**:
- [ ] Every ruled-in promise has an entry whose title states the promise, not a surface
- [ ] Every entry's Authority section cites at least one durable source or carries a dated
      `[OWNER-VERBATIM]` first capture; no entry rests on evidence alone
- [ ] `0001` through `0004` visible prose and owner payload match Item 1's migrated state; the five
      already-ratified Markdown destination changes are not widened
- [ ] `.project/product/README.md` describes the two-register convention and `INDEX.md` remains
      script-generated
- [ ] Every active entry carries a `checked` stamp with a git ref
- [ ] A product-lens run can resolve the ledger index-first without following a dead path

**Location**: `.project/active/product-promises/`

**Required Reading**:
- `.project/product/README.md` — density bar, entry format, the promises-vs-decisions boundary,
  first-capture rule, cross-seam placement
- `.project/product/0001`…`0004` — what already exists and must not change
- `.project/active/decision-harvest/candidate-register.md` — the ruled rows
- `claude-pack/scripts/product-lens.md` — how the ledger gets consumed, so entries are written
  to be resolvable

**Deliverables**:
- `.project/active/product-promises/{spec,design,plan}.md`
- `.project/product/P-NNN-*.md` entries plus regenerated `INDEX.md`

---

### Item 5: `.project` Purge

**Type**: Code/Integration
**Effort**: 1 day (spec 1h, design 1h, plan 1h, execute 5h)
**Dependencies**: Items 3 and 4 (nothing is deleted until the knowledge is out)

**Objective**: Reduce `.project/` from 675,740 lines to a working directory plus two durable
registers, without losing a single ruled-in decision or promise.

**Current State**:
- ✅ Ruled-in knowledge is now in the registers (Items 3 and 4)
- ⚠️ `.project/ledger/ledger-4a.json` is read by three scripts and must survive
- ⚠️ `.project/research/` is the highest value-per-line content in the tree
- ❌ 156,201 lines of committed console output; 137,712 lines of machine JSON; 109,720 lines of
      byte-exact duplicates; `ruff_all.log` committed ten times for 120,736 lines
- ❌ 40 of 48 `.project/active/` directories are closed items never archived (74,233 lines)
- ❓ Whether `.project/completed/` should leave the repo entirely or be trimmed in place

**Scope**:
1. **Stop the recurrence first.** `.gitignore` the log family repo-wide
   (`.project/**/*.log`, `*.console`, `*.err`, `*full-suite.txt`) so the next item cannot
   re-add what this one removes.
2. **Delete the reproducible**: committed logs (−156,201), `runbook-patches/` (−7,272, diffs of
   commits already in git history), the six snapshot-inventory JSONs (−115,315, replaced by
   digests), and the `run1/run2/run3` triplicates (−~28,000, replaced by a three-hash manifest;
   19 of 24 files per run are byte-identical).
3. **Fix the hygiene bug**: archive the 40 stale `active/` directories, and record archive-on-
   close as the standing rule so `active/` stops accumulating a second copy of the process.
4. **Trim `.project/completed/`** to each item's spec, design, audit verdict, and close note —
   or relocate it wholesale, per the owner's ruling on whether agents need it readable at HEAD.
5. **Repair the citations**: fix or remove the 25 broken `.project` paths cited from `src/`,
   `tests/`, and `docs/`, using Item 2's triage.
6. **Protect the registers' own authority** (product-lens `epic_plan-F1`). The ledger says a
   promise not reachable from the index "has no home", and `0001` cites
   `.project/completed/20260814_*`, `.project/concepts/*`, and `.project/backlog/BACKLOG.md:439`
   — while `0002` cites the `20260816_qualified-reference-occurrence-anchoring` spike findings
   and that item's verification ledgers. Item 5 deletes and re-homes exactly that material.
   Before any deletion: resolve every path cited by `.project/product/*` and `.project/adr/*`,
   re-point or preserve each, and convert line-number citations to anchor text. The
   `BACKLOG.md:439` citation has **already drifted** — the target is now at `:552` — so this is
   a live failure, not a hypothetical. Deleting rather than re-pointing any cited path needs an
   owner ruling recorded in the citing entry.
7. **Preserve explicitly**: `.project/adr/`, `.project/product/`, `.project/research/`,
   `.project/ledger/`, `.project/backlog/`, `.project/memories/`, `.project/reference/`,
   `.project/scripts/`, `CURRENT_WORK.md`, and the live `elaborator-downstream` item.

**Out of Scope**:
- Deleting anything under `tests/` or `src/` (Items 7 and 8)
- Rewriting `.project/research/` content
- Any change to the two registers

**Success Criteria**:
- [ ] `.project/` is under 100,000 lines
- [ ] Zero committed `.log`, `.console`, `.err`, or `*full-suite.txt` files, and `.gitignore`
      prevents their return
- [ ] Zero byte-exact duplicate files over 2KB remain, verified by hash sweep
- [ ] `.project/active/` contains only genuinely live items
- [ ] Every citation of a `.project` path from `src/`, `tests/`, and `docs/` resolves
- [ ] Every path cited by `.project/product/*` and `.project/adr/*` resolves after the purge,
      with zero line-number citations remaining (anchor text instead)
- [ ] No path cited by a ledger entry was deleted rather than re-pointed without an owner
      ruling recorded in that entry
- [ ] Every entry in `.project/adr/` and `.project/product/` still resolves all its citations
      — checked after the deletion, not before
- [ ] `ledger-4a.json` still loads through all three consuming scripts
- [ ] Full suite green with the license loaded

**Location**: `.project/active/project-purge/`

**Required Reading**:
- `.project/research/20260820-201945_line-count-anatomy-and-salvageability.md` §8 and
  Recommendations Track 1-2 — the category table, duplicate groups, and preserve list
- `.project/active/decision-harvest/citation-triage.md` — which citations are repairable
- `.project/active/decision-records/citation-resolution.md` — what the registers depend on

**Deliverables**:
- `.project/active/project-purge/{spec,design,plan}.md`
- Updated `.gitignore`
- `.project/active/project-purge/deletion-manifest.md` — what was removed, by category, with
  line counts and the git ref where it remains recoverable
- `.project/active/project-purge/post-purge-citation-check.md`

---

### Item 6: Coverage Audit

**Type**: Testing/Research
**Effort**: 2 days (spec 1h, design 2h, plan 1h, execute 12h)
**Dependencies**: None. Owner's stated order places it after Item 5.

**Objective**: Establish what the test suite actually defends — which meaningful functions,
invariants, and end-to-end flows are protected, and where the gaps are — using a measured
signal rather than a test count. Report only; this item deletes nothing.

**Current State**:
- ✅ 2,492 test functions across 219 Python files, 30,824 lines of test code
- ⚠️ 544 of ~1,700 collected test functions (32%) are license-gated, and `pyproject.toml:46`
      excludes the execution lane by default — a default run exercises about two-thirds
- ⚠️ 106 `@pytest.mark.req(...)` markers exist and nothing verifies the matrix
- ❌ Nothing measures whether any test would fail if the code it covers were wrong
- ❌ Known false defenders: `tests/conformance/test_baselines.py` claims to validate that
      output matches captured baselines and in fact asserts a static file parses;
      `test_v6_snapshot_inventory.py` asserts `isinstance(..., list)` over 7 MB of data
- ❓ Whether mutation testing runs against this codebase at acceptable cost

**Scope**:
1. **Phase 1 — mutation-testing spike (de-risk, half a day, kill criterion).** Run a mutation
   tool against two representative modules — `elaboration/project.py` (projection semantics)
   and `generation/modules.py` (emission) — and measure the mutant kill rate. This converts
   "do we have real coverage" from judgment into a number.
   **Run it with `SYSIDE_LICENSE_KEY` loaded and the execution lane enabled** (product-lens
   `epic_plan-F3`). A default run touches about two-thirds of the suite, so a kill rate measured
   on it would score the live-parser and execution tests near zero and hand Item 7 a
   defensible-looking case for deleting exactly the tests that defend `0004`'s parse step.
   Report gated-lane kill rate separately from default-lane.
   **A low kill rate is evidence for investigation, never sufficient authority to delete.**
   **Kill criterion**: if the tooling cannot run against this codebase within the phase budget,
   stop and fall back to the manual invariant-mapping approach in Phase 2 rather than forcing
   the tool. Record which happened.
2. **Phase 2 — invariant and flow inventory, promise-indexed.** Enumerate the meaningful units:
   the product's invariants (occurrence identity, refusal-before-mutate, byte-identity of sealed
   output, entry-point key rules), the end-to-end flows (live extraction → generation, snapshot
   → generation, generated package → real simkit execution), and the load-bearing functions the
   research identified. Map each to the tests that defend it.
   **`0001` through `0004` are rows in this inventory, not context** (product-lens
   `epic_plan-F2`). Each promise maps to the tests that defend it, and the tests the ledger
   already names as its proof are marked as such: `0002` names
   `tests/conformance/test_usage_owned_reference_anchoring.py` and
   `test_elaboration_public_mutation.py`; `0003` names
   `test_definition_owned_reference_positions.py` and `test_occurrence_domain_derivation.py` as
   "the complete current proof". A ledger-cited test carries a deletion lock into Items 7 and 8.
3. **Phase 3 — grade each mapping.** Real defense, weak defense (asserts shape not behavior),
   or no defense. Name the false defenders explicitly; a test whose docstring overstates what
   it checks is worse than no test because it suppresses the question.
4. **Phase 4 — name the gaps.** What is undefended that matters, ranked. This becomes new-test
   work, filed to the backlog rather than done here.
5. **Separate "gated" from "entangled."** A test that skips without a license is gated by design.
   A test that *raises* without a release-evidence manifest is entangled with machinery it should
   not need — and four of them are product tests, not process tests:
   `test_hierarchy_resolver.py` (761), `test_ast_dispatch_invariant.py` (512),
   `test_self_binding_guidance_contract.py` (260), `test_exact_route_fingerprint_stability.py` (219).
   Grade their coverage on its merits and say what each would need to run from an ordinary checkout.
   **Entanglement is never a reason to delete a product test.** The immediate unblock — flipping the
   gate from raise to skip — is filed separately as `[ARTIFACT-MANIFEST-TESTS-HARD-FAIL]`
   `[OWNER, 2026-08-21]` and is not this item's work.
6. **Account for the gating honestly.** A test that only runs with a license, or only outside
   the default marker set, defends less than its line count suggests. Report effective coverage
   under the default invocation separately from full coverage.

**Out of Scope**:
- Deleting or rewriting any test (Item 7)
- Writing new tests to close gaps — those are filed, not built
- Changing `pyproject.toml` markers or the gating design

**Success Criteria**:
- [ ] The spike has a recorded outcome — a kill-rate number for both modules, or a recorded
      determination that the tooling does not run here, with the reason
- [ ] Every product invariant and end-to-end flow named in the inventory maps to specific
      tests, or is explicitly recorded as undefended
- [ ] Every mapping carries a grade (real / weak / none) with the assertion that justifies it
- [ ] False defenders are listed by `file:line` with what they claim versus what they check
- [ ] Effective default-run coverage is reported separately from license-loaded coverage
- [ ] Every manifest-entangled test is classified product or process, and each product one carries a
      recorded path to running from an ordinary checkout
- [ ] `0001` through `0004` each appear as inventory rows with their defending tests graded,
      and every ledger-cited test is flagged with a deletion lock
- [ ] Every gap exits the item as either a closed gap or a filed `BACKLOG.md` item **with an
      id**, cited from the coverage inventory (product-lens `epic_plan-F4`) — the emit step is
      the live case: `baseline_outputs/` is 13,923 lines whose reader's four assertions pass on
      hand-written stubs, and this epic must not close with that named in a report and owned by
      nobody
- [ ] The report makes no deletion recommendation the owner has not been asked to rule on

**Location**: `.project/active/coverage-audit/`

**Required Reading**:
- `.project/research/20260820-201945_line-count-anatomy-and-salvageability.md` §7 — test
  composition, the false defenders already identified, gating figures
- `.project/product/INDEX.md` and entries — the promises the suite is supposed to defend
- `CLAUDE.md` — the pipeline stages and what each is contracted to guarantee
- `tests/conftest.py` and `pyproject.toml` — the gating and marker design

**Deliverables**:
- `.project/active/coverage-audit/{spec,design,plan}.md`
- `.project/active/coverage-audit/spike-mutation-testing.md` — the Phase 1 outcome
- `.project/active/coverage-audit/coverage-inventory.md` — the mapping with grades
- `.project/active/coverage-audit/gaps.md` — ranked, filed to `BACKLOG.md`

---

### Item 7: Test Remediation

**Type**: Testing
**Effort**: 1.5 days (spec 1h, design 1h, plan 1h, execute 9h)
**Dependencies**: Item 6 (acts on its owner-ruled findings)

**Objective**: Remove the tests and committed data that defend nothing, and correct the ones
whose docstrings overstate what they check — so the suite's size stops implying coverage it
does not have.

**Current State**:
- ✅ Item 6's graded inventory says which tests defend what
- ⚠️ Cross-tier duplication is only ~390 lines (0.9%) — there is little to consolidate
- ❌ ~47,000 lines of `unit_map` JSON whose only assertion is `isinstance(..., list)`
- ❌ `tests/fixtures/baseline_outputs/` (13,923 lines) has one reader that regenerates nothing;
      `golden/calc_def_compilation_golden.json` (3,254) and `baseline_yaml/` (844) have none
- ❌ `catf_mfe_d5` is a 5,718-line copy differing by four lines, with a generator script already
      committed; ~20 of `test_d5_variants.py`'s 31 tests test that script's CLI, not the product
- ⚠️ Some process tests belong to items that closed months ago

**Scope**:
1. **Delete tests that defend nothing**, each deletion naming in the commit what it was
   believed to defend and why that belief was wrong. This record is the deliverable, not
   ceremony — it is what stops the same test being rewritten.
2. **Shrink the committed data**: replace the item8 `unit_map` arrays with digests (preserving
   every live assertion), and remove the three zero-reader fixture sets.
3. **Decide `baseline_outputs/`** — either restore a regenerating comparison that makes it real,
   or delete it with its reader. It cannot stay as 13,923 lines asserting a file parses.
4. **Collapse the D5 fixture forks** to generated variants, keeping the committed
   `instance_graph_snapshot.json` beside each — those cannot be regenerated without a license
   and are what keep repointed tests license-free. Only the `.sysml` half is derivable.
5. **Retire process tests whose items are closed**, per Item 6's grading.
6. **Fix the overstating docstrings** on tests that stay.

**Deletion lock** (product-lens `epic_plan-F2`): a test named as Authority or Evidence by any
`.project/product/` entry is never deleted, thinned, or weakened without an owner ruling
recorded in the citing entry. Item 6's inventory flags these; this item honours the flag.

**Entanglement is not deadness** `[OWNER, 2026-08-21]`. Four product tests fail on a clean checkout
because they raise on a missing release-evidence manifest, not because they defend nothing. They are
disentangled, never deleted, and `tests/conformance/test_stop_parser_documentation_contract.py` is
mixed — it also carries the only mechanical guard on the owner-verbatim `0003`/`0004` quotes.

**Out of Scope**:
- Writing new tests for the gaps (filed by Item 6 to the backlog)
- Deleting `src/` code or the test families pinning it (Item 8)
- Changing the license-gating or marker design

**Success Criteria**:
- [ ] Every deleted test's commit message names the defense it was believed to provide and the
      evidence that it did not
- [ ] `tests/` committed data is reduced by at least 60,000 lines
- [ ] Zero fixture files with no reader remain, verified by sweep
- [ ] `baseline_outputs/` is either genuinely regenerating or gone
- [ ] No remaining test docstring claims a check the test does not perform, for every test the
      audit graded weak
- [ ] Test *function* count drops by less than the line count does — this item removes data and
      false defenders, not coverage
- [ ] Full suite green with the license loaded, and the licensed pass/fail counts are unchanged
      except for tests deliberately removed

**Location**: `.project/active/test-remediation/`

**Required Reading**:
- `.project/active/coverage-audit/coverage-inventory.md` — the grades that authorize deletion
- `.project/research/20260820-201945_line-count-anatomy-and-salvageability.md` §7 — line counts
  and the license caveat on D5 snapshot fixtures
- Memory: generated baselines are format-exempt — never `ruff-format` `tests/fixtures/baseline_outputs`

**Deliverables**:
- `.project/active/test-remediation/{spec,design,plan}.md`
- `.project/active/test-remediation/deletion-record.md` — each removal with its false-belief note
- Reduced `tests/` tree, suite green

---

### Item 8: Code Cleanup

**Type**: Implementation
**Effort**: 1.75 days (spec 1h, design 2h, plan 1h, execute 10h)
**Dependencies**: Item 7 (dead code and its pinning test families retire together). Item 3 if
the tracks are parallelized — the ADRs say why one-time-use code was written.

**Objective**: Delete the dead code, and give every remaining non-production surface an owner
ruling: durable, relocated, or retired with its item.

**Current State**:
- ✅ `src/` is well-factored — 2.0% duplication, median function 15 lines, one live
      implementation per concept (verified: resolution, entry-point classification, occurrence
      walking)
- ⚠️ ~2,370 code lines (15%) are unreachable, held up by test families that outlived their
      subject — this is why a symbol-level scan reports 98 lines and a lane-level review 2,370
- ❌ `scripts/archive/` is 8,274 lines that import modules the cutover deleted and cannot execute
- ❌ 3,633 of 8,609 lines of `docs/architecture/reference/` describe deleted code
- ⚠️ `verification/` is 3,858 lines added whole by PR #13, plus ~4,900 lines of tests for it
- ➡️ `CLAUDE.md:65` and the `contracts/serialize.py` `allow_nan` omission left this epic entirely
      — filed as `[SERIALIZE-NAN-SEAL]` and `[V11-DEAD-GATE-DOCS]` `[OWNER, 2026-08-20]`

**Scope**:
0. **Honour the deletion lock.** Same rule as Item 7: no ledger-cited test is retired without
   an owner ruling recorded in the citing entry, even when it pins dead code
   (product-lens `epic_plan-F2`).
1. **Delete the dead lanes, each with its pinning tests in the same commit** — the V11 preflight
   code (85 lines; the doc corrections are `[V11-DEAD-GATE-DOCS]`, filed separately); deriver-era
   generators (123); `ConcreteConstraint`
   (105); dead extractor and model classes (126); the dead `compile_predicate` / `load_predicate`
   pair (54); error-subclass boilerplate (~50); assorted mechanical duplicates (~390).
2. **Rule on the legacy extraction lane** (941 lines, `hierarchy_resolver.py` +
   `usage_extractor.py`). Unreachable from the CLI, but its tie-break semantics differ from the
   survivor's — `most_specific` warns where `_most_specific_definition` raises. Needs a ruling
   before deletion, not just a grep.
3. **Delete `scripts/archive/`** (8,274 lines) and the twelve retired reference docs (3,633).
4. **Disposition `verification/`** — durable release tooling with its own package and lifecycle,
   or scaffolding that retires with `stop-reinventing-the-parser`. This is an owner ruling, and
   it governs ~8,700 lines including its tests. Whichever way it goes, **`verification/` must stop
   being a hard dependency of product tests**: nine test files import it today and four of those are
   product tests (`epic_plan` note, `[OWNER, 2026-08-21]`). A ruling that keeps `verification/`
   still owes that seam.
5. **Hold the snapshot codec as its own decision.** `snapshot/instance_graph.py` could shed ~550
   lines, but it costs an `instance-graph/v4` schema bump and 22 licensed fixture re-captures.
   File it to the backlog rather than doing it here.

**Out of Scope**:
- The snapshot codec consolidation (filed to backlog)
- Refactoring live `src/` code — the preflight and contract layers were checked and earn their
  keep, and the tiers are not to be collapsed
- Any behavior change to the product

**Success Criteria**:
- [ ] Every deleted symbol is unreachable from `run_codegen` on both the live and from-snapshot
      paths, demonstrated rather than asserted
- [ ] No commit deletes production code without deleting the tests that pinned it
- [ ] `scripts/archive/` and the twelve retired reference docs are gone
- [ ] `verification/` has a recorded owner ruling and the tree reflects it
- [ ] The legacy extraction lane has a recorded semantics ruling before any deletion
- [ ] Generated output is byte-identical to pre-item for every fixture, proving no behavior
      change — run with the license loaded
- [ ] Full suite green; `vulture` and the lane-level sweep both report a materially smaller
      dead surface than the 2,370-line baseline

**Location**: `.project/active/code-cleanup/`

**Required Reading**:
- `.project/research/20260820-201945_line-count-anatomy-and-salvageability.md` §5 and §6 — the
  verified dead-code inventory with `file:line` references, and the dismissed candidates
  (`source_manifest.py:540/:556` and the `KeyError` idiom are NOT defects)
- `.project/active/coverage-audit/coverage-inventory.md` — which test families are safe to retire
- `CLAUDE.md` "Retired" section — what the cutover already removed, so this does not re-tread it
- Memory: byte-identity `captured_at` churn — how to run the byte-identity gate so a full
  re-capture's timestamp rewrite does not mask the real diff

**Deliverables**:
- `.project/active/code-cleanup/{spec,design,plan}.md`
- `.project/active/code-cleanup/reachability-evidence.md` — the demonstration per deleted lane
- `.project/active/code-cleanup/dispositions.md` — `verification/`, the legacy lane, the codec
- Reduced `src/`, `scripts/`, `docs/` trees; byte-identical generated output

---

---

## Source Documents

- `.project/research/20260820-201945_line-count-anatomy-and-salvageability.md` (research) —
  the measurement this epic rests on: bucketed line counts for PR #13 and ELABORATE-FIRST,
  repo composition over time, `src/` dead-code inventory with verified file:line references,
  test-suite composition, `.project` category table and per-item process-cost ratios
- `.project/product/INDEX.md` + `0001`…`0004` (product ledger) — the four promises already
  recorded, including two `[OWNER-VERBATIM]` entries that must survive any purge
- `CLAUDE.md` (project instructions) — the retirement record, the ADR convention, and the
  five-preflight claim this epic corrects
- `agentic-project-init/project-pack/` (scaffolding source) — `adr/README.md`,
  `product/README.md`, `scripts/adr.sh`, `scripts/product.sh`, `EPIC_GUIDE.md`,
  `epic_template.md`
- `agentic-project-init` commit `1456213` (product-intent-ledger) — the PRODUCT-intent update
  that motivates the reinstall
- `.project/CURRENT_WORK.md` — live work state; `elaborator-downstream` is the only open item

---

## Product-Lens

Run at epic_plan over the decomposition, 2026-08-20. Gate: **DISPOSED** — no BLOCK. All six
findings are closed in the decomposition rather than deferred to execution, per the lens's own
note that F1 and F2 become BLOCK-shaped if Item 5 or Item 7 proceeds without them.

```
## epic_plan — 2026-08-20 — rev da15f14 (.project/backlog/epic_repo_cleanup.md)
Point (re-derived): The product is three steps — parse the models with a SysML v2 parser, walk the AST to reconstruct the math, write it into TEAx Python — and any manual fallback or workaround for an unresolved reference is a massive, disgusting smell; ill-formed models are refused with a diagnostic, never accommodated.   [source: .project/product/0004-product-identity-parse-walk-emit.md (owner quote, 2026-08-16) and 0003-no-workarounds-for-bad-models.md (owner quote, 2026-08-16), grade: owner/HARD]
Secondary point: one modeled source occurrence becomes exactly one runtime source, or elaboration refuses by name; its named durable authority is a specific set of conformance tests.   [source: .project/product/0002-exact-owner-anchoring.md, grade: agent/ratified]
Falsifier: after the epic runs, delete or weaken any artifact named as Authority/Evidence by 0001–0004 (a cited conformance test, a cited archive path) without an owner ruling, or leave the parse/walk/emit steps with no test that would fail if a workaround or a wrong-owner binding returned — observable as a green suite over a reintroduced fallback, or as a P-00N entry whose citations no longer resolve.
Findings:
- epic_plan-F1 [DO] No item protects the product ledger's own citations from the purge: the "zero broken citations" success criterion scopes only `src/`, `tests/`, `docs/`, while 0001 cites `.project/concepts/*`, `.project/completed/20260814_*`, and `.project/backlog/BACKLOG.md:439` (already drifted — `[ACAUSAL-RELATIONS-CAPABILITY]` is now at `:552`), and 0002 cites `.project/completed/20260816_qualified-reference-occurrence-anchoring/spike/.../findings.md` and that item's `verification/` ledgers. Item 5 deletes and re-homes exactly that material. — .project/product/INDEX.md ("if a promise is not reachable from here, it has no home") + 0001/0002 Authority blocks (owner/HARD core in 0001; agent/ratified in 0002) — disposition: add a success criterion and an Item 5 step — every path cited by `.project/product/*` and by any new `.project/adr/` entry resolves after the purge, and line-number citations are re-anchored or converted to anchor text. Not owner-cleared; needs owner sign-off if any cited path is to be deleted rather than re-pointed.
- epic_plan-F2 [DO] Items 6 and 7 have no promise-indexed obligation: the coverage inventory maps "meaningful functions, invariants, and end-to-end flows" but is never required to map 0001–0004 to the tests that defend them, and no deletion gate checks a candidate test against the ledger. 0002 names `tests/conformance/test_usage_owned_reference_anchoring.py` and `test_elaboration_public_mutation.py`; 0003 names `test_definition_owned_reference_positions.py` and `test_occurrence_domain_derivation.py` as "the complete current proof". Item 8 additionally deletes "the test families pinning" dead src. — 0002 Evidence, 0003 "First application" (agent/ratified and owner/HARD respectively) — disposition: make the Item 6 inventory promise-indexed, and add a hard rule to Items 7/8 that a ledger-cited test is never deleted or thinned without an owner ruling recorded in the entry.
- epic_plan-F3 [DON'T] Item 6's stated first phase — a mutation-testing spike "for an objective kill-rate signal" — systematically undercounts exactly the tests that defend the parse step. 544 of 1,700 test functions (32%) are license-gated and `pyproject.toml:46` excludes the `execution` lane, so a default run touches about two-thirds of the suite; a kill-rate measured on that run scores the live-parser and execution tests near zero and hands Item 7 a defensible-looking case to delete them. — 0004 step 1 ("use a SysML v2 parser to interpret the models"), owner/HARD; measurement from .project/research/20260820-201945_line-count-anatomy-and-salvageability.md:349 — disposition: bind Item 6 to run mutation analysis with `SYSIDE_LICENSE_KEY` loaded and the execution lane enabled, and to report gated-lane kill-rate separately; record that a low kill-rate is evidence for investigation, never sufficient authority to delete.
- epic_plan-F4 [DO] The epic requires Item 6 to name gaps but nothing obliges a gap to get an owner or a backlog id. The measured state already shows the emit step effectively unguarded — `tests/fixtures/baseline_outputs/` (13,923 lines) has one reader whose four assertions pass on hand-written stubs, and `tests/conformance/test_zero_entry_package_golden.py:11` says outright that none of them proves the bytes are the right bytes. As written, the epic can close with that corpus deleted, the gap named in a report, and no owned item. — 0004 step 3 ("write the math into python using TEAx"), owner/HARD — disposition: add a success criterion that every gap named by Item 6 exits as either a closed gap or a filed backlog item with an id, cited from the coverage inventory.
- epic_plan-F5 [DO] The owner's sequential order runs the purge (Item 5) before the test and code tracks (6–8), but Item 2's harvest is scoped to "decisions and promises" only. Items 7 and 8 must answer "what was this test believed to defend, and why was that belief wrong" and "why was this dead code left standing" — and that rationale lives in the `.project/active/` and `completed/` material Item 5 removes first. The archive is destroyed one item before it is needed. — Epic CSF, "Every settled decision that a future agent would otherwise re-derive wrongly survives … *before* anything is deleted" (agent-authored epic text, grade AGENT) reinforced by owner-verbatim sequence ("ONCE that is done, then we can go through and DELETE") — disposition: extend Item 2's harvest to capture test-and-code rationale (what each vestigial family was built to defend, and the retirement records behind the dead src), or gate Item 5's deletion of `active/`+`completed/` behind Items 7 and 8. Owner order is preserved either way.
- epic_plan-F6 [DON'T] A live correctness defect in the sealing layer is scheduled last: `canonical_json` at `src/sysml_codegen/contracts/serialize.py:28` omits `allow_nan=False`, so a NaN or Infinity serializes as bare `NaN` into the fingerprint payload and a contract seals over invalid JSON with a confident digest. It sits as the final sub-bullet of the largest item, behind ~5 days of deletion work. A seal that certifies a non-number is the "confident wrong number" failure mode 0002 exists to prevent. — 0002 ("a confident wrong number is the failure mode 0001 cannot tolerate"), agent/ratified — disposition: lift the `allow_nan=False` fix and the `CLAUDE.md:65` correction out of Item 8 into Item 1, where they cost minutes and cannot be stranded by an epic that stalls.
Smells fired: none of the seven, as scoped.
Gate: DISPOSED (epic_plan-F1, epic_plan-F2, epic_plan-F3, epic_plan-F4, epic_plan-F5, epic_plan-F6)
```

**Dispositions applied in this decomposition:**

| Finding | Where it landed |
|---|---|
| F1 | Item 5 scope step 6 + two new success criteria — ledger citations resolved before deletion; `BACKLOG.md:439` drift verified as live (target now `:552`) |
| F2 | Item 6 Phase 2 is promise-indexed; **deletion lock** added to Items 7 and 8 |
| F3 | Item 6 Phase 1 binds the spike to a licensed run with the execution lane enabled; low kill rate is explicitly never deletion authority |
| F4 | Item 6 success criterion — every gap exits closed or as a filed backlog item with an id |
| F5 | Item 2 scope step 5 — test-and-code rationale harvested before Item 5 destroys its sources; owner's sequential order preserved |
| F6 | `allow_nan=False` and the V11 doc corrections left the epic entirely — filed as standalone `[SERIALIZE-NAN-SEAL]` and `[V11-DEAD-GATE-DOCS]` at the top of `BACKLOG.md` `[OWNER, 2026-08-20]`, since neither belongs to a scaffolding or cleanup item |

---

## Dependencies

**External**:
- `agentic-project-init` checkout at `/home/reid/agentic-project-init` — the scaffolding source
  for Item 1. Its `project-pack/` and `scripts/test_{adr,product}.sh` must be current.
- `SYSIDE_LICENSE_KEY` from `/home/reid/1cfe/agentic-mbse/.env` — required for Item 6's spike
  (per F3), for Item 8's byte-identity gate, and for any full-suite green claim. Without it the
  gated tests skip rather than fail, so a green run with no key is not a full run.
- A mutation-testing tool that runs against this codebase — unvalidated; Item 6 Phase 1 is the
  spike that finds out, with a recorded fallback.

**Internal**:
- `elaborator-downstream` is the only live item in `.project/active/` and must survive Item 5's
  archive sweep untouched.
- The `[DIAGNOSTIC-PROVENANCE-BY-CONSTRUCTION]` follow-up and the four exact-evidence follow-ups
  filed by `stop-reinventing-the-parser` remain open in `BACKLOG.md` and are not in scope here.

**Item Dependency Graph**:
```
Item 1 (scaffolding + register boundary + the two stranded fixes)
  └─> Item 2 (harvest: decisions, promises, AND test/code rationale)
        ├─> Item 3 (author decision records) ──┐
        └─> Item 4 (author product promises) ──┴─> Item 5 (.project purge)

Item 6 (coverage audit — report only)
  └─> Item 7 (test remediation)
        └─> Item 8 (code cleanup)

Cross-track: Item 8 must land after Item 3 if the tracks are parallelized.
Owner's stated order runs 1-5 then 6-8 sequentially; parallel is available and halves calendar.
```

---

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| The purge deletes authority a product-ledger entry rests on | High | F1 disposition: resolve every `.project/product/*` and `.project/adr/*` citation before deletion; owner ruling required to delete rather than re-point. One citation has already drifted |
| A ledger-cited conformance test is deleted as "defending nothing" | High | F2 disposition: deletion lock on ledger-cited tests in Items 7 and 8; Item 6's inventory flags them |
| Mutation kill-rate measured on the default lane condemns the license-gated parser tests | High | F3 disposition: spike runs licensed with the execution lane on; gated-lane rate reported separately; low rate is never deletion authority |
| Item 2's harvest misses a decision, and Item 5 deletes its only record | High | The owner's three named seeds are the harvest's acceptance test; if the sweep does not surface them independently it is not thorough enough. Git history remains the backstop |
| Item 5 runs before Items 7-8 need the archive | Medium | F5 disposition: Item 2 captures test-and-code rationale into a register that survives the purge |
| Dead-code deletion changes generated bytes | Medium | Item 8 gates on byte-identical output for every fixture, licensed. Memory: a full re-capture rewrites every `captured_at`, so run the timestamp-only diff check first |
| The legacy extraction lane's tie-break semantics turn out to matter | Medium | Item 8 requires a recorded semantics ruling before deletion — `most_specific` warns where `_most_specific_definition` raises |
| Epic stalls partway, leaving the repo half-migrated with two ADR homes | Medium | Item 1 is self-contained and leaves a coherent state: both registers installed, criterion filed, conventions corrected, two bugs fixed |
| `verification/` disposition is deferred indefinitely | Low | Item 8 requires a recorded ruling, not a decision — "durable, own package" is an acceptable outcome |

---

## Timeline

**Total Effort**: ~11 days sequential; ~6-7 days if the two tracks run in parallel.

| Item | Effort | Dependencies |
|------|--------|--------------|
| 1. Scaffolding reinstall and register boundary | 1 day | None |
| 2. Decision harvest inventory | 1.5 days | Item 1 |
| 3. Author the decision records | 1.5 days | Item 2 |
| 4. Author the product promises | 0.75 day | Item 2 (parallel to 3) |
| 5. `.project` purge | 1 day | Items 3, 4 |
| 6. Coverage audit | 2 days | None (owner order: after 5) |
| 7. Test remediation | 1.5 days | Item 6 |
| 8. Code cleanup | 1.75 days | Item 7 (and Item 3 if parallelized) |

---

## Lessons Learned (Post-Completion)

*Fill in after epic is complete*

**What Went Well**:
- TBD

**What Could Improve**:
- TBD

**Surprises**:
- TBD

---

**Last Updated**: 2026-08-20
**Next Action**: Start Item 1 — `/_my_spec` in `.project/active/scaffolding-register-boundary/`
