# Audit: Scaffolding Reinstall and Register Boundary

**Verdict:** Certify
**Audited:** 2026-08-21
**Branch:** repo-cleanup
**Commit:** 3566fdd

---

## The Point

The product is three steps: parse the models with a SysML v2 parser, walk the AST to reconstruct
the math, write it into TEAx Python. Any manual fallback for an unresolved reference is a smell;
ill-formed models are refused with a diagnostic, never accommodated. `[OWNER-VERBATIM, 2026-08-16]`,
`.project/product/0004` and `0003`.

This item does not touch that product. It serves it one hop back. Those promises are written down
so a future agent cannot quietly undo them, and the ledger's contract is "if a promise is not
reachable from here, it has no home." Before this item the ledger was hand-maintained against a
pack that says a script owns it, and the repo had two places to file a decision with no rule for
which. The obligation every phase was checked against: **the four promises come out reachable,
unaltered, and correctly graded**, and a cold agent can route a new decision from one stated rule.

## Summary

The item delivers what it specified. Both engines are installed byte-identical to the pack and
pass the pack's own suites here (32/32, 46/46). The four promises are renamed, carry accurate
frontmatter, regenerate into the committed index byte-for-byte, and their bodies are unchanged
below the block except for the five owner-ratified link repoints. The routing criterion is filed
`[OWNER]`, all nine existing decisions are triaged, and no live document claims a single ADR home.
Five follow-up findings remain, none a spec gap: three lines of pack README prose edited in place
without a design note, two dead negative assertions in the I6 test, an old-form compatibility
branch in a test helper, `promoted_to: null` on the most-duplicated ADR entry, and a pre-existing
stale line number in `0001`'s Authority that Item 3 already owns.

## Product Judgment

**Is this the right piece of work? Yes.** It is the smallest change that makes the promise-keeping
mechanism true: the ledger is now read by the tool the pack says owns it, and the routing rule is
one audience question a cold agent can apply without a subject list. Nothing in it narrows or
reinterprets the owner's promises; the owner-verbatim quotes in `0003` and `0004` are byte-identical
to their pre-item state, and the one test guarding them runs unweakened.

**Product-lens ledger gate: DISPOSED.** Run 1 (spec stage) disposed six findings into the spec.
Run 2 (this audit) returned five findings, all DISPOSE, no BLOCK. The epic's live gate
(`.project/backlog/epic_repo_cleanup.md` Product-Lens) is DISPOSED with no BLOCK. No
owner/`[HARD]` contradiction is open in either ledger.

**Smells that fired, and how each is resolved here:**

- **Smell 1 (hand-forked pack file), `audit-F1`.** Confirmed and narrowed. Three lines of the
  pack's own README were edited in place (`.project/product/README.md:36`, `:40-43`), plus a clean
  appended repo-local section. The edit was forced: the pack sentence "it lives in
  `.project/adr/`" is itself a single-home claim, which I6 forbids. The divergence is not silent.
  `test_no_document_claims_a_single_adr_home` asserts "two decision registers" and both register
  paths in that file, so a pack refresh that clobbers it fails the suite. D5 and the spec's
  `[HARD]` index-resolution requirement named this file as the home for the rule. Resolution: the
  smell is real but bounded and guarded; it lands as a design-conformance finding (the in-place
  edit is undocumented) and a follow-up to surface the pack sentence upstream. It does not control
  the verdict.
- **Smell 1, second instance, `audit-F4`.** `.project/adr/0001` restates its rule in `CLAUDE.md`
  and `.project/product/README.md` but declares `promoted_to: null`. The duplication itself is
  owner-required (epic ruling: "`CLAUDE.md` … Item 1 corrects them"). Only the bookkeeping is
  missing. Resolution: code-integrity finding, one frontmatter line; not verdict-controlling.
- **Smell 6 (test cannot fail for the reason it was written), `audit-F2`.** Partly confirmed. The
  negative arm pins one historical phrasing plus two strings that never existed. But the test's
  positive arm is the actual guard and does fail when the convention is removed (verified by
  reading: it requires both register paths and the phrase "two decision registers" in `CLAUDE.md`
  and the README). The lens's falsifier, adding a fresh single-home sentence, would pass the test;
  no string test can catch arbitrary prose, and that is not what I6 asked for. Resolution:
  code-integrity nit; the two dead strings should go. Not verdict-controlling.

