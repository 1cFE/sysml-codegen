# Stage brief — narrow-correction step 2: real compiler convergence

You are executing step 2 of the 2026-08-12 narrow correction for Item 7: make L-033/L-034
true in the tree and make the ledger checker capable of catching this class of false execution
record. The persistent authority is the "Narrow correction — executable sequence" in
`.project/active/cutover-recovery/plan.md`; the detailed diagnosis is
`/tmp/handoff-20260812-074345.md` completion-sequence step 2.

This work is **[AGENT] (ratified for execution by owner, 2026-08-12)**. Amend false records;
never append a contradictory second status. Work synchronously and never pause for background
agents. Stop on a real premise conflict.

## Preflight and required reading

Read before editing:

- `.project/active/cutover-recovery/owner-disposition-20260811.md` narrow dispositions.
- `.project/active/cutover-recovery/plan.md` L-033/L-034 history, Gate 4C dispositions for
  L-280/L-281/L-284, REVISE steps 2/3/6, and the narrow-correction sequence.
- `.project/active/cutover-recovery/ledger-4a.json` rows L-033, L-034, L-280, L-281, L-284.
- `.project/active/cutover-recovery/evidence/expression-compiler-qualifier-drop-dryrun.txt` as
  historical measurement. Do not treat its pre-migration failures as the current node list.
- `tests/conformance/test_exact_compiler_core.py`, the named replacement.
- `scripts/check_ledger_4a.py` and `tests/unit/test_check_ledger_4a.py`.

Assert the canonical environment before tests:

- Python: `/home/reid/1cfe/item7-rebuild-venv/bin/python`.
- `sysml_codegen.__file__` resolves under
  `/home/reid/1cfe/sysml-codegen-item7-rebuild`.
- `agentic_mbse.__file__` resolves under
  `/home/reid/1cfe/agentic-mbse-item7-rebuild`.
- `simkit.__file__` resolves under `/home/reid/1cfe/teax`.
- Canonical ruff is 0.16.2. Put the venv `bin` first on `PATH`. Load the SysIDE license from
  `/home/reid/1cfe/agentic-mbse/.env` for the licensed suite.

Confirm both worktrees are clean and record their starting OIDs. Never touch either protected
original repository.

## Required production convergence

1. In `extraction/expression_compiler.py`, delete the legacy name-keyed
   `CompilationResult`, `CalcDefCompilationResult`, and `compile_calc_def` implementation.
   Keep `ExactCompilationResult`, `ExactCalcDefCompilationResult`, and
   `compile_calc_def_exact` as the sole compiler core and migrate no caller away from them.
   **Do not rename the exact survivor to an unsuffixed name.** The latest correction requires
   the three L-033 `removes.symbols` names to be absent; recreating one by renaming would repeat
   the false convergence.
2. In `CalculationDefinitionData`, delete the legacy name-keyed payload fields
   `output_expression_asts`, `all_member_names`, and `member_expressions`. Keep the UUID-keyed
   fields and `member_names_by_id`.
3. Delete the extractor's name-keyed dictionaries and writes. It must populate only the exact-ID
   payload. Do not change expression text reconstruction or the exact member inventory.
4. Remove or migrate every production/test read of those three `CalculationDefinitionData`
   fields. Generic local variables named `all_member_names` in unrelated historical spike or
   computed-attribute logic are not this payload and must not be changed merely to satisfy grep.

## Test responsibility disposition

- Delete `test_exact_compiler_surface_does_not_replace_the_legacy_adapter`; its premise is false
  after convergence.
- In `tests/conformance/test_expression_compiler.py` and
  `tests/unit/test_expression_compiler.py`, retire only the currently collected nodes whose
  subject or setup invokes the removed legacy compiler/result shape. Preserve pure renderer,
  `classify_compilability`, exact-compiler, and already-repointed live-metadata tests.
- Determine the exact current node list from the current source and collection. The historical
  prose says about 32 across L-281/L-284, but migrations have already moved some responsibilities;
  record the actual fully-qualified deleted node IDs. Never use the provisional trim file.
