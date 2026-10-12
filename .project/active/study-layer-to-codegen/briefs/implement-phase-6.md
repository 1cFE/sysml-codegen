# Brief: implement Phase 6 — study-layer-to-codegen

Sent by the orchestrator (2026-10-12) to `/_my_implement`. Implement **Phase 6** of `.project/active/study-layer-to-codegen/plan.md`: the installer, docs and ADRs, the scripts the orchestrator runs, and the final suites. Only Phase 6. Read Phases 1–5's Implementation Notes first.

## State

- Phase 5 was merged from its parallel worktree (`bea97cb`).
- Merged suite: 2713 passed, 9 skipped, 1 failed. The failure is the known guidance-contract test. ruff and mypy are clean.
- agentic-mbse's `installer/v1` is at `0843fe2`, and this `.venv` imports it from `/home/reid/1cfe/agentic-mbse-study-layer`.
- The design is amended at `1f69dd7`: nine route modules, and the record-copy rule.

## Fixes carried into this phase [AGENT, orchestrator, 2026-10-12]

Apply each one, and record it in the notes.

1. **`link_mode`.** `install_bundle` takes `"symlink"` or `"copy"`. The design's DD4 says `"link"`. Pass `"symlink"`, or whatever the CLI's chosen mode is, mapped to those two values.
2. **The `indicators.py` "65 edges" count** (Phase 5 proposal). This is a fusion-specific count in a docstring or comment. State it generally. SC5 allows docstring edits.
3. **The `/home/` path in `teax-completion.md`** (Phase 5 proposal). It now ships to every project through the installer, so the owner's bar applies: no machine paths. Replace it with a general instruction. If a path is needed, use a placeholder the user fills in.
4. **The root rule under read coverage** (Phase 4 note). The shipped runbook's "The tools" section and `integration-guide.md` state the rule as it now is:
   - a route run under read coverage needs no project-root variable when its package is in a git work tree;
   - outside a work tree, the run refuses with a message that names `SYSML_CODEGEN_PROJECT_ROOT`.

   Remove any text that says the variable is always needed.
5. **The fusion-tea adoption runbook draft:**
   - **Nine route modules.** Every step-5 command and check names the nine live `study_route.py` files explicitly. No pathspec glob: git's `*` crosses `/` and would match the route copies inside committed records, which must never change.
   - **The env grep fix:** `STOP_PARSER_[A-Z_]*`, from Phase 4's note.
   - **Both step-5 patches.** List `step5-tests.patch` (Phase 4) and `step5-guide-contract.patch` (Phase 5), with the order they apply in. Check they apply together cleanly to a fresh `b06585709` copy from the staged sources.
   - **The citations of Phase 4's drafts.** Phase 5 wrote these against the plan's paths. Check them against the real files.
6. **Re-run parity** if Phase 5's docstring commit trips the plan's re-run trigger (it changed five study modules). Record the table. It must stay at 28 cases with 0 `DIFFERENT`.

## The installer bar

- `install-commands` installs through agentic-mbse's `Installer`, with sysml-codegen's own manifest, for Claude Code and Codex.
- The policy template is a project document: created once and preserved.
- `teax-completion` keeps installing.
- The `INSTALLER_API_VERSION` check is lazy and fails closed, naming the revision needed.
- It works from a built wheel. Package data is in the wheel; check it with a wheel build in your tests or scripts.
- The coexistence tests run in both orders against agentic-mbse's `init`.

## The orchestrator scripts

The plan names them: the wheel install transcript, the dry-run setup, and the rehearsal. Make each one runnable as written, with its expected observations. The orchestrator runs them after this phase.

## As before

- **The contract** is `design.md` and `spec.md`. The closed list is B1–B13. Use `uv run --no-sync`.
- **Commit** each coherent step with explicit paths (`git commit -- <paths>`), after checking the index is otherwise empty. Each subject leads with what changed. End each message with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Do not push.
- **Before you finish,** tick Phase 6's checkboxes and add Implementation Notes: final suite counts (default, teax lane, license lane), and anything the orchestrator steps O1–O5 need.

Do not start background tasks. Finish with a short report and `ARTIFACT: .project/active/study-layer-to-codegen/plan.md`.
