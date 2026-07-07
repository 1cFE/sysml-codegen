# Audit: Item 8 — Dead Code & Cleanup Debt (PIPELINE-TRUTH)

**Verdict:** PASS
**Audited:** 2026-07-06
**Branch:** pipeline-truth-epic
**Commit:** 2196645 (HEAD); item spans 3314264, d5032c3, 529dc74, 3ec4efa, 024028b, b1dece5, 2196645

---

## Summary

Every claim in the close-out reproduces. The 12 deleted symbols have zero grep residue
across `src/ tests/ scripts/ docs/`; the 11 deleted tests were all self-tests of those
symbols; the Row-D dispatch fix is in place, its probe passes, and the byte-identity gate
holds against the pre-Phase-5 corpus. REQ-AST-10 has a doc-19 row, a matrix PASS row, and
an independently-anchored fixture expectation. All doc obligations traveled in their code
commit (R1). The four filing-ledger entries exist with content, and the D1-F3 NO-OP
argument checks out against the catf baseline. Gates: 2000/4/5 suite, ruff 19, mypy 104 —
all at or better than the 20/105 baseline.

One nuance, not a defect: the Row-D probe asserts against the committed snapshot rather
than re-walking live, so the durable "RED-before-fix" evidence is the plan's recorded
trace, not a re-runnable artifact. R4 was followed at implement time; noted below.

## Findings

### Plan completion

All six phases verified complete.

- **Phase 0** — baseline recorded (2005/20/105), Item-4 v2 gate confirmed. Gate re-based
  to not-worse-than 20/105; enforced correctly.
- **Phase 1** — 6 deletions + 4 skipif guards. Templates gone
  (`templates/pydantic_schema.py.jinja2`, `templates/entry_point_schema.py.jinja2`
  both absent); `skipif` count in `test_output_registry.py` is 0.
- **Phase 2** — both forks resolved: `get_default_value` DEAD→deleted,
  `generate_derived_group_json` deleted with both export sites. Zero hits for both.
- **Phase 3** — four docstrings + dotted-leaf pin. (Docstring bodies not re-diffed line
  by line; suite green with the +5 pins confirms behavior unchanged.)
- **Phase 4** — all D1 residue dispositioned to BACKLOG/NO-OP; no code landed, gates held.
- **Phase 5** — Row-D fix + fixture + REQ home. Verified in detail below.
- **Phase 6** — close-out count story reconciles (see Spec conformance).

### Spec conformance

- **SC-G (zero grep hits + green + gates).** VERIFIED. All 12 deleted symbols
  (`map_sysml_type_to_rootmodel_wrapper`, `PYTHON_TO_ROOTMODEL_WRAPPER`,
  `_check_semantic_match`, `_extract_keywords`, `binding_to_entry_point`,
  `_binding_to_entry_point`, `get_default_value`, `generate_derived_group_json`, the two
  templates, the skipif marker) → **0 hits** across `src/ tests/ scripts/` and `docs/`.
  Suite **2000 passed / 4 skipped / 5 xfailed**. Ruff **19**, mypy **104** — both better
  than the live 20/105 baseline.

- **Count story auditable (net decrease, each deleted test named).** VERIFIED. Net −5
  passed (2005→2000) = −11 deleted self-tests + 6 added (5 dotted-leaf pins + 1 Row-D
  probe). The 11 deleted tests were confirmed against the diffs: 6 in d5032c3
  (`test_wrapper_*` ×5, `test_python_to_rootmodel_dict_has_4_entries`) all pinning the dead
  wrapper fn/dict; 5 in 529dc74 (`test_req_pgd_06_default_value_*`) all pinning the dead
  `get_default_value`. No non-self-test lost coverage — the modified tests
  (`test_type_mapping_module_exists`, `test_req_dm_03_fields_backtracking_result`) keep the
  live-behavior assertions.

- **Aggregation-literal fix reproduced then fixed (R4).** VERIFIED. The fix is in
  `hierarchy_resolver.py:418` — `is_literal_expression` now dispatches above the
  invocation catch-all at `:422`, with an in-code REQ-AST-10 comment. Probe
  `test_agg_literal_dispatch.py` PASSES (1 passed). Byte-identity: `git show
  024028b:tests/fixtures/<f>/extraction_snapshot.json | diff` empty for wi014_toy,
  ife_plant, catf_mfe_model — reorder is byte-inert on the committed corpus. RED evidence
  is the plan trace (`plan.md:454`): pre-fix walk gave
  `transformed_expression='(module.cost + LiteralRationalEvaluation())'`,
  `has_unsupported_nodes=True`. See note under Code integrity on the probe's snapshot-read
  design.

- **Fixed dispatch has a REQ home.** VERIFIED. REQ-AST-10 in doc-19's table
  (`19-ast-dispatch-invariant.md:41`) verified-by the fixture; matrix PASS row at
  `verification-matrix.md:91`; the fires-on-shape expectation (`5.0` survives,
  `has_unsupported_nodes` False, no `LiteralRationalEvaluation`) is hard-coded in the test,
  not computed by the walker.

