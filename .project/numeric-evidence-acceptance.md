# Numeric evidence acceptance

[OWNER] Fix the blank study column problem across affected repositories, on new branches from main, and submit PRs (2026-09-05 request in fusion-tea).

[INHERITED: fusion-tea `.project/research/20260905-091948_blank-study-column-root-cause.md`] Generated multi-output fields already reach separate numeric pipeline exits. TEAx evidence projection drops their plain numbers.

[AGENT] Keep generated representations unchanged. Add a real-runtime acceptance test generating and sealing a two-output calculation and a dependent single-output calculation through live and snapshot routes. Assert explicit, distinct expected values at evaluation and after study-store close/reopen/query, before and after changing an input. Match queried cases by their input values and assert the expected input set. Remove the mutation test's obsolete multi-output evidence exclusion and assert coverage of the entire graph's numeric outputs.

[AGENT] This acceptance requires TEAx's numeric publication repair (evidence schema v3). No production codegen dependency pin or package regeneration is required by this test-only change. Historic stores retain their prior evidence; new runtime schema compatibility prevents mixing old and new study evidence.

## Validation

Codegen test commit `43333a5` and TEAx runtime commit `ca5d490` were archived and extracted under `/tmp/codegen-numeric-artifacts`. The execution provenance binds those archive hashes and the retained Agentic `443388823f0db46c14df1728d3843d0a74ee7590` wheel. The licensed real-runtime lane passed all 96 tests, including live and snapshot mixed-output acceptance and the whole fusion-tea mutation matrix. The new live acceptance fails at explicit numeric-output equality against the old TEAx runtime.

`ruff check src/` passes. `mypy src/` reports 30 existing errors in eight source files; the branch has no production source diff from `origin/main`.

The full licensed default suite passed 2,543 tests with nine existing skips and 96 execution-test deselections. Its sole failure was the artifact-wheel test being denied writes to the existing uv cache by the sandbox; rerunning that test with cache access passed (one test). The default lane used the codegen virtual environment so CLI subprocess tests could resolve `sysml-codegen`; the execution lane used the Agentic environment for real TEAx dependencies. Logs are retained at `/tmp/codegen-numeric-default-tests-cli.log`, `/tmp/codegen-numeric-cache-recheck.log`, and `/tmp/codegen-numeric-execution-tests.log`.

Review changed the query assertions to match expected values by source input. Both focused live/snapshot tests passed against archived codegen `1f04262` and TEAx `6260502`, bound by `/tmp/codegen-numeric-artifacts-review/execution-provenance.json`; log: `/tmp/codegen-numeric-review-tests.log`. Ruff and diff checks passed. README describes the runtime capability and preserves Python Boolean 0/1 behavior. These focused changes do not alter production generator code.
