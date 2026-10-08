# PR-readiness implementation evidence

## Baseline captured before source changes — 2026-10-08

[AGENT] Starting codegen `6872977541eae935d4be2789f48f723ffea7101b` and companion `8f43a09` produce the durable complete-package digest oracle in `tests/expectations/public_package_oracle/baseline.json`. Public replay passes all 23 checks: exact 22-snapshot inventory plus 22 complete generated file/refusal comparisons. Version fields are compared as complete bytes. Refusal checks also preserve an existing sentinel directory. The original expectations are immutable; later reviewed deltas must carry exact old/new hashes separately.

Fresh scratch package trees and capture/replay logs are under `/tmp/pr-readiness-evidence/`. The licensed unchanged `fusion_tea` recapture is byte-identical to the committed envelope, SHA-256 `7d30e7e6499814f9496818e38e12ba46d3d176da627415cd9a50fd239d0b8bed`, retained at `fusion_tea-pre-C4.json`. License file: `/home/reid/1cfe/agentic-mbse/.env`; licensed syside availability was independently established before this stage. No credentials are recorded.

Fresh licensed all-22 assessment is retained as `prechange_freshness.json` beside the oracle (unit maps reduced to digest only; full evidence remains in scratch). Two preexisting stale snapshots were found before implementation: `quoted_owner_formula` retains unquoted reference display text where the current companion reports authored quotes, without a projected computation/input change; `solar_battery_d5` changes plural expression port ordering without changing counts/input bytes. Exact prechange diffs are retained. This conflicts with the plan premise that only C3/C4 need recapture; dependent final freshness conclusions remain parked pending reproduced causes and an explicit disposition.

Current customer source archive and three-case starting generation are coordinated independently by the root agent against frozen customer `0e045fb30d9ba1b2f62b3a14b3c3fbfcb3985bc9`; its receipt will be added before Phase 1 completes. Inherited review results are not fresh acceptance.
