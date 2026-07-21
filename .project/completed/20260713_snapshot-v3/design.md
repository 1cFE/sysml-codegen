# Design: Snapshot v3 — Constraint Facts Load-Bearing

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-07-12
**Branch:** constraint-exec-epic
**Commit:** 3733048
**Epic:** CONSTRAINT-EXEC — Item 8

---

## Overview

Make the neutral `ConstraintFacts` a load-bearing, versioned section of the extraction
snapshot, wire the from-snapshot rebuild path to **re-lower** from it (not carry a frozen
catalog), reject stale/sectionless snapshots loudly, and flip `lower_constraints_enabled` to
default True — with `plant_values`/`fusion_tea` grandfathered flag-off behind a marker that is
loud in the snapshot itself.

## Related Artifacts

- **Spec:** `.project/active/snapshot-v3/spec.md`
- **Epic:** `.project/backlog/epic_constraint_execution.md` (Item 8)
- **Concept:** `.project/concepts/constraint-execution-and-design-space-studies-claude.md`
  (Required Invariants: snapshot rejection + parity + fidelity; Appendix B S3/S4 carry-forwards)
- **Required Reading (epic):** concept Required Invariants (lines 66, 139, 140, 142, 191);
  S3/S4 results and carry-forwards; memory `byte-identity-captured_at-churn`.
- **Upstream:** Item 1 `constraint_facts.py` / `expression_ir.py`
  (`.project/reference/agentic-mbse-landed/`); Item 5 lowering + flag
  (`.project/active/constraint-lowering/`).

## Research Findings

Files analyzed (all `src/sysml_codegen/` unless noted):

- **Live lowering, three threading points** — `orchestration/pipeline_builder.py`:
  P1 RESOLVE `lower_constraints(...)` at `:864-873` (guarded on
  `lower_constraints_enabled and constraint_facts.usages`); P2 INJECT roots-before-pruning at
  `:883-909`; P3 EXTEND `extend_graph_with_constraints(...)` at `:976-979`. The transitional
  default lives at `:697` with the retire-me comment at `:856-863`.
- **The lowering algorithm** — `analysis/constraint_lowering.py`. `lower_constraints()` (`:436`)
  takes `facts`, `occ_index`, `registry`, `design_attrs`, `calc_usages`; the ONLY use of
  `occ_index` is `occ_index.occurrences_of(owner_eqn)` inside `_expand_owner_instances` (`:350`),
  and only for `part_def`-owned usages (`calc_def` uses `calc_usages`, `package` is a single
  top-level instance). `constraint_id` folds occurrence `instance_path`, source-local identity,
  `membership_kind`, and `is_negated` (`mint_constraint_id`, `:259`).
- **The part-instance index** — `analysis/part_instance_index.py`. `occurrences_of(qn)` (`:291`)
  computes subtype closure over the live `qn_to_partdef` map, walks structured paths, and
  returns a **sorted** `list[InstanceOccurrence]`; raises `NonFiniteCardinalityError` on a
  non-finite multiplicity (never a silent drop). `InstanceOccurrence` (`:197`) = `part_def_qn` +
  `steps: tuple[PathStep, ...]`; `PathStep` (`:26`) = `(owning_def_qn, feature_name,
  occurrence_index)`. `build_part_instance_index(model)` needs a **live** model.
- **Serializer / loader** — `snapshot/serializer.py` (the flat section dict at `:83-109`;
  recursive `_serialize_value` handles dataclasses/tuples/sets/enums); `snapshot/loader.py`
  (version hard-gate `:127-140`; the `compilation_results` **degrade-with-warning** precedent
  `:184-203` we must NOT copy; `_require(..., raise_on_missing=True)` raise idiom `:53-79`).
- **Offline rebuild** — `snapshot/graph_rebuild.py`. `build_classifier_inputs_from_snapshot`
  already re-derives registry, materializes supplied values into `design_attrs` (`:74-85`), and
  builds the `group_deriver`; `build_full_graph_from_snapshot` builds the base graph with
  `include_all=True` (`:175`). Both run **no** constraint phase today.
