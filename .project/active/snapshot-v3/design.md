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
answers** — a small, deterministic table keyed by the owner QN lowering will query, with subtype
closure already folded in. Everything else lowering touches (registry, design attributes,
calc-usages, the executable profile) is already re-derived offline or round-trips inside the
facts. So offline lowering is genuine re-derivation from carried *inputs*, and it produces
byte-identical `constraint_id`s because its two identity-bearing inputs — the occurrences and the
facts — reload byte-identical.

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
  strings/ints; `occurrences_of` returns them pre-sorted; the table preserves that order.
  *If false → the multi-instance parity fixture's `constraint_id`s diverge live-vs-snapshot —
  the exact failure the fixture is chosen to catch.*
- **B3. `include_all=True` offline makes live P2 (roots-before-pruning) inert.** With no pruning,
  every calc usage — including one whose only consumer is an assertion — is already in the graph,
  so the producer channel each `MODULE_OUTPUT` input binds to exists without root injection.
  *If false → a constraint's `bound_channel` dangles offline and `_validate_channel_references`
  raises inside `extend_graph_with_constraints`.*
- **B4. The facts round-trip is lossless enough that `evaluate_profile` and `serialize_expression`
  return byte-identical predicates offline.** Item 1's canonical JSON + Item 3's profile are
  deterministic functions of the facts. *If false → `predicate_ir` or eligibility differs, so the
  catalog (and its ordering) differs across paths.*
- **B5. The set of owner QNs lowering queries is exactly the `part_def`-kind owning-definition QNs
  in the facts, knowable at capture from the facts alone.** *If false → the captured table misses
  a key lowering asks for offline, and the frozen index raises on a key it should have held.*

## Key Decisions

- **D1. Serialize the resolved per-owner occurrence table, keyed by the queried owner EQN, closure
  pre-applied.** `{ sanitize_qualified_name(owner_qn): [InstanceOccurrence, ...] }` for every
  `part_def` owner in the facts. *Rejected: serialize index inputs and rebuild the subtype closure
  offline (needs `qn_to_partdef` / `_supertype_closure`, i.e. a live model — the thing we are
  removing; more offline code, more divergence surface). Rejected: carry the resolved
  `ConcreteConstraint` catalog (carriage-not-re-derivation, the S3 CF(2) trap — the parity would
  be vacuous).*
- **D2. No `blocked` map in the table.** The guidance floated `+ blocked set`; with a per-owner
  `occurrences_of` query (not a bulk `all_occurrences()` dump), a non-finite owner *raises* at
  capture and halts it — exactly as live — so no blocked entry can reach a valid v3 snapshot.
  Offline, a queried key absent from the table is a corruption → raise, never `[]`. *Rejected:
  bulk `all_occurrences()` + `blocked` (would need offline closure to answer supertype queries —
  D1's rejected alternative).*
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
- **D5. The missing-section gate raises, reusing the version-gate idiom.** In
  `load_extraction_snapshot`, after the version check: `"constraint_facts" not in raw` →
  `SnapshotFormatError` with a re-capture instruction. *Rejected: the `compilation_results`
  degrade-with-warning path (`loader.py:184-203`) — the spec forbids it here; a missing facts
  section is a corruption, not a legitimately-absent optional block.*
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
serializer code).

**Capture data flow (live):** `build_pipeline_context` extracts facts (Step 2.6, already there);
when lowering runs it also builds the occurrence table via a new
`resolve_owner_occurrence_table(facts, occ_index)` helper (co-located with the owner-expansion
logic it mirrors) and sets `constraint_lowering_mode`. All three land on `PipelineContext`.
`capture_snapshot` passes them to the serializer. When `lower_constraints_enabled=False`
(grandfathered), facts are still extracted and serialized, the table is `{}`, mode is
`grandfathered_off`.

**Load / rejection (`loader.py`):** version gate (unchanged) → **new** missing-`constraint_facts`
gate (raise) → validate `constraint_facts["schema_version"] == CONSTRAINT_FACTS_SCHEMA_VERSION`
(raise on mismatch) → code-pin assert `EXPRESSION_IR_SCHEMA_VERSION == "expression-ir/v1"`
(coordinated-pair skew guard, mirrors `constraint_lowering.py`'s `PROFILE_SEMANTIC_VERSION`
assert) → deserialize facts via `constraint_facts.parse`, occurrence table into
`InstanceOccurrence` objects, and read the mode. These join the `snap` dict.

**Offline lowering (`graph_rebuild.build_full_graph_from_snapshot`):** after the base graph is
built (mirroring live P1→P3, P2 skipped per B3):

```
if snap["constraint_lowering_mode"] == "applied" and facts.usages:
    occ_index = FrozenOccurrenceIndex(snap["part_occurrences"])
    concrete = lower_constraints(facts, occ_index=occ_index, registry=inputs["registry"],
                                 design_attrs=inputs["design_attrs"],
                                 calc_usages=snap["calc_usages"])
    if concrete:
        graph = extend_graph_with_constraints(graph, concrete, inputs["group_deriver"])
```

`FrozenOccurrenceIndex` (new, in `part_instance_index.py`) holds the table and implements
`occurrences_of(qn)` = lookup; a missing key raises (corruption), never `[]`. It is the only new
type; it needs no closure, no model.

**Grandfather surfacing:** when `mode == "grandfathered_off"` and `facts.usages` is non-empty, the
offline path emits one loud WARNING naming the ungenerated assertions (the surfacing law — the
grandfather is announced at every load, not silent).

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

## Component Overview

- **`constraint_facts` / `part_occurrences` / `constraint_lowering_mode` on `PipelineContext`**
  (`orchestration/pipeline_context.py`) — the capture-time carriers of the lowering *inputs* and
  mode.
