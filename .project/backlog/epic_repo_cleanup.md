# Epic: Repo Cleanup — Keep the Decisions, Delete the Exhaust

**Epic ID**: REPO-CLEANUP
**Status**: In Progress
**Priority**: P1
**Created**: 2026-08-20
**Revised**: 2026-08-23 — collapsed from eight pipeline items to three moves (see *Revision*)
**Estimated Effort**: ~3 days remaining

---

## Executive Summary

The repository is 880k lines, of which the product is 15k. `.project/` is 78% of the tree.
This epic writes the handful of durable decisions and promises into the two registers
(`.project/adr/`, `.project/product/`), deletes the archive from HEAD, then deletes the dead
code and the tests and fixtures that defend nothing.

**Critical Success Factor**: After this epic a cold agent learns what was settled, and why, from
the registers and `research/` in an afternoon. Nothing else about `.project/` size matters.

**Backstop**: git history. Nothing deleted from HEAD is lost; the purge commit records the
pre-purge SHA. This is why the work runs as commits, not as documents about commits.

---

## Revision (2026-08-23)

`[OWNER, 2026-08-23]` The eight-item shape was about 80% process ceremony and 20% analysis.
Per-item spec / design / plan / audit / close is cut. Each remaining move runs as one checklist,
commits, and a green licensed suite.

`[AGENT] (ratified by owner, 2026-08-23)` The three-move decomposition below, and the three
fixes to the harvest it records (concepts preserved, citations fixed by sed, rationale register
dropped).

Out of scope: the eleven named deliverable documents of the original decomposition
(`candidate-register.md`, `citation-triage.md`, `test-code-rationale.md`,
`citation-resolution.md`, `deletion-manifest.md`, `post-purge-citation-check.md`,
`spike-mutation-testing.md`, `coverage-inventory.md`, `gaps.md`, `reachability-evidence.md`,
`dispositions.md`) are not required, because each re-narrates either a commit message or a
section of the research document that already exists. The mutation-testing spike is not
required because the research document already names the false defenders by `file:line` and a
kill rate was never going to be deletion authority (product-lens F3).

---

## Why This Epic?

Measured 2026-08-20 in `.project/research/20260820-201945_line-count-anatomy-and-salvageability.md`:

- `.project/` is 675,740 lines / 1,781 files. Exactly one file (`ledger/ledger-4a.json`) is
  read by any tool. 109,720 lines are byte-exact duplicates; `ruff_all.log` is committed ten
  times. 40 of 48 `active/` directories are closed items never archived.
- `tests/` is 148,391 lines, 30,824 of them Python. ~73,400 lines are committed data with no
  reader or a reader that asserts `isinstance(..., list)`.
- `src/` carries ~2,370 dead lines (15%): the elaborate-first cutover deleted the consumers and
  left the producers standing, pinned by tests that outlived their subject.
- Citation contract is already broken: 27 of 72 distinct `.project` paths cited from `src/`,
  `tests/`, and `docs/` do not resolve (re-measured 2026-08-23).

---

## Owner Rulings (settled)

- `[OWNER, 2026-08-20]` **Split the registers by who the decision binds.** Model-author
  decisions stay in `docs/architecture/modeling-assumptions.md` as `ADR-0NN`; toolchain-builder
  decisions go in `.project/adr/`. Filed as `.project/adr/0001-route-decisions-by-who-they-bind.md`.
- `[OWNER, 2026-08-21]` **Entanglement is not deadness.** Four product tests fail on a clean
  checkout because they raise on a missing release-evidence manifest
  (`test_hierarchy_resolver.py`, `test_ast_dispatch_invariant.py`,
  `test_self_binding_guidance_contract.py`, `test_exact_route_fingerprint_stability.py`). They
  are disentangled, never deleted. The raise→skip flip is `[ARTIFACT-MANIFEST-TESTS-HARD-FAIL]`.
- `[OWNER, 2026-08-20]` `allow_nan=False` and the V11 doc corrections left the epic as
  `[SERIALIZE-NAN-SEAL]` and `[V11-DEAD-GATE-DOCS]` in `BACKLOG.md`.
- `[OWNER, 2026-08-23]` Process ceremony is cut (see *Revision*).

## Standing rules (from the product-lens, 2026-08-20, gate DISPOSED)

These survive the revision because they are the only real safety checks in the epic.

- **Deletion lock** (F2). A test named as Authority or Evidence by any `.project/product/*`
  entry is never deleted, thinned, or weakened without an owner ruling recorded in the citing
  entry. `0002` names `test_usage_owned_reference_anchoring.py` and
  `test_elaboration_public_mutation.py`; `0003` names
  `test_definition_owned_reference_positions.py` and `test_occurrence_domain_derivation.py`.
