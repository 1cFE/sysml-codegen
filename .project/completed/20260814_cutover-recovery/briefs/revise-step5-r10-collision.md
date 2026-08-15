# Stage brief — REVISE step 5 (partial): the R10 same-named-constraint collision test

**You are executing the R10 half of owner step 4** of the REVISE path.
Plan: `/home/reid/1cfe/sysml-codegen-item7-rebuild/.project/active/cutover-recovery/plan.md`.
Read first: `owner-disposition-20260811.md` (step 4), the plan's amended Gate 4D S4 section
(the R8 context — R8 itself is BLOCKED on an open owner question; do not touch
`elaborate.py`'s qualifier handling or the `SI_RENDERING_COLLISION` pins beyond what R10
itself requires), and the existing collision tests
(`tests/conformance/test_elaboration_projection.py:156`, `test_d5_variants.py:273`,
`test_costed_component_exact_route.py:324`).

Work synchronously. Never pause for background agents; finish or stop with questions.

## Intent

Owner ruling: add a collision test for R10 — two same-named constraint usages under one
owner must not mint the same `…__threshold`-style constraint entry-point/catalog key. No
corpus model has the shape today, which is why nothing pins it. The deliverable is a kept
test with a purpose-built fixture proving the product either (a) mints distinct keys for
the two usages, or (b) refuses with a typed collision error. WHICH of the two the product
does today is a measurement, not a choice: build the fixture, run the exact route, record
the behavior, and pin it if it is sound. Silent collision — one key, last writer wins, no
error — is the only unacceptable outcome; if that is what you measure, that is a rule-10
surfacing (it is the same defect class as the S4 qualifier collapse), and the stage stops
with the evidence instead of pinning it.

## Worklist

1. Author a minimal fixture (beside the corpus, joins no ledger, never touches the 37
   ratified fixtures or the accepted batch): one part owner carrying two constraint usages
   with the same usage name (each with an `in attribute threshold` parameter, per the
   `gate_a` idiom), such that both would project constraint entries. Follow
   sysml-conventions (load the skill). If the parser itself refuses duplicate sibling names
   at this position, record that as the refusal mechanism with the parser diagnostic pinned
   — that IS an acceptable (b) outcome, provided the refusal is typed and reaches the user
   before generation.
2. Author the kept conformance test: elaborate/project via the public route; assert distinct
   keys or the typed refusal; assert the catalog/entry-point key multiset explicitly (exact
   vocabulary, no substring matching).
3. Record the measured behavior in the plan stage note (which of (a)/(b) it is, and the
   mechanism), and tick the disposition-record R10 line.

## Environment

Same as prior stages: worktree `/home/reid/1cfe/sysml-codegen-item7-rebuild`; venv
`/home/reid/1cfe/item7-rebuild-venv` (assert resolved `__file__` first); license via
`set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a`, zero license-skip lines is the
only proof; scratch beside repos; venv bin on PATH.
Expected clean start (post step 4): licensed suite **3866 / 47 / 83**; execution lane **83**;
corpus `--check` 15/22/0; ruff src **16**; mypy **69 in 16**; ledger paths 304/0; surface 0;
groups READY; runbook patches 4 passed.

## Battery before commit

Full licensed suite (delta = exactly the new nodes, named); corpus `--check`; ruff/mypy
no-new; `git diff --check`; `check_ledger_4a.py` paths + surface + groups;
`test_runbook_patches.py`. One commit; plan stage note updated.

## Report back

The measured behavior (a/b) with the exact keys or diagnostic; fixture + node names; battery
numbers; commit OID. Any rule-10 surfacing. `ARTIFACT:` the updated plan.
