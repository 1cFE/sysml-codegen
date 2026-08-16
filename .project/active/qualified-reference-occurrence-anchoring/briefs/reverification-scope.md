# Re-verification brief — re-audit findings 1, 5, 6 only

For an independent agent, run by the owner. **Scope is the remediation at `c2fa657`, not the
item.** The repair itself (`98970c9`) has already been independently re-verified twice by separate
sessions and is not in question here.

## Why this pass exists

The last certification failed for one specific reason worth holding in mind the whole way: a
verification stage self-reported "0 identity-block changes over 153 roots," and it took an
independent pass to find that 140 of those roots carried **no identity block at all**. The
comparator mapped a missing block to `None`, compared `None == None`, and counted the root as
compared.

So the failure was never a missing capture. It was **a comparator that read absence as agreement**.
That is the shape of defect to hunt for, here and anywhere else in this tooling.

## What is in scope

Exactly three findings from `audit.md`'s "Independent re-audit — 2026-08-16" section.

**Finding 1 — identity coverage (High).** Claimed fixed by capturing identity for every root that
elaborates and by making `verification/adjudicate.py` raise `MissingIdentityBlockError` rather than
compare two absences.

**Finding 5 — absent leaf failed open (Low).** `_resolve_direct_reference` previously fell through
to the consumer-positional route when the element index lacked the exact leaf, and
`corpus_compare.py` excluded the same shape, so code and verifier shared one blind spot. Claimed
fixed by refusing at that site and by resolving the verifier against a full live `Feature` index.

**Finding 6 — weakly pinned edges (Low).** Claimed fixed by pinning the arrayed strict/lenient edge
on the full consumer/parameter/detail tuple, and by giving the missing-leaf-target raise a real
fixture and kept test — the remediation reports that raise is reachable from an authored model,
contrary to what its brief expected.

## Out of scope — do not touch

Findings **2, 3, 4, and 7** are owner-dispositioned, not defects to fix:

- **2** — SC1's deep-override exception. Settled: SC1 now reads "every shared resolver consumer that
  can reach the one-segment branch," lane named as unevidenced. See `2e42d6c`.
- **3** — arrayed aggregation split. Settled: accepted, follow-up filed at
  `[ANCHORING-ARRAYED-DIAGNOSTIC]` in `.project/backlog/BACKLOG.md`.
- **4** — the self-binding `[HARD]` line. Already corrected, and its residual overclaim aligned in
  `2e42d6c`.
- **7** — companion checkout revision not recorded in the ledger. Not yet done; note it if you like,
  but it is not this pass's job.

Also out of scope: the 17 environmental missing-`pandas` suite failures, and the repo-wide
ruff/mypy backlog (131/52, verified identical at the item's start commit `2768c68`).

## Claims worth distrusting

Regenerate rather than read. The committed ledgers are the artifact under test, not the evidence.

1. **The comparator actually fires.** Delete an identity block from a copy of `after.json` and
   confirm `adjudicate.py` raises rather than reporting agreement. A fix that captures 139 blocks
   but leaves `None == None` intact would look green and still be broken.
2. **`before.json` was regenerated under the real pre-repair resolver**, not reconstructed or
   hand-edited. The remediation claims it restored `elaborate.py` at `98970c9^`, regenerated, then
   restored. Check that it is byte-identical to the committed pre-remediation capture *apart from*
   the added identity blocks and the one new fixture.
3. **The root arithmetic.** 154 roots, 139 with identity, 15 without. Confirm all 15 genuinely
   refuse to elaborate and that a refused root is compared on its refusal string rather than waved
   through — that is the same "absence as agreement" trap in a second costume.
4. **Finding 5 is a real behavior change, not a comment.** The site now raises. Confirm the retained
   census (154 roots, 769 one-segment leaves, 0 absent) is the whole population and that
   `corpus_compare.py` no longer excludes the shape.
5. **Changed rows moved 19 → 20**, from the new finding-6 fixture. Confirm row 20 is adjudicated,
   and that it refuses on both sides with only the diagnostic detail sharpening.
6. **No existing assertion was weakened.** `git diff 8bea4b8 c2fa657 -- tests/` should show
   strengthening and addition only.

## Environment

```bash
set -a; source ../agentic-mbse/.env; set +a
uv run --extra dev pytest tests/ -rs
```

An unlicensed skip is not evidence. Expected full suite: 17 failed / 2145 passed / 34 skipped /
88 deselected, failing node set identical by name to the frozen baseline in `verification/`.

If you restore a historical `elaborate.py` for a negative control, verify `git diff -- src/` is
empty before finishing. Leaving the tree dirty is a failure of the pass.

## What a good outcome looks like

A verdict on the three findings, each closed or reopened on evidence you generated. If a finding is
still open, say so plainly — reporting one is the success case for this pass, not its failure.
