# Stage brief — Phase 4, Gate 4B Groups G0 + G1

**You are executing two approved ledger groups** of the recovery plan:
`/home/reid/1cfe/sysml-codegen-item7-rebuild/.project/active/cutover-recovery/plan.md`.
Read first: the approved ledger `ledger-4a.md` (G0 and G1 tables + the orchestrator approval
record with the C1/C2 rulings in the plan's Gate 4A completion notes), Phase 4 rules, and
`evidence/audit-3e.md` F5 (both halves — C2's subject).

## Scope

**G0 — 9 rows, deletes nothing.** The prerequisite migrations exactly as row-listed:
- Move `SysMLParsingError` and `CodeGenerationError` from `orchestration/pipeline_context.py`
  to a route-neutral home (pick the honest one — `generation/errors.py` already exists as an
  error home; decide and record). Repoint the six importing files listed in rows
  L-018..L-024 (exact_pipeline_context, source_manifest, diagnostic_screen, constraint_catalog,
  generation/errors, generation/initialization). Public exception identity must survive:
  anything catching these classes today must still catch them (alias in the old location until
  G3 removes the module, or re-export — record the choice).
- Move `collect_uncovered_params` and `collect_unwired_fallthrough` out of
  `resolution/graph_builder.py` to a neutral home; repoint `cli/__init__.py:262`.
- The four L-025 cli items, including **C2 as ruled**: delete the unreachable
  GrandfatheredSnapshotError import+handler; remove the `--design-path-filter` flag (typed
  refusal in 3E becomes flag-gone; help text and tests updated per disposition); repoint the two
  helpers; and fix the row-36 refusal — typed error, ordered BEFORE `_clear_output_directory`,
  red→green with an `unresolvable_attr_probe`-shaped specimen through public generate. The
  existing fail-before-mutate specimens must stay green.
- L-021: drop nothing yet — repoint the two error aliases; the PipelineContext alias stays until
  G3 (census API-12 detail in the row).

**G1 — 1 row, first deletion of the recovery.** Delete
`src/sysml_codegen/analysis/signature_extractor.py` AND `tests/unit/test_signature_extractor.py`
together, citing the C1 ruling: the living owner is `generation/preservation.py`, replacement
proof nodes `tests/conformance/test_gen_stencils.py` + `test_generation_boundary.py` +
`tests/unit/test_stencils.py`. Remove the `analysis/__init__.py:20` re-export. Run the proof
nodes explicitly and record their counts.

## Requirements

1. Declare the full path set before editing (the ledger rows give it; add the neutral-home
   files). Unexpected changed path stops the group.
2. **One commit per group** (G0 then G1), each with its battery run BEFORE the commit:
   - G0 battery: full licensed suite (explain delta exactly — expect +1..+2 for the C2 specimen,
     −N only where a flag-removal test row was dispositioned; every removed/changed test node
     named with its ledger authority), 37-path corpus (15/22, zero rows moved), execution lane
     38, ruff byte-identical, mypy measured (71/17 or better), `git diff --check`.
   - G1 battery: full licensed suite (delta exactly the deleted unit-test module's nodes, named,
     citing C1), corpus, ruff/mypy, plus run the three replacement proof modules explicitly.
3. Update the ledger JSON row states (e.g. `executed`, with commit OID) and re-run
   `scripts/check_ledger_4a.py` — paths must stay consistent; the checker consuming the
   candidate diff means executed deletions must not turn into `problems`. If the checker's model
   can't represent an executed row, extend it (with tests) rather than special-casing.
4. Update the plan's Phase 4 notes per group; OID-record commit after both.

## Hard rules

Only G0+G1 rows (plus declared neutral homes). No other deletion, no doc changes, no probe or
snapshot changes. The `replacement_is_green` gate binds G1: run it for L-006 with the new proof
nodes before deleting. Rule-10 conflicts stop the group. Full permissions; venv + license
discipline as recorded (F2 trap; measured gates only — 3D's lesson).

## Report back

Per-group: what moved/was deleted, the C2 fix and its specimen, battery numbers with exact
delta explanations, checker state, commit OIDs. `ARTIFACT:` the updated plan.
