# Spec + Design: Lifecycle Item 12 — Legacy Snapshot and Tracking Identity Closure

**Status:** Draft (combined spec+design)
**Owner:** Reid W
**Created:** 2026-07-20
**Complexity:** MEDIUM
**Branch:** constraint-exec-epic
**Epic:** constraint-execution-lifecycle-contract (register row 16; contract row 16)

---

## Problem

Two loose ends from the constraint-execution lifecycle still let a package look
certified while resting on nothing.

1. **The silent constraint-drop path.** A snapshot captured with lowering disabled
   carries `constraint_lowering_mode = "grandfathered_off"`. On the product path
   (`generate --from-snapshot`) the offline rebuild only **warns** and drops the
   constraint assertions, then hands back a graph that generation seals into a
   certifying package (`snapshot/graph_rebuild.py:228`). A grandfathered snapshot
   that actually carried assertions would produce a sealed package with those
   assertions silently gone. The ratified contract requires this path to fail
   closed *before* a seal can exist.

2. **A dead correlation field.** `ConcreteConstraint.tracking_key`
   (`resolution/models.py:394`) is documented as the author-controlled
   cross-version correlation key (D8). It has **zero writers** in `src/`, is
   **absent from the catalog** (`assemble_constraint_catalog` never reads it), and
   is **never serialized** into a snapshot. The epic's non-goals lean on it as if
   the correlation story exists; it does not. It is a field carrying a promise
   nothing keeps.

This item closes both: make the product path reject `grandfathered_off`, and pick
one honest state for `tracking_key`.

## Measured Inventory (the evidence)

### `grandfathered_off` — every producer, reader, and what it can still mean at v5

The mode is **not** dead at v5. Measured against the checkout at codegen `b987869`:

**Constant + validity** — `snapshot/__init__.py:36-39`. Two legal modes:
`"applied"`, `"grandfathered_off"`. The loader rejects any third value
(`snapshot/loader.py:770-774`).

**Producers (two, and only one still fires in shipping capture):**

| Producer | Site | Fires today? |
|---|---|---|
| Extraction-only capture (models that can't build a pipeline, so lowering never runs) | `scripts/capture_extraction_snapshots.py:241` — hardcodes the mode | **Yes** — 7 committed snapshots |
| Full-pipeline capture opt-out via `capture_snapshot(lower_constraints_enabled=False)` | `snapshot/capture.py:24,50`, threaded to `pipeline_builder.py:1177` ternary | **No** — the `GRANDFATHERED` set is empty (`scripts:168 = frozenset()`; Item 14 emptied it) |
| Live inert build via `build_pipeline_context(lower_constraints_enabled=False)` | `pipeline_builder.py:838,977,1177` | **Test-only** — 4 conformance tests; never sealed |

**The 7 committed `grandfathered_off` snapshots** are all extraction-only probes:
`agg_literal_probe`, `chain_override_probe`, `expression_binding_probe`,
`invocation_binding_probe`, `self_named_binding_trap`, `shadowed_reference`,
`unresolvable_attr_probe`. **Every one carries 0 constraint usages** — so the
warn-and-drop branch is vacuous for them today (it needs `facts.usages`). They are
loaded by extractor / backtracker / computed-attribute tests, e.g.
`test_written_qualifier_anchoring.py:67` runs the **product read-path**
(`build_pipeline_context_from_snapshot(shadowed_reference)`) to inspect the
assembled context. These snapshots are inspection artifacts by construction; they
are never generated into a sealed package.

**Readers of the mode:**

- `snapshot/graph_rebuild.py:99` — gates offline re-lowering (`applied` ⇒ re-lower).
- `snapshot/graph_rebuild.py:210,228` — the warn-and-drop branch (the fail-open).
- `snapshot/loader.py:743-774` — validates the value is in the legal set.
- `snapshot/serializer.py:157` — a facts-copy guard keyed on `!= "applied"`.
- `orchestration/pipeline_builder.py:1177` — stamps the live context's mode.

**What `grandfathered_off` can still mean at v5:** exactly one live thing — an
**extraction-only snapshot whose model cannot be lowered at all**, carrying honest
facts and an empty occurrence table. The full-pipeline "captured with lowering
turned off" meaning is already dead in shipping capture (empty `GRANDFATHERED`
set). A pre-v5 grandfathered snapshot on disk is separately unreachable: the v5
version gate rejects it before the mode is ever read
(`test_snapshot_v5_gate.py:56`).

