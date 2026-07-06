# Design: Subtype-Aware Enumeration & Constraint-Report Truth

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-07-06
**Branch:** pipeline-truth-epic (agentic-mbse on an Item-4 companion branch — see spec "agentic-mbse landing")
**Base commit:** a7c21df
**Epic:** PIPELINE-TRUTH, Item 4

---

## Overview

Make model-wide constraint enumeration subtype-aware at one adapter choke point, so the
constraint drop report finally sees `assert constraint`; serialize a constraint manifest so the
report is faithful on the `generate --from-snapshot` path; and fix the same blindness in three
agentic-mbse validators. The semantics are fixed by the spec's 8-row decision table; this design
owns the mechanisms.

## Related Artifacts

- **Spec:** `.project/active/subtype-enumeration/spec.md` (decision table = the contract)
- **Spec review:** `.project/active/subtype-enumeration/spec-review.md` (satisfy exclusion, format-bump sequencing)
- **Discovery register:** `.project/research/20260706_pipeline-truth-discovery.md` §D4 (evidence base; agentic-mbse rows derive from here — that repo is sandbox-blocked)
- **Architecture:** `docs/architecture/reference/01-extraction.md` (REQ-EXT-09), `reference/27-snapshot-generation.md`, `modeling-assumptions.md` §8
- **R4 probe (deferred):** `.project/active/subtype-enumeration/_probe.py`

---

## R4 Verification Table (design-open, MANDATORY)

Environmental limit recorded plainly: **this autonomous session's approval gate blocks all code
execution** (`uv run`, `.venv/bin/python`, `pytest` all return "requires approval" with no human
to grant it) **and the sandbox blocks every read of `/home/reid/1cfe/agentic-mbse`** (Read + Bash
+ subagent all denied — the exact trap the `agentic-mbse-repo-path` memory and the spec's own
"sandboxed out of that repo" note describe). So the codegen findings are confirmed by **direct
source read of the exact query + gate lines** (stronger than a black-box probe — I read the
precise code), corroborated by the orchestrator's already-executed live/license-free runs
(register L20–33). The live probe is **authored and committed** (`_probe.py`); running it is an
**implement-stage gate** that updates register §D4. Nothing here is claimed as "I ran it and saw X".

| # | Finding | Probe | Verdict |
|---|---------|-------|---------|
| 1 | `extractor.py:107` queries exact-type `ConstraintUsage`; `:123` `if constraints:` gates BOTH the per-item INFO loop and the summary WARN → report totally silent when the only constraint is an `assert`. wi014_toy carries `assert constraint affordable` at `toy_plant.sysml:51`. | `_probe.py` PROBE1: load wi014_toy live, count exact `ConstraintUsage` (=0), `is_instance(assert,"ConstraintUsage")` (=True), assert `report_dropped_constraints` emits 0 records. | **CONFIRMED** (source read: `extractor.py:107,123`; fixture `toy_plant.sysml:51`; register L25). Live run deferred. |
| 2 | `constraint_extractor.py:50` uses the same exact-type `ConstraintUsage` query; docstring line 4 claims "constraint, assert constraint, and require constraint" support. Zero callers in `src/`/`tests/`. | `_probe.py` PROBE2: `extract_all_constraints(wi014_model)` returns 0 total despite the assert. | **CONFIRMED** (source read: `constraint_extractor.py:4,50`; zero-caller grep in register L26 + spec-review L43). Live run deferred. |
| 3 | agentic-mbse `level3_dataflow.py:48` queries abstract `Import` → matches nothing → dep graph always `{}` → circular check structurally always passes. Secondary: `imported_namespace` guard skips MembershipImports even once type is fixed. | Seeded circular-import fixture: assert non-empty graph + circular check FAILS. | **CONFIRMED-BY-REGISTER** (§D4 "worst new"; L125). Live re-verify + line re-check deferred to implement (repo sandbox-blocked). |
| 4 | agentic-mbse `level4_constraints.py:113` exact-type `ConstraintUsage` → undercounts asserts. | assert-bearing fixture: droppable count matches independent literal. | **CONFIRMED-BY-REGISTER** (§D4 L124). Deferred to implement. |
| 5 | agentic-mbse `level6_architecture.py:602` exact-type `ConstraintUsage` → non-executable WARN never fires on asserts. | assert-bearing fixture: WARN fires; clean fixture: silent. | **CONFIRMED-BY-REGISTER** (§D4 L124). Deferred to implement. |