- **`resolve_owner_occurrence_table(facts, occ_index)`** (`analysis/constraint_lowering.py`) —
  builds the per-owner table from the live index; reuses the same owner-QN selection logic
  `_expand_owner_instances` uses. Called in `build_pipeline_context` when lowering runs.
- **`FrozenOccurrenceIndex`** (`analysis/part_instance_index.py`) — offline stand-in exposing
  `occurrences_of(qn)`; dict lookup, raises on a missing key.
- **Serializer additions** (`snapshot/serializer.py`) — write the three new keys; `bump
  SNAPSHOT_FORMAT_VERSION → 3` (`snapshot/__init__.py:15`).
- **Loader additions** (`snapshot/loader.py`) — missing-section gate, version-pin checks, facts +
  occurrence deserializers.
- **Offline lowering wiring** (`snapshot/graph_rebuild.py`) — the P1+P3 constraint phase.
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

- **Occurrence table build point.** Build it where `occ_index` already exists — inside the
  `if lower_constraints_enabled and constraint_facts.usages:` block (`pipeline_builder.py:865`) —
  so no second index is constructed. `resolve_owner_occurrence_table` iterates the `part_def`
  owner EQNs and calls `occ_index.occurrences_of` (a `NonFiniteCardinalityError` here halts capture,
  same as lowering would).
- **Serializer reuses `_serialize_value`.** `InstanceOccurrence`/`PathStep` are plain frozen
  dataclasses with no AST fields → recurse cleanly. Do **not** hand-roll their dicts.
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

## Integration Strategy

Single atomic change (INV-6 forbids v2/v3 coexistence), sequenced so the committed state is
coherent — the loader's expected version and the committed snapshots move together:

1. **Code:** version bump; serializer writes the three keys; loader gates + deserializers;
   `FrozenOccurrenceIndex`; `resolve_owner_occurrence_table`; offline P1+P3 wiring; flip default
   True + retire `:856-863`; `GRANDFATHERED` set in both capture scripts; add `constraint_inline`
   + `constraint_multi_instance` to `MODELS`.
2. **Re-capture Layer A** (extraction snapshots, needs license): every fixture → v3 + facts
   section; clean constraint fixtures gain occurrences + `mode:"applied"`; the grandfathered pair
   captured flag-off (`mode:"grandfathered_off"`, honest non-empty facts, empty table).
3. **Re-capture Layer B** (pipeline baselines, license-free from Layer A): clean constraint
   fixtures gain constraint structure; constraint-free unchanged; grandfathered unchanged.
4. **Timestamp churn revert; deliberate diff review** against the four expected-diff classes
   (spec [INFERRED] corpus bullet); anything outside is investigated.

The marker is the coordination mechanism (Open Question "two flip surfaces"): because offline
lowering keys off `mode`, not `facts present`, flipping the live default and turning on offline
lowering in the same change cannot halt the grandfathered pair — the corpus is green at the
committed state, not merely at some later cleanup.

## Validation Approach

- **Rejection tests (kept):** (a) a v2 snapshot → `SnapshotFormatError` via the existing version
  gate (the bump alone); (b) a hand-built v3 snapshot with `constraint_facts` **removed** →
  `SnapshotFormatError` with a re-capture message (the new gate); (c) a v3 snapshot whose facts
  `schema_version` is wrong → `SnapshotFormatError`. Mirrors `test_hygiene_tail_loader.py`'s
  `pytest.raises(SnapshotFormatError, match=...)` shape.
- **Round-trip test (kept):** `serialize → load → serialize` of a constraint-bearing snapshot is
  byte-identical for the facts section; reloaded `InstanceOccurrence`s equal captured (INV-2).
- **Parity test (kept, the acceptance bar):** for `wi014_toy`, `constraint_multi_instance`,
  `constraint_inline` — live `build_pipeline_context(..., lower_constraints_enabled=True)` and
  `build_full_graph_from_snapshot` produce identical `constraint_id`s, catalog order, and graph
  structure (INV-3). The 22 previously-measured divergences become this test's met baseline.
- **Present-empty test:** a constraint-free fixture (empty `usages`) loads with an empty catalog,
  no raise, graph byte-identical to today.
- **Grandfather test:** `plant_values`/`fusion_tea` from-snapshot generation succeeds (no `gain`
  halt), graphs byte-identical, and a WARNING names the ungenerated assertion.
- **Suite:** full `uv run pytest tests/` green; `git status` after capture shows only the four
  expected-diff classes.

## Next-Stage Handoff

**Fixed:** the three v3 keys and their shapes (D1–D4); the raise-not-degrade missing-section gate
(D5); offline P1+P3 / skip-P2 (B3); the marker-driven grandfather (D3); the parity fixture set
(D6); default flips to True.

**Open for the plan:** exact `parse` entry shape for the embedded facts dict (re-encode vs a
dict-taking parser) — pick whichever the round-trip test proves byte-exact; whether
`FrozenOccurrenceIndex` and `PartInstanceIndex` share a small `Protocol` or just duck-type
(`lower_constraints` only calls `occurrences_of`); the precise marker constant names.

**De-risk first:** the `constraint_multi_instance` occurrence round-trip and its `constraint_id`
parity (B2 + the highest-risk surface). Land that fixture's capture + parity test before wiring
the rest, so a serialization divergence surfaces on the smallest reproducing case. If it fails,
the frozen-table shape (D1) is what to revisit — a `/_my_spike` on the occurrence round-trip is
cheap insurance before the full corpus re-capture.

---

**Next Step:** After approval → `/_my_design_review` (fresh session), then `/_my_plan`.