- **Capture** — `snapshot/capture.py` runs live `build_pipeline_context` and serializes
  `PipelineContext` fields; the context exposes `concrete_constraints` (output) but neither the
  raw `ConstraintFacts` (input) nor the occurrence table. `scripts/capture_extraction_snapshots.py`
  (`capture_snapshot` per fixture; `plant_values` + `fusion_tea` are in `MODELS`) and
  `scripts/capture_pipeline_baselines.py` (rebuilds baselines from committed snapshots).
- **Versions** — `ConstraintFacts.schema_version = "constraint-facts/v1"`
  (`constraint_facts.py:39`); every `ExpressionIR` node embeds
  `schema_version = "expression-ir/v1"` (`expression_ir.py:38`), so the predicate version rides
  along inside the canonical facts JSON. `constraint_facts.serialize/parse` give the byte-stable
  round-trip (Item 1). `constraint_inline` / `constraint_multi_instance` fixtures exist but have
  **no committed snapshot** — they must be added to the corpus for the parity test.

## Core Concept

A v3 snapshot carries three new things: the **neutral facts** (`ConstraintFacts`, serialized by
Item 1's canonical `serialize()`), a **resolved occurrence table** (the exact per-owner
`occurrences_of(...)` results the live index produced at capture, closure already applied), and
a **lowering-mode marker** recording whether lowering was applied at capture. The from-snapshot
path deserializes the facts, wraps the occurrence table in a frozen index that answers
`occurrences_of` by dictionary lookup, and calls the **real** `lower_constraints()` +
`extend_graph_with_constraints()` — re-deriving every `constraint_id` from the carried inputs,
never reloading a frozen catalog.

The key insight: the offline path lacks a live model, but the *only* thing lowering needs a live
model for is `occurrences_of`. We do not rebuild that capability offline; we **capture its
answers** — but not by reimplementing "which owners does lowering query." At capture we wrap the
live index in a **recording** index and run the real `lower_constraints` through it, so the table
we serialize is exactly the transcript of the queries lowering actually made (subtype closure
already folded into each answer). Offline replays that transcript by dictionary lookup. Sufficiency
is by construction: the same facts drive the same algorithm to the same queries on both paths.
Everything else lowering touches (registry, design attributes, calc-usages, the executable
profile) is already re-derived offline or round-trips inside the facts. So offline lowering is
genuine re-derivation from carried *inputs*, and it produces byte-identical `constraint_id`s
because its two identity-bearing inputs — the occurrences and the facts — reload byte-identical.

The marker is what lets both flip surfaces move together without breaking the corpus. "Facts
present" cannot mean "lower offline," because `plant_values`/`fusion_tea` genuinely assert
something the `gain` gap can't yet resolve — lowering them halts. The marker decouples the two:
their snapshots carry honest, non-empty facts (round-trip fidelity intact) plus
`constraint_lowering_mode: "grandfathered_off"`, and the offline path reads the marker and skips
lowering, leaving their graphs byte-identical to today. The grandfather is loud in the artifact,
not a silent empty section.

Existing pieces this composes with, each keeping its concern:
- `constraint_facts.serialize/parse` (Item 1) — canonical facts round-trip. We store and reload
  its output; we do not re-canonicalize.
- `lower_constraints` / `extend_graph_with_constraints` (Item 5) — the lowering algorithm, run
  unchanged offline against a frozen occurrence index.
- `graph_rebuild` offline re-derivation (registry, supplied-values, group_deriver) — the
  constraint phase joins the end of it, mirroring live P1/P3.
- The version hard-gate idiom (`loader.py:127-140`, `_require(raise_on_missing=True)`) — reused
  verbatim for the new missing-section gate.

## Key Bets

- **B1. The only live-model dependency in lowering is `occurrences_of`.** Everything else
  (`registry`, `design_attrs` incl. materialized supplied values, `calc_usages`, `evaluate_profile`
  over the facts) is already reconstructed offline or rides inside the facts. *If false → a
  frozen occurrence index is insufficient and offline lowering silently diverges or crashes on a
  missing live dependency.*
- **B2. Serialized occurrences reload byte-identical to the live ones, so re-derived
  `constraint_id`s are byte-identical.** `InstanceOccurrence` is a closed dataclass of
  strings/ints; `occurrences_of` returns them pre-sorted; the table preserves that order, and the
  owner keys are pinned sorted (INV-7). *If false → the multi-instance parity fixture's
  `constraint_id`s diverge live-vs-snapshot — the exact failure the fixture is chosen to catch.*