> The three agentic-mbse rows carry the spec's caveat: "the probe wins — re-verify before building
> on any single line number." Their line numbers (`:48`, `:113`, `:602`, adapter `:214`) are
> register-sourced and **must be re-confirmed at implement** when the companion branch is checked out.

---

## Core Concept

There is one blindness and one silence, and both collapse to a single idea: **enumeration must
respect the type hierarchy, and the report must be rendered from a serializable manifest — not
recomputed from a live model.**

- **The blindness** is that syside's model-wide query is exact-type (`nodes(kind,
  include_subtypes=False)`), while `is_instance` on the same adapter is hierarchy-aware. Every
  diagnostic that enumerates and then classifies is therefore lying: it enumerates blind and
  classifies smart. The fix is one adapter parameter (`include_subtypes`), opt-in per call site per
  the decision table — not a global flip.

- **The silence** is that the constraint report reads the live model directly, so it (a) can't run
  offline and (b) has no serialization carrier. The fix is to split the report into **collect** (live,
  produces a typed manifest) and **render** (pure, consumes the manifest). The manifest is
  serialized into the snapshot; the from-snapshot path deserializes it and calls the *same* renderer.
  Live and offline reports are then identical by construction.

The load-bearing subtlety is the exclusion. `include_subtypes=True` on `ConstraintUsage` sweeps in
`RequirementUsage` (and its `satisfy` subtype), which are requirement-side, not dropped predicates.
So the swept set is partitioned by one hierarchy-aware predicate — `is_instance(x,
"RequirementUsage")` — defined **once** in the adapter and reused by all three constraint sites in
both repos. That single predicate is the family-level fix; nobody hand-rolls exact-type string
matching. The manifest keeps the *whole* swept subtree (including the excluded requirement/satisfy
elements, tagged by kind) so the zero-found sentinel's scanned/reported/excluded breakdown
reproduces offline and a swept-and-excluded `satisfy` stays observable rather than silent.

This composes with existing pieces, adding no parallel machinery: the adapter
(`syside_adapter.elements_of_type`) gains parameters; `report_dropped_constraints` is refactored in
place into collect+render; the snapshot serializer/loader gain one top-level field; the from-snapshot
context (`snapshot_context.py:24`) gains one replay call; `PipelineContext` gains one field.

## Key Bets

- **B1.** syside `nodes(kind, include_subtypes=True)` returns the full subtype subtree for `kind`,
  and the adapter's `is_instance` is hierarchy-aware (so an `exclude` built on it is correct).
  *If false → the sweep still misses asserts, or the exclusion filters the wrong set; the whole
  mechanism is inert.* (Register §D4 L117,129; live confirmation deferred.)
- **B2.** The metamodel hierarchy holds: `AssertConstraintUsage ⊂ ConstraintUsage`;
  `SatisfyRequirementUsage ⊂ RequirementUsage ⊂ ConstraintUsage`; `require constraint` is a *plain*
  `ConstraintUsage` (no distinct metaclass — the require/assume kind is on the membership); `Import`
  is abstract with only `MembershipImport`/`NamespaceImport` concrete.
  *If false → the exclusion drops the wrong things and the sentinel counts lie.* (Verified against
  the syside stub in spec-review L26–28; the satisfy correction is the one that flipped the semantic.)
- **B3.** `extract_all_constraints`, `_deserialize_constraint_info`, and the abstract-`Import` query
  have zero real consumers (zero callers / always-empty result), so deleting/fixing them changes no
  working behavior. *If false → a live consumer breaks, or a validator that appeared to "pass"
  regresses loudly.* (Zero-caller grep in register L26,32 + spec-review L43; agentic-mbse leg deferred.)
- **B4.** No supported model currently uses `satisfy`, an enum-valued entry point, or
  connection/view/case subtypes. *If false → excluding satisfy or keeping exact-type on
  AttributeUsage/PartDefinition silently drops a real assertion or entry point.* (Spec satisfy note;
  §D4 AT-RISK rows. Mitigation: the sentinel keeps satisfy/requirement observable.)

## Key Decisions

- **D1. Exclusion = adapter `exclude` capability, is_instance-based, defined once.** The load-bearing
  predicate `is_instance(x, "RequirementUsage")` lives in the adapter and is the sole definition of
  "requirement-side." agentic-mbse rows 6/7 call `elements_of_type("ConstraintUsage",
  include_subtypes=True, exclude=("RequirementUsage",))`; codegen's collect does the full
  `include_subtypes=True` sweep and partitions with the *same* adapter `is_instance` (it needs the
  per-kind breakdown for the manifest, so it can't take the pre-filtered set). Both derive droppability
  from one hierarchy-aware predicate. *Rejected: three call-site `is_instance` filters (drift risk —
  the satisfy exclusion is subtle and must be defined once, R4 family-level fix); exact-type string
  compare (the original bug).*
- **D2. Serialization carrier = a top-level `dropped_constraints` manifest.** A list of typed records
  `{owner_kind, owner_name, owner_qualified_name, constraint_name, constraint_kind, source_line}`
  covering all three owner kinds. *Rejected: populating the `PartDefinitionData.constraints` stub —
  it is per-part-def and cannot carry calc-def-owned or part-usage-owned constraints (spec [INFERRED]).* 
- **D3. `report_dropped_constraints` splits into collect (live) + render (pure).** `render` is a
  module-level function over the manifest with no syside import; both the live path and the
  from-snapshot path call it. This is what makes live-vs-snapshot parity hold *by construction*
  rather than by a matched second implementation. *Rejected: a second offline-only report
  implementation (guaranteed to drift from the live one — the exact anti-pattern Item 3's parity work
  exists to catch).* 
- **D4. `extract_all_constraints` (row 2) is deleted in this item.** Its false docstring is precisely
  the constraint-report-truth surface Item 4 owns; with zero callers, leaving it for Item 8 would let
  the false "supports assert constraint" claim survive this item. `_deserialize_constraint_info`
  (`loader.py:275`, dead) is deleted alongside, since the new manifest deserializer supersedes it.
  *Coordinate with Item 8 so each dies once; implement re-runs the zero-caller grep before deleting.*
  *Rejected: hand both to Item 8 (leaves the false docstring alive through the truth item).* 
- **D5. Snapshot format hard-gates 1→2; all 20 committed snapshots re-captured.** The from-snapshot
  constraint report is a success criterion, so a v1 snapshot silently reporting "no constraints" would
  reintroduce the blind-vs-empty ambiguity this item kills. *Rejected: additive-optional manifest
  (loader `.get` default, no bump) — the mechanism Item 10 used for `reference_chain` — because it
  would leave old snapshots silently constraint-blind, defeating the criterion.*

## Architecture

Data flow, one constraint's journey:

```
LIVE:   model --elements_of_type("ConstraintUsage", include_subtypes=True)-->
        swept --collect_constraint_manifest (is_instance kind-ladder)-->
        manifest --render_constraint_report--> logs
                 \--> PipelineContext.constraint_manifest --serialize--> snapshot["dropped_constraints"]

