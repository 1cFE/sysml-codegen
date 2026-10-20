# Brief: /_my_implement — integrate Item 2a with Item 3 after rebase

The owner merged epic Item 3 (`l6-subset-profile`, agentic-mbse PR #32, `1a3d67c6`). The orchestrator rebased agentic-mbse branch `subset-conformance` onto it (pre-rebase head tagged `pre-rebase-2a`). One conflict, in `tests/fixtures/subset_profile/inventory/matrix.toml` row PUSH-DOWN-HIER-PROFILE-MULTIPLICITY-SHAPE, was resolved by keeping Item 3's closure text with 2a's `sites = []`, `site_status = "codegen_account"`. Check that resolution.

The rebased agentic-mbse suite (`uv sync --all-extras`, `.env` sourced) now has 73 failures/errors against the 5-ID baseline in `.project/active/subset-profile-conformance/evidence/baseline.md`:
- `tests/test_validation/test_l6_contract.py` 53 (e.g. `ValueError: not enough values to unpack (expected 1, got 0)`)
- `tests/test_l6_run_consumers.py` 10 errors (`ModuleNotFoundError: No module named 'probe'`; 2a moved probe helpers to `isolated_tree.py`)
- `test_subset_coverage.py` 2, `test_shipped_text.py` 1, `test_sysml/test_text_fallback.py` 1
- `test_subset_gate_receipt.py` 1 (expected: covered files changed; needs a fresh gate run)
- plus the 5 baseline IDs.

Task:
1. Find each cause and fix it in the cleanest place, so Item 3 runs on 2a's contract (v2 records, `case:` citations, new `calc-usage-result` rule, packaged cases, `isolated_tree.py`). Do not change the intended behavior of either item: Item 3's L6 output contract (its spec/design are archived in agentic-mbse `.project/completed/` for l6-subset-profile) and 2a's conformance guarantees both stand. If they genuinely conflict, stop and report rather than picking one.
2. Run the agentic-mbse suite back to the 5-ID baseline, plus mypy/ruff at baseline counts (88/118, or report a justified change).
3. Rerun the gate (`scripts/subset_profile/codegen_suite.py`, committed revisions, worktrees untouched during the run) against the codegen worktree head and commit a fresh `codegen_gate.json`; the receipt test passes.
4. Run the codegen licensed suite and the 22-snapshot / oracle checks against the rebased agentic-mbse: 9-ID baseline, byte-identical, unchanged.
5. Note the integration in `plan.md` (new section after the final-audit fixes) and update both `CURRENT_WORK.md` files.

Repositories: sysml-codegen this worktree; agentic-mbse `/home/reid/src/subset-conformance/agentic-mbse`. Commit on `subset-conformance` branches only; never push, merge or open PRs. No RG-1 changes. End commit messages with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. End with a short report and `ARTIFACT: <path>`.
