# Product-Lens Ledger — dead-worktree-pins

Append-only. One block per run (`product-lens.md` spec §3). A `BLOCK` stays in force until a later
block cites its id and records an authorized disposition.

---

## spec — 2026-08-15 — rev 9ce5548 (work: `.project/active/dead-worktree-pins/spec.md`)
Epic: none (phase-D cleanup residue) — **attribution correct.** Both broken gates belong to
completed, archived work (ledger-4a is cutover-recovery Gate 4A; the execution lane is fusion-tea
acceptance), CONSTRAINT-SEMANTICS closed 2026-08-14, and the breakage was caused by an
owner-directed cleanup rather than by any item's scope. The nearest owner is the sibling item
`.project/active/self-binding-replacement/spec.md`, which excludes this work in its own Non-Goals
and holds the reverted patch — so the item is traceable, not orphaned. No epic row should be minted.

Point (re-derived): A gate's headline must distinguish "checked and passed" from "not checked";
a headline that cannot is not evidence, and disclosure of a gap is not the same as reporting it.
[source: `docs/architecture/modeling-assumptions.md:704-740` (ADR-009), back-registered at
`.project/product/INDEX.md:24` as the enforcement record behind P-001; grade: **agent/ratified**
(`[AGENT] (ratified by owner, 2026-08-12)`, live). The same class is stated in the ledger's own
reason for existing — *"the gate accepted absence as proof of retirement"*
(`.project/ledger/ledger-4a.md`, "What this ledger is, and what it fixes"), orchestrator-approved
2026-08-11.]
Secondary point: nothing in this item may change what the product claims — P-001's promise and its
Critical Success Factor are untouched by a pin repair (`.project/product/P-001-design-search-free-variation.md:11-33`, grade **owner-verbatim**). The spec honors this
explicitly (Non-Goals 3). No commission finding against P-001.
Falsifier: after the repair, put the checker in a state where a row is not actually verified and
watch it still print a line a reader reads as "all 304 verified" — i.e. run
`check_ledger_4a.py paths` and observe `304 rows checked, 0 problems` while
`check_removed_symbols` inspected 12 rows. For the pin: change nothing but the resolution target
and see the assertion still pass.

Findings:
- spec-F1 [DO] **The repair leaves the headline in the exact shape ADR-009 forbids.**
  `scripts/check_ledger_4a.py:809` prints `f"{len(ledger['rows'])} rows checked, …"` — 304
  unconditionally — while `check_removed_symbols` only inspects rows with `state == "executed"`
  and a `removes` block (12 of 304 at HEAD), and skips any whose path is absent (`:192-193`). The
  spec's criteria fix the *cause* of the new blind rows (correct root, nonzero exit on a missing
  configured root) and then dispose of the residue by writing a seventh documented ceiling
  (criterion 6). That is disclosure, not distinction; ADR-009's own remedy for this class was a new
  reporting **state** (`partial_coverage`), not a caveat in prose. Positive obligation the spec
  omits: the run must report what it verified separately from what it passed by absence, so the
  headline means what a reader takes it to mean and the next relocation cannot be silent.
  — `docs/architecture/modeling-assumptions.md:704-740`; `.project/ledger/ledger-4a.md`
  (**agent/ratified**) — disposition: DISPOSE — design adds a coverage split to the `paths`
  headline (verified / skipped-by-absence / not-in-scope-of-this-check). The scope note's
  "do not over-invest" does not cover this: it argues against building for absent automation, and
  this is the item's own stated defect class.
- spec-F2 [DO] **Two of the three acceptance demonstrations are point-in-time, so they cannot
  notice the next rot.** The missing-root criterion correctly demands *"a regression check"*
  (spec.md:92-95). The falsified-removal-claim criterion (`:86-91`) and the environment-pin
  criterion (`:82-85`) demand only that a failure be *demonstrated*. This item exists because a pin
  that was demonstrated working in July silently stopped checking anything in August; a
  demonstration recorded in a review has the same lifespan as the one that broke. Obligation: both
  land as kept, runnable negative checks. Both are cheap — `check_removed_symbols(rows,
  repo_roots=…)` already takes an injectable `repo_roots` (`:180-183`), so a synthetic falsified row
  is a unit test; and the pin's assertion can be a pure predicate over a resolved-path dict fed a
  wrong path, which is also the mechanism answer to the spec's one open question (`:158-159`).
  — derived from ADR-009 plus the spec's own `[NEED]` at `:130-134` (**`[INFERRED]`**) —
  disposition: DISPOSE — strengthen both criteria to "a kept check that fails on a wrong
  resolution / a falsified claim", at design or plan.
