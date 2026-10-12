# Brief: spec — study-layer-to-codegen (WRAP-SPLIT Item 3)

Sent by the orchestrator (agentic-mbse `/_my_orchestrate` run, 2026-10-12) to `/_my_spec`. Write the spec at `.project/active/study-layer-to-codegen/spec.md` in this repo (sysml-codegen worktree `/home/reid/1cfe/sysml-codegen-study-layer`, branch `study-layer-to-codegen`, base `aa35f06`).

## The work item

WRAP-SPLIT Item 3, "Move the study layer to sysml-codegen". The epic lives in agentic-mbse. A copy is at `.orchestrate-logs/src/agentic-mbse@main/.project/backlog/epic_wrap-split.md`; read its header ("Owner decisions carried in"), its Success Criteria, and Item 3 in full. The research audit it implements is beside it (`.project/research/20261005-204804_wrap-split-agentic-mbse-fusion-tea.md`, § 1b and Open Question 1).

## Where things are (read this first)

You cannot read sibling repos. The orchestrator copied what you need into this worktree's gitignored `.orchestrate-logs/src/`. Read them freely; do not edit, run, or commit them.
- `.orchestrate-logs/src/fusion-tea@b06585709/`: fusion-tea's study layer at its `origin/main`. Contains `.claude/skills/run-study/{SKILL,runbook,record-template}.md`, `scripts/study/*` with 7 schemas, `scripts/integrate.py`, `modeling_project/STUDY_POLICY.md`, `tests/study/*` (with `data/synthetic_pkg`), the two repo tests `integrate.py` runs as gates, `docs/integration_seam_operator_guide.md`, the run-study concept, concept-design and its review, ADR-0009 and ADR-0010, four package annexes, `pyproject.toml`, `CLAUDE.md`, `.gitignore`.
- `.orchestrate-logs/src/fusion-tea@b06585709/CONSUMER_SURFACE.md`: every non-record fusion-tea file that imports or invokes the study tools. The orchestrator generated it.
- `.orchestrate-logs/src/agentic-mbse@main/`: the epic, the research audit, the shared migration ledger, agentic-mbse's installer (`src/agentic_mbse/cli/installation.py`), its `CLAUDE.md` (read "Init File Ownership" and "Change Coordination"), and Item 2's design and fusion-tea runbook. Item 2 is the precedent for a shipped dated snapshot and for a post-merge fusion-tea runbook.

## Intent, with provenance

Owner-grade (carry these as owner, quote where quoted):
- [OWNER] (epic header, 2026-10-06) The study layer ships from sysml-codegen. That means the `run-study` skill and the tools it calls (`scripts/study/*`, `integrate.py`). sysml-codegen already depends on agentic-mbse, owns the generated-package contracts the tools read, and already has an `install-commands` subcommand. agentic-mbse ships the goal layer.
- [OWNER] (epic header) Fusion vocabulary is acceptable in examples. The bar is that the text reads as a general rule or practice. What must go: pointers into fusion-tea or sysml-codegen internals as authority, hard-coded machine paths, consumer requirement numbers (MR-7), and instructions that only make sense for one project.
- [OWNER] (epic header) No loss of information for fusion-tea. Any instruction removed from the ported text because it is consumer-specific moves into fusion-tea's own files, recorded in the shared migration ledger.
- [OWNER] (epic header) Keep the item count low.
- [OWNER] (fusion-tea run-study concept, "Next-Stage Handoff") The capability factors as a lightweight skill + runbook + policy rulebook + tools, and agent judgment is not frozen into tools. Indicators are context, never gates. Intake is collaborative and flexible. One skill serves the executing and administrator roles. "Nothing pushes back" on a requested axis is a model-underdevelopment signal, surfaced to the user. The concept's "Owner's Words" section holds the verbatim quotes; carry the ones you rely on as `[OWNER-VERBATIM]` with the quote.

Inherited, challengeable:
- [INHERITED: research audit § 1b] The split of `STUDY_POLICY.md` into general sections (§1–5, §9, §11) and fusion sections (§6–8, §10, worked examples). This is the research agent's classification, not the owner's. Re-check it against the policy text.
- [INHERITED: epic Item 3] The scope list, the success criteria, the effort (2 days), and the Out of Scope list. The epic is agent-authored apart from its header decisions.

## Orchestrator decisions [AGENT, orchestrator, 2026-10-12]

The owner delegated these at Align ("take accountability"). Record them as `[AGENT]` decisions in the spec, not as owner requirements.
1. **This item delivers the sysml-codegen side; fusion-tea adopts after merge.** fusion-tea pins sysml-codegen at `8a758e9` (2026-08-19), which is 142 commits behind this branch's base. I verified this in fusion-tea `pyproject.toml:37` and sysml-codegen `git rev-list`. fusion-tea can only run the tools from the installed package after that pin moves, and moving it changes the code generator its packages are built with. So the item delivers four things:
   - the skill, the tools, the installer work, the neutral fixture and the tests in sysml-codegen;
   - a fusion-tea adoption runbook, in the shape of Item 2's runbook;
   - ledger rows;
   - any fusion-tea text that must exist before the ported text drops it. The orchestrator writes this on a fusion-tea branch.

   Epic criterion 3 ("fusion-tea's study suite passes with its copies replaced by wrappers or removed, and one existing study record re-verifies unchanged") becomes runbook verification. If you see a way to rehearse it inside the item, on a copy of fusion-tea, specify it. The orchestrator would run it, since stage agents cannot reach fusion-tea. Moving the pin is the owner's call.