- **doc-19 note retired, BACKLOG closed, doc-25 hedge pinned.** VERIFIED. doc-19:65 now
  reads "`_walk_aggregation_ast` now conforms (REQ-AST-10)" and hands retirement to Item 10.
  BACKLOG aggregation entry → "✅ RESOLVED by PIPELINE-TRUTH Item 8 (Row D)"
  (`BACKLOG.md:255`). Dotted-leaf pin (`TestDottedLeafAliasMatch`, 5 tests) added in
  3ec4efa; doc-25 rewritten (13-line change in that commit).

- **Every D1 finding dispositioned.** VERIFIED. F1/SC-11 → FILE `[SC11-IMPORT-REWRITE]` +
  corrected the false "filed follow-up" claim; F2 → FILE `[SANITIZER-MERGE]`; F3 → NO-OP
  (see below); F4 → FILE `[GB-PARAMGROUPS-TYPING]`; F5 → DONE (dead subprocess var
  removed). All four BACKLOG tags exist with content (`:190, :179, :200, :213`).

- **D1-F3 NO-OP argument sound.** VERIFIED against the baseline:
  `catf_mfe_model/designs/catf_mfe/vacuum.sysml:130` — `attribute pumping_speed_total :
  Real = 200`. A valued design attribute (USAGE_LITERAL, valued), so the uncovered-params
  collector correctly skips it. Benign pre-existing catf gap, not a bug. Correctly
  recorded as NO-OP.

- **4 vacuous skipif guards removed.** VERIFIED (skipif count = 0).

- **R1 (docs travel in-commit).** VERIFIED per commit: doc-08/09/11 in d5032c3;
  doc-17 + verification-matrix in 529dc74 (breadcrumb landed at `:380`, spec cited `:379`
  — line drift, not a gap; `PENDING-ITEM7 · [ITEM7-PGD06]` present); doc-25 in 3ec4efa.

### Design conformance

No design.md (spec+plan only, per the item). Requirements are the catalog A–H; all
traced above.

- **[HARD] byte-identity via scripts, no hand-edited baselines** — VERIFIED (diff empty;
  plan records timestamp-only churn reverted).
- **[HARD] R4 verify-then-fix** — followed; intent checked against doc-19, RED trace
  recorded before the hoist.
- **[HARD] sequencing vs Item 4** — Phase 5 ran after the v2 re-capture (all snapshots at
  format v2 per Phase 0); fixture captured at v2.
- **[HARD] no ComputationGraph rev** — every change is a deletion, docstring, test, pin,
  or the dispatch reorder.
- **[HARD] test-deletion rule** — 11 deletions all self-tests; net decrease; each named.
- **Item 5 cross-check (disjointness).** VERIFIED. Item 5's design fences
  `_walk_aggregation_ast` (`silent-failure-hardening/design.md:247-256`): D3-8 edits only
  the OperatorExpression operator translation, written against the *post-reorder* dispatch,
  and sequences its implement after Item 8's. The current shape matches — literal branch
  (`:418`) sits above the invocation catch-all (`:422`), OperatorExpression arm
  (`:386-406`) untouched. The two edits are disjoint within the function.
- **Handoffs left correctly.** `_deserialize_constraint_info` / `extract_all_constraints`
  are absent from `src/` — Item 4 (which owns them, per Non-Goals) already handled them;
  Item 8 correctly did not touch them.

### Code integrity

- **Row-D probe reads the snapshot, not a live walk (note, not a defect).**
  `test_agg_literal_dispatch.py:27` loads the committed `agg_literal_probe`
  snapshot and asserts on its `transformed_expression` / `has_unsupported_nodes`. So the
  test's RED/GREEN status is a function of what was captured, and the durable proof that
  the *walker* changed behavior is the plan's prose trace (`plan.md:454`), not a
  re-runnable pre-fix artifact. This is a reasonable design for an extraction-only probe
  (the scoped design-instance path isn't exercised) and R4 was followed at implement time
  (RED-first capture with pre-fix code, documented). Recorded so a future reader knows the
  "red before" evidence lives in prose, not a committed fixture snapshot.

- No slop or failure-honesty issues in the touched code. The dispatch reorder adds a clear
  REQ-AST-10 comment (`hierarchy_resolver.py:414-417`) explaining why literals must precede
  the catch-all. The §H skipif removal replaced try/except import stubs with plain imports
  (FAIL-LOUDLY), which is the correct direction.

- Line-number drift from the spec (matrix `:379`→`:380`, BACKLOG `:185` moved) is expected
  and was handled by re-grep at implement, exactly as the [HARD] re-grep rule requires.

---

## Certification

Checked and verified: all 12 deletions (zero residue, src/tests/scripts/docs); the 11
deleted tests as self-tests against the actual diffs; the Row-D fix location, its passing
probe, and byte-identity against 024028b for three corpora; REQ-AST-10's doc-19 row, matrix
PASS row, and independently-anchored fixture expectation; the R1 in-commit doc travel for
doc-08/09/11/17/25 and the matrix breadcrumb; the four BACKLOG filing entries with content;
the D1-F3 NO-OP against the catf baseline; the gates (2000/4/5, ruff 19, mypy 104); and the
Item 5 disjointness fence against the post-reorder function shape.

Spec success criteria and plan phases are all marked complete by the implementer and are
all independently verified here. No criteria left open. The one recorded note (probe reads
snapshot, RED evidence is prose) does not block certification — R4 was honored at implement
time.

Marking: spec SC and plan phases stand as verified. Epic Item 8 / SC-G verified green.

ARTIFACT: .project/active/cleanup-debt/audit.md
