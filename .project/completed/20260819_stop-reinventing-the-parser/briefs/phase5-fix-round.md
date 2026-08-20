# Brief — Phase 5 audit fix round: make provenance a boundary property, re-mint the chain

The item-level independent audit returned **Needs Work**
(`.project/active/stop-reinventing-the-parser/audit.md`, committed at `e861acd`) against the
sealed Phase 5 chain. The findings are production defects, so per the plan's stop rule the old
identities (`C_prod` `707346d`, `F_final` `2243b7ce`, `C_evidence` `a184133`) are **invalid**
and a new dependent chain must be minted after the fixes. Your job: close the four blocking
findings at their root, land the disposal-grade follow-ups, re-run the affected phase gates,
re-mint the artifact chain through the committed runner, and hand back to the independent
auditor. Read in order:

1. `audit.md` — the verdict: four blocking findings with mechanisms and probe models, six
   DISPOSE-grade follow-ups, and what already holds (do not re-litigate the confirmed parts).
2. `plan.md` — Revision 4: Phase 5's stop rule and completion record; Phase 4's closure block
   (its rollback rule now fires: affected Phase 4 gates rerun).
3. `design.md` — Revision 8: `#d7-one-codegen-conversion-boundary` (the single public
   conversion — the seam finding 2 says is not total), `#one-total-inspection-operation` (the
   `sum` bullet), `#d8-diagnostic-ownership`, bet **B6** (the finding-3 obligation), and the
   evidence/public-boundary matrix.
4. `run-records/phase2-audit.md` — the Agentic obligations that re-apply when that tree
   reopens.

Owner rulings for this round **[OWNER, 2026-08-18, this session]**: fix the refusal *class*,
do not add function support — "supporting `min`/`max` serves zero existing models and would
not discharge the finding" (measured: no fixture or fusion-tea model uses
`max`/`min`/`abs`/`sqrt`/`floor`/`ceil`). File function support as a separately-owned
capability backlog row instead. `sum` must be identified by its exact library declaration, not
its name — ratified as part of this direction.

## Trees, identities, and the chain reset

- **Codegen:** `/tmp/stop-parser-rev2/worktrees/sysml-codegen`, branch `stop-parser-impl-r2`,
  currently at `a184133` (`C_evidence`). **Do not build on `C_evidence`** — its evidence files
  must never enter a production tree. First acts:
  `git branch evidence-chain-r1 a184133` (preservation ref for the invalidated chain), then
  move the branch to `C_prod`: `git reset --hard 707346d` (this dedicated worktree only —
  never any user checkout). Fix commits go on top of `707346d`; the sequence ends in a new
  `C_prod-r2`.
- **Agentic:** `/tmp/stop-parser-rev2/worktrees/agentic-mbse`, branch
  `stop-parser-evidence-r2` at `3f8bd58` (`A_final`). Reopened **for this round only** —
  finding 1's sum-identification defect lives at `src/agentic_mbse/sysml/reference_use.py:363`.
  Fix commits on top produce a new `A_final-r2`; every Phase-2 audited obligation re-applies
  to the landing (scoped strict zero, focused suites, fast-suite 18-node baseline, wheel check
  at `0.1.3` / `semantic-evidence/v2`).
- **Docs checkout** `/home/reid/1cfe/sysml-codegen`: records + plan updates, committed as your
  final act. Fusion/TEAx/1costingfe: same frozen pins as before, dedicated extractions only,
  user checkouts untouched. Nothing pushed anywhere.

## The four blocking fixes (tests first, at the root, in this order)

1. **F1a — unsupported invocations refuse pre-graph, with provenance.** Reproduction (kept
   test material): `floor_cost : Real = max(cell.capital_cost, 1.0)` with
   `NumericalFunctions` imported currently survives acquisition and dies at graph projection
   as `SI_SNAPSHOT_INVALID: unsupported invocation survived on '<internal name>'` — no
   authored reference, no `file:line`, model-blaming code. Required: the evidence
   inventory/acquisition refuses **any invocation whose function is not the supported `sum`**
   before any consumer or graph construction, with the authored expression, root-relative
   `file:line`, and a source-vocabulary code (`C_base` used
   `SI_EXPRESSION_SOURCE_UNSUPPORTED`; follow design D8's code ownership). Where the refusal
   lives (Agentic acquisition vs Codegen inventory) follows the design's boundary split —
   measure, decide, and record; surface if the design genuinely doesn't settle it.
2. **F1b — `sum` identified by declaration, not name.** Replace the
   `getattr(function, "name", None) == "sum"` test with identification against the exact
   standard-library declaration (the same mapped-metatype/exact-referent currency as the rest
   of the boundary). A user-defined `calc def sum` must NOT get plural semantics — kept test.
   Record the design's one-sentence tightening (the D5 `sum` bullet now states declaration
   identity) as a dated owner-ratified correction note in design.md, rev-8 style — not a new
   revision cycle.
