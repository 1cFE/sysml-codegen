Design EXEC-SUBSET-CONTRACT Item 2b, live half (`subset-profile-screen`, sysml-codegen, branch `subset-profile-screen`). Agentic-mbse sibling worktree: `/home/reid/src/subset-conformance/agentic-mbse` (a change to its `src/agentic_mbse/sysml/` or `errors.py` needs a gate rerun and new receipt, so prefer designs that don't need one; say so if yours does).

Read: `.project/active/subset-profile-screen/spec.md` (revision 3), `spec-review.md`, `product-lens.md`, `briefs/align.md`, `spike-snapshot/FINDINGS.md`. 2a's design for the adapters and receipts: `git show c381fb00:.project/active/subset-profile-conformance/design.md`.

Intent, graded:
- [OWNER-ratified 2026-10-20] The generator's own route alone decides whether `generate` and `check` refuse. The shared screen only adds findings to the report. No new refusal on any route keyed on the screen, its version or its failure.
- [OWNER] RG-1/RG-2/RG-3 stay with the owner. Anything that would change what the generator accepts or refuses is parked for the owner, not designed in.
- [ORCHESTRATOR] What the modeler gets: one command that tells them, before anything is written, whether `generate` will build their model, every reason it won't, and every screen finding, honestly marked where something could not be assessed. `generate` reports the same findings in the same form.
- [ORCHESTRATOR ruling] Snapshot carriage is split out. 2b keeps v6; replay marks the screen not assessed.

Engineering bar — this matters most. 2b is a refactor straight through `cli/__init__.py`'s generate flow and `orchestration/elaborated_pipeline.py` (whose refusal converters rebuild objects field by field and drop new fields silently). I want:
- one read-only preparation function (or small object) with a clear typed result that both commands call, not `check` as a copy of `generate` with writes skipped, and not flags threaded through the existing function;
- destination mutation and emission clearly outside it, so "check writes nothing" holds by structure, with sentinel tests as the proof rather than the only guard;
- the report model (generator outcome, screen findings, not-assessed entries, disagreements) as one type that both CLIs render, so "same form" is structural;
- the smallest move for the one late refusal (`PARAM_FIELD_COLLISION`), following the `_preflight_registry_class_names` precedent, unless you find a reason it isn't enough;
- no speculative abstraction for the snapshot half; leave a clean seam, nothing more.
Read the real code before deciding. If the current generate flow resists clean factoring somewhere, say where and what it costs, rather than papering over it.

Settle every spec Open Question that is the design's to settle (the `check` CLI shape and exit codes, how a `SubsetDiagnostic` joins a generator refusal, omission/exclusion readiness, which lanes the parity evidence runs, the version-bump question). Record any decision that touches owner territory as parked for the owner.

Re-run the product lens on the design, as your command describes. Write `.project/active/subset-profile-screen/design.md`.
