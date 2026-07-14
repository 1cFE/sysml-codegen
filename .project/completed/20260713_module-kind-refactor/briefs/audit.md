# Brief: Item 6 audit — module_kind Refactor

You are a fresh audit session in the orchestrated CONSTRAINT-EXEC epic run. Repo: sysml-codegen, branch `constraint-exec-epic`. You did not implement this; audit it against the written artifacts.

## Process constraints
- Work synchronously; never pause for background agents.
- Do NOT run `git commit` — the orchestrator commits.
- Artifact: `audit.md` in `.project/active/module-kind-refactor/`.
- You have execution: run the gates yourself, do not trust recorded outcomes.

## Audit target
Implementation commits `a4319e8..58ce68f` (six phases) against `spec.md` (review-revised), `design.md` (review-revised), `plan.md` (with Implementation Notes).

## What to verify by execution, not by reading
1. **The four final gates**: repo-wide zero-hit grep for `is_computed_attribute`/`is_aggregation`; full suite; ruff; conformance byte-identity. Run them.
2. **Fail-loud contract**: the seven seam-entry tests exist and fail when the guard is deleted (pick ONE seam, mutate the guard out, confirm RED, revert, confirm GREEN — record the mutation).
3. **Baseline diff shape**: `git show f867aed` (or diff the baseline regen commit) — confirm the computation_graph.json changes are exactly the two-out/two-in-plus-null swap at the ordered position, nothing else.
4. **The two deviations** (deleted tests; ModuleKind docstring): check each against the spec's requirements — is any spec-required behavior now untested? The "both flags true" state being unconstructible is a claim about the enum; verify no code path can still express the ambiguity.
5. **Success criteria walk**: every spec success criterion checked or named unmet, with evidence per item.

Verdict: Certify / Certify-with-notes / Fail, with a findings table. If you find placeholder code, silent scope cuts, or unproven claims recorded as proven, say so plainly.

## Execution fallback
If the sandbox blocks you from running a gate or mutation, do NOT downgrade the verdict to code-trace-only silently: write a "Requested live probes" section listing each exact command / file:line mutation with its expected RED/GREEN outcome. The orchestrator (full permissions) will run each, record results, and append an addendum. Attempt execution first — pytest and read-only commands usually work.
