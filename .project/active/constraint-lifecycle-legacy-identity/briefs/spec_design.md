# Combined Spec+Design Brief — Lifecycle Item 12: Legacy Snapshot and Tracking Identity Closure

**Stage:** spec (one combined spec+design artifact; bounded closure item)
**Epic authority:** Item 12 (register row 16); contract row 16.

## Intent

- [INHERITED: ratified contract] Normal product generation FAILS CLOSED on `grandfathered_off`
  before a certifying seal can exist — the silent constraint-drop path for grandfathered
  snapshots dies. (Item 8's wi014_toy regen already tripped the loud grandfathered warning
  once — that warning exists; this item makes the drop impossible on the product path, not
  just warned.)
- If legacy inspection is retained at all: explicit opt-in only, visibly non-executable and
  non-certifying (cannot produce a sealed/certifying package). If nothing needs it, delete
  the mode outright — deletion is the epic-preferred branch.
- `tracking_key`: either fully populate/catalog/test it as the author correlation key, or
  DELETE the field and every cross-version correlation claim (docs included). No middle state.
- Preserve the distinctions among semantic, catalog, executable, proposal, case, attempt, and
  artifact identities; delete dead identity surface not selected by design.
- Resume/query mismatch behavior stays fail-closed or starts explicit new lineage (Item 8's
  store gate is the mechanism — verify, don't rebuild).
- [OWNER] No LOC metrics; deletion over shims.

## Ground truth

- Chain: codegen `b987869` (+ docs d5f155b), agentic-mbse `4c18d61`, teax `c342b10`.
- Snapshot format is v5 with the shape gate (Item 5) — a grandfathered v≤4 snapshot cannot
  even load now; inventory what `grandfathered_off` can still mean at v5 (it may be nearly
  dead already — MEASURE: find every reader/setter of the flag and every path that reaches
  lowering with it set).
- `tracking_key`: find every producer/consumer/doc claim before choosing populate-vs-delete;
  the choice is the design's to make on evidence (which consumers actually correlate across
  versions today? If none: delete).

## Out of scope (firewall)

Claiming anonymous identities stable across versions without an explicit author key; Item
13's composed proof.

## Artifact shape

One document: the measured inventory (flag readers, tracking_key surface), provenance-graded
requirements, the selected mechanism per question with rejected branch recorded as decision,
RED-first acceptance (a grandfathered snapshot on the product path must fail closed with a
contextual error; the opt-in mode if retained provably cannot seal), phased plan, deletion
inventory.