OFFLINE: snapshot["dropped_constraints"] --loader--> snap["constraint_manifest"]
         --render_constraint_report (SAME fn)--> logs   [byte-identical to live]
```

Boundaries:

- **agentic-mbse `syside_adapter.elements_of_type`** — the choke point. Gains keyword-only
  `include_subtypes: bool = False` (passes through to `nodes`) and `exclude: Collection[str] = ()`
  (drops any element `is_instance` of a named type). One additive change, consumed by both repos.
- **`extraction/constraint_report.py` (new)** — pure module: `ConstraintKind` enum,
  `ConstraintManifestEntry` dataclass, `render_constraint_report(manifest, logger)`. No syside import,
  so offline replay is license-free.
- **`SysMLDataExtractor.collect_constraint_manifest()` (new method, replaces the query in
  `report_dropped_constraints`)** — live sweep + kind-ladder → `list[ConstraintManifestEntry]`. Owner
  kind computed live via the existing `_constraint_owner_kind` (is_instance).
- **`pipeline_builder.build_pipeline_context` step 2.5** — `manifest = extractor.collect_...();
  render_constraint_report(manifest); ctx.constraint_manifest = manifest`.
- **serializer / loader** — one top-level `dropped_constraints` field in/out.
- **`snapshot_context.build_pipeline_context_from_snapshot`** — one added
  `render_constraint_report(snap["constraint_manifest"])` call (the replay).

## Required Invariants

- **INV-A (opt-in).** Adapter default `include_subtypes=False`, `exclude=()`. Every existing call
  site is byte-for-byte unchanged unless it opts in; the only behavior deltas are decision-table rows
  1/6/7 (and row 5's Import fix). Rows 3/4/8 KEEP exact-type deliberately; row-4 sites are unchanged.
- **INV-B (parity).** Live and from-snapshot reports call the *same* `render_constraint_report` over
  the *same* `ConstraintManifestEntry` shape → identical log output for the same model.
- **INV-C (full sweep in manifest).** The manifest holds the entire swept `ConstraintUsage` subtree
  including excluded requirement/satisfy entries (tagged by kind), so scanned/reported/excluded
  reproduce offline and satisfy stays observable.
- **INV-D (single droppable predicate).** Droppable ≡ swept minus `is_instance("RequirementUsage")`.
  Every consumer in both repos derives droppability from that one adapter predicate.
- **INV-E (hard gate).** `SNAPSHOT_FORMAT_VERSION = 2`; loader rejects any other version; no v1/v2
  coexistence; all 20 committed snapshots re-captured on v2.

## Component Overview

- **`elements_of_type` (agentic-mbse adapter, `syside_adapter.py:~214`)** — adds the two keyword-only
  params + a docstring teaching the per-site decision table (D4-mandated docs home). Preserve its
  current decorator (called both as `SysideAdapter.elements_of_type(...)` and
  `self.adapter.elements_of_type(...)` today — a `@staticmethod` serves both; confirm at implement).
- **`ConstraintKind` / `ConstraintManifestEntry` / `render_constraint_report`** — new pure report
  module. Kinds: `ASSERT`, `PLAIN` (droppable), `REQUIREMENT`, `SATISFY` (excluded). Ordered
  is_instance ladder: assert → satisfy → requirement → plain (satisfy checked before requirement
  because `SatisfyRequirementUsage ⊂ RequirementUsage`).
- **`collect_constraint_manifest`** — live producer on the extractor.
- **serializer/loader/snapshot_context/PipelineContext/capture** — thread the manifest through.
- **agentic-mbse `level3_dataflow` / `level4_constraints` / `level6_architecture`** — rows 5/6/7 fixes.
- **REQ-EXT-09 test class + docs** — re-anchor and truth updates.

## Non-Goals

Constraint execution; connection/interface/view/case/analysis extraction (row 4);
`EnumerationUsage`-as-entry-point (row 3, Item 5); the other D3 silent-failure sites (Item 5).
Distinguishing `require` from `plain` in the manifest (folded as `PLAIN`; the require/assume kind
lives on the membership — a documented v2 limitation, revisited by the constraint-execution epic).

## Implementation Notes

- **Zero-found sentinel (row 1).** One always-emitted INFO from `render_constraint_report`:
  `"Constraint drop report: scanned {N} ConstraintUsage (incl. subtypes), reported {M} droppable
  ({K} assert, {J} require/plain), excluded {E} requirement/satisfy."` Then M per-droppable INFO
  lines (as today). Then, only if `M > 0`, the existing summary WARN. Logger stays
  `sysml_codegen.extraction.extractor` on both paths. N=0 → sentinel shows all zeros, no WARN;
  N>0,M=0 → sentinel shows scanned>0/excluded>0, observable, no WARN.