2. **Artifacts live here.** The spec, design and plan go in sysml-codegen `.project/active/study-layer-to-codegen/`, not agentic-mbse as the epic's Deliverables say. The reason is that the code lands here and stage agents can only read this repo. The orchestrator adds the pointer and ledger rows in agentic-mbse.
3. **Installer mechanism is the design's call.** The design chooses between reusing agentic-mbse's `Installer` and a standalone sysml-codegen installer. The spec states the ownership requirement, not the mechanism. A small agentic-mbse change is allowed if the design picks reuse.
4. **teax stays an optional runtime dependency.** sysml-codegen does not depend on teax today, and teax is not on a package index. Tools that need it import it only when used, and fail with a clear message when it is missing.
5. **The neutral fixture starts from fusion-tea's `tests/study/data/synthetic_pkg`.** The design may replace it with a better one.

## Facts the orchestrator verified that the epic does not carry [AGENT, verified by orchestrator 2026-10-12]

- **fusion-tea uses the tools as a library, not only as scripts.** About 30 package scripts import `scripts.study.{common, manifest, identity, indicators, verify}`, and six `build.py` files import `scripts.integrate.rederived_census` (see `CONSUMER_SURFACE.md`). For fusion-tea's later switch to be a thin re-export, the moved package has to keep the public functions those imports use, with the same names and behaviour. This follows from "no loss of information" and the epic's "thin wrappers".
- **Committed study records name the old tool paths.** `record-template.md:369` records `tool.path` as `scripts/study/<tool>.py`, and 1338 committed record files in fusion-tea mention those paths. The epic's Out of Scope forbids changing committed records. The spec must say how a record reports tool identity after the move without making existing records fail to re-verify.
- **`integrate.py` is coupled to fusion-tea beyond what the epic lists.** Its gates run two fusion-tea repo tests: `tests/test_dependency_provenance.py` (`integrate.py:189`) and `tests/models/test_model_family_spines.py` (`:199`). It also imports `_by_entry_type` from the second (`:1161`). It uses `STOP_PARSER_TEAX_ROOT` and `TEAX_SIMKIT_SUBPATH`. `read_coverage.py:95` reads `STOP_PARSER_TEAX_ROOT` too. Making these general means the target declares its gates. The spec captures the requirement; the design picks the mechanism.
- **fusion-tea installs `run-study` for both Claude Code and Codex.** Its tracked `.agents/skills/run-study` is a link to `../../.claude/skills/run-study`. agentic-mbse's installer now installs every skill for both assistants. Replacing fusion-tea's local copies therefore needs both assistants covered.
- **sysml-codegen's `install-commands` does not work from a wheel today.** `get_commands_dir()` (`src/sysml_codegen/cli/__init__.py:59`) resolves `claude/commands/` at the source-checkout root. The wheel packages only `src/sysml_codegen`: the orchestrator built it, and `teax-completion.md` is absent from its 87 files. fusion-tea installs sysml-codegen from a git rev, so it gets a wheel. "Installs into a fresh target" must therefore hold when sysml-codegen is installed from a built wheel.
- **Baseline for this branch.** `uv run --env-file /home/reid/1cfe/sysml-codegen/.env pytest tests/` gives 2206 passed, 9 skipped, 1 failed. The failure is `tests/conformance/test_self_binding_guidance_contract.py::test_zero_unmarked_self_named_examples_across_all_trees`, which flags agentic-mbse's `project_templates/MODELING_PROCESS.md.template` through the `../agentic-mbse` path dependency. It predates this item and is not this item's to fix. syside needs that `--env-file` (the worktree has no `.env`).

## What a good spec does here

- Holds the bar at "a fresh target that uses sysml-codegen and teax gets a working study capability from `sysml-codegen install-commands`, with nothing borrowed from fusion-tea", not at "files copied".
- Grades every requirement by the capture-fidelity vocabulary: `[NEED]` for owner-stated, `[INFERRED]` for what you derive, `[INHERITED]` with its source.
- Keeps the success criteria checkable, each with how it is checked.
- Names the open questions the design must answer instead of answering them: installer mechanism, tool CLI shape, how gates become target-declared, how tool identity is recorded.
- Stays inside the epic's Out of Scope. The design-choice principle and the goal layer are Item 2's.

Do the half-hour import-repackaging check the epic calls for (`scripts.study` → a package import without the `scripts.` convention, with `manifest.repo_root()` and schema lookup). Do it on a scratch copy outside the staged sources, and record what you found in the spec.

Do not start background tasks. Finish with `ARTIFACT: <path>`. If something only the owner can answer blocks you, ask me instead of guessing.