- Migrate surviving schema/extractor/return-style assertions from the name-keyed fields to exact
  UUID-keyed behavior when their recorded disposition is repoint. If the exact replacement
  already exists beside a legacy-shape assertion, delete only the obsolete assertion.
- Keep `tests/conformance/test_exact_compiler_core.py` green as the named replacement. Add no
  duplicate replacement unless a real behavior gap is measured.

## Checker hardening and ledger correction

Strengthen `check_ledger_4a.py`, with kept unit tests, in two ways:

1. An executed row that records deleted test/behavioral responsibility must fail `paths` when
   `replacement_proof_node` is null or empty. Add a structured ledger field carrying the exact
   deleted node IDs for the per-node L-281/L-284 retirements; do not hide this fact in prose.
2. Every `removes.symbols` entry on every executed row must be mechanically verified absent from
   the module/class surface at its repository path. This must catch the current L-033 failure and
   dataclass fields such as L-034, not only whole-file deletion. Cover both surviving paths and
   deleted paths, and cover the companion rows L-036/L-037 using the paired rebuild checkout.
   The check should inspect definitions/declared fields rather than comments or historical prose.

Add an L-034 `removes` block for the three retired fields so the new check owns them. Update the
checker module's stated ceilings because this false-execution class is no longer unchecked.

Correct L-033/L-034 and L-281/L-284 by amending their false execution records. The final ledger
must name the actual product/test/checker commit that completed the work, replace the stale
"deletion stays with the runbook" claims, carry the exact deleted-node lists and named replacement,
and explain briefly how blanket `retire_step.py close 2` produced the false `82c7951` claim.
Do not alter L-280's already-real whole-file retirement.

Use two commits if needed: first product/tests/checker, then ledger/plan/current-work so the record
can name the first commit's OID. Mark narrow-correction step 2 complete only after the final checks.
Set R8 as the next active step in `.project/CURRENT_WORK.md`.

## Declared path set

Only these sysml-codegen paths may change:

- `src/sysml_codegen/extraction/expression_compiler.py`
- `src/sysml_codegen/extraction/data_models.py`
- `src/sysml_codegen/extraction/extractor.py`
- `tests/conformance/test_expression_compiler.py`
- `tests/unit/test_expression_compiler.py`
- `tests/conformance/test_data_models.py`
- `tests/unit/test_data_models.py`
- `tests/conformance/test_extractor.py`
- `tests/conformance/test_return_style_extraction.py`
- `scripts/check_ledger_4a.py`
- `tests/unit/test_check_ledger_4a.py`
- `.project/active/cutover-recovery/ledger-4a.json`
- `.project/active/cutover-recovery/plan.md`
- `.project/CURRENT_WORK.md`

Do not edit the historical dry-run/probe files. Do not edit agentic-mbse in this stage. If another
path genuinely must change, stop before editing and report why.

## Validation

At minimum, using the canonical environment:

1. Assert the three removed compiler symbols are absent as definitions and the exact compiler is
   the only production compiler core.
2. Assert the three legacy dataclass fields are absent; no source/test access remains through
   `calc_def.<legacy-field>`; the extractor has no name-keyed payload write.
3. Run the affected compiler, data-model, extractor, return-style, exact-core, and checker tests.
4. Run the full licensed sysml-codegen suite with `-rs` and record pass/skip/deselect counts plus
   zero `no live syside license` lines. Explain the exact node-count decrease from the recorded
   per-node retirements.
5. Run `check_ledger_4a.py paths`, `surface`, `groups`, and the full `replacements` check with the
   canonical Python. L-033/L-034 replacement proofs must be green.
6. Run `scripts/check_proof_integrity.py` and the distinctness checker used by the final battery.
7. Run ruff on every changed Python file and `ruff check src`; no new finding and the canonical
   total must be no worse than 14. Run `mypy src`; no worse than 57 errors in 11 files.
8. `git diff --check`; exact declared path set; both worktrees clean after commits.

Report both commit OIDs, exact retired node IDs/counts, before/after symbol and payload surfaces,
all validation counts, and any premise conflict.

`ARTIFACT:` `.project/active/cutover-recovery/ledger-4a.json`
