# Brief — Targeted design amendment: Revision 7

You are amending an existing, approved technical design. This is a **targeted amendment**, not a
redesign. Read first, in order:

1. `.project/active/stop-reinventing-the-parser/run-records/phase1-stop-report.md` — the complete
   evidence record driving this amendment. Every claim marked [verified] was reproduced by the
   orchestrator; treat those as established facts. The seven rulings at the bottom are
   **owner-ratified (2026-08-17)** and binding on this amendment.
2. `.project/active/stop-reinventing-the-parser/design.md` — Revision 6, review verdict Approve.
   You are producing Revision 7.
3. `.project/active/stop-reinventing-the-parser/plan.md` — rev 2, so you know what downstream
   consumes your anchors. Do not edit the plan; a separate plan revision follows.

For fact-checking, a clean read-only worktree at `C_base` exists:
`/tmp/stop-parser-rev2/worktrees/sysml-codegen` (branch `stop-parser-impl-r2`, commit `78a9beb9…`).
Key files: `verification/capture_baseline.py`, `verification/expected-transitions.md`,
`verification/probe-fixture-lock.json`, `src/sysml_codegen/extraction/source_evidence.py`.
Do not modify that worktree. Probe models: `/tmp/stop-parser-rev2/scratch/`.

## What Revision 7 must change — exactly these five areas

1. **Lock and inventory semantics** (`#probe-fixture-commit-lock`, `#closed-fixture-inventory`):
   replace the byte-identity-in-current-tree rule ("Any changed byte invalidates the verdicts")
   with the implemented contract: the `43edf9bd` lock is verified against its **own historical
   tree**; current outputs are validated through the transition-ledger machinery
   (`capture_baseline.py`: frozen `P_seed` reconstruction from Git, `validate_current_batch`,
   `validate_output_transitions`). Preserve the lock unchanged — never re-derive it (ruling 2).
   State frozen counts (15 graph / 22 refusals, `bd7bf245…` at `P_seed`) versus current counts
   (14 / 23, `7f926978…`) explicitly, each labeled with its state. Add the missing committed
   check: a test that verifies the lock against its historical tree (today that check exists only
   as a hand-run; Phase 1 must add it as a kept test).
2. **Current code facts** (`#current-code-facts`): correct the escape-trigger description to the
   verified mechanism — the preflight screens only calc-usage in-direction bindings
   (`screen_source_readiness` over `usage.bindings`); a bare computed-attribute initializer
   becomes a typed alias outside that population; alias resolution drops the index's role;
   singular slot → silent occurrence-zero binding (any authored index, in range or not); plural
   slot → incidental `SI_OCCURRENCE_AMBIGUOUS`. Operator-wrapped forms refuse correctly today.
3. **Test design for the indexed red set** (ruling 6): both cases are required kept tests —
   `Cell[1]` out-of-range bare chain proving silent rewriting (zero-diagnostic graph at `C_base`),
   and `Cell[3]` bare chain proving inventory refusal must **precede** occurrence-ambiguity
   (`SI_OCCURRENCE_AMBIGUOUS → SI_INDEXED_SOURCE_UNSUPPORTED` transition). State the
   inventory-before-occurrence ordering as a design decision and add the diagnostic transition to
   the ledger obligations so Phase 4 reconciliation expects it (amendment area 5 of the stop
   report).
4. **`deep_cross_scope` ruling** (rulings 4-5): record graph→refusal as intended tightening —
   the old capture was a caller-supplied-substitute mis-wire (evidence in the stop report); the
   old graph must never be restored. Add to the documentation/backlog obligations: file exact
   deep qualified-output wiring as a separately owned capability, and fix the fixture's stale
   comment ("Exact projection wires this input to the one concrete core output") so it states the
   current refusal contract and points at the owned follow-up.
5. **Revision base statement** (`#revision-6-implementation-base`): keep `C_base`/`A_base`
   unchanged (ruling 1). Correct any prose implying the current tree must byte-match `P_seed`
   evidence.

## Hard constraints

- Do not touch the approved mechanism: D1-D10 decisions, the closed-variant architecture, the
  artifact chain, the acyclic topology, the consumer/ownership manifests. If an amendment area
  seems to require a mechanism change, stop and surface it instead of making it.
- Preserve existing section anchors — the plan links to them. New content goes under existing
  headings or clearly-marked new subsections.
- Update the design's revision header/history to Revision 7 with a short amendment note naming
  the stop report as its evidence source.
- No code, fixture, or verification-file edits anywhere. design.md only.
- Do not weaken any obligation: the amendment corrects false factual claims and adds the ratified
  rulings; every closure requirement from Revision 6 stays as strong or stronger.

## Deliverable

Edit `.project/active/stop-reinventing-the-parser/design.md` in place (docs checkout,
`/home/reid/1cfe/sysml-codegen`). Do not commit — the orchestrator reviews and commits. Final
message: a prose summary of exactly what changed per amendment area, any place you had to deviate
from this brief and why, ending with
`ARTIFACT: .project/active/stop-reinventing-the-parser/design.md`.