- spec-F3 [DON'T] **The severity ranking is stated without its magnitude, and the magnitude
  changes how the work should be sized.** "the quiet one is the more serious" (`:25`) and "every
  `repo: agentic-mbse` row" (`:33-41`) are true but read as large. Checked: there are exactly **2**
  such rows (L-036, L-037), and the checker's sixth documented ceiling already names that pair by
  id (`scripts/check_ledger_4a.py:66-68`). Meanwhile **292** rows never enter this check at all.
  The cleanup did not create the evidence problem — it created a 2-row instance of a headline
  problem that was already there. Naming `304 rows checked, 0 problems` as the misleading artifact
  while omitting both numbers invites an implementer to repair the 2 rows and inherit the headline,
  which is spec-F1. — `.project/ledger/ledger-4a.json`; `scripts/check_ledger_4a.py:186-193,809`
  (**checked fact**) — disposition: DISPOSE — state both counts (2 blind, 12 in scope, 304 in the
  headline) in the Problem section.
- spec-F4 [DO] **A count in the scope note is wrong, and it is the count the note leans on.**
  "it does carry 62 of its own tests" (`:168`) — the only file that tests the checker,
  `tests/unit/test_check_ledger_4a.py`, collects **54** nodes (`pytest --collect-only`, verified
  2026-08-15); no other test file references `check_ledger_4a`. The number is load-bearing for the
  "already well covered, do not over-invest" argument. — measured (**`[AGENT]`**) — disposition:
  DISPOSE — correct to 54 or drop the count.
- spec-F5 [DO] **An owner-stated criterion has a consequence the spec does not state.** A startup
  hard-fail on a missing configured root makes `paths` mode unrunnable in any checkout that lacks
  `../agentic-mbse` beside it. CLAUDE.md treats the companion checkout as an install-time
  assumption, but it is not guaranteed for a fresh clone, and today that case degrades silently
  instead of stopping. The criterion is owner-graded and right; the consequence still belongs in
  the spec so design chooses the failure text deliberately — name the repo key, the resolved path,
  and what to clone — rather than shipping a bare exit. — spec.md:92-95 + `CLAUDE.md` install
  section (**`[INFERRED]`**) — disposition: DISPOSE — record the consequence and require a
  self-explaining error.

Smells fired (must escalate into the stage's judgment, not sit green):
- **Smell 3 — a special category exempts a case whose user-visible meaning is unchanged.** Two
  absences carry the same meaning to a reader ("this row was not verified"): a missing row path and
  a missing configured checkout. The spec keeps the first silent-by-design and makes the second a
  hard failure. The distinction is real *for the checker's internal logic* (a delete row is
  supposed to be gone) and invisible in the output. This is the substance of spec-F1: the fix is
  not to make per-row absence fail, it is to make the output say which kind of pass each row got.
- **Smell 1 — two representations must be manually kept synchronized.** Criterion 6 adds a seventh
  hand-written ceiling to a docstring list that nothing verifies against behavior. The existing
  list already drifted in this exact way: ceiling 6 names the two-row agentic skip in
  `replacements` while the same root silently blinded `paths`, which no ceiling mentioned.

Judgments the call site asked for, stated plainly:
- **Is the framing honest?** Yes, and it checks out. No `.github/`, no non-sample git hooks, no
  pre-commit config — the "invoked by hand" claim is verified. The `[OWNER 2026-08-14]` living-gate
  ruling is real. The three-reference inventory is complete: `grep -rn item7-rebuild` over
  `tests/ scripts/ src/`, excluding `scripts/archive/`, returns exactly those three lines.
- **Does it under- or over-scope?** It under-scopes in one place (spec-F1/F2) and is correctly
  restrained everywhere else. It does not over-scope. Note that `test_fusion_tea_real_teax.py:109`
  pins `"/teax/packages/teax-simkit/"` by the same hardcoded-fragment technique and is deliberately
  left alone — consistent with Non-Goals, but the `[INFERRED]` anchor-derivation requirement
  (`:135-138`) applies to it too whenever someone next touches that fixture.
- **Do the criteria satisfy ADR-009, or gesture at it?** Half-and-half. The falsified-claim
  criterion is genuinely ADR-009-shaped — it is the one thing that distinguishes verified from
  skipped, and the spec says so in the right words. The nonzero-exit criterion closes the specific
  recurrence. What is missing is the reporting side: after this item lands, the headline still
  cannot tell a reader which rows were verified. The item does not have to fix all 292 rows to
  satisfy the rule; it has to stop the headline from claiming them.
- **Is the environment-pin invariant the right one?** Yes — "must still reject a wrong resolution"
  is exactly the property that a naive repair (assert the resolved path contains `sysml_codegen`)
  would destroy while going green. It is not stated strongly enough: see spec-F2.

Gate: DISPOSED (spec-F1, spec-F2, spec-F3, spec-F4, spec-F5)
No BLOCK. Every finding rests on a live-but-not-owner-originated decision (ADR-009,
`[AGENT] (ratified)`), on a measured fact, or on my own inference; none contradicts an owner
`[OWNER]`/`[HARD]` statement. The spec honors all four owner-graded rows it carries. spec-F1 and
spec-F2 are the two that should change the artifact before implementation; spec-F3 through spec-F5
are corrections.

---

## spec — 2026-08-15 — rev 9ce5548 (work: `.project/active/dead-worktree-pins/spec.md`, revision applying spec-review.md)
Point (re-derived): A gate's headline must distinguish "checked and passed" from "not checked"; a
gate that cannot fail is not evidence. [source: `docs/architecture/modeling-assumptions.md` ADR-009,
back-registered `.project/product/INDEX.md:24`; grade: **agent/ratified** (`[AGENT] (ratified by
owner, 2026-08-12)`, live). Same class stated in `.project/ledger/ledger-4a.md`, "What this ledger is,
and what it fixes" — *"the gate accepted absence as proof of retirement"*, orchestrator-approved
2026-08-11.]
Secondary point: unchanged — nothing here touches what P-001 claims
(`.project/product/P-001-design-search-free-variation.md:11-33`, **owner-verbatim**). Non-Goals 3
still honors it. No commission finding against P-001.
Falsifier: point a configured repo root at a nonexistent directory and watch `check_ledger_4a.py
paths` still print `304 rows checked, 0 problems`; or change only the resolution target of the
`environment` fixture and see the assertion still pass.

Findings:
- spec-F6 [DON'T] **The startup hard-fail's mode scope is unstated, and the two statements the spec
  does make disagree.** Criterion 6 (`spec.md:83-86`) puts the missing-root check "once at startup,
  before any row is walked" — a placement that is mode-independent — while Non-Goals
  (`spec.md:138-141`) say `replacements`, `surface` and `groups` are untouched and all six documented
  ceilings stay as written. Ceiling 6 (`scripts/check_ledger_4a.py:64-68`) is a *promise that
  `replacements` keeps running* without the companion checkout, proving 302 of 304. A literal startup
  hard-fail converts that documented partial-run into a full stop for every mode. One of the two
  statements has to give, and design should not decide it by accident.
  — `spec.md:83-86` vs `spec.md:138-141` + `scripts/check_ledger_4a.py:64-68` (**`[INFERRED]`**, over
  an owner-graded criterion whose *intent* is not in question) — disposition: DISPOSE — design states
  the scope explicitly (gate `paths` only, or gate all modes and amend ceiling 6 in the same change).
- spec-F7 [DO] **The deferred coverage split has no durable home.** Non-Goals record the deferral by
  pointing at `product-lens.md` spec-F1 (`spec.md:133-137`). That file is item-local and moves to
  `.project/completed/` when this item closes, so the residual class — the `paths` headline claims 304
  rows while `check_removed_symbols` inspects 12 — becomes reachable only by knowing which archived
  item to open. The repo's own pattern for a deferred-but-live idea is a backlog id
  (`[ACAUSAL-RELATIONS-CAPABILITY]`, `.project/backlog/BACKLOG.md:439`, cited from
  `P-001-design-search-free-variation.md:99-103`). Obligation: give the deferral a backlog id, or say
  in one line that it is deliberately allowed to lapse.
  — ADR-009 + `.project/product/P-001-design-search-free-variation.md:99-103` (**agent/ratified**,
  narrowed by owner) — disposition: DISPOSE — one backlog entry at plan or close; not a change to this
  item's scope, and explicitly not a re-raise of spec-F1's obligation.

Smells fired: **none.** Both prior smells cleared in this revision, checked rather than assumed.
- Smell 1 (two representations manually synchronized) no longer fires: the revision drops the
  criterion that added a seventh hand-written ceiling and instead freezes the list
  (`spec.md:138-141`). Note that spec-F6, if resolved the "gate all modes" way, re-opens it — ceiling
  6 would then need editing in the same change.
- Smell 3 (special category exempting a case whose user-visible meaning is unchanged) no longer
  fires: with the startup check in place, "row path absent" can only occur inside an existing
  checkout, so the two absences stop carrying the same reader-meaning. The exemption is removed at the
  source rather than documented around. The spec states this distinction directly at `:106-109`.

Gate: DISPOSED (spec-F6, spec-F7)
No BLOCK, and none carried forward. Every prior finding is resolved or authorized-deferred below; the
two new findings rest on inference and on a ratified ADR, neither contradicting an `[OWNER]`/`[HARD]`
statement. The revision is a real improvement: the two behavioral gaps (F1's reporting side excepted,
by owner ruling) are closed with kept checks rather than demonstrations.

Resolves:
- spec-F1: DEFERRED — authority: owner (`spec-review.md` Resolutions, `[L1-2] [OWNER 2026-08-15]`
  "Keep in narrow") — basis: the coverage split is now an explicit Non-Goal (`spec.md:133-137`) with
  the owner ruling cited; per §2 the owner disposition outranks the prior agent-grade DISPOSE. The
  obligation still holds product-wide on ADR-009 (**agent/ratified**), unowned — see spec-F7 for its
  missing home.
- spec-F2: FIXED — authority: agent (verified against revised text) — basis: both point-in-time
  criteria became kept checks — the pin is "kept as a negative check in the suite, not a one-off
  demonstration" (`spec.md:73-75`) and the falsified-removal-claim criterion is "a **kept** negative
  check" (`spec.md:79-82`); the third was already a regression check (`:86`).
- spec-F3: FIXED — authority: agent (measured) — basis: the Problem section now states all three
  counts in place — 304 rows checked, 12 carrying a removed-symbol claim, 2 of them agentic
  (`spec.md:31-46`) — so the 2-row instance can no longer read as a large one.
- spec-F4: FIXED — authority: agent (measured) — basis: the scope note now reads **54** tests
  (`spec.md:156`), matching `pytest --collect-only` on `tests/unit/test_check_ledger_4a.py`, the only
  file referencing the checker.
- spec-F5: FIXED — authority: agent (verified against revised text) — basis: `spec.md:159-163` states
  the consequence (`paths` unrunnable without the companion checkout beside it), calls it the intended
  trade, and requires a deliberate message that names the missing root and says the gate abstained.

---

## spec — 2026-08-15 — rev 9ce5548 (work: `.project/active/dead-worktree-pins/spec.md`, second revision — resolution note only, no new lens run)
Resolves:
- spec-F6: FIXED — authority: agent (scoping per existing owner statements, no new decision) —
  basis: the missing-root criterion now states the mode scope explicitly — the startup hard-fail
  gates `paths` only, and `replacements` keeps its documented ceiling-6 partial-run. This is the
  only reading consistent with the owner's stated consequence (which names `paths` becoming
  unrunnable) and the owner-ruled Non-Goals mode boundary; the "gate all modes" alternative would
  contradict both and re-fire smell 1 on ceiling 6.

spec-F7 remains open with its recorded disposition (one backlog entry at plan or close, or a
one-line deliberate-lapse note — owner's choice).

---

## audit — 2026-08-15 — rev 58bc6aa
Point (re-derived): Gate evidence must distinguish verified success from absence: a missing
checkout cannot prove retirement, and a pin must reject evidence from the wrong tree. [source:
`.project/ledger/ledger-4a.md`, “What this ledger is, and what it fixes”;
`docs/architecture/modeling-assumptions.md` §9, ADR-009; grade: **agent/ratified**]
Falsifier: remove a configured checkout, restore a claimed-removed companion symbol, or resolve an
imported package outside its pinned checkout; the corresponding gate still reports success.
Findings:
- None. The live work keeps all three falsifiers: missing-root `paths` abstains nonzero before
  checking rows, companion removal claims are inspected against the main checkout, and the
  acceptance fixture consumes the wrong-resolution predicate.
Smells fired: none.
Prior BLOCK scan: none unresolved; `spec-F7` is non-blocking.
Gate: CLEAR