`audit-F3` (triage record lives only under `active/`) is mitigated by ordering: the epic's Item 3
scope step 2a carries both re-homes, and Item 3 runs before the Item 5 purge. `audit-F5` (three
bodies edited) was surfaced by the implementer and owner-ratified before this audit; the diffs are
exactly the five link destinations the spec permits.

## Findings

### Plan completion

All five phases verified. Every checkbox was already marked by the implementer; this audit
re-verified each and found none falsely marked.

- Phase 1 — `phase1-findings.md` records the proof and the line-1 ghost-row failure mode. The
  body hash it reports (`ffdbdf03…`) is reproducible from `git show da15f14:…P-003…`.
- Phase 2 — `adr.sh`, `product.sh`, `adr/README.md` are byte-identical to the pack (`cmp`).
  `docs/` and `src/` are untouched in `da15f14..HEAD`. Pack suites pass: `test_adr.sh` 32/32,
  `test_product.sh` 46/46.
- Phase 3 — see I1, I2, I4, I5 below.
- Phase 4 — `.project/adr/0001` exists, `provenance: "[OWNER]"`, states one audience question.
  `adr-triage.md` records nine outcomes and the I3 cross-check. `adr.sh new` in a scratch copy
  allocates `0004`, so the allocator works from this checkout.
- Phase 5 — `0002` and `0003` filed `[AGENT] (ratified by owner, 2026-08-21)`. All four promises
  carry `checked: 2026-08-21 @ 02733b4`; `02733b4` is a real commit. mypy: 30 errors in 8 files,
  matching the recorded baseline, with `git diff da15f14..HEAD -- src` empty.

### Spec conformance

Success criteria, each verified:

- Cold agent can route from one criterion — **met.** `.project/adr/0001:17-20` is one question;
  `CLAUDE.md:143-151` and `.project/product/README.md:46-60` cite it.
- `.project/adr/` exists with the criterion as first entry, `[OWNER]` — **met.**
- Nine triage outcomes — **met.** `adr-triage.md:17-27`.
- Engines manage their registers — **met.** Both indexes regenerate byte-identical in a scratch
  copy, twice; `adr.sh new` allocates the next id.
- Index resolves to entries and exposes grade — **met.** I1 holds for all four product ids and
  three ADR ids; grades live in entry frontmatter; the resolution rule is stated in
  `.project/product/README.md:46-48` and filed as `.project/adr/0002`.
- Promises unchanged below the block except five repoints; citations resolve both directions —
  **met.** Body diff against `da15f14` blobs: `0001` identical; `0002` one line, `0003` one line,
  `0004` three lines, every change a `P-00N-*.md` → `000N-*.md` destination with label unchanged.
  Five total, matching the spec. Outbound: every path cited by the four entries exists. Inbound:
  no file outside `.project/completed/` and this item's own folder references a `P-00N-*.md`
  filename. (The `# P-00N —` headings and `[P-00N]` labels inside the entries are immutable
  visible text and correctly untouched.)
- `CLAUDE.md` and `INDEX.md` no longer claim a single home — **met.** Grep for the retired
  phrasing finds nothing live.
- Owner-verbatim assertions unweakened; index assertions re-expressed — **met.**
  `tests/conformance/test_stop_parser_documentation_contract.py:272-308`: quote text and the three
  step lines unchanged; the two filename assertions became id-row-plus-glob checks.
- Licensed runnable suite green under the accepted limitation — **met.** Re-run this audit with
  the license loaded: 2,371 passed, 9 skipped, 94 deselected, reconciled exactly to the plan's
  count (2,304 + 67 from `tests/unit/test_hierarchy_resolver.py`, which does not need the
  manifest). The documentation contract passes 14/14 with its 3 pre-existing manifest-bound tests
  failing on the missing `STOP_PARSER_ARTIFACT_SOURCE_INPUTS`. The exact full-suite gate remains
  unavailable, not green, as the owner accepted on 2026-08-21.

Tagged requirements: all `[OWNER]`, `[HARD]`, `[INFERRED]` and `[INHERITED]` items are met by the
evidence above. Non-goals respected: nothing moved in `modeling-assumptions.md`, nothing deleted
from `.project/`, no `src/` change, no `agentic-project-init` change.