- **Register citations resolve after the purge** (F1). Every path cited by `.project/product/*`
  and `.project/adr/*` resolves after Move B, with line-number citations converted to anchor
  text. `0001`'s `BACKLOG.md:439` has already drifted. Deleting a cited path instead of
  re-pointing it needs an owner ruling recorded in the citing entry.
- **Gaps get an id** (F4). Any coverage gap Move C names exits as a `BACKLOG.md` item with an
  id, not a line in a report. The emit step is the live case: `tests/fixtures/baseline_outputs/`
  (13,923 lines) has a reader whose assertions pass on hand-written stubs.
- **Byte identity** with the license loaded gates every `src/` deletion.

---

## Done

### Item 1: Scaffolding and register boundary ✅

Certified 2026-08-21 at `3566fdd`; archived to
`.project/completed/20260821_scaffolding-register-boundary/`. Both registers installed and
script-managed; `.project/adr/0001`–`0003` filed; product `0001`–`0004` checked at `02733b4`;
nine existing ADRs triaged, with ADR-007 and ADR-009 recorded as builder-facing and carried to
Move A (`adr-triage.md` in the archive).

### Item 2: Decision harvest ✅ (closed by this revision)

The harvest is `.project/active/decision-harvest/execution-history.md`: 126 `completed/`
folders summarised one record each (`spine/*.json`, joined by `join.py`), with a `Bin` column
and a *Binning* section dated 2026-08-23. 21 of 126 rows marked: 7 ADR rows collapsing to ~5
entries, 3 product rows collapsing to ~2, 11 keep-as-notes. All three owner seeds ("use the
parser"; exact identity / occurrence enumeration; refuse rather than work around) surfaced
from the sweep independently. Do not rerun `join.py` without re-applying the markup.

Three findings on review (2026-08-23), each resolved in place rather than by more harvest:

1. **`.project/concepts/` was not swept and is preserved instead.** 55 docs / 18k lines of
   owner-voice shaping text, cited by product `0001`, `modeling-assumptions.md`,
   `verification-matrix.md`, and two conformance tests. Cheaper to keep than to harvest. It
   joins the Move B preserve list. `[AGENT] (ratified by owner, 2026-08-23)`
2. **Broken citations are a sed job, not a triage.** 25 of the 27 missing paths are
   `.project/active/<item>/…` whose folder moved to `.project/completed/YYYYMMDD_<item>/`
   (one-to-one, verified). The other two: `solar-battery-sysml-model` (no archive copy
   anywhere) and `.project/research/whatever.md` (a placeholder). Fixed in Move B.
3. **The test-and-code rationale register is not needed.** The research document `§5`–`§7`
   already carries the dead-code inventory and false-defender list by `file:line`, and the
   "why was it left standing" answer is one sentence: the cutover deleted consumers and left
   producers, pinned by tests. Move C cites the research document directly.

Residual risk, owned by the owner: the summaries are two compression hops from the source
(subagent summaries, then binning over summaries). Mitigation is a ten-minute skim of the 105
unmarked titles in the timeline before Move B; git history backs everything else.

---

## Moves

No spec, design, plan, or audit documents. Each move: one checklist in
`.project/active/<move>/plan.md`, commits, licensed suite green, then archive the folder.

### Move A: Write the entries (Items 3 + 4)

**Effort**: 0.5 day. **Dependencies**: none (harvest is done).

**Objective**: File every marked row from the harvest into the register `.project/adr/0001`
assigns, each with a `Why` a future challenge re-derives against rather than relitigates.

**Steps**:
1. `adr.sh new` for each ADR candidate: H-124 (use the parser: exact SysIDE declaration
   evidence or refuse by name, never proximity/arrival-order/substring guessing);
   H-108/110/111 as one entry (elaborate-first: exact identity over string matching, legacy
   stack deleted with no compat shims, v5 snapshots refused by name); H-090 (no late-fill or
   post-build graph mutation; direct literal actuals are valid; the embedded catalog is TEAx's
   sole schema authority); H-078 (agentic-mbse owns neutral SysML facts, codegen owns Python
   rendering, dependency one-way — check `CLAUDE.md` Dependencies first; this may be a short
   entry whose value is the Why); H-125 (cross-repo merges are explicit merge commits because
   fusion-tea pins SHAs).
2. Re-home ADR-007 and ADR-009 `[OWNER, 2026-08-21]`: file each as a `.project/adr/` entry,
   reduce `modeling-assumptions.md` §§7 and 9 to pointers, repoint citations, and update
   `0001`'s ADR-009 Authority citation.
3. `product.sh new` for H-112/113 (coverage truth: every authored constraint usage gets exactly
   one recorded disposition; a package never reports full satisfaction over unassessed gates).
   H-089 (sealed packages) only if not already inside `0002`; check first.
4. `product.sh check` the new entries. `0001`–`0004` bodies stay unchanged.
5. The 11 "keep" rows get cited from the entry bodies where relevant (H-107 is the Why behind
   elaborate-first; H-016, H-104, H-116 are gotchas worth a line). No separate artifact.

**Rules**: Provenance graded honestly — `[OWNER]` only where the owner originated it;
`[AGENT] (ratified …)` otherwise, never settled. Rejected alternatives recorded as "Out of
scope: X, because Y", never "we must not X". Every entry carries its substance; no entry
cites a path Move B deletes.

**Done when**: every marked row has an entry or a recorded reason it doesn't; `adr.sh index`
and `product.sh index` regenerate cleanly; every citation in every new entry resolves.

### Move B: Purge `.project` (Item 5)

**Effort**: 0.5 day. **Dependencies**: Move A.

**Objective**: `.project/` becomes the two registers, `research/`, `concepts/`, the ledger, the
backlog, scripts, and live work. Everything else leaves HEAD.

**Steps**:
1. `.gitignore` the log family repo-wide: `.project/**/*.log`, `*.console`, `*.err`,
   `*full-suite.txt`.
2. Delete `.project/completed/` from HEAD (551,573 lines). Record the pre-purge SHA in the
   commit message; that is the deletion manifest. Ruled: wholesale `[OWNER, 2026-08-23]`.
3. Delete the 40+ closed `active/` directories (100,330 lines; `decision-harvest` archives with
   its `execution-history.md` and `spine/` as the one record of the archive that stays reachable
   — move it to `research/`). Keep `elaborator-downstream` and anything the owner names live.
4. Delete `reports/`, `diagrams/`, `specs/`, `logs/` unless a register entry cites them; check
   with grep before, not after.
5. Fix the 27 citations: sed `active/<item>` → `completed/…` targets that now live only in git
   become citations to the commit, or are dropped where the citing text no longer needs them;
   `solar-battery-sysml-model` and `whatever.md` are dropped by hand.
6. Resolve every path cited by `.project/product/*` and `.project/adr/*` (F1); convert
   line-number citations to anchor text.
7. Record archive-on-close as the standing rule in `.project/README.md` so `active/` stops
   accumulating a second copy of the process.

**Preserve**: `adr/`, `product/`, `research/`, `concepts/`, `ledger/` (three scripts read
`ledger-4a.json`), `backlog/`, `memories/`, `reference/`, `scripts/`, `CURRENT_WORK.md`,
`README.md`, `EPIC_GUIDE.md`, `epic_template.md`.

**Done when**: `.project/` under 100k lines; zero committed logs and `.gitignore` prevents
their return; zero byte-exact duplicates over 2KB (hash sweep); every `.project` citation from
`src/`, `tests/`, `docs/`, and both registers resolves; `ledger-4a.json` still loads; licensed
suite green.

### Move C: Delete what defends nothing (Items 6 + 7 + 8)

**Effort**: 1–1.5 days. **Dependencies**: Move A (the ADRs say why the dead code was written).

**Objective**: Remove the dead `src/` lanes with their pinning tests, the fixtures with no
reader, and the tests whose assertions check nothing, in commits that each say what was
believed to be defended and why that belief was wrong.

**Inventory**: the research document `§5` (dead `src/` by `file:line`), `§6` (deletable weight
outside `src/`), `§7` (test composition, false defenders, gating). That document is the
coverage inventory; no second one is written.

**Steps**:
1. Dead `src/` lanes, each with its pinning tests in the same commit: V11 preflight code (85),
   deriver-era generators (123), `ConcreteConstraint` (105), dead extractor/model classes
   (126), `compile_predicate`/`load_predicate` (54), error-subclass boilerplate (~50),
   mechanical duplicates (~390). Unreachability from `run_codegen` on both paths is
   demonstrated in the commit message (grep of importers + `vulture`), not asserted.
2. The legacy extraction lane (941 lines, `hierarchy_resolver.py` + `usage_extractor.py`),
   with its pinning tests; the commit notes the warn-vs-raise difference. Ruled: delete
   `[OWNER, 2026-08-23]`.
3. Committed test data: replace the item8 `unit_map` arrays (~47,000 lines) with digests,
   preserving every live assertion; delete the zero-reader sets
   (`golden/calc_def_compilation_golden.json`, `baseline_yaml/`, and whatever the reader sweep
   finds); collapse the `catf_mfe_d5` fork (5,718 lines, four-line diff) to the generator,
   keeping each `instance_graph_snapshot.json` because those need a license to regenerate.
4. `baseline_outputs/` (13,923 lines): restore a real regenerating comparison or delete it with
   its reader. Either way the emit-step gap gets a `BACKLOG.md` id (F4).
5. `scripts/archive/` (8,274 lines; imports deleted modules) and the twelve retired reference
   docs (3,633 lines) are deleted. Document 09's mixed content gets its retired half cut.
6. `verification/` (~8,700 lines with tests) is deleted — ruled retire `[OWNER, 2026-08-23]`.
   The nine test files that import it are cut loose from it; four are product tests.
7. Fix overstating docstrings on tests that stay, as they are passed.
8. Process tests for items that closed months ago: delete, naming the item in the commit.
9. Filed, not done: the snapshot codec consolidation (~550 lines; costs a schema bump and 22
   licensed re-captures); any coverage gap worth a new test.

**Safety**: the deletion lock (F2) on ledger-cited tests; entanglement-is-not-deadness on the
four manifest-gated product tests; byte-identical generated output for every fixture with the
license loaded (run the timestamp-only diff check first — a full re-capture rewrites every
`captured_at`); licensed pass/fail counts unchanged except for tests deliberately removed.

**Done when**: `vulture` and the lane sweep report a materially smaller dead surface than
2,370 lines; `tests/` committed data down by at least 60,000 lines with the test *function*
count dropping far less than the line count; zero fixture files with no reader; byte identity
holds; licensed suite green.

---

## Owner rulings on the three open dispositions (2026-08-23)

All three ruled `[OWNER, 2026-08-23]`:

1. **`completed/` leaves HEAD wholesale** (Move B step 2). No trimming pass. The registers,
   `research/`, `concepts/`, and the harvest's `execution-history.md` carry the knowledge; git
   carries the bytes at the pre-purge SHA recorded in the commit. Clone size does not shrink and
   no history is rewritten — fusion-tea's SHA pins stay valid.
2. **`verification/` retires** with this epic (~8,700 lines with its tests). Built for the PR #13
   shipment; the sealed evidence it produced is published (`stop-parser/*-final` tags) and
   deleting the tool unseals nothing. Recoverable at the purge SHA if a shipment of that shape
   recurs. The nine importing test files are cut loose from it either way.
3. **The legacy extraction lane is deleted** (941 lines, `hierarchy_resolver.py` +
   `usage_extractor.py`, with its pinning tests). The warn-vs-raise tie-break difference is the
   old leniency the elaborate-first cutover removed, not a lost capability; the deletion commit
   notes the semantic difference explicitly.

---

## Dependencies

**External**:
- `SYSIDE_LICENSE_KEY` from `/home/reid/1cfe/agentic-mbse/.env` — required for every
  full-suite green claim and for Move C's byte-identity gate. Without it gated tests skip, so a
  green run with no key is not a full run.

**Internal**:
- `elaborator-downstream` is live in `.project/active/` and survives Move B untouched.
- `[DIAGNOSTIC-PROVENANCE-BY-CONSTRUCTION]`, the four exact-evidence follow-ups, and
  `[ARTIFACT-MANIFEST-TESTS-HARD-FAIL]` remain open in `BACKLOG.md` and are not in scope.

**Order**: A → B → C. B and C could run in parallel; not worth the coordination for ~2 days.

---

## Risks

| Risk | Mitigation |
|---|---|
| The purge deletes authority a register entry rests on | F1: resolve every register citation after Move B; deleting a cited path needs an owner ruling in the citing entry |
| A ledger-cited test is deleted as "defending nothing" | F2 deletion lock; the four cited tests are named above |
| The harvest missed a decision and Move B deletes its only HEAD copy | Owner skims the 105 unmarked titles before Move B; git history keeps the bytes; a missed decision is re-harvested from `git show`, not lost |
| Dead-code deletion changes generated bytes | Byte-identity gate, licensed, with the `captured_at` churn handled first |
| The legacy lane's tie-break turns out to matter | Ruled delete `[OWNER, 2026-08-23]`; the deletion commit records the semantic difference |

---

## Source Documents

- `.project/research/20260820-201945_line-count-anatomy-and-salvageability.md` — the
  measurement; `§5`–`§8` are the inventories Moves B and C act on
- `.project/active/decision-harvest/execution-history.md` — the harvest and its binning
- `.project/completed/20260821_scaffolding-register-boundary/adr-triage.md` — ADR-007/009 outcomes
- `.project/adr/README.md`, `.project/product/README.md` — density bars and entry formats
- `claude-pack/rules/capture-fidelity.md` — provenance grades; law 3 for rejected alternatives
- `CLAUDE.md` "Retired" section — what the cutover already removed

---

## Lessons Learned (Post-Completion)

*Fill in after epic is complete.*

- 2026-08-23: the original decomposition priced eight items at 8–11 days, most of it writing
  documents about commits. The revision prices the same outcome at ~3 days.
