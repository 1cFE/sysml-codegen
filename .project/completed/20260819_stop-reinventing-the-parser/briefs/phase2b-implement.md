# Brief — Phase 2b implement: land the shared unit primitive in Agentic

You are executing **Phase 2b only** of plan **Revision 4**. This phase reopens the Agentic tree
that Phase 2 closed, under an owner ruling, to fix one falsified premise: the unit operand of a
`[` annotation was validated as a feature reference, which is false for every compound unit
(`[kg/m^3]` is an `OperatorExpression`) and currently refuses the product's real corpus. Read in
order:

1. `.project/active/stop-reinventing-the-parser/plan.md` — **Revision 4**, your contract:
   "Phase 2b" (checklist + validation) and the Global Execution Contract's "Live implementation
   trees and the Agentic reopening" subsection.
2. `design.md` — **Revision 8** — `#one-total-inspection-operation` (the owner-verbatim opaque
   contract, the `unit_annotation_value` primitive, the arity ruling, "What this retires in the
   Phase-2 tree").
3. `run-records/phase3-stop-report.md` — the measured cause.
4. `run-records/phase2-audit.md` — the audited obligations you re-apply, and m3's closure that
   your landing re-bases on non-emission.

Provenance: the opaque-unit contract and the primitive's signature are **[OWNER]** rulings
(2026-08-18), encoded in design rev 8 with verbatim quotes — implement them exactly. The
wrong-arity outcome (raise the named refusal; `None` strictly means "not a `[` annotation") is
an [AGENT] ruling derived from the owner's verbatim "enforce exactly two operands", recorded in
the design. On any conflict, design rev 8 wins; surface conflicts, never resolve silently.

## Where you work [AGENT]

- Agentic worktree: `/tmp/stop-parser-rev2/worktrees/agentic-mbse` (branch
  `stop-parser-evidence-r2` at `68bca37`). The Phase-3-era read-only rule is superseded **for
  this phase only**. Verify clean at `68bca37` before starting.
- Docs checkout: `/home/reid/1cfe/sysml-codegen` — only the plan.md "Phase 2b completion"
  section update, committed as your final act.
- The Codegen worktree (`b4e97dd`) is read-only context. Touch nothing else; no user checkouts;
  no `/tmp/stop-parser.QVJIIP/*`.

## The work (plan rev 4 Phase 2b — binding; tests first)

1. **Tests first.** Retire (delete) the two superseded shape assertions design rev 8 names —
   the non-feature-reference refusal and the unresolved-unit-referent refusal pinned around
   `reference_use.py:316` and their kept tests — and write the owner's four coverage cases
   before production edits:
   - `[m]` — simple unit still accepted, value operand visited;
   - representative compound forms `[kg/m^3]` and `[W/(m·K)]` — the annotation is accepted and
     the unit operand neither traversed nor emitted (live licensed models);
   - wrong arity through a synthetic node — raises the named
     `SemanticEvidenceError(EXPRESSION_KIND_UNSUPPORTED)`, never returns `None`;
   - references in the **value** operand are still visited.
2. **The primitive:** `unit_annotation_value(expression) -> Any | None` — recognizes `[` from
   the mapped metatype, enforces exactly two operands (raising the named refusal), returns the
   value operand, leaves the unit operand opaque (never traverses, never emits, no unit-grammar
   validation of any kind). `None` strictly means "not a `[` annotation".
3. **`inspect_reference_uses` calls it** — one parser-shape owner; the never-emit rule and the
   arity refusal survive; nothing else about the inspection contract changes.
4. **Export it** on the boundary per the design's export list, so Codegen can call it in
   Phase 3.

## Validation (re-applied Phase-2 obligations — binding)

- Focused suites (`tests/test_sysml/`, ownership) green; scoped strict
  (`uv run mypy --strict src/agentic_mbse/errors.py src/agentic_mbse/sysml/reference_use.py`)
  zero; fast suite with license: expect exactly the 18-node optional-dep baseline plus nothing;
  repo-wide mypy/Ruff baselines unchanged (101 / 119 at `68bca37`); targeted Ruff clean on
  changed files.
- Wheel/extraction check at the same `0.1.3` / `semantic-evidence/v2` contract (no new version
  is minted — the artifact was never released; plan rev 4 records this). Extraction directory
  name must contain `agentic-mbse`.
- **[OWNER-VERBATIM]** "do not rerun the PDF suite anymore" — the slow PDF/HTML corpus and 15
  paid/network cases stay unrun.
- SysIDE license: `set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a`; never copy a
  secret anywhere.

## Deliverables

1. Commits on `stop-parser-evidence-r2` on top of `68bca37`, tests-first then production, in
   reviewable units.
2. Every Phase 2b validation box executed with commands and results recorded.
3. plan.md "Phase 2b completion" section filled and committed in the docs checkout.
4. Final message: prose summary — what was retired, the primitive's contract as landed, the
   four coverage cases' results, gates — ending with
   `ARTIFACT: .project/active/stop-reinventing-the-parser/plan.md`. If a stop rule trips or a
   design conflict appears, say so plainly at the top and stop.

Phase 2b is the end of your scope. The Phase 2 audit addendum and Phase 3 are separate stages;
do not start them.