**Latent misreport (found while measuring):** the from-snapshot `PipelineContext`
never sets `constraint_lowering_mode`, so it inherits the dataclass default
`"grandfathered_off"` (`pipeline_context.py:146`) — **every** from-snapshot
context reports `grandfathered_off`, even one built from an `applied` snapshot
(`orchestration/snapshot_context.py`, the `PipelineContext(...)` call omits the
field). The only reader of `ctx.constraint_lowering_mode` is `capture.py:66`,
which only ever sees a **live** context, so nothing depends on the wrong value —
but the gate this item adds cannot trust that field until it is fixed.

### `tracking_key` — every producer, consumer, and doc claim

- **Field:** `resolution/models.py:394` (`str | None = None`); docstring
  `:372-373` ("Optional author-controlled correlation key (D8); never part of
  `constraint_id`").
- **Writers in `src/`:** none. **Reads in `src/`:** none.
- **Catalog:** absent — `generation/constraint_catalog.assemble_constraint_catalog`
  never touches it.
- **Serialization:** `ConcreteConstraint` is not serialized into snapshots
  (`snapshot/serializer.py` has no reference; snapshots carry raw facts and
  re-lower). So the field never reaches a persisted format.
- **Tests:** one — `tests/unit/test_concrete_constraint_model.py:351-354` sets it
  and round-trips it. Nothing else.
- **Docs:** none under `docs/`. Cross-version correlation *claims* that lean on it
  live only in the epic contract artifact
  (`.project/active/constraint-execution-lifecycle-contract/spec.md:228,541`).

**Which consumer correlates across versions today? None.** The brief's stated
delete condition ("if none: delete") is met.

## Success Criteria

- [x] `generate --from-snapshot` on a `grandfathered_off` snapshot **fails closed
      with a contextual error** (naming lowering / recapture), before any output
      file is written and therefore before any seal exists.
- [x] A `grandfathered_off` snapshot **provably cannot produce a sealed /
      certifying package** — there is no code path from it to `seal_package`.
- [x] Grandfathered extraction-only snapshots **remain loadable for inspection**
      (the 7 probe fixtures and their tests keep passing); the mode is retained as
      an explicitly non-certifying inspection state, not deleted.
- [x] A full-pipeline model **can no longer be captured `grandfathered_off`** — the
      capture-time opt-out for lowerable models is gone.
- [x] `tracking_key` **does not exist** on `ConcreteConstraint`; no cross-version
      correlation is claimed anywhere (docs and epic non-goals amended).
- [x] The from-snapshot context **reports its snapshot's real lowering mode**, not
      the defaulted `grandfathered_off`.
- [x] The full suite (`uv run pytest tests/`) is green, including the RED tests
      below, with **no snapshot re-capture** (no format bump).

## Known Requirements

- **[INHERITED: ratified contract, row 16]** Normal product generation fails
  closed on `grandfathered_off` before a certifying seal can exist; the silent
  constraint-drop path dies. *(Brief Intent bullet 1.)*
- **[INHERITED: ratified contract]** If legacy inspection is retained, it is
  explicit opt-in, visibly non-executable and non-certifying (cannot produce a
  sealed/certifying package). Delete outright if nothing needs it. *(Brief Intent
  bullet 2; deletion is the epic-preferred branch.)*
- **[INHERITED: ratified contract]** `tracking_key`: fully implement as the author
  correlation key, or delete the field and every cross-version correlation claim,
  docs included. No middle state. *(Brief Intent bullet 3.)*
- **[INHERITED: ratified contract]** Preserve the distinctions among semantic,
  catalog, executable, proposal, case, attempt, and artifact identities; delete
  dead identity surface not selected by design. *(Brief Intent bullet 4.)*
- **[INHERITED: ratified contract]** Resume/query mismatch stays fail-closed or
  starts explicit new lineage — verify Item 8's store gate, do not rebuild.
  *(Brief Intent bullet 5.)*
- **[OWNER]** No LOC metrics; deletion over shims.
- **[HARD]** `seal_package` is a pure directory→contract function
  (`contracts/seal.py:93`) with no access to the pipeline context or snapshot
  mode. The fail-closed gate therefore cannot live in `seal_package`; it must live
  upstream, at the generation boundary that reads the snapshot.
- **[HARD]** The from-snapshot read-path helper
  (`build_pipeline_context_from_snapshot`) is shared with inspection tests that
  legitimately run it on a grandfathered probe (`test_written_qualifier_anchoring.py:67`).
  The gate therefore cannot live in that shared helper; it must live on the
  **generate command** path only.

## Design Decisions

### D1 — Fail closed at the generate command, on the snapshot's real mode

**Decision.** The `generate` command's from-snapshot branch
(`cli/__init__.py:981-986`) checks the lowering mode right after building the
context and **raises a contextual error** if it is `grandfathered_off` — before
`_preflight_constraint_names` (`:997`) and long before any output write
(`:1018`) or seal (`:1061`). The error names the cause and the fix ("this snapshot
was captured without constraint lowering (grandfathered); it cannot produce a
certifying package — recapture with lowering enabled").

**Why here and not elsewhere:**

- *Not in `seal_package`* — it is pure over the directory (`[HARD]` above); by the
  time it runs the constraints are already gone and the mode is unknowable.
- *Not in `build_pipeline_context_from_snapshot`* — that helper is the inspection
  read-path too; gating there breaks `test_written_qualifier_anchoring.py:67` and
  every future inspection of a grandfathered probe (`[HARD]` above).
- *At the generate command* — this is exactly "normal product generation," the
  boundary the contract names. Inspection callers of the shared helper are
  untouched; only the certifying command refuses.

**Rejected branch (recorded as decision, not instruction):** gating at load by
removing `grandfathered_off` from `VALID_CONSTRAINT_LOWERING_MODES`. Rejected
because it would make the 7 extraction-only probe snapshots unloadable, breaking
their extractor tests — load is inspection, and inspection of a non-lowered
snapshot is legitimate. Generation is what a non-lowered snapshot must be stopped
from producing.

### D2 — Retain `grandfathered_off` as an extraction-only inspection state; delete the full-pipeline opt-out

**Decision.** Something needs the mode: extraction-only models cannot be lowered,
so their honest state *is* "facts extracted, not lowered." Keep the mode and the
extraction-only capture path (`scripts:241`). Make it visibly non-certifying via
D1. **Delete** the capture-time opt-out for lowerable models —
`capture_snapshot(lower_constraints_enabled=...)` and the now-empty `GRANDFATHERED`
plumbing — so a full-pipeline model can only ever be captured `applied`.

The inspection-path warn (`graph_rebuild.py:228`) **stays**: on a direct
`build_full_graph_from_snapshot` inspection load it honestly signals "constraints
present in facts, not lowered into this graph." That boundary is non-certifying, so
warn-and-continue is correct there. D1's hard gate is what covers the *product*
boundary. Two boundaries, two honest behaviors.

**Rejected branch:** delete the mode entirely and convert the 7 probes to
`applied`. Rejected — they cannot build a pipeline, so `applied` is a lie for
them; the mode is the only honest label for an un-lowerable extraction.

### D3 — Delete `tracking_key`

**Decision.** Delete the field, its docstring, and its one test. No consumer
correlates across versions (measured: zero writers, absent from catalog, never
serialized), so the delete condition is met, and "no middle state" forbids leaving
a populated-nowhere field. Amend the epic contract's two non-goal lines to a
one-line decision record: cross-version correlation is not supported; the
`tracking_key` field was removed (Item 12). No format bump — the field never
reached a serialized surface.

**Rejected branch:** fully implement it (author surface, catalog column, tests).
Rejected — no stated consumer needs cross-version correlation now; implementing a
correlation key with no correlator is speculative surface, and Item 13's composed
proof is explicitly out of scope.

### D4 — Thread the snapshot's real mode into the from-snapshot context

**Decision.** In `snapshot_context.py`, pass
`constraint_lowering_mode=snap["constraint_lowering_mode"]` into the constructed
`PipelineContext`, replacing the defaulted `grandfathered_off`. This fixes the
latent misreport (found above) *and* supplies D1's gate signal from the context
rather than a second snapshot load. Safe: the only reader of the field
(`capture.py:66`) sees only live contexts.

### D5 — Retain the live `build_pipeline_context(lower_constraints_enabled=...)` flag

**Decision (scope boundary, recorded so it is not read as an oversight).** Keep
the live flag. It is **not dead** — 4 constraint-lowering conformance tests pass
`False` to build an inert context so a halting/blocked assertion does not raise
before the test reaches its own `lower_constraints` call
(`test_constraint_lowering.py:63-69`, `test_orchestrator.py:371`,
`test_constraint_pipeline_threading.py:36,225`,
`test_constraint_lowering.py:1003`). It is **not a product hole** — the live CLI
path hardcodes the default (`cli:989`), and the only capturer of a live context,
`capture_snapshot`, loses its opt-out under D2, so it always captures `applied`.
Deleting the flag would force an unrelated rewrite of the constraint-lowering test
harness. The closure targets the snapshot → generate → seal path; a live,
never-sealed test context is off that path.

### Identity distinctions (Brief bullet 4)

The only dead identity surface is `tracking_key` (D3). The live identities are
preserved and untouched: `constraint_id` (semantic / source-local +
owner-instance + membership + polarity, `resolution/models.py:378`), the catalog
ordering (`constraint_catalog`), and the executable fingerprint
(`seal.py:111`). Anonymous-ID inputs digesting `loc.file` are Item 13's concern
and out of scope here.

### Resume/query mismatch (Brief bullet 5) — verify, not rebuild

This item introduces **no** resume, query, or lineage surface. The five changes
(D1 gate, D2 capture deletion, D3 field deletion, D4 mode threading, the retained
inspection warn) touch none of the store-gate machinery. Verification is therefore
a confirmation, not new code: the plan asserts no lineage path is added. (The store
gate itself is Item 8's, in the constraint store; unchanged here.)

## Deletion Inventory

| What | Where | Note |
|---|---|---|
| `graph_rebuild.py:228-236` warn branch | keep or delete? | **Keep** (D2) — inspection-path honesty; not deleted |
| `capture_snapshot(lower_constraints_enabled=...)` param + body use | `snapshot/capture.py:24,36-39,50` | Delete param; capture always `applied` |
| `GRANDFATHERED` set + conditional | `scripts/capture_extraction_snapshots.py:168,282` | Delete set; drop the `lower_constraints_enabled=` arg at `:279-283` |
| `tracking_key` field | `resolution/models.py:394` | Delete |
| `tracking_key` docstring | `resolution/models.py:372-373` | Delete |
| `tracking_key` test | `tests/unit/test_concrete_constraint_model.py:351-354` | Delete |
| Cross-version correlation non-goal claims | `.../constraint-execution-lifecycle-contract/spec.md:228,541` | Amend to one-line decision record |

**Not deleted, deliberately:** the `grandfathered_off` mode constant and its legal
value (D2); the extraction-only capture path (D2); the live inert-build flag (D5);
the inspection warn (D2). Each is either live or the honest label for a real state.

## RED-first Acceptance

Each test is written to **fail on the current tree** first, then pass after the
change.

- **RED-1 — product path fails closed.** Build (or fixture) a `grandfathered_off`
  snapshot and run the `generate --from-snapshot` command against it. Assert it
  raises a contextual error whose message names lowering/grandfathering and
  recapture. *Red today:* generation currently warns-and-seals. *Green after D1.*
  Use a snapshot **carrying constraint usages** so the test proves the drop is what
  is prevented (the 7 committed probes have 0 usages; capture one from a
  constraint-bearing fixture with the pre-deletion opt-out inside the test, or
  hand-craft the mode field on a copy of a lowered snapshot).
- **RED-2 — no seal reachable.** Assert that running the generate command on a
  `grandfathered_off` snapshot writes **no** `package_contract.json` and creates no
  output tree (the gate precedes `_clear_output_directory` and `_seal_package`).
  *Red today:* a sealed package is produced. *Green after D1.*
- **RED-3 — inspection still works.** Assert the 7 probe fixtures still load via
  `build_full_graph_from_snapshot` / `build_pipeline_context_from_snapshot`, and
  `test_written_qualifier_anchoring.py` still passes. *Guards against over-gating
  (the rejected load-time branch).* Green today and after — a regression fence.
- **RED-4 — full-pipeline model cannot be grandfathered.** Assert
  `capture_snapshot` no longer accepts `lower_constraints_enabled` (signature has
  no such parameter) and always stamps `applied`. *Red today:* the param exists.
  *Green after D2.*
- **RED-5 — `tracking_key` is gone.** Assert `ConcreteConstraint` has no
  `tracking_key` field (`"tracking_key" not in ConcreteConstraint.model_fields`)
  and that a dumped instance has no such key. Delete the old round-trip test.
  *Red today:* the field exists. *Green after D3.*
- **RED-6 — from-snapshot context reports the real mode.** Assert
  `build_pipeline_context_from_snapshot(applied_snapshot).constraint_lowering_mode
  == "applied"`. *Red today:* it returns the defaulted `grandfathered_off`.
  *Green after D4.*

## Phased Plan

1. **D4 first (mode honesty).** Thread `snap["constraint_lowering_mode"]` into the
   from-snapshot `PipelineContext`. Land RED-6. Grep `tests/` for any assertion
   that relies on the buggy default before flipping.
2. **D1 (the gate).** Add the contextual fail-closed check to the generate
   command's from-snapshot branch, reading `ctx.constraint_lowering_mode`. Land
   RED-1 and RED-2.
3. **D2 (capture deletion).** Remove `capture_snapshot`'s `lower_constraints_enabled`
   param and the `GRANDFATHERED` plumbing in the capture script. Land RED-4. Keep
   the inspection warn. Confirm RED-3 (regression fence) stays green.
4. **D3 (`tracking_key` deletion).** Delete field, docstring, and test; amend the
   contract non-goal lines. Land RED-5.
5. **Verify bullet 5.** Confirm no resume/query/lineage surface was added (a
   read-through, not code).
6. **Full suite green**, no re-capture, no format bump. Audit for placeholder /
   TODO residue.

## Non-Goals

- Claiming anonymous identities stable across versions without an explicit author
  key (Brief firewall).
- Item 13's composed proof.
- Deleting the `grandfathered_off` mode or the extraction-only capture path
  (D2 — a real state needs it).
- Deleting the live `build_pipeline_context(lower_constraints_enabled=...)` flag
  (D5 — live test affordance, off the certifying path).
- A snapshot format bump — nothing here touches a serialized surface.
- Rebuilding Item 8's store gate (Brief bullet 5 — verify only).

## Open Questions / Deferred to design

None load-bearing. The two delegated choices (populate-vs-delete `tracking_key`;
retain-vs-delete legacy inspection) are decided on the measured evidence above
(D3, D2). Two mechanism points resolved rather than deferred, recorded so a
reviewer can challenge them: gate placement at the generate command vs. the shared
helper (D1), and reading the mode from the context after the D4 fix vs. a second
snapshot load (D4).

---

## Related Artifacts

- **Epic:** `.project/backlog/` constraint-execution-lifecycle-contract (register
  row 16; contract row 16)
- **Brief:** `.project/active/constraint-lifecycle-legacy-identity/briefs/spec_design.md`
- **Required Reading / ground chain:** codegen `b987869` (+ docs `d5f155b`),
  agentic-mbse `4c18d61`, teax `c342b10`
- **Adjacent evidence:** the grandfathered guard datapoint in
  `.project/active/constraint-lifecycle-diagnostics-defaults/evidence.md:274-283`;
  the `tracking_key` dead-field finding in
  `.project/research/20260719-125806_constraint-execution-lifecycle-contract-adversarial-review.md:333`

---

**Next Steps:** After review, proceed to `/_my_plan` (or straight to
`/_my_implement` given the phased plan above), then `/_my_audit`.