One observation outside this item's reach:

- `.project/product/0001-design-search-free-variation.md:128` cites ADR-009 at
  `docs/architecture/modeling-assumptions.md:588`; the heading is at `:704`. The drift predates
  this item (`modeling-assumptions.md` last changed 2026-08-16; the entry was filed 2026-08-14)
  and cannot be fixed here under I2. The spec's `[OWNER, 2026-08-21]` requirement already binds
  Item 3 to repoint this citation when it moves ADR-009.

### Design conformance

Implementation follows the design, with one undocumented deviation:

- **`.project/product/README.md:36` and `:40-43` edit pack prose in place.** The design's
  component overview describes this file as "pack contract plus a repo-local section." The
  section is there and clean, but the pack's own heading and one clause were also rewritten,
  because the pack sentence asserts the single home I6 forbids. The edit is forced and correct;
  it is not recorded. What should change: add one line to `design.md` D5 naming the in-place
  edit and why, and raise the pack sentence upstream as a pack issue (the owner has said the
  same boundary problem exists across the claude commands). Until then, every pack refresh of
  this file is a hand-merge, detected by `test_no_document_claims_a_single_adr_home`.

D1–D4 followed as written. D6 deferred as recorded. I1–I6 all hold at HEAD.

### Code integrity

- `tests/conformance/test_stop_parser_documentation_contract.py:53` — `_product_ids_in` accepts
  `- [`, a `P-` prefix, and 3-digit ids with `zfill(4)`. Those are the retired hand-rolled index
  forms; no live index line matches them and I5 guarantees the generated form. A compatibility
  branch with no caller. What should change: match the generated row only
  (`^- (?P<id>[0-9]{4}) · `).
- `tests/conformance/test_stop_parser_documentation_contract.py:95-98` — the negative arm checks
  three strings; `only adr home` and `single adr home` never existed in the tree. What should
  change: keep the one historical phrasing with a comment saying that is what it pins, or drop
  the negative arm and let the positive assertions carry I6.
- `.project/adr/0001-route-decisions-by-who-they-bind.md:12` — `promoted_to: null` while the rule
  is restated in `CLAUDE.md` and `.project/product/README.md`. `0002` and `0003` declare theirs.
  What should change: set `promoted_to` to the two paths. Note `adr.sh` has no `promote`
  subcommand, so this is a hand frontmatter edit either way; the owner should say whether that
  is acceptable on a filed entry or whether the field stays null by policy.
- `tests/conformance/test_stop_parser_documentation_contract.py:125` asserts the literal example
  `docs/architecture/modeling-assumptions.md ADR-009` inside the immutable `0003` entry. When
  Item 3 re-homes ADR-009 the example names a decision that no longer lives there. The entry
  cannot be edited; the test can. Forward note for Item 3, not a defect today.

No god functions, silent fallbacks, or broad excepts were introduced; the new test helpers raise
on missing fields rather than defaulting.

---

## Certification

Checked and marked:

- Plan: all five phases, every checkbox re-verified (they were pre-marked by the implementer;
  none was false).
- Spec: all nine success criteria verified; all tagged requirements met; non-goals respected.
- Epic: Item 1's six success criteria verified against the evidence above; the heading receives ✅.
- Invariants I1–I6 re-derived mechanically at HEAD, not read from the plan.
- Product-lens: run 2 appended to `product-lens.md`; both runs DISPOSED; epic gate DISPOSED.

**Not checked:**

- The exact full-suite gate. Nine manifest-dependent files were omitted exactly as the plan
  records; this audit did not build the five-repository artifact manifest and cannot say those
  tests pass.
- Whether the four promises still hold in code. The `checked` stamps assert the entries were
  validated for the ledger at `02733b4`; this audit did not re-verify the promised behavior, per
  the spec's non-goal. Note the pack README reads `check` as "the promise still holds," which is
  a stronger claim than the spec's "I looked"; the owner should be aware of that gap in wording.
- The pack installer's dry-run census. Phase 2's counts were read from the plan and the commit
  delta, not re-run.
- `.project/completed/` citations of `P-00N`. Out of scope by the spec (Item 5 deletes them); not
  swept.
