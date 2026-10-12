# Brief: implement Phase 4 (finish) — study-layer-to-codegen

Sent by the orchestrator (2026-10-12) to `/_my_implement`. Finish **Phase 4** of `.project/active/study-layer-to-codegen/plan.md`. The previous session paused at SC12's stop rule (`12c38b9`). Read its notes in the plan first. Only Phase 4. Phase 5 is running in parallel in another worktree (branch `study-layer-text`); do not touch Phase 5's section of the plan or the shipped skill text.

## Decisions on the pause [AGENT, orchestrator, 2026-10-12]

- **Q1: option (a).** Add the three named rules to the parity harness, each citing its reason:
  1. **Moved-only declarations under the installed `sysml_codegen` package are B8 additions.** In the original, a route's reads of the installed package were already permitted as `runtime-observed` under the venv prefix. The moved observer declares them with digests: the permission is the same and the receipt records more.
  2. **Reads of the installed package are compared by module, with category free.**
  3. **The preload exclusion also covers the three non-standard-library modules the moved driver preloads** (`sysml_codegen`, `sysml_codegen.study`, `sysml_codegen.study.roots`). Measure them, don't list them by hand, and record them in `preloads.json`.

  Re-run `parity.py … report` and confirm all 28 cases are `EQUAL` or `EQUAL after closed-list fields`. Record the per-case result.
- **Q2: ratified as listed.** That covers the original-environment `SYSML_CODEGEN_PROJECT_ROOT`, the B7 mapping row, the three noise patterns proven by orig vs. orig2, and the comparison choices. Record them in the harness's rule list with their evidence.
- **New: fix the B1 regression under read coverage.**
  - **The regression.** Outside `integrate`, a route run under `read_coverage.run_route` without `SYSML_CODEGEN_PROJECT_ROOT` makes the moved `build_sealed` call `git`. The observer refuses that as `unsupported integer-descriptor open: 3`, which doesn't name the cause. The original resolved its root from `__file__` and never ran git. So the move introduced this, and documenting a variable would leave a trap for every target.
  - **The fix.** `run_route` resolves the project root, anchored on its `package` argument through `roots`, before it constructs or activates the observer. It pins that root for the duration of the route and restores the previous state afterwards.
  - **If the root can't be resolved,** the receipt fails closed, with `route_error` naming the cause, in `roots`' own words.
  - Add whatever small API `roots` needs for that pin-and-restore. Keep it typed and documented, and say whether it joins the supported target API.
  - **Tests:** the station route under `run_route` with no `SYSML_CODEGEN_PROJECT_ROOT` passes gate 7's read coverage, and a package in no work tree fails closed with the named cause.
  - Record this in the plan as a B1 refinement, and confirm parity is unchanged by it. The original-environment variable stays only because the original seam needs it.
- **Then finish Phase 4 as planned:** the fusion-tea code drafts, the smoke test, the test patch (check whether the three Appendix H3 tests still need the variable once this fix is in), and the rehearsal helpers.

## As before

- **The contract** is `design.md` and `spec.md`. The closed list is B1–B13. Use `uv run --no-sync`.
- **Commit** each coherent step with explicit paths (`git commit -- <paths>`), after checking the index is otherwise empty. Each subject leads with what changed. End each message with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Do not push.
- **Before you finish,** tick Phase 4's checkboxes and add Implementation Notes: the final parity table, test counts, and anything Phase 6 must know.

Do not start background tasks. Finish with a short report and `ARTIFACT: .project/active/study-layer-to-codegen/plan.md`.
