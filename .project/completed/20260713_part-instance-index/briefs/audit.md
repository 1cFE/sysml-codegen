# Brief: Item 4 audit — Part-Instance Index

You are a fresh audit session in the orchestrated CONSTRAINT-EXEC epic run. Repo: sysml-codegen, branch `constraint-exec-epic`. You did not implement this; audit it.

## Process constraints
- Work synchronously; never pause for background agents.
- Do NOT run `git commit` — the orchestrator commits.
- Artifact: `audit.md` in `.project/active/part-instance-index/`.
- Attempt execution first; if the sandbox blocks a gate/mutation, write a "Requested live probes" section (exact command / file:line mutation + expected RED/GREEN) for the orchestrator to run and append.

## Audit target
The three Item 4 phase commits against `spec.md`, `design.md` (rev 2), `plan.md` (+ Implementation Notes), and `b1-probe-evidence.md`.

## Priority finding to adjudicate — the `all_occurrences()` swallow
The implementer deviated: `all_occurrences()` catches `NonFiniteCardinalityError` per-definition (bulk-dump convenience) while `occurrences_of(owner)` raises. Adjudicate against Design Principle 5 (silence is never an outcome) and the epic's "non-finite blocks with a named diagnostic": if Item 5's lowering were to iterate via `all_occurrences()`, would a constraint-owning definition with a blocked multiplicity be silently skipped? If yes, this is a real defect in waiting — require a cure (e.g. bulk API returns blocked defs explicitly beside occurrences, or is removed/renamed to make the swallow impossible to misuse). Check what the design actually specified for the API surface.

## Also verify (by execution where possible)
1. Classifier truth table vs `b1-probe-evidence.md` — all 8 rows, including the FeatureReferenceExpression (parameterized) block despite non-None cached bounds.
2. The 9/9 oracle + collision + Cartesian + determinism live tests: run them (plan has the commands; the implementer reports the plain venv is licensed — verify, else use the sibling-env form).
3. Additive gate: no production module imports the new one (grep), suite 2161/4, mypy 77 baseline, ruff.
4. Success-criteria walk with evidence per item; call out any unproven claim.

Verdict: Certify / Certify-with-notes / Fail.
