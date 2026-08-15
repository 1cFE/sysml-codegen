# Stage brief — REVISE step 3: replace/repoint the gated behavior tests

**You are executing step 3 of the owner's REVISE path** on the Item 7 cutover recovery.
Plan: `/home/reid/1cfe/sysml-codegen-item7-rebuild/.project/active/cutover-recovery/plan.md`.
Read first: `owner-disposition-20260811.md` (step 2, items 3–6), the plan's fifth-entry items
3–6 with their 2026-08-11 rulings, the "Revise step 2 completion" stage note (its rulings and
deferred-node list bind this stage), `runbook-patches/provisional-trim.txt` (the 113-node list
this stage makes unnecessary), and the affected ledger rows (L-135, L-153, L-100, L-281,
L-287, L-291/L-292/L-293 area).

Work synchronously. Never pause for background agents or schedule check-backs; finish the
artifact this turn or stop with questions as your entire final message.

## Intent

The owner ruled: replace or repoint the affected behavior tests BEFORE their evidence sources
are deleted, so the final retirement runs with **no provisional trim**. These subjects are
live and survive; only their v5 evidence source retires. The bar is the part-6 bar:
independent expectations (hand arithmetic, model-derived values, exact vocabularies),
mechanism citations, no thinning. A per-node disposition is allowed only where a subject
genuinely ends, and it must name the replacement. Nodes already ruled retire-with-the-shape
at step 2 (L-281/L-284's ~32, L-280's) are NOT this stage's — do not touch them.

## Worklist (re-measure at HEAD; recorded counts are from the runbook simulation)

1. **L-135 `test_extractor.py` — 59 nodes** reading retiring v5 fixtures. Repoint onto v6
   snapshots (the ACCEPTED batch), live extraction, or purpose-built minimal fixtures. One
   node's second arm
   (`TestReqExt09ConstraintDropDiagnostic::test_dropped_constraints_land_unassessed_spanning_owner_kinds`)
   needs `catf_mfe_model`, which the exact route refuses (`SI_SELF_BINDING`). Move the
   subject to the `catf_mfe_d5` variant if it carries the trigger (65-constraint sweep across
   owner kinds); otherwise record a per-node disposition with named replacement. Decide in
   the open, in the plan note.
2. **L-153 `test_hierarchy_resolver.py` (44/46) + L-100 `test_ast_dispatch_invariant.py`
   (3/20) — 47 nodes**, breaking at retirement step 1 through the conformance v5 fixtures.
   Repoint onto v6 or live evidence.
3. **L-281 `test_expression_compiler.py` — the five nodes beyond its per-node table** that
   read conformance v5 fixtures (distinct from the ~32 retire-with-shape nodes; re-measure
   which five at HEAD).
4. **L-287 `test_calc_compat_parity.py` — 28 nodes** (assigned here by the step-2 ruling):
   repoint how they CONSTRUCT their input facts (name-keyed → `_by_id`). The subject
   (calc-compat renderer parity) is out of Item 7 scope — its assertions must not change.
   This clears the named dependent on L-034's fields before their deletion row executes.
5. **Capture-filter — gated item 6.** Owner ruling: carry unknown-fixture rejection into the
   v6 capture driver. Add a license-free unknown-positional-name refusal to
   `scripts/capture_v6_batch.py`, with a test node. Repoint/replace the two
   `test_capture_fixtures_filter.py` nodes that die with `scripts/capture_filter.py`, and
   give the four `select_fixtures` nodes their disposition (the module loses its last caller
   at retirement step 2; deletion stays with the runbook).

## Ground rules

- Evidence goes to v6 snapshots, live-route generation, or NEW minimal fixtures that
  elaborate on the exact route. Never modify the 37 ratified corpus fixtures or the accepted
  batch; new fixtures live beside them and join no ledger. Load the sysml-conventions skill
  if writing SysML.
- No wrong-oracle repointing: expectations independently derived, never read back from the
  route under test.
- If a v6 snapshot lacks data a node needs (v5 extraction facts vs v6 instance graph), that
  is a real decision: either the node's subject is v5-only (per-node disposition, named
  replacement) or the evidence moves to live extraction (node becomes license-gated — a real
  change, stated in the docstring). Choose deliberately, per node, and record it.
- Ledger + plan bookkeeping: per-file rows updated; fifth-entry items 3–6 amended as
  executed (cite commits); the runbook section records that `provisional-trim.txt` is
  retired from the final-run flow (the trim ban is the owner's).
- Runbook patch drift: regenerate broken patches from a scratch worktree at the new
  committed HEAD; `tests/unit/test_runbook_patches.py` green. Note the patch-exclusion trap:
  exclusion by exact filename, not substring.
- Rule 10 stands: premise conflicts STOP the stage; your final message is the surfacing.

## Environment

- Worktrees: codegen `/home/reid/1cfe/sysml-codegen-item7-rebuild` (this stage's tree),
  agentic `/home/reid/1cfe/agentic-mbse-item7-rebuild` (read-only here), venv
  `/home/reid/1cfe/item7-rebuild-venv`. FIRST ACTION: assert resolved `__file__` for
  `sysml_codegen`, `agentic_mbse`, `simkit`. Re-assert after any venv operation.
- License: `set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a`. Only valid proof:
  zero `no live syside license` skip lines.
- Scratch worktrees beside the repos in `/home/reid/1cfe/`, never `/tmp`. Never commit
  `uv.lock`. Put the venv's `bin` on PATH.
- Expected clean start (post step 2): codegen **3863 / 47 / 53** licensed, zero license
  skips; corpus `--check` 15/22/0; ruff src **16**; mypy **69 in 16**; ledger paths 303/0;
  surface 0; groups all READY; runbook patches 4 passed.

## Battery before each commit

Full licensed suite (delta = exactly the replaced/repointed/authored nodes, named); corpus
`--check` 15/22/0; ruff (16, no new)/mypy (69 in 16, no new); `git diff --check`;
`check_ledger_4a.py` paths + surface + groups; `test_runbook_patches.py` green. Commit per
coherent slice (one row-family per commit is a good default), message naming the rows.

## Report back

Per-file: nodes replaced/repointed/dispositioned, with names and evidence targets; the
catf_mfe decision; the capture-driver rejection node; any license-gating changes; battery
numbers; commit OIDs. Nodes left for later stages, named. Any rule-10 surfacing.
`ARTIFACT:` the updated plan.
