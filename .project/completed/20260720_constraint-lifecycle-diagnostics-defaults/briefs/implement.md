# Implement Brief — Lifecycle Item 4: Diagnostic Severity and Modeled-Default Fidelity

**Stage:** implement (phase groups; orchestrator reviews between groups)
**Authority:** approved `spec.md` + `design.md` (rev 2, Approve-with-notes; both review rounds
in `design-review.md`) in `.project/active/constraint-lifecycle-diagnostics-defaults/`. The
phased plan is folded into the design; check its boxes and write implementation notes there.

## Mandatory item 0 — apply C3 before any production code

Amend design.md per the round-2 must-fix, then implement accordingly:
- Row 16 reads `req.occurrence_owner_path or req.instance_path` — preserving the three
  lenient graph_builder builders (`:1369`, `:1606`, `:1629`) that rely on row 16 today,
  keeping rows 12/13 dead for the calc consumer, reintroducing neither C1(a) nor C1(b).
- Gate 3's probe scope widens beyond "bound bindings" to cover aggregation/LocalTerm
  resolutions (as written it cannot see C3's regression class).

## Ratified decisions (do not re-litigate)

DD-B1: severity is a fact-schema field — constraint-facts/v2, SNAPSHOT_FORMAT_VERSION 4,
licensed 34-snapshot re-capture (byte-identity captured_at procedure per project memory).
Carry mechanism: two dedicated row-16 fields (written_reference + occurrence_owner_path);
calc consumer never sets instance_path. Gates: per-binding (outcome, identity, key_form)
probe over the corpus + changed-outcome stop clause. Bracketed owners: deliberate safe-miss
with two-check Phase 0 exit and movement stop. Phase ordering: Phase 0 parity, Phases 1–3
codegen-only, Phase 4 agentic-mbse-first (facts v2), Phase 5 licensed re-capture + snapshot
routes. Both version gates fail closed in both directions. Owner rulings: no LOC metrics;
Opus cap on any suborchestration.

## Execution rules (standing discipline)

- Tests first per phase; RED-before-GREEN on public acceptance shapes; shared_producer's RED
  surface must be BUILT (the claimed test never existed) against the current two-key state
  before the carry lands.
- Forced differences (carry's 22-EP rename set; the two-null-key EntryPoint regeneration;
  inputs/*.json churn; R-8 byte changes) each enumerated and pinned BEFORE regeneration; one
  regeneration event each; every value-change (vs key-change) is a stop.
- Items 1–3 certified seams extended, never reworked; their acceptance files/fixtures remain
  byte-identical except where a pinned forced difference says otherwise.
- Cross-repo: agentic-mbse work on its constraint-exec-epic branch at
  /home/reid/1cfe/agentic-mbse; record exact new pin; both skew directions get RED tests.
- No wrapper/flag/alias survives a cutover; deletions in the same change set.

## Environment

License: `set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a` — verify via zero
`no live syside license` skips in -rs output (counts do NOT discriminate). TEAx lane per Item 1
evidence §3. Never format fixtures/baselines. `.claude/projects/` untouchable. Preserve
unrelated dirty files.
