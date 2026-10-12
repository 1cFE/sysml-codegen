# Brief: design_review — study-layer-to-codegen (WRAP-SPLIT Item 3)

Sent by the orchestrator (agentic-mbse `/_my_orchestrate` run, 2026-10-12) to `/_my_design_review`, in a fresh session. Review `.project/active/study-layer-to-codegen/design.md` (committed `4533510`) against its spec, `spec.md` (`a09bdb1`). The briefs in `briefs/` show what each stage was told.

## Sources

Stage agents can't read sibling repos. Staged, read-only copies are in `.orchestrate-logs/src/`:
- fusion-tea `@b06585709`: the study layer, `CONSUMER_SURFACE.md`, `CONSUMER_ATTRIBUTES.md`, and one committed record's documents;
- agentic-mbse `@main`: the installer, `CLAUDE.md`, the epic, the ledger, and Item 2's design and runbook.

This repo's code is live in the worktree. You may run read-only probes on scratch copies (`.orchestrate-logs/scratch/`) to check a claim.

## The orchestrator's position on the design's premise conflicts

Check these. Don't take them on trust.
- **Conflict 1 (no agentic-mbse version bump; `INSTALLER_API_VERSION` instead).** The orchestrator verified that the snapshot loader rejects a mismatched `agentic_mbse_version` (`src/sysml_codegen/snapshot/envelope.py:459-473`). It accepts the design's route provisionally. Challenge it if the API-constant check leaves a real hole.
- **Conflict 3 (a new neutral model instead of `wi014_toy`).** Accepted provisionally.
- **Conflict 4 (`integrate` writes its usual `BLOCKER` when teax is missing).** Accepted provisionally, as a reading of B9 that keeps `integrate`'s two-class return.

## What to press on

Beyond your standard pass:
1. **Engineering quality.** Is `sysml_codegen.study` a clean, well-bounded package, or a lift-and-shift with new names?
   - Look hard at `roots.py`, at the project-root rule (env var, else git work tree, else exit 2), and at how root-dependent functions behave for library callers (Appendix C). fusion-tea calls `manifest.repo_relative_posix` from 13 files.
   - Does anything still smell of fusion-tea's layout?
2. **The declaration surface.** Is `[tool.sysml-codegen.integrate]` in the target's `pyproject.toml` the right home and shape? Consider a target without a `pyproject.toml`, and a monorepo. Is the undeclared-gate path really fail-closed (D8)?
3. **Installer reuse.** Is Appendix B's agentic-mbse change minimal and behaviour-preserving for agentic-mbse's existing callers? Does a separate manifest truly isolate the two installers in both orders, including retired-resource removal and legacy-link adoption? Is `install_bundle` the right public seam?
4. **Byte-faithfulness.** Does the edit map (Appendix A) stay inside the closed list B1–B11? Can the SC12 parity design (Appendix G) catch an unlisted difference? Is it masking anything it shouldn't?
5. **fusion-tea adoption.** Do module aliases that pin fusion-tea's root (DD14) really keep `replay.py`, the cwd-determinism tests and the consumers working? Can the three-run rehearsal (Appendix H) separate move failures from the 142-commit generator jump?
6. **Plan-readiness and size.** Could a plan stage turn this into phases without redesigning anything? The estimate is about 6 days against the epic's 2. Is anything in the design gold-plating that the spec does not require?

Write the review where `/_my_design_review` puts it, with a verdict and must-fix / should-fix points. Do not commit. Do not start background tasks. Finish with `ARTIFACT: <path>`.
