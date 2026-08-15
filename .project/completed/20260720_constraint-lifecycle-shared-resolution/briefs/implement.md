# Implement Brief — Lifecycle Item 2: Shared Producer Resolution and Gate A

**Stage:** implement (phases run in groups; orchestrator reviews between groups)
**Authority:** approved `spec.md` + `design.md` (rev 2, Approve-with-notes, round-2 record in
`design-review.md`) in `.project/active/constraint-lifecycle-shared-resolution/`. The design
contains the folded-in phased plan — there is no separate plan.md; check its phase boxes and
write implementation notes there.

## Ratified decisions (do not re-litigate)

- PC-1: `part_usage` owner branch in `prepare_constraint_usages` is an approved extension —
  existing branches byte-unchanged, Item 1's full acceptance + unit suites stay green.
- PC-2: backfill requirement stands on iteration-order basis, not D-1.
- PC-3/I10: V11 scope stays calculation-only; the widening question belongs to Item 3.
- Deletions = the four guess-among-candidates behaviors ONLY; deterministic unique-or-refuse
  forms survive as declared lenient-only key forms. `test_silent_failure_family3.py:73-86` is
  the declared migration, not collateral.
- D9's one QN rule is a Phase 1 de-risk pin BEFORE any cutover.
- Owner rulings: no LOC gates (qualitative deletion mandate); subagent/stage model cap Opus.

## Review notes to incorporate (from round 2 — small, mandatory)

1. D1: add one sentence acknowledging `resolution/` placement adds a second deferred edge
   (do not present the layer as clean).
2. Row 4: `manual_required = literal_default is None → MANUAL_REQUIRED` refusal flips
   compilability — add it to the design's forced-difference list up front.
3. Row 18 re-typing: add a test pin (the item7 tests route elsewhere).
4. I5: state and implement which consumer's default wins when two mint the same QN (PC-2
   showed it happens); make it deterministic and tested.

## Execution rules (Item 1 discipline carries over)

- Tests first per phase; RED on public fixtures before production edits where the design
  specifies acceptance shapes; never modify Item 1's frozen acceptance file or fixtures, nor
  any existing fixture/baseline byte (byte-identity gates: existing fixtures must survive the
  cutover unchanged except where the design's forced-difference list says otherwise — each
  forced difference gets its own justification and pin).
- Both the new part_usage branch and the surviving package branch need live fixture coverage
  (round-1 finding: zero exists today).
- No wrapper/flag/alias/route-adapter survives a cutover phase; delete in the same change set.
- Stop conditions in the design are binding; a contradicted bet stops the phase and reports.

## Environment (verified)

License: `set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a`. agentic-mbse checkout:
/home/reid/1cfe/agentic-mbse. TEAx lane: agentic-mbse venv + TEAX_SIMKIT_PATH per Item 1
evidence §3. Never ruff-format tests/fixtures or baseline_outputs. `.claude/projects/` is
user-owned — never touch. Preserve unrelated dirty files.
