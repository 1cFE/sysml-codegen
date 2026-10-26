# TEAx execution lane receipt (repeated-rollup-collision, phase 5)

`lane.sh <codegen commit> <empty work folder>` builds an isolated lane and runs `tests/execution -m execution` with a provenance manifest. It is the subset-profile-screen recipe (`.project/active/subset-profile-screen/evidence/execution-lane/`) with three changes: codegen is this checkout, agentic-mbse is the committed HEAD of `/home/reid/src/agentic-mbse` (the editable dependency this branch was built against) rather than `e268357f`, and the manifest writer is `lane_manifest.py` beside the script, which takes the agentic-mbse commit as a third argument.

## Receipt, 2026-10-26

| codegen commit | codegen archive sha256 | agentic-mbse | TEAx | result |
|---|---|---|---|---|
| `73a69863` (phase 4: fixtures, tests and pins) | `999a6c0c63e25aa2…` | `a2808cb9`, wheel `bbcf15a709aa6fb7…` | `8d877460`, archive `c566cf44569c9557…` | 137 passed, 0 failed, 0 skipped |

137 is the earlier lane's 124 plus the 13 cases of the new `tests/execution/test_repeated_rollup_teax.py`. Full manifest: `provenance-73a69863.json`.

Not checked: the 124 earlier test IDs were not compared one by one against the 2026-10-20 receipts, and the lane used a different agentic-mbse commit than those receipts.
