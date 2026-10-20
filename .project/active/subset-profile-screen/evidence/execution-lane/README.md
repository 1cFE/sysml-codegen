# TEAx execution lane: recipe and receipts (Item 2b, Phase 9)

The execution lane is `tests/execution -m execution` run against an isolated build: a `git archive` of the codegen commit, agentic-mbse `e268357f` built as a wheel, and TEAx `8d877460` cloned. `CODEGEN_EXECUTION_PROVENANCE` points at a `stop-parser-execution-provenance/v1` manifest that records each root's commit and archive or wheel digest.

The recipe is the retired `verification/run_independent_green.py` (`git show 7fb488fb^:verification/run_independent_green.py`). `lane.sh` here is that recipe as one script: `lane.sh <codegen commit> <empty work folder>` builds everything, writes the manifest with `lane_manifest.py`, and runs the lane, leaving `run.txt` and `run.xml` in the folder. It needs `/home/reid/src/teax` and the license in `../agentic-mbse/.env`.

## Receipts, 2026-10-20

| codegen commit | codegen archive sha256 | result |
|---|---|---|
| `556cbedf` (2b base) | `e0889c830882c141…` | 124 passed, 0 failed, 0 skipped |
| `d8f98340` (Phase 8; Phase 9 changes no file under `src/`) | `fd8bb8d9afc1c1c5…` | 124 passed, 0 failed, 0 skipped |
| `8621bac4` (Phase 8 follow-up, report length) | `b30b0214ab8a950c…` | 124 passed, 0 failed, 0 skipped |

All runs used agentic-mbse wheel `2c6cf3d03521b25e…` and TEAx `8d877460` (archive `c566cf44569c9557…`). All three runs have the same 124 test IDs with the same outcomes (checked: True). The full manifests are `provenance-base-556cbedf.json`, `provenance-phase8-d8f98340.json` and `provenance-phase8-followup-8621bac4.json`.