- **REQ-EXT-09 re-anchor** (`tests/conformance/test_extractor.py`, class 888–922; self-referential
  block 895–899): (a) replace `expected = sum(same query)` with a **literal** transcribed from a
  fixture-source grep, commented with the grep; (b) add the **part-usage-owner** leg — needs a
  fixture carrying a part-usage-owned constraint (wi014's assert is part-*def*-owned; confirm
  catf_mfe covers part-usage, else add a small Item-4-owned fixture row); (c) add a **wi014 assert
  pin** (literal 1 droppable assert `affordable`); (d) add an **executable mutation check** —
  `collect_constraint_manifest` run with `include_subtypes=False` MUST miss the assert, proving the
  test discriminates (stronger than a comment); (e) add a **from-snapshot leg** (license-free) asserting
  the replayed report matches the live one (feeds Item 3 parity). No mocks (R1) — use live extractor
  + committed snapshot.
- **House style (R1):** `ConstraintKind` is an `Enum` (V1–V11 diagnostic idiom); manifest entries are
  a frozen dataclass; the kind-ladder is compute-once (build manifest) then look-up (render). The
  manifest is a list, not a map, so no NewType key is introduced.
- **agentic-mbse row 5:** prefer `elements_of_type("Import", include_subtypes=True)` (consistent
  mechanism) over enumerating `MembershipImport`+`NamespaceImport` (hard-codes the subtype list); ALSO
  fix the `imported_namespace` guard that skips MembershipImports. Pins: seeded circular-import fixture
  FAILS the circular check + non-empty graph (fires-on-shape); acyclic fixture PASSES, non-empty graph,
  no false cycle (silent-on-clean).
