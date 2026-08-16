# Verification artifacts — before the resolver repair

Everything here was captured on **2026-08-15** at commit `d78c42e`, before any production
change and (for the full-suite baseline) before any fixture was added. Phase 3 and Phase 5
compare against these files rather than against memory or research predictions.

The licensed environment is required for every capture:

```bash
set -a; source ../agentic-mbse/.env; set +a
```

## `before-full-suite.txt` — the pre-change full-suite baseline

```bash
uv run --extra dev pytest tests/ -rs -q
```

**Result: 17 failed, 2080 passed, 34 skipped, 88 deselected in 170.09s.** Captured before
this phase added a single fixture or test, so Phase 5 compares like with like.

* **All 17 failures are one environmental cause:** `ModuleNotFoundError: No module named
  'pandas'`. They are `tests/runtime/test_fusion_tea_acceptance.py` (4),
  `tests/unit/test_report_precedence.py` (12), and
  `tests/conformance/test_output_schema_contract.py::test_each_schema_is_a_named_multioutput_subclass_with_exact_required_fields`
  (1). Nothing in this item touches them.
* **All 34 skips are golden-fixture skips**, 25 from `test_computed_attribute_golden.py`
  ("no computed attributes in the golden") and 9 from `test_calc_compat_parity.py` ("no calc
  output expressions in the golden").
* **Zero license-related skips.** A skipped licensed test would have made the run worthless;
  there are none, so this is a real full run.
* The 88 deselected come from the project's own `-m "not execution"` default in
  `pyproject.toml`.

## `corpus_roots.json` — the frozen corpus root set

140 tracked model roots: every top-level directory under `tests/fixtures`, every root under
`.project/active/self-binding-replacement/spike/fixtures`, and the source-identity probe
model directory. This is the same root set the 2026-08-15 corpus scans measured, so the rows
below compare to those reports.

It is frozen deliberately. The thirteen fixture roots this item promotes are captured in a
separate `promoted` section of the ledger and never enter the corpus counts, so the
before/after comparison cannot be diluted by the regression fixtures the item itself adds.

## `before.json` — the pre-repair corpus ledger

```bash
uv run python .project/active/qualified-reference-occurrence-anchoring/verification/corpus_compare.py \
  --output .project/active/qualified-reference-occurrence-anchoring/verification/before.json
```

Canonical JSON; three consecutive runs were byte-identical.

What a row is: one authored reference of **one segment whose exact leaf is owned by a live
`PartUsage`** — exactly the population the repaired branch acts on — keyed by
`(root, lane, consumer node, reference ordinal, leaf declaration)`. Each row carries the
exact leaf and owner declaration IDs, the caller lane, and the shipped result: a typed edge,
the full diagnostic that replaced it, or a named structural reason. Written reference text
is recorded as a classification key for a human reader and is never compared.

Counts:

| Section | Roots | Refused | Sites | Lanes | Outcomes |
|---|---|---|---|---|---|
| corpus | 140 | 15 | 409 | 318 calc binding, 76 computed expression, 15 constraint binding | 405 edge, 4 diagnostic |
| promoted | 13 | 0 | 16 | 9 calc binding, 4 computed expression, 1 alias, 1 constraint binding, 1 constraint predicate | 12 edge, 4 diagnostic |

Three of those numbers are independent corroboration of the 2026-08-15 measurement rather
than a restatement of it: the corpus has exactly **76** computed-expression sites and **15**
constraint-binding sites, matching
`.project/research/20260815-142743_bare-expression-side-measurement.md:92-124`, and it has
**zero** alias and **zero** inline-predicate sites, which is why those two lanes have no
evidence except the authored fixture this phase adds.

The corpus's 4 diagnostics are the spike copies of u4, u5, and u7's two inputs. With u6's
silently wrong edge that is the five changed sites the corpus scan predicted.

**Deep-override lane:** 0 one-segment sites across every root that elaborated. Each root
also records its deep-override site count and the segment lengths it uses, so the lane is
counted rather than assumed absent — this is the standing D11 coverage gap, measured again
here.

**Where a refused root goes.** A root that fails to load, is blocked by model validation, or
raises during elaboration is one row with a named `refused` reason and no sites. Phase 5
compares the refusal strings as well as the site keys, so a root that starts or stops
refusing is a visible difference rather than a silently missing set of sites.

## `before-snapshot-inventory.json` — committed v6 snapshots before the repair

```bash
uv run python scripts/assess_v6_snapshot_churn.py \
  --output .project/active/qualified-reference-occurrence-anchoring/verification/before-snapshot-inventory.json
```

**23 tracked, 23 assessed, 0 stale.** Every committed snapshot agrees with live elaboration
today, so any staleness Phase 4 finds is caused by this repair and by nothing else.

## After the repair — Phase 3

Two files were added on 2026-08-15 after the single resolver change landed. Both come from the
same commands as their `before` counterparts, so the comparison is file to file.

* `after-phase3.json` — the post-repair ledger. Against `before.json`: the corpus moves from
  405 edge / 4 diagnostic to **409 edge / 0 diagnostic** over the same 409 site keys, exactly 5
  sites change (u4, u5, u7's two inputs, and u6's moved edge), and the per-root `identity`
  blocks — occurrence wire IDs and every attribute/calculation/constraint node ID — compare
  **equal across all 153 roots**.
* `after-phase3-full-suite.txt` — 17 failed, 2132 passed, 34 skipped, 88 deselected. The failing
  node set is identical to `before-full-suite.txt`'s 17 missing-pandas failures.

Phase 5 re-runs the ledger against the shipped tree and adjudicates the corpus formally; these
two files are Phase 3's own evidence, not that adjudication.
