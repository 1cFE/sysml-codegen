# Brief: Phase 5 — corpus adjudication and certification

Sent to an `implement` stage session by the orchestrator.

## Work item

`plan.md` Phase 5, every checkbox. The plan is the contract.

Re-derive the full affected surface **from the shipped resolver**, adjudicate every difference, run
the project quality checks, and prepare the bounded documentation obligation for close.

## Intent this serves (provenance marked)

- `[OWNER-VERBATIM, 2026-08-13]` The product seeks a design search where engineering design
  parameters can be freely varied and viability and outcomes such as LCOE can be assessed, without
  embedding engineering logic by predetermining free variables and backing into the rest.
- `[INHERITED: plan.md Phase 5 / design D8]` **Predictions are not acceptance evidence.** Capture
  what the shipped resolver actually does and adjudicate the difference against the frozen
  before-state. Zero unadjudicated rows.

## What earlier phases established — do not re-derive

**[AGENT — orchestrator, from `85f598a`, `98970c9`, `a3b46dc`]**

- Frozen before-state and the Phase-3 after-state are in `verification/` — start at its `README.md`.
- Corpus moved at exactly **5** sites (u4, u5, u7's two inputs repaired from diagnostic to typed
  edge; u6's silent edge moved to `comp_a`'s occurrence at the same slot). Ledger went 405 edge + 4
  diagnostic → 409 edge + 0 diagnostic.
- Occurrence records and node IDs compare **equal across all 153 roots**.
- Snapshots: 23 tracked, **0 stale**, no recapture performed. D9's trigger never fired.
- Full-suite baseline: 17 failures, **all** a missing `pandas`, environmental and pre-existing.
  Zero license skips. Post-Phase-4: 17 failed / 2143 passed.
- D11's `deep override affected-shape coverage unproven` gap is **open by owner disposition** and
  must remain visible through close.
- D10 took route 1 on evidence; SC8 is kept as written and is **not** subject to a gap record.

## The one call this phase must make honestly

**[AGENT — orchestrator]** The arrayed-owner case (`usage_owner_bare_alias_arrayed`) changed from a
**silent answer** to an `SI_OCCURRENCE_AMBIGUOUS` refusal. That is a behavior change that can make a
model which loads today start failing. Adjudicate it explicitly and on its merits against the item's
declared "fail loudly rather than fall back" intent — do not let it pass as an unremarked row. The
owner has been told about this class and did not reserve the call, so it is yours to make and
record with reasoning.

More generally: adjudicate each changed row as fix or regression on the evidence, not on the
expectation that it should be a fix. If a row genuinely looks like a regression, say so plainly —
reporting one is a success of this phase, not a failure of the item.

## Constraints

- Licensed environment: `set -a; source ../agentic-mbse/.env; set +a`. No license-related skip.
- **Do not touch `src/`** beyond what Phase 3 landed. Confirm only `elaborate.py` changed in
  production and that no evidence, occurrence, slot, graph, projection, or codec schema was widened.
- The bounded documentation check against `.project/active/self-binding-replacement/spec.md:56,66-70,74-78`
  is **bounded**: correct a mismatch only within that spec's own instruction. Do not change D-5/D-7
  guidance or fusion-tea migration. Record that the final verifier remains `/_my_close`.
- Do not absorb unrelated fixes into this item. The 17 missing-`pandas` failures are environmental
  and stay as they are — compare the delta, do not "fix" them.
- Do not check SC8 or the deep-override lane as fully evidenced if a standing gap remains open.

## Deliverable

`verification/after.json` and `verification/adjudication.md` with zero unadjudicated rows, the full
Validation section run and reported exactly, every spec success criterion reconciled with one
retained test or evidence row, and the plan's "Phase 5 Completion" notes filled in. End with
`ARTIFACT: <path>`.
