---
name: byte-identity-captured-at-churn
description: Why a full snapshot re-capture shows ALL fixtures modified, and how to run the byte-identity gate correctly
metadata:
  type: reference
---

Running `scripts/capture_extraction_snapshots.py` (no `--fixtures`) rewrites the
`captured_at` timestamp in **every** `extraction_snapshot.json`, so `git status` shows
all ~23 fixtures modified even when your code change is semantically inert. This looks
like a byte-identity gate FAILURE but usually isn't.

**How to run the gate correctly (Row-D / aggregation-dispatch style changes):**
1. Capture only the new fixture: `--fixtures <name>`.
2. To prove inertness on existing corpora, re-capture all, then verify each modified
   snapshot's diff is **timestamp-only**:
   `for f in $(git diff --name-only -- tests/fixtures/); do git diff "$f" | grep -E '^[+-]' | grep -vE '^(\+\+\+|---)' | grep -v captured_at; done`
   Empty output ⇒ the change is byte-inert.
3. Revert the timestamp churn so the gate shows only the new fixture:
   `git diff --name-only -- 'tests/fixtures/*/extraction_snapshot.json' | xargs git checkout --`
   (A bare `git checkout -- tests/fixtures/*/...` ABORTS if the glob hits an untracked new
   fixture dir — filter to tracked paths as above.)

Verified 2026-07-06 landing Item 8's Row-D `_walk_aggregation_ast` literal-hoist: all 23
existing v2 corpora differed only in `captured_at`; the sole real change was the new
`agg_literal_probe` fixture. Related: [[plant-idiom-fixtures]], [[syside-license-via-scripts-not-dashc]].