- **Format bump + re-capture (D5, [HARD]).** Bump `snapshot/__init__.py:12` to 2. Re-capture all 20
  `tests/fixtures/*/extraction_snapshot.json` via the capture script (Item 1's `--fixtures` filter),
  **one reviewed commit**, license-gated. Reviewed-diff gate: every snapshot byte-identical to before
  EXCEPT the `snapshot_format_version` field and, for constraint-bearing models, the new
  `dropped_constraints` array. Sequencing (spec [HARD]): **Item 1 impl → Item 4 impl → Item 2 impl**,
  one working tree, one regen at a time.
- **Docs (same change):** `modeling-assumptions.md` §8 reworded (report covers `ConstraintUsage`
  incl. `assert`/`require`/plain, excludes `RequirementUsage`+`satisfy`, live + from-snapshot);
  `01-extraction.md` REQ-EXT-09 row (independent anchor + part-usage leg + assert pin, drop the
  "counted structurally" anti-pattern text); decision table published in agentic-mbse adapter docs
  with a pointer here; retire BACKLOG `[CONSTRAINT-SILENCE]`.

## Potential Risks

- **Adapter shape uncertainty (agentic-mbse sandbox-blocked).** I could not read
  `syside_adapter.py` to confirm the current decorator/signature of `elements_of_type` or that
  `nodes` accepts `include_subtypes`. Mitigation: the change is additive keyword-only params; the
  register (§D4 L117–118) states the subtype mode exists and the adapter never passes it. **Implement
  must re-read the adapter first** and adjust the exact call to `nodes`.
- **`require` vs `plain` conflation.** The manifest folds both to `PLAIN`. If a future consumer needs
  the require/assume distinction, it must inspect the membership — a documented v2 gap, not a silent
  loss (the constraint is still reported as droppable).
- **Re-capture blast radius.** 20 license-gated regenerations in one commit; a stray semantic diff
  (beyond version + manifest) means an unintended extraction change slipped in. Mitigation: the
  reviewed-diff gate above; diff every file, not just spot-check.
- **Part-usage-owner fixture.** The re-anchored test's part-usage leg may need a new fixture; keep it
  Item-4-owned and minimal so it doesn't entangle Item 1's fixture work.

## Integration Strategy

Extends, replaces nothing structural. `report_dropped_constraints` keeps its name and call site
(`pipeline_builder.py:685`) but delegates to collect+render. The from-snapshot path gains the report
it never had. The adapter change is backward-compatible (defaults preserve every current call). The
format bump is the one breaking change, absorbed by the mandated re-capture.

## Validation Approach

- **Live (license):** REQ-EXT-09 fires on wi014 assert + catf_mfe (independent literal), covers
  calc-def/part-def/part-usage owners, mutation check discriminates, silent-on-clean holds.
- **Offline (license-free):** from-snapshot report replays byte-identically (INV-B parity); loader
  rejects a v1 snapshot (INV-E).
- **agentic-mbse (companion branch):** seeded circular-import FAILS + non-empty graph; acyclic PASSES;
  level4/level6 assert fixtures fire; enum fixture pins row 8.
- **Re-capture gate:** reviewed diff = version field + manifest only.
- **Both suites green** (R2). **R4:** run `_probe.py` live and update register §D4.

## Next-Stage Handoff

- **Fixed:** the 5 decisions (D1–D5); the collect/render split; manifest shape; sentinel wording;
  format bump to 2; sequencing Item1→Item4→Item2.
- **Open (implement resolves):** exact adapter signature/decorator + `nodes` call (re-read agentic-mbse
  first); the three agentic-mbse line numbers (re-verify, "probe wins"); whether catf_mfe already
  carries a part-usage-owned constraint or a fixture is needed; the require/plain fold is accepted.
- **De-risk first:** re-read the agentic-mbse adapter and run `_probe.py` live before touching any
  call site — every downstream edit assumes B1 (subtype mode exists, is_instance hierarchy-aware).
  Then land the adapter param, then the codegen report, then serialization + re-capture, then the
  three validators.

---
Next Step: After approval → `/_my_plan` (multi-file, cross-repo, sequenced re-capture warrants a checkboxed plan).