3. **F2 — the D7 seam becomes total.** Every failure crossing the public boundary — CLI and
   API, live/admitted/capture, `--models` and `--from-snapshot` — carries code, authored
   reference or nearest authored context, root-relative `file:line`, and cause chain; **no
   route can exit with a raw Python traceback.** Fix at the single conversion seam, not
   per-shape. Kept tests: the audit's four provenance-dropping shapes plus the two committed
   fixtures that crash today (`anonymous_return`, `zero_output_calc`) — each asserts the full
   public contract. Add a seam-level catch-any test (a planted internal failure must exit as
   a formed diagnostic, never a traceback).
4. **F3 — complete B6.** The extractor still resolves types through the unqualified table;
   read design B6 and the audit's finding, finish the qualified route, delete the unqualified
   table read, kept test that a name-collision model resolves exactly. If B6's full closure is
   genuinely larger than this item, surface the boundary with evidence — do not quietly
   descope.

Then: **F4 — reconciliation ledger** gets its A/B and disposition columns and the three
mis-cited rows corrected (record fix, no code). Land the six DISPOSE-grade follow-ups exactly
as `audit.md` disposes them. File the new backlog row **[SCALAR-FUNCTION-VOCABULARY]** (owner
decision above): supporting `min`/`max`/other scalar functions is a separately-owned
capability; today they refuse by name via F1a; row names the refusal code and this decision's
date.

## Re-running the affected gates (in dependency order)

1. Agentic landing: Phase-2 obligation battery from a clean extraction; then a short
   **Phase 2 audit addendum** is owed — record the evidence in the phase record for the
   auditor who follows.
2. Codegen: the Phase 3/4 gates the fixes touch — focused natural-route + registry suites,
   static closure, D1-D4, occurrence byte-identity, baseline/transition reconciliation, full
   default suite from a fresh declared extraction. Every figure recomputable from a recorded
   command.
3. **Re-mint the chain:** rerun Phase 5 end-to-end through the committed runner — all 21
   lanes, no unexpected skips, new archives/wheels/hashes, new `A_final-r2` / `C_prod-r2` /
   `F_final-r2` / `C_evidence-r2` with the same topology proofs (evidence child direct on the
   new `C_prod`, exactly six files, mechanical auditor all groups green). The runner writes
   all evidence; hand-run results don't count. Update the product-lens append to the new
   identity.
4. Update plan.md: Phase 5 completion superseded-identities note (old chain invalidated, SHAs
   + preservation ref), new identities table, and the fix-round record. Do not rewrite the
   historical audit verdict.

## Standing constraints (all still binding)

License via `set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a`; never copy a secret.
**[OWNER-VERBATIM]** "do not rerun the PDF suite anymore." `deep_cross_scope_probe` graph
restoration is the global stop condition. No compatibility surface for anything removed.
Extraction-lane requirements (`STOP_PARSER_ARTIFACT_SOURCE_INPUTS`, Agentic sibling layout,
`agentic-mbse` in Agentic paths). Mutation-check the new kept tests — a test that cannot fail
is a finding class this item has produced three times. Tests first in both repos. Do not
self-certify; the independent auditor re-attacks the new chain after you.

## Deliverables

1. Commits: Agentic fix sequence → `A_final-r2`; Codegen fix sequence from `707346d` →
   `C_prod-r2` → `C_evidence-r2` (only child); `F_final-r2` in the dedicated Fusion worktree;
   `evidence-chain-r1` preservation ref in place. Nothing pushed.
2. All gate reruns and the 21-lane runner output recorded with recomputable commands and
   counts.
3. plan.md, design.md correction note, ledger, backlog rows, product-lens — updated and
   committed in the docs checkout.
4. Final message: prose — each finding's closure with its kill evidence, the new identity
   table, lane results, deviations — ending with
   `ARTIFACT: .project/active/stop-reinventing-the-parser/plan.md`. Any stop rule or design
   conflict: say so plainly at the top and stop.
