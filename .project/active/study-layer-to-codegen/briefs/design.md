# Brief: design — study-layer-to-codegen (WRAP-SPLIT Item 3)

Sent by the orchestrator (agentic-mbse `/_my_orchestrate` run, 2026-10-12) to `/_my_design`. Write the design at `.project/active/study-layer-to-codegen/design.md`.

## Input

- **The contract.** `.project/active/study-layer-to-codegen/spec.md` (approved for design at `a09bdb1`). Read all of it. Twelve criteria. The closed list B1–B11 of what the move may change. Decisions D6–D11 are settled; do not reopen them. Open questions OQ1–OQ9 and OQ11–OQ14 are yours to answer. OQ10 is closed by D6.
- **The review behind it.** `spec-review.md`, and the briefs in `briefs/`.
- **Staged sources** (gitignored, read-only) in `.orchestrate-logs/src/`:
  - fusion-tea `@b06585709`: the study layer, `CONSUMER_SURFACE.md`, and the new `CONSUMER_ATTRIBUTES.md`. The latter holds three things: every module attribute fusion-tea uses (SC6 and D9's compatibility tier); the 17 generated package names and 20 root key prefixes (SC5's closed lists); and one committed record's tool-bearing documents under `exploration/stellarator_e2e/studies/20260916-primary-loop-sizing/` (SC7's pre-move fixture).
  - agentic-mbse `@main`: the installer (`src/agentic_mbse/cli/installation.py`), its `CLAUDE.md`, the epic, and Item 2's design and runbook.
- **The repackaging check.** `.orchestrate-logs/scratch/repack-check/{check.py,output.txt}`. You may extend it on scratch copies to settle a design question by measurement.

## What the orchestrator expects

**Engineering quality is the bar, not "it runs".** This code becomes sysml-codegen's supported study package and a public API for other targets.
- Design a clean package. Pick its name and layout deliberately, and justify them against this repo's conventions (`CLAUDE.md`, `src/sysml_codegen/` structure).
- One root concept, done once: a project root and a tool home, not scattered `Path.cwd()` calls.
- Typed public functions under this repo's strict mypy.
- Tests in this repo's lanes.
- Where the original code has a smell the spec lets you keep, for example the `if __package__` path inserts, say whether it goes or stays, and why.

**Answer every open question with a decision, the alternatives you rejected, and the reason.** Make the design concrete enough that the plan stage doesn't redesign anything. Name modules, functions, file paths, the gate-declaration format with an example, the CLI surface with example invocations, and the installer's on-disk layout in a target.

**Installer (OQ1).**
- The orchestrator leans toward reusing agentic-mbse's `Installer`. sysml-codegen should not grow a second implementation of the same ownership rules.
- Each installer should keep its own manifest, so neither can mistake the other's files for retired ones. A small public API change in agentic-mbse is allowed: for example, a manifest-path parameter, or a function for installing a skill bundle from another source tree.
- If you choose reuse, specify that agentic-mbse change exactly: file, signature and tests. Also specify the version and dependency-bound change. agentic-mbse is `0.1.3` at `main` and at fusion-tea's pin, so the bound can't guarantee the API exists today. And say what fusion-tea's agentic-mbse pin then needs.
- If reuse turns out to couple sysml-codegen to agentic-mbse internals, a standalone installer is acceptable, with three conditions: it uses the same on-disk layout as agentic-mbse's skills (`.agents/skills/<name>` plus the Claude alias), the same ownership semantics, and you state the rejected reuse with the reason.
- Either way: the policy template is a project document (created once, preserved on re-install). `teax-completion` keeps installing. Installation works from a wheel (SC1).

**The fixture (OQ9).** It decides how much of SC3, SC4 and SC12 is reachable. Prefer a neutral package this repo's generator produces from a small SysML model, the way existing fixtures are made, over hand-extending `synthetic_pkg`, if that makes `verify` and the `integrate` paths reachable. Size it honestly against the estimate. Cut 2 (integrate `CANDIDATE`) is available if the plan needs it, so don't let the fixture balloon.

**SC12's parity script.** Design it now, not at plan time: which inputs, which tools, how the original fusion-tea copy runs (the staged copy in a scratch fusion-tea layout), and how the closed-list fields are masked.

**The fusion-tea runbook (SC9).** Design its steps and the rehearsal. The orchestrator runs the rehearsal on a disposable fusion-tea copy, because stage agents can't reach fusion-tea. So specify the rehearsal as commands the orchestrator can run, with expected observations.

**The ported text (SC5, SC10).** Specify the porting approach for `SKILL.md`, the runbook, the record template, the policy template and `integrate`'s operator guide. Also specify the read-through record's format, and how its moved-line verdicts become ledger rows. The ledger is in agentic-mbse (staged copy at `.orchestrate-logs/src/agentic-mbse@main/.project/active/wrap-split-migration-ledger.md`); read Item 2's section for the row format. The orchestrator appends the rows.

Run the product-lens if `/_my_design` calls for it. Use its fallback if you can't reach its files.

Do not commit. Do not start background tasks. If something only the owner can answer blocks you, ask me. Finish with `ARTIFACT: <path>`.
