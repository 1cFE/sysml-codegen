# Brief: Phase 3 — repair the shared one-segment resolver

Sent to an `implement` stage session by the orchestrator.

## Work item

`plan.md` Phase 3, every checkbox. The plan is the contract; this brief adds what earlier phases
settled and where the orchestrator holds the bar.

**This is the only production edit in the whole item.** One branch, in one file:
`src/sysml_codegen/elaboration/elaborate.py:2062-2076`.

## Intent this serves (provenance marked)

- `[OWNER-VERBATIM, 2026-08-13]` The product seeks a design search where engineering design
  parameters can be freely varied and viability and outcomes such as LCOE can be assessed, without
  embedding engineering logic by predetermining free variables and backing into the rest. One
  modeled source occurrence must become exactly one runtime source reaching every and only its
  bound consumers.
- `[INHERITED: design.md D1]` The one-segment branch of the shared semantic resolver is the last
  common policy seam before all six consumer lanes diverge. Repairing it there is why every lane
  inherits the fix from one change.
- `[INHERITED: spec/design]` **Fail loudly rather than fall back.** Owner-selection failure is
  final. No fallback, no positional recovery, no new diagnostic code.

## What earlier phases established — do not re-derive

**[AGENT — orchestrator, from commits `d78c42e`, `7673bf9`, `85f598a`]**

- The mechanism, confirmed on element IDs: a `FeatureSlotId` is the root of the redefinition family
  (`elaboration/occurrence.py:70-73`), so `comp_a::length` and `comp_b::length` share one slot.
  `_resolve_leaf` discards the exact leaf's owner and re-finds that shared slot by walking the
  **consumer's** occurrence lineage (`elaborate.py:2299-2347`). That discard is the defect.
- There are **15 intentionally red nodes** in
  `tests/conformance/test_usage_owned_reference_anchoring.py` and passing controls beside them.
  Your success condition is: every red node green, **every control still green**, and no new
  failure anywhere.
- `u2`/`u3`/`u3b` are **definition-owned-leaf** controls. The qualifier names a usage but the leaf
  is declared on the part definition, so the repaired branch must **not** activate for them.
- The arrayed-owner negative (`usage_owner_bare_alias_arrayed`) currently answers **silently**.
  After the repair it must raise `SI_OCCURRENCE_AMBIGUOUS` — a silent answer there is the exact
  hidden-recovery failure this phase must not ship.
- `tests/fixtures/usage_owner_bare_alias_def_owned` and `..._subset_def_owned` are guard controls:
  live owner is a `PartDefinition`, branch must not activate.

## The shape of the change (from design D2/D3/D4/D5)

Recover the exact live leaf and its live semantic owner. Activate **only** for
`SysideAdapter.is_instance(owner, "PartUsage")` — not `owner_is_definition == false`, and never on
source spelling or qualified-name text. Contextualize that owner through the existing occurrence
selector with **scalar** cardinality (`plural=False`, even when the caller passed `plural=True` —
D4). Select the exact leaf slot at the selected occurrence and require exactly one typed target.
Every other owner kind keeps the current `_resolve_leaf` route untouched.

Reuse `elaborate.py:2119-2219` and `elaborate.py:2350-2366`. The branch returns the **raw** typed
edge — alias following and diagnostic translation stay with the callers (D5).

## Constraints

- Licensed environment: `set -a; source ../agentic-mbse/.env; set +a`. An unlicensed skip is not
  evidence.
- **No caller, evidence schema, occurrence index, slot index, graph model, projection path, or
  snapshot codec change.** If you believe one is required, that is a premise conflict — stop and
  report it, do not widen the change.
- Do not add a fallback, resolver-level alias following, or a new diagnostic code.
- Do not weaken or delete a Phase-2 assertion to make a test pass. If an assertion looks wrong,
  stop and report it — a red test that was designed as the oracle is not yours to edit.
- Run focused mypy on `elaborate.py` and Ruff on everything touched.

## Quality bar

`[AGENT — orchestrator]` This branch is the product's semantic core and will be read for years.
Minimal is not the same as terse: the code should make the owner → occurrence → leaf sequence
legible, name why scalar cardinality is forced, and keep the failure path obviously final. Match the
surrounding file's idiom and comment density. Do not leave a TODO.

## Deliverable

Phase 3's "Changes Required" and its full "Validation" section, with results reported exactly —
including the manual checks: u4–u7 typed edges and full diagnostics inspected, u6 confirmed to have
no residual `comp_b.length` edge and no recovery path invoked, and Phase-2 occurrence records and
node IDs compared byte-for-byte against the repaired graphs. Fill in the plan's "Phase 3 Completion"
notes. End with `ARTIFACT: <path>`.
