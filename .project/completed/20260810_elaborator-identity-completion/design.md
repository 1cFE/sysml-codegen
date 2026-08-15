# Design Authority Map: Exact-Identity Completion

**Status:** Adopts existing owner-approved design; no new architecture
**Item:** ELABORATE-FIRST Item 6
**Created:** 2026-08-09

## The Point

SysIDE has already resolved semantic identity. Item 6 finishes carrying that identity through every
executable payload and projection structure before Item 7 makes the route authoritative. It does
not introduce another identity system or alter the public generation seam.

## Governing Design

The normative design is `.project/active/elaborator-design/design.md`. This file is an item-local
index for planning, not a second copy. These sections govern Item 6:

| Item-6 responsibility | Governing design |
|---|---|
| declaration and payload identity | D1, D4, D7, D10; Required Invariants 1–12 |
| effective child declarations and concrete occurrence context | D2, D3, D6; Exact contextualization rules |
| structured graph occurrences and neutral IR | D4, D7, D9; Architecture steps 2–5 |
| one-way public projection and direct-edge ordering | D8; Required Invariants 7 and 11 |
| repository ownership and route isolation | Component Overview; Integration Strategy |
| adversarial and public mutation evidence | Validation Approach; Appendix A |

The Item-6 research maps the remaining implementation gaps to current files:
`.project/research/20260809-153245_item6-identity-completion-and-cutover-census.md`.

## Item Boundary

Item 6 changes only the internal exact route and any live `agentic-mbse` API needed to preserve
exact identity. The legacy route remains shipped and snapshot v5 remains byte-identical. Item 7
owns the new snapshot envelope, authority switch, deletion ledger, corpus recapture, and dual-run
harness removal.

## Feasibility Pins

- Exact consumer edges, typed graph IDs, and the 29-cell route already exist and are certified.
- `SysideAdapter.element_id()` is the validated parser UUID boundary.
- SysIDE 0.8.4 supplies effective declaration views but not concrete occurrences; D3 records the
  split.
- The existing internal graph codec proves canonical typed-ID round-trip, but Item 6 must add the
  structured occurrences and IR that D9 already requires.
- Neutral constraint facts remain tool-independent. A live ID-bearing association may wrap them;
  changing their serialized contract is not implied by this item.

## Item-Local Implementation Choices

These choices close the spec's implementation questions without changing the shared architecture:

- Calculation extraction adds live raw-UUID sidecars and exact-ID maps beside the frozen legacy
  name-keyed fields. Codegen wraps those UUIDs at the elaboration boundary. The legacy fields and
  snapshot-v5 serializer remain unchanged.
- `agentic-mbse` returns a live ID-bearing wrapper around the existing neutral constraint facts and
  profile decisions. The wrapper records usage ID and effective definition ID while live SysIDE
  objects are available. Each profile decision is associated with its exact usage ID; the decision
  has no separate parser identity. The neutral fact dataclasses and their serialized form do not
  gain parser identity.
- Graph nodes retain `agentic_mbse.sysml.expression_ir.ExpressionIR` as typed objects, plus exact
  consumer ports for every feature-reference occurrence. The internal graph codec is the only place
  that turns the IR into canonical JSON. Projection never reparses an IR string to discover inputs.
- The fixed D10 catalog remains the vocabulary: absent or unusable declaration identity uses the
  `SI_ID_*` codes, an exact association to a missing/conflicting graph port uses
  `SI_EDGE_DANGLING`, malformed graph/IR/eligibility wire data uses `SI_SNAPSHOT_INVALID`, and a
  profile `BLOCK` uses `SI_CONSTRAINT_BLOCKED` to make strict elaboration and projection halt while
  preserving typed lenient evidence.

## Risks

Use the governing design's Potential Risks. Item-specific concentration points are the coordinated
constraint API across repositories, legacy-v5 byte freeze while extraction records gain IDs,
native `Usage.usages` parity on retyping/inheritance, and preserving the current generated public
API while removing projection's reverse string joins.
