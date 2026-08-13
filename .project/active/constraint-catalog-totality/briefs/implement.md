# Stage brief: implement — CONSTRAINT-SEMANTICS Item 2 (Canonical Usage Domain and Catalog Totality)

Work in `/home/reid/1cfe/sysml-codegen-item7-rebuild` (branch `item7-rebuild`). Companion changes
(Phase 4C) go in `/home/reid/1cfe/agentic-mbse-item7-rebuild` (same-named branch; the editable
install reads that worktree). You run with bypass permissions; both trees are yours to edit.

**Execute the plan:** `.project/active/constraint-catalog-totality/plan.md` — phase by phase, in
order, checking off items as you complete them and adding per-phase completion notes (what
changed, issues, deviations) so a resumed session picks up where you stopped. The design
(`design.md`, rev 3) is your architecture authority; the spec (`spec.md`) carries the success
criteria; deviations from the design are recorded in the plan notes with reasons, and anything
that contradicts a design premise is surfaced, not silently absorbed.

## Non-negotiables (from spec/design/plan — enforce on yourself)

- **Phase gates are real:** do not start a phase until the previous phase's gate is green.
  Documentation corrections and expected outputs land BEFORE confirmation tests run.
- **Frozen twins:** `catf_mfe_model` and `catf_mfe_d5` constraint syntax untouched;
  `catf_mfe_d5` must end with exactly 65 usage carriers, 9 eligible, and still generate.
- **One authority:** no parallel inventory; the expectation files are test-side oracles only.
- **Identity end to end:** `declaration_id` joins domain ↔ occurrence nodes ↔ catalog records;
  no QN string matching in any join.
- **Minting never raises, for any form.** The form gate runs before any predicate walk.
- **Licensed runs:** `set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a` (the `.env` lives
  in the main agentic-mbse checkout, NOT the worktree); a licensed run is proven by zero
  `no live syside license` skip lines, never by pass counts.
- **Recapture protocol:** the single reviewed recapture is the LAST fixture-committing step;
  review = timestamp-only diff check, revert untouched fixtures. Never ruff-format fixtures,
  baselines, or generated files.
- **Phase 4C ordering (PD4):** the companion severity-map entry and schema-version bump land in
  the same window as codegen's pin move — the codegen suite is red in between; keep that window
  inside the phase, both suites green at its gate.
- **Zero-new gates:** `ruff check src` and mypy stay at or below their recorded baselines in both
  repos; new code is clean.

## Commit discipline

Commit per phase (or tighter), in the repo the phase touches, message subject leading with the
phase and the decision. Do not push. Do not touch `main`. The four `all_satisfied` assertions in
`tests/execution/` stay untouched (Item 3's).

## Deliverable at the end

`.project/active/constraint-catalog-totality/verification.md` — the final gate evidence with
exact counts: focused tests, full licensed codegen suite, full companion suite (in the companion
worktree), ruff/mypy zero-new in both repos, fixture diff review record (timestamp-churn
protocol), `git diff --check` both repos, the 65/9 catf_mfe_d5 counts, oracle coverage count,
and the recapture record (fixture count at execution). Note anything left open honestly.

If you run out of time or context mid-plan, stop at a phase boundary with the plan checkboxes
and notes current — the orchestrator will resume the session. Finish with `ARTIFACT: <path>`
(verification.md, or the plan if stopping early) as the last line.