- **B3. `include_all=True` offline makes live P2 (roots-before-pruning) inert.** With no pruning,
  every calc usage — including one whose only consumer is an assertion — is already in the graph,
  so the producer channel each `MODULE_OUTPUT` input binds to exists without root injection.
  *If false → a constraint's `bound_channel` dangles offline and `_validate_channel_references`
  raises inside `extend_graph_with_constraints`.*
- **B4. The facts round-trip is lossless enough that `evaluate_profile` and `serialize_expression`
  return byte-identical predicates offline.** Item 1's canonical JSON + Item 3's profile are
  deterministic functions of the facts. *If false → `predicate_ir` or eligibility differs, so the
  catalog (and its ordering) differs across paths.*
- **B5. The occurrence table is a complete replay set by construction, because both paths issue
  the same `occurrences_of` queries.** The table *is* the transcript of the real capture-time
  `lower_constraints` call (MF3); offline runs the identical algorithm over the identical facts, so
  it queries the identical owner set (`part_def`-kind, `ADMIT`-eligible owners — the profile+kind
  filter lowering itself applies). *If false → offline lowering issues a query the transcript
  didn't record, and the frozen index raises on the missing key (loud, not silent).*

## Key Decisions

- **D1. Serialize the resolved per-owner occurrence table, captured as the transcript of the real
  `lower_constraints` call (MF3), not a re-derived owner set.** `{ owner_eqn: [InstanceOccurrence,
  ...] }`, closure pre-applied, keyed exactly by the queries lowering made. *Rejected: a separate
  `resolve_owner_occurrence_table` helper that re-selects owners from the facts (a second
  owner-selection path that must track lowering's `part_def`-kind **and** `ADMIT`-eligible filter
  forever, and can halt capture on a non-finite owner of an unassessed usage that live lowering
  never queries — the review's MF3). Rejected: serialize index inputs and rebuild the subtype
  closure offline (needs a live model — the thing we are removing). Rejected: carry the resolved
  `ConcreteConstraint` catalog (carriage-not-re-derivation, the S3 CF(2) trap — vacuous parity).*
- **D2. No `blocked` map in the table.** The guidance floated `+ blocked set`; because the table is
  the transcript of the real per-owner `occurrences_of` queries lowering made, a non-finite owner
  *raises* inside `_expand_owner_instances` and halts capture — exactly as live — so no blocked
  entry can reach a valid v3 snapshot. A queried owner with zero instances returns `[]` (recorded
  as an empty list, harmless — it is simply never blocking). Offline, a queried key absent from the
  table is a corruption → raise, never `[]`. *Rejected: bulk `all_occurrences()` + `blocked` (would
  need offline closure to answer supertype queries — D1's rejected alternative).*
- **D3. Grandfather via an explicit lowering-mode marker in the snapshot, driven by a named
  exclusion set in the capture scripts.** Top-level `constraint_lowering_mode: "applied" |
  "grandfathered_off"`. The two fixtures are captured with `lower_constraints_enabled=False`
  (from a named `GRANDFATHERED` set in both capture scripts), which stamps `grandfathered_off`;
  the offline path skips lowering for that mode. *Rejected: write an empty facts section for the
  grandfathered pair (dishonest — the model asserts; indistinguishable from a constraint-free
  model; violates the round-trip-fidelity `[HARD]` and the spec's own expected-diff class 2
  "non-empty facts on constraint-bearing snapshots"). Rejected: infer "don't lower" from an
  absent/empty occurrence table (a clean fixture with only `calc_def`/`package` owners also has
  an empty table — ambiguous).*
  - **Scope of the grandfather = the capture scripts, not the CLI.** After the flip,
    `generate --from-snapshot plant_values` succeeds (reads `grandfathered_off`, skips lowering),
    but live `generate --models plant_values` runs lowering under the new default and **halts on
    the `gain` gap** (`unresolved actual 'gain'`, INV-2). That halt is intended and loud — the
    honest signal that the model is not yet fully executable, and the exact prerequisite Item 14
    clears. It is not a regression to paper over; the CLI does not carry the exclusion set.
- **D4. Thread the raw facts + occurrence table + mode onto `PipelineContext`; capture serializes
  them.** New fields `constraint_facts`, `part_occurrences`, `constraint_lowering_mode`, populated
  in `build_pipeline_context`. *Rejected: re-extract facts inside `capture_snapshot` (a second
  extraction pass, and the occurrence table would still have to be rebuilt from a live model the
  capture path is trying to run once).*
- **D5. The rejection gate raises for all three keys and validates the mode enum, reusing the
  version-gate idiom.** In `load_extraction_snapshot`, after the version check: any of the three
  new keys absent, a torn facts dict, a wrong facts/expression-ir version, or a
  `constraint_lowering_mode` outside `{"applied","grandfathered_off"}` → `SnapshotFormatError` with
  a re-capture instruction (MF1 + MF2; full matrix in Architecture). *Rejected: gate only
  `constraint_facts` (leaves `part_occurrences`/`constraint_lowering_mode` to raise a raw
  `KeyError` — not loud, not a re-capture message — the review's MF1). Rejected: a catch-all
  `else: skip` on the mode (an unknown mode silently skips lowering — reopens the silence trap,
  MF2). Rejected: the `compilation_results` degrade-with-warning path (`loader.py:184-203`) — the
  spec forbids it here.*
- **D6. Add `constraint_inline` + `constraint_multi_instance` to both capture `MODELS` dicts.**
  The parity test needs committed v3 snapshots for them. *Rejected: prove parity only on
  `wi014_toy` (weaker — misses per-occurrence expansion, the exact path the occurrence table
  exists to serve).*

## Architecture

**Snapshot format v3 (new top-level keys), added to `serialize_extraction_snapshot`:**

```
snapshot_format_version: 3
...existing keys...
constraint_lowering_mode: "applied" | "grandfathered_off"   # always present
constraint_facts: { schema_version: "constraint-facts/v1", definitions, usages,
                    contexts, diagnostics }                  # always present (may be empty)
part_occurrences: { "<owner_eqn>": [ {part_def_qn, steps:[{owning_def_qn,
                    feature_name, occurrence_index}]} ] }    # present; {} when none
```

`constraint_facts` is Item 1's `serialize(facts)` output parsed back to a dict and embedded (so
the canonical bytes are preserved, not re-derived). `part_occurrences` is `_serialize_value` over
the `dict[str, list[InstanceOccurrence]]` (dataclasses → dicts, tuples → lists — no new
serializer code), with **owner keys emitted sorted** (INV-7 / MF4) since `snapshot_to_json` does
not `sort_keys`; occurrence lists are already sorted by `occurrences_of`.

**Capture data flow (live):** `build_pipeline_context` extracts facts (Step 2.6, already there).
When lowering runs, the live `occ_index` is wrapped in a `RecordingOccurrenceIndex` that delegates
`occurrences_of` to the real index and records each `(owner_eqn → result)`; the **real**
`lower_constraints` call runs through it (MF3). After it returns, `recorder.recorded` *is* the
occurrence table — exactly the queries lowering made, sufficient by construction. That table, the
raw facts, and `constraint_lowering_mode = "applied"` land on `PipelineContext`; `capture_snapshot`
passes them to the serializer. When `lower_constraints_enabled=False` (grandfathered), facts are
still extracted and serialized, the table is `{}`, mode is `grandfathered_off`.

**Load / rejection (`loader.py`), in order — every step raises `SnapshotFormatError` with a
re-capture message, never `KeyError` (MF1):**
1. Version gate (unchanged, `:127-140`).
2. **All three keys present** — `constraint_facts`, `part_occurrences`, `constraint_lowering_mode`
   each guarded with the `_require(raise_on_missing=True)` idiom. Any absent → raise.
3. **Facts well-formed** — `constraint_facts` is a dict carrying `schema_version`; a torn dict
   (missing `schema_version`) raises here, not a downstream `KeyError`.
4. **Facts version pinned (data)** — `schema_version == CONSTRAINT_FACTS_SCHEMA_VERSION` else raise.
5. **Embedded expression-ir version pinned (data)** — scan the facts' embedded predicate nodes'
   `schema_version` tokens; any `!= EXPRESSION_IR_SCHEMA_VERSION` raises (MF/NH5 — a *data-level*
   check, not only the code-pin assert, so a torn `expression-ir/v2` node is caught here rather
   than relied on `parse` to reject).
6. **Mode is a known enum** — `constraint_lowering_mode ∈ {"applied", "grandfathered_off"}` else
   raise (MF2 — an unrecognized mode is corruption, never a silent skip).
7. Code-pin asserts `CONSTRAINT_FACTS_SCHEMA_VERSION`/`EXPRESSION_IR_SCHEMA_VERSION` equal their
   pinned literals (coordinated-pair skew guard, mirrors `PROFILE_SEMANTIC_VERSION` at
   `constraint_lowering.py:463`).
8. Deserialize facts via `constraint_facts.parse`, occurrence table into `InstanceOccurrence`
   objects, mode string — join the `snap` dict.

**Offline lowering (`graph_rebuild.build_full_graph_from_snapshot`):** the mode is already a
validated enum by load time, so the dispatch is total — `applied` lowers, `grandfathered_off`
skips-with-warning, no third branch exists. After the base graph is built (mirroring live P1→P3,
P2 skipped per B3):

```
mode = snap["constraint_lowering_mode"]          # validated ∈ {applied, grandfathered_off} at load
if mode == "applied" and facts.usages:
    occ_index = FrozenOccurrenceIndex(snap["part_occurrences"])
    concrete = lower_constraints(facts, occ_index=occ_index, registry=inputs["registry"],
                                 design_attrs=inputs["design_attrs"],
                                 calc_usages=snap["calc_usages"])
    if concrete:
        graph = extend_graph_with_constraints(graph, concrete, inputs["group_deriver"])
elif mode == "grandfathered_off" and facts.usages:
    logger.warning("… assertions present but captured un-lowered (grandfathered); …")
```

`FrozenOccurrenceIndex` (new, in `part_instance_index.py`) holds the table and implements
`occurrences_of(qn)` = lookup; a missing key raises (corruption), never `[]`. With `RecordingOccurrenceIndex`
it is one of two thin wrappers over the same `occurrences_of` surface — record at capture, replay
offline. Neither needs closure or a model.

**Mode × section behavior matrix** (every cell defined — MF1/MF2/NH1):

| `constraint_lowering_mode` | `constraint_facts` | `part_occurrences` | offline behavior |
|---|---|---|---|
| `applied` | present, `usages` non-empty | present | lower + extend (the parity path) |
| `applied` | present, `usages` empty | `{}` | no-op (guarded on `facts.usages`); graph = today's |
| `grandfathered_off` | present, `usages` non-empty | `{}` | skip lowering + loud WARNING naming assertions |
| `grandfathered_off` | present, `usages` empty | `{}` | skip (constraint-free; degenerate but valid) |
| any valid mode | **absent** | — | `SnapshotFormatError` (MF1, step 2) |
| any valid mode | present, no `schema_version` | — | `SnapshotFormatError` (MF1, step 3) |
| any valid mode | — | **absent** | `SnapshotFormatError` (MF1, step 2) |
| **unknown/torn mode** | — | — | `SnapshotFormatError` (MF2, step 6) |

## Required Invariants

- **INV-1. `constraint_facts` present on every v3 snapshot.** Absent → `SnapshotFormatError`.
- **INV-2. Facts + occurrence round-trip is lossless.** `parse(serialize(facts)) == facts`
  bytewise; each reloaded `InstanceOccurrence` equals the captured one (frozen-dataclass equality).
- **INV-3. Byte-identical catalog across paths.** For a clean-lowering fixture, live and
  from-snapshot generation produce identical `constraint_id`s, identical catalog order, identical
  emitted graph structure.
- **INV-4. Offline never invokes the parser.** `FrozenOccurrenceIndex` and everything it feeds are
  license-free; `build_part_instance_index` is never called offline.
- **INV-5. Grandfathered graphs unchanged.** `plant_values`/`fusion_tea` `computation_graph.json`
  baselines stay byte-identical (mode gate short-circuits lowering).
- **INV-6. No v2/v3 coexistence.** The loader hard-gates the version; every committed snapshot is
  re-captured at v3 in the same change.
- **INV-7. `part_occurrences` is byte-stable across re-captures.** Owner keys emitted sorted;
  occurrence lists sorted by `_occurrence_sort_key` (already). No `set`-order or hash-randomized
  key leaks into the section (MF4).
- **INV-8. Every v3 snapshot is loadable-or-rejected, never silently degraded.** All three new
  keys, the facts `schema_version`, the embedded expression-ir version, and the mode enum are
  validated at load; any failure raises `SnapshotFormatError`. No new degrade-with-warning path.

## Component Overview

- **`constraint_facts` / `part_occurrences` / `constraint_lowering_mode` on `PipelineContext`**
  (`orchestration/pipeline_context.py`) — the capture-time carriers of the lowering *inputs* and
  mode.
- **`RecordingOccurrenceIndex`** (`analysis/part_instance_index.py`) — capture-time wrapper over
  the live `PartInstanceIndex`; delegates `occurrences_of` and records each `(owner_eqn → result)`.
  After the real `lower_constraints` call, `.recorded` is the occurrence table by construction (no
  second owner-selection path — MF3).
- **`FrozenOccurrenceIndex`** (`analysis/part_instance_index.py`) — offline stand-in exposing
  `occurrences_of(qn)`; dict lookup, raises on a missing key. The replay dual of the recorder.
- **Serializer additions** (`snapshot/serializer.py`) — write the three new keys; `bump
  SNAPSHOT_FORMAT_VERSION → 3` (`snapshot/__init__.py:15`).
- **Loader additions** (`snapshot/loader.py`) — missing-section gate, version-pin checks, facts +
  occurrence deserializers.
- **Offline lowering wiring** (`snapshot/graph_rebuild.py`) — the P1+P3 constraint phase, dispatched
  on the load-validated mode enum.
- **Flag flip + capture exclusion** — `pipeline_builder.py:697` default → True (retire `:856-863`);
  a named `GRANDFATHERED = {"plant_values", "fusion_tea"}` set in both capture scripts routing
  `lower_constraints_enabled=False` through `capture_snapshot`.

## Non-Goals

- Constraint **code** emission (the predicate compiler, module `.py`, aggregator/catalog runtime)
  — Item 7. This wires graph *structure* only.
- The facts schema shape — Item 1. We serialize and version-pin; we do not change it.
- Fixing the `gain` hierarchy-extraction gap — Item 14's named prerequisite. We grandfather the
  two affected fixtures and hand the fix on.
- Redesigning offline registry/backtracker re-derivation — already exists; the constraint phase
  is additive.
- Fingerprint sealing — Item 9. Parity here is graph/catalog identity, an input to the fingerprint.

## Implementation Notes

- **Occurrence table = the lowering transcript (MF3).** Inside the
  `if lower_constraints_enabled and constraint_facts.usages:` block (`pipeline_builder.py:865`),
  wrap the already-built `occ_index` in `RecordingOccurrenceIndex(occ_index)` and pass the wrapper
  as `lower_constraints(..., occ_index=recorder, ...)`. The wrapper records every `occurrences_of`
  call the *real* lowering makes (so it inherits lowering's exact `part_def`-kind + `ADMIT`-eligible
  filter — no reimplementation). After the call, `recorder.recorded` is the table. A
  `NonFiniteCardinalityError` still surfaces from the real call and halts capture, same as today.
- **Pin `part_occurrences` order (MF4).** Serialize the table with `sorted()` owner keys; occurrence
  lists are already `occurrences_of`-sorted. `snapshot_to_json` does not `sort_keys`, so an unsorted
  dict (e.g. from `set` iteration) would churn the section every capture and break the byte-identity
  gate.
- **Serializer reuses `_serialize_value`.** `InstanceOccurrence`/`PathStep` are plain frozen
  dataclasses with no AST fields → recurse cleanly. Do **not** hand-roll their dicts.
- **Embedded expression-ir version (NH5).** The load-time check scans the facts section's predicate
  nodes for their embedded `schema_version` and raises on any `!= EXPRESSION_IR_SCHEMA_VERSION` —
  a data-level guard, not only the code-pin assert, so a torn `expression-ir/v2` node is rejected at
  the boundary rather than trusted to `constraint_facts.parse`.
- **Facts embedding.** Store `json.loads(constraint_facts.serialize(facts))` so the section is the
  canonical object (byte-stable, sorted) and `snapshot_to_json`'s re-dump is deterministic. On
  load, `constraint_facts.parse(json.dumps(section))` — or add a dict-taking `parse` entry to
  avoid the re-encode; keep whichever preserves the exact round-trip the tests assert.
- **Extraction-only capture** (`_capture_extraction_only`) also needs the section: call
  `extract_constraint_facts(extractor.model)`, write it, mode `grandfathered_off` (no pipeline →
  no lowering), empty table. Otherwise those v3 snapshots fail INV-1.
- **Gate message idiom.** Copy the `_require(raise_on_missing=True)` phrasing: name the missing
  section, say it is load-bearing, end with "Recapture the snapshot."
- **`constraint_lowering_mode` naming.** Chosen over a bare bool so the grandfather reads as a
  named state in the JSON. `"applied"` is the default; the string is future-extensible if a third
  mode ever appears.

## Potential Risks

- **Offline registry/channel divergence.** If the offline registry resolves a constraint actual to
  a different channel than live, `constraint_id`/wiring diverges. Mitigation: the parity fixtures
  are the exact clean-lowering shapes (`wi014_toy`, `constraint_multi_instance`,
  `constraint_inline`); the byte-identity test is the guard. This is pre-existing offline-parity
  territory (Items 10/11) narrowed to constraint inputs.
- **`constraint_multi_instance` occurrence identity.** The highest-risk new surface (B2). The
  fixture exercises per-occurrence expansion; if serialized `instance_path`s reorder or lose an
  index, `constraint_id`s move. Mitigation: capture preserves `occurrences_of`'s sort; a dedicated
  round-trip test asserts reloaded occurrences equal captured.
- **`captured_at` churn masking real diffs.** Every re-capture rewrites timestamps. Mitigation:
  the established timestamp-only churn check + revert (memory `byte-identity-captured_at-churn`),
  then deliberate review of each remaining diff — including the two known stale baselines
  (`deep_cross_scope`, `ife_plant`), reviewed not waved through.
- **Grandfather drift.** If the exclusion set silently grows, real assertions get dropped.
  Mitigation: the set is named in code + docs; the offline load-time WARNING names ungenerated
  assertions on every grandfathered load.
- **Silent staleness of the occurrence table (NH4).** Offline lowering trusts the frozen table
  with no live model to cross-check, so a model edited but not re-captured lowers against stale
  occurrences — internally consistent, silently stale. This design does **not** detect that; the
  loader's existing per-file source-hash freshness warning (`loader.py:280-302`) flags the edited
  source, and executable-fingerprint sealing (Item 9) is where the staleness itself becomes a hard
  boundary. Stated here as an explicit, accepted boundary, not an oversight.

## Integration Strategy

Single atomic change (INV-6 forbids v2/v3 coexistence), sequenced so the committed state is
coherent — the loader's expected version and the committed snapshots move together:

1. **Code:** version bump; serializer writes the three keys; loader gates + deserializers;
   `RecordingOccurrenceIndex` + `FrozenOccurrenceIndex`; offline P1+P3 wiring; flip default
   True + retire `:856-863`; `GRANDFATHERED` set in both capture scripts; add `constraint_inline`
   + `constraint_multi_instance` to `MODELS`.
2. **Re-capture Layer A** (extraction snapshots, needs license): every fixture → v3 + facts
   section; clean constraint fixtures gain occurrences + `mode:"applied"`; the grandfathered pair
   captured flag-off (`mode:"grandfathered_off"`, honest non-empty facts, empty table).
3. **Re-capture Layer B** (pipeline baselines, license-free from Layer A): clean constraint
   fixtures gain constraint structure; constraint-free unchanged; grandfathered unchanged.
4. **Timestamp churn revert; deliberate diff review** against the expected-diff classes below;
   anything outside is investigated, not accepted.

**Expected-diff classes (extends spec [INFERRED] corpus bullet to all three new keys — NH2):**
1. `snapshot_format_version: 2 → 3` on every snapshot.
2. `constraint_facts` section added to every snapshot (empty `usages` for constraint-free models;
   honest non-empty for constraint-bearing, including the grandfathered pair).
3. `part_occurrences` added to every snapshot (`{}` for constraint-free and grandfathered; the
   resolved table for clean-lowering constraint fixtures).
4. `constraint_lowering_mode` added to every snapshot (`"applied"`, or `"grandfathered_off"` for
   the two carved-out fixtures and extraction-only fixtures).
5. Constraint structure in the `baseline_outputs/` graphs of clean-lowering constraint fixtures
   only (Layer B).
6. `captured_at` churn — reverted before commit.
The two grandfathered fixtures show classes 1–4 in their *snapshots* but their Layer-B graphs stay
byte-identical (class 5 excludes them).

The marker is the coordination mechanism (Open Question "two flip surfaces"): because offline
lowering keys off `mode`, not `facts present`, flipping the live default and turning on offline
lowering in the same change cannot halt the grandfathered pair — the corpus is green at the
committed state, not merely at some later cleanup.

## Validation Approach

- **Rejection tests (kept), one per matrix corruption cell — all raise `SnapshotFormatError` with a
  re-capture message, never `KeyError`:** (a) v2 snapshot (existing version gate, the bump alone);
  (b) v3 with `constraint_facts` **removed** (MF1); (c) v3 with `part_occurrences` **removed**
  (MF1); (d) v3 with `constraint_lowering_mode` **removed** (MF1); (e) v3 `constraint_facts`
  present but missing `schema_version` — a torn dict (MF1 step 3); (f) v3 facts `schema_version`
  wrong (data-pin); (g) v3 embedded `expression-ir` node version wrong (NH5 data-pin); (h) v3
  `constraint_lowering_mode` an **unknown string** (e.g. `"off"`, `""`) — must raise, must not
  silently skip lowering (MF2). Mirrors `test_hygiene_tail_loader.py`'s
  `pytest.raises(SnapshotFormatError, match=...)` shape.
- **Round-trip test (kept):** `serialize → load → serialize` of a constraint-bearing snapshot is
  byte-identical for the facts section; reloaded `InstanceOccurrence`s equal captured (INV-2).
- **Parity test (kept, the acceptance bar):** for `wi014_toy`, `constraint_multi_instance`,
  `constraint_inline` — live `build_pipeline_context(..., lower_constraints_enabled=True)` and
  `build_full_graph_from_snapshot` produce identical `constraint_id`s, catalog order, and graph
  structure (INV-3). *Acceptance is two distinct things (NH3):* these three fixtures prove
  live/snapshot **byte-identity**; the **22 corpus-wide conformance divergences** the flip was
  blocked on are eliminated separately by the full conformance suite going green after re-capture.
  The parity fixtures do not, by themselves, cover all 22 — do not conflate the two.
- **Present-empty test:** a constraint-free fixture (empty `usages`) loads with an empty catalog,
  no raise, graph byte-identical to today.
- **Grandfather test:** `plant_values`/`fusion_tea` from-snapshot generation succeeds (no `gain`
  halt), graphs byte-identical, and a WARNING names the ungenerated assertion.
- **Suite:** full `uv run pytest tests/` green; `git status` after capture shows only the four
  expected-diff classes.

## Next-Stage Handoff

**Fixed:** the three v3 keys and their shapes (D1–D4); the all-three-key raise-not-degrade gate +
mode-enum validation (D5, MF1/MF2); the mode×section matrix; occurrence table as the lowering
transcript (MF3); `part_occurrences` sorted-key ordering (INV-7, MF4); offline P1+P3 / skip-P2
(B3); the marker-driven grandfather (D3); the parity fixture set (D6); default flips to True.

**Open for the plan:** exact `parse` entry shape for the embedded facts dict (re-encode vs a
dict-taking parser) — pick whichever the round-trip test proves byte-exact; whether
`RecordingOccurrenceIndex`/`FrozenOccurrenceIndex`/`PartInstanceIndex` share a small `Protocol` or
just duck-type (`lower_constraints` only calls `occurrences_of`); how the embedded expression-ir
version scan walks predicate nodes (shallow token scan vs typed traversal); the precise marker
constant names.

**De-risk first:** the `constraint_multi_instance` occurrence round-trip and its `constraint_id`
parity (B2 + the highest-risk surface). Land that fixture's capture + parity test before wiring
the rest, so a serialization divergence surfaces on the smallest reproducing case. If it fails,
the frozen-table shape (D1) is what to revisit — a `/_my_spike` on the occurrence round-trip is
cheap insurance before the full corpus re-capture.

---

**Next Step:** After approval → `/_my_design_review` (fresh session), then `/_my_plan`.
