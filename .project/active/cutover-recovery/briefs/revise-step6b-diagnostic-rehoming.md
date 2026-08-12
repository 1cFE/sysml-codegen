# Stage brief — REVISE step 6b: re-home REQ-DIAG-02/03 on the exact route

**You are resolving the rule-10 surfacing from the retirement stage** (plan: "Revise step 6"
notes; `.project/active/cutover-recovery/plan.md`). Read first: the retirement stage note's
surfacing, `docs/architecture/reference/30-diagnostic-severity.md` (REQ-DIAG-02/03 and the
severity contract), ledger row L-023, and the orchestrator's measurements below.

Work synchronously. Never pause for background agents; finish or stop with questions.

## The measured facts (orchestrator, 2026-08-12 — re-verify, don't trust)

1. `analysis/diagnostic_screen.py` has zero callers; its only two ever were the deleted
   legacy builders. L-023's `unreachability: "live on the exact route"` is false — the exact
   route NEVER called it. The gap therefore predates the retirement: the shipped public
   route has behaved this way since the Phase 3 authority switch.
2. On the exact route, `build_elaborated_pipeline([tests/fixtures/non_finite_literal])`
   fails with a bare `ValueError: Out of range float values are not JSON compliant: inf`
   from serialization — generation halts by ACCIDENT, with a message naming nothing. On the
   public CLI that `ValueError` is swallowed by the broad catch at `cli/__init__.py:1133`
   (the audit's "silent unexpected-failure fallback" finding — same seam, same defect
   class).
3. The data the screen used to read still flows: `IdentifiedConstraintFacts.diagnostics`
   carries `ExtractionDiagnosticFact` with writer-set `DiagnosticSeverity`
   (`agentic-mbse constraint_facts.py:244`, severity at `:230-233`); nothing on the exact
   route reads it.

## The authority

REQ-DIAG-02: "A blocking diagnostic halts generation before lowering, on both the live and
snapshot routes, naming every blocking diagnostic." REQ-DIAG-03: "An advisory diagnostic is
rendered and generation continues; advisory rendering cannot swallow the blocking halt."
These are Active recorded requirements (CONSTRAINT-EXEC Item 4, merged main). Re-implementing
them on the shipping route is executing recorded authority, not a new decision. The doc's
discharge citations point at the deleted screen and must be re-cited to the new mechanism.

## Worklist

1. **Screen the identified diagnostics at the elaboration boundary.** Where elaboration
   consumes `extract_identified_constraint_facts(...)`, read `facts.diagnostics`; if any
   carries `DiagnosticSeverity.BLOCKING`, raise the exact route's typed elaboration error
   naming EVERY blocking diagnostic (kind + message + location, matching the retired
   screen's naming bar); log advisories first so the halt cannot swallow them. The halt
   must run before any snapshot/graph serialization so both live and snapshot routes get it
   (capture goes through elaboration — verify that claim and cite it).
2. **Pin it, both routes.** The `non_finite_literal` fixture exists. Add kept conformance
   nodes: live route refuses typed (assert the diagnostic kind and location appear; assert
   it is NOT a bare ValueError), capture refuses typed the same way, and — if cheap — an
   advisory-kind synthetic test proving the continue path (the severity table currently has
   only the one BLOCKING kind; if an advisory pin needs machinery the tree doesn't have,
   state that in the note instead of building scaffolding).
3. **Delete `analysis/diagnostic_screen.py`** with its recorded disposition: amend L-023
   with the measurement (correction by amendment, not appending), disposition migrate →
   delete, the new mechanism named as the replacement, the false unreachability claim
   corrected. Mint/adjust rows only as `check_paths` allows; cite the retirement stage
   surfacing + this brief as authority.
4. **Re-cite doc 30**: the REQ-DIAG-02/03 discharge rows point at the new mechanism with
   real file:line citations; note the history (screen retired with the v5 builders; the
   requirement re-homed at the elaboration boundary) in one line, not a narrative.
5. **Narrow the CLI catch-all** (`cli/__init__.py:1133`, audit code-integrity): catch the
   named operational refusals (the typed elaboration/snapshot/source-admission errors) and
   let programming defects propagate to the CLI boundary. Make partial-output cleanup
   explicit if the current behavior mutates output before failing — measure first. Keep the
   change minimal; the audit finding is the scope.
6. **Archive the stale probe** [orchestrator ruling on retirement surfacing 2]:
   `scripts/probes/probe_constraint_profile_qualifier_drop.py` moves under
   `scripts/archive/` with a one-line header note that its legacy column became
   unexecutable at the retirement (it is committed evidence, not live tooling). If ruff
   findings move as a result, record the delta.

## Boundaries

- Do NOT touch the R8/qualifier area (`elaborate.py` input naming, `SI_RENDERING_COLLISION`
  pins) — R8 is owner-blocked.
- Do not modify the accepted batch, corpus fixtures, or sealed snapshots.
- Rule 10 stands.

## Environment

As prior stages (venv assert first, license, PATH). Post-retirement clean numbers at
codegen `46ad549` / agentic `3fbda2f`: licensed suite **1701 / 34 / 65**, exec lane **65**,
`--verify` 15/22/0, `-k corpus` 9, ruff src **14** / tree 643, mypy **57 in 11**, paths
304/0, surface 0, groups all-affected-0, proof 0/0, replacements 221/81/0, runbook patches
green. (Ruff note: the open owner question on the pre-existing findings is NOT this stage's
to resolve; no new findings, and record any deltas from deletions/moves.)

## Battery before commit

Full licensed suite (delta named), exec lane, `--verify`, ruff/mypy with deltas explained,
`git diff --check`, ledger paths/surface/groups + `check_proof_integrity.py`,
`test_runbook_patches.py` if patches are affected. One or two commits (product + record is a
fine split); plan stage note updated.

## Report back

The new mechanism (file:line), the refusal message shape for the fixture on both routes, the
CLI catch-all change, nodes added (named), L-023's amended row, doc-30 citations, battery
numbers, commit OIDs. Any rule-10 surfacing. `ARTIFACT:` the updated plan.
